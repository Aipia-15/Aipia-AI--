import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import json
import re
import urllib.parse
import time

# --- 1. 基本設定 ---
st.set_page_config(layout="wide", page_title="Aipia")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

PREFECTURES = [""] + ["北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県", "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県", "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県", "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県", "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"]

def call_groq_safe(prompt):
    for model_id in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]:
        try:
            res = client.chat.completions.create(model=model_id, messages=[{"role": "user", "content": prompt}], temperature=0.5)
            if res.choices[0].message.content: return res.choices[0].message.content
        except: continue
    return None

def parse_json_safely(text):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match: return None
        return json.loads(match.group().replace("'", '"').replace('\n', ' '))
    except: return None

# --- 2. セッション管理 ---
keys = ["step", "found_spots", "selected_spots", "plans", "confirmed", "more_count", "form_data", "hotel_data"]
for k in keys:
    if k not in st.session_state:
        if k == "step": st.session_state[k] = "input"
        elif k in ["found_spots", "selected_spots", "plans"]: st.session_state[k] = []
        else: st.session_state[k] = None

# --- 3. スタイル定義 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:wght@700&display=swap');
    .stApp { background-color: #F8F6F4; font-family: 'Noto Serif JP', serif; }
    .header-container { text-align: center; padding: 30px 0; border-bottom: 2px solid #D4AF37; background: #FFF; margin-bottom: 20px; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 3rem; color: #111; letter-spacing: 4px; margin: 0; }
    .aipia-sub { color: #D4AF37; font-weight: bold; font-size: 0.9rem; margin-top: -5px; }
    .spot-card { background: white; padding: 20px; border-radius: 12px; border-left: 6px solid #D4AF37; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    .time-step { background-color: #E3F2FD; padding: 20px; border-radius: 10px; margin: 15px 0; border: 1px solid #BBDEFB; position: relative; }
    .aipia-badge { position: absolute; top: -10px; right: -10px; background: #FFD700; color: #000; padding: 5px 15px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; border: 2px solid #FFF; }
    .advice-card { background-color: #FFF3E0; border-left: 5px solid #FF9800; padding: 12px; border-radius: 5px; font-size: 0.9rem; }
    .reserve-btn { display: inline-block; padding: 10px 20px; margin: 5px; border-radius: 5px; color: white !important; text-decoration: none; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">-AIが創る、秘境への旅行プラン-</p></div>', unsafe_allow_html=True)

# --- STEP 1: ホーム画面 ---
if st.session_state.step == "input":
    col_k1, col_k2 = st.columns([3, 1])
    with col_k1: keyword = st.text_input("🔍 探したいキーワード", placeholder="例：秘境の滝、地元の店、絶景温泉")
    with col_k2: transport = st.radio("🚃 交通手段", ["電車・公共交通", "車・レンタカー"], horizontal=True)

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1: dep_place = st.text_input("🛫 出発地点", value="新宿駅")
    with col2: date_range = st.date_input("📅 旅行日程", value=(datetime.now(), datetime.now() + timedelta(days=1)))
    with col3: dep_time = st.time_input("🕔 出発時刻", value=datetime.strptime("08:00", "%H:%M").time())

    col4, col5, col6 = st.columns([2, 2, 2])
    with col4: pref = st.selectbox("📍 都道府県", PREFECTURES)
    with col5: city = st.text_input("🏠 市区町村（任意）")
    with col6: budget = st.number_input("💰 予算/人", 5000, 500000, 50000)

    col7, col8, col9 = st.columns([2, 1, 1])
    with col7: purposes = st.multiselect("✨ 目的", ["秘境探索", "美食", "温泉", "歴史", "絶景", "バリアフリー"], default=["秘境探索"])
    with col8: adults = st.number_input("大人(名)", 1, 20, 2)
    with col9: kids = st.number_input("小人(名)", 0, 20, 0)
    
    walk_speed = st.select_slider("🚶‍♂️ 歩く速度", options=["ゆっくり", "普通", "早歩き"], value="普通")

    if st.button("⚜️ 秘境リサーチを開始する", use_container_width=True, type="primary"):
        st.session_state.form_data = {"dep": dep_place, "dest": f"{pref}{city}", "transport": transport, "speed": walk_speed}
        
        # 進捗バー：スポット検索
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.text("現地の観光スポットをリサーチ中...")
        
        prompt = f"{pref}{city}周辺で{keyword}に関連する実在スポット10件。名称|解説|住所|URL 形式。架空の名前は厳禁。"
        res = call_groq_safe(prompt)
        
        progress_bar.progress(100)
        if res:
            st.session_state.found_spots = [l.split('|') for l in res.strip().split('\n') if '|' in l]
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: スポット選択 ---
elif st.session_state.step == "select_spots":
    st.subheader(f"📍 {st.session_state.form_data['dest']} の厳選候補")
    for i, s in enumerate(st.session_state.found_spots):
        if len(s) < 2: continue
        url = s[3] if len(s)>3 and "http" in s[3] else f"https://www.google.com/search?q={urllib.parse.quote(s[0])}"
        st.markdown(f'<div class="spot-card"><b>{s[0]}</b><br><small>{s[1]}</small><br><a href="{url}" target="_blank" style="color:#D4AF37; font-size:0.8rem;">🌐 公式情報・地図</a></div>', unsafe_allow_html=True)
        if st.checkbox(f"「{s[0]}」を採用", key=f"chk_{i}"):
            if s[0] not in st.session_state.selected_spots: st.session_state.selected_spots.append(s[0])
    
    col_more, col_next = st.columns(2)
    with col_more:
        if st.button("➕ スポットをさらに追加"):
            progress_bar = st.progress(0)
            res = call_groq_safe(f"{st.session_state.form_data['dest']}の未紹介スポットを10件。名称|解説|住所|URL")
            progress_bar.progress(100)
            if res:
                st.session_state.found_spots.extend([l.split('|') for l in res.strip().split('\n') if '|' in l])
                st.rerun()
    with col_next:
        if st.button("✅ プラン生成へ進む", type="primary"): st.session_state.step = "hotel_survey"; st.rerun()

# --- STEP 3: ホテル・設備 ---
elif st.session_state.step == "hotel_survey":
    st.subheader("🏨 宿泊と設備の希望")
    h_type = st.selectbox("宿泊スタイル", ["実在する老舗旅館", "バリアフリーホテル", "モダンラグジュアリー", "地元の隠れ家宿"])
    if st.button("✨ 5つの超詳細プランを生成", type="primary"):
        st.session_state.hotel_data = {"type": h_type}
        st.session_state.step = "plan_gen"; st.rerun()

# --- STEP 4: プラン表示（進捗バー付き5案生成） ---
elif st.session_state.step == "plan_gen":
    if not st.session_state.plans:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(5):
            status_text.text(f"プラン案 {i+1}/5 を構築中...")
            prompt = f"""
            出発地:{st.session_state.form_data['dep']}, 目的地:{st.session_state.form_data['dest']}, 交通:{st.session_state.form_data['transport']}
            選択スポット:{st.session_state.selected_spots}, 宿泊:{st.session_state.hotel_data['type']}
            【重要】
            1. ホテルは実在するものを選び、住所も記載。
            2. 各ステップにGoogle Map等へのURLを必ず含める。
            3. 選んでいない食事処をAIが1つ以上追加し is_recommended を true に。
            {{'route_info': '経路要約', 'advices': ['A1', 'A2', 'A3'], 'hotel_name': '実在ホテル', 'hotel_address': '住所', 'days': [{{'label': '1日目', 'steps': [{{'arrival': '...', 'departure': '...', 'content': '...', 'url': 'https://...', 'is_recommended': false}}]}}]}}
            """
            res = call_groq_safe(prompt)
            parsed = parse_json_safely(res)
            if parsed: st.session_state.plans.append(parsed)
            progress_bar.progress((i + 1) * 20)
        status_text.empty()

    if st.session_state.plans:
        p_idx = st.sidebar.radio("プラン比較", range(len(st.session_state.plans)), format_func=lambda x: f"プラン案 {x+1}")
        data = st.session_state.plans[p_idx]
        
        st.success(f"🚂 **アクセス:** {data.get('route_info')}")
        cols = st.columns(3)
        for idx, adv in enumerate(data.get("advices", [])[:3]):
            cols[idx].markdown(f'<div class="advice-card">💡 {adv}</div>', unsafe_allow_html=True)
            
        st.info(f"🏨 **宿泊先:** {data.get('hotel_name')} ({data.get('hotel_address')})")

        for day in data.get("days", []):
            st.markdown(f"#### 📅 {day['label']}")
            for step in day.get("steps", []):
                badge = '<div class="aipia-badge">Aipia厳選！</div>' if step.get('is_recommended') else ''
                url = step.get('url') or f"https://www.google.com/search?q={urllib.parse.quote(step['content'][:10])}"
                st.markdown(f'<div class="time-step">{badge}<b>{step["arrival"]} - {step["departure"]}</b><br>{step["content"]}<br><a href="{url}" target="_blank" style="font-size:0.8rem;">🔗 公式/地図リンク</a></div>', unsafe_allow_html=True)

        if st.button("🏆 この内容で最終確定", type="primary"): 
            st.session_state.confirmed = data; st.session_state.step = "share"; st.rerun()

# --- STEP 5: 共有・予約 ---
elif st.session_state.step == "share":
    plan = st.session_state.confirmed
    h_name = plan.get("hotel_name")
    q = urllib.parse.quote(h_name)
    st.balloons()
    st.header(f"✨ 最終確定：{h_name}")
    
    st.markdown(f"""
        <a href="https://search.rakuten.co.jp/search/mall/{q}/" target="_blank" class="reserve-btn" style="background:#bf0000;">楽天トラベル</a>
        <a href="https://www.jalan.net/keyword/{q}/" target="_blank" class="reserve-btn" style="background:#ff7a00;">じゃらん</a>
        <a href="https://www.ikyu.com/search/?keyword={q}" target="_blank" class="reserve-btn" style="background:#003567;">一休.com</a>
    """, unsafe_allow_html=True)

    st.subheader("📱 LINE等への共有用テキスト")
    share_text = f"【Aipia 旅のプラン】\n宿泊：{h_name}\n"
    for d in plan['days']:
        share_text += f"\n{d['label']}\n"
        for s in d['steps']: share_text += f"・{s['arrival']}-{s['departure']}：{s['content']}\n"
    st.text_area("コピーして共有してください", share_text, height=150)

    if st.button("🏠 ホームへ戻る"): 
        for k in keys: st.session_state[k] = "input" if k == "step" else ([] if isinstance(st.session_state[k], list) else None)
        st.rerun()
