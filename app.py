import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse
import json
import re

# --- 1. 基本設定 ---
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

# CSS (余白と視認性の向上)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:wght@700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    .header-container { text-align: center; padding: 20px 0; border-bottom: 2px solid #D4AF37; background: #FFF; margin-bottom: 10px; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 3rem; color: #111; letter-spacing: 5px; margin: 0; }
    .aipia-sub { color: #D4AF37; font-weight: bold; letter-spacing: 2px; font-size: 0.8rem; margin-top: -5px; }
    
    /* スポット間の余白 */
    .spot-card { margin-bottom: 40px; padding: 15px; background: #FFF; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    
    .day-box { background-color: #E8F5E9; padding: 10px 25px; border-radius: 12px; display: inline-block; font-weight: bold; margin: 25px 0 10px 0; color: #2E7D32; border: 1px solid #C8E6C9; }
    .time-step { background-color: #E3F2FD; padding: 18px; border-radius: 8px; margin: 8px 0; border: 1px solid #BBDEFB; line-height: 1.6; }
    .arrow { text-align: center; font-size: 1.5rem; color: #90CAF9; margin: 5px 0; font-weight: bold; }
    .ai-badge { background-color: #FF5252; color: white; font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; float: right; font-weight: bold; }
    .advice-box { background-color: #F1F8E9; padding: 20px; border-radius: 10px; border: 1px solid #C8E6C9; margin: 30px 0; }
    .spot-placeholder { width: 100%; height: 120px; background-color: #C8E6C9; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #2E7D32; font-weight: bold; }
    .reserve-btn { background-color: #D32F2F; color: white !important; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; text-align: center; }
    .confirmed-link { color: #0D47A1; text-decoration: underline; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "plans" not in st.session_state: st.session_state.plans = []
if "confirmed_plan" not in st.session_state: st.session_state.confirmed_plan = None

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">-AIが創る、秘境への旅行プラン-</p></div>', unsafe_allow_html=True)

# --- STEP 1: ホーム画面 ---
if st.session_state.step == "input":
    keyword = st.text_input("🔍 キーワード検索")
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
    
    col7, col8, col9 = st.columns([2, 1, 1])
    with col7: purposes = st.multiselect("✨ 目的", ["秘境探索", "美食", "温泉", "歴史", "絶景"], default=["秘境探索"])
    with col8: adults = st.number_input("大人", 1, 20, 2)
    with col9: kids = st.number_input("小人", 0, 20, 0)

    if st.button("⚜️ 秘境リサーチを開始", use_container_width=True, type="primary"):
        if not pref: st.error("都道府県を選択してください"); st.stop()
        st.session_state.form_data = {"dep": dep_place, "dest": f"{pref}{city}", "speed": walk_speed}
        prompt = f"{pref}{city}周辺で{keyword}に関連する秘境スポットを10件。名称|解説|住所"
        content = call_groq_safe(prompt)
        if content:
            st.session_state.found_spots = [l.split('|') for l in content.strip().split('\n') if '|' in l]
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: スポット選択 (余白調整) ---
elif st.session_state.step == "select_spots":
    st.markdown(f"### 📍 {st.session_state.form_data['dest']} 候補地")
    for i, s in enumerate(st.session_state.found_spots):
        st.markdown(f'<div class="spot-card">', unsafe_allow_html=True)
        col_img, col_txt = st.columns([1, 4])
        with col_img:
            st.markdown(f'<div class="spot-placeholder">{s[0][:10]}</div>', unsafe_allow_html=True)
        with col_txt:
            st.markdown(f"**{s[0]}**")
            st.caption(s[1])
            if st.checkbox("旅程に採用", key=f"s_{i}"):
                if s[0] not in st.session_state.selected_spots: st.session_state.selected_spots.append(s[0])
        st.markdown('</div>', unsafe_allow_html=True)
    
    col_more, col_next = st.columns(2)
    with col_more:
        if st.button("➕ スポットをさらにリサーチ"):
            prompt = f"{st.session_state.form_data['dest']}の別の秘境。名称|解説|住所"
            content = call_groq_safe(prompt)
            if content:
                st.session_state.found_spots.extend([l.split('|') for l in content.split('\n') if '|' in l])
                st.rerun()
    with col_next:
        if st.button("✅ ホテル調査へ", type="primary"): st.session_state.step = "hotel_survey"; st.rerun()

# --- STEP 3: ホテル調査 ---
elif st.session_state.step == "hotel_survey":
    st.markdown("### 🏨 宿泊の希望")
    h_type = st.selectbox("ホテルのタイプ", ["絶景の宿", "老舗旅館", "モダンホテル", "コスパ宿"])
    h_barriers = st.multiselect("バリアフリー（複数選択）", ["段差なし", "車椅子対応", "エレベーター", "手すり"])
    if st.button("✨ 5つの詳細プランを生成", type="primary"):
        st.session_state.hotel_wish = f"{h_type} ({', '.join(h_barriers)})"
        st.session_state.step = "plan_gen"; st.rerun()

# --- STEP 4: プラン生成 (詳細度アップ) ---
elif st.session_state.step == "plan_gen":
    if not st.session_state.plans:
        with st.spinner("移動ルートと時間を計算中..."):
            for _ in range(5):
                prompt = f"""
                2日間の詳細な旅行プランをJSONで。
                出発地：{st.session_state.form_data['dep']} -> 目的地：{st.session_state.form_data['dest']}
                採用：{st.session_state.selected_spots}
                ホテル希望：{st.session_state.hotel_wish}
                ルール：
                1. 各地点の『到着時間 - 出発時間』を必ず記載。
                2. 冒頭に『出発地から目的地への進み方(例:特急やバスの乗り継ぎ)』を詳細に記載。
                3. ホテルの『到着(チェックイン)時間』と翌日の『出発(チェックアウト)時間』を明記。
                JSON：{{"days": [{{"label": "一日目", "steps": [{{"time": "00:00-00:00", "content": "内容", "is_ai_suggested": false}}]}}], "hotel": {{"name": "名", "address": "住所"}}}}
                """
                res = call_groq_safe(prompt)
                try:
                    match = re.search(r"\{.*\}", res, re.DOTALL)
                    if match: st.session_state.plans.append(json.loads(match.group()))
                except: continue
    st.session_state.step = "display"; st.rerun()

# --- STEP 5: 表示・確定 ---
elif st.session_state.step == "display":
    plan_idx = st.sidebar.selectbox("プラン比較", [f"プラン {i+1}" for i in range(len(st.session_state.plans))])
    data = st.session_state.plans[int(plan_idx[-1])-1]
    
    for day in data['days']:
        st.markdown(f'<div class="day-box">{day["label"]}</div>', unsafe_allow_html=True)
        for i, step in enumerate(day['steps']):
            ai_tag = '<span class="ai-badge">AIおすすめ</span>' if step.get('is_ai_suggested') else ""
            st.markdown(f'<div class="time-step">{ai_tag}<small><b>{step["time"]}</b></small><br>{step["content"]}</div>', unsafe_allow_html=True)
            if i < len(day['steps']) - 1: st.markdown('<div class="arrow">↓</div>', unsafe_allow_html=True)
    
    st.markdown(f"### 🏨 宿泊予定：{data['hotel']['name']}")
    if st.button("🏆 このプランで確定する", use_container_width=True, type="primary"):
        st.session_state.confirmed_plan = data; st.session_state.step = "share"; st.rerun()

# --- STEP 6: 確定画面 (URL埋め込み) ---
elif st.session_state.step == "share":
    st.success("🎉 プラン確定！")
    data = st.session_state.confirmed_plan
    
    for day in data['days']:
        st.markdown(f'<div class="day-box">{day["label"]}</div>', unsafe_allow_html=True)
        for i, step in enumerate(day['steps']):
            name = step["content"].split('：')[0].split('(')[0].strip()
            url = f"https://www.google.com/search?q={urllib.parse.quote(name)}"
            link_html = f'<a href="{url}" target="_blank" class="confirmed-link">{name}</a>'
            rest = step["content"].replace(name, "", 1)
            st.info(f"🕒 {step['time']} \n\n {link_html}{rest}")
            if i < len(day['steps']) - 1: st.write("　↓")

    h_name = data['hotel']['name']
    st.markdown(f"### 🏨 宿泊先：<a href='https://www.google.com/search?q={urllib.parse.quote(h_name)}' target='_blank' class='confirmed-link'>{h_name}</a>", unsafe_allow_html=True)
    
    st.markdown("""<div class="advice-box"><b>💡 Aipiaの旅のアドバイス</b><br>
    1. 特急の予約方法：えきねっと等のアプリで事前予約がスムーズです。 2. ホテル到着が遅れる場合は必ず連絡を。</div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1: st.markdown(f'<a href="https://line.me/R/msg/text/?確定プラン：{h_name}泊" class="reserve-btn" style="background-color:#06C755; width:100%;" target="_blank">LINE共有</a>', unsafe_allow_html=True)
    with c2: st.markdown(f'<a href="https://mail.google.com/mail/?view=cm&fs=1" class="reserve-btn" style="background-color:#EA4335; width:100%;" target="_blank">Gmail共有</a>', unsafe_allow_html=True)
    
    if st.button("🏠 最初に戻る"): st.session_state.clear(); st.rerun()
