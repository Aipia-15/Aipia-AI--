import streamlit as st
from groq import Groq
from datetime import datetime

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - AI Travel Planner")

# 2. クライアント設定
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 3. デザイン (CSS) - 文字サイズと余白を徹底強化
st.markdown("""
    <style>
    /* 全体のベース文字サイズをさらに拡大 */
    html, body, [class*="css"] {
        font-size: 24px; 
    }
    .stApp { background-color: #FCF9F2; }
    
    .logo-container { 
        text-align: center; 
        padding: 80px 0 60px 0; /* 上下の余白を拡大 */
    }
    
    /* Aipiaロゴ：画面の主役級サイズ */
    .aipia-logo { 
        font-family: 'Georgia', serif; font-style: italic; 
        font-size: 180px; /* 極大サイズ */
        font-weight: bold; color: #111; 
        margin-bottom: 40px; /* サブタイトルとの間のスペース */
        line-height: 1;
    }
    
    /* サブタイトル：一行でパッと読めるサイズ */
    .sub-title { 
        font-size: 36px; /* 大幅アップ */
        color: #444; font-weight: bold; 
        letter-spacing: 10px; /* 文字間隔を広げて高級感を */
        margin-top: 20px; 
    }
    
    /* 入力フォームのラベルサイズを巨大化 */
    .stTextInput label, .stSelectbox label, .stSlider label, .stDateInput label, .stNumberInput label {
        font-size: 30px !important; font-weight: bold !important; color: #111 !important;
        margin-bottom: 15px !important;
    }
    
    /* スポットカード */
    .spot-card { 
        background-color: white; padding: 50px; border-radius: 40px; 
        border: 1px solid #ddd; box-shadow: 0 15px 40px rgba(0,0,0,0.1); 
        margin-bottom: 60px; 
    }
    .spot-title { font-size: 52px; font-weight: bold; color: #111; margin-bottom: 25px; }
    .spot-desc { font-size: 28px; line-height: 1.6; color: #222; }
    
    /* ステータスボックス */
    .status-box { 
        background-color: #f1f5f9; padding: 25px; border-radius: 25px; 
        font-size: 26px; font-weight: bold; color: #1e293b; 
        margin-top: 30px; display: flex; justify-content: space-around; 
        border: 2px solid #cbd5e1;
    }
    
    /* ボタンを巨大化 */
    .stButton > button {
        font-size: 32px !important; padding: 15px 30px !important;
        border-radius: 20px !important;
    }
    </style>
    """, unsafe_allow_html=True)

if "step" not in st.session_state: st.session_state.step = "input"
if "parsed_spots" not in st.session_state: st.session_state.parsed_spots = []

# --- ヘッダー：スペースとサイズを最適化 ---
st.markdown("""
    <div class="logo-container">
        <p class="aipia-logo">Aipia</p>
        <p class="sub-title">- AIが創る、秘境への旅行プラン -</p>
    </div>
    """, unsafe_allow_html=True)

# --- STEP 1: 入力画面 ---
if st.session_state.step == "input":
    st.markdown("<br><h2 style='text-align: center; font-size: 45px;'>🔍 旅のコンセプトを決める</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1: departure = st.text_input("🛫 出発地", value="東京")
    with col2: destination = st.text_input("📍 目的地", placeholder="例：松本市、祖谷...")
    with col3: keyword = st.text_input("🔍 自由入力キーワード", placeholder="例：城下町、隠れ家...")

    col4, col5, col6, col7 = st.columns([2, 1, 1, 2])
    with col4: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now()))
    with col5: adults = st.number_input("大人", min_value=1, value=2)
    with col6: kids = st.number_input("子ども", min_value=0, value=0)
    with col7: walking_speed = st.select_slider("🚶 歩くスピード", options=["ゆっくり", "標準", "せっかち"], value="標準")

    st.markdown("<hr style='border: 2px solid #ddd;'>", unsafe_allow_html=True)
    st.write("### 🏨 宿泊のこだわり")
    c_h1, c_h2, c_h3 = st.columns(3)
    with c_h1: 
        hotel_type = st.selectbox("ホテルの種類", ["こだわらない", "高級旅館", "リゾートホテル", "カジュアルホテル", "古民家・民宿"])
        room_size_pref = st.radio("お部屋のゆとり", ["人数相応", "少し広め", "スイート・贅沢に"], horizontal=True)
    with c_h2: 
        room_type = st.multiselect("お部屋タイプ", ["和室", "洋室", "和洋室", "離れ"])
        special_req = st.multiselect("必須設備", ["露天風呂付き客室", "禁煙", "ペット可"])
    with c_h3:
        barrier_free = st.multiselect("バリアフリー", ["段差なし", "車椅子対応", "手すりあり"])

    tags = st.multiselect("🏝 旅のテーマ", ["絶景", "秘境", "歴史", "温泉", "郷土料理", "アクティビティ", "サウナ"], default=["絶景", "歴史"])
    budget_input = st.text_input("💰 予算（1人あたり）", placeholder="例：10万円")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✨ この条件でスポットを探す", use_container_width=True, type="primary"):
        with st.spinner("AIが最高のスポットをコンシェルジュ中..."):
            st.session_state.form_data = {
                "adults": adults, "kids": kids, "budget": budget_input, 
                "speed": walking_speed, "hotel": hotel_type, "room_size": room_size_pref,
                "room_type": room_type, "special": special_req, "barrier": barrier_free, "tags": tags
            }
            target = destination if destination else keyword
            prompt = f"""{target}周辺で、テーマ『{tags}』に沿った具体的な観光スポット（建物、公園、店舗、自然景勝地など）を10件提案してください。
            【禁止】: 県名・市名のみ、ビジターセンター、案内所、広域エリア名。
            【必須】: 実際にその場所を訪れて感動できる『具体的な固有名称』。
            
            形式：
            名称: (名称)
            解説: (魅力、120文字程度)
            予算: (目安)
            おすすめ度: (★5)
            混雑度: (低・中・高)
            URL: (URL)
            ---"""
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            st.session_state.parsed_spots = [s.strip() for s in res.choices[0].message.content.split("---") if "名称:" in s][:10]
            st.session_state.step = "select_spots"
            st.rerun()

