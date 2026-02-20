import streamlit as st
from groq import Groq
from datetime import datetime

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - AI Travel Planner")

# 2. クライアント設定
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 3. デザイン (CSS) - カードとステータス用
st.markdown("""
    <style>
    .stApp { background-color: #FCF9F2; }
    .logo-container { text-align: center; padding: 20px 0; }
    .aipia-logo { font-family: 'Georgia', serif; font-style: italic; font-size: 80px; font-weight: bold; color: #111; margin-bottom: -10px; }
    .sub-title { font-size: 18px; color: #555; font-weight: bold; letter-spacing: 4px; }
    
    /* スポットカードのデザイン */
    .spot-card {
        background-color: white;
        padding: 20px;
        border-radius: 20px;
        border: 1px solid #eee;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 25px;
    }
    .status-box {
        background-color: #f8fafc;
        padding: 10px;
        border-radius: 10px;
        font-size: 14px;
        color: #475569;
        margin-top: 10px;
        display: flex;
        justify-content: space-around;
    }
    .plan-card { background-color: white; padding: 25px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); white-space: pre-wrap; }
    </style>
    """, unsafe_allow_html=True)

# セッション状態の初期化
if "step" not in st.session_state: st.session_state.step = "input"
if "parsed_spots" not in st.session_state: st.session_state.parsed_spots = []

# --- ヘッダー ---
st.markdown('<div class="logo-container"><p class="aipia-logo">Aipia</p><p class="sub-title">- AIが創る、秘境への旅行プラン -</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力画面 ---
if st.session_state.step == "input":
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1: departure = st.text_input("🛫 出発地", value="東京")
    with col2: destination = st.text_input("📍 目的地", placeholder="例：四国、九州...")
    with col3: keyword = st.text_input("🔍 キーワード検索", placeholder="例：絶景、廃校、サウナ...")

    col4, col5, col6 = st.columns([2, 1, 1])
    with col4: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now()))
    with col5: adults = st.number_input("大人", min_value=1, value=2)
    with col6: kids = st.number_input("子ども", min_value=0, value=0)

    tags = st.multiselect("🏝 旅のテーマ", ["絶景", "秘境", "温泉", "郷土料理", "穴場", "エモい", "サウナ"], default=["絶景"])
    budget_input = st.text_input("💰 予算（1人あたり）", placeholder="例：10万円")

    if st.button("✨ この条件でスポットを探す", use_container_width=True, type="primary"):
        with st.spinner("AIが10件のスポット詳細を生成中..."):
            st.session_state.form_data = {"adults": adults, "kids": kids, "budget": budget_input}
            target = destination if destination else keyword
            # AIに構造化されたデータを要求
            prompt = f"""{target}周辺でテーマ『{tags}』に合うスポット10件を以下の形式で出力してください。
            名称 / 説明(150文字) / 推定予算 / おすすめ度(星5) / 混雑度(3段階) / 公式URL
            ※各スポットの間は '---' で区切ってください。"""
            
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            raw_text = res.choices[0].message.content
            st.session_state.parsed_spots = raw_text.split("---")[:10]
            st.session_state.step = "select_spots"
            st.rerun()

# --- STEP 2: お気に入り選択 (詳細カード形式) ---
elif st.session_state.step == "select_spots":
    st.subheader("🏝 気になるスポットをお気に入り登録（右上のボタンで選択）")
    
    selected_names = []
    for i, spot_data in enumerate(st.session_state.parsed_spots):
        # 簡易的なデータ分割（AIの出力を想定）
        lines = spot_data.strip().split("\n")
        if len(lines) < 2: continue
        
        name = lines[0].replace("#", "").strip()
        
        with st.container():
            st.markdown(f'<div class="spot-card">', unsafe_allow_html=True)
            
            # 右上にお気に入りボタンを配置するためのカラム
            col_main, col_fav = st.columns([9, 1])
            with col_fav:
                is_favorite = st.checkbox("⭐", key=f"fav_{i}", help="お気に入り登録")
                if is_favorite: selected_names.append(name)
            
            with col_main:
                col_img, col_txt = st.columns([1, 2])
                with col_img:
                    st.image(f"https://picsum.photos/seed/travel_{i}/500/350", use_container_width=True)
                with col_txt:
                    st.bold(name)
                    st.write(spot_data) # AIの回答内容を表示
                    st.markdown(f"""
                        <div class="status-box">
                            <span>💰 予算目安: 5,000円〜</span>
                            <span>⭐ おすすめ度: ★★★★☆</span>
                            <span>👥 混雑度: 普通</span>
                        </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

    hotel_type = st.selectbox("🏨 宿泊の希望", ["露天風呂付き客室", "モダンなホテル", "キャンプ", "古民家"])
    
    if st.button("🚀 選択したスポットでプランを作る", use_container_width=True, type="primary"):
        if not selected_names:
            st.warning("スポットを1つ以上選んでください！")
        else:
            st.session_state.selected_names = selected_names
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
