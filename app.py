import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse
import re
import time

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 2. デザイン (ホーム画面を維持)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    .top-nav { position: absolute; top: 10px; left: 20px; z-index: 999; }
    .header-container { text-align: center; padding: 40px 0; border-bottom: 1px solid #D4AF37; background: #FFF; margin-bottom: 40px; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 3.5rem; color: #111; letter-spacing: 5px; margin: 0; }
    .aipia-sub { letter-spacing: 3px; color: #D4AF37; font-size: 1.0rem; margin-top: 5px; font-weight: bold; }
    
    .spot-selection-card { background: #FFFFFF; border: 1px solid #E0D8C3; border-radius: 16px; margin-bottom: 25px; overflow: hidden; display: flex; flex-direction: row; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }
    .spot-image { width: 300px; height: 200px; object-fit: cover; background: #EEE; }
    .spot-content { padding: 20px; flex: 1; }
    .spot-title { font-size: 1.4rem; font-weight: bold; margin-bottom: 10px; color: #111; }

    .timeline-item { background: #FFF; border-left: 5px solid #D4AF37; padding: 20px; margin-bottom: 15px; border-radius: 0 12px 12px 0; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
    .ai-recommend-box { background-color: #E8F5E9; border-left: 5px solid #2E7D32; padding: 20px; margin: 20px 0; border-radius: 8px; color: #1B5E20; font-weight: bold; }
    .plan-img { width: 100%; max-height: 400px; object-fit: cover; border-radius: 12px; margin: 15px 0; }
    
    .footer { background: #FFF; padding: 60px 0; border-top: 1px solid #D4AF37; text-align: center; margin-top: 80px; }
    </style>
""", unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}

# ロゴ (リセット)
st.markdown('<div class="top-nav">', unsafe_allow_html=True)
if st.button("Aipia", key="home_btn"):
    st.session_state.clear()
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">- AIが創る、秘境への旅行プラン -</p></div>', unsafe_allow_html=True)

# スポット取得 (画像URL生成ロジックを修正)
def get_spots(dest, tags, count=10):
    prompt = f"""
    {dest}周辺の「実在するピンポイントな観光施設・景勝地」を必ず{count}件リストアップしてください。
    自治体名は禁止。必ず以下の形式で出力してください。
    名称|解説|写真キーワード(英語1単語)
    ---
    例:
    河童橋|上高地の象徴的な吊り橋。|bridge
    ---
    """
    # 賢い方のモデルを使用
    res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
    lines = res.choices[0].message.content.strip().split("\n")
    results = []
    for line in lines:
        if "|" in line:
            parts = line.split("|")
            if len(parts) >= 2:
                name = parts[0].replace("- ", "").strip()
                desc = parts[1].strip()
                kw = parts[2].strip() if len(parts) > 2 else "Japan"
                # 最新のUnsplash URL形式に変更
                img_url = f"https://images.unsplash.com/photo-1528164344705-4754268799af?q=80&w=800&auto=format&fit=crop" # デフォルト
                if kw:
                    img_url = f"https://images.unsplash.com/photo-1542051841857-5f90071e7989?q=80&w=800&auto=format&fit=crop&sig={urllib.parse.quote(name)}"
                
                results.append({"name": name, "desc": desc, "img": img_url})
    return results[:count]

# STEP 1: 入力
if st.session_state.step == "input":
    st.markdown('<h3 style="text-align:center;">01. Travel Profile</h3>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: dep = st.text_input("🛫 出発地", value="新宿駅")
    with c2: dest = st.text_input("📍 目的地", placeholder="例：上高地、祖谷渓")
    with c3: bud = st.text_input("💰 予算/人", value="5万円")
    c4, c5, c6 = st.columns(3)
    with c4: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now() + timedelta(days=2)))
    with c5: adults = st.number_input("大人", 1, 10, 2)
    with c6: kids = st.number_input("子供", 0, 10, 0)
    tags = st.multiselect("✨ 重視ポイント", ["秘境・絶景", "歴史", "美食", "温泉"], default=["秘境・絶景"])

    if st.button("⚜️ 厳選スポットを調査する", use_container_width=True, type="primary"):
        st.session_state.form_data = {"dep": dep, "dest": dest, "days": (date_range[1]-date_range[0]).days + 1 if isinstance(date_range, tuple) and len(date_range)==2 else 1}
        with st.spinner("実在するスポットを検索中..."):
            st.session_state.found_spots = get_spots(dest, tags)
            st.session_state.step = "select_spots"; st.rerun()

# STEP 2: スポット選択
elif st.session_state.step == "select_spots":
    st.markdown(f'<h3 style="text-align:center;">02. {st.session_state.form_data["dest"]} の候補地</h3>', unsafe_allow_html=True)
    if not st.session_state.found_spots:
        st.warning("スポットが見つかりませんでした。もう一度お試しください。")
        if st.button("戻る"): st.session_state.step = "input"; st.rerun()
    
    for i, spot in enumerate(st.session_state.found_spots):
        st.markdown(f"""
            <div class="spot-selection-card">
                <img src="{spot['img']}" class="spot-image">
                <div class="spot-content">
                    <div class="spot-title">{spot['name']}</div>
                    <p>{spot['desc']}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.checkbox(f"{spot['name']} を採用", key=f"check_{i}"):
            if spot['name'] not in st.session_state.selected_spots: st.session_state.selected_spots.append(spot['name'])
    
    if st.button("🏨 プランを5つ作成する", use_container_width=True, type="primary"):
        st.session_state.step = "final_plan"; st.rerun()

# STEP 4: 最終プラン (5つのタブ + AIおすすめ)
elif st.session_state.step == "final_plan":
    f = st.session_state.form_data
    if not st.session_state.final_plans:
        with st.spinner("緻密なプランを編纂中..."):
            for label in ["プランA", "プランB", "プランC", "プランD", "プランE"]:
                # Rate Limit対策で少しモデルを使い分けるか待機を入れる
                prompt = f"""
                一流コンシェルジュとして{f['days']}日間のプランを作成。
                - 宿泊は実在のホテル1箇所。
                - 行動ごとに <div class='timeline-item'> で囲む。
                - 時間は「09:00 - 10:30」形式。
                - スポット名はリンク形式 [名称](https://www.google.com/search?q=名称) に。
                - 画像を挿入: <img src='https://images.unsplash.com/photo-1542051841857-5f90071e7989?q=80&w=800' class='plan-img'>
                - 最後に <div class='ai-recommend-box'> で「AIおすすめ情報」を記載。
                - 選択スポット：{', '.join(st.session_state.selected_spots)}
                """
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                st.session_state.final_plans[label] = res.choices[0].message.content
                time.sleep(1) 

    tabs = st.tabs(list(st.session_state.final_plans.keys()))
    for label, tab in zip(st.session_state.final_plans.keys(), tabs):
        with tab:
            st.markdown(st.session_state.final_plans[label], unsafe_allow_html=True)
            text_summary = re.sub('<[^<]+?>', '', st.session_state.final_plans[label])
            st.markdown(f'<a href="https://social-plugins.line.me/lineit/share?text={urllib.parse.quote(text_summary)}" style="background:#06C755; color:white; padding:15px; display:block; text-align:center; border-radius:10px; text-decoration:none; font-weight:bold;">LINEで送信</a>', unsafe_allow_html=True)

st.markdown('<div class="footer">2025-2026 / AIPIA</div>', unsafe_allow_html=True)
