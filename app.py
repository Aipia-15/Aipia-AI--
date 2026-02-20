import streamlit as st
from groq import Groq
from datetime import datetime

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia")

# 2. クライアント設定
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 3. デザイン (CSS) - 黒いバーの中にすべてを封じ込める
st.markdown("""
    <style>
    .stApp { background-color: #FCF9F2; }
    
    /* 巨大な黒いバー（看板） */
    .black-banner {
        background-color: #111;
        width: 100%;
        padding: 80px 0;
        text-align: center;
        margin-bottom: 60px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    /* バーの中のAipiaロゴ */
    .aipia-logo { 
        font-family: 'Georgia', serif; font-style: italic; 
        font-size: 25vw; 
        font-weight: bold; 
        color: #FCF9F2; /* 背景色のクリームで白抜き風に */
        line-height: 0.8;
        letter-spacing: -0.02em;
        margin: 0;
    }
    
    /* バーの中のサブタイトル */
    .sub-title { 
        font-size: 4vw; 
        color: #FCF9F2; 
        font-weight: bold; 
        letter-spacing: 1.5vw; 
        margin-top: 20px;
        line-height: 1;
        opacity: 0.9;
    }

    /* スマホ版調整 */
    @media (max-width: 768px) {
        .black-banner { padding: 40px 10px; }
        .aipia-logo { font-size: 80px; }
        .sub-title { font-size: 18px; letter-spacing: 3px; }
    }
    
    /* 入力フォーム周り */
    .stTextInput label, .stSelectbox label, .stSlider label {
        font-size: 14px !important; color: #444 !important;
    }
    .plan-card {
        background-color: white; padding: 40px; border-radius: 20px;
        font-size: 18px; line-height: 2; border: 1px solid #eee;
    }
    </style>
    """, unsafe_allow_html=True)

# セッション状態
if "step" not in st.session_state: st.session_state.step = "input"
if "parsed_spots" not in st.session_state: st.session_state.parsed_spots = []
if "final_plan_content" not in st.session_state: st.session_state.final_plan_content = ""

# --- ヘッダー：黒いバーの中にAipia ---
st.markdown("""
    <div class="black-banner">
        <p class="aipia-logo">Aipia</p>
        <p class="sub-title">- AIが創る、秘境への旅行プラン -</p>
    </div>
    """, unsafe_allow_html=True)

# --- STEP 1: 入力ロジック ---
if st.session_state.step == "input":
    st.markdown("<p style='text-align:center; color:#999; letter-spacing:4px;'>JOURNEY CONFIGURATION</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1: departure = st.text_input("🛫 出発地", value="東京")
    with col2: destination = st.text_input("📍 目的地", placeholder="長野、徳島など")
    with col3: keyword = st.text_input("🔍 自由入力", placeholder="歴史、温泉など")

    col4, col5, col6, col7 = st.columns([2,1,1,2])
    with col4: date_range = st.date_input("📅 日程")
    with col5: adults = st.number_input("大人", 1, 10, 2)
    with col6: kids = st.number_input("子ども", 0, 10, 0)
    with col7: walking_speed = st.select_slider("🚶 歩行速度", options=["ゆっくり", "標準", "せっかち"])

    tags = st.multiselect("🏝 テーマ", ["絶景", "秘境", "歴史", "温泉", "美食"], default=["絶景", "歴史"])
    budget = st.text_input("💰 予算/人", placeholder="例：10万円")

    if st.button("✨ Aipiaで秘境を探索する", use_container_width=True, type="primary"):
        with st.spinner("Analyzing the world..."):
            st.session_state.form_data = {"adults": adults, "kids": kids, "budget": budget, "speed": walking_speed}
            target = destination if destination else keyword
            prompt = f"{target}周辺で、テーマ『{tags}』に沿った観光地を10件。名称、解説(120文字)、予算、星5、混雑、URL。区切りは --- 。"
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            st.session_state.parsed_spots = [s.strip() for s in res.choices[0].message.content.split("---") if "名称:" in s]
            st.session_state.step = "select_spots"
            st.rerun()

# --- STEP 2: スポット選択 ---
elif st.session_state.step == "select_spots":
    st.markdown("<h2 style='text-align:center;'>SELECT DESTINATIONS</h2>", unsafe_allow_html=True)
    selected_names = []
    for i, spot in enumerate(st.session_state.parsed_spots):
        details = {line.split(":", 1)[0].strip(): line.split(":", 1)[1].strip() for line in spot.split("\n") if ":" in line}
        name = details.get("名称", f"Spot {i+1}")
        st.markdown(f'<div style="background:white; padding:25px; border-radius:15px; margin-bottom:15px; border:1px solid #eee;">', unsafe_allow_html=True)
        if st.checkbox(f"⭐ {name}", key=f"f_{i}"): selected_names.append(name)
        st.write(details.get("解説", ""))
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 この内容でプランを生成", use_container_width=True, type="primary"):
        st.session_state.selected_names = selected_names
        st.session_state.step = "final_plan"
        st.rerun()

# --- STEP 3: 最終プラン ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plan_content:
        f = st.session_state.form_data
        prompt = f"大人{f['adults']}名、歩行「{f['speed']}」。スポット：{st.session_state.selected_names}。詳細な旅行プランを作成。"
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
        st.session_state.final_plan_content = res.choices[0].message.content

    st.markdown(f'<div class="plan-card">{st.session_state.final_plan_content}</div>', unsafe_allow_html=True)
    if st.button("← 戻る"): 
        st.session_state.step = "input"; st.session_state.final_plan_content = ""; st.rerun()
