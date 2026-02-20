import streamlit as st
from groq import Groq
from datetime import datetime

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia")

# 2. クライアント設定
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 3. デザイン (CSS) - 黒帯の中に巨大ロゴと改行後のサブタイトル
st.markdown("""
    <style>
    .stApp { background-color: #FCF9F2; }
    
    /* 巨大な黒いバー（看板） */
    .black-banner {
        background-color: #111;
        width: 100%;
        padding: 100px 0; /* 上下の厚みを増加 */
        text-align: center;
        margin-bottom: 80px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.3);
    }
    
    /* Aipiaロゴ：一番大きく、圧倒的な存在感 */
    .aipia-logo { 
        font-family: 'Georgia', serif; font-style: italic; 
        font-size: 30vw; /* 画面幅の3割を占める特大サイズ */
        font-weight: bold; 
        color: #FCF9F2; 
        line-height: 1.0;
        letter-spacing: -0.01em;
        margin: 0;
        display: block; /* 確実に一行占有 */
    }
    
    /* サブタイトル：改行を挟んで配置 */
    .sub-title { 
        font-size: 5vw; 
        color: #FCF9F2; 
        font-weight: bold; 
        letter-spacing: 1.8vw; 
        margin-top: 60px; /* ここで一行分の改行スペースを確保 */
        display: inline-block;
        opacity: 0.95;
        line-height: 1.2;
    }

    /* レスポンシブ調整：スマホでも「看板」を維持 */
    @media (max-width: 768px) {
        .black-banner { padding: 60px 15px; }
        .aipia-logo { font-size: 110px; }
        .sub-title { 
            font-size: 20px; 
            letter-spacing: 5px; 
            margin-top: 30px; 
        }
    }
    
    /* 入力フォームのラベル（控えめなサイズ） */
    .stTextInput label, .stSelectbox label, .stSlider label {
        font-size: 15px !important; color: #444 !important;
    }
    
    .plan-card {
        background-color: white; padding: 50px; border-radius: 30px;
        font-size: 18px; line-height: 2.2; border: 1px solid #eee;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# セッション状態の初期化
if "step" not in st.session_state: st.session_state.step = "input"
if "parsed_spots" not in st.session_state: st.session_state.parsed_spots = []
if "final_plan_content" not in st.session_state: st.session_state.final_plan_content = ""

# --- ヘッダー：漆黒のバー ＆ 巨大ロゴ ---
st.markdown("""
    <div class="black-banner">
        <p class="aipia-logo">Aipia</p>
        <p class="sub-title">- AIが創る、秘境への旅行プラン -</p>
    </div>
    """, unsafe_allow_html=True)

# --- STEP 1: 旅行条件入力 ---
if st.session_state.step == "input":
    st.markdown("<p style='text-align:center; color:#888; letter-spacing:5px; font-weight:bold;'>PLANNING INTERFACE</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1: departure = st.text_input("🛫 出発地", value="東京")
    with col2: destination = st.text_input("📍 目的地", placeholder="例：長野、徳島、北海道...")
    with col3: keyword = st.text_input("🔍 キーワード", placeholder="例：隠れ家、サウナ、古民家...")

    col4, col5, col6, col7 = st.columns([2,1,1,2])
    with col4: date_range = st.date_input("📅 日程")
    with col5: adults = st.number_input("大人", 1, 20, 2)
    with col6: kids = st.number_input("子ども", 0, 20, 0)
    with col7: walking_speed = st.select_slider("🚶 歩行速度", options=["ゆっくり", "標準", "せっかち"], value="標準")

    tags = st.multiselect("🏝 旅のテーマ", ["絶景", "秘境", "歴史", "温泉", "美食", "文化財"], default=["絶景", "秘境"])
    budget = st.text_input("💰 予算/人", placeholder="例：10万円")

    if st.button("✨ この条件で秘境を探索", use_container_width=True, type="primary"):
        with st.spinner("Analyzing destination data..."):
            st.session_state.form_data = {"adults": adults, "kids": kids, "budget": budget, "speed": walking_speed}
            target = destination if destination else keyword
            prompt = f"{target}周辺で、テーマ『{tags}』に合う具体的な観光地を10件。名称、解説(120文字程度)、予算、星5、混雑、URL。区切りは --- 。"
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            st.session_state.parsed_spots = [s.strip() for s in res.choices[0].message.content.split("---") if "名称:" in s]
            st.session_state.step = "select_spots"
            st.rerun()

# --- STEP 2: スポット選択 ---
elif st.session_state.step == "select_spots":
    st.markdown("<h2 style='text-align:center;'>CHOOSE YOUR FAVORITES</h2>", unsafe_allow_html=True)
    selected_names = []
    for i, spot in enumerate(st.session_state.parsed_spots):
        details = {line.split(":", 1)[0].strip(): line.split(":", 1)[1].strip() for line in spot.split("\n") if ":" in line}
        name = details.get("名称", f"Spot {i+1}")
        st.markdown(f'<div style="background:white; padding:30px; border-radius:20px; margin-bottom:20px; border:1px solid #eee;">', unsafe_allow_html=True)
        if st.checkbox(f"⭐ {name}", key=f"f_{i}"): selected_names.append(name)
        st.write(details.get("解説", ""))
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 最終プランを生成する", use_container_width=True, type="primary"):
        st.session_state.selected_names = selected_names
        st.session_state.step = "final_plan"
        st.rerun()

# --- STEP 3: 最終プラン表示 ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plan_content:
        f = st.session_state.form_data
        with st.spinner("AI is crafting your ultimate itinerary..."):
            prompt = f"大人{f['adults']}名、予算{f['budget']}、歩行「{f['speed']}」。スポット：{st.session_state.selected_names}。これらを元に、5つの詳細な旅行プランを作成してください。"
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            st.session_state.final_plan_content = res.choices[0].message.content

    st.markdown(f'<div class="plan-card">{st.session_state.final_plan_content}</div>', unsafe_allow_html=True)
    if st.button("← 最初の画面へ戻る", use_container_width=True): 
        st.session_state.step = "input"
        st.session_state.final_plan_content = ""
        st.rerun()
