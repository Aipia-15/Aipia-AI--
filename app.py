import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse
import re
import time

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 2. デザイン (以前のホーム画面を完全に維持)
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
    .timeline-item { background: #FFF; border-left: 5px solid #D4AF37; padding: 20px; margin-bottom: 15px; border-radius: 0 12px 12px 0; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
    .ai-recommend-box { background-color: #E8F5E9; border-left: 5px solid #2E7D32; padding: 20px; margin: 20px 0; border-radius: 8px; color: #1B5E20; font-weight: bold; }
    .footer { background: #FFF; padding: 60px 0; border-top: 1px solid #D4AF37; text-align: center; margin-top: 80px; }
    </style>
""", unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}

# ロゴ（リセット機能）
st.markdown('<div class="top-nav">', unsafe_allow_html=True)
if st.button("Aipia", key="home_btn"):
    st.session_state.clear()
    st.session_state.step = "input"
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">- AIが創る、秘境への旅行プラン -</p></div>', unsafe_allow_html=True)

# スポット取得 (ピンポイント指定を強化)
def get_spots(dest, tags, count=10):
    prompt = f"""
    {dest}周辺の「具体的な観光スポット（市・村の名前は禁止）」を{count}件挙げてください。
    建物、滝、展望台、レストラン、寺社など。形式：@@@名称|解説|検索名@@@
    """
    res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
    items = res.choices[0].message.content.split("@@@")
    results = []
    for item in items:
        if "|" in item:
            p = item.split("|")
            name = p[0].strip()
            if not any(x in name for x in ["市", "村", "町", "県"]): # 簡易フィルタ
                results.append({"name": name, "desc": p[1].strip() if len(p)>1 else "", "img": f"https://source.unsplash.com/featured/?{urllib.parse.quote(name)}"})
    return results[:count]

# STEP 1: 入力 (変更なし)
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
    st.markdown(f'<h3 style="text-align:center;">02. {st.session_state.form_data["dest"]} の候補地</h3>', unsafe_allow_html=True)
    for i, spot in enumerate(st.session_state.found_spots):
        st.markdown(f'<div class="spot-selection-card"><img src="{spot["img"]}" class="spot-image"><div class="spot-content"><div class="spot-title">{spot["name"]}</div><p>{spot["desc"]}</p></div></div>', unsafe_allow_html=True)
        if st.checkbox(f"{spot['name']} を採用", key=f"check_{i}"):
            if spot['name'] not in st.session_state.selected_spots: st.session_state.selected_spots.append(spot['name'])
    if st.button("🏨 確定してプラン生成へ", use_container_width=True, type="primary"):
        st.session_state.step = "final_plan"; st.rerun()

# STEP 3: 最終プラン (5つのタブ + 8bモデルで安定)
elif st.session_state.step == "final_plan":
    f = st.session_state.form_data
    if not st.session_state.final_plans:
        with st.spinner("5つのプランを爆速で作成中..."):
            for label in ["プランA", "プランB", "プランC", "プランD", "プランE"]:
                prompt = f"""
                一流コンシェルジュとして{f['days']}日間の実在プランを作成せよ。宿泊は{f['dest']}付近の実在ホテル。
                - 各行動を <div class='timeline-item'> で囲む。
                - 各スポットに「到着時間 - 出発時間」を明記。
                - 名称は [名称](https://www.google.com/search?q=名称) の形式。
                - 最後に <div class='ai-recommend-box'> で「AIおすすめ情報」を書くこと。
                - 選択したスポット：{', '.join(st.session_state.selected_spots)}
                """
                res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
                st.session_state.final_plans[label] = res.choices[0].message.content
                time.sleep(0.5) # 微調整の待機

    tabs = st.tabs(list(st.session_state.final_plans.keys()))
    for label, tab in zip(st.session_state.final_plans.keys(), tabs):
        with tab:
            st.markdown(st.session_state.final_plans[label], unsafe_allow_html=True)
            text_summary = re.sub('<[^<]+?>', '', st.session_state.final_plans[label])
            st.markdown(f'<a href="https://social-plugins.line.me/lineit/share?text={urllib.parse.quote(text_summary)}" style="background:#06C755; color:white; padding:15px; display:block; text-align:center; border-radius:10px; text-decoration:none; font-weight:bold;">LINEで送信</a>', unsafe_allow_html=True)

st.markdown('<div class="footer">2025-2026 / AIPIA</div>', unsafe_allow_html=True)
