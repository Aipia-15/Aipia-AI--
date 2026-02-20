import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse
import re

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 2. CSS（視覚的な区切り・タイムライン）
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    .top-nav { position: absolute; top: 10px; left: 20px; z-index: 999; }
    .header-container { text-align: center; padding: 40px 0; border-bottom: 1px solid #D4AF37; background: #FFF; margin-bottom: 40px; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 3.5rem; color: #111; letter-spacing: 5px; margin: 0; }
    .aipia-sub { letter-spacing: 3px; color: #D4AF37; font-size: 1.0rem; margin-top: 5px; font-weight: bold; }
    
    /* タイムライン表示用 */
    .timeline-item {
        background: #FFF; border-left: 5px solid #D4AF37; padding: 25px; margin-bottom: 20px;
        border-radius: 0 15px 15px 0; box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }
    .time-badge { font-family: 'Playfair Display', serif; font-weight: bold; color: #D4AF37; font-size: 1.1rem; }
    .action-img { width: 100%; max-height: 300px; object-fit: cover; border-radius: 10px; margin: 15px 0; }
    
    .footer { background: #FFF; padding: 60px 0; border-top: 1px solid #D4AF37; text-align: center; margin-top: 80px; }
    </style>
""", unsafe_allow_html=True)

# セッション管理
for key in ["step", "found_spots", "selected_spots", "final_plans", "confirmed_plan"]:
    if key not in st.session_state:
        st.session_state[key] = "input" if key == "step" else ([] if "spots" in key else {})

# ロゴ・ホーム復帰機能
st.markdown('<div class="top-nav">', unsafe_allow_html=True)
if st.button("Aipia", key="home_btn"):
    st.session_state.clear()
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">- AIが創る、秘境への旅行プラン -</p></div>', unsafe_allow_html=True)

# スポット取得関数 (実在性重視)
def get_spots(dest, tags, count=10, exclude=[]):
    prompt = f"""
    【重要】{dest}周辺に「実在する」観光地・飲食店を{count}件挙げてください。架空の場所は厳禁。
    各スポットを '@@@名称|解説|検索用英語名@@@' の形式で出力してください。
    除外リスト: {', '.join(exclude)}
    """
    res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
    items = res.choices[0].message.content.split("@@@")
    results = []
    for item in items:
        if "|" in item:
            p = item.split("|")
            name = p[0].strip()
            results.append({
                "name": name, 
                "desc": p[1].strip() if len(p)>1 else "",
                "url": f"https://www.google.com/search?q={urllib.parse.quote(name)}",
                "img": f"https://source.unsplash.com/featured/?{urllib.parse.quote(p[2].strip() if len(p)>2 else name)}"
            })
    return results[:count]

# STEP 1: 入力
if st.session_state.step == "input":
    st.markdown('<h3 style="text-align:center;">01. Travel Profile</h3>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: dep = st.text_input("🛫 出発地", "新宿駅")
    with c2: dest = st.text_input("📍 目的地", placeholder="例：上高地")
    with c3: bud = st.text_input("💰 予算", "5万円")
    c4, c5 = st.columns(2)
    with c4: start_time = st.time_input("⏰ 出発時間", datetime.strptime("08:00", "%H:%M").time())
    with c5: tags = st.multiselect("✨ 重視", ["秘境・絶景", "美食", "温泉", "歴史"], default=["秘境・絶景"])

    if st.button("⚜️ 調査開始", use_container_width=True, type="primary"):
        st.session_state.form_data = {"dep": dep, "dest": dest, "start_time": start_time.strftime("%H:%M")}
        st.session_state.found_spots = get_spots(dest, tags)
        st.session_state.step = "select_spots"; st.rerun()

# STEP 2: スポット選択
elif st.session_state.step == "select_spots":
    st.markdown(f'<h3 style="text-align:center;">02. スポット選定</h3>', unsafe_allow_html=True)
    for i, spot in enumerate(st.session_state.found_spots):
        st.markdown(f'<div class="timeline-item"><b>{spot["name"]}</b><br>{spot["desc"]}</div>', unsafe_allow_html=True)
        if st.checkbox(f"{spot['name']}を選択", key=f"s_{i}"):
            if spot['name'] not in st.session_state.selected_spots: st.session_state.selected_spots.append(spot['name'])
    
    if st.button("🏨 プラン作成へ", use_container_width=True, type="primary"):
        st.session_state.step = "final_plan"; st.rerun()

# STEP 4: プラン生成・確定
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plans:
        with st.spinner("実在するホテルとルートを検証中..."):
            for label in ["プランA", "プランB"]:
                prompt = f"""
                一流コンシェルジュとして、{st.session_state.form_data['dest']}の旅程を作成。
                【条件】
                1. 宿泊先は実在するホテル1件に固定。
                2. 行動ごとに <div class='timeline-item'> で囲む。
                3. 各項目に [到着時間 - 出発時間] を明記。
                4. スポット名は [名称](URL) 形式。URLは https://www.google.com/search?q=スポット名 とする。
                5. 最後に【自定評】としてLINE共有用のテキストまとめを付けろ。
                """
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                st.session_state.final_plans[label] = res.choices[0].message.content

    tabs = st.tabs(list(st.session_state.final_plans.keys()))
    for label, tab in zip(st.session_state.final_plans.keys(), tabs):
        with tab:
            st.markdown(st.session_state.final_plans[label], unsafe_allow_html=True)
            if st.button(f"💎 {label}を確定して共有", key=f"conf_{label}"):
                st.session_state.confirmed_plan = st.session_state.final_plans[label]
                st.session_state.step = "share"; st.rerun()

# STEP 5: 共有
elif st.session_state.step == "share":
    st.success("旅程が確定しました！")
    text_only = re.sub('<[^<]+?>', '', st.session_state.confirmed_plan) # HTMLタグ除去
    encoded = urllib.parse.quote(text_only)
    st.markdown(f'<a href="https://social-plugins.line.me/lineit/share?text={encoded}" style="background:#06C755; color:white; padding:20px; display:block; text-align:center; border-radius:10px; text-decoration:none;">LINEで送る</a>', unsafe_allow_html=True)
    if st.button("最初に戻る"): st.session_state.clear(); st.rerun()

st.markdown('<div class="footer">2025-2026 / AIPIA</div>', unsafe_allow_html=True)
