import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import re

# --- 1. ページ設定 ---
st.set_page_config(layout="wide", page_title="Aipia")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. スタイル設定（画像に寄せたUI） ---
st.markdown("""
    <style>
    .stApp { background-color: #FCF9F2; }
    .black-banner {
        background-color: #111; width: 100%; padding: 40px 0;
        text-align: center; margin-bottom: 20px;
    }
    .aipia-logo { 
        font-family: 'Georgia', serif; font-style: italic; 
        font-size: 8vw; font-weight: bold; color: #FCF9F2; line-height: 1.0; margin: 0;
    }
    /* プラン表示用カード */
    .main-plan-card {
        background-color: white; border-radius: 25px; padding: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1); border: 1px solid #ddd;
    }
    .timeline-item { border-left: 2px dashed #999; margin-left: 20px; padding-left: 20px; position: relative; }
    .timeline-time { font-weight: bold; color: #333; }
    .spot-highlight { background: #f0f0f0; padding: 10px; border-radius: 10px; margin: 5px 0; }
    .aipia-recommend { border: 2px solid #ffcc00; background: #fffdf0; padding: 10px; border-radius: 10px; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "parsed_spots" not in st.session_state: st.session_state.parsed_spots = []
if "selected_names" not in st.session_state: st.session_state.selected_names = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}

# --- ヘッダー ---
st.markdown('<div class="black-banner"><p class="aipia-logo">Aipia</p><p style="color:white; letter-spacing:10px;">- 秘境への旅路 -</p></div>', unsafe_allow_html=True)

# --- STEP 1: 基本条件入力 ---
if st.session_state.step == "input":
    st.markdown("### 1. 基本条件を入力してください")
    col1, col2, col3 = st.columns(3)
    with col1: departure = st.text_input("🛫 出発地 (必須)", key="dep")
    with col2: destination = st.text_input("📍 目的地", placeholder="長野、徳島など")
    with col3: budget = st.text_input("💰 予算/人 (必須)", placeholder="10万円など")

    col_date, col_pa, col_pc, col_speed = st.columns([3, 1, 1, 2])
    with col_date: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now() + timedelta(days=1)))
    with col_pa: adults = st.number_input("大人", 1, 10, 2)
    with col_pc: kids = st.number_input("子供", 0, 10, 0)
    with col_speed: walking_speed = st.select_slider("🚶 歩行速度", options=["ゆっくり", "標準", "せっかち"], value="標準")

    # ホテルのこだわり条件
    st.markdown("#### 🏨 ホテルのこだわり")
    h1, h2, h3 = st.columns(3)
    with h1: hotel_style = st.selectbox("宿泊スタイル", ["こだわらない", "高級旅館", "リゾートホテル", "古民家・民宿"])
    with h2: room_pref = st.multiselect("こだわり条件", ["露天風呂付", "和室", "洋室", "禁煙", "ペット可"])
    with h3: hotel_etc = st.text_input("その他宿への要望", placeholder="例：夕食は部屋出し希望")

    if st.button("✨ 次へ進む", use_container_width=True, type="primary"):
        if departure and budget and len(date_range) == 2:
            st.session_state.form_data = {
                "departure": departure, "destination": destination, "budget": budget, 
                "adults": adults, "kids": kids, "speed": walking_speed, 
                "dates": f"{date_range[0]}〜{date_range[1]}", "hotel": f"{hotel_style}({room_pref}) {hotel_etc}"
            }
            # スポット検索
            with st.spinner("周辺の秘境スポットを探索中..."):
                prompt = f"{destination}周辺の観光地を8つ提案してください。名称、解説(100文字)の形式で。区切りは === 。"
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                st.session_state.parsed_spots = [s.strip() for s in res.choices[0].message.content.split("===") if "名称" in s]
                st.session_state.step = "select_spots"
                st.rerun()
        else:
            st.error("必須項目を入力してください。")

# --- STEP 2: スポット選択 ---
elif st.session_state.step == "select_spots":
    st.markdown("### 2. 行きたいスポットを選択してください")
    for i, spot_text in enumerate(st.session_state.parsed_spots):
        name = re.search(r"名称[:：]\s*(.*)", spot_text).group(1) if "名称" in spot_text else f"スポット{i}"
        with st.container():
            st.markdown('<div class="spot-card">', unsafe_allow_html=True)
            c1, c2 = st.columns([1, 3])
            c1.image(f"https://picsum.photos/seed/{name}/300/200")
            if c2.checkbox(f"**{name}**", key=f"s_{i}"):
                if name not in st.session_state.selected_names: st.session_state.selected_names.append(name)
            c2.write(spot_text)
            st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 プランを生成する", use_container_width=True, type="primary"):
        if st.session_state.selected_names:
            st.session_state.step = "final_plan"
            st.rerun()
        else:
            st.error("1つ以上選択してください。")

# --- STEP 3: 最終プラン（画像のUI再現） ---
elif st.session_state.step == "final_plan":
    # 5つのプランを生成（未生成の場合のみ）
    if not st.session_state.final_plans:
        with st.spinner("複数のプランを計算中..."):
            f = st.session_state.form_data
            for p_label in ["プランA", "プランB", "プランC"]:
                prompt = f"""
                {f['dates']}、{f['departure']}発、目的地{f['destination']}。
                予算{f['budget']}、大人{f['adults']}名、子供{f['kids']}名。歩行:{f['speed']}。
                宿要望:{f['hotel']}。選択スポット:{st.session_state.selected_names}。
                
                以下の項目を必ず含めて詳細な行程を作成してください：
                1. 各地点の出発/到着時間
                2. 交通手段（電車名、路線、徒歩分数）
                3. 各スポットの滞在時間
                4. 各項目の金額（交通費、入場料等）
                5. 合計金額の算出
                6. 【Aipiaのおすすめ！】として、未選択の秘境スポットを1つ行程に追加。
                """
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                st.session_state.final_plans[p_label] = res.choices[0].message.content

    # UIレイアウト
    col_left, col_mid, col_right = st.columns([1, 3, 1])

    # 左側：プラン切り替えタブ風
    with col_left:
        st.write("### プラン一覧")
        selected_plan = st.radio("プラン選択", list(st.session_state.final_plans.keys()), label_visibility="collapsed")
        st.button("プラン改善", use_container_width=True)

    # 中央：メインプラン表示（画像風）
    with col_mid:
        st.markdown(f"## {selected_plan} <span style='font-size:15px; font-weight:normal;'>すべての条件を満たす</span>", unsafe_allow_html=True)
        st.markdown(f'<div class="main-plan-card">{st.session_state.final_plans[selected_plan]}</div>', unsafe_allow_html=True)

    # 右側：概要・登録スポット
    with col_right:
        st.markdown(f"""
            <div style="background:white; padding:15px; border-radius:10px; border:1px solid #ddd;">
                <p><b>予算金額</b>: {st.session_state.form_data['budget']}</p>
                <p><b>旅行人数</b>: 大人{st.session_state.form_data['adults']} 小人{st.session_state.form_data['kids']}</p>
            </div>
            <br>
            <div style="background:#333; color:white; padding:10px; border-radius:5px 5px 0 0;">★ 登録したスポット</div>
            <div style="background:white; padding:15px; border:1px solid #ddd;">
                {'<br>'.join([f"・{name}" for name in st.session_state.selected_names])}
            </div>
        """, unsafe_allow_html=True)
        if st.button("最初に戻る"):
            st.session_state.step = "input"
            st.session_state.final_plans = {}
            st.rerun()
