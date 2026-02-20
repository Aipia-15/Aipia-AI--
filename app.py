import streamlit as st
from groq import Groq

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - AI Travel Planner")

# 2. デザイン（CSS）
st.markdown("""
    <style>
    .stApp { background-color: #FCF9F2; }
    .aipia-logo {
        font-family: 'Georgia', serif; font-style: italic;
        font-size: 60px; font-weight: bold; color: #111;
        text-align: center; margin-bottom: -10px;
    }
    .sub-title {
        text-align: center; color: #555; font-weight: bold;
        letter-spacing: 2px; margin-bottom: 30px;
    }
    /* プラン表示用カード */
    .plan-card {
        background-color: white; padding: 25px;
        border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border: 1px solid #eee; margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. クライアント設定
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- ヘッダー ---
st.markdown('<p class="aipia-logo">Aipia</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">-AIが創る、秘境への旅行プラン-</p>', unsafe_allow_html=True)

# --- 選択・入力エリア ---
# 画像のように横並びの入力欄を作る
col1, col2, col3, col4 = st.columns(4)

with col1:
    departure = st.text_input("🛫 出発地", value="東京")
with col2:
    destination = st.text_input("📍 目的地", placeholder="例：四国、九州など")
with col3:
    duration = st.selectbox("📅 期間", ["日帰り", "1泊2日", "2泊3日", "3泊4日以上"])
with col4:
    budget = st.selectbox("💰 予算感", ["節約", "標準", "贅沢"])

# スポット選択（複数選択式）
st.write("### 🏝 気になるテーマを選んでください")
tags = st.multiselect(
    "AIがプランに組み込みます",
    ["温泉", "絶景", "郷土料理", "穴場", "アクティビティ", "歴史・文化", "インスタ映え", "のんびり"],
    default=["絶景", "穴場"]
)

# --- プラン作成ボタン ---
st.markdown("<br>", unsafe_allow_html=True)
create_button = st.button("✨ 究極のスポットからプランを作成する", use_container_width=True, type="primary")

# --- ロジック部分 ---
if create_button:
    if not destination:
        st.error("目的地を入力してください！")
    else:
        with st.spinner("AIが秘境プランを練っています..."):
            # AIへの指示を組み立て
            prompt = f"""
            以下の条件で最高の旅行プランを2つ提案してください。
            【出発地】: {departure}
