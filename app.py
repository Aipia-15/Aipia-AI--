import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse
import re
import time

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 2. デザイン (一貫性を保つCSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    .top-nav { position: absolute; top: 10px; left: 20px; z-index: 999; }
    .header-container { text-align: center; padding: 40px 0; border-bottom: 1px solid #D4AF37; background: #FFF; margin-bottom: 40px; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 3.5rem; color: #111; letter-spacing: 5px; margin: 0; }
    .aipia-sub { letter-spacing: 3px; color: #D4AF37; font-size: 1.0rem; margin-top: 5px; font-weight: bold; }
    
    /* プランの統一スタイル */
    .timeline-item { background: #FFF; border-left: 5px solid #D4AF37; padding: 25px; margin-bottom: 15px; border-radius: 0 12px 12px 0; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
    .time-range { color: #D4AF37; font-weight: bold; font-family: 'Playfair Display', serif; font-size: 1.1rem; }
    .ai-recommend-box { background-color: #E8F5E9; border-left: 5px solid #2E7D32; padding: 25px; margin: 30px 0; border-radius: 8px; color: #1B5E20; }
    .plan-img { width: 100%; max-height: 450px; object-fit: cover; border-radius: 12px; margin: 15px 0; }
    
    .footer { background: #FFF; padding: 60px 0; border-top: 1px solid #D4AF37; text-align: center; margin-top: 80px; }
    </style>
""", unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}

# ロゴ
st.markdown('<div class="top-nav">', unsafe_allow_html=True)
if st.button("Aipia", key="home_btn"):
    st.session_state.clear()
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">- AIが創る、秘境への旅行プラン -</p></div>', unsafe_allow_html=True)

# スポット取得
def get_spots(dest, tags, count=10):
    prompt = f"{dest}周辺の「実在するピンポイントな観光施設」を必ず{count}件。名称|解説|英語キーワード 形式で。"
    res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
    lines = res.choices[0].message.content.strip().split("\n")
    results = []
    for line in lines:
        if "|" in line:
            parts = line.split("|")
            name = parts[0].strip("- ")
            # 画像はより安定したURLを使用
            results.append({"name": name, "desc": parts[1] if len(parts)>1 else "", "img": f"https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?q=80&w=800&auto=format&fit=crop&sig={urllib.parse.quote(name)}"})
    return results[:count]

# STEP 1: 入力 (ホーム画面維持)
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
    tags = st.multiselect("✨ 重視ポイント", ["秘境・絶景", "歴史", "美食", "温泉"], default=["秘境・絶景"])

    if st.button("⚜️ 厳選スポットを調査する", use_container_width=True, type="primary"):
        st.session_state.form_data = {"dep": dep, "dest": dest, "days": (date_range[1]-date_range[0]).days + 1 if isinstance(date_range, tuple) and len(date_range)==2 else 1}
        st.session_state.found_spots = get_spots(dest, tags)
        st.session_state.step = "select_spots"; st.rerun()

# STEP 2: スポット選択
elif st.session_state.step == "select_spots":
    for i, spot in enumerate(st.session_state.found_spots):
        st.markdown(f'<div class="spot-selection-card" style="display:flex; background:white; border-radius:12px; margin-bottom:15px; overflow:hidden; border:1px solid #ddd;"><img src="{spot["img"]}" style="width:200px; object-fit:cover;"><div style="padding:15px;"><h4>{spot["name"]}</h4><p>{spot["desc"]}</p></div></div>', unsafe_allow_html=True)
        if st.checkbox(f"{spot['name']}を採用", key=f"c_{i}"):
            if spot['name'] not in st.session_state.selected_spots: st.session_state.selected_spots.append(spot['name'])
    if st.button("🏨 プランを5つ作成する", use_container_width=True, type="primary"):
        st.session_state.step = "final_plan"; st.rerun()

# STEP 4: 最終プラン (記述スタイルとリンクの統一)
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plans:
        with st.spinner("記述スタイルを統一し、5つのプランを作成中..."):
            for label in ["プランA", "プランB", "プランC", "プランD", "プランE"]:
                prompt = f"""
                一流コンシェルジュとして、{st.session_state.form_data['days']}日間の旅程を以下の【絶対ルール】に従って作成せよ。
                
                【絶対ルール】
                1. 各行動を必ず <div class='timeline-item'> で囲むこと。
                2. 時間は冒頭に <span class='time-range'>到着時間 - 出発時間</span> の形式で書くこと。
                3. スポット名は [スポット名](https://www.google.com/search?q=スポット名) の形式のみを使用。URL=...という表記は禁止。
                4. 各日程の最後に <img src='https://images.unsplash.com/photo-1501785888041-af3ef285b470?q=80&w=800' class='plan-img'> を挿入せよ。
                5. 連泊の2日目以降も具体的に1日の流れを書くこと。
                6. 最後に必ず <div class='ai-recommend-box'>AIおすすめ情報：(ここに内容)</div> を出力すること。
                7. 選択されたスポット：{', '.join(st.session_state.selected_spots)}
                """
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                st.session_state.final_plans[label] = res.choices[0].message.content
                time.sleep(1) # API制限回避

    tabs = st.tabs(list(st.session_state.final_plans.keys()))
    for label, tab in zip(st.session_state.final_plans.keys(), tabs):
        with tab:
            st.markdown(st.session_state.final_plans[label], unsafe_allow_html=True)
            # LINE送信用のテキスト整形
            clean_text = re.sub('<[^<]+?>', '', st.session_state.final_plans[label])
            st.markdown(f'<a href="https://social-plugins.line.me/lineit/share?text={urllib.parse.quote(clean_text)}" style="background:#06C755; color:white; padding:15px; display:block; text-align:center; border-radius:10px; text-decoration:none; font-weight:bold;">LINEで送信</a>', unsafe_allow_html=True)

st.markdown('<div class="footer">2025-2026 / AIPIA</div>', unsafe_allow_html=True)
