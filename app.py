import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse
import json
import re

# --- 1. 基本設定 ---
st.set_page_config(layout="wide", page_title="Aipia - AI旅行編集コンシェルジュ")
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

# CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:wght@700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    .header-container { text-align: center; padding: 20px 0; border-bottom: 2px solid #D4AF37; background: #FFF; margin-bottom: 10px; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 3rem; color: #111; letter-spacing: 5px; margin: 0; }
    .aipia-sub { color: #D4AF37; font-weight: bold; letter-spacing: 2px; font-size: 0.8rem; margin-top: -5px; }
    .spot-card { margin-bottom: 40px; padding: 15px; background: #FFF; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .day-box { background-color: #E8F5E9; padding: 10px 25px; border-radius: 12px; display: inline-block; font-weight: bold; margin: 25px 0 10px 0; color: #2E7D32; border: 1px solid #C8E6C9; }
    .time-step { background-color: #E3F2FD; padding: 18px; border-radius: 8px; margin: 8px 0; border: 1px solid #BBDEFB; }
    .arrow { text-align: center; font-size: 1.5rem; color: #90CAF9; margin: 5px 0; font-weight: bold; }
    .ai-badge { background-color: #FF5252; color: white; font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; float: right; font-weight: bold; }
    .advice-box { background-color: #F1F8E9; padding: 20px; border-radius: 10px; border: 1px solid #C8E6C9; margin: 30px 0; }
    .spot-placeholder { width: 100%; height: 120px; background-color: #C8E6C9; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #2E7D32; font-weight: bold; }
    .reserve-btn { background-color: #D32F2F; color: white !important; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; text-align: center; border: none; cursor: pointer; }
    .edit-container { background: #FFF; border: 1px dashed #D4AF37; padding: 20px; border-radius: 15px; margin: 20px 0; }
    </style>
""", unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "plans" not in st.session_state: st.session_state.plans = []
if "editing_plan" not in st.session_state: st.session_state.editing_plan = None

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">-AIが創る、秘境への旅行プラン-</p></div>', unsafe_allow_html=True)

# --- STEP 1 & 2 & 3 (省略せずロジック維持) ---
if st.session_state.step == "input":
    keyword = st.text_input("🔍 キーワード検索")
    st.write("---")
    walk_speed = st.select_slider("🚶‍♂️ 歩く速度", options=["ゆっくり", "普通", "早歩き"], value="普通")
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1: dep_place = st.text_input("🛫 出発地点", value="新宿駅")
    with c2: date_range = st.date_input("📅 旅行日程", value=(datetime.now(), datetime.now() + timedelta(days=1)))
    with c3: dep_time = st.time_input("🕔 出発時刻", value=datetime.strptime("08:00", "%H:%M").time())
    c4, c5, c6 = st.columns([2, 2, 2])
    with c4: pref = st.selectbox("📍 都道府県", PREFECTURES)
    with c5: city = st.text_input("🏠 詳細エリア")
    with c6: budget = st.number_input("💰 予算/人", 5000, 500000, 50000)
    if st.button("⚜️ 秘境リサーチを開始", use_container_width=True, type="primary"):
        st.session_state.form_data = {"dep": dep_place, "dest": f"{pref}{city}", "speed": walk_speed}
        prompt = f"{pref}{city}周辺の秘境スポットを10件。名称|解説|住所"
        content = call_groq_safe(prompt); st.session_state.found_spots = [l.split('|') for l in content.split('\n') if '|' in l]
        st.session_state.step = "select_spots"; st.rerun()

elif st.session_state.step == "select_spots":
    st.markdown(f"### 📍 {st.session_state.form_data['dest']} 候補")
    for i, s in enumerate(st.session_state.found_spots):
        st.markdown('<div class="spot-card">', unsafe_allow_html=True)
        col_img, col_txt = st.columns([1, 4])
        with col_img: st.markdown(f'<div class="spot-placeholder">{s[0][:10]}</div>', unsafe_allow_html=True)
        with col_txt:
            st.markdown(f"**{s[0]}**")
            if st.checkbox("採用", key=f"s_{i}"):
                if s[0] not in st.session_state.selected_spots: st.session_state.selected_spots.append(s[0])
        st.markdown('</div>', unsafe_allow_html=True)
    if st.button("✅ プラン生成へ進む", type="primary"): st.session_state.step = "plan_gen"; st.rerun()

# --- STEP 4: プラン生成 & 表示 ---
elif st.session_state.step == "plan_gen":
    if not st.session_state.plans:
        with st.spinner("プランを構築中..."):
            for _ in range(5):
                prompt = f"{st.session_state.form_data['dep']}発、{st.session_state.selected_spots}を含む2日間の旅程をJSONで作成せよ。各所に『到着-出発時間』を明記。"
                res = call_groq_safe(prompt)
                try: 
                    match = re.search(r"\{.*\}", res, re.DOTALL)
                    if match: st.session_state.plans.append(json.loads(match.group()))
                except: continue
    
    plan_idx = st.sidebar.selectbox("プラン切替", [f"プラン {i+1}" for i in range(len(st.session_state.plans))])
    current_data = st.session_state.plans[int(plan_idx[-1])-1]

    # --- 編集モード ---
    if st.toggle("🛠️ プランを自由編集する（並び替え・時間変更）"):
        st.markdown('<div class="edit-container">', unsafe_allow_html=True)
        st.subheader("編集パネル")
        edited_steps = []
        for d_idx, day in enumerate(current_data['days']):
            st.write(f"📅 {day['label']}")
            for s_idx, step in enumerate(day['steps']):
                c_edit1, c_edit2, c_edit3 = st.columns([1, 2, 1])
                with c_edit1: new_time = st.text_input(f"時間", value=step['time'], key=f"t_{d_idx}_{s_idx}")
                with c_edit2: new_content = st.text_input(f"内容", value=step['content'], key=f"c_{d_idx}_{s_idx}")
                with c_edit3: order = st.number_input("順序", 0, 20, s_idx, key=f"o_{d_idx}_{s_idx}")
                edited_steps.append({"day": d_idx, "time": new_time, "content": new_content, "order": order})
        
        if st.button("🔄 編集内容で再生成（清書）"):
            # 順序でソート
            edited_steps.sort(key=lambda x: x['order'])
            # セッションに反映
            new_days = current_data['days'].copy()
            for d in range(len(new_days)):
                new_days[d]['steps'] = [e for e in edited_steps if e['day'] == d]
            current_data['days'] = new_days
            st.success("再生成しました！下の確定ボタンで保存できます。")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- 通常表示 ---
    for day in current_data['days']:
        st.markdown(f'<div class="day-box">{day["label"]}</div>', unsafe_allow_html=True)
        for i, step in enumerate(day['steps']):
            st.markdown(f'<div class="time-step"><small><b>{step["time"]}</b></small><br>{step["content"]}</div>', unsafe_allow_html=True)
            if i < len(day['steps']) - 1: st.markdown('<div class="arrow">↓</div>', unsafe_allow_html=True)
    
    if st.button("🏆 この内容で確定する", use_container_width=True, type="primary"):
        st.session_state.confirmed_plan = current_data
        st.session_state.step = "share"; st.rerun()

# --- STEP 5: 共有 ---
elif st.session_state.step == "share":
    st.success("🎉 プラン確定！")
    data = st.session_state.confirmed_plan
    for day in data['days']:
        st.markdown(f'### {day["label"]}')
        for step in day['steps']:
            name = step["content"].split('：')[0].strip()
            url = f"https://www.google.com/search?q={urllib.parse.quote(name)}"
            st.info(f"🕒 {step['time']} \n\n <a href='{url}' target='_blank' style='font-weight:bold; color:#0D47A1;'>{name}</a>", unsafe_allow_html=True)

    st.markdown("""<div class="advice-box"><b>💡 Aipiaの旅のアドバイス</b><br>
    編集した時間は移動時間に余裕がありますか？えきねっと等の予約も忘れずに。</div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1: st.markdown(f'<a href="https://line.me/R/msg/text/?確定プラン共有" class="reserve-btn" style="background-color:#06C755; width:100%;">LINE共有</a>', unsafe_allow_html=True)
    with c2: st.markdown(f'<a href="https://mail.google.com/mail/?view=cm&fs=1" class="reserve-btn" style="background-color:#EA4335; width:100%;">Gmail共有</a>', unsafe_allow_html=True)
    if st.button("🏠 最初に戻る"): st.session_state.clear(); st.rerun()
