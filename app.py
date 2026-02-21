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

# --- 2. セッション管理 ---
for key in ["step", "found_spots", "selected_spots", "plans", "confirmed", "more_count"]:
    if key not in st.session_state:
        if key == "step": st.session_state[key] = "input"
        elif key in ["found_spots", "selected_spots", "plans"]: st.session_state[key] = []
        else: st.session_state[key] = 0

# --- 3. スタイル定義 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:wght@700&display=swap');
    .stApp { background-color: #F8F6F4; font-family: 'Noto Serif JP', serif; }
    .header-container { text-align: center; padding: 40px 0; border-bottom: 2px solid #D4AF37; background: #FFF; margin-bottom: 30px; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 3.5rem; color: #111; letter-spacing: 5px; margin: 0; }
    .aipia-sub { color: #D4AF37; font-weight: bold; letter-spacing: 2px; font-size: 1rem; margin-top: -5px; }
    .spot-card { background: white; padding: 20px; border-radius: 12px; border-left: 6px solid #D4AF37; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    .time-step { background-color: #E3F2FD; padding: 20px; border-radius: 10px; margin: 15px 0; border: 1px solid #BBDEFB; position: relative; }
    .aipia-badge { position: absolute; top: -10px; right: -10px; background: #FFD700; color: #000; padding: 5px 15px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; border: 2px solid #FFF; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }
    .advice-card { background-color: #FFF3E0; border-left: 5px solid #FF9800; padding: 12px; border-radius: 5px; font-size: 0.9rem; }
    .reserve-btn { display: inline-block; padding: 10px 20px; margin: 5px; border-radius: 5px; color: white !important; text-decoration: none; font-weight: bold; font-size: 0.9rem; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">-AIが創る、秘境への旅行プラン-</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力画面 ---
if st.session_state.step == "input":
    col_k1, col_k2 = st.columns([3, 1])
    with col_k1: keyword = st.text_input("🔍 探したいキーワード", placeholder="例：秘境の滝、地元の人が通う店、絶景温泉")
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
    with col7: purposes = st.multiselect("✨ 目的", ["秘境探索", "美食", "温泉", "歴史", "絶景", "バリアフリー"], default=["秘境探索", "美食"])
    with col8: adults = st.number_input("大人", 1, 10, 2)
    with col9: kids = st.number_input("小人", 0, 10, 0)
    
    walk_speed = st.select_slider("🚶‍♂️ 歩く速度", options=["ゆっくり", "普通", "早歩き"], value="普通")

    if st.button("⚜️ 秘境リサーチを開始する", use_container_width=True, type="primary"):
        st.session_state.form_data = {"dep": dep_place, "dest": f"{pref}{city}", "transport": transport, "speed": walk_speed, "people": f"大人{adults}名,小人{kids}名", "purposes": purposes}
        prompt = f"{pref}{city}周辺で{keyword}に関連する実在スポット10件。名称|解説|正確な住所|公式サイトURL(なければGoogleMapのURL) 形式。必ず10件出すこと。"
        res = call_groq_safe(prompt)
        if res:
            st.session_state.found_spots = [l.split('|') for l in res.strip().split('\n') if '|' in l]
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: スポット選択 ---
elif st.session_state.step == "select_spots":
    st.subheader(f"📍 {st.session_state.form_data['dest']} の厳選候補")
    for i, s in enumerate(st.session_state.found_spots):
        if len(s) < 2: continue
        url = s[3] if len(s)>3 and "http" in s[3] else f"https://www.google.com/search?q={urllib.parse.quote(s[0])}"
        st.markdown(f'<div class="spot-card"><b>{s[0]}</b><br><small>{s[1]}</small><br><a href="{url}" target="_blank" style="color:#D4AF37; font-size:0.8rem;">🌐 地図・公式サイト</a></div>', unsafe_allow_html=True)
        if st.checkbox(f"「{s[0]}」を旅程に組み込む", key=f"chk_{i}"):
            if s[0] not in st.session_state.selected_spots: st.session_state.selected_spots.append(s[0])
    
    col_more, col_next = st.columns(2)
    with col_more:
        if st.button("➕ スポットをもっと見る"):
            st.session_state.more_count += 1
            res = call_groq_safe(f"{st.session_state.form_data['dest']}でさらに隠れた名所や食事処を10件。名称|解説|住所|URL 形式。")
            if res:
                st.session_state.found_spots.extend([l.split('|') for l in res.strip().split('\n') if '|' in l])
                st.rerun()
    with col_next:
        if st.button("✅ プラン詳細の生成へ", type="primary"): st.session_state.step = "hotel_survey"; st.rerun()

# --- STEP 3: ホテル・設備 ---
elif st.session_state.step == "hotel_survey":
    st.subheader("🏨 宿泊とバリアフリーの最終確認")
    h_style = st.selectbox("宿泊スタイル", ["絶景旅館", "老舗料理宿", "バリアフリー完備の最新ホテル", "隠れ家的な宿"])
    h_barrier = st.multiselect("必要な配慮", ["段差なし（フラット）", "車椅子対応トイレ", "貸切風呂あり", "エレベーター至近"])
    if st.button("✨ 5つの超詳細プランを生成", type="primary"):
        st.session_state.hotel_data = {"style": h_style, "barrier": h_barrier}
        st.session_state.step = "plan_gen"; st.rerun()

# --- STEP 4: プラン表示 ---
elif st.session_state.step == "plan_gen":
    if not st.session_state.plans:
        with st.spinner("AIが最適なルートと追加スポットを計算中..."):
            for i in range(5):
                prompt = f"""
                出発地:{st.session_state.form_data['dep']}, 目的地:{st.session_state.form_data['dest']}, 交通:{st.session_state.form_data['transport']}
                選んだスポット:{st.session_state.selected_spots}, 希望ホテル:{st.session_state.hotel_data['style']}, 設備:{st.session_state.hotel_data['barrier']}
                
                【指示】
                1. 1日目・2日目など全日程を網羅し、各日4〜5ステップ以上の詳細な行程にすること。
                2. 選ばれたスポットを必ず組み込み、さらにAIがその付近の「食事処」や「休憩所」を勝手に1つ以上追加し、そのステップの is_recommended を true にすること。
                3. 実在するホテル名を 'hotel_name' に、住所を 'hotel_address' に明記。1日目の15:00-18:00に宿泊行程を必ず入れる。
                4. 各ステップにURLを必ず入れる（Google検索URL可）。
                
                {{'route_info': '出発地からの詳細経路', 'advices': ['アドバイス1', '2', '3'], 'hotel_name': '実在ホテル名', 'hotel_address': '住所', 'days': [{{'label': '1日目', 'steps': [{{'arrival': '09:00', 'departure': '10:30', 'content': '...', 'url': '...', 'is_recommended': false}}]}}]}}
                """
                res = call_groq_safe(prompt)
                parsed = parse_json_safely(res)
                if parsed: st.session_state.plans.append(parsed)

    if st.session_state.plans:
        p_idx = st.sidebar.radio("プランの比較", range(len(st.session_state.plans)), format_func=lambda x: f"プラン案 {x+1}")
        data = st.session_state.plans[p_idx]

        st.success(f"🚂 **アクセスルート:** {data.get('route_info')}")
        cols = st.columns(3)
        for idx, adv in enumerate(data.get("advices", [])[:3]):
            cols[idx].markdown(f'<div class="advice-card">💡 {adv}</div>', unsafe_allow_html=True)

        st.info(f"🏨 **提案ホテル:** {data.get('hotel_name')} ({data.get('hotel_address')})")

        if st.toggle("🛠️ 行程を編集する"):
            for day in data.get("days", []):
                for step in day.get("steps", []):
                    step['content'] = st.text_area(f"{step['arrival']} 内容", step['content'])

        for day in data.get("days", []):
            st.markdown(f"#### 📅 {day['label']}")
            for step in day.get("steps", []):
                badge = '<div class="aipia-badge">Aipia厳選スポット！</div>' if step.get('is_recommended') else ''
                st.markdown(f'<div class="time-step">{badge}<b>{step["arrival"]} - {step["departure"]}</b><br>{step["content"]}<br><a href="{step.get("url","#")}" target="_blank" style="font-size:0.8rem;">🔗 詳細</a></div>', unsafe_allow_html=True)

        if st.button("🏆 この内容で確定し共有・予約へ", type="primary"): 
            st.session_state.confirmed = data; st.session_state.step = "share"; st.rerun()

# --- STEP 5: 共有・予約 ---
elif st.session_state.step == "share":
    plan = st.session_state.confirmed
    h_name = plan.get("hotel_name")
    q = urllib.parse.quote(h_name)
    
    st.balloons()
    st.header(f"✨ 旅の最終プラン：{h_name}")
    
    # 予約リンク
    st.markdown("### 🏨 宿泊施設を予約する")
    st.markdown(f"""
        <a href="https://search.rakuten.co.jp/search/mall/{q}/" target="_blank" class="reserve-btn" style="background:#bf0000;">楽天トラベル</a>
        <a href="https://www.jalan.net/keyword/{q}/" target="_blank" class="reserve-btn" style="background:#ff7a00;">じゃらん</a>
        <a href="https://www.ikyu.com/search/?keyword={q}" target="_blank" class="reserve-btn" style="background:#003567;">一休.com</a>
    """, unsafe_allow_html=True)

    # 共有機能（テキストコピー用）
    st.markdown("### 📱 旅程を共有する")
    share_text = f"【Aipia 旅のしおり】\nホテル：{h_name}\n"
    for d in plan['days']:
        share_text += f"\n{d['label']}\n"
        for s in d['steps']:
            share_text += f"・{s['arrival']}-{s['departure']}：{s['content']}\n"
    st.text_area("以下の内容をコピーしてLINE等に貼り付けてください", share_text, height=150)

    for day in plan.get("days", []):
        st.subheader(day['label'])
        for step in day.get("steps", []):
            st.info(f"🕒 {step['arrival']} - {step['departure']}\n\n{step['content']}")
    
    if st.button("🏠 ホームへ戻る"): 
        for key in ["step", "found_spots", "selected_spots", "plans", "confirmed", "more_count"]:
            st.session_state[key] = "input" if key == "step" else ([] if isinstance(st.session_state[key], list) else 0)
        st.rerun()
