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
    .plan-card {
        background-color: white; padding: 25px;
        border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border: 1px solid #eee; margin-top: 20px; white-space: pre-wrap;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. クライアント設定
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- ヘッダー ---
st.markdown('<p class="aipia-logo">Aipia</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">-AIが創る、秘境への旅行プラン-</p>', unsafe_allow_html=True)

# --- 選択・入力エリア ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    departure = st.text_input("🛫 出発地", value="東京")
with col2:
    destination = st.text_input("📍 目的地", placeholder="例：四国、九州など")
with col3:
    duration = st.selectbox("📅 期間", ["日帰り", "1泊2日", "2泊3日", "3泊4日以上"])
with col4:
    budget = st.selectbox("💰 予算感", ["節約", "標準", "贅沢"])

st.write("### 🏝 気になるテーマを選んでください")
tags = st.multiselect(
    "AIがプランに組み込みます",
    ["温泉", "絶景", "郷土料理", "穴場", "アクティビティ", "歴史・文化", "インスタ映え", "のんびり"],
    default=["絶景", "穴場"]
)

st.markdown("<br>", unsafe_allow_html=True)
create_button = st.button("✨ 究極のスポットからプランを作成する", use_container_width=True, type="primary")

# --- ロジック部分 ---
if create_button:
    if not destination:
        st.error("目的地を入力してください！")
    else:
        with st.spinner("AIが秘境プランを練っています..."):
            prompt = f"""
            以下の条件で最高の旅行プランを2つ提案してください。
            【出発地】: {departure}
            【目的地】: {destination}
            【期間】: {duration}
            【予算】: {budget}
            【重視するテーマ】: {', '.join(tags)}
            
            指示：
            - 必ず具体的な「秘境」スポットを1つ以上含めてください。
            - 1日の行程は4〜5項目に絞ってください。
            - 最後に「旅の総評」を短く添えてください。
            """
            
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "あなたは一流の旅行プランナーです。"},
                              {"role": "user", "content": prompt}]
                )
                
                plan_result = response.choices[0].message.content
                st.markdown(f'<div class="plan-card">{plan_result}</div>', unsafe_allow_html=True)
                st.balloons()
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

st.divider()
st.sidebar.subheader("⭐ お気に入り登録")
st.sidebar.write("作成されたプランからスポットを保存できます（今後実装予定）")
