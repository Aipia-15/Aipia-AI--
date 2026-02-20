import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse
import json

# --- 1. 基本設定 ---
st.set_page_config(layout="wide", page_title="Aipia - AI秘境旅行プラン")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def call_groq_safe(prompt):
    target_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    for model_id in target_models:
        try:
            res = client.chat.completions.create(model=model_id, messages=[{"role": "user", "content": prompt}], temperature=0.7)
            return res.choices[0].message.content
        except: continue
    return None

# CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    .header-container { text-align: center; padding: 20px 0; border-bottom: 2px solid #D4AF37; background: #FFF; margin-bottom: 10px; }
    .aipia-logo { font-size: 3rem; color: #111; letter-spacing: 5px; margin: 0; font-weight: bold; }
    .aipia-sub { color: #D4AF37; font-weight: bold; letter-spacing: 2px; font-size: 0.8rem; margin-top: -5px; }
    
    .day-box { background-color: #E8F5E9; padding: 10px 20px; border-radius: 12px; display: inline-block; font-weight: bold; margin: 20px 0 10px 0; color: #2E7D32; }
    .time-step { background-color: #E3F2FD; padding: 15px; border-radius: 8px; margin: 5px 0; border: 1px solid #BBDEFB; }
    .arrow { text-align: center; font-size: 1.5rem; color: #90CAF9; margin: 2px 0; }
    .ai-badge { background-color: #FF5252; color: white; font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; float: right; font-weight: bold; }
    .advice-box { background-color: #F1F8E9; padding: 20px; border-radius: 10px; border: 1px solid #C8E6C9; margin-bottom: 20px; }
    .hotel-title { font-size: 1.6rem; font-weight: bold; color: #1A237E; margin: 15px 0; }
    .spot-img { width: 100%; border-radius: 8px; margin-bottom: 10px; object-fit: cover; height: 150px; background: #EEE; }
    </style>
""", unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "plans" not in st.session_state: st.session_state.plans = []

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">-AIが創る、秘境への旅行プラン-</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力 ---
if st.session_state.step == "input":
    # 1. 歩く速度
    walk_speed = st.select_slider("🚶‍♂️ 歩く速度", options=["ゆっくり", "普通", "早歩き"], value="普通")
    # 2. キーワード検索
    keyword = st.text_input("🔍 キーワード検索", placeholder="例：絶景の滝、静かな古民家カフェ")
    st.write("---")
    # 3. メイン入力
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1: dep_place = st.text_input("🛫 出発地点", value="新宿駅")
    with c2: date_range = st.date_input("📅 旅行日程", value=(datetime.now(), datetime.now() + timedelta(days=1)))
    with c3: dep_time = st.time_input("🕔 出発時刻", value=datetime.strptime("08:00", "%H:%M").time())
    c4, c5, c6 = st.columns(3)
    with c4: pref = st.selectbox("📍 都道府県", [""] + ["北海道", "東京都", "神奈川県", "京都府", "大阪府"]) # 短縮表示
    with c5: city = st.text_input("🏠 詳細エリア")
    with c6: budget = st.number_input("💰 予算/人", 5000, 500000, 50000)
    c7, c8, c9 = st.columns([2, 1, 1])
    with c7: purposes = st.multiselect("✨ 目的", ["秘境探索", "美食", "温泉", "歴史", "写真"], default=["秘境探索"])
    with c8: adults = st.number_input("大人", 1, 10, 2)
    with c9: kids = st.number_input("小人", 0, 10, 0)

    if st.button("⚜️ 秘境リサーチ開始", use_container_width=True, type="primary"):
        st.session_state.form_data = {"dep": dep_place, "dest": f"{pref}{city}", "speed": walk_speed}
        prompt = f"{pref}{city}周辺の秘境スポットを10件。名称|解説|住所|画像検索キーワード"
        content = call_groq_safe(prompt)
        if content:
            st.session_state.found_spots = [l.split('|') for l in content.split('\n') if '|' in l]
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: カタログ (More機能復活) ---
elif st.session_state.step == "select_spots":
    st.markdown(f"### 📍 {st.session_state.form_data['dest']} スポット")
    for i, s in enumerate(st.session_state.found_spots):
        col1, col2 = st.columns([1, 3])
        with col1:
            img_url = f"https://source.unsplash.com/featured/?{urllib.parse.quote(s[3] if len(s)>3 else s[0])}"
            st.markdown(f'<img src="{img_url}" class="spot-img">', unsafe_allow_html=True)
        with col2:
            st.markdown(f"**{s[0]}**")
            st.caption(s[1])
            if st.checkbox("採用", key=f"s_{i}"):
                if s[0] not in st.session_state.selected_spots: st.session_state.selected_spots.append(s[0])
    
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        if st.button("➕ More (10個追加)"):
            prompt = f"{st.session_state.form_data['dest']}の別の秘境を10件。名称|解説|住所|画像検索キーワード"
            content = call_groq_safe(prompt)
            if content: st.session_state.found_spots.extend([l.split('|') for l in content.split('\n') if '|' in l]); st.rerun()
    with c_m2:
        if st.button("✅ ホテルの希望調査へ", type="primary"): st.session_state.step = "hotel_survey"; st.rerun()

# --- STEP 3: ホテル調査 (バリアフリー追加) ---
elif st.session_state.step == "hotel_survey":
    st.markdown("### 🏨 宿泊の希望")
    h_type = st.radio("ホテルのタイプ", ["絶景の宿", "老舗旅館", "モダンホテル"])
    h_barrier = st.radio("バリアフリー対応", ["特に不要", "段差が少ない", "車椅子対応・手すりあり"])
    if st.button("✨ 5つのプランを同時生成", type="primary"):
        st.session_state.step = "plan_generation"; st.rerun()

# --- STEP 4: プラン生成 ---
elif st.session_state.step == "plan_generation":
    if not st.session_state.plans:
        with st.spinner("5通りの詳細プランを構築中..."):
            for i in range(5):
                prompt = f"""
                2日間のプランをJSON形式で作成せよ。
                出発：{st.session_state.form_data['dep']}
                採用：{st.session_state.selected_spots}
                ルール：
                1. 各スポットに「到着時間」「出発時間」を明記。
                2. AIおすすめランチは実在する店名を記載し[AIおすすめ]タグを付与。
                3. 特急利用時は「えきねっと等の予約サイト名」と「予約手順」を記載。
                4. ホテル帰宅(チェックイン)時間を必ず記載。
                """
                res = call_groq_safe(prompt)
                try: st.session_state.plans.append(json.loads(res[res.find('{'):res.rfind('}')+1]))
                except: continue
    
    st.session_state.step = "display"; st.rerun()

# --- STEP 5: 表示 ---
elif st.session_state.step == "display":
    plan_idx = st.sidebar.radio("プラン切替", [f"プラン {i+1}" for i in range(len(st.session_state.plans))])
    data = st.session_state.plans[int(plan_idx[-1])-1]
    
    for day in data['days']:
        st.markdown(f'<div class="day-box">{day["label"]}</div>', unsafe_allow_html=True)
        for step in day['steps']:
            ai_tag = '<span class="ai-badge">AIおすすめ</span>' if step.get('is_ai_suggested') else ""
            st.markdown(f'<div class="time-step">{ai_tag}<small>{step["time"]}</small><br><b>{step["content"]}</b></div>', unsafe_allow_html=True)
            st.markdown('<div class="arrow">↓</div>', unsafe_allow_html=True)

    st.markdown("""<div class="advice-box"><b>💡 Aipiaの旅のアドバイス</b><br>
    1. 秘境エリアは電波が弱いためマップを事前保存しましょう。<br>
    2. 特急券は早割（トクだ値等）で30%安くなる場合があります。<br>
    3. 現地の移動はタクシー予約が必須な場所が多いです。</div>""", unsafe_allow_html=True)

    if st.button("🏆 このプランで確定（共有ページへ）"):
        st.session_state.step = "share"; st.rerun()

elif st.session_state.step == "share":
    st.success("プランが確定しました！")
    st.markdown("### 📤 共有する")
    line_url = f"https://line.me/R/msg/text/?旅プラン確定！"
    gmail_url = f"https://mail.google.com/mail/?view=cm&fs=1&body=旅プラン"
    st.markdown(f'<a href="{line_url}" target="_blank">LINEで共有</a> | <a href="{gmail_url}" target="_blank">Gmailで共有</a>', unsafe_allow_html=True)
    if st.button("🏠 最初に戻る"): st.session_state.clear(); st.rerun()
