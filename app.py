import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse

# 1. ページ基本設定
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

PREFECTURES = [""] + ["北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県", "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県", "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県", "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県", "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"]

# CSSデザイン (初期の高級感を復元)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    .header-container { text-align: center; padding: 30px 0; border-bottom: 2px solid #D4AF37; background: #FFF; margin-bottom: 30px; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 3.5rem; color: #111; letter-spacing: 5px; margin: 0; }
    .aipia-sub { color: #D4AF37; font-weight: bold; letter-spacing: 3px; font-size: 0.9rem; margin-top: -10px; }
    .spot-card { background: #FFF; border: 1px solid #E0D8C3; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
    .line-button { background-color: #06C755; color: white !important; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; text-align: center; }
    .plan-row { background: white; padding: 15px; border-left: 5px solid #D4AF37; margin-bottom: 10px; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "show_more" not in st.session_state: st.session_state.show_more = False
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}
if "edit_mode" not in st.session_state: st.session_state.edit_mode = False

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">- AI Executive Concierge -</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力 ---
if st.session_state.step == "input":
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1: dep_place = st.text_input("🛫 出発地点", value="新宿駅")
    with c2: date_range = st.date_input("📅 旅行日程", value=(datetime.now(), datetime.now() + timedelta(days=1)))
    with c3: dep_time = st.time_input("🕔 出発時刻", value=datetime.strptime("08:00", "%H:%M").time())

    c4, c5 = st.columns(2) # 都道府県・市区町村 横並び
    with c4: pref = st.selectbox("📍 目的地（都道府県）", PREFECTURES)
    with c5: city = st.text_input("🏠 市区町村・エリア詳細")

    c6, c7, c8 = st.columns([1, 2, 1])
    with c6: keyword = st.text_input("🔍 キーワード")
    with c7: purposes = st.multiselect("✨ 目的", ["秘境探索", "美食", "温泉", "歴史"], default=["秘境探索"])
    with c8: budget = st.number_input("💰 予算/人", 5000, 500000, 50000)

    c9, c10 = st.columns(2)
    with c9: adults = st.number_input("大人 (中学生以上)", 1, 20, 2)
    with c10: kids = st.number_input("小人 (小学生以下)", 0, 20, 0)

    if st.button("⚜️ 10個の厳選スポットをリサーチする", use_container_width=True, type="primary"):
        if not pref: st.error("都道府県を選んでください"); st.stop()
        st.session_state.form_data = {"dep": dep_place, "dep_time": dep_time, "dest": f"{pref}{city}", "budget": budget, "adults": adults, "kids": kids}
        
        with st.spinner("実在する10件のスポットを解析中..."):
            prompt = f"{pref}{city}周辺で、{keyword}に関連する「実在する」スポットを必ず10件、以下の形式で出せ。名称|説明(200字)|予算|バリアフリー|駐車場|実在住所"
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
            lines = [l.strip() for l in res.choices[0].message.content.split('\n') if '|' in l]
            st.session_state.found_spots = [{"name": p[0], "desc": p[1], "fee": p[2], "bf": p[3], "park": p[4], "loc": p[5]} for p in [line.split('|') for line in lines] if len(p) >= 6][:10]
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: スポットカタログ（10件・More機能） ---
elif st.session_state.step == "select_spots":
    st.markdown(f"### 📍 {st.session_state.form_data['dest']} の厳選カタログ")
    
    num_display = 10 if st.session_state.show_more else 5
    for i in range(min(num_display, len(st.session_state.found_spots))):
        spot = st.session_state.found_spots[i]
        with st.container():
            c_img, c_txt = st.columns([1, 3])
            c_img.image(f"https://source.unsplash.com/featured/?{urllib.parse.quote(spot['name'])}", use_column_width=True)
            with c_txt:
                st.markdown(f"#### {spot['name']} <small>(📍{spot['loc']})</small>", unsafe_allow_html=True)
                st.write(spot['desc'])
                st.markdown(f"💰 {spot['fee']} | ♿ {spot['bf']} | 🚗 {spot['park']}")
                if st.checkbox("採用", key=f"s_{i}"): st.session_state.selected_spots.append(spot['name'])
        st.divider()

    if not st.session_state.show_more:
        if st.button("More（さらに5つの候補を表示）"): st.session_state.show_more = True; st.rerun()

    if st.button("✅ 確定して5つのプランを作成", use_container_width=True, type="primary"):
        st.session_state.step = "final_plan"; st.rerun()

# --- STEP 3: 5つのプラン・編集・ホテル・LINE ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plans:
        with st.spinner("ホテル宿泊を含む5つのプランを作成中..."):
            for label in ["Plan A", "Plan B", "Plan C", "Plan D", "Plan E"]:
                prompt = f"{st.session_state.form_data['dep']}発 {st.session_state.form_data['dep_time']}。宿泊(ホテル名)を必ずプラン内に含めろ。採用スポット：{st.session_state.selected_spots}。形式：時間|予定"
                res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
                st.session_state.final_plans[label] = [{"time": l.split('|')[0], "act": l.split('|')[1]} for l in res.choices[0].message.content.split('\n') if '|' in l]

    chosen = st.radio("プラン選択", list(st.session_state.final_plans.keys()), horizontal=True)

    if not st.session_state.edit_mode:
        for item in st.session_state.final_plans[chosen]:
            st.markdown(f'<div class="plan-row"><b>{item["time"]}</b> : {item["act"]}</div>', unsafe_allow_html=True)
        if st.button("✏️ このプランを編集する（時間をずらす・削る）"): st.session_state.edit_mode = True; st.rerun()
    else:
        new_items = []
        for i, item in enumerate(st.session_state.final_plans[chosen]):
            c1, c2, c3 = st.columns([1, 4, 1])
            t = c1.text_input("時間", item['time'], key=f"edit_t_{i}")
            a = c2.text_input("予定", item['act'], key=f"edit_a_{i}")
            if not c3.button("🗑️", key=f"edit_d_{i}"): new_items.append({"time": t, "act": a})
        if st.button("💾 編集を保存"): st.session_state.final_plans[chosen] = new_items; st.session_state.edit_mode = False; st.rerun()

    st.divider()
    # LINE共有 (改行を保持)
    share_txt = f"【Aipia】旅行プラン - {chosen}\n" + "\n".join([f"{x['time']} {x['act']}" for x in st.session_state.final_plans[chosen]])
    st.markdown(f'<a href="https://line.me/R/msg/text/?{urllib.parse.quote(share_txt)}" class="line-button">LINEで共有</a>', unsafe_allow_html=True)

    if st.button("🏠 ホームへ戻る"): st.session_state.clear(); st.session_state.step = "input"; st.rerun()
