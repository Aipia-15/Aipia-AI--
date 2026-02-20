import streamlit as st
from groq import Groq
from datetime import datetime

# 1. ページタイトルを「Aipia」のみに設定
st.set_page_config(layout="wide", page_title="Aipia")

# 2. クライアント設定
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 3. デザイン (CSS) - 圧縮を解除し、伸びやかな巨大ロゴへ
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-size: 15px; 
    }
    .stApp { background-color: #FCF9F2; }
    
    .logo-container { 
        text-align: center; 
        padding: 120px 0 100px 0; /* 上下の余白をさらに贅沢に */
    }
    
    /* Aipiaロゴ：圧縮を解除し、美しく巨大化 */
    .aipia-logo { 
        font-family: 'Georgia', serif; font-style: italic; 
        font-size: 300px; /* PC版：さらに巨大に */
        font-weight: bold; color: #111; 
        line-height: 1.2; /* 詰まりを解消 */
        letter-spacing: 5px; /* 文字間隔を広げて伸びやかに */
        margin-bottom: 60px; /* サブタイトルとの間に大きな隙間を */
    }
    
    /* サブタイトル：存在感をさらにアップ */
    .sub-title { 
        font-size: 70px; /* さらに大きく */
        color: #333; font-weight: bold; 
        letter-spacing: 20px; /* 文字間をさらに広げて高級感を */
        margin-top: 30px;
        padding: 30px 0;
        display: inline-block;
        border-top: 3px solid #111;
        border-bottom: 3px solid #111;
    }

    /* --- レスポンシブ対応（スマホ版） --- */
    @media (max-width: 768px) {
        .aipia-logo {
            font-size: 100px; /* スマホでもしっかり大きく */
            letter-spacing: 2px;
            margin-bottom: 30px;
        }
        .sub-title {
            font-size: 28px;
            letter-spacing: 6px;
            padding: 15px 0;
        }
    }
    
    .spot-card { 
        background-color: white; padding: 40px; border-radius: 20px; 
        border: 1px solid #eee; box-shadow: 0 10px 30px rgba(0,0,0,0.05); 
        margin-bottom: 50px; 
    }
    .spot-title { font-size: 36px; font-weight: bold; color: #111; margin-bottom: 15px; }
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
    st.markdown("<p style='text-align: center; color: #aaa; letter-spacing: 3px; font-size: 18px;'>ESTABLISH YOUR JOURNEY</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1: departure = st.text_input("🛫 出発地", value="東京")
    with col2: destination = st.text_input("📍 目的地", placeholder="例：長野県、徳島県...")
    with col3: keyword = st.text_input("🔍 キーワード", placeholder="例：歴史、温泉、サウナ...")

    col4, col5, col6, col7 = st.columns([2, 1, 1, 2])
    with col4: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now()))
    with col5: adults = st.number_input("大人", min_value=1, value=2)
    with col6: kids = st.number_input("子ども", min_value=0, value=0)
    with col7: walking_speed = st.select_slider("🚶 歩行速度", options=["ゆっくり", "標準", "せっかち"], value="標準")

    st.markdown("<hr style='border: 0.5px solid #ddd; margin: 40px 0;'>", unsafe_allow_html=True)
    
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
    if st.button("✨ Aipiaで旅を創る", use_container_width=True, type="primary"):
        with st.spinner("極上の秘境をコンシェルジュ中..."):
            st.session_state.form_data = {
                "adults": adults, "kids": kids, "budget": budget_input, 
                "speed": walking_speed, "hotel": hotel_type, "room_size": room_size_pref,
                "room_type": room_type, "special": special_req, "barrier": barrier_free, "tags": tags
            }
            target = destination if destination else keyword
            prompt = f"{target}周辺で、テーマ『{tags}』に沿った具体的な観光スポット（施設名、店舗名、場所名）を10件提案してください。名称、解説(120文字)、予算、おすすめ度(星5)、混雑度(低中高)、URLの順で。区切りは --- で。"
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            st.session_state.parsed_spots = [s.strip() for s in res.choices[0].message.content.split("---") if "名称:" in s][:10]
            st.session_state.step = "select_spots"
            st.rerun()

# --- STEP 2: お気に入り選択 ---
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
            with c_img: st.image(f"https://picsum.photos/seed/aipia_v8_{i}/800/600", use_container_width=True)
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
    with st.spinner("Writing..."):
        prompt = f"大人{f['adults']}名、予算{f['budget']}。歩行「{f['speed']}」。宿泊：{f['hotel']}。スポット：{st.session_state.selected_names}。5つのプランを詳細に作成。"
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
        st.markdown(f'<div style="background-color: white; padding: 50px; border-radius: 30px; font-size: 18px; line-height: 2;">{res.choices[0].message.content}</div>', unsafe_allow_html=True)

    if st.button("← 戻る", use_container_width=True):
        st.session_state.step = "input"; st.rerun()
