import streamlit as st
from groq import Groq
from datetime import datetime

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - AI Travel Planner")

# 2. クライアント設定
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 3. デザイン (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #FCF9F2; }
    .logo-container { text-align: center; padding: 50px 0 30px 0; }
    
    /* タイトル：Aipiaをさらに大きく */
    .aipia-logo { 
        font-family: 'Georgia', serif; font-style: italic; 
        font-size: 120px; font-weight: bold; color: #111; 
        margin-bottom: -20px; line-height: 1;
    }
    /* サブタイトル：上より小さく、洗練されたフォント */
    .sub-title { 
        font-size: 18px; color: #666; font-weight: bold; 
        letter-spacing: 5px; margin-top: 0px; 
    }
    
    .spot-card { background-color: white; padding: 25px; border-radius: 20px; border: 1px solid #eee; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 30px; }
    .status-box { background-color: #f8fafc; padding: 12px; border-radius: 12px; font-size: 14px; color: #475569; margin-top: 15px; display: flex; justify-content: space-around; border: 1px solid #e2e8f0; }
    .plan-card { background-color: white; padding: 25px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); white-space: pre-wrap; }
    </style>
    """, unsafe_allow_html=True)

if "step" not in st.session_state: st.session_state.step = "input"
if "parsed_spots" not in st.session_state: st.session_state.parsed_spots = []

# --- ヘッダー（サイズ調整済み） ---
st.markdown("""
    <div class="logo-container">
        <p class="aipia-logo">Aipia</p>
        <p class="sub-title">- AIが創る、秘境への旅行プラン -</p>
    </div>
    """, unsafe_allow_html=True)

# --- STEP 1: 入力画面 ---
if st.session_state.step == "input":
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1: departure = st.text_input("🛫 出発地", value="東京")
    with col2: destination = st.text_input("📍 目的地", placeholder="例：松本市、祖谷...")
    with col3: keyword = st.text_input("🔍 キーワード", placeholder="例：城下町、隠れ家、サウナ...")

    col4, col5, col6, col7 = st.columns([2, 1, 1, 2])
    with col4: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now()))
    with col5: adults = st.number_input("大人", min_value=1, value=2)
    with col6: kids = st.number_input("子ども", min_value=0, value=0)
    with col7: walking_speed = st.select_slider("🚶 歩くスピード", options=["ゆっくり", "標準", "せっかち"], value="標準")

    st.write("### 🏨 宿泊・お部屋の希望")
    c_h1, c_h2, c_h3 = st.columns(3)
    with c_h1: 
        hotel_type = st.selectbox("ホテルの種類", ["こだわらない", "高級旅館", "リゾートホテル", "カジュアルホテル", "古民家・民宿"])
        room_size_pref = st.radio("お部屋の広さ", ["人数に合わせる", "少しゆったりめ", "とにかく広く！"], horizontal=True)
    with c_h2: 
        room_type = st.multiselect("お部屋のタイプ", ["和室", "洋室(ベッド)", "和洋室", "離れ・一棟貸し"])
        special_req = st.multiselect("こだわり条件", ["露天風呂付き客室", "禁煙ルーム", "ペット同伴可"])
    with c_h3:
        barrier_free = st.multiselect("安心・バリアフリー", ["バリアフリー対応", "車椅子利用", "段差が少ない"])

    # 「歴史」テーマを追加
    tags = st.multiselect("🏝 旅のテーマ", ["絶景", "秘境", "歴史", "温泉", "郷土料理", "アクティビティ", "サウナ"], default=["絶景", "歴史"])
    budget_input = st.text_input("💰 予算（1人あたり）", placeholder="例：10万円")

    if st.button("✨ この条件でスポットを探す", use_container_width=True, type="primary"):
        with st.spinner("『場所』にこだわって検索中..."):
            st.session_state.form_data = {
                "adults": adults, "kids": kids, "budget": budget_input, 
                "speed": walking_speed, "hotel": hotel_type, "room_size": room_size_pref,
                "room_type": room_type, "special": special_req, "barrier": barrier_free, "tags": tags
            }
            target = destination if destination else keyword
            # プロンプトをさらに厳格化：ビジターセンターや案内所を禁止
            prompt = f"""{target}周辺で、テーマ『{tags}』に沿った具体的な観光スポットを10件提案してください。
            【禁止事項】: 県名・市名のみの名称、ビジターセンター、観光案内所、道の駅。
            【必須事項】: 実際に観光客が体験・感動できる『具体的な場所名（寺社、展望台、古民家、店舗など）』を挙げてください。
            
            形式：
            名称: (具体的なスポット名)
            解説: (その場所の見どころ、100文字程度)
            予算: (目安)
            おすすめ度: (★5つ中)
            混雑度: (低・中・高)
            URL: (公式サイトURL)
            ---"""
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            st.session_state.parsed_spots = [s.strip() for s in res.choices[0].message.content.split("---") if "名称:" in s][:10]
            st.session_state.step = "select_spots"
            st.rerun()

# --- STEP 2: お気に入り選択（以下省略なし） ---
elif st.session_state.step == "select_spots":
    st.subheader("🏝 気になるスポットをお気に入り登録")
    selected_names = []
    for i, spot_data in enumerate(st.session_state.parsed_spots):
        details = {}
        for line in spot_data.split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                details[k.strip()] = v.strip()
        name = details.get("名称", f"スポット {i+1}")
        
        st.markdown('<div class="spot-card">', unsafe_allow_html=True)
        col_main, col_fav = st.columns([9, 1])
        with col_fav:
            if st.checkbox("⭐", key=f"fav_{i}"): selected_names.append(name)
        with col_main:
            c_img, c_txt = st.columns([1, 2])
            with c_img: st.image(f"https://picsum.photos/seed/aipia_v4_{i}/600/400", use_container_width=True)
            with c_txt:
                st.markdown(f"### {name}")
                st.write(details.get("解説", "情報取得中..."))
                st.markdown(f'<div class="status-box"><span>💰 {details.get("予算", "不明")}</span><span>✨ {details.get("おすすめ度", "不明")}</span><span>👥 混雑: {details.get("混雑度", "不明")}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 選択したスポットでプランを作る", use_container_width=True, type="primary"):
        if not selected_names: st.warning("スポットを1つ以上選んでください！")
        else:
            st.session_state.selected_names = selected_names
            st.session_state.step = "final_plan"
            st.rerun()

# --- STEP 3: 最終プラン ---
elif st.session_state.step == "final_plan":
    st.subheader("🗓 あなただけの特別プラン")
    f = st.session_state.form_data
    with st.spinner("詳細な移動スケジュールを計算中..."):
        prompt = f"""以下の条件で5種類の旅行プランを作成してください。
        【基本】大人{f['adults']}名、子供{f['kids']}名、予算{f['budget']}
        【移動】歩行速度は「{f['speed']}」。
        【宿泊】{f['hotel']}、広さ「{f['room_size']}」、{f['room_type']}、{f['special']}、{f['barrier']}を考慮。
        【選択スポット】{st.session_state.selected_names}
        ルール：食事処には[右上におすすめ！]、最後に予約URL。
        """
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
        st.markdown(f'<div class="plan-card">{res.choices[0].message.content}</div>', unsafe_allow_html=True)

    if st.button("← 最初からやり直す"):
        st.session_state.step = "input"
        st.rerun()
