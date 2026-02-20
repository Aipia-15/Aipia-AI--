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
    .logo-container { text-align: center; padding: 40px 0; }
    .aipia-logo { 
        font-family: 'Georgia', serif; font-style: italic; 
        font-size: 100px; font-weight: bold; color: #111; margin-bottom: -10px; 
    }
    .sub-title { font-size: 20px; color: #555; font-weight: bold; letter-spacing: 4px; }
    .plan-card { 
        background-color: white; padding: 25px; border-radius: 20px; 
        box-shadow: 0 10px 25px rgba(0,0,0,0.05); border: 1px solid #eee; 
        margin-top: 20px; white-space: pre-wrap;
    }
    .inspi-card {
        background-color: white; padding: 15px; border-radius: 12px;
        border: 1px solid #eee; text-align: center; height: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# セッション状態（データの保存箱）の初期化
if "step" not in st.session_state: st.session_state.step = "input"
if "spots_list" not in st.session_state: st.session_state.spots_list = ""
if "form_data" not in st.session_state: st.session_state.form_data = {}

# --- ヘッダー ---
st.markdown("""
    <div class="logo-container">
        <p class="aipia-logo">Aipia</p>
        <p class="sub-title">- AIが創る、秘境への旅行プラン - </p>
    </div>
    """, unsafe_allow_html=True)

# --- STEP 1: 入力画面 ---
if st.session_state.step == "input":
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1: departure = st.text_input("🛫 出発地", value="東京")
    with col2: destination = st.text_input("📍 目的地", placeholder="例：四国、九州...")
    with col3: keyword = st.text_input("🔍 キーワード検索", placeholder="例：サウナ、雲海...")

    col4, col5, col6 = st.columns([2, 1, 1])
    with col4: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now()))
    with col5: adults = st.number_input("大人", min_value=1, value=2)
    with col6: kids = st.number_input("子ども", min_value=0, value=0)

    tags = st.multiselect("🏝 旅のテーマ", 
        ["絶景", "秘境", "温泉", "郷土料理", "アクティビティ", "サウナ", "離島", "歴史・文化", "エモい", "子連れ"], 
        default=["絶景"])
    budget = st.text_input("💰 予算（1人あたり）", placeholder="例：10万円")

    if st.button("✨ この条件でスポットを探す", use_container_width=True, type="primary"):
        with st.spinner("AIが厳選スポットを10件抽出中..."):
            st.session_state.form_data = {
                "dep": departure, "dest": destination, "key": keyword,
                "adults": adults, "kids": kids, "tags": tags, "budget": budget
            }
            target = destination if destination else keyword
            prompt = f"{target}周辺で、テーマ『{tags}』に沿った観光スポットを10件、魅力と公式サイトURL付きで教えて。"
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            st.session_state.spots_list = res.choices[0].message.content
            st.session_state.step = "select_spots"
            st.rerun()

    # 下部：インスピレーション
    st.markdown("<br><br><h3 style='text-align: center;'>💡 行き先に迷ったら...</h3>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    recs = [("徳島・祖谷", "日本三大秘境"), ("長崎・五島", "教会と海"), ("山形・銀山", "大正ロマン"), ("熊本・阿蘇", "火の国絶景")]
    for i, (title, desc) in enumerate(recs):
        with [c1, c2, c3, c4][i]:
            st.markdown(f'<div class="inspi-card"><h4>{title}</h4><p>{desc}</p></div>', unsafe_allow_html=True)

# --- STEP 2: スポット選択 & ホテル希望 ---
elif st.session_state.step == "select_spots":
    st.subheader("🏝 おすすめの10スポット")
    st.markdown(st.session_state.spots_list)
    
    selected = st.text_area("気になるスポット名を記入してください")
    hotel_type = st.selectbox("🏨 宿泊の希望", ["露天風呂付き客室", "モダンなホテル", "キャンプ", "古民家"])
    
    if st.button("🚀 このスポットで5種類のプランを作る"):
        st.session_state.selected_spots = selected
        st.session_state.hotel_type = hotel_type
        st.session_state.step = "final_plan"
        st.rerun()

# --- STEP 3: 最終プラン表示 ---
elif st.session_state.step == "final_plan":
    st.subheader("🗓 あなただけの特別プラン（5種類）")
    f = st.session_state.form_data
    with st.spinner("詳細な行程表を作成中..."):
        prompt = f"""
        条件：大人{f['adults']}名、子供{f['kids']}名。予算1人{f['budget']}。
        以下のスポットを使い、5種類の異なるプランを作成して。
        スポット：{st.session_state.selected_spots}
        宿泊：{st.session_state.hotel_type}
        
        ルール：
        - 乗り換え・移動時間を明記。
        - 各スポット付近のおすすめ食事処を追加し「[右上におすすめ！]」と書く。
        - 最後に予約ページや公式サイトのURLをまとめて表示。
        """
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        st.markdown(f'<div class="plan-card">{res.choices[0].message.content}</div>', unsafe_allow_html=True)

    if st.button("← 最初からやり直す"):
        st.session_state.step = "input"
        st.rerun()
