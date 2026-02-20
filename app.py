import streamlit as st
from groq import Groq
from datetime import datetime

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - AI Travel Planner")

# 2. デザイン（CSS）
st.markdown("""
    <style>
    .stApp { background-color: #FCF9F2; }
    
    /* ロゴエリアの調整 */
    .logo-container {
        text-align: center;
        padding-top: 20px;
        padding-bottom: 40px;
    }
    .aipia-logo {
        font-family: 'Georgia', serif; 
        font-style: italic;
        font-size: 70px; 
        font-weight: bold; 
        color: #111;
        margin-bottom: 0px;
        line-height: 1;
    }
    .sub-title {
        display: block; /* 改行を確実にする */
        font-size: 18px;
        color: #555; 
        font-weight: bold;
        letter-spacing: 3px;
        margin-top: 15px;
    }
    
    .plan-card {
        background-color: white; padding: 25px;
        border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border: 1px solid #eee; margin-top: 20px; white-space: pre-wrap;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. クライアント設定
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- ヘッダー（改行とデザインを修正） ---
st.markdown("""
    <div class="logo-container">
        <p class="aipia-logo">Aipia</p>
        <p class="sub-title">- AIが創る、秘境への旅行プラン -</p>
    </div>
    """, unsafe_allow_html=True)

# --- 選択・入力エリア ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    departure = st.text_input("🛫 出発地", value="東京")
with col2:
    destination = st.text_input("📍 目的地", placeholder="例：徳島県 祖谷")
with col3:
    date_range = st.date_input(
        "📅 日程を選択",
        value=(datetime.now(), datetime.now()),
        format="YYYY/MM
