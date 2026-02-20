import streamlit as st
from groq import Groq
from datetime import datetime

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - AI Travel Planner")

# 2. デザイン（CSS）
st.markdown("""
    <style>
    .stApp { background-color: #FCF9F2; }
    
    /* ロゴエリアの調整 */
    .logo-container {
        text-align: center;
        padding-top: 20px;
        padding-bottom: 40px;
    }
    .aipia-logo {
        font-family: 'Georgia', serif; 
        font-style: italic;
        font-size: 70px; 
        font-weight: bold; 
        color: #111;
        margin-bottom: 0px;
        line-height: 1.2;
    }
    .sub-title {
        display: block;
        font-size: 18px;
        color: #555; 
        font-weight: bold;
        letter-spacing: 3px;
        margin-top: 10px;
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
st.markdown("""
    <div class="logo-container">
        <p class="aipia-logo">Aipia</p>
        <p class="sub-title">- AIが創る、秘境への旅行プラン -</p>
    </div>
    """, unsafe_allow_html=True)

# --- 選択・入力エリア ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    departure = st.text_input("🛫 出発地", value="東京")
with col2:
    destination = st.text_input("📍 目的地", placeholder="例：徳島県 祖谷")
with col3:
    date_range = st.date_input(
        "📅 日程を選択",
        value=(datetime.now(), datetime.now()),
        format="YYYY/MM/DD"
    )
with col4:
    budget = st.text_input("💰 予算（1人あたり）", placeholder="例：5万円、100,000円")

# 日数計算
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    diff = (end_date - start_date).days + 1
    stay_info = f"{start_date} から {end_date} までの {diff}日間"
else:
    stay_info = "日帰り"

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
    elif not budget:
        st.error("予算を入力してください！")
    else:
        with st.spinner("AIが秘境プランを練っています..."):
            # プロンプトの組み立て
            prompt_text = f"【出発地】: {departure}\n【目的地】: {destination}\n【日程】: {stay_info}\n【予算】: {budget}\n【テーマ】: {', '.join(tags)}"
            
            full_instruction = f"""
            以下の条件で最高の旅行プランを2つ提案してください。
            {prompt_text}
            
            指示：
            - 指定された予算（{budget}）内で収まるような、コストパフォーマンスを意識した提案にしてください。
            - 必ず具体的な「秘境」スポットを1つ以上含めてください。
            - 各日の行程は4〜5項目に絞ってください。
            - 最後に「旅の総評」を短く添えてください。
            """
            
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "あなたは一流の旅行プランナーです。"},
                              {"role": "user", "content": full_instruction}]
                )
                
                plan_result = response.choices[0].message.content
                st.markdown(f'<div class="plan-card">{plan_result}</div>', unsafe_allow_html=True)
                st.balloons()
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
