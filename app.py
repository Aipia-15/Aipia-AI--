import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse
import time

# 1. ページ基本設定
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

PREFECTURES = [""] + ["北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県", "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県", "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県", "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県", "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"]

# CSSデザイン
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&display=swap');
    .stApp { background-color: #FBF9F7; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    .header-container { text-align: center; padding: 25px 0; border-bottom: 2px solid #D4AF37; background: #FFF; margin-bottom: 30px; }
    .spot-card { background: #FFF; border: 1px solid #E0D8C3; border-radius: 15px; padding: 20px; margin-bottom: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); }
    .status-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; margin: 3px; background: #F3EEE7; color: #5D4037; font-weight: bold; border: 1px solid #D4AF37; }
    .line-button { background-color: #06C755; color: white !important; padding: 10px 20px; border-radius: 5px; text-decoration: none; font-weight: bold; display: inline-block; }
    </style>
""", unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}
if "edit_mode" not in st.session_state: st.session_state.edit_mode = False

st.markdown('<div class="header-container"><h1 style="letter-spacing:10px; font-family:serif;">Aipia</h1><p style="color:#D4AF37;">- 日本全国、至高の秘境旅をあなたに -</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力 (ホーム画面レイアウト) ---
if st.session_state.step == "input":
    st.markdown('<h3 style="text-align:center;">Travel Profile</h3>', unsafe_allow_html=True)
    
    r1_c1, r1_c2, r1_c3 = st.columns([2, 2, 1])
    with r1_c1: dep_place = st.text_input("🛫 出発地点", value="新宿駅")
    with r1_c2: date_range = st.date_input("📅 旅行日程", value=(datetime.now(), datetime.now() + timedelta(days=1)))
    with r1_c3: dep_time = st.time_input("🕔 出発時刻", value=datetime.strptime("08:00", "%H:%M").time())

    r2_c1, r2_c2 = st.columns(2)
    with r2_c1: pref = st.selectbox("📍 目的地（都道府県）", PREFECTURES)
    with r2_c2: city = st.text_input("🏠 市区町村・エリア詳細")

    r3_c1, r3_c2, r3_c3 = st.columns([1, 2, 1])
    with r3_c1: keyword = st.text_input("🔍 キーワード", placeholder="例：絶景, 古民家")
    with r3_c2: purposes = st.multiselect("✨ 旅の目的", ["秘境探索", "美食・地酒", "歴史・重要文化財", "温泉・癒やし", "現代アート"], default=["秘境探索"])
    with r3_c3: budget = st.number_input("💰 予算/人(円)", 5000, 500000, 50000, step=5000)

    if st.button("⚜️ 10個の秘境スポットを呼び出す", use_container_width=True, type="primary"):
        if not pref: st.error("都道府県を選択してください"); st.stop()
        st.session_state.form_data = {"dep": dep_place, "dep_time": dep_time, "dest": f"{pref}{city}", "budget": budget, "days": 2}
        
        with st.spinner("実在する名所をリサーチ中..."):
            prompt = f"{pref}{city}周辺で、{keyword}に関連する「実在する」スポットを必ず10件挙げよ。架空の場所は厳禁。形式：名称|詳細な魅力説明(150字以上)|費用目安|バリアフリー情報|駐車場の有無|実在する所在地詳細"
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
            lines = [l.strip() for l in res.choices[0].message.content.split('\n') if '|' in l]
            st.session_state.found_spots = []
            for l in lines[:10]:
                p = l.split('|')
                if len(p) >= 6:
                    st.session_state.found_spots.append({"name": p[0], "desc": p[1], "fee": p[2], "bf": p[3], "park": p[4], "loc": p[5]})
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: スポットカタログ (10選表示) ---
elif st.session_state.step == "select_spots":
    st.markdown(f"### 📍 {st.session_state.form_data['dest']} の厳選スポット（10選）")
    
    for i, spot in enumerate(st.session_state.found_spots):
        with st.container():
            col_img, col_txt = st.columns([1, 2.5])
            with col_img:
                st.image(f"https://source.unsplash.com/featured/?{urllib.parse.quote(spot['name'])}", caption=spot['name'], use_column_width=True)
            with col_txt:
                st.markdown(f"#### {spot['name']}")
                st.caption(f"📍 所在地：{spot['loc']}")
                st.write(spot['desc'])
                st.markdown(f'<span class="status-badge">💰 {spot["fee"]}</span><span class="status-badge">♿ {spot["bf"]}</span><span class="status-badge">🚗 {spot["park"]}</span>', unsafe_allow_html=True)
                if st.checkbox("このスポットを採用", key=f"sel_{i}"):
                    if spot['name'] not in st.session_state.selected_spots: st.session_state.selected_spots.append(spot['name'])
        st.divider()

    if st.button("✅ 確定して5つのプランを生成", use_container_width=True, type="primary"):
        st.session_state.step = "final_plan"; st.rerun()

# --- STEP 3: 5つのプラン・編集・LINE共有 ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plans:
        with st.spinner("ホテル宿泊を含む5つの極上プランを作成中..."):
            for label in ["Plan A", "Plan B", "Plan C", "Plan D", "Plan E"]:
                prompt = f"{st.session_state.form_data['dep']}発、{st.session_state.form_data['dep_time']}開始。{st.session_state.form_data['dest']}周辺のホテル・旅館への宿泊を必ず含めろ。採用スポット：{st.session_state.selected_spots}。形式：時間|行動"
                res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
                st.session_state.final_plans[label] = [{"time": l.split('|')[0].strip(), "act": l.split('|')[1].strip()} for l in res.choices[0].message.content.split('\n') if '|' in l]

    st.markdown("### 🗓️ 旅のしおり - 5つの提案")
    chosen = st.radio("プランを切り替えて比較してください", list(st.session_state.final_plans.keys()), horizontal=True)

    if not st.session_state.edit_mode:
        st.markdown(f'<div style="background:#FFF; padding:30px; border-radius:15px; border:1px solid #D4AF37;"><h3>{chosen}</h3>', unsafe_allow_html=True)
        for item in st.session_state.final_plans[chosen]:
            st.markdown(f"**{item['time']}** : {item['act']}")
        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("✏️ このプランを自分好みに編集する"):
            st.session_state.edit_mode = True; st.rerun()
    else:
        st.markdown("#### 🛠️ 自由編集モード")
        new_plan = []
        for i, item in enumerate(st.session_state.final_plans[chosen]):
            c1, c2, c3 = st.columns([1, 4, 1])
            t = c1.text_input("時間", item['time'], key=f"t_{chosen}_{i}")
            a = c2.text_input("予定", item['act'], key=f"a_{chosen}_{i}")
            if not c3.button("🗑️", key=f"d_{chosen}_{i}"): new_plan.append({"time": t, "act": a})
        if st.button("💾 編集を完了して保存"):
            st.session_state.final_plans[chosen] = new_plan
            st.session_state.edit_mode = False; st.rerun()

    st.divider()
    # LINE共有機能
    share_text = f"【Aipia 旅行プラン】\n" + "\n".join([f"{x['time']} {x['act']}" for x in st.session_state.final_plans[chosen]])
    line_url = f"https://line.me/R/msg/text/?{urllib.parse.quote(share_text)}"
    st.markdown(f'<a href="{line_url}" class="line-button">LINEで旅程を共有する</a>', unsafe_allow_html=True)
    
    if st.button("🏠 最初に戻る"):
        st.session_state.clear(); st.session_state.step = "input"; st.rerun()
