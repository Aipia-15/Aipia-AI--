import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse
import time

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

PREFECTURES = [""] + ["北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県", "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県", "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県", "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県", "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"]

# CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    .header-container { text-align: center; padding: 20px 0; border-bottom: 2px solid #D4AF37; background: #FFF; margin-bottom: 30px; }
    .catalog-card { background: #FFF; border: 1px solid #E0D8C3; border-radius: 12px; padding: 20px; margin-bottom: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
    .status-badge { display: inline-block; padding: 3px 10px; border-radius: 15px; font-size: 0.8rem; margin: 3px; background: #F1ECE4; color: #5D4037; font-weight: bold; }
    .timeline-item { background: #FFF; border-left: 5px solid #D4AF37; padding: 20px; margin-bottom: 15px; }
    .time-range { color: #D4AF37; font-weight: bold; font-size: 1.2rem; display: block; }
    .chuuni-title { font-size: 1.8rem; font-style: italic; color: #111; text-align: center; margin-bottom: 20px; border-bottom: 2px solid #D4AF37; }
    </style>
""", unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}
if "editing_plan" not in st.session_state: st.session_state.editing_plan = ""

st.markdown('<div class="header-container"><p style="font-family:\'Playfair Display\',serif;font-size:3rem;margin:0;">Aipia</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力 ---
if st.session_state.step == "input":
    st.markdown('<h3 style="text-align:center;">Travel Profile</h3>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: dep_place = st.text_input("🛫 出発地点", value="新宿駅")
    with c2: dep_time = st.time_input("🕔 出発時間", value=datetime.strptime("08:00", "%H:%M").time())
    with c3: pref = st.selectbox("📍 目的地（都道府県）", PREFECTURES)

    c4, c5, c6 = st.columns(3)
    with c4: city = st.text_input("🏠 市区町村エリア")
    with c5: keyword = st.text_input("🔍 キーワード")
    with c6: purposes = st.multiselect("✨ 目的", ["秘境探索", "美食", "温泉", "歴史"], default=["秘境探索"])

    c7, c8, c9, c10 = st.columns(4)
    with c7: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now() + timedelta(days=1)))
    with c8: adults = st.number_input("大人", 1, 10, 2)
    with c9: kids = st.number_input("小人", 0, 10, 0)
    with c10: budget = st.number_input("💰 予算/人", 5000, 500000, 50000, step=5000)

    if st.button("⚜️ スポットを検索する", use_container_width=True, type="primary"):
        if not pref: st.error("都道府県を選んでください"); st.stop()
        st.session_state.form_data = {"dep": dep_place, "dep_time": dep_time, "dest": f"{pref}{city}", "days": 2, "budget": budget, "purposes": purposes}
        
        with st.spinner("スポットを厳選中..."):
            prompt = f"{pref}{city}周辺で、{keyword}・{purposes}に合う実在スポットを必ず5件挙げろ。形式：名称|解説|費用|人気|混雑|おすすめ|バリアフリー|駐車場|周辺秘境|周辺食事"
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
            # バグ防止のため空行を除去し確実にパース
            lines = [l.strip() for l in res.choices[0].message.content.split('\n') if '|' in l]
            st.session_state.found_spots = []
            for l in lines:
                p = l.split('|')
                if len(p) >= 10:
                    st.session_state.found_spots.append({"name": p[0], "desc": p[1], "fee": p[2], "pop": p[3], "crowd": p[4], "star": p[5], "bf": p[6], "park": p[7], "sub_h": p[8], "sub_f": p[9]})
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: 選択・確定 ---
elif st.session_state.step == "select_spots":
    st.markdown(f"### 📍 {st.session_state.form_data['dest']} の候補地")
    for i, spot in enumerate(st.session_state.found_spots):
        st.markdown(f"""<div class="catalog-card"><b>{spot['name']}</b><br><small>{spot['desc']}</small><br>
        <span class="status-badge">♿ {spot['bf']}</span><span class="status-badge">🚗 {spot['park']}</span><span class="status-badge">💰 {spot['fee']}</span></div>""", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        if c1.checkbox(f"「{spot['name']}」を採用", key=f"m_{i}"): st.session_state.selected_spots.append(spot['name'])
        if c2.checkbox(f"周辺秘境：{spot['sub_h']}", key=f"h_{i}"): st.session_state.selected_spots.append(spot['sub_h'])
        if c3.checkbox(f"周辺食事：{spot['sub_f']}", key=f"f_{i}"): st.session_state.selected_spots.append(spot['sub_f'])

    if st.button("✅ 旅程を確定して生成する", use_container_width=True, type="primary"):
        st.session_state.step = "final_plan"; st.rerun()

# --- STEP 3: プラン表示・編集・共有 ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plans:
        with st.spinner("詳細な旅程（ホテル・移動込）を作成中..."):
            for label in ["プランA", "プランB"]:
                prompt = f"""出発地{st.session_state.form_data['dep']}を{st.session_state.form_data['dep_time']}に出発する旅程を作れ。
                宿泊（ホテル）を必ず含め、時間は正確に。スポット：{st.session_state.selected_spots}
                形式：<div class='chuuni-title'>題名</div> <div class='timeline-item'><span class='time-range'>時間</span> 内容</div>"""
                res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
                st.session_state.final_plans[label] = res.choices[0].message.content

    tab1, tab2 = st.tabs(["プラン表示", "編集・共有"])
    with tab1:
        chosen = st.radio("プラン選択", list(st.session_state.final_plans.keys()), horizontal=True)
        st.markdown(st.session_state.final_plans[chosen], unsafe_allow_html=True)
        if st.button("🔄 このプランを再生成"): 
            del st.session_state.final_plans[chosen]; st.rerun()
    
    with tab2:
        st.session_state.editing_plan = st.text_area("プランの自由編集", value=st.session_state.final_plans[chosen], height=400)
        if st.button("📋 共有用リンクを発行"):
            share_text = urllib.parse.quote(st.session_state.editing_plan)
            st.success(f"共有用データが生成されました（このURLをコピー）： https://aipia.travel/share?data={share_text[:50]}...")
