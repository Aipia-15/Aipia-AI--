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
    .logo-container { text-align: center; padding: 40px 0; }
    .aipia-logo { 
        font-family: 'Georgia', serif; font-style: italic; 
        font-size: 100px; /* さらに大きく */
        font-weight: bold; color: #111; margin-bottom: -10px; 
    }
    .sub-title { font-size: 20px; color: #555; font-weight: bold; letter-spacing: 4px; }
    
    /* 下部のおすすめプラン用カード */
    .inspi-card {
        background-color: white; padding: 15px; border-radius: 12px;
        border: 1px solid #eee; text-align: center;
        transition: 0.3s; cursor: pointer;
    }
    .inspi-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"

# --- ヘッダー ---
st.markdown("""
    <div class="logo-container">
        <p class="aipia-logo">Aipia</p>
        <p class="sub-title">- AIが創る、秘境への旅行プラン -</p>
    </div>
    """, unsafe_allow_html=True)

if st.session_state.step == "input":
    # --- 検索・入力セクション ---
    with st.container():
        col1, col2, col3 = st.columns([2, 2, 2])
        with col1: departure = st.text_input("🛫 出発地", value="東京")
        with col2: destination = st.text_input("📍 目的地（空欄でもOK）", placeholder="例：四国、九州...")
        with col3: keyword = st.text_input("🔍 キーワード検索", placeholder="例：サウナ、廃校、雲海...")

        col4, col5, col6 = st.columns([2, 1, 1])
        with col4: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now()))
        with col5: adults = st.number_input("大人", min_value=1, value=2)
        with col6: kids = st.number_input("子ども", min_value=0, value=0)

        # テーマ拡充
        tags = st.multiselect("🏝 旅のテーマ（複数選択）", 
            ["絶景", "秘境", "温泉", "郷土料理", "アクティビティ", "サウナ", "離島", "歴史・文化", "エモい", "子連れ", "贅沢体験", "修行"], 
            default=["絶景"])

        budget = st.text_input("💰 予算（1人あたり）", placeholder="例：10万円")

        if st.button("✨ この条件でスポットを探す", use_container_width=True, type="primary"):
            # ここでAIにスポット生成させるロジック（前回のコードと同様）
            st.session_state.step = "select_spots"
            st.rerun()

    # --- 下部：おすすめのプラン（インスピレーション） ---
    st.markdown("<br><br><br><h3 style='text-align: center; color: #333;'>💡 行き先に迷ったら...</h3>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    recommendations = [
        {"title": "徳島・祖谷", "desc": "日本三大秘境で過ごす、かづら橋と温泉の旅"},
        {"title": "長崎・五島列島", "desc": "エメラルドの海と教会群を巡る離島の休日"},
        {"title": "山形・銀山温泉", "desc": "大正ロマン溢れる雪景色の街並み"},
        {"title": "熊本・阿蘇", "desc": "地球の息吹を感じる絶景ドライブプラン"}
    ]
    for i, col in enumerate([c1, c2, c3, c4]):
        with col:
            st.markdown(f"""
                <div class="inspi-card">
                    <h4>{recommendations[i]['title']}</h4>
                    <p style='font-size: 13px; color: #666;'>{recommendations[i]['desc']}</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"{recommendations[i]['title']}を選択", key=f"btn_{i}"):
                # ここで目的地を自動入力する等の処理が可能
                pass

# --- ステップ2以降（スポット選択・プラン生成） ---
# （前回のコードと同様のため省略しますが、プロンプトに「大人◯名、子ども◯名」の情報を渡すよう修正します）
