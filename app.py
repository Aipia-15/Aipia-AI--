import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse

# 1. 変数定義（NameErrorを回避）
PREFECTURES = [""] + ["北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県", "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県", "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県", "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県", "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"]

# 2. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
MODEL = "llama-3.3-70b-versatile" 

# デモ画面を再現するCSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&display=swap');
    .stApp { background-color: #F8F9FA; color: #333; font-family: 'Noto Serif JP', serif; }
    .header-container { text-align: center; padding: 40px 0; background: #FFF; border-bottom: 3px solid #00695C; }
    .aipia-logo { font-size: 3rem; font-weight: bold; color: #111; letter-spacing: 4px; margin: 0; }
    .aipia-sub { color: #00695C; font-weight: bold; font-size: 1rem; margin-top: -5px; }
    
    /* タイムラインデザイン */
    .timeline-container { padding: 20px; background: #FFF; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
    .day-label { background: #00695C; color: white; padding: 5px 15px; border-radius: 5px; font-weight: bold; display: inline-block; margin-bottom: 20px; }
    .timeline-item { border-left: 2px solid #00695C; margin-left: 20px; padding-left: 30px; position: relative; padding-bottom: 25px; }
    .timeline-dot { position: absolute; left: -7px; top: 5px; width: 12px; height: 12px; background: #00695C; border-radius: 50%; }
    .time-badge { font-weight: bold; color: #00695C; font-size: 1.1rem; }
    .plan-card { background: #F1F8E9; border-radius: 10px; padding: 15px; border: 1px solid #C8E6C9; margin-top: 5px; }
    
    /* 予算カード */
    .budget-grid { display: flex; gap: 15px; flex-wrap: wrap; margin-top: 20px; justify-content: space-around; }
    .budget-card { background: #FFF; border-radius: 10px; padding: 15px; min-width: 120px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border: 1px solid #00695C; }
    .budget-val { font-weight: bold; font-size: 1.1rem; color: #00695C; display: block; }
    
    .link-btn { background: #00695C; color: white !important; padding: 4px 12px; border-radius: 15px; text-decoration: none; font-size: 0.75rem; font-weight: bold; display: inline-block; margin-top: 10px; }
    .line-footer { background: #06C755; color: white !important; padding: 18px; border-radius: 12px; text-align: center; font-weight: bold; display: block; margin-top: 40px; text-decoration: none; font-size: 1.2rem; }
    </style>
""", unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}
if "edit_mode" not in st.session_state: st.session_state.edit_mode = False

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">- AI Executive Concierge -</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力 ---
if st.session_state.step == "input":
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1: dep = st.text_input("🛫 出発地点", "新宿駅")
    with c2: dates = st.date_input("📅 旅行日程", [datetime.now(), datetime.now() + timedelta(days=1)])
    with c3: dep_time = st.time_input("🕔 出発時刻", datetime.strptime("08:00", "%H:%M").time())
    
    c4, c5 = st.columns(2)
    with c4: pref = st.selectbox("📍 都道府県", PREFECTURES)
    with c5: city = st.text_input("🏠 詳細エリア")
    
    c6, c7, c8 = st.columns([1, 1, 1])
    with c6: adults = st.number_input("大人", 1, 20, 2)
    with c7: kids = st.number_input("小人", 0, 20, 0)
    with c8: budget = st.number_input("予算/人", 5000, 500000, 50000)

    if st.button("⚜️ 秘境スポットを10個リサーチする", use_container_width=True, type="primary"):
        if not pref: st.error("都道府県を選択してください"); st.stop()
        st.session_state.form_data = {"dep": dep, "dest": f"{pref}{city}", "days": 2, "budget": budget}
        with st.spinner("実在する名所を10件厳選中..."):
            prompt = f"{pref}{city}周辺の観光名所を10件挙げよ。形式：名称|詳細説明|予算目安|住所"
            res = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}])
            st.session_state.found_spots = [l.split('|') for l in res.choices[0].message.content.split('\n') if '|' in l][:10]
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: カタログ (10個 & More機能) ---
elif st.session_state.step == "select_spots":
    st.markdown(f"### 📍 {st.session_state.form_data['dest']} 厳選カタログ")
    for i, s in enumerate(st.session_state.found_spots):
        with st.container():
            st.markdown(f"""<div class="plan-card"><b>{s[0]}</b><br><small>{s[3]}</small><p>{s[1]}</p>
            <a class="link-btn" href="https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(s[0]+' '+s[3])}" target="_blank">Google Map</a></div>""", unsafe_allow_html=True)
            if st.checkbox("旅程に採用", key=f"s_{i}"):
                if s[0] not in st.session_state.selected_spots: st.session_state.selected_spots.append(s[0])
    
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        if st.button("➕ More (さらに10個リサーチ)"):
            prompt = f"{st.session_state.form_data['dest']}周辺の、まだ挙げていない観光スポットをさらに10件。形式：名称|詳細説明|予算目安|住所"
            res = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}])
            st.session_state.found_spots.extend([l.split('|') for l in res.choices[0].message.content.split('\n') if '|' in l][:10])
            st.rerun()
    with c_m2:
        if st.button("✅ プラン生成へ進む", type="primary"): st.session_state.step = "final_plan"; st.rerun()

# --- STEP 3: タイムライン・ホテル・予算カード ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plans:
        with st.spinner("ホテル宿泊を含む全日程プランを作成中..."):
            for label in ["Plan A", "Plan B", "Plan C", "Plan D", "Plan E"]:
                prompt = f"{st.session_state.form_data['dest']} 2日間の旅程。宿泊施設(実在するホテル名)を必ず組み込め。形式：日付|時間|予定内容|予算目安"
                res = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}])
                st.session_state.final_plans[label] = [l.split('|') for l in res.choices[0].message.content.split('\n') if '|' in l]

    chosen = st.radio("プラン選択", list(st.session_state.final_plans.keys()), horizontal=True)
    
    st.markdown('<div class="timeline-container">', unsafe_allow_html=True)
    current_day = ""
    for item in st.session_state.final_plans[chosen]:
        if len(item) >= 3:
            if item[0] != current_day:
                current_day = item[0]
                st.markdown(f'<div class="day-label">{current_day}</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="timeline-item"><div class="timeline-dot"></div>
                <span class="time-badge">{item[1]}</span>
                <div class="plan-card">
                    <b>{item[2]}</b><br>
                    <a class="link-btn" href="https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(item[2])}" target="_blank">目的地を見る</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 予算内訳
    st.markdown("### 💰 予算概算")
    st.markdown(f"""
    <div class="budget-grid">
        <div class="budget-card">🚆 交通費<span class="budget-val">¥12,000</span></div>
        <div class="budget-card">🏨 宿泊費<span class="budget-val">¥18,000</span></div>
        <div class="budget-card">🍖 食費<span class="budget-val">¥10,000</span></div>
        <div class="budget-card">🎟️ その他<span class="budget-val">¥5,000</span></div>
    </div>
    <div style="text-align:right; font-size:1.8rem; font-weight:bold; color:#00695C; margin-top:20px;">合計 ¥45,000 / 人</div>
    """, unsafe_allow_html=True)

    # LINE共有
    full_plan_text = f"【Aipia】旅程表 - {chosen}\n" + "\n".join([f"{x[0]} {x[1]} {x[2]}" for x in st.session_state.final_plans[chosen] if len(x)>2])
    line_url = f"https://line.me/R/msg/text/?{urllib.parse.quote(full_plan_text)}"
    st.markdown(f'<a href="{line_url}" target="_blank" class="line-footer">LINEでこのプランを共有する</a>', unsafe_allow_html=True)

    if st.button("🏠 ホームに戻る"): st.session_state.clear(); st.session_state.step = "input"; st.rerun()
