import streamlit as st
from groq import Groq
from datetime import datetime

# 1. ページタイトルを「Aipia」のみに設定
st.set_page_config(layout="wide", page_title="Aipia")

# 2. クライアント設定
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 3. デザイン (CSS) - 画面サイズに応じたレスポンシブ巨大文字
st.markdown("""
    <style>
    /* 全体の基本文字サイズは小さめ（メリハリ用） */
    html, body, [class*="css"] {
        font-size: 14px; 
    }
    .stApp { background-color: #FCF9F2; }
    
    .logo-container { 
        text-align: center; 
        padding: 80px 0 60px 0; 
    }
    
    /* Aipiaロゴ：PCとスマホでサイズを変える */
    .aipia-logo { 
        font-family: 'Georgia', serif; font-style: italic; 
        font-size: 240px; /* PC版 */
        font-weight: bold; color: #111; 
        margin-bottom: 40px; 
        line-height: 0.8;
        letter-spacing: -8px;
    }
    
    /* サブタイトル：PCとスマホでサイズを変える */
    .sub-title { 
        font-size: 60px; /* PC版 */
        color: #222; font-weight: bold; 
        letter-spacing: 15px; 
        margin-top: 20px;
        padding: 20px 0;
        display: inline-block;
        border-top: 2px solid #111;
        border-bottom: 2px solid #111;
    }

    /* --- スマホ版のサイズ調整 (@media) --- */
    @media (max-width: 768px) {
        .aipia-logo {
            font-size: 80px; /* スマホでは画面に収まるサイズに */
            letter-spacing: -2px;
            margin-bottom: 20px;
        }
        .sub-title {
            font-size: 24px; /* スマホ用サイズ */
            letter-spacing: 4px;
            padding: 10px 0;
        }
        .logo-container { padding: 40px 0; }
    }
    
    /* スポットカード */
    .spot-card { 
        background-color: white; padding: 30px; border-radius: 15px; 
        border: 1px solid #eee; box-shadow: 0 4px 20px rgba(0,0,0,0.03); 
        margin-bottom: 40px; 
    }
    .spot-title { font-size: 32px; font-weight: bold; color: #111; }
    
    /* プラン表示 */
    .plan-card { 
        background-color: white; padding: 40px; border-radius: 20px; 
        font-size: 16px; line-height: 2; white-space: pre-wrap; 
        border: 1px solid #eee;
    }
    </style>
    """, unsafe_allow_html=True)

if "step" not in st.session_state: st.session_state.step = "input"
if "parsed_spots" not in st.session_state: st.session_state.parsed_spots = []

# --- ヘッダー ---
st.markdown("""
    <div class="logo-container">
        <p class="aipia-logo">Aipia</p>
        <p class="sub-title">- AIが創る、秘境への旅行プラン -</p>
    </div>
    """, unsafe_allow_html=True)

# --- STEP 1: 入力画面 ---
if st.session_state.step == "input":
    st.markdown("<p style='text-align: center; color: #999; letter-spacing: 2px;'>TRAVEL CONFIGURATION</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1: departure = st.text_input("🛫 出発地", value="東京")
    with col2: destination = st.text_input("📍 目的地", placeholder="例：松本市、祖谷...")
    with col3: keyword = st.text_input("🔍 キーワード", placeholder="例：城下町、隠れ家...")

    col4, col5, col6, col7 = st.columns([2, 1, 1, 2])
    with col4: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now()))
    with col5: adults = st.number_input("大人", min_value=1, value=2)
    with col6: kids = st.number_input("子ども", min_value=0, value=0)
    with col7: walking_speed = st.select_slider("🚶 歩行速度", options=["ゆっくり", "標準", "せっかち"], value="標準")

    st.markdown("<hr style='border: 0.5px solid #eee;'>", unsafe_allow_html=True)
    
    c_h1, c_h2, c_h3 = st.columns(3)
    with c_h1: 
        hotel_type = st.selectbox("宿泊タイプ", ["こだわらない", "高級旅館", "リゾートホテル", "古民家・民宿"])
        room_size_pref = st.radio("広さ", ["標準", "広め", "贅沢"], horizontal=True)
    with c_h2: 
        room_type = st.multiselect("部屋タイプ", ["和室", "洋室", "和洋室"])
        special_req = st.multiselect("こだわり", ["露天風呂付", "禁煙", "ペット"])
    with c_h3:
        barrier_free = st.multiselect("配慮", ["段差なし", "車椅子対応"])

    tags = st.multiselect("🏝 テーマ", ["絶景", "秘境", "歴史", "温泉", "郷土料理", "サウナ"], default=["絶景", "歴史"])
    budget_input = st.text_input("💰 予算/人", placeholder="例：10万円")

    if st.button("✨ 秘境を探索する", use_container_width=True, type="primary"):
        with st.spinner("Searching..."):
            st.session_state.form_data = {
                "adults": adults, "kids": kids, "budget": budget_input, 
                "speed": walking_speed, "hotel": hotel_type, "room_size": room_size_pref,
                "room_type": room_type, "special": special_req, "barrier": barrier_free, "tags": tags
            }
            target = destination if destination else keyword
            prompt = f"{target}周辺で、テーマ『{tags}』に沿った具体的な観光スポットを10件提案。施設案内所は禁止。名称、解説(120文字)、予算、おすすめ度(星5)、混雑度(低中高)、URLの順で。区切りは --- で。"
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            st.session_state.parsed_spots = [s.strip() for s in res.choices[0].message.content.split("---") if "名称:" in s][:10]
            st.session_state.step = "select_spots"
            st.rerun()

# --- STEP 2: スポット選択 ---
elif st.session_state.step == "select_spots":
    selected_names = []
    for i, spot_data in enumerate(st.session_state.parsed_spots):
        details = {line.split(":", 1)[0].strip(): line.split(":", 1)[1].strip() for line in spot_data.split("\n") if ":" in line}
        name = details.get("名称", f"Spot {i+1}")
        
        st.markdown(f'<div class="spot-card">', unsafe_allow_html=True)
        col_main, col_fav = st.columns([8, 2])
        with col_fav:
            if st.checkbox(f"Add ⭐", key=f"fav_{i}"): selected_names.append(name)
        with col_main:
            c_img, c_txt = st.columns([1, 2])
            with c_img: st.image(f"https://picsum.photos/seed/aipia_v7_{i}/800/600", use_container_width=True)
            with c_txt:
                st.markdown(f'<p class="spot-title">{name}</p>', unsafe_allow_html=True)
                st.write(details.get("解説", ""))
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 プランを生成", use_container_width=True, type="primary"):
        st.session_state.selected_names = selected_names
        st.session_state.step = "final_plan"
        st.rerun()

# --- STEP 3: 最終プラン ---
elif st.session_state.step == "final_plan":
    f = st.session_state.form_data
    with st.spinner("Generating..."):
        prompt = f"大人{f['adults']}名、予算{f['budget']}。歩行「{f['speed']}」。宿泊：{f['hotel']}。スポット：{st.session_state.selected_names}。5つのプランを詳細に作成。"
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
        st.markdown(f'<div class="plan-card">{res.choices[0].message.content}</div>', unsafe_allow_html=True)

    if st.button("← Back", use_container_width=True):
        st.session_state.step = "input"; st.rerun()
