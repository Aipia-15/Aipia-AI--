import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
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
            res = client.chat.completions.create(model=model_id, messages=[{"role": "user", "content": prompt}], temperature=0.7)
            if res.choices[0].message.content: return res.choices[0].message.content
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
    .spot-card { margin-bottom: 30px; padding: 25px; background: #FFF; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.06); border-left: 6px solid #D4AF37; }
    .spot-placeholder { width: 100%; height: 160px; background: linear-gradient(135deg, #C8E6C9, #A5D6A7); border-radius: 12px; display: flex; align-items: center; justify-content: center; color: #1B5E20; font-weight: bold; font-size: 1.4rem; text-align: center; padding: 15px; }
    .day-box { background: linear-gradient(90deg, #E8F5E9, #FFF); padding: 12px 25px; border-radius: 8px; font-weight: bold; margin: 35px 0 15px 0; color: #2E7D32; border-left: 5px solid #2E7D32; }
    .time-step { background-color: #E3F2FD; padding: 20px; border-radius: 10px; margin: 10px 0; border: 1px solid #BBDEFB; }
    .status-label { font-size: 0.9rem; color: #555; font-weight: bold; margin-right: 8px; }
    .rating-stars { color: #FFA000; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">-AIが創る、秘境への旅行プラン-</p></div>', unsafe_allow_html=True)

if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "plans" not in st.session_state: st.session_state.plans = []

# --- STEP 1: 入力 (交通手段の観点追加) ---
if st.session_state.step == "input":
    col_k1, col_k2 = st.columns([3, 1])
    with col_k1: keyword = st.text_input("🔍 キーワード検索（例：滝、廃墟、地元の名店）")
    with col_k2: transport = st.radio("🚃 優先する交通手段", ["電車・公共交通", "車・レンタカー"], horizontal=True)
    
    st.write("---")
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1: dep_place = st.text_input("🛫 出発地点", value="新宿駅")
    with col2: date_range = st.date_input("📅 旅行日程", value=(datetime.now(), datetime.now() + timedelta(days=1)))
    with col3: dep_time = st.time_input("🕔 出発時刻", value=datetime.strptime("08:00", "%H:%M").time())
    
    col4, col5, col6 = st.columns([2, 2, 2])
    with col4: pref = st.selectbox("📍 都道府県", PREFECTURES)
    with col5: city = st.text_input("🏠 市区町村（任意）")
    with col6: budget = st.number_input("💰 予算/人", 5000, 500000, 50000)

    if st.button("⚜️ 秘境リサーチを開始する", use_container_width=True, type="primary"):
        st.session_state.form_data = {"dep": dep_place, "dest": f"{pref}{city}", "transport": transport}
        prompt = f"{pref}{city}周辺で{keyword}に関連する秘境を10件。必ず『名称|解説|住所|おすすめ度1-5|混雑度1-5』の形式で出力。URL等の参考情報も解説に含めて。"
        content = call_groq_safe(prompt)
        if content:
            st.session_state.found_spots = [l.split('|') for l in content.strip().split('\n') if '|' in l]
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: スポット選択 (More機能復活) ---
elif st.session_state.step == "select_spots":
    st.markdown(f"### 📍 {st.session_state.form_data['dest']} スポットカタログ")
    for i, s in enumerate(st.session_state.found_spots):
        if len(s) < 3: continue
        rating = int(s[3]) if len(s) > 3 and s[3].strip().isdigit() else 4
        st.markdown(f'''<div class="spot-card"><div style="display:flex; gap:20px;">
            <div style="flex:1;"><div class="spot-placeholder">{s[0]}</div></div>
            <div style="flex:3;"><h4>{s[0]}</h4><p>{s[1]}</p>
            <span class="status-label">おすすめ度:</span><span class="rating-stars">{"★"*rating}</span></div>
        </div></div>''', unsafe_allow_html=True)
        if st.checkbox("採用する", key=f"s_{i}"):
            if s[0] not in st.session_state.selected_spots: st.session_state.selected_spots.append(s[0])
    
    col_more, col_next = st.columns(2)
    with col_more:
        if st.button("➕ スポットをもっと見る"):
            res = call_groq_safe(f"{st.session_state.form_data['dest']}の別の秘境候補を10件。名称|解説|住所|4|2")
            if res: st.session_state.found_spots.extend([l.split('|') for l in res.split('\n') if '|' in l]); st.rerun()
    with col_next:
        if st.button("✅ ホテル・バリアフリー調査へ", type="primary"): st.session_state.step = "hotel_survey"; st.rerun()

# --- STEP 3: ホテル・バリアフリー ---
elif st.session_state.step == "hotel_survey":
    st.markdown("### 🏨 宿泊と安心のこだわり")
    h_type = st.selectbox("宿泊タイプ", ["絶景の宿", "老舗旅館", "バリアフリー完備の宿", "コスパ重視"])
    h_barrier = st.multiselect("必要な設備", ["段差なし", "車椅子対応", "手すり", "エレベーター至近"])
    if st.button("✨ プラン案を生成する", type="primary"):
        st.session_state.hotel_data = {"type": h_type, "barrier": h_barrier}
        st.session_state.step = "plan_gen"; st.rerun()

# --- STEP 4: プラン表示・編集・交通明記 ---
elif st.session_state.step == "plan_gen":
    if not st.session_state.plans:
        with st.spinner("具体的な交通ルートを計算中..."):
            prompt = f"{st.session_state.form_data['dep']}発、{st.session_state.selected_spots}を巡る2日間プラン。移動は{st.session_state.form_data['transport']}。電車なら具体的な路線名と駅名を明記し、{{'days': [{{'label': '1日目', 'steps': [{{'time': '09:00', 'content': '内容'}}]}}]}} の形式で出力せよ。"
            res = call_groq_safe(prompt)
            match = re.search(r"\{.*\}", res, re.DOTALL)
            if match: st.session_state.plans.append(json.loads(match.group()))

    if st.session_state.plans:
        plan_idx = st.sidebar.selectbox("比較案", [f"プラン {i+1}" for i in range(len(st.session_state.plans))])
        current_data = st.session_state.plans[int(plan_idx[-1])-1]

        if st.toggle("🛠️ プランを手動編集する"):
            for d_idx, day in enumerate(current_data.get("days", [])):
                st.subheader(day.get("label"))
                for s_idx, step in enumerate(day.get("steps", [])):
                    col_e1, col_e2 = st.columns([1, 4])
                    step['time'] = col_e1.text_input(f"時間 {d_idx}-{s_idx}", step['time'])
                    step['content'] = col_e2.text_area(f"内容 {d_idx}-{s_idx}", step['content'])
        
        for day in current_data.get("days", []):
            st.markdown(f'<div class="day-box">{day.get("label")}</div>', unsafe_allow_html=True)
            for step in day.get("steps", []):
                st.markdown(f'<div class="time-step"><b>{step.get("time")}</b><br>{step.get("content")}</div>', unsafe_allow_html=True)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔄 別のプラン案を生成"): st.session_state.plans = []; st.rerun()
        with col_btn2:
            if st.button("🏆 このプランで確定・共有", type="primary"): 
                st.session_state.confirmed_plan = current_data
                st.session_state.step = "share"; st.rerun()

# --- STEP 5: 旅のしおり・共有 ---
elif st.session_state.step == "share":
    st.success("🎉 最高の旅のしおりが完成しました！")
    plan = st.session_state.confirmed_plan
    st.write("---")
    for day in plan.get("days", []):
        st.subheader(f"📅 {day.get('label')}")
        for step in day.get("steps", []):
            st.info(f"🕒 {step.get('time')} - {step.get('content')}")
    
    st.write("---")
    st.button("🔗 共有リンクをコピー（デモ）")
    if st.button("🏠 ホームに戻る"): st.session_state.clear(); st.rerun()