# --- STEP 2: お気に入り選択 ---
elif st.session_state.step == "select_spots":
    st.markdown("<h2 style='font-size: 50px;'>🏝 おすすめスポット（お気に入りを選択）</h2>", unsafe_allow_html=True)
    selected_names = []
    for i, spot_data in enumerate(st.session_state.parsed_spots):
        details = {line.split(":", 1)[0].strip(): line.split(":", 1)[1].strip() for line in spot_data.split("\n") if ":" in line}
        name = details.get("名称", f"スポット {i+1}")
        
        st.markdown(f'<div class="spot-card">', unsafe_allow_html=True)
        col_main, col_fav = st.columns([7, 3])
        with col_fav:
            if st.checkbox(f"お気に入り登録 ⭐", key=f"fav_{i}"): 
                selected_names.append(name)
        with col_main:
            c_img, c_txt = st.columns([1, 1.2])
            with c_img: 
                st.image(f"https://picsum.photos/seed/aipia_v5_{i}/800/600", use_container_width=True)
            with c_txt:
                st.markdown(f'<p class="spot-title">{name}</p>', unsafe_allow_html=True)
                st.markdown(f'<p class="spot-desc">{details.get("解説", "")}</p>', unsafe_allow_html=True)
                st.markdown(f"""
                    <div class="status-box">
                        <span>💰 {details.get("予算", "不明")}</span>
                        <span>✨ {details.get("おすすめ度", "不明")}</span>
                        <span>👥 混雑: {details.get("混雑度", "不明")}</span>
                    </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 選択したスポットで究極のプランを作る", use_container_width=True, type="primary"):
        if not selected_names: st.warning("スポットを選択してください！")
        else:
            st.session_state.selected_names = selected_names
            st.session_state.step = "final_plan"
            st.rerun()

# --- STEP 3: 最終プラン ---
elif st.session_state.step == "final_plan":
    st.markdown("<h2 style='font-size: 50px;'>🗓 Aipia 厳選旅行プラン</h2>", unsafe_allow_html=True)
    f = st.session_state.form_data
    with st.spinner("詳細な旅程を書き上げています..."):
        prompt = f"""以下の条件で、毛色の違う5種類の旅行プランを作成してください。
        【基本】大人{f['adults']}名、子供{f['kids']}名、予算{f['budget']}
        【移動速度】歩行「{f['speed']}」に合わせて分単位でスケジュールを組んでください。
        【宿泊】{f['hotel']}、{f['room_size']}な部屋、{f['room_type']}、{f['special']}、{f['barrier']}を考慮した具体的な宿名。
        【スポット】{st.session_state.selected_names}
        ルール：食事処に[右上におすすめ！]、最後に予約・交通URL。
        """
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
        st.markdown(f'<div class="plan-card" style="font-size: 28px;">{res.choices[0].message.content}</div>', unsafe_allow_html=True)

    if st.button("← 最初の画面へ戻る", use_container_width=True):
        st.session_state.step = "input"
        st.rerun()
