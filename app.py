import streamlit as st
from groq import Groq

# ページ設定：横幅を広く使う
st.set_page_config(layout="wide", page_title="Aipia - AI Travel Planner")

# 1. APIキーの設定
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 2. デザイン（CSS）：画像のような色使いとフォントを再現
st.markdown("""
    <style>
    /* 全体の背景色（ほんのり暖色） */
    .stApp {
        background-color: #FCF9F2;
    }
    /* サイドバーのスタイル */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #eee;
    }
    /* タイトルのデザイン */
    .aipia-logo {
        font-family: 'Georgia', serif;
        font-style: italic;
        font-size: 60px;
        font-weight: bold;
        color: #111;
        text-align: center;
        margin-bottom: -10px;
    }
    .sub-title {
        text-align: center;
        color: #555;
        font-weight: bold;
        letter-spacing: 2px;
        margin-bottom: 30px;
    }
    /* 入力エリアのカード風デザイン */
    .input-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- サイドバー：設定項目 ---
with st.sidebar:
    st.image("https://picsum.photos/seed/travel/200/100", use_container_width=True) # 仮のロゴ画像
    st.header("📍 旅の条件")
    departure = st.text_input("出発地", value="東京")
    destination = st.text_input("目的地", placeholder="どこへ行きたいですか？")
    dates = st.date_input("日程", [])
    budget = st.select_slider("予算感", options=["節約", "標準", "贅沢"])
    
    st.divider()
    st.subheader("★ 登録したスポット")
    st.info("まだスポットが登録されていません")

# --- メインエリア：ロゴとチャット ---
st.markdown('<p class="aipia-logo">Aipia</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">-AIが創る、秘境への旅行プラン-</p>', unsafe_allow_html=True)

# AIの性格設定
SYSTEM_PROMPT = f"""
あなたは旅行プランナー「Aipia」です。
ユーザーの希望（出発地：{departure}、目的地：{destination}、予算：{budget}）に基づき、
誰も知らないような「秘境」を組み込んだ、ワクワクする2パターンの旅行プランを作成してください。
"""

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# チャット表示
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

# 入力欄
if prompt := st.chat_input("プランの要望を詳しく教えてください（例：温泉に入りたい、3日間で回りたい）"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Groqで回答生成
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages,
            stream=True
        )
        for chunk in response:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                response_placeholder.markdown(full_response + "▌")
        response_placeholder.markdown(full_response)
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})
