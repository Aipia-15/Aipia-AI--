import streamlit as st
from groq import Groq
from datetime import datetime
import re

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
    .spot-item { background-color: white; padding: 20px; border-radius: 15px; margin-bottom: 20px; border: 1px solid #eee; }
    .plan-card { background-color: white; padding: 25px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); white-space: pre-wrap; }
    </style>
    """, unsafe_allow_html=True)

# セッション状態の初期化
if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "form_data" not in st.session_state: st.session_state.form_data = {}

# --- ヘッダー ---
st.markdown('<div class="logo-container"><p class="aipia-logo">Aipia</p><p class="sub-title">- AIが創る、秘境への旅行プラン -</p></div>', unsafe_allow_html=True)

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

    tags = st.multiselect("🏝 旅のテーマ", ["絶景", "秘境", "温泉", "郷土料理", "アクティビティ", "サウナ", "離島", "エモい", "子連れ"], default=["絶景"])
    budget = st.text_input("💰 予算（1人あたり）", placeholder="例：10万円")

    if st.button("✨ この条件でスポットを探す", use_container_width=True, type="primary"):
        with st.spinner("AIが厳選スポットと画像を抽出中..."):
            st.session_state.form_data = {"adults": adults, "kids": kids, "budget": budget, "dest": destination}
            target = destination if destination else keyword
            prompt = f"{target}周辺でテーマ『{tags}』に合う観光スポット10件を、名称と100文字程度の解説、公式サイトURLの形式で出力してください。"
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            
            # 簡易的なリスト化（AIの回答から名称を抽出）
            spots_raw = res.choices[0].message.content
            st.session_state.found_spots = spots_raw.split("\n\n")[:10]
            st.session_state.step = "select_spots"
            st.rerun()

# --- STEP 2: お気に入り選択 (画像付き) ---
elif st.session_state.step == "select_spots":
    st.subheader("🏝 気になるスポットをお気に入り登録（複数選択可）")
    
    selected_spots = []
    for i, spot_info in enumerate(st.session_state.found_spots):
        with st.container():
            col_img, col_txt = st.columns([1, 2])
            with col_img:
                # プレースホルダー画像（実際の名称を画像検索する代わりに美しい旅の画像を表示）
                st.image(f"https://picsum.photos/seed/{i+100}/400/300", use_container_width=True, caption="スポットイメージ")
            with col_txt:
                st.markdown(spot_info)
                if st.checkbox("お気に入り登録", key=f"spot_{i}"):
                    # 名称だけを抽出して保存
                    name = spot_info.split('\n')[0].replace('1. ', '').replace('2. ', '') # 簡易パース
                    selected_spots.append(name)
    
    hotel_type = st.selectbox("🏨 宿泊の希望", ["露天風呂付き客室", "モダンなホテル", "キャンプ", "古民家"])
    
    if st.button("🚀 選択したスポットでプランを作る", use_container_width=True, type="primary"):
        if not selected_spots:
            st.warning("スポットを1つ以上選んでください！")
        else:
            st.session_state.selected_names = selected_spots
            st.session_state.hotel_type = hotel_type
            st.session_state.step = "final_plan"
            st.rerun()

# --- STEP 3: 最終プラン ---
elif st.session_state.step == "final_plan":
    st.subheader("🗓 あなただけの特別プラン（5種類）")
    f = st.session_state.form_data
    with st.spinner("詳細な行程表を作成中..."):
        prompt = f"大人{f['adults']}名、子供{f['kids']}名、予算{f['budget']}。スポット「{st.session_state.selected_names}」と宿泊「{st.session_state.hotel_type}」を軸に、乗り換え時間を含めた5種類のプランを作ってください。食事処には[右上におすすめ！]と明記し、最後に関連URLをまとめてください。"
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
        st.markdown(f'<div class="plan-card">{res.choices[0].message.content}</div>', unsafe_allow_html=True)

    if st.button("← 最初からやり直す"):
        st.session_state.step = "input"
        st.rerun()
