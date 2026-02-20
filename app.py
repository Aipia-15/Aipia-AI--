import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import re

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - AI秘境コンシェルジュ")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 2. デザイン (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #FCF9F2; }
    .black-banner { background-color: #111; width: 100%; padding: 30px 0; text-align: center; margin-bottom: 20px; }
    .aipia-logo { font-family: 'Georgia', serif; font-style: italic; font-size: 6vw; font-weight: bold; color: #FCF9F2; line-height: 1.0; margin: 0; }
    .spot-card { background-color: white; padding: 20px; border-radius: 15px; margin-bottom: 20px; border: 1px solid #eee; }
    .plan-box { background-color: white; border-radius: 15px; padding: 35px; border: 1px solid #ddd; line-height: 1.8; margin-bottom: 20px; }
    .advice-title { color: #D4AF37; font-weight: bold; font-size: 20px; margin-top: 20px; }
    
    /* 印刷用設定 */
    @media print {
        .no-print, .stButton, .stSidebar, .stTabs { display: none !important; }
        .stApp { background-color: white !important; }
        .plan-box { border: none !important; box-shadow: none !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# セッション状態の初期化
if "step" not in st.session_state: st.session_state.step = "input"
if "parsed_spots" not in st.session_state: st.session_state.parsed_spots = []
if "display_count" not in st.session_state: st.session_state.display_count = 10
if "selected_names" not in st.session_state: st.session_state.selected_names = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}
if "confirmed_plan" not in st.session_state: st.session_state.confirmed_plan = None

st.markdown('<div class="black-banner no-print"><p class="aipia-logo">Aipia</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力 ---
if st.session_state.step == "input":
    st.markdown("### 1. 旅行条件の設定")
    col1, col2, col3 = st.columns(3)
    with col1: departure = st.text_input("🛫 出発地 (必須)", key="dep", placeholder="例：東京駅")
    with col2: destination = st.text_input("📍 目的地", placeholder="地域名・駅名など")
    with col3: budget = st.text_input("💰 予算/人 (必須)", placeholder="10万円など")

    col_date, col_pa, col_pc, col_speed = st.columns([3, 1, 1, 2])
    with col_date: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now() + timedelta(days=1)))
    with col_pa: adults = st.number_input("大人", 1, 10, 2)
    with col_pc: kids = st.number_input("子供", 0, 10, 0)
    with col_speed: walking_speed = st.select_slider("🚶 歩行速度", options=["ゆっくり", "標準", "せっかち"], value="標準")

    st.markdown("#### 🏨 宿泊・バリアフリー詳細設定")
    h1, h2, h3 = st.columns(3)
    with h1: 
        hotel_style = st.selectbox("宿泊スタイル", 
            ["こだわらない", "高級旅館", "リゾートホテル", "古民家・民宿", "ビジネスホテル", "グランピング", "一棟貸し別荘"])
    with h2: 
        room_pref = st.multiselect("客室へのこだわり", 
            ["露天風呂付", "和洋室", "オーシャンビュー", "マウンテンビュー", "サウナ付", "部屋食", "禁煙席重視", "ペット同伴"])
    with h3: 
        barrier_free = st.multiselect("バリアフリー・サポート", 
            ["車椅子レンタル", "段差なし(フルフラット)", "エレベーター至近", "手すりあり", "多目的トイレ", "貸切家族風呂", "刻み食対応"])

    if st.button("✨ 秘境スポットを探索", use_container_width=True, type="primary"):
        if departure and budget and len(date_range) == 2:
            st.session_state.form_data = {
                "departure": departure, "destination": destination, "budget": budget, 
                "adults": adults, "kids": kids, "speed": walking_speed, 
                "dates": f"{date_range[0]}〜{date_range[1]}", 
                "hotel": f"{hotel_style} / 希望:{room_pref} / BF:{barrier_free}"
            }
            with st.spinner("スポットを20件生成中..."):
                prompt = f"{destination}周辺の観光地を20件教えてください。日本語のみ。中国語や謎の記号は禁止。「名称：」「解説：」「URL：」の形式で。"
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                raw_text = re.sub(r'[」」「]', '', res.choices[0].message.content)
                st.session_state.parsed_spots = re.findall(r"(名称[:：].*?)(?=名称[:：]|$)", raw_text, re.DOTALL)
                st.session_state.step = "select_spots"
                st.rerun()

# --- STEP 2: スポット選択 ---
elif st.session_state.step == "select_spots":
    st.markdown(f"## SPOT DISCOVERY ({min(st.session_state.display_count, len(st.session_state.parsed_spots))}件を表示)")
    
    for i in range(min(st.session_state.display_count, len(st.session_state.parsed_spots))):
        spot_text = st.session_state.parsed_spots[i]
        name_match = re.search(r"名称[:：]\s*(.*)", spot_text)
        name = name_match.group(1).split('\n')[0].strip() if name_match else f"スポット{i}"
        desc = re.search(r"解説[:：]\s*(.*)", spot_text, re.DOTALL).group(1).split('URL')[0].strip() if "解説" in spot_text else "解説なし"
        
        with st.container():
            st.markdown('<div class="spot-card">', unsafe_allow_html=True)
            c1, c2 = st.columns([1, 2])
            with c1: st.image(f"https://picsum.photos/seed/{name}/400/250", use_container_width=True)
            with c2:
                st.markdown(f'### {name}')
                st.write(desc)
                if st.checkbox(f"候補に追加", key=f"sel_{i}"):
                    if name not in st.session_state.selected_names: st.session_state.selected_names.append(name)
            st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.display_count < len(st.session_state.parsed_spots):
        if st.button("🔽 もっと見る"):
            st.session_state.display_count += 10
            st.rerun()

    if st.button("🚀 5つのプランを生成する", use_container_width=True, type="primary"):
        st.session_state.step = "final_plan"
        st.rerun()

# --- STEP 3: プラン表示 ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plans:
        with st.spinner("AIが5つの異なる旅程を執筆中..."):
            f = st.session_state.form_data
            for label in ["プランA", "プランB", "プランC", "プランD", "プランE"]:
                prompt = f"""
                あなたは一流コンシェルジュ。{f['dates']}の{f['departure']}発着の旅行。
                予算{f['budget']}。歩行{f['speed']}。宿{f['hotel']}。
                選択したスポット{st.session_state.selected_names}。
                
                【必須構成】
                1. タイムライン（移動手段、時刻、各滞在時間、各スポットの公式サイトURL）
                2. 宿泊先（最安予約サイトURLを含む）
                3. 合計金額の概算
                4. 【Aipiaのおすすめ！】未選択の秘境1つ追加
                5. 【AipiaAiのアドバイス】秘境のコツや注意点を3つ。
                日本語のみで、読みやすく適度なスペースを空けて出力。
                """
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                st.session_state.final_plans[label] = res.choices[0].message.content

    tabs = st.tabs(list(st.session_state.final_plans.keys()))
    for label, tab in zip(st.session_state.final_plans.keys(), tabs):
        with tab:
            st.image(f"https://picsum.photos/seed/header_{label}/1200/300", use_container_width=True)
            st.markdown(f'<div class="plan-box">{st.session_state.final_plans[label]}</div>', unsafe_allow_html=True)
            if st.button(f"✅ {label}を確定してしおりを作成", key=f"conf_{label}"):
                st.session_state.confirmed_plan = st.session_state.final_plans[label]
                st.session_state.step = "print_ready"
                st.rerun()

# --- STEP 4: 印刷画面 ---
elif st.session_state.step == "print_ready":
    st.markdown("## 🖨 旅のしおり（確定プラン）")
    st.markdown(f'<div style="background:white; padding:
