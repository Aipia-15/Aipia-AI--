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
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">-AIが創る、秘境への旅行プラン-</p></div>', unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "plans" not in st.session_state: st.session_state.plans = []
if "spot_count" not in st.session_state: st.session_state.spot_count = 0

# --- STEP 1: ホーム画面入力 ---
if st.session_state.step == "input":
    col_k1, col_k2 = st.columns([3, 1])
    with col_k1: keyword = st.text_input("🔍 キーワード検索")
    with col_k2: transport = st.radio("🚃 交通手段", ["電車・公共交通", "車・レンタカー"], horizontal=True)
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1: dep_place = st.text_input("🛫 出発地点", value="新宿駅")
    with col2: date_range = st.date_input("📅 旅行日程", value=(datetime.now(), datetime.now() + timedelta(days=1)))
    with col3: dep_time = st.time_input("🕔 出発時刻", value=datetime.strptime("08:00", "%H:%M").time())
    
    col4, col5, col6 = st.columns([2, 2, 2])
    with col4: pref = st.selectbox("📍 都道府県", PREFECTURES)
    with col5: city = st.text_input("🏠 市区町村")
    with col6: budget = st.number_input("💰 予算/人", 5000, 500000, 50000)
    
    col7, col8, col9 = st.columns([2, 1, 1])
    with col7: purposes = st.multiselect("✨ 目的", ["秘境探索", "美食", "温泉", "歴史", "絶景", "海・水辺", "街歩き"], default=["秘境探索"])
    with col8: adults = st.number_input("大人", 1, 20, 2)
    with col9: kids = st.number_input("小人", 0, 20, 0)

    if st.button("⚜️ 秘境リサーチを開始する", use_container_width=True, type="primary"):
        st.session_state.form_data = {"dep": dep_place, "dest": f"{pref}{city}", "transport": transport}
        prompt = f"{pref}{city}周辺で{keyword}に関連するスポットを10件。山に偏らず、海、街、歴史施設を含めること。名称|解説|住所|おすすめ度1-5|混雑度1-5 の形式で。"
        content = call_groq_safe(prompt)
        if content:
            st.session_state.found_spots = [l.split('|') for l in content.strip().split('\n') if '|' in l]
            st.session_state.spot_count = 10
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: スポット選択 (More機能・連番対応) ---
elif st.session_state.step == "select_spots":
    st.markdown(f"### 📍 候補スポット")
    for i, s in enumerate(st.session_state.found_spots):
        st.markdown(f'''<div class="spot-card"><div style="display:flex; gap:20px;">
            <div style="flex:1;"><div class="spot-placeholder">{i+1}. {s[0]}</div></div>
            <div style="flex:3;"><h4>{s[0]}</h4><p>{s[1]}</p></div>
        </div></div>''', unsafe_allow_html=True)
        if st.checkbox(f"スポット {i+1} を採用", key=f"s_{i}"):
            if s[0] not in st.session_state.selected_spots: st.session_state.selected_spots.append(s[0])
    
    col_more, col_next = st.columns(2)
    with col_more:
        if st.button("➕ スポットをもっと見る"):
            prompt = f"{st.session_state.form_data['dest']}の別のジャンル（海、街並み、伝統文化）のスポットを10件。名称|解説|住所|4|2"
            res = call_groq_safe(prompt)
            if res:
                new_spots = [l.split('|') for l in res.split('\n') if '|' in l]
                st.session_state.found_spots.extend(new_spots)
                st.session_state.spot_count += len(new_spots)
                st.rerun()
    with col_next:
        if st.button("✅ ホテル・プラン生成へ", type="primary"): st.session_state.step = "hotel_survey"; st.rerun()

# --- STEP 3: ホテル・バリアフリー ---
elif st.session_state.step == "hotel_survey":
    st.markdown("### 🏨 宿泊の希望")
    h_type = st.selectbox("宿泊タイプ", ["絶景の宿", "老舗旅館", "バリアフリー完備の宿", "モダンホテル"])
    h_barrier = st.multiselect("必要なバリアフリー設備", ["段差なし", "車椅子対応", "手すり"])
    if st.button("✨ プランを生成する", type="primary"):
        st.session_state.hotel_data = {"type": h_type, "barrier": h_barrier}
        st.session_state.step = "plan_gen"; st.rerun()

# --- STEP 4: プラン表示（到着・出発時間を明記、ホテル明記、編集機能） ---
elif st.session_state.step == "plan_gen":
    if not st.session_state.plans:
        with st.spinner("詳細な交通ルートと時間を計算中..."):
            prompt = f"""
            {st.session_state.form_data['dep']}発、{st.session_state.selected_spots}を巡る2日間プラン。
            交通手段: {st.session_state.form_data['transport']}
            宿泊: {st.session_state.hotel_data['type']}（具体的なホテル名を提案すること）
            各工程で「到着時間」と「出発時間」を必ず両方明記。
            電車なら路線名・駅名を、車ならIC名を具体的に記載。
            形式: {{'days': [{{'label': '1日目', 'steps': [{{'arrival': '09:00', 'departure': '10:30', 'content': '内容'}}]}}]}}
            """
            res = call_groq_safe(prompt)
            match = re.search(r"\{.*\}", res, re.DOTALL)
            if match: st.session_state.plans.append(json.loads(match.group()))

    if st.session_state.plans:
        plan = st.session_state.plans[0]
        if st.toggle("🛠️ プランを手動編集する"):
            for d_idx, day in enumerate(plan.get("days", [])):
                for s_idx, step in enumerate(day.get("steps", [])):
                    c1, c2, c3 = st.columns([1, 1, 3])
                    step['arrival'] = c1.text_input(f"着 {d_idx}-{s_idx}", step.get('arrival', ''))
                    step['departure'] = c2.text_input(f"出 {d_idx}-{s_idx}", step.get('departure', ''))
                    step['content'] = c3.text_area(f"内容 {d_idx}-{s_idx}", step['content'])
        
        for day in plan.get("days", []):
            st.markdown(f'<div class="day-box">{day.get("label")}</div>', unsafe_allow_html=True)
            for step in day.get("steps", []):
                st.markdown(f'''<div class="time-step">
                    <span style="color:#D32F2F; font-weight:bold;">{step.get('arrival')}着 / {step.get('departure')}発</span><br>
                    {step.get('content')}</div>''', unsafe_allow_html=True)
        
        if st.button("🏆 確定・共有へ", type="primary"): st.session_state.step = "share"; st.rerun()

# --- STEP 5: 確定・共有 ---
elif st.session_state.step == "share":
    st.success("🎉 プランが確定しました！")
    plan = st.session_state.plans[0]
    for day in plan.get("days", []):
        st.subheader(day.get("label"))
        for step in day.get("steps", []):
            st.info(f"🕒 {step.get('arrival')}着 / {step.get('departure')}発\n\n{step.get('content')}")
    
    if st.button("🏠 ホームへ戻る"): st.session_state.clear(); st.rerun()
