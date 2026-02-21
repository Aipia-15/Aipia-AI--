import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse
import json
import re

# --- 1. 基本設定 ---
st.set_page_config(layout="wide", page_title="Aipia - AI旅行編集コンシェルジュ", page_icon="Aipia.png")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

PREFECTURES = [""] + ["北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県", "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県", "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県", "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県", "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"]

def call_groq_safe(prompt):
    target_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    for model_id in target_models:
        try:
            res = client.chat.completions.create(model=model_id, messages=[{"role": "user", "content": prompt}], temperature=0.7)
            return res.choices[0].message.content
        except: continue
    return None

# CSS (左上ロゴと新しいヘッダーデザイン)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:wght@700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    
    /* 左上固定ヘッダー */
    .header-bar {
        display: flex;
        align-items: center;
        padding: 10px 20px;
        background-color: #FFF;
        border-bottom: 1px solid #EEE;
        margin-bottom: 30px;
        border-radius: 0 0 15px 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .logo-img { height: 40px; margin-right: 15px; }
    .logo-text { font-family: 'Playfair Display', serif; font-size: 1.8rem; color: #111; letter-spacing: 2px; margin: 0; }
    
    .spot-card { margin-bottom: 40px; padding: 20px; background: #FFF; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-left: 5px solid #D4AF37; }
    .day-box { background: linear-gradient(90deg, #E8F5E9, #FFF); padding: 10px 25px; border-radius: 8px; font-weight: bold; margin: 30px 0 15px 0; color: #2E7D32; border-left: 5px solid #2E7D32; }
    .time-step { background-color: #E3F2FD; padding: 20px; border-radius: 10px; margin: 10px 0; border: 1px solid #BBDEFB; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    .arrow { text-align: center; font-size: 1.5rem; color: #90CAF9; margin: 5px 0; }
    .spot-placeholder { width: 100%; height: 130px; background-color: #C8E6C9; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #2E7D32; font-weight: bold; font-size: 0.8rem; }
    .reserve-btn { background: linear-gradient(135deg, #D32F2F, #B71C1C); color: white !important; padding: 14px 28px; border-radius: 10px; text-decoration: none; font-weight: bold; display: inline-block; text-align: center; width: 100%; border: none; }
    .edit-panel { background: #FFF; border: 2px solid #D4AF37; padding: 25px; border-radius: 15px; margin: 20px 0; }
    </style>
""", unsafe_allow_html=True)

# 左上ロゴバーの表示
# 注意: Aipia.png がローカルにある場合、st.imageを使うかBase64エンコードして表示します
st.markdown(f"""
    <div class="header-bar">
        <img src="https://raw.githubusercontent.com/streamlit/streamlit/develop/examples/assets/streamlit_logo.png" class="logo-img" style="display:none;"> <p class="logo-text">Aipia</p>
    </div>
""", unsafe_allow_html=True)

# 実際のロゴ画像をサイドバー上部またはメインエリア左上に配置
col_logo, _ = st.columns([1, 5])
with col_logo:
    try:
        st.image("Aipia.png", width=60)
    except:
        st.caption("Aipia Logo")

# --- ロジック開始 ---
if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "plans" not in st.session_state: st.session_state.plans = []

# --- STEP 1: 入力 (ご指定のレイアウト変更反映済み) ---
if st.session_state.step == "input":
    st.subheader("✨ 旅のテーマを決める")
    keyword = st.text_input("🔍 キーワード検索（例：神秘的な森、地元の人しか知らない温泉）")
    st.write("---")
    walk_speed = st.select_slider("🚶‍♂️ 歩く速度", options=["ゆっくり", "普通", "早歩き"], value="普通")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1: dep_place = st.text_input("🛫 出発地点", value="新宿駅")
    with col2: date_range = st.date_input("📅 旅行日程", value=(datetime.now(), datetime.now() + timedelta(days=1)))
    with col3: dep_time = st.time_input("🕔 出発時刻", value=datetime.strptime("08:00", "%H:%M").time())
    
    col4, col5, col6 = st.columns([2, 2, 2])
    with col4: pref = st.selectbox("📍 都道府県", PREFECTURES)
    with col5: city = st.text_input("🏠 詳細エリア")
    with col6: budget = st.number_input("💰 予算/人", 5000, 500000, 50000)
    
    if st.button("⚜️ 秘境リサーチを開始", use_container_width=True, type="primary"):
        st.session_state.form_data = {"dep": dep_place, "dest": f"{pref}{city}", "speed": walk_speed}
        prompt = f"{pref}{city}周辺の秘境スポットを10件。名称|解説|住所"
        content = call_groq_safe(prompt)
        if content:
            st.session_state.found_spots = [l.split('|') for l in content.split('\n') if '|' in l]
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: スポット選択 (More機能 & 余白) ---
elif st.session_state.step == "select_spots":
    st.markdown(f"### 📍 {st.session_state.form_data['dest']} 秘境カタログ")
    for i, s in enumerate(st.session_state.found_spots):
        st.markdown('<div class="spot-card">', unsafe_allow_html=True)
        col_img, col_txt = st.columns([1, 4])
        with col_img: st.markdown(f'<div class="spot-placeholder">{s[0][:10]}</div>', unsafe_allow_html=True)
        with col_txt:
            st.markdown(f"**{s[0]}**")
            st.caption(s[1])
            if st.checkbox("このスポットを採用", key=f"s_{i}"):
                if s[0] not in st.session_state.selected_spots: st.session_state.selected_spots.append(s[0])
        st.markdown('</div>', unsafe_allow_html=True)
    
    col_m, col_n = st.columns(2)
    with col_m:
        if st.button("➕ もっとリサーチする"):
            content = call_groq_safe(f"{st.session_state.form_data['dest']}の別の秘境。名称|解説|住所")
            if content: st.session_state.found_spots.extend([l.split('|') for l in content.split('\n') if '|' in l]); st.rerun()
    with col_n:
        if st.button("✅ プラン生成へ進む", type="primary"): st.session_state.step = "plan_gen"; st.rerun()

# --- STEP 4: プラン生成・編集・再生成 ---
elif st.session_state.step == "plan_gen":
    if not st.session_state.plans:
        with st.spinner("詳細な移動ルートを構築中..."):
            for _ in range(5):
                prompt = f"{st.session_state.form_data['dep']}発、{st.session_state.selected_spots}を含む2日間プランをJSONで。各地点の『到着-出発時間』、出発地からの移動手段、ホテルの滞在時間を必ず含むこと。"
                res = call_groq_safe(prompt)
                try: 
                    match = re.search(r"\{.*\}", res, re.DOTALL)
                    if match: st.session_state.plans.append(json.loads(match.group()))
                except: continue
    
    plan_idx = st.sidebar.selectbox("プランを比較", [f"プラン {i+1}" for i in range(len(st.session_state.plans))])
    current_data = st.session_state.plans[int(plan_idx[-1])-1]

    # 編集トグル
    if st.toggle("🛠️ このプランを編集（場所の入れ替え・時間調整）"):
        st.markdown('<div class="edit-panel">', unsafe_allow_html=True)
        st.subheader("プラン編集")
        for d_idx, day in enumerate(current_data['days']):
            st.write(f"📅 {day['label']}")
            for s_idx, step in enumerate(day['steps']):
                c_e1, c_e2, c_e3 = st.columns([1, 2, 1])
                step['time'] = c_e1.text_input("時間", value=step['time'], key=f"t{d_idx}{s_idx}")
                step['content'] = c_e2.text_input("内容", value=step['content'], key=f"c{d_idx}{s_idx}")
                # 順序の概念はここではシンプルに配列書き換えで対応
        if st.button("🔄 編集内容で再生成（確定前に清書）"): st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # 表示
    for day in current_data['days']:
        st.markdown(f'<div class="day-box">{day["label"]}</div>', unsafe_allow_html=True)
        for i, step in enumerate(day['steps']):
            st.markdown(f'<div class="time-step"><small><b>{step["time"]}</b></small><br>{step["content"]}</div>', unsafe_allow_html=True)
            if i < len(day['steps']) - 1: st.markdown('<div class="arrow">↓</div>', unsafe_allow_html=True)
    
    if st.button("🏆 このプランを最終確定する", use_container_width=True, type="primary"):
        st.session_state.confirmed_plan = current_data; st.session_state.step = "share"; st.rerun()

# --- STEP 5: 確定・共有 ---
elif st.session_state.step == "share":
    st.success("🎉 プランが完成しました！")
    data = st.session_state.confirmed_plan
    for day in data['days']:
        st.markdown(f'<div class="day-box">{day["label"]}</div>', unsafe_allow_html=True)
        for i, step in enumerate(day['steps']):
            name = step["content"].split('：')[0].strip()
            url = f"https://www.google.com/search?q={urllib.parse.quote(name)}"
            st.info(f"🕒 {step['time']} \n\n **[{name}]({url})** \n {step['content'].replace(name, '')}")

    st.markdown(f"### 🏨 宿泊先: {data.get('hotel', {{}}).get('name', '宿泊施設')}")
    st.write("---")
    c1, c2 = st.columns(2)
    c1.markdown(f'<a href="https://line.me/R/msg/text/?旅プラン確定" class="reserve-btn" style="background-color:#06C755;">LINE共有</a>', unsafe_allow_html=True)
    c2.markdown(f'<a href="mailto:?subject=旅プラン&body=内容" class="reserve-btn" style="background-color:#EA4335;">Gmail共有</a>', unsafe_allow_html=True)
    if st.button("🏠 ホームへ戻る"): st.session_state.clear(); st.rerun()
