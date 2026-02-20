import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse
import re

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 2. デザイン（CSS）
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    .top-nav { position: absolute; top: 10px; left: 20px; z-index: 999; }
    .header-container { text-align: center; padding: 40px 0; border-bottom: 1px solid #D4AF37; background: #FFF; margin-bottom: 40px; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 3.5rem; color: #111; letter-spacing: 5px; margin: 0; }
    .aipia-sub { letter-spacing: 3px; color: #D4AF37; font-size: 1.0rem; margin-top: 5px; font-weight: bold; }
    
    /* タイムライン */
    .timeline-item {
        background: #FFF; border-left: 5px solid #D4AF37; padding: 20px; margin-bottom: 15px;
        border-radius: 0 12px 12px 0; box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    /* AIおすすめ情報の緑背景ボックス */
    .ai-recommend-box {
        background-color: #E8F5E9; border-left: 5px solid #2E7D32; padding: 20px;
        margin: 20px 0; border-radius: 8px; color: #1B5E20; font-size: 0.95rem;
    }
    .action-img { width: 100%; max-height: 300px; object-fit: cover; border-radius: 10px; margin: 10px 0; }
    .footer { background: #FFF; padding: 40px 0; border-top: 1px solid #D4AF37; text-align: center; margin-top: 60px; }
    </style>
""", unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}

# ホーム復帰
st.markdown('<div class="top-nav">', unsafe_allow_html=True)
if st.button("Aipia", key="home_btn"):
    st.session_state.clear()
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">- AIが創る、秘境への旅行プラン -</p></div>', unsafe_allow_html=True)

# スポット取得
def get_spots(dest, tags):
    prompt = f"{dest}周辺でテーマ「{tags}」に合う実在の施設を10件。'@@@名称|解説|検索英語名@@@'の形式で。"
    res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
    items = res.choices[0].message.content.split("@@@")
    results = []
    for item in items:
        if "|" in item:
            p = item.split("|")
            name = p[0].strip()
            results.append({"name": name, "desc": p[1].strip(), "img": f"https://source.unsplash.com/featured/?{urllib.parse.quote(name)}"})
    return results

# STEP 1: 入力
if st.session_state.step == "input":
    st.markdown('<h3 style="text-align:center;">01. Travel Profile</h3>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: dest = st.text_input("📍 目的地", placeholder="例：上高地、屋久島")
    with c2: days = st.number_input("📅 日数", 1, 7, 2)
    tags = st.multiselect("✨ 重視", ["秘境・絶景", "美食", "温泉", "歴史"], default=["秘境・絶景"])
    if st.button("⚜️ 調査開始", use_container_width=True, type="primary"):
        st.session_state.form_data = {"dest": dest, "days": days}
        st.session_state.found_spots = get_spots(dest, tags)
        st.session_state.step = "select_spots"; st.rerun()

# STEP 2: スポット選択
elif st.session_state.step == "select_spots":
    for i, spot in enumerate(st.session_state.found_spots):
        st.markdown(f'<div class="timeline-item"><b>{spot["name"]}</b><br>{spot["desc"]}</div>', unsafe_allow_html=True)
        if st.checkbox(f"{spot['name']}を採用", key=f"s_{i}"):
            if spot['name'] not in st.session_state.selected_spots: st.session_state.selected_spots.append(spot['name'])
    if st.button("🏨 プラン作成（5つ）", use_container_width=True, type="primary"):
        st.session_state.step = "final_plan"; st.rerun()

# STEP 3: 最終プラン生成
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plans:
        with st.spinner("5つのプランを緻密に作成中..."):
            for label in ["プランA", "プランB", "プランC", "プランD", "プランE"]:
                prompt = f"""一流コンシェルジュとして、{st.session_state.form_data['dest']}の{st.session_state.form_data['days']}日間プランを作成せよ。
                【必須ルール】
                1. 宿泊は実在するホテル1箇所に連泊。
                2. 到着・出発時間を「09:00 - 10:30」のように明記。
                3. スポット名はリンク形式 [スポット名](https://www.google.com/search?q=スポット名) にすること。
                4. 各日程を具体的に。2日目も「1日目と同様」は禁止。
                5. 最後に <div class='ai-recommend-box'> で「AIおすすめ情報」を詳しく書け。
                6. 各行動を <div class='timeline-item'> で囲むHTML形式。
                """
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                st.session_state.final_plans[label] = res.choices[0].message.content

    tabs = st.tabs(list(st.session_state.final_plans.keys()))
    for label, tab in zip(st.session_state.final_plans.keys(), tabs):
        with tab:
            st.markdown(st.session_state.final_plans[label], unsafe_allow_html=True)
            text_only = re.sub('<[^<]+?>', '', st.session_state.final_plans[label])
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f'<a href="https://social-plugins.line.me/lineit/share?text={urllib.parse.quote(text_only)}" style="background:#06C755; color:white; padding:15px; display:block; text-align:center; border-radius:10px; text-decoration:none;">LINEで送信</a>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<a href="https://mail.google.com/mail/?view=cm&fs=1&body={urllib.parse.quote(text_only)}" style="background:#DB4437; color:white; padding:15px; display:block; text-align:center; border-radius:10px; text-decoration:none;">Gmailで送信</a>', unsafe_allow_html=True)

st.markdown('<div class="footer">2025-2026 / AIPIA</div>', unsafe_allow_html=True)
