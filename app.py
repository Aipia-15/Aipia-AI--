import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import re

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 2. デザイン (CSS) - 画像のUIに寄せる
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
    .plan-container {
        background-color: white; border-radius: 20px; padding: 40px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1); border: 1px solid #ddd;
        white-space: pre-wrap; font-size: 16px; line-height: 1.8;
    }
    </style>
    """, unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "parsed_spots" not in st.session_state: st.session_state.parsed_spots = []
if "selected_names" not in st.session_state: st.session_state.selected_names = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}

st.markdown('<div class="black-banner"><p class="aipia-logo">Aipia</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力 ---
if st.session_state.step == "input":
    st.markdown("### 1. 旅行の条件を入力してください")
    col1, col2, col3 = st.columns(3)
    with col1: departure = st.text_input("🛫 出発地 (必須)", key="dep", placeholder="例：東京駅")
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
                target = destination if destination else "日本の秘境"
                # 不用な言語や記号を混ぜないよう指示を強化
                prompt = f"{target}周辺の観光スポットを8つ教えてください。日本語のみを使用し、記号「や」を文頭に付けないでください。各スポットを「名称：」「解説：」の形式で出力してください。"
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                
                raw_text = res.choices[0].message.content
                # 抽出ロジックの改善（不要な記号を除去）
                raw_text = re.sub(r'[」」「]', '', raw_text) 
                found_spots = re.findall(r"(名称[:：].*?)(?=名称[:：]|$)", raw_text, re.DOTALL)
                
                if found_spots:
                    st.session_state.parsed_spots = found_spots
                    st.session_state.step = "select_spots"
                    st.rerun()
                else:
                    st.error("スポットが見つかりませんでした。")
        else:
            st.error("必須項目を入力してください。")

# --- STEP 2: スポット選択 ---
elif st.session_state.step == "select_spots":
    st.markdown("## SPOT DISCOVERY")
    for i, spot_text in enumerate(st.session_state.parsed_spots):
        name_match = re.search(r"名称[:：]\s*(.*)", spot_text)
        name = name_match.group(1).split('\n')[0].strip() if name_match else f"スポット {i+1}"
        desc_match = re.search(r"解説[:：]\s*(.*)", spot_text, re.DOTALL)
        desc = desc_match.group(1).strip() if desc_match else spot_text

        st.markdown(f'<div class="spot-card">', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 2])
        with c1: st.image(f"https://picsum.photos/seed/{name}/400/300", use_container_width=True)
        with c2:
            st.markdown(f'### {name}')
            st.write(desc)
            if st.checkbox(f"候補に入れる", key=f"sel_{i}"):
                if name not in st.session_state.selected_names: st.session_state.selected_names.append(name)
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 5つのプランを生成する", use_container_width=True, type="primary"):
        if st.session_state.selected_names:
            st.session_state.step = "final_plan"
            st.rerun()
        else:
            st.error("スポットを1つ以上選んでください。")

# --- STEP 3: 最終プラン（A〜E 5つ） ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plans:
        with st.spinner("予算内で帰宅までの行程を5パターン計算中..."):
            f = st.session_state.form_data
            for label in ["プランA", "プランB", "プランC", "プランD", "プランE"]:
                prompt = f"""
                あなたはプロの旅行コンシェルジュです。以下の条件で日本語の旅行プランを作成してください。
                出発地: {f['departure']}
                目的地: {f['destination']}
                日程: {f['dates']}
                予算: 1人あたり {f['budget']} 以内で完結（交通費・宿泊費・食費・入場料込）
                人数: 大人{f['adults']}名, 子供{f['kids']}名
                歩行速度: {f['speed']}
                選択スポット: {st.session_state.selected_names}

                【厳守事項】
                1. 行程は「{f['departure']}」を出発し、最終日に「{f['departure']}」へ帰宅するまでを分刻みで書くこと。
                2. 具体的な列車名、路線名、移動時間を記載すること。
                3. 各工程の予想金額を出し、最後に「合計金額」が予算内であることを示すこと。
                4. 「【Aipiaのおすすめ！】」として、選択されていない秘境スポットを1つ追加すること。
                5. 謎の記号や他言語を混ぜず、読みやすい日本語で出力すること。
                """
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                st.session_state.final_plans[label] = res.choices[0].message.content

    # タブでプラン切り替え
    tabs = st.tabs(list(st.session_state.final_plans.keys()))
    for i, tab in enumerate(tabs):
        label = list(st.session_state.final_plans.keys())[i]
        with tab:
            st.markdown(f"### 📍 {label} 詳細スケジュール")
            st.markdown(f'<div class="plan-container">{st.session_state.final_plans[label]}</div>', unsafe_allow_html=True)

    if st.button("最初に戻る"):
        st.session_state.step = "input"
        st.session_state.final_plans = {}
        st.rerun()
