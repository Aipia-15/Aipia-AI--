import streamlit as st
from groq import Groq
from datetime import datetime

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - AI Travel Planner")

# 2. クライアント設定
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 3. デザイン (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #FCF9F2; }
    .logo-container { text-align: center; padding: 40px 0; }
    .aipia-logo { 
        font-family: 'Georgia', serif; font-style: italic; 
        font-size: 100px; font-weight: bold; color: #111; margin-bottom: -10px; 
    }
    .sub-title { font-size: 20px; color: #555; font-weight: bold; letter-spacing: 4px; }
    .plan-card { 
        background-color: white; padding: 25px; border-radius: 20px; 
        box-shadow: 0 10px 25px rgba(0,0,0,0.05); border: 1px solid #eee; 
        margin-top: 20px; white-space: pre-wrap;
    }
    .inspi-card {
        background-color: white; padding: 15px; border-radius: 12px;
        border: 1px solid #eee; text-align: center; height: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# セッション状態の管理
if "step" not in st.session_state: st.session_state.step = "input"
if "spots_list" not in st.session_state: st.session_state.spots_list = ""

# --- ヘッダー ---
st.markdown("""
    <div class="logo-container">
        <p class="aipia-logo">Aipia</p>
        <p class="sub-title">- AIが創る、秘境への旅行プラン -</p>
    </div>
    """, unsafe_allow_html=True)

# --- STEP 1: 入力画面 ---
if st.session_state.step == "input":
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1: departure = st.text_input("🛫 出発地", value="東京")
    with col2: destination = st.text_input("📍 目的地（空欄でもOK）", placeholder="例：四国、九州...")
    with col3: keyword = st.text_input("🔍 キーワード検索", placeholder="例：サウナ、廃校、雲海...")

    col4, col5, col6 = st.columns([2, 1, 1])
    with col4: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now()))
    with col5: adults = st.number_input("大人", min_value=1, value=2)
    with col6: kids = st.number_input("子ども", min_value=0, value=0)

    tags = st.multiselect("🏝 旅のテーマ", 
        ["絶景", "秘境", "温泉", "郷土料理", "アクティビティ", "サウナ", "離島", "歴史・文化", "エモい", "子連れ", "贅沢体験"], 
        default=["絶景"])
    budget = st.text_input("💰 予算（1人あたり）", placeholder="例：10万円")

    if st.button("✨ この条件でスポットを探す", use_container_width=True, type="primary"):
        with st.spinner("AIが厳選スポットを10件抽出中..."):
            target = destination if destination else keyword
            prompt = f"{target}周辺で、テーマ『{tags}』に沿った観光スポットを10件教えてください。公式サイトURLも付けてください。"
            res =
            
