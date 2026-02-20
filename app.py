import streamlit as st
from groq import Groq

# 1. APIキーの設定（Groqのキーを使います）
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# アプリの見た目
st.title("Aipia")
st.caption("-AIが創る、秘境への旅行プラン-")

# --- ここが「SYSTEM_PROMPT」です！ ---
SYSTEM_PROMPT = """
あなたは「Aipia（アイピア） -AIが創る、秘境への旅行プラン-」の専属AIコンシェルジュです。

以下のルールを厳守して旅行プランを提案してください：
1. 目的：ユーザーが入力したキーワードや目的地から、まだ見ぬ「秘境」や「究極のスポット」を提案すること。
2. スポット優先：ユーザーが選択したスポットを「最優先事項」として必ずプランの軸に組み込むこと。
3. 構成：詳細すぎる分刻みのスケジュールではなく、1日の主要な動き（4〜5項目）に絞った、実現可能でワクワクする行程表を作ること。
4. 提案数：ユーザーを迷わせないよう、厳選した2パターンの旅行案を提示すること。
5. トーン：洗練された、かつ親しみやすいガイドのような口調で話すこと。

もし目的地が具体的すぎたり抽象的すぎたりしてプランが作れない場合は、優しく条件変更を提案してください。
"""

# チャットの履歴管理
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# 画面に過去の会話を表示（システム指示は隠す）
for msg in st.session_state.messages:
    if msg["role"] != "system":
        st.chat_message(msg["role"]).write(msg["content"])

# 入力欄
if prompt := st.chat_input("次はどこへ行きたいですか？"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Groqで回答生成
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=st.session_state.messages
    )
    
    answer = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)
