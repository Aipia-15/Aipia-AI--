import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import re
import urllib.parse

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - AI秘境コンシェルジュ")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 2. デザイン (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #FCF9F2; }
    .black-banner { background-color: #111; width: 100%; padding: 40px 0; text-align: center; margin-bottom: 20px; }
    .aipia-logo { font-family: 'Georgia', serif; font-style: italic; font-size: 8vw; font-weight: bold; color: #FCF9F2; line-height: 1.0; margin: 0; }
    .plan-box { background-color: white; border-radius: 15px; padding: 40px; border: 1px solid #ddd; line-height: 1.6; margin-bottom: 20px; }
    .timeline-title { 
        font-family: 'Helvetica', sans-serif; font-size: 28px; font-weight: 800; 
        color: #111; border-left: 8px solid #111; padding-left: 15px; margin: 30px 0 20px 0;
        letter-spacing: 2px; text-transform: uppercase;
    }
    .share-container { background: #f9f9f9; padding: 20px; border-radius: 10px; text-align: center; margin-top: 20px; }
    @media print { .no-print { display: none !important; } }
    </style>
    """, unsafe_allow_html=True)

# セッション状態
if "step" not in st.session_state: st.session_state.step = "input"
if "parsed_spots" not in st.session_state: st.session_state.parsed_spots = []
if "display_count" not in st.session_state: st.session_state.display_count = 10
if "selected_names" not in st.session_state: st.session_state.selected_names = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}
if "confirmed_plan" not in st.session_state: st.session_state.confirmed_plan = None

st.markdown('<div class="black-banner no-print"><p class="aipia-logo">Aipia</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力 ---
if st.session_state.step == "input":
    st.markdown("### 1. 旅のプロファイルを構築する")
    col1, col2, col3 = st.columns(3)
    with col1: departure = st.text_input("🛫 出発地 (必須)", key="dep")
    with col2: destination = st.text_input("📍 目的地", placeholder="地域名・駅名など")
    with col3: budget = st.text_input("💰 予算/人 (必須)", placeholder="10万円など")

    col_date, col_pa, col_pc, col_speed = st.columns([3, 1, 1, 2])
    with col_date: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now() + timedelta(days=1)))
    with col_pa: adults = st.number_input("大人", 1, 10, 2)
    with col_pc: kids = st.number_input("子供", 0, 10, 0)
    with col_speed: walking_speed = st.select_slider("🚶 歩行速度", options=["ゆっくり", "標準", "せっかち"], value="標準")

    st.markdown("#### 🏨 宿泊 & バリアフリー")
    h1, h2, h3 = st.columns(3)
    with h1: hotel_style = st.selectbox("宿泊スタイル", ["こだわらない", "高級旅館", "リゾート", "古民家", "グランピング"])
    with h2: room_pref = st.multiselect("客室こだわり", ["露天風呂付", "和洋室", "サウナ付", "部屋食"])
    with h3: barrier_free = st.multiselect("バリアフリー", ["車椅子対応", "段差なし", "手すりあり", "貸切風呂"])

    if st.button("✨ スポット探索を開始", use_container_width=True, type="primary"):
        if departure and budget and len(date_range) == 2:
            st.session_state.form_data = {"departure": departure, "destination": destination, "budget": budget, "adults": adults, "kids": kids, "speed": walking_speed, "dates": f"{date_range[0]}〜{date_range[1]}", "hotel": f"{hotel_style}/{room_pref}/{barrier_free}"}
            with st.spinner("Analyzing destination..."):
                prompt = f"{destination}周辺の観光地を20件。日本語のみ。「名称：」「解説：」「URL：」の形式を厳守。"
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                st.session_state.parsed_spots = re.findall(r"(名称[:：].*?)(?=名称[:：]|$)", re.sub(r'[」」「]', '', res.choices[0].message.content), re.DOTALL)
                st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: スポット選択 ---
elif st.session_state.step == "select_spots":
    st.markdown("## SPOT DISCOVERY")
    for i in range(min(st.session_state.display_count, len(st.session_state.parsed_spots))):
        spot_text = st.session_state.parsed_spots[i]
        name = re.search(r"名称[:：]\s*(.*)", spot_text).group(1).split('\n')[0].strip() if "名称" in spot_text else f"スポット{i}"
        st.markdown('<div class="spot-card">', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 2])
        with c1: st.image(f"https://picsum.photos/seed/{name}/400/250", use_container_width=True)
        with c2:
            st.markdown(f'### {name}')
            st.write(re.search(r"解説[:：]\s*(.*)", spot_text, re.DOTALL).group(1).split('URL')[0].strip() if "解説" in spot_text else "")
            if st.checkbox(f"候補に追加", key=f"sel_{i}"):
                if name not in st.session_state.selected_names: st.session_state.selected_names.append(name)
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.display_count < len(st.session_state.parsed_spots) and st.button("🔽 もっと見る"):
        st.session_state.display_count += 10; st.rerun()

    if st.button("🚀 5つのプランを生成", use_container_width=True, type="primary"):
        st.session_state.step = "final_plan"; st.rerun()

# --- STEP 3: 5つのプラン表示 ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plans:
        with st.spinner("AIコンシェルジュがプランを均一化して作成中..."):
            f = st.session_state.form_data
            for label in ["プランA", "プランB", "プランC", "プランD", "プランE"]:
                prompt = f"""
                【均一フォーマットで出力】日本語のみ。
                1. 冒頭に <div class="timeline-title">THE CHRONICLE: {label}</div> と出力
                2. タイムライン（時刻 | 場所 | 移動手段・金額・公式サイトURL）
                3. 宿泊先詳細（施設名 | 最安予約サイトURL）
                4. 合計概算金額
                5. 【Aipiaのおすすめ！】未選択の秘境1つ
                6. <div class="advice-title">AipiaAiのアドバイス</div> として、秘境の心得を3つ箇条書き。
                条件：{f['departure']}発着、予算{f['budget']}内、歩行{f['speed']}、バリアフリー/宿要望{f['hotel']}。
                選択：{st.session_state.selected_names}
                """
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                st.session_state.final_plans[label] = res.choices[0].message.content

    tabs = st.tabs(list(st.session_state.final_plans.keys()))
    for label, tab in zip(st.session_state.final_plans.keys(), tabs):
        with tab:
            st.markdown(f'<div class="plan-box">{st.session_state.final_plans[label]}</div>', unsafe_allow_html=True)
            if st.button(f"✅ {label}を確定・共有する", key=f"conf_{label}"):
                st.session_state.confirmed_plan = st.session_state.final_plans[label]
                st.session_state.step = "share_ready"; st.rerun()

# --- STEP 4: 共有画面 ---
elif st.session_state.step == "share_ready":
    st.markdown("## 🌍 SHARE YOUR JOURNEY")
    st.markdown(f'<div style="background:white; padding:40px; border:1px solid #000;">{st.session_state.confirmed_plan}</div>', unsafe_allow_html=True)
    
    # SNS共有ロジック
    share_text = f"Aipiaで最高の秘境旅行プランを作成しました！ #Aipia #AI旅行プラン"
    encoded_text = urllib.parse.quote(share_text)
    
    st.markdown(f"""
        <div class="share-container no-print">
            <h3>このプランを共有する</h3>
            <a href="https://twitter.com/intent/tweet?text={encoded_text}" target="_blank" style="background:#1DA1F2; color:white; padding:10px 20px; border-radius:5px; text-decoration:none; margin:5px; display:inline-block;">X (Twitter) で共有</a>
            <a href="https://www.facebook.com/sharer/sharer.php?u=#" target="_blank" style="background:#4267B2; color:white; padding:10px 20px; border-radius:5px; text-decoration:none; margin:5px; display:inline-block;">Facebook で共有</a>
            <p style="margin-top:10px; font-size:12px; color:#666;">※リンクをコピーしてLINEやInstagramに貼り付けてください</p>
            <button onclick="window.print()" style="background:#111; color:white; padding:10px 20px; border:none; border-radius:5px; cursor:pointer;">PDFを保存 / 印刷</button>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("最初に戻る"): st.session_state.step = "input"; st.session_state.final_plans = {}; st.rerun()
