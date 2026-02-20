import streamlit as st
from groq import Groq
from datetime import datetime, timedelta

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia")

# 2. クライアント設定
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 3. デザイン (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #FCF9F2; }
    .black-banner {
        background-color: #111;
        width: 100%;
        padding: 100px 0;
        text-align: center;
        margin-bottom: 80px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.3);
    }
    .aipia-logo { 
        font-family: 'Georgia', serif; font-style: italic; 
        font-size: 30vw; 
        font-weight: bold; color: #FCF9F2; 
        line-height: 1.0; margin: 0; display: block;
    }
    .sub-title { 
        font-size: 5vw; color: #FCF9F2; font-weight: bold; 
        letter-spacing: 1.8vw; margin-top: 60px; display: inline-block;
    }
    .plan-card {
        background-color: white; padding: 50px; border-radius: 30px;
        font-size: 18px; line-height: 2.2; border: 1px solid #eee;
    }
    /* 日程選択を見やすく */
    .stDateInput div { font-size: 18px !important; }
    </style>
    """, unsafe_allow_html=True)

if "step" not in st.session_state: st.session_state.step = "input"
if "parsed_spots" not in st.session_state: st.session_state.parsed_spots = []
if "final_plan_content" not in st.session_state: st.session_state.final_plan_content = ""

# --- ヘッダー ---
st.markdown("""
    <div class="black-banner">
        <p class="aipia-logo">Aipia</p>
        <p class="sub-title">- AIが創る、秘境への旅行プラン -</p>
    </div>
    """, unsafe_allow_html=True)

# --- STEP 1: 入力 ---
if st.session_state.step == "input":
    st.markdown("<p style='text-align:center; color:#888; letter-spacing:5px;'>PLANNING INTERFACE</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1: departure = st.text_input("🛫 出発地", value="東京")
    with col2: destination = st.text_input("📍 目的地", placeholder="例：長野、徳島...")
    with col3: keyword = st.text_input("🔍 キーワード", placeholder="例：温泉、古民家...")

    col_date, col_p, col_s = st.columns([3, 2, 2])
    with col_date:
        # 【修正点】 value に 2つの日付を渡すことで範囲選択（レンジ）を有効化
        date_range = st.date_input(
            "📅 旅行日程（開始日と終了日を選択）", 
            value=(datetime.now(), datetime.now() + timedelta(days=2)),
            help="カレンダー上で開始日と終了日の2箇所をクリックしてください"
        )
    with col_p:
        adults = st.number_input("大人", 1, 20, 2)
        kids = st.number_input("子ども", 0, 20, 0)
    with col_s:
        walking_speed = st.select_slider("🚶 歩行速度", options=["ゆっくり", "標準", "せっかち"], value="標準")

    tags = st.multiselect("🏝 旅のテーマ", ["絶景", "秘境", "歴史", "温泉", "美食"], default=["絶景", "秘境"])
    budget = st.text_input("💰 予算/人")

    if st.button("✨ この条件で秘境を探索", use_container_width=True, type="primary"):
        # 日程が正しく範囲（2点）で選択されているか確認
        if isinstance(date_range, tuple) and len(date_range) == 2:
            with st.spinner("秘境を検索中..."):
                st.session_state.form_data = {
                    "adults": adults, "kids": kids, "budget": budget, 
                    "speed": walking_speed, "dates": f"{date_range[0]}から{date_range[1]}"
                }
                target = destination if destination else keyword
                prompt = f"{target}周辺で、テーマ『{tags}』に合う具体的な観光地を10件提案してください。名称、解説(120文字)、予算、星5、混雑、URL。区切りは --- 。"
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                st.session_state.parsed_spots = [s.strip() for s in res.choices[0].message.content.split("---") if "名称:" in s]
                st.session_state.step = "select_spots"
                st.rerun()
        else:
            st.error("⚠️ カレンダーで『開始日』と『終了日』の両方を選択してください。")

# --- STEP 2: スポット選択 ---
elif st.session_state.step == "select_spots":
    st.markdown("<h2 style='text-align:center;'>CHOOSE YOUR FAVORITES</h2>", unsafe_allow_html=True)
    selected_names = []
    for i, spot in enumerate(st.session_state.parsed_spots):
        details = {line.split(":", 1)[0].strip(): line.split(":", 1)[1].strip() for line in spot.split("\n") if ":" in line}
        name = details.get("名称", f"Spot {i+1}")
        st.markdown('<div style="background:white; padding:30px; border-radius:20px; margin-bottom:20px; border:1px solid #eee;">', unsafe_allow_html=True)
        if st.checkbox(f"⭐ {name}", key=f"f_{i}"): selected_names.append(name)
        st.write(details.get("解説", ""))
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 最終プランを生成する", use_container_width=True, type="primary"):
        st.session_state.selected_names = selected_names
        st.session_state.step = "final_plan"
        st.rerun()

# --- STEP 3: 最終プラン表示 ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plan_content:
        f = st.session_state.form_data
        with st.spinner(f"{f['dates']} の旅程を執筆中..."):
            prompt = f"日程：{f['dates']}。大人{f['adults']}名、予算{f['budget']}。歩行「{f['speed']}」。選んだスポット：{st.session_state.selected_names}。これらを元に、5つの詳細な旅行プランを作成してください。"
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            st.session_state.final_plan_content = res.choices[0].message.content

    st.markdown(f'<div class="plan-card">{st.session_state.final_plan_content}</div>', unsafe_allow_html=True)
    if st.button("← 戻る"): 
        st.session_state.step = "input"; st.session_state.final_plan_content = ""; st.rerun()
