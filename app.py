import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse
import json

# --- 1. 基本設定・都道府県リスト完全版 ---
st.set_page_config(layout="wide", page_title="Aipia - AI秘境旅行プラン")
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

# CSS (UIデザイン指定を完全反映)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:wght@700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    .header-container { text-align: center; padding: 20px 0; border-bottom: 2px solid #D4AF37; background: #FFF; margin-bottom: 10px; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 3rem; color: #111; letter-spacing: 5px; margin: 0; }
    .aipia-sub { color: #D4AF37; font-weight: bold; letter-spacing: 2px; font-size: 0.8rem; margin-top: -5px; }
    
    .day-box { background-color: #E8F5E9; padding: 10px 25px; border-radius: 12px; display: inline-block; font-weight: bold; margin: 25px 0 10px 0; color: #2E7D32; border: 1px solid #C8E6C9; }
    .time-step { background-color: #E3F2FD; padding: 15px; border-radius: 8px; margin: 5px 0; border: 1px solid #BBDEFB; line-height: 1.6; }
    .arrow { text-align: center; font-size: 1.8rem; color: #90CAF9; margin: 2px 0; font-weight: bold; }
    .ai-badge { background-color: #FF5252; color: white; font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; float: right; font-weight: bold; }
    .advice-box { background-color: #F1F8E9; padding: 20px; border-radius: 10px; border: 1px solid #C8E6C9; margin: 30px 0; }
    .hotel-highlight { font-size: 1.8rem; font-weight: bold; color: #1A237E; margin: 15px 0; border-bottom: 2px solid #1A237E; display: inline-block; }
    .spot-img { width: 100%; border-radius: 10px; margin-bottom: 10px; object-fit: cover; height: 180px; background: #EEE; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    .reserve-btn { background-color: #D32F2F; color: white !important; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# セッション初期化
if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "plans" not in st.session_state: st.session_state.plans = []

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">-AIが創る、秘境への旅行プラン-</p></div>', unsafe_allow_html=True)

# --- STEP 1: ホーム画面 ---
if st.session_state.step == "input":
    walk_speed = st.select_slider("🚶‍♂️ 歩く速度", options=["ゆっくり", "普通", "早歩き"], value="普通")
    keyword = st.text_input("🔍 キーワード検索（例：静かな滝、古民家ランチ）")
    st.write("---")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1: dep_place = st.text_input("🛫 出発地点", value="新宿駅")
    with col2: date_range = st.date_input("📅 旅行日程", value=(datetime.now(), datetime.now() + timedelta(days=1)))
    with col3: dep_time = st.time_input("🕔 出発時刻", value=datetime.strptime("08:00", "%H:%M").time())
    
    col4, col5, col6 = st.columns([2, 2, 2])
    with col4: pref = st.selectbox("📍 都道府県", PREFECTURES)
    with col5: city = st.text_input("🏠 詳細エリア・市区町村")
    with col6: budget = st.number_input("💰 予算/人", 5000, 500000, 50000)
    
    col7, col8, col9 = st.columns([2, 1, 1])
    with col7: purposes = st.multiselect("✨ 目的", ["秘境探索", "美食", "温泉", "歴史", "写真映え"], default=["秘境探索"])
    with col8: adults = st.number_input("大人", 1, 20, 2)
    with col9: kids = st.number_input("小人", 0, 20, 0)

    if st.button("⚜️ 秘境リサーチを開始する", use_container_width=True, type="primary"):
        if not pref: st.error("都道府県を選択してください"); st.stop()
        st.session_state.form_data = {"dep": dep_place, "dest": f"{pref}{city}", "speed": walk_speed, "start_date": date_range[0]}
        prompt = f"{pref}{city}周辺の{keyword}に関連する秘境スポットを10件。名称|解説|住所|画像検索ワード"
        content = call_groq_safe(prompt)
        if content:
            st.session_state.found_spots = [l.split('|') for l in content.split('\n') if '|' in l]
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: スポット選択 ---
elif st.session_state.step == "select_spots":
    st.markdown(f"### 📍 {st.session_state.form_data['dest']} スポットカタログ")
    for i, s in enumerate(st.session_state.found_spots):
        col_img, col_txt = st.columns([1, 3])
        with col_img:
            search_word = s[3] if len(s) > 3 else s[0]
            st.markdown(f'<img src="https://source.unsplash.com/featured/?{urllib.parse.quote(search_word)}" class="spot-img">', unsafe_allow_html=True)
        with col_txt:
            st.markdown(f"**{s[0]}**")
            st.caption(s[1])
            if st.checkbox("このスポットを採用", key=f"s_{i}"):
                if s[0] not in st.session_state.selected_spots: st.session_state.selected_spots.append(s[0])
        st.divider()
    
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        if st.button("➕ More (さらに10個リサーチ)"):
            prompt = f"{st.session_state.form_data['dest']}の別の秘境を10件。名称|解説|住所|画像検索ワード"
            content = call_groq_safe(prompt)
            if content: st.session_state.found_spots.extend([l.split('|') for l in content.split('\n') if '|' in l]); st.rerun()
    with c_m2:
        if st.button("✅ ホテルの希望調査へ進む", type="primary"): st.session_state.step = "hotel_survey"; st.rerun()

# --- STEP 3: ホテル調査 ---
elif st.session_state.step == "hotel_survey":
    st.markdown("### 🏨 宿泊の希望")
    h_type = st.selectbox("ホテルのタイプ", ["絶景が見える宿", "歴史ある老舗旅館", "モダンな隠れ家ホテル", "コスパ重視の宿"])
    h_barrier = st.radio("バリアフリー観点", ["特に指定なし", "車椅子対応・手すりあり", "段差が少ない/エレベーター近接"])
    
    if st.button("✨ 5つのプランを生成する", type="primary"):
        st.session_state.hotel_wish = f"{h_type}(バリアフリー:{h_barrier})"
        st.session_state.step = "plan_gen"; st.rerun()

# --- STEP 4: プラン生成 ---
elif st.session_state.step == "plan_gen":
    if not st.session_state.plans:
        with st.spinner("5通りの詳細な旅程を構築しています..."):
            for i in range(5):
                prompt = f"""
                2日間のプランをJSON形式で作成せよ。
                条件：歩く速度={st.session_state.form_data['speed']}
                採用スポット：{st.session_state.selected_spots}
                
                ルール：
                1. 各地点に「到着時間」と「出発時間」を必ず記載。
                2. 実在するホテル名と、夕方の「ホテル帰宅時間」を記載。
                3. AIおすすめの具体的ランチ店名(実在)を出し、右上に[AIおすすめ]タグ。
                4. 特急利用時は、予約サイト(えきねっと等)と予約手順を記載。
                JSON構造: {{"days": [{{"label": "一日目", "steps": [{{"time": "時間", "content": "内容", "is_ai_suggested": bool}}]}}], "hotel_info": {{"name": "名", "address": "所"}}}}
                """
                res = call_groq_safe(prompt)
                try: st.session_state.plans.append(json.loads(res[res.find('{'):res.rfind('}')+1]))
                except: continue
    st.session_state.step = "display"; st.rerun()

# --- STEP 5: 表示 ---
elif st.session_state.step == "display":
    plan_idx_str = st.sidebar.selectbox("プランを切り替える", [f"プラン {i+1}" for i in range(len(st.session_state.plans))])
    idx = int(plan_idx_str.split()[-1]) - 1
    data = st.session_state.plans[idx]
    
    for day in data['days']:
        st.markdown(f'<div class="day-box">{day["label"]}</div>', unsafe_allow_html=True)
        for i, step in enumerate(day['steps']):
            ai_tag = '<span class="ai-badge">AIおすすめ</span>' if step.get('is_ai_suggested') else ""
            st.markdown(f'<div class="time-step">{ai_tag}<small><b>{step["time"]}</b></small><br>{step["content"]}</div>', unsafe_allow_html=True)
            if i < len(day['steps']) - 1:
                st.markdown('<div class="arrow">↓</div>', unsafe_allow_html=True)

    st.markdown("""<div class="advice-box"><b>💡 Aipiaの旅のアドバイス</b><br>
    1. 秘境エリアは急な天候変化が多いため、軽量な雨具の携行を推奨します。<br>
    2. 特急券は「えきねっと」等の事前予約で割引（トクだ値等）が適用されます。<br>
    3. 現地でのタクシー利用は台数が限られるため、前日までの予約が安心です。</div>""", unsafe_allow_html=True)

    if st.button("🏆 このプランで確定し、共有する"): st.session_state.step = "share"; st.rerun()

# --- STEP 6: 共有ページ ---
elif st.session_state.step == "share":
    st.success("プランが確定しました！")
    h_name = st.session_state.plans[0]['hotel_info']['name'] if 'hotel_info' in st.session_state.plans[0] else "選択されたホテル"
    st.markdown(f'<div class="hotel-highlight">最終宿泊先：{h_name}</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<a href="https://line.me/R/msg/text/?Aipia秘境プラン" class="reserve-btn" style="background-color:#06C755; width:100%;" target="_blank">LINEで共有</a>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<a href="https://mail.google.com/mail/?view=cm&fs=1" class="reserve-btn" style="background-color:#EA4335; width:100%;" target="_blank">Gmailで共有</a>', unsafe_allow_html=True)
    
    if st.button("🏠 最初に戻る"): st.session_state.clear(); st.rerun()
