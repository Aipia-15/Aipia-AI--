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
        background-color: #111; width: 100%; padding: 80px 0;
        text-align: center; margin-bottom: 60px;
    }
    .aipia-logo { 
        font-family: 'Georgia', serif; font-style: italic; 
        font-size: 20vw; font-weight: bold; color: #FCF9F2; 
        line-height: 1.0; margin: 0;
    }
    .sub-title { 
        font-size: 3.5vw; color: #FCF9F2; font-weight: bold; 
        letter-spacing: 1.2vw; margin-top: 40px; display: inline-block;
    }
    .spot-card {
        background-color: white; padding: 30px; border-radius: 20px;
        margin-bottom: 30px; border: 1px solid #eee; box-shadow: 0 10px 30px rgba(0,0,0,0.05);
    }
    .spot-title { font-size: 28px; font-weight: bold; color: #111; margin-bottom: 10px; }
    label { font-size: 15px !important; font-weight: bold !important; color: #444 !important; }
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
    st.markdown("<h3 style='text-align:center;'>TRAVEL CONFIGURATION</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1: departure = st.text_input("🛫 出発地 (必須)", placeholder="例：東京、大阪駅...")
    with col2: destination = st.text_input("📍 目的地", placeholder="例：長野、徳島...")
    with col3: keyword = st.text_input("🔍 キーワード", placeholder="例：歴史、温泉...")

    # 直列配置
    col_date, col_p_adult, col_p_child, col_speed = st.columns([3, 1, 1, 2])
    with col_date:
        date_range = st.date_input("📅 日程（開始日と終了日を2箇所クリック：必須）", 
                                  value=(datetime.now(), datetime.now() + timedelta(days=2)))
    with col_p_adult:
        adults = st.number_input("大人", 1, 20, 2)
    with col_p_child:
        kids = st.number_input("子供", 0, 20, 0)
    with col_speed:
        walking_speed = st.select_slider("🚶 歩行速度 (必須)", options=["ゆっくり", "標準", "せっかち"], value="標準")

    tags = st.multiselect("🏝 旅のテーマ", ["絶景", "秘境", "歴史", "温泉", "美食"], default=["絶景", "秘境"])
    budget = st.text_input("💰 予算/人 (必須)", placeholder="例：5万円、100,000円...")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✨ この条件で秘境を探索", use_container_width=True, type="primary"):
        # --- 必須チェック ---
        if not departure:
            st.error("⚠️ 『出発地』を入力してください。")
        elif not budget:
            st.error("⚠️ 『予算』を入力してください。")
        elif not (isinstance(date_range, tuple) and len(date_range) == 2):
            st.error("⚠️ 日程は『開始日』と『終了日』の両方を選択してください。")
        else:
            with st.spinner("極上の秘境をリサーチ中..."):
                st.session_state.form_data = {
                    "departure": departure, "adults": adults, "kids": kids, 
                    "budget": budget, "speed": walking_speed, "dates": f"{date_range[0]}〜{date_range[1]}"
                }
                target = destination if destination else (keyword if keyword else "日本国内の秘境")
                prompt = f"{target}周辺で、テーマ『{tags}』に合う具体的な観光スポットを10件。名称、解説(120文字程度)の順で。区切りは --- 。"
                
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                st.session_state.parsed_spots = [s.strip() for s in res.choices[0].message.content.split("---") if "名称" in s]
                st.session_state.step = "select_spots"
                st.rerun()

# --- STEP 2: スポット選択 ---
elif st.session_state.step == "select_spots":
    st.markdown("<h2 style='text-align:center;'>SPOT DISCOVERY</h2>", unsafe_allow_html=True)
    selected_names = []
    
    for i, spot_text in enumerate(st.session_state.parsed_spots):
        name_match = re.search(r"名称[:：]\s*(.*)", spot_text)
        desc_match = re.search(r"解説[:：]\s*(.*)", spot_text)
        name = name_match.group(1) if name_match else f"スポット {i+1}"
        desc = desc_match.group(1) if desc_match else spot_text[:100]

        st.markdown(f'<div class="spot-card">', unsafe_allow_html=True)
        col_img, col_txt = st.columns([1, 2])
        with col_img:
            # 写真を復活 (Picsumを活用してスポットごとにユニークな画像を表示)
            st.image(f"https://picsum.photos/seed/aipia_{i}_{name}/800/600", use_container_width=True)
        with col_txt:
            st.markdown(f'<p class="spot-title">{name}</p>', unsafe_allow_html=True)
            st.write(desc)
            if st.checkbox(f"この場所をプランに入れる ⭐", key=f"sel_{i}"):
                selected_names.append(name)
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 最終プランを生成する", use_container_width=True, type="primary"):
        if selected_names:
            st.session_state.selected_names = selected_names
            st.session_state.step = "final_plan"
            st.rerun()
        else:
            st.error("⚠️ 最低1つはスポットを選んでください。")

# --- STEP 3: 最終プラン ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plan_content:
        f = st.session_state.form_data
        with st.spinner("AIコンシェルジュが執筆中..."):
            prompt = f"出発地:{f['departure']}、日程:{f['dates']}、予算:{f['budget']}、大人{f['adults']}名、子供{f['kids']}名、歩行:{f['speed']}。選んだスポット:{st.session_state.selected_names}。これらを巡る詳細な旅行プランを5つ提案して。"
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            st.session_state.final_plan_content = res.choices[0].message.content

    st.markdown(f'<div style="background:white; padding:50px; border-radius:30px; line-height:2;">{st.session_state.final_plan_content}</div>', unsafe_allow_html=True)
    if st.button("← 戻る"): 
        st.session_state.step = "input"; st.session_state.final_plan_content = ""; st.rerun()
