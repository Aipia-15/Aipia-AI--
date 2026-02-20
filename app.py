import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import re
import urllib.parse

# --- ページ設定 ---
st.set_page_config(layout="wide", page_title="Aipia - Premium Travel Designer")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- デザイン (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&display=swap');

    .stApp { background-color: #F0F2F5; font-family: 'Noto Serif JP', serif; }
    
    /* ヘッダー・フッター（見本再現） */
    .header-bar { display: flex; justify-content: space-between; align-items: center; padding: 10px 40px; background: white; border-bottom: 1px solid #E0E0E0; position: sticky; top: 0; z-index: 1000; }
    .header-logo { font-family: 'Playfair Display', serif; font-size: 24px; font-weight: bold; }
    
    .footer-section { background: #F8F9FA; padding: 60px 0; border-top: 1px solid #E0E0E0; text-align: center; margin-top: 60px; }
    .footer-logo { font-family: 'Playfair Display', serif; font-size: 36px; color: #1A1A1A; }
    
    /* 共有セクション */
    .share-box { background: white; padding: 40px; border-radius: 20px; border: 1px solid #DDD; text-align: center; margin-top: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }
    .btn-line { background-color: #06C755; color: white !important; padding: 12px 30px; border-radius: 30px; text-decoration: none; font-weight: bold; margin: 10px; display: inline-block; transition: 0.3s; }
    .btn-gmail { background-color: #DB4437; color: white !important; padding: 12px 30px; border-radius: 30px; text-decoration: none; font-weight: bold; margin: 10px; display: inline-block; transition: 0.3s; }
    .btn-line:hover, .btn-gmail:hover { opacity: 0.8; transform: translateY(-2px); }
    
    @media print { .no-print { display: none !important; } }
    </style>
""", unsafe_allow_html=True)

# --- セッション管理 ---
if "step" not in st.session_state: st.session_state.step = "input"
if "confirmed_plan" not in st.session_state: st.session_state.confirmed_plan = ""

# ヘッダー
st.markdown('<div class="header-bar no-print"><div class="header-logo">Aipia</div><div style="font-size:12px;">🇯🇵 日本語 ∨</div></div>', unsafe_allow_html=True)

# --- 各ステップのロジック (要約) ---
if st.session_state.step == "input":
    st.markdown("<h1 style='text-align:center; font-family:Playfair Display; margin-top:50px;'>Aipia</h1>", unsafe_allow_html=True)
    if st.button("⚜️ プラン作成を開始", use_container_width=True):
        # 実際にはここでデータ入力
        st.session_state.confirmed_plan = "【Aipia 旅程】\n10:00 鷹の台駅発\n13:00 善光寺参拝\n宿泊：信州の隠れ宿..."
        st.session_state.step = "share_ready"; st.rerun()

elif st.session_state.step == "share_ready":
    st.markdown("### 04. プランを書き出す")
    st.markdown(f'<div style="background:white; padding:30px; border-radius:12px; border:1px solid #DDD;">{st.session_state.confirmed_plan.replace("\n", "<br>")}</div>', unsafe_allow_html=True)
    
    # 共有用URLエンコード
    plan_text = st.session_state.confirmed_plan
    encoded_plan = urllib.parse.quote(plan_text)
    
    # LINE用リンク
    line_url = f"https://social-plugins.line.me/lineit/share?text={encoded_plan}"
    
    # Gmail用リンク
    subject = urllib.parse.quote("Aipiaより：あなたの秘境旅行プラン")
    gmail_url = f"https://mail.google.com/mail/?view=cm&fs=1&to=&su={subject}&body={encoded_plan}"
    
    st.markdown(f"""
        <div class="share-box no-print">
            <h4 style="margin-bottom:20px; font-family:serif;">このプランをパートナーや自分に送る</h4>
            <a href="{line_url}" target="_blank" class="btn-line">LINEで送る</a>
            <a href="{gmail_url}" target="_blank" class="btn-gmail">Gmailで送る</a>
            <p style="font-size:12px; color:#888; margin-top:20px;">※ボタンを押すとそれぞれのアプリが立ち上がります</p>
            <hr style="margin:30px 0;">
            <button onclick="window.print()" style="background:#111; color:white; border:none; padding:10px 20px; border-radius:4px; cursor:pointer;">PDFとして保存する</button>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("最初に戻る"): st.session_state.step = "input"; st.rerun()

# フッター
st.markdown("""
    <div class="footer-section no-print">
        <div class="footer-logo">Aipia</div>
        <p class="footer-desc">あなたの望む秘境への旅行プランをAIが提案します。</p>
        <div style="font-weight:bold; color:#5D7EA3; font-size:12px;">2025-2026 / AIPIA / GCIS</div>
    </div>
""", unsafe_allow_html=True)
