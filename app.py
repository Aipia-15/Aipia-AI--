import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse
import json
import re

# --- 1. 基本設定 ---
st.set_page_config(layout="wide", page_title="Aipia")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

PREFECTURES = [""] + ["北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県", "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県", "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県", "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県", "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"]

def call_groq_safe(prompt):
    target_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    for model_id in target_models:
        try:
            res = client.chat.completions.create(
                model=model_id, 
                messages=[{"role": "user", "content": prompt}], 
                temperature=0.7,
                timeout=25
            )
            content = res.choices[0].message.content
            if content: return content
        except: continue
    return None

# --- 2. スタイル定義 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:wght@700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    .header-container { text-align: center; padding: 40px 0; border-bottom: 2px solid #D4AF37; background: #FFF; margin-bottom: 30px; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 3.5rem; color: #111; letter-spacing: 5px; margin: 0; }
    .aipia-sub { color: #D4AF37; font-weight: bold; letter-spacing: 2px; font-size: 1rem; margin-top: -5px; }
    .spot-card { margin-bottom: 45px; padding: 25px; background: #FFF; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.06); border-left: 6px solid #D4AF37; }
    .spot-placeholder { width: 100%; height: 160px; background: linear-gradient(135deg, #C8E6C9, #A5D6A7); border-radius: 12px; display: flex; align-items: center; justify-content: center; color: #1B5E20; font-weight: bold; font-size: 1.4rem; text-align: center; padding: 15px; }
    .day-box { background: linear-gradient(90deg, #E8F5E9, #FFF); padding: 12px 25px; border-radius: 8px; font-weight: bold; margin: 35px 0 15px 0; color: #2E7D32; border-left: 5px solid #2E7D32; }
    .time-step { background-color: #E3F2FD; padding: 20px; border-radius: 10px; margin: 10px 0; border: 1px solid #BBDEFB; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">-AIが創る、秘境への旅行プラン-</p></div>', unsafe_allow_html=True)

if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "plans" not in st.session_state: st.session_state.plans = []

# --- STEP 1: 入力 ---
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
    with col7: purposes = st.multiselect("✨ 目的", ["秘境探索", "美食", "温泉", "歴史", "絶景"], default=["秘境探索"])
    with col8: adults = st.number_input("大人", 1, 20, 2)
    with col9: kids = st.number_input("小人", 0, 20, 0)

    if st.button("⚜️ 秘境リサーチを開始する", use_container_width=True, type="primary"):
        with st.spinner("秘境を探索中..."):
            st.session_state.form_data = {"dep": dep_place, "dest": f"{pref}{city}", "speed": walk_speed}
            prompt = f"{pref}{city}周辺で{keyword}に関連する秘境を10件。名称|解説|住所|おすすめ度1-5|混雑度1-5 の形式で。"
            content = call_groq_safe(prompt)
            if content:
                st.session_state.found_spots = [l.split('|') for l in content.strip().split('\n') if '|' in l]
                st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: スポット選択 ---
elif st.session_state.step == "select_spots":
    st.markdown(f"### 📍 {st.session_state.form_data['dest']} スポットカタログ")
    for i, s in enumerate(st.session_state.found_spots):
        if len(s) < 3: continue
        st.markdown(f'''<div class="spot-card"><div class="row" style="display:flex; gap:20px;">
            <div style="flex:1;"><div class="spot-placeholder">{s[0]}</div></div>
            <div style="flex:3;"><h4>{s[0]}</h4><p>{s[1]}</p></div>
        </div></div>''', unsafe_allow_html=True)
        if st.checkbox("採用する", key=f"s_{i}"):
            if s[0] not in st.session_state.selected_spots: st.session_state.selected_spots.append(s[0])
    
    if st.button("✅ ホテル調査へ進む", type="primary"): st.session_state.step = "hotel_survey"; st.rerun()

# --- STEP 3: ホテル ---
elif st.session_state.step == "hotel_survey":
    st.markdown("### 🏨 宿泊の希望")
    h_type = st.selectbox("宿泊タイプ", ["絶景の宿", "老舗旅館", "バリアフリー完備の宿", "コスパ重視"])
    h_barrier = st.multiselect("設備希望", ["段差なし", "車椅子対応", "手すりあり"])
    if st.button("✨ プランを生成", type="primary"):
        st.session_state.hotel_data = {"type": h_type, "barrier": h_barrier}
        st.session_state.step = "plan_gen"; st.rerun()

# --- STEP 4: プラン表示（修正箇所） ---
elif st.session_state.step == "plan_gen":
    if not st.session_state.plans:
        with st.spinner("プラン作成中..."):
            prompt = f"{st.session_state.selected_spots}を含む2日間プランをJSON形式で作成せよ。構造は {{'days': [{{'label': '1日目', 'steps': [{{'time': '09:00', 'content': '内容'}}]}}]}} とすること。"
            res = call_groq_safe(prompt)
            try:
                match = re.search(r"\{.*\}", res, re.DOTALL)
                if match:
                    data = json.loads(match.group())
                    if "days" in data: st.session_state.plans.append(data)
            except: st.error("プランの解析に失敗しました。再試行してください。")

    if st.session_state.plans:
        plan_idx = st.sidebar.selectbox("プラン案", [f"プラン {i+1}" for i in range(len(st.session_state.plans))])
        current_data = st.session_state.plans[int(plan_idx[-1])-1]

        # KeyError対策: .get() を使用
        for day in current_data.get("days", []):
            st.markdown(f'<div class="day-box">{day.get("label", "日程")}</div>', unsafe_allow_html=True)
            for step in day.get("steps", []):
                st.markdown(f'<div class="time-step"><b>{step.get("time", "")}</b><br>{step.get("content", "内容なし")}</div>', unsafe_allow_html=True)
        
        if st.button("🏆 最終確定"): st.session_state.step = "share"; st.rerun()
    else:
        if st.button("🔄 再生成する"): st.rerun()

elif st.session_state.step == "share":
    st.success("旅のしおりが完成しました！")
    if st.button("🏠 最初に戻る"): st.session_state.clear(); st.rerun()
