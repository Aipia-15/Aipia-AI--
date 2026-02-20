import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse
import re
import time # ★重要：休憩を入れるために必要

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 2. デザイン (CSS) - ホーム画面・旅程スタイル
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    .top-nav { position: absolute; top: 10px; left: 20px; z-index: 999; }
    .header-container { text-align: center; padding: 40px 0; border-bottom: 1px solid #D4AF37; background: #FFF; margin-bottom: 40px; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 3.5rem; color: #111; letter-spacing: 5px; margin: 0; }
    .aipia-sub { letter-spacing: 3px; color: #D4AF37; font-size: 1.0rem; margin-top: 5px; font-weight: bold; }

    .spot-selection-card { background: #FFFFFF; border: 1px solid #E0D8C3; border-radius: 16px; margin-bottom: 25px; overflow: hidden; display: flex; flex-direction: row; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }
    .spot-image { width: 280px; height: 180px; object-fit: cover; background: #EEE; }
    .spot-content { padding: 20px; flex: 1; }

    .timeline-item { background: #FFF; border-left: 5px solid #D4AF37; padding: 25px; margin-bottom: 20px; border-radius: 0 12px 12px 0; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
    .time-range { color: #D4AF37; font-weight: bold; font-family: 'Playfair Display', serif; font-size: 1.3rem; display: block; margin-bottom: 10px; }
    .chuuni-title { font-size: 1.8rem; font-style: italic; color: #111; text-align: center; margin-bottom: 30px; border-bottom: 2px solid #D4AF37; padding-bottom: 10px; }
    .ai-recommend-box { background-color: #E8F5E9; border-left: 5px solid #2E7D32; padding: 25px; margin: 30px 0; border-radius: 8px; color: #1B5E20; font-weight: bold; }
    
    .footer { background: #FFF; padding: 60px 0; border-top: 1px solid #D4AF37; text-align: center; margin-top: 80px; }
    </style>
""", unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}

st.markdown('<div class="top-nav">', unsafe_allow_html=True)
if st.button("Aipia", key="home_btn"):
    st.session_state.clear()
    st.session_state.step = "input"
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">- AIが創る、秘境への旅行プラン -</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力 ---
if st.session_state.step == "input":
    st.markdown('<h3 style="text-align:center;">01. Travel Profile</h3>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: dep = st.text_input("🛫 出発地", value="新宿駅")
    with c2: dest = st.text_input("📍 目的地", placeholder="例：上高地")
    with c3: bud = st.text_input("💰 予算/人", value="5万円")
    c4, c5, c6 = st.columns(3)
    with c4: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now() + timedelta(days=2)))
    with c5: adults = st.number_input("大人", 1, 10, 2)
    with c6: kids = st.number_input("子供", 0, 10, 0)
    c7, c8 = st.columns(2)
    with c7: start_time = st.time_input("⏰ 出発時間", value=datetime.strptime("08:00", "%H:%M").time())
    with c8: tags = st.multiselect("✨ 重視", ["秘境・絶景", "歴史", "美食", "温泉"], default=["秘境・絶景"])

    if st.button("⚜️ 調査開始", use_container_width=True, type="primary"):
        st.session_state.form_data = {"dest": dest, "days": (date_range[1]-date_range[0]).days + 1 if isinstance(date_range, tuple) and len(date_range)==2 else 1}
        # スポット取得
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": f"{dest}の具体的スポット10件。名称|解説|英語名 形式で。"}])
        lines = res.choices[0].message.content.strip().split("\n")
        st.session_state.found_spots = [{"name": l.split("|")[0].strip("- "), "desc": l.split("|")[1], "img": f"https://images.unsplash.com/photo-1542051841857-5f90071e7989?q=80&w=800&sig={l}"} for l in lines if "|" in l]
        st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: スポット選択 ---
elif st.session_state.step == "select_spots":
    for i, spot in enumerate(st.session_state.found_spots):
        st.markdown(f'<div class="spot-selection-card"><img src="{spot["img"]}" class="spot-image"><div class="spot-content"><h4>{spot["name"]}</h4><p>{spot["desc"]}</p></div></div>', unsafe_allow_html=True)
        if st.checkbox(f"{spot['name']} を採用", key=f"c_{i}"):
            if spot['name'] not in st.session_state.selected_spots: st.session_state.selected_spots.append(spot['name'])
    if st.button("🏨 プラン生成", use_container_width=True, type="primary"):
        st.session_state.step = "final_plan"; st.rerun()

# --- STEP 3: 最終プラン（エラー対策版） ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plans:
        progress_bar = st.progress(0)
        for i, label in enumerate(["プランA", "プランB", "プランC", "プランD", "プランE"]):
            try:
                prompt = f"""
                一流コンシェルジュとして{st.session_state.form_data['days']}日間の旅程を作成せよ。
                1. 冒頭に <div class='chuuni-title'>旅のタイトル（厨二病風）</div>
                2. 各行動は <div class='timeline-item'> で囲む。
                3. 時間表記は独立した行：<span class='time-range'>09:00 - 10:00</span>
                4. スポット名は [名称](https://www.google.com/search?q=名称) 形式（URL=表記は禁止）。
                5. 最後に <div class='ai-recommend-box'>AIおすすめ情報</div>
                選択スポット：{', '.join(st.session_state.selected_spots)}
                """
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                st.session_state.final_plans[label] = res.choices
