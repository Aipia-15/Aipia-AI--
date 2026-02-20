import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse
import re

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 2. CSS：視覚的な区切りと確定プランのデザイン
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    
    .top-nav { position: absolute; top: 10px; left: 20px; z-index: 999; }
    .header-container { text-align: center; padding: 40px 0; border-bottom: 1px solid #D4AF37; background: #FFF; margin-bottom: 40px; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 3.5rem; color: #111; letter-spacing: 5px; margin: 0; }
    .aipia-sub { letter-spacing: 3px; color: #D4AF37; font-size: 1.0rem; margin-top: 5px; font-weight: bold; }

    /* 行動ごとの区切りカード */
    .timeline-item {
        background: #FFF; border-left: 4px solid #D4AF37; padding: 20px; margin-bottom: 15px;
        border-radius: 0 12px 12px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .time-range { font-family: 'Playfair Display', serif; font-weight: bold; color: #D4AF37; margin-bottom: 5px; }
    .action-title { font-size: 1.2rem; font-weight: bold; margin-bottom: 8px; }
    .action-img { width: 100%; max-height: 250px; object-fit: cover; border-radius: 8px; margin: 10px 0; }
    
    /* 確定済みプラン表示 */
    .final-itinerary-box {
        background: white; border: 2px solid #111; padding: 40px; border-radius: 20px;
    }
    
    .footer { background: #FFF; padding: 60px 0; border-top: 1px solid #D4AF37; text-align: center; margin-top: 80px; }
    </style>
""", unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}
if "confirmed_plan" not in st.session_state: st.session_state.confirmed_plan = None

# 左上のロゴ
st.markdown('<div class="top-nav">', unsafe_allow_html=True)
if st.button("Aipia", key="home_btn"):
    st.session_state.clear()
    st.session_state.step = "input"
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">- AIが創る、秘境への旅行プラン -</p></div>', unsafe_allow_html=True)

def get_spots(dest, tags, count=10, exclude_names=[]):
    exclude_text = f"除外：{', '.join(exclude_names)}" if exclude_names else ""
    prompt = f"{dest}周辺でテーマ「{tags}」に合う実在施設を必ず{count}件。@@@名称|解説|検索英語名@@@ 形式で。{exclude_text}"
    res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
    items = res.choices[0].message.content.split("@@@")
    results = []
    for item in items:
        if "|" in item:
            p = item.split("|")
            name = p[0].strip()
            results.append({"name": name, "desc": p[1].strip() if len(p)>1 else "", "img": f"https://source.unsplash.com/featured/?{urllib.parse.quote(p[2].strip() if len(p)>2 else name)},Japan"})
    return results[:count]

# STEP 1: 入力
if st.session_state.step == "input":
    st.markdown('<h3 style="text-align:center;">01. Travel Profile</h3>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: dep = st.text_input("🛫 出発地", value="新宿駅")
    with c2: dest = st.text_input("📍 目的地", placeholder="例：上高地、伊勢志摩")
    with c3: bud = st.text_input("💰 予算/人", value="5万円")
    c4, c5, c6 = st.columns(3)
    with c4: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now() + timedelta(days=2)))
    with c5: adults = st.number_input("大人", 1, 10, 2)
    with c6: kids = st.number_input("子供", 0, 10, 0)
    c7, c8 = st.columns(2)
    with c7: start_time = st.time_input("⏰ 出発時間", value=datetime.strptime("08:00", "%H:%M").time())
    with c8: tags = st.multiselect("✨ 重視ポイント", ["秘境・絶景", "歴史・国宝", "ミシュラン美食", "温泉", "現代アート"], default=["秘境・絶景"])

    if st.button("⚜️ スポットを調査する", use_container_width=True, type="primary"):
        st.session_state.form_data = {"dep": dep, "dest": dest, "budget": bud, "tags": tags, "adults": adults, "kids": kids, "start_time": start_time.strftime("%H:%M"), "days": (date_range[1]-date_range[0]).days + 1 if isinstance(date_range, tuple) and len(date_range)==2 else 1}
        st.session_state.found_spots = get_spots(dest, tags, 10)
        st.session_state.step = "select_spots"; st.rerun()

# STEP 2: スポット選択
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
        if st.button("🏨 詳細設定へ", use_container_width=True, type="primary"): st.session_state.step = "select_details"; st.rerun()

# STEP 3: 詳細設定
elif st.session_state.step == "select_details":
    st.markdown('<h3 style="text-align:center;">03. ポリシー設定</h3>', unsafe_allow_html=True)
    speed = st.select_slider("🚶 歩行速度", options=["ゆったり", "標準", "アクティブ"], value="標準")
    h_pref = st.multiselect("🏨 宿泊のこだわり", ["バリアフリー対応", "露天風呂付客室", "離れ・一棟貸し", "歴史的建築", "サウナ", "美食の宿"], default=["露天風呂付客室"])
    if st.button("⚜️ 5つの緻密なプランを生成", use_container_width=True, type="primary"):
        st.session_state.form_data.update({"speed": speed, "h_pref": h_pref})
        st.session_state.step = "final_plan"; st.rerun()

# STEP 4: プラン比較・確定
elif st.session_state.step == "final_plan":
    f = st.session_state.form_data
    if not st.session_state.final_plans:
        with st.spinner("究極の旅程を編纂中..."):
            for label in ["プランA", "プランB", "プランC", "プランD", "プランE"]:
                prompt = f"""一流コンシェルジュとして{f['days']}日間の緻密なプランを作成。
                出発：{f['dep']}（{f['start_time']}）、拠点：{f['dest']}。選択スポット：{', '.join(st.session_state.selected_spots)}。
                【必須形式】
                - 1拠点連泊。冒頭に <div class='base-hotel-card'> で宿泊先を表示。
                - 各行動を <div class='timeline-item'> で囲む。
                - 到着予想時間と出発予定時間を必ず「XX:XX - XX:XX」の形式で明記。
                - スポット名にはGoogle MapのURLを [スポット名](https://www.google.com/maps/search/?api=1&query=スポット名) 形式で含める。
                - 写真URLを適宜 <img class='action-img' src='https://source.unsplash.com/featured/?スポット名'> で挿入。
                - HTML形式で出力。"""
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                st.session_state.final_plans[label] = res.choices[0].message.content

    tabs = st.tabs(list(st.session_state.final_plans.keys()))
    for label, tab in zip(st.session_state.final_plans.keys(), tabs):
        with tab:
            st.markdown(st.session_state.final_plans[label], unsafe_allow_html=True)
            if st.button(f"💎 この{label}で確定する", key=f"conf_{label}", use_container_width=True, type="primary"):
                st.session_state.confirmed_plan = st.session_state.final_plans[label]
                st.session_state.step = "share_screen"; st.rerun()

# STEP 5: 確定・共有画面（旅程表のまとめ）
elif st.session_state.step == "share_screen":
    st.markdown('<h2 style="text-align:center;">⚜️ Itinerary Confirmed</h2>', unsafe_allow_html=True)
    
    # 共有用にプレーンテキストの旅程を要約
    with st.spinner("共有用テキストを作成中..."):
        summary_prompt = f"以下のHTMLプランを、LINEやメールで見やすい箇条書きの旅程表（テキスト）に要約してください。時間は到着と出発を明記し、URLも残すこと：\n\n{st.session_state.confirmed_plan}"
        summary_res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": summary_prompt}])
        summary_text = summary_res.choices[0].message.content

    st.markdown('<div class="final-itinerary-box">', unsafe_allow_html=True)
    st.markdown(st.session_state.confirmed_plan, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    encoded_text = urllib.parse.quote(summary_text)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<a href="https://social-plugins.line.me/lineit/share?text={encoded_text}" style="display:block; text-align:center; background:#06C755; color:white; padding:20px; border-radius:15px; text-decoration:none; font-weight:bold; font-size:1.2rem;">LINEで友達に送る</a>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<a href="https://mail.google.com/mail/?view=cm&fs=1&body={encoded_text}&su=最高の旅程表を共有します" style="display:block; text-align:center; background:#DB4437; color:white; padding:20px; border-radius:15px; text-decoration:none; font-weight:bold; font-size:1.2rem;">Gmailで送る</a>', unsafe_allow_html=True)

    if st.button("プラン選択に戻る"): st.session_state.step = "final_plan"; st.rerun()

st.markdown('<div class="footer"><div class="aipia-logo" style="font-size:1.5rem;">Aipia</div><div style="font-weight:bold; color:#D4AF37; margin-top:10px;">2025-2026 / AIPIA / GCIS</div></div>', unsafe_allow_html=True)
