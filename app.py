st.title("Aipia") # 例：「爆速旅行プランナー」など

import streamlit as st
from groq import Groq

# Groqのクライアント設定
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("My AI App (Groq Edition)")

# AI Studioから持ってきた指示（長すぎたので一旦短く整理しました）
SYSTEM_PROMPT = "あなたは優秀な旅行プランナーです。"

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Groqで回答生成（爆速です！）
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile", # 無料で使える強力なモデル
        messages=st.session_state.messages
    )
    
    answer = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)
