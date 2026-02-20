import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import re

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - AI秘境コンシェルジュ")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 2. デザイン (CSS) - スペースの最適化と印刷対応
st.markdown("""
    <style>
    .stApp { background-color: #FCF9F2; }
    .black-banner {
        background-color: #111; width: 100%; padding: 30px 0;
        text-align: center; margin-bottom: 20px;
    }
    .aipia-logo { 
        font-family: 'Georgia', serif; font-style: italic; 
        font-size: 6vw; font-weight: bold; color: #FCF9F2; line-height: 1.0; margin: 0;
    }
    .spot-card {
        background-color: white; padding: 15px; border-radius: 12px;
        margin-bottom: 15px; border: 1px solid #eee; box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    /* プラン表示：行間と余白を詰める */
    .plan-text {
        background-color: white; border-radius: 10px; padding: 20px;
        border: 1px solid #ddd; white-space: pre-wrap; 
        font-size: 15px; line-height: 1.4; color: #333;
    }
    .advice-box {
        background-color: #f0f7ff; border-left: 5px solid #007bff;
        padding: 15px; margin-top: 15px; border-radius: 5px;
    }
    @media print {
        .no-print { display: none !important; }
        .stApp { background-color: white !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "parsed_spots" not in st.session_state: st.session_state.parsed_spots = []
if "display_count" not in st.session_state: st.session_state.display_count = 10
if "selected_names" not in st.session_state: st.session_state.selected_names = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}
if "confirmed_plan" not in st.session_state: st.session_state.confirmed_plan = None

st.markdown('<div class="black-banner no-print"><p class="aipia-logo">Aipia</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力 ---
if st.session_state.step == "input":
    st.markdown("### 1. 旅行の条件を入力してください")
    col1, col2, col3 = st.columns(3)
    with col1: departure = st.text_input("🛫 出発地 (必須)", key="dep", placeholder="例：東京駅")
    with col2: destination = st.text_input("📍 目的地", placeholder="地域名・駅名など")
    with col3: budget = st.text_input("💰 予算/人 (必須)", placeholder="10万円など")

    col_date, col_pa, col_pc, col_speed = st.columns([3, 1, 1, 2])
    with col_date: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now() + timedelta(days=1)))
    with col_pa: adults = st.number_input("大人", 1, 10, 2)
    with col_pc: kids = st.number_input("子供", 0, 10, 0)
    with col_speed: walking_speed = st.select_slider("🚶 歩行速度", options=["ゆっくり", "標準", "せっかち"], value="標準")

    st.markdown("#### 🏨 ホテルのこだわり・バリアフリー")
    h1, h2, h3 = st.columns(3)
    with h1: hotel_style = st.selectbox("宿泊スタイル", ["こだわらない", "高級旅館", "リゾート", "古民家", "ビジネス"])
    with h2: room_pref = st.multiselect("こだわり", ["露天風呂付客室", "源泉掛け流し", "部屋食", "高層階", "海が見える"])
    with h3: barrier_free = st.multiselect("バリアフリー", ["車椅子対応", "段差なし", "貸切風呂あり", "手すりあり"])

    if st.button("✨ 秘境スポットを検索", use_container_width=True, type="primary"):
        if departure and budget and len(date_range) == 2:
            st.session_state.form_data = {
                "departure": departure, "destination": destination, "budget": budget, 
                "adults": adults, "kids": kids, "speed": walking_speed, 
                "dates": f"{date_range[0]}〜{date_range[1]}", 
                "hotel": f"{hotel_style}({room_pref}) {barrier_free}"
            }
            with st.spinner("スポットを10件生成中..."):
                target = destination if destination else "日本の秘境"
                prompt = f"{target}周辺の観光スポットを10件。日本語のみを使用し、中国語漢字や特殊記号を排除。「名称：」「解説：」の形式で。URLも含めて。"
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                raw_text = re.sub(r'[」」「]', '', res.choices[0].message.content)
                st.session_state.parsed_spots = re.findall(r"(名称[:：].*?)(?=名称[:：]|$)", raw_text, re.DOTALL)
                st.session_state.step = "select_spots"
                st.rerun()

# --- STEP 2: スポット選択 ---
elif st.session_state.step == "select_spots":
    st.markdown("## SPOT DISCOVERY (10件表示中)")
    
    # 表示数分だけループ
    current_spots = st.session_state.parsed_spots[:st.session_state.display_count]
    for i, spot_text in enumerate(current_spots):
        name = re.search(r"名称[:：]\s*(.*)", spot_text).group(1).split('\n')[0].strip() if "名称" in spot_text else f"スポット{i}"
        desc = re.search(r"解説[:：]\s*(.*)", spot_text, re.DOTALL).group(1).strip() if "解説" in spot_text else spot_text
        
        st.markdown(f'<div class="spot-card">', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 2])
        with c1: st.image(f"https://picsum.photos/seed/{name}/400/250", use_container_width=True)
        with c2:
            st.markdown(f'### {name}')
            st.write(desc)
            if st.checkbox(f"プランに追加", key=f"sel_{i}"):
                if name not in st.session_state.selected_names: st.session_state.selected_names.append(name)
        st.markdown('</div>', unsafe_allow_html=True)

    # もっと見るボタン
    if st.session_state.display_count < len(st.session_state.parsed_spots):
        if st.button("🔽 もっと見る"):
            st.session_state.display_count += 10
            st.rerun()

    if st.button("🚀 5つのプランを生成する", use_container_width=True, type="primary"):
        st.session_state.step = "final_plan"
        st.rerun()

# --- STEP 3: 5つのプラン表示 ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plans:
        with st.spinner("プランA〜Eを同時作成中...（予算・帰宅・バリアフリー考慮）"):
            f = st.session_state.form_data
            for label in ["プランA", "プランB", "プランC", "プランD", "プランE"]:
                prompt = f"""
                プロの旅行コンシェルジュとして日本語のみで作成。
                {f['departure']}発着、予算{f['budget']}以内、{f['dates']}、{f['adults'] + f['kids']}名、歩行:{f['speed']}。
                バリアフリー・宿要望:{f['hotel']}。
                選択スポット:{st.session_state.selected_names}。
                
                【形式】
                ・タイムライン形式（余計な改行を減らしコンパクトに）
                ・各場所の「公式サイトURL」を記載
                ・宿泊先は「最安予約サイトURL（例：楽天トラベル等）」を記載
                ・合計金額を最後に明記
                ・【Aipiaのおすすめ！】スポット1つ追加
                ・最後に「AipiaAiのアドバイス」として秘境や豆知識を3つ。
                """
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                st.session_state.final_plans[label] = res.choices[0].message.content

    tabs = st.tabs(list(st.session_state.final_plans.keys()))
    for i, tab in enumerate(tabs):
        label = list(st.session_state.final_plans.keys())[i]
        with tab:
            st.markdown(f'<div class="plan-text">{st.session_state.final_plans[label]}</div>', unsafe_allow_html=True)
            if st.button(f"✅ {label}を確定して印刷準備", key=f"conf_{label}"):
                st.session_state.confirmed_plan = st.session_state.final_plans[label]
                st.session_state.step = "print_ready"
                st.rerun()

# --- STEP 4: 確定・印刷画面 ---
elif st.session_state.step == "print_ready":
    st.markdown("## 🖨 旅行プラン確定（印刷用）")
    st.info("このページを右クリックで「印刷」するか、PDFとして保存してください。")
    st.markdown(f'<div style="background:white; padding:30px; border:2px solid #111;">{st.session_state.confirmed_plan}</div>', unsafe_allow_html=True)
    
    if st.button("最初に戻る", class_name="no-print"):
        st.session_state.step = "input"
        st.session_state.final_plans = {}
        st.rerun()
