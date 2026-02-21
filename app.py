import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import json
import re
import urllib.parse

# --- 1. 基本設定 ---
st.set_page_config(layout="wide", page_title="Aipia")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

PREFECTURES = [""] + ["北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県", "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県", "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県", "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県", "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"]

def call_groq_safe(prompt):
    target_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    for model_id in target_models:
        try:
            res = client.chat.completions.create(model=model_id, messages=[{"role": "user", "content": prompt}], temperature=0.7)
            if res.choices[0].message.content: return res.choices[0].message.content
        except: continue
    return None

def parse_json_safely(text):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match: return None
        return json.loads(match.group().replace("'", '"'))
    except: return None

# --- 2. スタイル ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    .header-container { text-align: center; padding: 30px 0; border-bottom: 2px solid #D4AF37; background: #FFF; margin-bottom: 20px; }
    .spot-card { margin-bottom: 15px; padding: 15px; background: #FFF; border-radius: 10px; border-left: 6px solid #D4AF37; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .route-info { background-color: #ECEFF1; border-radius: 8px; padding: 15px; margin: 10px 0; border-left: 5px solid #607D8B; font-size: 0.9rem; }
    .time-step { background-color: #E3F2FD; padding: 15px; border-radius: 10px; margin: 10px 0; border: 1px solid #BBDEFB; }
    .advice-card { background-color: #FFF3E0; border-left: 5px solid #FF9800; padding: 12px; border-radius: 5px; font-size: 0.85rem; flex: 1; min-width: 200px; }
    .reserve-btn { display: inline-block; padding: 10px 15px; margin: 5px; border-radius: 5px; color: white !important; text-decoration: none; font-weight: bold; font-size: 0.8rem; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-container"><h1>Aipia</h1><p>-AIが算出する、出発地からの完全ルート-</p></div>', unsafe_allow_html=True)

# セッション
if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "plans" not in st.session_state: st.session_state.plans = []
if "page_offset" not in st.session_state: st.session_state.page_offset = 0

# --- STEP 1: 入力 ---
if st.session_state.step == "input":
    col_k1, col_k2 = st.columns([3, 1])
    with col_k1: keyword = st.text_input("🔍 探したいスポット・体験", placeholder="例：秘境の温泉、車で行ける絶景、歴史ある街並み")
    with col_k2: transport = st.radio("🚃 移動手段", ["公共交通機関", "車・レンタカー"], horizontal=True)
    
    col1, col2 = st.columns(2)
    with col1: dep_place = st.text_input("🛫 出発地（駅名や住所）", value="新宿駅")
    with col2: dest_area = st.text_input("📍 目的地エリア（都道府県・市）", value="長野県")
    
    if st.button("⚜️ ルートとスポットをリサーチ", use_container_width=True, type="primary"):
        st.session_state.form_data = {"dep": dep_place, "dest": dest_area, "transport": transport}
        # 重複を避けるためページオフセットを使用
        prompt = f"{dest_area}の{keyword}に関連する「実在する」観光施設を10件。名称|解説|住所|URL 形式。架空の名前は厳禁。"
        res = call_groq_safe(prompt)
        if res:
            st.session_state.found_spots = [l.split('|') for l in res.strip().split('\n') if '|' in l]
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: スポット選択 ---
elif st.session_state.step == "select_spots":
    st.subheader(f"📍 {st.session_state.form_data['dest']} の候補")
    for i, s in enumerate(st.session_state.found_spots):
        if len(s) < 2: continue
        st.markdown(f'<div class="spot-card"><b>{s[0]}</b><br><small>{s[1]}</small></div>', unsafe_allow_html=True)
        if st.checkbox("採用", key=f"s_{i}"):
            if s[0] not in st.session_state.selected_spots: st.session_state.selected_spots.append(s[0])
    
    col_more, col_next = st.columns(2)
    with col_more:
        if st.button("➕ 他のスポットをもっと見る"):
            st.session_state.page_offset += 1
            res = call_groq_safe(f"{st.session_state.form_data['dest']}で、まだ出していないスポットをさらに10件。名称|解説|住所|URL 形式。")
            if res:
                new_items = [l.split('|') for l in res.strip().split('\n') if '|' in l]
                st.session_state.found_spots.extend(new_items)
                st.rerun()
    with col_next:
        if st.button("✅ ルート・ホテル生成へ", type="primary"): st.session_state.step = "hotel_survey"; st.rerun()

# --- STEP 3: 希望 ---
elif st.session_state.step == "hotel_survey":
    st.subheader("🏨 宿泊とバリアフリーの確認")
    h_type = st.selectbox("ホテルの種類", ["絶景旅館", "バリアフリー対応ホテル", "駅近モダンホテル"])
    barrier = st.multiselect("配慮事項", ["段差なし", "車椅子トイレ", "手すり", "エレベーター"])
    if st.button("✨ 全日程の完全ルートを生成", type="primary"):
        st.session_state.hotel_data = {"type": h_type, "barrier": barrier}
        st.session_state.step = "plan_gen"; st.rerun()

# --- STEP 4: プラン表示 (ルート算出) ---
elif st.session_state.step == "plan_gen":
    if not st.session_state.plans:
        with st.spinner("出発地からの経路を計算中..."):
            for i in range(3):
                prompt = f"""
                出発地:{st.session_state.form_data['dep']}, 目的地:{st.session_state.form_data['dest']}, 交通:{st.session_state.form_data['transport']}
                スポット:{st.session_state.selected_spots}, 宿泊:{st.session_state.hotel_data['type']}
                
                【必須要件】
                1. 冒頭に 'route_summary' として、出発地から目的地までの具体的経路（例：特急あずさで約3時間等）を明記。
                2. 実在するホテル名を 'hotel_name' に入れる。「塩嶺王寺」のような架空名は厳禁。
                3. 1日目・2日目の全行程を作成。チェックイン時間は必ず15:00-18:00の間で設定。
                4. アドバイス3個を 'advices' 配列に。
                
                {{'route_summary': '...', 'advices': ['...', '...', '...'], 'hotel_name': '実在ホテル', 'days': [{{'label': '1日目', 'steps': [{{'arrival': '10:00', 'departure': '11:00', 'content': '...'}}]}}]}}
                """
                res = call_groq_safe(prompt)
                parsed = parse_json_safely(res)
                if parsed: st.session_state.plans.append(parsed)

    if st.session_state.plans:
        p_idx = st.sidebar.radio("プラン選択", range(len(st.session_state.plans)), format_func=lambda x: f"案 {x+1}")
        data = st.session_state.plans[p_idx]
        
        st.markdown(f'<div class="route-info">🚀 <b>アクセス経路:</b> {data.get("route_summary")}</div>', unsafe_allow_html=True)
        
        col_adv = st.columns(3)
        for idx, a in enumerate(data.get("advices", [])[:3]):
            col_adv[idx].markdown(f'<div class="advice-card">💡 {a}</div>', unsafe_allow_html=True)
            
        st.info(f"🏨 提案ホテル: {data.get('hotel_name')}")
        
        if st.toggle("🛠️ 行程を編集する"):
            for d in data.get("days", []):
                for stp in d.get("steps", []):
                    stp['content'] = st.text_area(f"{stp['arrival']}の内容", stp['content'])

        for day in data.get("days", []):
            st.markdown(f"#### 📅 {day['label']}")
            for step in day.get("steps", []):
                st.markdown(f'<div class="time-step"><b>{step["arrival"]} - {step["departure"]}</b><br>{step["content"]}</div>', unsafe_allow_html=True)

        if st.button("🏆 この内容で予約へ", type="primary"):
            st.session_state.confirmed = data; st.session_state.step = "share"; st.rerun()

elif st.session_state.step == "share":
    plan = st.session_state.confirmed
    h_name = plan.get("hotel_name")
    q = urllib.parse.quote(h_name)
    st.success(f"旅程が確定しました。")
    st.markdown(f"### 🏨 {h_name} の予約はこちら")
    st.markdown(f"""
        <a href="https://search.rakuten.co.jp/search/mall/{q}/" target="_blank" class="reserve-btn" style="background:#bf0000;">楽天トラベル</a>
        <a href="https://www.jalan.net/keyword/{q}/" target="_blank" class="reserve-btn" style="background:#ff7a00;">じゃらん</a>
        <a href="https://www.ikyu.com/search/?keyword={q}" target="_blank" class="reserve-btn" style="background:#003567;">一休.com</a>
    """, unsafe_allow_html=True)
    st.button("最初から作成", on_click=lambda: st.session_state.clear())
