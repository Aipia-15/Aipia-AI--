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
        background: #FFFFFF; border: 1px solid #D1C9B8; padding: 30px; margin-bottom: 20px;
        box-shadow: 10px 10px 30px rgba(0,0,0,0.03);
    }
    
    /* タイムライン UI */
    .day-header { font-family: 'Playfair Display', serif; font-size: 2.5rem; border-bottom: 1px solid #D4AF37; margin-bottom: 30px; }
    .time-slot { display: flex; margin-bottom: 30px; border-left: 1px solid #D4AF37; padding-left: 25px; position: relative; }
    .time-slot::before { content: ''; position: absolute; left: -6px; top: 0; width: 11px; height: 11px; background: #D4AF37; border-radius: 50%; }
    .time-val { font-family: 'Playfair Display', serif; font-weight: bold; min-width: 60px; }
    
    /* 予算内訳 & 裏技（紺色） */
    .budget-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 20px 0; }
    .budget-item { border: 1px solid #EEE; padding: 10px; text-align: center; background: #FAFAFA; }
    .tips-box { background: #1A1A1A; color: #E0D8C3; padding: 30px; margin-top: 30px; }
    .tips-title { color: #D4AF37; font-weight: bold; margin-bottom: 15px; }

    /* フッター */
    .footer { background: #FFF; padding: 60px 0; border-top: 1px solid #D4AF37; text-align: center; margin-top: 80px; }
    </style>
""", unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p></div>', unsafe_allow_html=True)

# --- STEP 1: 基本条件 & スポット検索 ---
if st.session_state.step == "input":
    st.markdown("### 01. 旅のプロファイル")
    c1, c2 = st.columns(2)
    with c1: dep = st.text_input("🛫 出発地", value="新宿駅")
    with c2: dest = st.text_input("📍 目的地", placeholder="例：下北半島、奥出雲、高野山")
    
    date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now() + timedelta(days=2)))
    
    st.write("💰 予算/人 (限度額)")
    budget_limit = st.select_slider("予算上限を選択", options=[f"{i}万円" for i in range(5, 105, 5)], value="30万円")
    
    st.write("✨ 重視ポイント（複数選択）")
    tags = st.multiselect("カテゴリー", ["秘境・絶景", "歴史・国宝", "ミシュラン美食", "温泉・隠れ家", "現代アート", "伝統工芸", "城郭巡り", "古民家再生", "パワースポット"], default=["秘境・絶景"])

    if st.button("⚜️ このエリアのスポットを調べる", use_container_width=True):
        st.session_state.form_data = {"dep": dep, "dest": dest, "budget": budget_limit, "tags": tags, "days": (date_range[1]-date_range[0]).days + 1}
        with st.spinner("厳選スポットをリサーチ中..."):
            prompt = f"{dest}周辺で{tags}に合う具体的な施設を20件、名称・解説・URLで。"
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            st.session_state.parsed_spots = re.findall(r"(名称[:：].*?)(?=名称[:：]|$)", res.choices[0].message.content, re.DOTALL)
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: スポット選択 ---
elif st.session_state.step == "select_spots":
    st.markdown("### 02. 訪れる場所を選択")
    for i, spot in enumerate(st.session_state.parsed_spots[:15]):
        name = re.search(r"名称[:：]\s*(.*)", spot).group(1).split('\n')[0].strip()
        with st.container():
            st.markdown(f'<div class="spot-card"><b>{name}</b><br>{spot[len(name)+5:200]}...</div>', unsafe_allow_html=True)
            if st.checkbox(f"{name} を旅程に入れる", key=f"s_{i}"):
                if name not in st.session_state.selected_spots: st.session_state.selected_spots.append(name)
    
    if st.button("🏨 次へ：宿泊のこだわりを選択", use_container_width=True):
        st.session_state.step = "select_hotel_pref"; st.rerun()

# --- STEP 3: 宿泊・詳細設定 ---
elif st.session_state.step == "select_hotel_pref":
    st.markdown("### 03. 宿泊と詳細のこだわり")
    c1, c2 = st.columns(2)
    with c1:
        adults = st.number_input("大人人数", 1, 10, 2)
        kids = st.number_input("子供人数", 0, 10, 0)
    with c2:
        speed = st.select_slider("🚶 歩行速度", options=["ゆったり", "標準", "アクティブ"], value="標準")
    
    h_pref = st.multiselect("🏨 宿泊のこだわり", ["露天風呂付客室", "離れ・一棟貸し", "歴史的建築", "オーシャンビュー", "サウナ完備", "部屋食", "バリアフリー対応", "オールインクルーシブ"])

    if st.button("⚜️ 究極のプランを生成する", use_container_width=True):
        st.session_state.form_data.update({"adults": adults, "kids": kids, "speed": speed, "h_pref": h_pref})
        st.session_state.step = "final_plan"; st.rerun()

# --- STEP 4: 最終プラン表示 ---
elif st.session_state.step == "final_plan":
    f = st.session_state.form_data
    if not st.session_state.final_plans:
        with st.spinner("5つのプランを編纂中..."):
            for label in ["プランA", "プランB", "プランC", "プランD", "プランE"]:
                prompt = f"""一流コンシェルジュとして執筆。{f['dep']}発 {f['dest']}行き {f['days']}日間。
                選択スポット: {st.session_state.selected_spots}
                人数: 大人{f['adults']}名 子供{f['kids']}名 / 予算上限: {f['budget']} / 宿泊: {f['h_pref']} / 速度: {f['speed']}
                
                【必須構成】
                - <div class="day-header">DAY X</div>
                - タイムライン (<div class="time-slot">)
                - 具体的店名（朝・昼・茶・晩）
                - 予算内訳（4グリッド）
                - コンシェルジュの裏技（紺色ボックス <div class="tips-box">)
                """
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                st.session_state.final_plans[label] = res.choices[0].message.content

    tabs = st.tabs(list(st.session_state.final_plans.keys()))
    for label, tab in zip(st.session_state.final_plans.keys(), tabs):
        with tab:
            st.markdown(st.session_state.final_plans[label], unsafe_allow_html=True)
            # LINE/Gmail共有
            encoded = urllib.parse.quote(st.session_state.final_plans[label])
            line_url = f"https://social-plugins.line.me/lineit/share?text={encoded}"
            gmail_url = f"https://mail.google.com/mail/?view=cm&fs=1&to=&su=Aipia旅行プラン&body={encoded}"
            st.markdown(f'<div style="text-align:center;"><a href="{line_url}" target="_blank" style="background:#06C755; color:white; padding:12px 30px; border-radius:30px; text-decoration:none; margin-right:10px;">LINEで送る</a><a href="{gmail_url}" target="_blank" style="background:#DB4437; color:white; padding:12px 30px; border-radius:30px; text-decoration:none;">Gmailで送る</a></div>', unsafe_allow_html=True)

    if st.button("最初に戻る"): st.session_state.clear(); st.rerun()

# フッター
st.markdown('<div class="footer"><div class="aipia-logo" style="font-size:2rem;">Aipia</div><div style="font-weight:bold; color:#D4AF37; margin-top:20px; letter-spacing:3px;">2025-2026 / AIPIA / GCIS</div></div>', unsafe_allow_html=True)
