import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import re
import urllib.parse
import time

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 2. 高級感 & 見本再現 CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');
    .stApp { background-color: #F4F1EE; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    
    /* ヘッダー */
    .header-container { text-align: center; padding: 40px 0; border-bottom: 1px solid #D4AF37; background: #FFF; margin-bottom: 40px; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 4rem; color: #111; letter-spacing: 5px; margin: 0; }
    
    /* カードデザイン */
    .spot-card, .plan-card {
        background: #FFFFFF; border: 1px solid #D1C9B8; padding: 40px; margin-bottom: 25px;
        box-shadow: 15px 15px 40px rgba(0,0,0,0.03);
    }
    
    /* タイムライン UI */
    .day-header { font-family: 'Playfair Display', serif; font-size: 2.5rem; border-bottom: 1px solid #D4AF37; margin-bottom: 30px; margin-top: 50px; }
    .time-slot { display: flex; margin-bottom: 35px; border-left: 1px solid #D4AF37; padding-left: 30px; position: relative; }
    .time-slot::before { content: ''; position: absolute; left: -6px; top: 0; width: 11px; height: 11px; background: #D4AF37; border-radius: 50%; }
    .time-val { font-family: 'Playfair Display', serif; font-weight: bold; min-width: 70px; font-size: 1.1rem; }
    .spot-name { font-weight: bold; font-size: 1.3rem; margin-bottom: 8px; }
    .spot-desc { line-height: 2.0; color: #333; }
    
    /* 予算内訳 & 裏技（紺色） */
    .budget-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 25px 0; }
    .budget-item { border: 1px solid #EEE; padding: 15px; text-align: center; background: #FAFAFA; }
    .tips-box { background: #1A1A1A; color: #E0D8C3; padding: 40px; margin-top: 40px; }
    .tips-title { color: #D4AF37; font-weight: bold; font-size: 1.2rem; margin-bottom: 20px; letter-spacing: 2px; }
    .tip-item { display: flex; margin-bottom: 15px; }
    .tip-num { color: #D4AF37; font-weight: bold; margin-right: 15px; }

    /* フッター */
    .footer { background: #FFF; padding: 80px 0; border-top: 1px solid #D4AF37; text-align: center; margin-top: 100px; }
    </style>
""", unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p></div>', unsafe_allow_html=True)

# --- STEP 1: 基本条件 & スポット検索 ---
if st.session_state.step == "input":
    st.markdown('<h3 style="text-align:center;">01. 旅のプロファイル</h3>', unsafe_allow_html=True)
    with st.container():
        c1, c2, c3 = st.columns(3)
        with c1: dep = st.text_input("🛫 出発地", value="新宿駅")
        with c2: dest = st.text_input("📍 目的地", placeholder="例：下北半島、奥出雲")
        with c3: bud = st.text_input("💰 予算/人", value="15万円")
        
        c4, c5, c6 = st.columns(3)
        with c4: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now() + timedelta(days=2)))
        with c5: adults = st.number_input("大人", 1, 10, 2)
        with c6: kids = st.number_input("子供", 0, 10, 0)
        
        tags = st.multiselect("✨ 重視ポイント", ["秘境・絶景", "歴史・国宝", "ミシュラン美食", "温泉・癒やし", "現代アート", "伝統工芸", "パワースポット", "地酒・ワイナリー"], default=["秘境・絶景"])

    if st.button("⚜️ このエリアのスポットを調べる", use_container_width=True, type="primary"):
        st.session_state.form_data = {
            "dep": dep, "dest": dest, "budget": bud, "tags": tags, 
            "days": (date_range[1]-date_range[0]).days + 1,
            "adults": adults, "kids": kids
        }
        with st.spinner("現地情報を精査し、候補地を選定しています..."):
            prompt = f"{dest}周辺で{tags}に合う具体的な施設を20件、名称・解説・URLで。広域地名は禁止。"
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            st.session_state.parsed_spots = re.findall(r"(名称[:：].*?)(?=名称[:：]|$)", res.choices[0].message.content, re.DOTALL)
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: スポット選択 ---
elif st.session_state.step == "select_spots":
    st.markdown(f"### 02. {st.session_state.form_data['dest']} の厳選スポット")
    st.write("旅程に組み込みたい場所をすべて選択してください。")
    
    for i, spot in enumerate(st.session_state.parsed_spots[:20]):
        name_match = re.search(r"名称[:：]\s*(.*)", spot)
        name = name_match.group(1).split('\n')[0].strip() if name_match else f"Spot {i}"
        with st.container():
            st.markdown(f'<div class="spot-card"><b>{name}</b><br><small>{spot[:250]}...</small></div>', unsafe_allow_html=True)
            if st.checkbox(f"{name} を選択", key=f"s_{i}"):
                if name not in st.session_state.selected_spots: st.session_state.selected_spots.append(name)
    
    if st.button("🏨 次へ：詳細なこだわり設定", use_container_width=True):
        st.session_state.step = "select_details"; st.rerun()

# --- STEP 3: 宿泊・詳細設定 ---
elif st.session_state.step == "select_details":
    st.markdown("### 03. 宿泊とプランの調整")
    c1, c2 = st.columns(2)
    with c1:
        speed = st.select_slider("🚶 歩行速度", options=["ゆったり", "標準", "アクティブ"], value="標準")
    with c2:
        h_pref = st.multiselect("🏨 宿泊のこだわり", ["露天風呂付客室", "離れ・一棟貸し", "歴史的建築", "部屋食", "バリアフリー対応", "サウナ完備"])

    if st.button("⚜️ 究極のプランを編纂する", use_container_width=True, type="primary"):
        st.session_state.form_data.update({"speed": speed, "h_pref": h_pref})
        st.session_state.step = "final_plan"; st.rerun()

# --- STEP 4: 最終プラン表示 ---
elif st.session_state.step == "final_plan":
    f = st.session_state.form_data
    if not st.session_state.final_plans:
        with st.spinner("5通りの極上プランを作成中..."):
            for label in ["プランA", "プランB", "プランC", "プランD", "プランE"]:
                prompt = f"""一流コンシェルジュとして執筆。{f['dep']}発 {f['dest']}行き {f['days']}日間。
                選択した場所: {st.session_state
