import streamlit as st
from groq import Groq
from datetime import datetime

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia")

# 2. クライアント設定
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 3. デザイン (CSS) - 限界突破の巨大フォント
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-size: 16px; 
    }
    .stApp { background-color: #FCF9F2; }
    
    .logo-container { 
        text-align: center; 
        padding: 150px 0 120px 0; /* 上下の余白を極限まで確保 */
    }
    
    /* Aipiaロゴ：もはや壁紙レベルのサイズ */
    .aipia-logo { 
        font-family: 'Georgia', serif; font-style: italic; 
        font-size: 400px; /* 限界まで巨大化 */
        font-weight: bold; color: #111; 
        line-height: 1.0; 
        letter-spacing: 10px; 
        margin: 0;
        display: block;
    }
    
    /* サブタイトル：これだけでも圧倒的な存在感 */
    .sub-title { 
        font-size: 100px; /* 極大 */
        color: #222; font-weight: bold; 
        letter-spacing: 25px; 
        margin-top: 60px;
        padding: 40px 0;
        display: inline-block;
        border-top: 5px solid #111;
        border-bottom: 5px solid #111;
        line-height: 1.2;
    }

    /* --- レスポンシブ対応（画面サイズに合わせて縮小） --- */
    @media (max-width: 1400px) {
        .aipia-logo { font-size: 250px; }
        .sub-title { font-size: 60px; letter-spacing: 15px; }
    }
    @media (max-width: 768px) {
        .aipia-logo { font-size: 120px; letter-spacing: 2px; }
        .sub-title { font-size: 30px; letter-spacing: 5px; padding: 20px 0; }
        .logo-container { padding: 60px 0; }
    }
    
    /* 入力欄などは洗練された小サイズを維持 */
    .stTextInput label, .stSelectbox label, .stSlider label {
        font-size: 14px !important; color: #666 !important;
    }
    </style>
    """, unsafe_allow_html=True)

if "step" not in st.session_state: st.session_state.step = "input"
if "parsed_spots" not in st.session_state: st.session_state.parsed_spots = []

# --- ヘッダー：極大ロゴセクション ---
st.markdown("""
    <div class="logo-container">
        <p class="aipia-logo">Aipia</p>
        <p class="sub-title">- AIが創る、秘境への旅行プラン -</p>
    </div>
    """, unsafe_allow_html=True)

# --- STEP 1: 入力画面 ---
if st.session_state.step == "input":
    st.markdown("<p style='text-align: center; color: #bbb; letter-spacing: 5px; font-size: 20px; margin-bottom: 50px;'>ESTABLISH YOUR JOURNEY</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1: departure = st.text_input("🛫 出発地", value="東京")
    with col2: destination = st.text_input("📍 目的地", placeholder="例：長野県、徳島県...")
    with col3: keyword = st.text_input("🔍 キーワード", placeholder="例：歴史、温泉、サウナ...")

    col4, col5, col6, col7 = st.columns([2, 1, 1, 2])
    with col4: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now()))
    with col5: adults = st.number_input("大人", min_value=1, value=2)
    with col6: kids = st.number_input("子ども", min_value=0, value=0)
    with col7: walking_speed = st.select_slider("🚶 歩行速度", options=["ゆっくり", "標準", "せっかち"], value="標準")

    st.markdown("<hr style='border: 1px solid #ddd; margin: 60px 0;'>", unsafe_allow_html=True)
    
    c_h1, c_h2, c_h3 = st.columns(3)
    with c_h1: 
        hotel_type = st.selectbox("宿泊スタイル", ["こだわらない", "高級旅館", "リゾートホテル", "古民家・民宿"])
        room_size_pref = st.radio("お部屋の広さ", ["標準", "広め", "贅沢"], horizontal=True)
    with c_h2: 
        room_type = st.multiselect("希望タイプ", ["和室", "洋室", "離れ"])
        special_req = st.multiselect("こだわり", ["露天風呂付", "禁煙", "ペット可"])
    with c_h3:
        barrier_free = st.multiselect("安心サポート", ["段差なし", "車椅子対応"])

    tags = st.multiselect("🏝 旅のテーマ", ["絶景", "秘境", "歴史", "温泉", "郷土料理", "サウナ"], default=["絶景", "歴史"])
    budget_input = st.text_input("💰 予算/人", placeholder="例：10万円")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✨ Aipiaでプランを生成する", use_container_width=True, type="primary"):
        with st.spinner("Searching for the hidden gems..."):
            st.session_state.form_data = {
                "adults": adults, "kids": kids, "budget": budget_input, 
                "speed": walking_speed, "hotel": hotel_type, "room_size": room_size_pref,
                "room_type": room_type, "special": special_req, "barrier": barrier_free, "tags": tags
            }
            target = destination if destination else keyword
            prompt = f"{target}周辺で、テーマ『{tags}』に沿った具体的な観光スポットを10件提案してください。名称、解説(120文字)、予算、おすすめ度(星5)、混雑度(低中高)、URLの順で。区切りは --- で。"
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            st.session_state.parsed_spots = [s.strip() for s in res.choices[0].message.content.split("---") if "名称:" in s][:10]
            st.session_state.step = "select_spots"
            st.rerun()

# --- STEP 2以降は前回のロジックを継承 ---
elif st.session_state.step == "select_spots":
    selected_names = []
    for i, spot_data in enumerate(st.session_state.parsed_spots):
        details = {line.split(":", 1)[0].strip(): line.split(":", 1)[1].strip() for line in spot_data.split("\n") if ":" in line}
        name = details.get("名称", f"Spot {i+1}")
        st.markdown(f'<div style="background-color:white; padding:40px; border-radius:20px; margin-bottom:40px; border:1px solid #eee;">', unsafe_allow_html=True)
        col_main, col_fav = st.columns([8, 2])
        with col_fav:
            if st.checkbox(f"⭐", key=f"fav_{i}"): selected_names.append(name)
        with col_main:
            st.markdown(f"### {name}")
            st.write(details.get("解説", ""))
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 この内容でプランを作る", use_container_width=True, type="primary"):
        st.session_state.selected_names = selected_names
        st.session_state.step = "final_plan"
        st.rerun()

elif st.session_state.step == "final_plan":
    f = st.session_state.form_data
    with st.spinner("Finalizing..."):
        prompt = f"大人{f['adults']}名、予算{f['budget']}。歩行「{f['speed']}」。宿泊：{f['hotel']}。スポット：{st.session_state.selected_names}。5つのプランを詳細に作成。"
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
        st.markdown(f'<div style="background-color: white; padding: 50px; border-radius: 30px; font-size: 18px; line-height: 2;">{res.choices[0].message.content}</div>', unsafe_allow_html=True)
    if st.button("← 戻る"): st.session_state.step = "input"; st.rerun()
