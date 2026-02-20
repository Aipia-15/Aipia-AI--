import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import re

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 2. デザイン (CSS)
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
    .spot-card {
        background-color: white; padding: 25px; border-radius: 15px;
        margin-bottom: 25px; border: 1px solid #eee; box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }
    .spot-title { font-size: 24px; font-weight: bold; color: #111; margin-bottom: 8px; }
    </style>
    """, unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "parsed_spots" not in st.session_state: st.session_state.parsed_spots = []
if "selected_names" not in st.session_state: st.session_state.selected_names = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}

# --- ヘッダー ---
st.markdown('<div class="black-banner"><p class="aipia-logo">Aipia</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力 ---
if st.session_state.step == "input":
    st.markdown("### 1. 旅行の条件を入力してください")
    col1, col2, col3 = st.columns(3)
    with col1: departure = st.text_input("🛫 出発地 (必須)", key="dep")
    with col2: destination = st.text_input("📍 目的地", placeholder="長野、徳島など", key="dest")
    with col3: budget = st.text_input("💰 予算/人 (必須)", placeholder="10万円など", key="bud")

    col_date, col_pa, col_pc, col_speed = st.columns([3, 1, 1, 2])
    with col_date: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now() + timedelta(days=1)))
    with col_pa: adults = st.number_input("大人", 1, 10, 2)
    with col_pc: kids = st.number_input("子供", 0, 10, 0)
    with col_speed: walking_speed = st.select_slider("🚶 歩行速度", options=["ゆっくり", "標準", "せっかち"], value="標準")

    st.markdown("#### 🏨 ホテルのこだわり")
    h1, h2 = st.columns(2)
    with h1: hotel_style = st.selectbox("宿泊スタイル", ["こだわらない", "高級旅館", "リゾートホテル", "古民家・民宿"])
    with h2: room_pref = st.multiselect("こだわり条件", ["露天風呂付", "和室", "洋室", "禁煙"])

    if st.button("✨ 次へ（スポットを検索）", use_container_width=True, type="primary"):
        if departure and budget and len(date_range) == 2:
            st.session_state.form_data = {
                "departure": departure, "destination": destination, "budget": budget, 
                "adults": adults, "kids": kids, "speed": walking_speed, 
                "dates": f"{date_range[0]}〜{date_range[1]}", "hotel": f"{hotel_style}({room_pref})"
            }
            with st.spinner("秘境をリサーチ中..."):
                # AIにスポットを箇条書きで出させる
                target = destination if destination else "日本の秘境"
                prompt = f"{target}周辺の観光スポットを8つ教えてください。名称と解説を100文字程度で。「名称：」「解説：」という言葉を必ず使ってください。"
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                
                # 抽出ロジックの改善：正規表現で「名称：」から始まるブロックをすべて見つける
                raw_text = res.choices[0].message.content
                found_spots = re.findall(r"(名称[:：].*?)(?=名称[:：]|$)", raw_text, re.DOTALL)
                
                if found_spots:
                    st.session_state.parsed_spots = found_spots
                    st.session_state.step = "select_spots"
                    st.rerun()
                else:
                    st.error("スポットが見つかりませんでした。目的地を変えて試してください。")
        else:
            st.error("必須項目を入力してください。")

# --- STEP 2: スポット選択（確実に表示） ---
elif st.session_state.step == "select_spots":
    st.markdown("## SPOT DISCOVERY")
    st.markdown("行きたいスポットにチェックを入れてください。")
    
    for i, spot_text in enumerate(st.session_state.parsed_spots):
        # 名前と解説をパース
        name_match = re.search(r"名称[:：]\s*(.*)", spot_text)
        name = name_match.group(1).split('\n')[0].strip() if name_match else f"おすすめスポット {i+1}"
        
        desc_match = re.search(r"解説[:：]\s*(.*)", spot_text, re.DOTALL)
        desc = desc_match.group(1).strip() if desc_match else spot_text

        st.markdown(f'<div class="spot-card">', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 2])
        with c1:
            st.image(f"https://picsum.photos/seed/{name}/400/300", use_container_width=True)
        with c2:
            st.markdown(f'<p class="spot-title">{name}</p>', unsafe_allow_html=True)
            st.write(desc)
            if st.checkbox(f"この場所を候補に入れる", key=f"sel_{i}"):
                if name not in st.session_state.selected_names:
                    st.session_state.selected_names.append(name)
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 プランを生成する", use_container_width=True, type="primary"):
        if st.session_state.selected_names:
            st.session_state.step = "final_plan"
            st.rerun()
        else:
            st.error("スポットを1つ以上選んでください。")

# --- STEP 3: 最終プラン（詳細版） ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plans:
        with st.spinner("詳細な旅程を算出中..."):
            f = st.session_state.form_data
            for p_label in ["プランA", "プランB"]:
                prompt = f"""
                出発地:{f['departure']}、目的地:{f['destination']}、日程:{f['dates']}。
                大人{f['adults']}名、子供{f['kids']}名、予算{f['budget']}。歩行:{f['speed']}。
                宿泊要望:{f['hotel']}。
                選択したスポット:{st.session_state.selected_names}。
                
                【指示】
                - 出発から到着まで、分刻みのタイムラインを作成。
                - 各スポットの滞在時間、移動手段（路線名・徒歩）、各工程の金額を明記。
                - 【Aipiaのおすすめ！】として、未選択の秘境を1つ追加。
                - 最後に交通費・宿泊費・入場料の「合計金額」を算出。
                """
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                st.session_state.final_plans[p_label] = res.choices[0].message.content

    col_left, col_right = st.columns([3, 1])
    with col_left:
        selected_p = st.tabs(list(st.session_state.final_plans.keys()))
        for i, tab in enumerate(selected_p):
            with tab:
                st.markdown(f"### {list(st.session_state.final_plans.keys())[i]} 詳細行程")
                st.write(st.session_state.final_plans[list(st.session_state.final_plans.keys())[i]])
    with col_right:
        st.info(f"予算: {f['budget']}\n\n人数: {f['adults'] + f['kids']}名")
        if st.button("やり直す"):
            st.session_state.step = "input"
            st.session_state.final_plans = {}
            st.rerun()
