import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import re
import urllib.parse

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 2. CSS：スポットカードとレイアウトの最適化
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    
    .header-container { text-align: center; padding: 40px 0; border-bottom: 1px solid #D4AF37; background: #FFF; margin-bottom: 40px; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 3.5rem; color: #111; letter-spacing: 5px; margin: 0; }
    
    /* スポット選択カード（縦並び） */
    .spot-selection-container { max-width: 800px; margin: 0 auto; }
    .spot-selection-card {
        background: #FFFFFF; border: 1px solid #E0D8C3; padding: 25px; border-radius: 12px;
        margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    .spot-title { font-size: 1.2rem; font-weight: bold; color: #111; margin-bottom: 8px; border-left: 4px solid #D4AF37; padding-left: 12px; }
    
    /* プランカード */
    .plan-outer-card {
        background: #FFFFFF; border-radius: 24px; border: 1px solid #EAEAEA; 
        padding: 40px; margin: 20px auto 60px auto; max-width: 900px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.05); color: #1A1A1A;
    }
    .day-header { font-family: 'Playfair Display', serif; font-size: 2.5rem; border-bottom: 1px solid #D4AF37; margin-bottom: 30px; }
    .tips-box { background: #1A1A1A; color: #E0D8C3; padding: 30px; border-radius: 16px; margin-top: 30px; }
    
    .share-button { 
        display: inline-block; padding: 10px 20px; border-radius: 30px; 
        text-decoration: none; font-weight: bold; color: white; margin: 5px;
    }
    .footer { background: #FFF; padding: 60px 0; border-top: 1px solid #D4AF37; text-align: center; margin-top: 80px; }
    </style>
""", unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p></div>', unsafe_allow_html=True)

# --- 関数：スポット検索 ---
def search_spots(dest, tags, count=10, exclude_names=[]):
    exclude_prompt = f"（{', '.join(exclude_names)} 以外の場所）" if exclude_names else ""
    prompt = f"{dest}周辺でテーマ「{tags}」に合う具体的で実在する観光施設・飲食店を{count}件挙げてください{exclude_prompt}。「名称：」「解説：」の形式で出力してください。"
    res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
    raw = res.choices[0].message.content
    new_spots = []
    items = re.split(r'\n(?=名称[:：])', raw)
    for item in items:
        n = re.search(r"名称[:：]\s*(.*)", item)
        d = re.search(r"解説[:：]\s*(.*)", item)
        if n: new_spots.append({"name": n.group(1).strip(), "desc": d.group(1).strip() if d else ""})
    return new_spots

# --- STEP 1: 入力 ---
if st.session_state.step == "input":
    st.markdown('<h3 style="text-align:center;">01. 旅のプロファイル</h3>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: dep = st.text_input("🛫 出発地", value="新宿駅")
    with c2: dest = st.text_input("📍 目的地", placeholder="例：下北半島")
    with c3: bud = st.text_input("💰 予算/人", value="5万円")
    
    c4, c5, c6 = st.columns(3)
    with c4: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now() + timedelta(days=2)))
    with c5: adults = st.number_input("大人人数", 1, 10, 2)
    with c6: kids = st.number_input("子供人数", 0, 10, 0)
    
    tags = st.multiselect("✨ 重視ポイント", ["秘境・絶景", "歴史・国宝", "美食", "温泉", "アート"], default=["秘境・絶景"])

    if st.button("⚜️ まずは10個のスポットを調べる", use_container_width=True, type="primary"):
        st.session_state.form_data = {"dep": dep, "dest": dest, "budget": bud, "tags": tags, "adults": adults, "kids": kids, "days": (date_range[1]-date_range[0]).days + 1 if isinstance(date_range, tuple) and len(date_range)==2 else 1}
        with st.spinner("リサーチ中..."):
            st.session_state.found_spots = search_spots(dest, tags, 10)
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: スポット選択（10個 + More） ---
elif st.session_state.step == "select_spots":
    st.markdown(f'<h3 style="text-align:center;">02. {st.session_state.form_data["dest"]} の候補地</h3>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="spot-selection-container">', unsafe_allow_html=True)
        for i, spot in enumerate(st.session_state.found_spots):
            st.markdown(f'<div class="spot-selection-card"><div class="spot-title">{spot["name"]}</div><p style="font-size:0.9rem;">{spot["desc"]}</p></div>', unsafe_allow_html=True)
            if st.checkbox(f"{spot['name']} を採用", key=f"s_{i}"):
                if spot['name'] not in st.session_state.selected_spots: st.session_state.selected_spots.append(spot['name'])
            else:
                if spot['name'] in st.session_state.selected_spots: st.session_state.selected_spots.remove(spot['name'])
        st.markdown('</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("➕ More（さらに10個出す）", use_container_width=True):
            with st.spinner("追加リサーチ中..."):
                existing = [s['name'] for s in st.session_state.found_spots]
                more = search_spots(st.session_state.form_data["dest"], st.session_state.form_data["tags"], 10, existing)
                st.session_state.found_spots.extend(more); st.rerun()
    with c2:
        if st.button("🏨 確定して次へ", use_container_width=True, type="primary"):
            if not st.session_state.selected_spots: st.error("スポットを選択してください")
            else: st.session_state.step = "select_details"; st.rerun()

# --- STEP 3: 詳細設定 ---
elif st.session_state.step == "select_details":
    st.markdown('<h3 style="text-align:center;">03. 詳細設定</h3>', unsafe_allow_html=True)
    speed = st.select_slider("🚶 歩行速度", options=["ゆったり", "標準", "アクティブ"], value="標準")
    h_pref = st.multiselect("🏨 宿泊こだわり", ["露天風呂付", "歴史建築", "部屋食", "サウナ"], default=["露天風呂付"])
    
    if st.button("⚜️ 5つのプランを生成する", use_container_width=True, type="primary"):
        st.session_state.form_data.update({"speed": speed, "h_pref": h_pref})
        st.session_state.step = "final_plan"; st.rerun()

# --- STEP 4: 最終プラン（5つ） ---
elif st.session_state.step == "final_plan":
    f = st.session_state.form_data
    if not st.session_state.final_plans:
        with st.spinner("5つのプランを編纂中..."):
            for label in ["プランA", "プランB", "プランC", "プランD", "プランE"]:
                spots_str = ", ".join(st.session_state.selected_spots)
                prompt = f"""一流コンシェルジュとして{f['days']}日間のプランを作成。選択スポット:{spots_str}、宿泊:{f['h_pref']}。
                <div class="plan-outer-card">で全体を囲み、各日に実在のホテル名を組み込め。HTML形式で出力せよ。"""
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                st.session_state.final_plans[label] = res.choices[0].message.content

    tabs = st.tabs(list(st.session_state.final_plans.keys()))
    for label, tab in zip(st.session_state.final_plans.keys(), tabs):
        with tab:
            st.markdown(st.session_state.final_plans[label], unsafe_allow_html=True)
            encoded = urllib.parse.quote(st.session_state.final_plans[label])
            st.markdown(f'<div style="text-align:center; padding:20px;"><a href="https://social-plugins.line.me/lineit/share?text={encoded}" class="share-button" style="background:#06C755;">LINE共有</a><a href="https://mail.google.com/mail/?view=cm&fs=1&body={encoded}" class="share-button" style="background:#DB4437;">Gmail共有</a></div>', unsafe_allow_html=True)

    if st.button("最初からやり直す"): st.session_state.clear(); st.rerun()

st.markdown('<div class="footer"><div class="aipia-logo" style="font-size:1.5rem;">Aipia</div><div style="font-weight:bold; color:#D4AF37; margin-top:10px;">2025 AIPIA</div></div>', unsafe_allow_html=True)
