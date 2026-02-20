import streamlit as st
from groq import Groq
from datetime import datetime

# ページ設定
st.set_page_config(layout="wide", page_title="Aipia - AI Travel Planner")

# クライアント設定
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- デザイン (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #FCF9F2; }
    .logo-container { text-align: center; padding-top: 10px; }
    .aipia-logo { font-family: 'Georgia', serif; font-style: italic; font-size: 60px; font-weight: bold; margin-bottom: 0px; }
    .sub-title { font-size: 16px; color: #555; letter-spacing: 2px; }
    .spot-card { background-color: white; padding: 15px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 10px; }
    .recommend-badge { float: right; background-color: #ff4b4b; color: white; padding: 2px 8px; border-radius: 5px; font-size: 12px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# セッション状態の初期化
if "step" not in st.session_state:
    st.session_state.step = "input"
if "spots" not in st.session_state:
    st.session_state.spots = []
if "selected_spots" not in st.session_state:
    st.session_state.selected_spots = []

# --- ヘッダー ---
st.markdown('<div class="logo-container"><p class="aipia-logo">Aipia</p><p class="sub-title">- AIが創る、秘境への旅行プラン -</p></div>', unsafe_allow_html=True)

# --- STEP 1: 条件入力 ---
if st.session_state.step == "input":
    col1, col2, col3, col4 = st.columns(4)
    with col1: departure = st.text_input("🛫 出発地", value="東京")
    with col2: destination = st.text_input("📍 目的地", placeholder="例：徳島県 祖谷")
    with col3: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now()))
    with col4: budget = st.text_input("💰 予算", placeholder="例：10万円")
    
    tags = st.multiselect("🏝 テーマ", ["温泉", "絶景", "郷土料理", "穴場", "アクティビティ"], default=["絶景"])

    if st.button("🔍 まずはお気に入りスポットを探す", use_container_width=True):
        with st.spinner("10件の厳選スポットを抽出中..."):
            # AIにスポット10件を依頼
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": f"{destination}周辺の観光スポットを10件、名称と特徴、公式サイトURLを箇条書きで教えてください。"}]
            )
            st.session_state.spots = res.choices[0].message.content
            st.session_state.step = "select_spots"
            st.rerun()

# --- STEP 2: スポット選択 ---
elif st.session_state.step == "select_spots":
    st.subheader("🏝 気になるスポットをお気に入り登録してください")
    st.write(st.session_state.spots)
    
    selected = st.text_area("お気に入り登録するスポット名を記入してください（複数可）")
    hotel_type = st.selectbox("🏨 ホテル・宿の希望", ["高級旅館", "ビジネスホテル", "キャンプ・グランピング", "民宿・古民家"])
    
    col_prev, col_next = st.columns(2)
    with col_prev:
        if st.button("← 条件をやり直す"):
            st.session_state.step = "input"
            st.rerun()
    with col_next:
        if st.button("✨ 5種類の詳細プランを生成する"):
            st.session_state.selected_spots = selected
            st.session_state.hotel_preference = hotel_type
            st.session_state.step = "generate_plan"
            st.rerun()

# --- STEP 3: プラン生成と表示 ---
elif st.session_state.step == "generate_plan":
    st.subheader("🗓 あなただけの特別プラン（5種類）")
    
    with st.spinner("乗り換え時間や食事処を含めたプランを計算中..."):
        final_prompt = f"""
        以下の条件で、毛色の違う旅行プランを5種類作成してください。
        【目的地】: {st.session_state.selected_spots}
        【宿泊希望】: {st.session_state.hotel_preference}
        
        ルール：
        1. 各プランに「おすすめの食事処」と「近くの秘境」を自動追加し、名称の横に「右上におすすめ！と明記」という指示に従い「[右上におすすめ！]」と書いてください。
        2. 乗り換え時間、徒歩移動時間を含めた詳細な行程表にすること。
        3. 各スポット、ホテル、交通機関の予約ページURLを必ず文末にまとめること。
        """
        
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": final_prompt}]
        )
        
        st.markdown(res.choices[0].message.content)

    col_btn1, col_btn2, col_btn3 = st.columns(3)
    with col_btn1: st.button("🔄 再生成")
    with col_btn2: st.button("✍️ 編集（スポット追加）")
    with col_btn3: st.success("✅ プラン確定（予約ページへ）")
    
    if st.button("最初に戻る"):
        st.session_state.step = "input"
        st.rerun()
    
