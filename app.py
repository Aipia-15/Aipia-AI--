import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import re

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia")

# 2. クライアント設定
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 3. デザイン (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #FCF9F2; }
    .black-banner {
        background-color: #111; width: 100%; padding: 100px 0;
        text-align: center; margin-bottom: 80px;
    }
    .aipia-logo { 
        font-family: 'Georgia', serif; font-style: italic; 
        font-size: 25vw; font-weight: bold; color: #FCF9F2; 
        line-height: 1.0; margin: 0;
    }
    .sub-title { 
        font-size: 4vw; color: #FCF9F2; font-weight: bold; 
        letter-spacing: 1.5vw; margin-top: 50px; display: inline-block;
    }
    .spot-card {
        background-color: white; padding: 30px; border-radius: 20px;
        margin-bottom: 25px; border: 1px solid #eee; box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    /* ラベルを小さく */
    label { font-size: 14px !important; color: #666 !important; }
    </style>
    """, unsafe_allow_html=True)

if "step" not in st.session_state: st.session_state.step = "input"
if "parsed_spots" not in st.session_state: st.session_state.parsed_spots = []
if "final_plan_content" not in st.session_state: st.session_state.final_plan_content = ""

# --- ヘッダー ---
st.markdown(f"""
    <div class="black-banner">
        <p class="aipia-logo">Aipia</p>
        <p class="sub-title">- AIが創る、秘境への旅行プラン -</p>
    </div>
    """, unsafe_allow_html=True)

# --- STEP 1: 入力 ---
if st.session_state.step == "input":
    col1, col2, col3 = st.columns(3)
    with col1: departure = st.text_input("🛫 出発地", value="東京")
    with col2: destination = st.text_input("📍 目的地", placeholder="例：長野、徳島...")
    with col3: keyword = st.text_input("🔍 キーワード", placeholder="例：歴史、温泉...")

    # 大人・子供を横に直列配置
    col_date, col_p_adult, col_p_child, col_speed = st.columns([3, 1, 1, 2])
    with col_date:
        date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now() + timedelta(days=2)))
    with col_p_adult:
        adults = st.number_input("大人", 1, 20, 2)
    with col_p_child:
        kids = st.number_input("子供", 0, 20, 0)
    with col_speed:
        walking_speed = st.select_slider("🚶 歩行速度", options=["ゆっくり", "標準", "せっかち"], value="標準")

    tags = st.multiselect("🏝 テーマ", ["絶景", "秘境", "歴史", "温泉", "美食"], default=["絶景", "秘境"])
    budget = st.text_input("💰 予算/人")

    if st.button("✨ この条件で秘境を探索", use_container_width=True, type="primary"):
        if isinstance(date_range, tuple) and len(date_range) == 2:
            with st.spinner("世界中の秘境を検索中..."):
                st.session_state.form_data = {
                    "adults": adults, "kids": kids, "budget": budget, 
                    "speed": walking_speed, "dates": f"{date_range[0]}〜{date_range[1]}"
                }
                target = destination if destination else keyword
                prompt = f"{target}周辺で、テーマ『{tags}』に合う具体的な観光スポットを10件教えてください。各スポットは必ず '名称:' で始めて、次に '解説:' を書いてください。区切りは --- を使ってください。"
                
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                content = res.choices[0].message.content
                
                # スポット紹介を確実に抽出するための分割
                raw_spots = [s.strip() for s in content.split("---") if "名称" in s]
                st.session_state.parsed_spots = raw_spots
                st.session_state.step = "select_spots"
                st.rerun()
        else:
            st.error("⚠️ カレンダーで開始日と終了日の両方を選択してください。")

# --- STEP 2: スポット選択 ---
elif st.session_state.step == "select_spots":
    st.markdown("<h2 style='text-align:center;'>SPOT DISCOVERY</h2>", unsafe_allow_html=True)
    selected_names = []
    
    if not st.session_state.parsed_spots:
        st.warning("スポットが見つかりませんでした。もう一度条件を変えて試してください。")
        if st.button("戻る"): st.session_state.step = "input"; st.rerun()
    else:
        for i, spot_text in enumerate(st.session_state.parsed_spots):
            # 文字列から名称と解説を簡易抽出
            name_match = re.search(r"名称[:：]\s*(.*)", spot_text)
            desc_match = re.search(r"解説[:：]\s*(.*)", spot_text)
            name = name_match.group(1) if name_match else f"スポット {i+1}"
            desc = desc_match.group(1) if desc_match else spot_text[:100]

            st.markdown(f'<div class="spot-card">', unsafe_allow_html=True)
            if st.checkbox(f"⭐ {name}", key=f"check_{i}"):
                selected_names.append(name)
            st.write(desc)
            st.markdown('</div>', unsafe_allow_html=True)

        if st.button("🚀 最終プランを生成", use_container_width=True, type="primary"):
            if selected_names:
                st.session_state.selected_names = selected_names
                st.session_state.step = "final_plan"
                st.rerun()
            else:
                st.error("スポットを1つ以上選択してください。")

# --- STEP 3: 最終プラン ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plan_content:
        f = st.session_state.form_data
        with st.spinner("最高のプランを作成中..."):
            prompt = f"日程:{f['dates']}、大人{f['adults']}名、子供{f['kids']}名。スポット:{st.session_state.selected_names}。これらを巡る詳細な旅行プランを5つ提案して。"
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            st.session_state.final_plan_content = res.choices[0].message.content

    st.markdown(f'<div style="background:white; padding:40px; border-radius:20px;">{st.session_state.final_plan_content}</div>', unsafe_allow_html=True)
    if st.button("← 戻る"): 
        st.session_state.step = "input"; st.session_state.final_plan_content = ""; st.rerun()
