import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse
import re

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 2. デザイン（CSS） - 以前のホーム画面のトーンを維持しつつ、プラン表示を強化
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    
    .top-nav { position: absolute; top: 10px; left: 20px; z-index: 999; }
    .header-container { text-align: center; padding: 40px 0; border-bottom: 1px solid #D4AF37; background: #FFF; margin-bottom: 40px; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 3.5rem; color: #111; letter-spacing: 5px; margin: 0; }
    .aipia-sub { letter-spacing: 3px; color: #D4AF37; font-size: 1.0rem; margin-top: 5px; font-weight: bold; }

    /* スポットカード */
    .spot-selection-card {
        background: #FFFFFF; border: 1px solid #E0D8C3; border-radius: 16px;
        margin-bottom: 25px; overflow: hidden; display: flex; flex-direction: row;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
    }
    .spot-image { width: 280px; height: 180px; object-fit: cover; background: #EEE; }
    .spot-content { padding: 20px; flex: 1; }

    /* プラン表示用 */
    .timeline-item {
        background: #FFF; border-left: 5px solid #D4AF37; padding: 20px; margin-bottom: 15px;
        border-radius: 0 12px 12px 0; box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .ai-recommend-box {
        background-color: #E8F5E9; border-left: 5px solid #2E7D32; padding: 20px;
        margin: 20px 0; border-radius: 8px; color: #1B5E20; font-weight: bold;
    }
    .action-img { width: 100%; max-height: 300px; object-fit: cover; border-radius: 10px; margin: 10px 0; }
    
    .footer { background: #FFF; padding: 60px 0; border-top: 1px solid #D4AF37; text-align: center; margin-top: 80px; }
    </style>
""", unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}

# 左上のロゴ（ホーム復帰）
st.markdown('<div class="top-nav">', unsafe_allow_html=True)
if st.button("Aipia", key="home_btn"):
    st.session_state.clear()
    st.session_state.step = "input"
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">- AIが創る、秘境への旅行プラン -</p></div>', unsafe_allow_html=True)

def get_spots(dest, tags, count=10, exclude_names=[]):
    prompt = f"{dest}周辺のテーマ「{tags}」に合う実在施設を必ず{count}件。形式：@@@名称|解説|検索名@@@ で。捏造禁止。"
    res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
    items = res.choices[0].message.content.split("@@@")
    results = []
    for item in items:
        if "|" in item:
            p = item.split("|")
            name = p[0].strip()
            results.append({"name": name, "desc": p[1].strip() if len(p)>1 else "", "img": f"https://source.unsplash.com/featured/?{urllib.parse.quote(name)},Japan"})
    return results[:count]

# --- STEP 1: 入力 (ホーム画面を維持) ---
if st.session_state.step == "input":
    st.markdown('<h3 style="text-align:center;">01. Travel Profile</h3>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: dep = st.text_input("🛫 出発地", value="新宿駅")
    with c2: dest = st.text_input("📍 目的地", placeholder="例：上高地、下北半島")
    with c3: bud = st.text_input("💰 予算/人", value="5万円")
    c4, c5, c6 = st.columns(3)
    with c4: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now() + timedelta(days=2)))
    with c5: adults = st.number_input("大人", 1, 10, 2)
    with c6: kids = st.number_input("子供", 0, 10, 0)
    c7, c8 = st.columns(2)
    with c7: start_time = st.time_input("⏰ 出発希望時間", value=datetime.strptime("08:00", "%H:%M").time())
    with c8: tags = st.multiselect("✨ 重視ポイント", ["秘境・絶景", "歴史・国宝", "ミシュラン美食", "温泉", "現代アート"], default=["秘境・絶景"])

    if st.button("⚜️ 厳選スポットを調査する", use_container_width=True, type="primary"):
        st.session_state.form_data = {"dep": dep, "dest": dest, "budget": bud, "tags": tags, "adults": adults, "kids": kids, "start_time": start_time.strftime("%H:%M"), "days": (date_range[1]-date_range[0]).days + 1 if isinstance(date_range, tuple) and len(date_range)==2 else 1}
        st.session_state.found_spots = get_spots(dest, tags, 10)
        st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: スポット選択 (More機能維持) ---
elif st.session_state.step == "select_spots":
    st.markdown(f'<h3 style="text-align:center;">02. {st.session_state.form_data["dest"]} の候補地</h3>', unsafe_allow_html=True)
    for i, spot in enumerate(st.session_state.found_spots):
        st.markdown(f'<div class="spot-selection-card"><img src="{spot["img"]}" class="spot-image"><div class="spot-content"><div class="spot-title">{spot["name"]}</div><p>{spot["desc"]}</p></div></div>', unsafe_allow_html=True)
        if st.checkbox(f"{spot['name']} を採用", key=f"check_{i}", value=spot['name'] in st.session_state.selected_spots):
            if spot['name'] not in st.session_state.selected_spots: st.session_state.selected_spots.append(spot['name'])
        else:
            if spot['name'] in st.session_state.selected_spots: st.session_state.selected_spots.remove(spot['name'])
    
    c_more, c_next = st.columns(2)
    with c_more:
        if st.button("➕ More", use_container_width=True):
            st.session_state.found_spots.extend(get_spots(st.session_state.form_data["dest"], st.session_state.form_data["tags"], 10, [s['name'] for s in st.session_state.found_spots])); st.rerun()
    with c_next:
        if st.button("🏨 確定して詳細設定へ", use_container_width=True, type="primary"): st.session_state.step = "select_details"; st.rerun()

# --- STEP 3: 詳細設定 ---
elif st.session_state.step == "select_details":
    st.markdown('<h3 style="text-align:center;">03. プランニング・ポリシー</h3>', unsafe_allow_html=True)
    speed = st.select_slider("🚶 歩行速度", options=["ゆったり", "標準", "アクティブ"], value="標準")
    h_pref = st.multiselect("🏨 宿泊のこだわり", ["バリアフリー対応", "露天風呂付客室", "離れ・一棟貸し", "歴史的建築", "サウナ", "美食の宿"], default=["露天風呂付客室"])
    if st.button("⚜️ 5つの緻密なプランを生成する", use_container_width=True, type="primary"):
        st.session_state.form_data.update({"speed": speed, "h_pref": h_pref})
        st.session_state.step = "final_plan"; st.rerun()

# --- STEP 4: 最終プラン生成 (指示を全件反映) ---
elif st.session_state.step == "final_plan":
    f = st.session_state.form_data
    if not st.session_state.final_plans:
        with st.spinner("究極の旅程を5つ編纂中..."):
            for label in ["プランA", "プランB", "プランC", "プランD", "プランE"]:
                prompt = f"""一流コンシェルジュとして、{f['days']}日間の緻密なプランを作成せよ。
                1. 宿泊先は実在するホテル1箇所に固定（連泊）。
                2. 行動ごとに <div class='timeline-item'> で囲む。
                3. 各スポットに「到着時間 - 出発時間」を明記。
                4. スポット名はリンク形式 [スポット名](https://www.google.com/search?q=スポット名) にし、画像も挿入せよ。
                5. 連泊の2日目以降も具体的に記述せよ。
                6. 最後に <div class='ai-recommend-box'> で「AIおすすめ情報」を緑背景で表示せよ。HTML形式で。
                """
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                st.session_state.final_plans[label] = res.choices[0].message.content

    tabs = st.tabs(list(st.session_state.final_plans.keys()))
    for label, tab in zip(st.session_state.final_plans.keys(), tabs):
        with tab:
            st.markdown(st.session_state.final_plans[label], unsafe_allow_html=True)
            text_only = re.sub('<[^<]+?>', '', st.session_state.final_plans[label])
            encoded = urllib.parse.quote(text_only)
            c1, c2 = st.columns(2)
            with c1: st.markdown(f'<a href="https://social-plugins.line.me/lineit/share?text={encoded}" style="background:#06C755; color:white; padding:15px; display:block; text-align:center; border-radius:10px; text-decoration:none; font-weight:bold;">LINEで送信</a>', unsafe_allow_html=True)
            with c2: st.markdown(f'<a href="https://mail.google.com/mail/?view=cm&fs=1&body={encoded}" style="background:#DB4437; color:white; padding:15px; display:block; text-align:center; border-radius:10px; text-decoration:none; font-weight:bold;">Gmailで送信</a>', unsafe_allow_html=True)

st.markdown('<div class="footer"><div class="aipia-logo" style="font-size:1.5rem;">Aipia</div><div style="font-weight:bold; color:#D4AF37; margin-top:10px;">2025-2026 / AIPIA / GCIS</div></div>', unsafe_allow_html=True)
