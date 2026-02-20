import streamlit as st
from groq import Groq
from datetime import datetime

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - AI Travel Planner")

# 2. クライアント設定
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 3. デザイン (CSS) - メリハリを極限まで追求
st.markdown("""
    <style>
    /* 全体のベース文字サイズを小さくし、洗練させる */
    html, body, [class*="css"] {
        font-size: 15px; 
        color: #333;
    }
    .stApp { background-color: #FCF9F2; }
    
    /* ヘッダーセクション */
    .logo-container { 
        text-align: center; 
        padding: 100px 0 80px 0; 
    }
    
    /* Aipiaロゴ：圧倒的な巨体 */
    .aipia-logo { 
        font-family: 'Georgia', serif; font-style: italic; 
        font-size: 200px; 
        font-weight: bold; color: #111; 
        margin-bottom: 60px; 
        line-height: 0.8;
        letter-spacing: -5px;
    }
    
    /* サブタイトル：ロゴに負けない大きさ */
    .sub-title { 
        font-size: 50px; 
        color: #222; font-weight: bold; 
        letter-spacing: 12px; 
        margin-top: 40px;
        border-top: 1px solid #ddd;
        border-bottom: 1px solid #ddd;
        padding: 20px 0;
        display: inline-block;
    }
    
    /* 入力フォーム等のラベルは小さく（あえて控えめに） */
    .stTextInput label, .stSelectbox label, .stSlider label, .stDateInput label, .stNumberInput label {
        font-size: 14px !important; font-weight: normal !important; color: #666 !important;
    }
    
    /* スポットカード */
    .spot-card { 
        background-color: white; padding: 30px; border-radius: 15px; 
        border: 1px solid #eee; box-shadow: 0 4px 20px rgba(0,0,0,0.03); 
        margin-bottom: 40px; 
    }
    .spot-title { font-size: 28px; font-weight: bold; color: #111; margin-bottom: 15px; }
    .spot-desc { font-size: 15px; line-height: 1.6; color: #444; }
    
    /* ステータスボックス */
    .status-box { 
        background-color: #fcfcfc; padding: 15px; border-radius: 10px; 
        font-size: 13px; color: #888; 
        margin-top: 20px; display: flex; justify-content: space-around; 
        border: 1px solid #f0f0f0;
    }
    
    /* プラン表示 */
    .plan-card { 
        background-color: white; padding: 50px; border-radius: 20px; 
        font-size: 16px; line-height: 2; white-space: pre-wrap; color: #222;
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

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✨ 秘境を探索する", use_container_width=True, type="primary"):
        with st.spinner("Searching..."):
            st.session_state.form_data = {
                "adults": adults, "kids": kids, "budget": budget_input, 
                "speed": walking_speed, "hotel": hotel_type, "room_size": room_size_pref,
                "room_type": room_type, "special": special_req, "barrier": barrier_free, "tags": tags
            }
            target = destination if destination else keyword
            prompt = f"{target}周辺で、テーマ『{tags}』に沿った具体的な観光スポットを10件提案してください。県・市名のみ、施設案内所は禁止。名称、解説(120文字)、予算、おすすめ度(星5)、混雑度(低中高)、URLの順で。区切りは --- で。"
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            st.session_state.parsed_spots = [s.strip() for s in res.choices[0].message.content.split("---") if "名称:" in s][:10]
            st.session_state.step = "select_spots"
            st.rerun()

# --- STEP 2: スポット選択 ---
elif st.session_state.step == "select_spots":
    st.markdown("<p style='text-align: center; font-size: 20px; color: #666;'>SELECT DESTINATIONS</p>", unsafe_allow_html=True)
    selected_names = []
    for i, spot_data in enumerate(st.session_state.parsed_spots):
        details = {line.split(":", 1)[0].strip(): line.split(":", 1)[1].strip() for line in spot_data.split("\n") if ":" in line}
        name = details.get("名称", f"Spot {i+1}")
        
        st.markdown(f'<div class="spot-card">', unsafe_allow_html=True)
        col_main, col_fav = st.columns([8, 2])
        with col_fav:
            if st.checkbox(f"Add ⭐", key=f"fav_{i}"): 
                selected_names.append(name)
        with col_main:
            c_img, c_txt = st.columns([1, 2])
            with c_img: 
                st.image(f"https://picsum.photos/seed/aipia_v6_{i}/800/600", use_container_width=True)
            with c_txt:
                st.markdown(f'<p class="spot-title">{name}</p>', unsafe_allow_html=True)
                st.markdown(f'<p class="spot-desc">{details.get("解説", "")}</p>', unsafe_allow_html=True)
                st.markdown(f"""
                    <div class="status-box">
                        <span>Cost: {details.get("予算", "-")}</span>
                        <span>Rating: {details.get("おすすめ度", "-")}</span>
                        <span>Crowd: {details.get("混雑度", "-")}</span>
                    </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 プランを生成", use_container_width=True, type="primary"):
        if not selected_names: st.warning("Please select at least one spot.")
        else:
            st.session_state.selected_names = selected_names
            st.session_state.step = "final_plan"
            st.rerun()

# --- STEP 3: 最終プラン ---
elif st.session_state.step == "final_plan":
    st.markdown("<p style='text-align: center; font-size: 20px; color: #666;'>YOUR ITINERARY</p>", unsafe_allow_html=True)
    f = st.session_state.form_data
    with st.spinner("Generating..."):
        prompt = f"大人{f['adults']}名、子供{f['kids']}名、予算{f['budget']}。歩行「{f['speed']}」。宿泊：{f['hotel']}、{f['room_size']}、{f['room_type']}、{f['special']}、{f['barrier']}。スポット：{st.session_state.selected_names}。5つのプランを詳細に作成。"
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
        st.markdown(f'<div class="plan-card">{res.choices[0].message.content}</div>', unsafe_allow_html=True)

    if st.button("← Back to Settings", use_container_width=True):
        st.session_state.step = "input"
        st.rerun()
