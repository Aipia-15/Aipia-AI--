import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse
import json
import re
import base64

# --- 1. 基本設定 ---
st.set_page_config(layout="wide", page_title="Aipia", page_icon="Aipia.png")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

PREFECTURES = [""] + ["北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県", "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県", "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県", "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県", "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"]

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return None

def call_groq_safe(prompt):
    target_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    for model_id in target_models:
        try:
            res = client.chat.completions.create(model=model_id, messages=[{"role": "user", "content": prompt}], temperature=0.7)
            return res.choices[0].message.content
        except: continue
    return None

# --- 2. スタイル定義 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:wght@700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    
    .nav-container { display: flex; align-items: center; cursor: pointer; text-decoration: none; margin-bottom: 30px; }
    .nav-logo { height: 60px; width: 60px; object-fit: contain; margin-right: 15px; border-radius: 50%; }
    .nav-text { font-family: 'Playfair Display', serif; font-size: 2.8rem; color: #111; letter-spacing: 3px; font-weight: 700; margin: 0; }
    
    .spot-card { margin-bottom: 45px; padding: 25px; background: #FFF; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.06); border-left: 6px solid #D4AF37; }
    .spot-placeholder { 
        width: 100%; height: 160px; background: linear-gradient(135deg, #C8E6C9, #A5D6A7); 
        border-radius: 12px; display: flex; align-items: center; justify-content: center; 
        color: #1B5E20; font-weight: bold; font-size: 1.4rem; text-align: center; padding: 15px;
    }
    .status-label { font-size: 0.9rem; color: #555; font-weight: bold; margin-right: 8px; }
    .rating-stars { color: #FFA000; font-size: 1.1rem; }
    .crowd-icons { color: #E53935; font-size: 1.1rem; }
    
    .day-box { background: linear-gradient(90deg, #E8F5E9, #FFF); padding: 12px 25px; border-radius: 8px; font-weight: bold; margin: 35px 0 15px 0; color: #2E7D32; border-left: 5px solid #2E7D32; }
    .time-step { background-color: #E3F2FD; padding: 20px; border-radius: 10px; margin: 10px 0; border: 1px solid #BBDEFB; }
    .arrow { text-align: center; font-size: 1.5rem; color: #90CAF9; margin: 5px 0; font-weight: bold; }
    .edit-panel { background: #FFF; border: 2px solid #D4AF37; padding: 25px; border-radius: 15px; margin: 20px 0; }
    .reserve-btn { background: linear-gradient(135deg, #D32F2F, #B71C1C); color: white !important; padding: 15px 30px; border-radius: 10px; text-decoration: none; font-weight: bold; display: inline-block; text-align: center; width: 100%; border: none; }
    </style>
""", unsafe_allow_html=True)

# --- 3. ヘッダー (ロゴ + Aipia) ---
logo_base64 = get_base64_image("Aipia.png")
header_html = f'''
    <a href="/" target="_self" class="nav-container">
        {f'<img src="data:image/png;base64,{logo_base64}" class="nav-logo">' if logo_base64 else ''}
        <p class="nav-text">Aipia</p>
    </a>
'''
st.markdown(header_html, unsafe_allow_html=True)

# --- 4. セッション管理 ---
if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "plans" not in st.session_state: st.session_state.plans = []

# --- STEP 1: ホーム画面 ---
if st.session_state.step == "input":
    keyword = st.text_input("🔍 キーワード検索")
    st.write("---")
    walk_speed = st.select_slider("🚶‍♂️ 歩く速度", options=["ゆっくり", "普通", "早歩き"], value="普通")
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1: dep_place = st.text_input("🛫 出発地点", value="新宿駅")
    with col2: date_range = st.date_input("📅 旅行日程", value=(datetime.now(), datetime.now() + timedelta(days=1)))
    with col3: dep_time = st.time_input("🕔 出発時刻", value=datetime.strptime("08:00", "%H:%M").time())
    col4, col5, col6 = st.columns([2, 2, 2])
    with col4: pref = st.selectbox("📍 都道府県", PREFECTURES)
    with col5: city = st.text_input("🏠 市区町村")
    with col6: budget = st.number_input("💰 予算/人", 5000, 500000, 50000)
    col7, col8, col9 = st.columns([2, 1, 1])
    with col7: purposes = st.multiselect("✨ 目的", ["秘境探索", "美食", "温泉", "歴史", "絶景", "癒やし"], default=["秘境探索"])
    with col8: adults = st.number_input("大人", 1, 20, 2)
    with col9: kids = st.number_input("小人", 0, 20, 0)

    if st.button("⚜️ 秘境リサーチを開始する", use_container_width=True, type="primary"):
        st.session_state.form_data = {"dep": dep_place, "dest": f"{pref}{city}", "speed": walk_speed}
        prompt = f"{pref}{city}周辺の秘境を10件。名称|解説|住所|おすすめ度1-5|混雑度1-5"
        content = call_groq_safe(prompt)
        if content:
            st.session_state.found_spots = [l.split('|') for l in content.split('\n') if '|' in l]
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: スポット選択 (More機能維持) ---
elif st.session_state.step == "select_spots":
    st.markdown(f"### 📍 {st.session_state.form_data['dest']} スポットカタログ")
    for i, s in enumerate(st.session_state.found_spots):
        if len(s) < 3: continue
        name, desc = s[0], s[1]
        rating = int(s[3]) if len(s) > 3 and s[3].strip().isdigit() else 4
        crowd = int(s[4]) if len(s) > 4 and s[4].strip().isdigit() else 2
        
        st.markdown('<div class="spot-card">', unsafe_allow_html=True)
        col_img, col_txt = st.columns([1.3, 3])
        with col_img:
            st.markdown(f'<div class="spot-placeholder">{name}</div>', unsafe_allow_html=True)
        with col_txt:
            st.markdown(f"#### {name}")
            st.write(desc)
            c_s1, c_s2 = st.columns(2)
            c_s1.markdown(f'<span class="status-label">おすすめ度:</span><span class="rating-stars">{"★" * rating}{"☆" * (5-rating)}</span>', unsafe_allow_html=True)
            c_s2.markdown(f'<span class="status-label">混雑度目安:</span><span class="crowd-icons">{"●" * crowd}{"○" * (5-crowd)}</span>', unsafe_allow_html=True)
            if st.checkbox("採用する", key=f"s_{i}"):
                if name not in st.session_state.selected_spots: st.session_state.selected_spots.append(name)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # More機能
    col_more, col_next = st.columns(2)
    with col_more:
        if st.button("➕ スポットをもっと見る（追加リサーチ）", use_container_width=True):
            with st.spinner("別の秘境を探索中..."):
                prompt = f"{st.session_state.form_data['dest']}のさらに別の秘境。名称|解説|住所|4|2"
                res = call_groq_safe(prompt)
                if res:
                    new_spots = [l.split('|') for l in res.split('\n') if '|' in l]
                    st.session_state.found_spots.extend(new_spots)
                    st.rerun()
    with col_next:
        if st.button("✅ ホテル調査へ進む", type="primary", use_container_width=True):
            if not st.session_state.selected_spots: st.warning("スポットを選択してください")
            else: st.session_state.step = "hotel_survey"; st.rerun()

# --- STEP 3 & 4: ホテル・プラン生成 & 編集 ---
elif st.session_state.step == "hotel_survey":
    st.markdown("### 🏨 宿泊の希望")
    h_type = st.selectbox("タイプ", ["絶景の宿", "老舗旅館", "モダンホテル", "コスパ宿"])
    if st.button("✨ プラン案を生成", type="primary"):
        st.session_state.hotel_wish = h_type
        st.session_state.step = "plan_gen"; st.rerun()

elif st.session_state.step == "plan_gen":
    if not st.session_state.plans:
        with st.spinner("プラン作成中..."):
            for _ in range(5):
                prompt = f"{st.session_state.selected_spots}を含む2日間プランをJSON形式で。移動手段・時間・宿泊先詳細を記載。"
                res = call_groq_safe(prompt)
                try:
                    match = re.search(r"\{.*\}", res, re.DOTALL)
                    if match: st.session_state.plans.append(json.loads(match.group()))
                except: continue
    
    plan_idx = st.sidebar.selectbox("プラン比較", [f"プラン {i+1}" for i in range(len(st.session_state.plans))])
    current_data = st.session_state.plans[int(plan_idx[-1])-1]

    if st.toggle("🛠️ プランを手動編集する"):
        st.markdown('<div class="edit-panel">', unsafe_allow_html=True)
        for d_idx, day in enumerate(current_data['days']):
            for s_idx, step in enumerate(day['steps']):
                c1, c2 = st.columns([1, 3])
                step['time'] = c1.text_input("時間", step['time'], key=f"t{d_idx}{s_idx}")
                step['content'] = c2.text_input("内容", step['content'], key=f"c{d_idx}{s_idx}")
        if st.button("🔄 編集を反映"): st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    for day in current_data['days']:
        st.markdown(f'<div class="day-box">{day["label"]}</div>', unsafe_allow_html=True)
        for i, step in enumerate(day['steps']):
            st.markdown(f'<div class="time-step"><small><b>{step["time"]}</b></small><br>{step["content"]}</div>', unsafe_allow_html=True)
            if i < len(day['steps']) - 1: st.markdown('<div class="arrow">↓</div>', unsafe_allow_html=True)
    
    if st.button("🏆 確定して共有画面へ"): st.session_state.confirmed_plan = current_data; st.session_state.step = "share"; st.rerun()

elif st.session_state.step == "share":
    st.success("🎉 プラン確定！ロゴをクリックでホームに戻れます")
    data = st.session_state.confirmed_plan
    for day in data['days']:
        st.markdown(f'### {day["label"]}')
        for step in day['steps']: st.info(f"🕒 {step['time']} \n\n {step['content']}")
