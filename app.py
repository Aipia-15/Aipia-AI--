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
if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "plans" not in st.session_state: st.session_state.plans = []
if "confirmed" not in st.session_state: st.session_state.confirmed = None
if "more_count" not in st.session_state: st.session_state.more_count = 0

# --- 3. スタイル定義 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:wght@700&display=swap');
    .stApp { background-color: #F8F6F4; font-family: 'Noto Serif JP', serif; }
    .header-container { text-align: center; padding: 40px 0; border-bottom: 2px solid #D4AF37; background: #FFF; margin-bottom: 30px; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 3.5rem; color: #111; letter-spacing: 5px; margin: 0; }
    .aipia-sub { color: #D4AF37; font-weight: bold; letter-spacing: 2px; font-size: 1rem; margin-top: -5px; }
    .spot-card { background: white; padding: 20px; border-radius: 12px; border-left: 6px solid #D4AF37; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    .url-link { color: #1976D2; text-decoration: none; font-size: 0.85rem; font-weight: bold; }
    .time-step { background-color: #E3F2FD; padding: 15px; border-radius: 10px; margin: 10px 0; border: 1px solid #BBDEFB; }
    .advice-card { background-color: #FFF3E0; border-left: 5px solid #FF9800; padding: 12px; border-radius: 5px; font-size: 0.9rem; }
    .reserve-btn { display: inline-block; padding: 10px 20px; margin: 5px; border-radius: 5px; color: white !important; text-decoration: none; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">-AIが創る、秘境への旅行プラン-</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力画面 ---
if st.session_state.step == "input":
    col_k1, col_k2 = st.columns([3, 1])
    with col_k1: keyword = st.text_input("🔍 探したいキーワード（例：秘境の滝、隠れ家カフェ）")
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
    with col7: purposes = st.multiselect("✨ 目的", ["秘境探索", "美食", "温泉", "歴史", "絶景", "街歩き"], default=["秘境探索"])
    with col8: adults = st.number_input("大人(名)", 1, 20, 2)
    with col9: kids = st.number_input("小人(名)", 0, 20, 0)
    
    walk_speed = st.select_slider("🚶‍♂️ 歩く速度", options=["ゆっくり", "普通", "早歩き"], value="普通")

    if st.button("⚜️ 秘境リサーチを開始する", use_container_width=True, type="primary"):
        st.session_state.form_data = {"dep": dep_place, "dest": f"{pref}{city}", "transport": transport, "speed": walk_speed, "people": f"大人{adults}名,小人{kids}名", "purposes": purposes}
        # 初回10個生成
        prompt = f"{pref}{city}周辺で{keyword}に関連する実在スポット10件。名称|解説|住所|公式サイトURL 形式で。URLは必ず含めて。"
        res = call_groq_safe(prompt)
        if res:
            st.session_state.found_spots = [l.split('|') for l in res.strip().split('\n') if '|' in l]
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: スポット選択 ---
elif st.session_state.step == "select_spots":
    st.subheader(f"📍 {st.session_state.form_data['dest']} の秘境候補")
    for i, s in enumerate(st.session_state.found_spots):
        if len(s) < 2: continue
        url_html = f'<br><a href="{s[3]}" target="_blank" class="url-link">🌐 公式サイト・詳細</a>' if len(s)>3 and "http" in s[3] else ""
        st.markdown(f'<div class="spot-card"><b>{s[0]}</b><br><small>{s[1]}</small>{url_html}</div>', unsafe_allow_html=True)
        if st.checkbox(f"「{s[0]}」を採用", key=f"chk_{i}"):
            if s[0] not in st.session_state.selected_spots: st.session_state.selected_spots.append(s[0])
    
    col_more, col_next = st.columns(2)
    with col_more:
        if st.button("➕ スポットをさらに10個表示"):
            st.session_state.more_count += 1
            res = call_groq_safe(f"{st.session_state.form_data['dest']}で未紹介のスポットを10件追加。名称|解説|住所|URL")
            if res:
                st.session_state.found_spots.extend([l.split('|') for l in res.strip().split('\n') if '|' in l])
                st.rerun()
    with col_next:
        if st.button("✅ プラン生成へ進む", type="primary"): st.session_state.step = "hotel_survey"; st.rerun()

# --- STEP 3: ホテル・バリアフリー ---
elif st.session_state.step == "hotel_survey":
    st.subheader("🏨 宿泊と設備の希望")
    h_type = st.selectbox("宿泊スタイル", ["絶景旅館", "バリアフリー対応の宿", "モダンホテル", "老舗料理宿"])
    h_barrier = st.multiselect("必要なバリアフリー設備", ["段差なし", "車椅子対応", "手すり", "エレベーター"])
    if st.button("✨ 5つの全日程プラン案を生成", type="primary"):
        st.session_state.hotel_data = {"type": h_type, "barrier": h_barrier}
        st.session_state.step = "plan_gen"; st.rerun()

# --- STEP 4: プラン表示 (5案・全日程・編集) ---
elif st.session_state.step == "plan_gen":
    if not st.session_state.plans:
        with st.spinner("5つの全日程プランを構築中..."):
            for i in range(5):
                prompt = f"""
                出発地:{st.session_state.form_data['dep']}, 交通:{st.session_state.form_data['transport']}, スポット:{st.session_state.selected_spots}, 宿泊:{st.session_state.hotel_data['type']}
                【必須】
                1. 1日目・2日目など「全日程」を必ず含める。
                2. 実在するホテル名を 'hotel_name' に明記。1日目の夕方にチェックイン時間を表記。
                3. 'route_info' に出発地からのアクセス要約を入れる。
                4. 'advices' 配列に3つのアドバイスを入れる。
                {{'route_info': '...', 'advices': ['...', '...', '...'], 'hotel_name': '...', 'days': [{{'label': '1日目', 'steps': [{{'arrival': '...', 'departure': '...', 'content': '...'}}]}}]}}
                """
                res = call_groq_safe(prompt)
                parsed = parse_json_safely(res)
                if parsed: st.session_state.plans.append(parsed)

    if st.session_state.plans:
        p_idx = st.sidebar.radio("プラン案を選択", range(len(st.session_state.plans)), format_func=lambda x: f"案 {x+1}")
        data = st.session_state.plans[p_idx]

        st.success(f"🚂 **アクセス概要:** {data.get('route_info')}")
        cols = st.columns(3)
        for idx, adv in enumerate(data.get("advices", [])[:3]):
            cols[idx].markdown(f'<div class="advice-card">💡 {adv}</div>', unsafe_allow_html=True)

        st.info(f"🏨 **提案ホテル:** {data.get('hotel_name')}")

        if st.toggle("🛠️ 行程を編集する"):
            for day in data.get("days", []):
                for step in day.get("steps", []):
                    step['content'] = st.text_area(f"{step['arrival']} の内容", step['content'])

        for day in data.get("days", []):
            st.markdown(f"#### 📅 {day['label']}")
            for step in day.get("steps", []):
                st.markdown(f'<div class="time-step"><b>{step["arrival"]} - {step["departure"]}</b><br>{step["content"]}</div>', unsafe_allow_html=True)

        col_r, col_c = st.columns(2)
        with col_r:
            if st.button("🔄 プランを再生成"): st.session_state.plans = []; st.rerun()
        with col_c:
            if st.button("🏆 この内容で確定", type="primary"): 
                st.session_state.confirmed = data; st.session_state.step = "share"; st.rerun()

# --- STEP 5: 確定共有 ---
elif st.session_state.step == "share":
    if not st.session_state.confirmed: st.session_state.step = "plan_gen"; st.rerun()
    plan = st.session_state.confirmed
    h_name = plan.get("hotel_name")
    q = urllib.parse.quote(h_name)
    
    st.balloons()
    st.header(f"✨ 確定した旅のしおり：{h_name}")
    st.markdown(f"""
        <div style="margin-bottom:20px;">
            <a href="https://search.rakuten.co.jp/search/mall/{q}/" target="_blank" class="reserve-btn" style="background:#bf0000;">楽天トラベルで予約</a>
            <a href="https://www.jalan.net/keyword/{q}/" target="_blank" class="reserve-btn" style="background:#ff7a00;">じゃらんで予約</a>
            <a href="https://www.ikyu.com/search/?keyword={q}" target="_blank" class="reserve-btn" style="background:#003567;">一休.comで予約</a>
        </div>
    """, unsafe_allow_html=True)

    for day in plan.get("days", []):
        st.subheader(day['label'])
        for step in day.get("steps", []):
            st.info(f"🕒 {step['arrival']} - {step['departure']}\n\n{step['content']}")
    
    if st.button("🏠 最初から作成する"): 
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
