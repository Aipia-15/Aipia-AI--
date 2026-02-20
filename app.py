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
        background-color: #111; width: 100%; padding: 60px 0;
        text-align: center; margin-bottom: 40px;
    }
    .aipia-logo { 
        font-family: 'Georgia', serif; font-style: italic; 
        font-size: 15vw; font-weight: bold; color: #FCF9F2; 
        line-height: 1.0; margin: 0;
    }
    .sub-title { 
        font-size: 3vw; color: #FCF9F2; font-weight: bold; 
        letter-spacing: 1.2vw; margin-top: 30px; display: inline-block;
    }
    .spot-card {
        background-color: white; padding: 25px; border-radius: 15px;
        margin-bottom: 25px; border: 1px solid #eee; box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }
    .spot-title { font-size: 24px; font-weight: bold; color: #111; margin-bottom: 8px; }
    label { font-size: 14px !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# セッション管理
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
    st.markdown("<h3 style='text-align:center;'>TRAVEL CONFIGURATION</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1: departure = st.text_input("🛫 出発地 (必須)", key="dep")
    with col2: destination = st.text_input("📍 目的地", placeholder="長野、徳島など", key="dest")
    with col3: keyword = st.text_input("🔍 キーワード", placeholder="秘境、温泉など", key="kw")

    col_date, col_pa, col_pc, col_speed = st.columns([3, 1, 1, 2])
    with col_date:
        date_range = st.date_input("📅 日程 (必須：開始と終了を選択)", 
                                  value=(datetime.now(), datetime.now() + timedelta(days=2)))
    with col_pa: adults = st.number_input("大人", 1, 20, 2)
    with col_pc: kids = st.number_input("子供", 0, 20, 0)
    with col_speed: walking_speed = st.select_slider("🚶 歩行速度", options=["ゆっくり", "標準", "せっかち"], value="標準")

    budget = st.text_input("💰 予算/人 (必須)", placeholder="10万円など")
    tags = st.multiselect("🏝 テーマ", ["絶景", "秘境", "歴史", "温泉", "美食"], default=["絶景", "秘境"])

    if st.button("✨ この条件で秘境を探索", use_container_width=True, type="primary"):
        if not departure or not budget or not (isinstance(date_range, tuple) and len(date_range) == 2):
            st.error("⚠️ 出発地、予算、日程（開始と終了）をすべて正しく入力してください。")
        else:
            with st.spinner("スポット情報を生成中..."):
                st.session_state.form_data = {
                    "departure": departure, "adults": adults, "kids": kids, 
                    "budget": budget, "speed": walking_speed, "dates": f"{date_range[0]}〜{date_range[1]}"
                }
                # AIに厳格なルールで出力させる
                target = destination if destination else keyword
                prompt = f"""{target}周辺の観光スポットを8つ提案してください。
                以下の形式を厳守し、各スポットを '===' で区切ってください。
                名称: (スポット名)
                解説: (100文字程度の解説)
                ===
                """
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                
                # 生のテキストを保存
                raw_content = res.choices[0].message.content
                # 念のため名称が含まれている行を分割してリスト化
                spots = [s.strip() for s in raw_content.split("===") if "名称" in s]
                
                if spots:
                    st.session_state.parsed_spots = spots
                    st.session_state.step = "select_spots"
                    st.rerun()
                else:
                    st.error("AIからの回答が読み取れませんでした。もう一度お試しください。")

# --- STEP 2: スポット選択 (ここが肝) ---
elif st.session_state.step == "select_spots":
    st.markdown("<h2 style='text-align:center;'>SPOT DISCOVERY</h2>", unsafe_allow_html=True)
    selected_names = []
    
    # 確実に1件ずつカードとして表示する
    for i, spot_text in enumerate(st.session_state.parsed_spots):
        # 名前と解説を抽出
        name = "不明なスポット"
        desc = spot_text
        
        name_search = re.search(r"名称[:：]\s*(.*)", spot_text)
        if name_search: name = name_search.group(1).strip()
        
        desc_search = re.search(r"解説[:：]\s*(.*)", spot_text)
        if desc_search: desc = desc_search.group(1).strip()

        st.markdown(f'<div class="spot-card">', unsafe_allow_html=True)
        c_img, c_txt = st.columns([1, 2])
        with c_img:
            # プレースホルダー画像（写真復活）
            st.image(f"https://picsum.photos/seed/{i}_{name}/400/300", use_container_width=True)
        with c_txt:
            st.markdown(f'<p class="spot-title">{name}</p>', unsafe_allow_html=True)
            st.write(desc)
            if st.checkbox(f"この場所を選択 ⭐", key=f"sel_{i}"):
                selected_names.append(name)
        st.markdown('</div>', unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🚀 プランを生成", use_container_width=True, type="primary"):
            if selected_names:
                st.session_state.selected_names = selected_names
                st.session_state.step = "final_plan"
                st.rerun()
            else:
                st.error("スポットを1つ以上選んでください。")
    with col_btn2:
        if st.button("← 戻る"): st.session_state.step = "input"; st.rerun()

# --- STEP 3: 最終プラン ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plan_content:
        f = st.session_state.form_data
        with st.spinner("AIが旅程を執筆中..."):
            prompt = f"{f['dates']}、{f['departure']}発、予算{f['budget']}。大人{f['adults']}名、子供{f['kids']}名、歩行速度:{f['speed']}。選んだ場所:{st.session_state.selected_names}。これらを使った5つの詳細な旅行プランを提案して。"
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            st.session_state.final_plan_content = res.choices[0].message.content

    st.markdown(f'<div style="background:white; padding:40px; border-radius:20px;">{st.session_state.final_plan_content}</div>', unsafe_allow_html=True)
    if st.button("← 戻る"): 
        st.session_state.step = "input"; st.session_state.final_plan_content = ""; st.rerun()
