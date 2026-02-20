import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
MODEL = "llama-3.3-70b-versatile" 

# デザインの高度なカスタマイズ (デモ画面の再現)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&display=swap');
    .stApp { background-color: #F8F9FA; color: #333; font-family: 'Noto Serif JP', serif; }
    .header-container { text-align: center; padding: 40px 0; background: #FFF; border-bottom: 3px solid #00695C; }
    .aipia-logo { font-size: 3rem; font-weight: bold; color: #111; letter-spacing: 4px; margin: 0; }
    .aipia-sub { color: #00695C; font-weight: bold; font-size: 1rem; margin-top: -5px; }
    
    /* タイムライン形式 */
    .timeline-item { border-left: 2px solid #00695C; margin-left: 20px; padding-left: 30px; position: relative; padding-bottom: 20px; }
    .timeline-dot { position: absolute; left: -7px; top: 5px; width: 12px; height: 12px; background: #00695C; border-radius: 50%; }
    .time-badge { font-weight: bold; color: #00695C; font-size: 1.1rem; }
    .plan-card { background: #FFF; border-radius: 15px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 15px; }
    
    /* 予算カード */
    .budget-grid { display: flex; gap: 15px; flex-wrap: wrap; margin-top: 20px; }
    .budget-card { background: #FFF; border-radius: 10px; padding: 15px; width: 140px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border: 1px solid #EEE; }
    .budget-icon { font-size: 1.5rem; display: block; }
    .budget-val { font-weight: bold; font-size: 1.2rem; display: block; margin-top: 5px; }
    
    .link-btn { background: #E0F2F1; color: #00695C !important; padding: 5px 15px; border-radius: 20px; text-decoration: none; font-size: 0.8rem; font-weight: bold; }
    .line-footer { background: #06C755; color: white !important; padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; display: block; margin-top: 30px; text-decoration: none; }
    </style>
""", unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">- AI Executive Concierge -</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力 ---
if st.session_state.step == "input":
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1: dep = st.text_input("🛫 出発地点", "新宿駅")
    with c2: dates = st.date_input("📅 旅行日程", [datetime.now(), datetime.now() + timedelta(days=2)])
    with c3: t = st.time_input("🕔 出発時刻", datetime.strptime("08:00", "%H:%M").time())
    
    c4, c5 = st.columns(2)
    with c4: pref = st.selectbox("📍 都道府県", PREFECTURES)
    with c5: city = st.text_input("🏠 詳細エリア")
    
    c6, c7 = st.columns(2)
    with c6: adults = st.number_input("大人", 1, 20, 2)
    with c7: kids = st.number_input("小人", 0, 20, 0)

    if st.button("⚜️ 秘境スポットをリサーチする", use_container_width=True, type="primary"):
        st.session_state.form_data = {"dep": dep, "dest": f"{pref}{city}", "days": 3}
        with st.spinner("10件のスポットを厳選中..."):
            prompt = f"{pref}{city}周辺の実在スポットを10件出せ。形式：名称|解説|予算|URL"
            res = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}])
            st.session_state.found_spots = [l.split('|') for l in res.choices[0].message.content.split('\n') if '|' in l][:10]
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: カタログ (More機能) ---
elif st.session_state.step == "select_spots":
    st.markdown(f"### 📍 {st.session_state.form_data['dest']} スポットカタログ")
    for i, s in enumerate(st.session_state.found_spots):
        with st.container():
            st.markdown(f"""<div class="plan-card"><h4>{s[0]}</h4><p>{s[1]}</p><p>💰 {s[2]}</p>
            <a class="link-btn" href="https://www.google.com/maps/search/{urllib.parse.quote(s[0])}" target="_blank">Google Mapで見る</a></div>""", unsafe_allow_html=True)
            if st.checkbox("このスポットを採用", key=f"s_{i}"): st.session_state.selected_spots.append(s[0])
    
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        if st.button("➕ More (さらに10個追加)"):
            prompt = f"{st.session_state.form_data['dest']}周辺で別の実在スポットを10件出せ。形式：名称|解説|予算|URL"
            res = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}])
            st.session_state.found_spots.extend([l.split('|') for l in res.choices[0].message.content.split('\n') if '|' in l][:10])
            st.rerun()
    with c_m2:
        if st.button("✅ プランを生成する", type="primary"): st.session_state.step = "final_plan"; st.rerun()

# --- STEP 3: タイムラインプラン & 予算 ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plans:
        with st.spinner("3日間のリッチなプランを生成中..."):
            for label in ["Plan A", "Plan B"]:
                prompt = f"{st.session_state.form_data['dest']} 3日間。宿泊施設を必ず含め。形式：日|時間|予定|予算カテゴリ"
                res = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}])
                st.session_state.final_plans[label] = [l.split('|') for l in res.choices[0].message.content.split('\n') if '|' in l]

    chosen = st.radio("プラン選択", list(st.session_state.final_plans.keys()), horizontal=True)
    
    # タイムライン表示
    for item in st.session_state.final_plans[chosen]:
        if len(item) >= 3:
            st.markdown(f"""
            <div class="timeline-item"><div class="timeline-dot"></div>
                <span class="time-badge">{item[1]}</span>
                <div class="plan-card">
                    <b>{item[2]}</b><br>
                    <a class="link-btn" href="https://www.google.com/maps/search/{urllib.parse.quote(item[2])}" target="_blank">公式サイト</a>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 予算内訳 (デモ再現)
    st.markdown("### 予算の内訳")
    st.markdown("""
    <div class="budget-grid">
        <div class="budget-card"><span class="budget-icon">🚆</span>交通費<span class="budget-val">¥20,000</span></div>
        <div class="budget-card"><span class="budget-icon">🏨</span>宿泊費<span class="budget-val">¥14,000</span></div>
        <div class="budget-card"><span class="budget-icon">🏔️</span>体験料<span class="budget-val">¥5,000</span></div>
        <div class="budget-card"><span class="budget-icon">🍣</span>食費<span class="budget-val">¥11,000</span></div>
    </div>
    <div style="text-align:right; font-size:2rem; font-weight:bold; color:#00695C; margin-top:20px;">合計概算 ¥50,000</div>
    """, unsafe_allow_html=True)

    line_txt = urllib.parse.quote(f"【Aipia】旅行プラン\n{chosen}を確認してください。")
    st.markdown(f'<a href="https://line.me/R/msg/text/?{line_txt}" class="line-footer">LINEで旅程を共有する</a>', unsafe_allow_html=True)
