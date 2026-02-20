import streamlit as st
from groq import Groq
from datetime import datetime

# 1. ページ設定 (タブ名はシンプルに)
st.set_page_config(layout="wide", page_title="Aipia")

# 2. クライアント設定
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 3. デザイン (CSS) - 重なりとサイズを徹底修正
st.markdown("""
    <style>
    .stApp { background-color: #FCF9F2; }
    
    /* ロゴコンテナ */
    .logo-container { 
        text-align: center; 
        padding: 100px 0 150px 0; 
        position: relative;
    }
    
    /* Aipiaロゴ：絶対的な主役、何物にも重ならない */
    .aipia-logo { 
        font-family: 'Georgia', serif; font-style: italic; 
        font-size: 1000px; 
        font-weight: bold; color: #111; 
        line-height: 1.9; 
        letter-spacing: 20px; 
        margin: 0;
        position: relative;
    }
    
    /* サブタイトル：大きく、かつ棒のデザインを統合 */
    .sub-title { 
        font-size: 500px; 
        color: #111; font-weight: bold; 
        letter-spacing: 10px; 
        margin-top: 25px;
        padding: 25px 0;
        display: inline-block;
        border-top: 1px solid #111; /* 黒い棒をより太く、文字との距離を確保 */
        border-bottom: 1px solid #111;
        line-height: 1.1;
        position: relative;
        z-index: 5;
    }

    /* レスポンシブ調整（スマホで見ても小さくならないように） */
    @media (max-width: 1400px) {
        .aipia-logo { font-size: 280px; }
        .sub-title { font-size: 80px; letter-spacing: 10px; }
    }
    @media (max-width: 768px) {
        .aipia-logo { font-size: 120px; letter-spacing: 2px; }
        .sub-title { font-size: 35px; letter-spacing: 5px; border-top: 8px solid #111; border-bottom: 8px solid #111; }
    }
    
    /* フォームの文字はあえて小さく洗練させる */
    .stTextInput label, .stSelectbox label, .stSlider label {
        font-size: 16px !important; color: #555 !important;
    }
    .plan-card {
        background-color: white; padding: 60px; border-radius: 40px;
        font-size: 20px; line-height: 2.2; border: 1px solid #eee;
        box-shadow: 0 20px 50px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# セッション状態の初期化
if "step" not in st.session_state: st.session_state.step = "input"
if "parsed_spots" not in st.session_state: st.session_state.parsed_spots = []
if "final_plan_content" not in st.session_state: st.session_state.final_plan_content = ""

# --- ヘッダー ---
st.markdown("""
    <div class="logo-container">
        <p class="aipia-logo">Aipia</p>
        <p class="sub-title">- AIが創る、秘境への旅行プラン -</p>
    </div>
    """, unsafe_allow_html=True)

# --- STEP 1: 入力 ---
if st.session_state.step == "input":
    st.markdown("<h2 style='text-align:center;'>TRAVEL CONFIG</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1: departure = st.text_input("🛫 出発地", value="東京")
    with col2: destination = st.text_input("📍 目的地", placeholder="例：長野、徳島...")
    with col3: keyword = st.text_input("🔍 自由入力", placeholder="例：歴史、温泉...")

    col4, col5, col6, col7 = st.columns([2,1,1,2])
    with col4: date_range = st.date_input("📅 日程")
    with col5: adults = st.number_input("大人", 1, 10, 2)
    with col6: kids = st.number_input("子ども", 0, 10, 0)
    with col7: walking_speed = st.select_slider("🚶 歩行速度", options=["ゆっくり", "標準", "せっかち"])

    # 詳細設定
    c1, c2, c3 = st.columns(3)
    with c1: hotel_type = st.selectbox("宿タイプ", ["こだわらない", "高級旅館", "リゾート"])
    with c2: room_pref = st.multiselect("部屋・こだわり", ["和室", "洋室", "露天風呂付", "禁煙"])
    with c3: barrier = st.multiselect("バリアフリー", ["段差なし", "車椅子対応"])

    tags = st.multiselect("🏝 テーマ", ["絶景", "秘境", "歴史", "温泉", "美食"], default=["絶景", "歴史"])
    budget = st.text_input("💰 予算/人")

    if st.button("✨ 秘境を探索する", use_container_width=True, type="primary"):
        with st.spinner("Searching..."):
            st.session_state.form_data = {"adults": adults, "kids": kids, "budget": budget, "speed": walking_speed, "hotel": hotel_type, "room": room_pref, "barrier": barrier}
            target = destination if destination else keyword
            prompt = f"{target}周辺で、テーマ『{tags}』に沿った具体的な場所を10件提案。名称、解説(120文字)、予算、星5評価、混雑度、URL。区切りは --- で。"
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            st.session_state.parsed_spots = [s.strip() for s in res.choices[0].message.content.split("---") if "名称:" in s]
            st.session_state.step = "select_spots"
            st.rerun()

# --- STEP 2: スポット選択 ---
elif st.session_state.step == "select_spots":
    st.markdown("<h2 style='text-align:center;'>SELECT SPOTS</h2>", unsafe_allow_html=True)
    selected_names = []
    for i, spot in enumerate(st.session_state.parsed_spots):
        details = {line.split(":", 1)[0].strip(): line.split(":", 1)[1].strip() for line in spot.split("\n") if ":" in line}
        name = details.get("名称", f"Spot {i+1}")
        with st.container():
            st.markdown(f'<div style="background:white; padding:30px; border-radius:20px; margin-bottom:20px;">', unsafe_allow_html=True)
            if st.checkbox(f"⭐ {name}", key=f"f_{i}"): selected_names.append(name)
            st.write(details.get("解説", ""))
            st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 プランを生成", use_container_width=True, type="primary"):
        st.session_state.selected_names = selected_names
        st.session_state.step = "final_plan"
        st.rerun()

# --- STEP 3: 最終プラン（修正済み） ---
elif st.session_state.step == "final_plan":
    st.markdown("<h2 style='text-align:center;'>YOUR JOURNEY</h2>", unsafe_allow_html=True)
    
    # まだプランが生成されていない場合のみAIにリクエスト
    if not st.session_state.final_plan_content:
        f = st.session_state.form_data
        with st.spinner("AIが最高の旅程を書き上げています..."):
            prompt = f"大人{f['adults']}名、予算{f['budget']}、歩行「{f['speed']}」。宿：{f['hotel']}、こだわり：{f['room']}、バリアフリー：{f['barrier']}。スポット：{st.session_state.selected_names}。これらを元に、詳細な5つの旅行プランを作成してください。"
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            st.session_state.final_plan_content = res.choices[0].message.content

    # 生成された（または保存されている）プランを表示
    st.markdown(f'<div class="plan-card">{st.session_state.final_plan_content}</div>', unsafe_allow_html=True)

    if st.button("← 条件を変えて最初からやり直す", use_container_width=True):
        st.session_state.step = "input"
        st.session_state.final_plan_content = ""
        st.rerun()
