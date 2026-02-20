import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse

# --- 1. 定数・変数定義 (NameError回避) ---
PREFECTURES = [""] + ["北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県", "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県", "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県", "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県", "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"]

# --- 2. ページ基本設定 ---
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
MODEL = "llama-3.3-70b-versatile"

# CSS: 最初の高級感を維持しつつ、視認性を向上
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    .header-container { text-align: center; padding: 30px 0; border-bottom: 2px solid #D4AF37; background: #FFF; margin-bottom: 30px; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 3.5rem; color: #111; letter-spacing: 5px; margin: 0; }
    .aipia-sub { color: #D4AF37; font-weight: bold; letter-spacing: 3px; font-size: 0.9rem; margin-top: -10px; }
    .plan-box { background: white; padding: 25px; border-left: 5px solid #D4AF37; border-radius: 8px; margin-bottom: 20px; white-space: pre-wrap; line-height: 1.8; }
    .link-btn { background-color: #00695C; color: white !important; padding: 5px 15px; border-radius: 20px; text-decoration: none; font-size: 0.8rem; }
    .line-button { background-color: #06C755; color: white !important; padding: 15px; border-radius: 10px; text-align: center; display: block; text-decoration: none; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">- AI Executive Concierge -</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力 (初期の全項目を復元) ---
if st.session_state.step == "input":
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1: dep_place = st.text_input("🛫 出発地点", value="新宿駅")
    with c2: date_range = st.date_input("📅 旅行日程", value=(datetime.now(), datetime.now() + timedelta(days=1)))
    with c3: dep_time = st.time_input("🕔 出発時刻", value=datetime.strptime("08:00", "%H:%M").time())

    c4, c5 = st.columns(2)
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
        days = (date_range[1] - date_range[0]).days + 1 if len(date_range) == 2 else 1
        st.session_state.form_data = {"dep": dep_place, "dep_time": dep_time, "dest": f"{pref}{city}", "budget": budget, "days": days, "start_date": date_range[0]}
        
        prompt = f"実在する{pref}{city}周辺のスポットを10件。形式：名称|詳細解説|予算|住所"
        res = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}])
        st.session_state.found_spots = [l.split('|') for l in res.choices[0].message.content.split('\n') if '|' in l][:10]
        st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: カタログ (More機能・10個ずつ追加) ---
elif st.session_state.step == "select_spots":
    st.markdown(f"### 📍 {st.session_state.form_data['dest']} カタログ")
    for i, s in enumerate(st.session_state.found_spots):
        with st.container():
            st.markdown(f"#### {s[0]} <small>({s[3]})</small>", unsafe_allow_html=True)
            st.write(s[1])
            st.markdown(f'<a class="link-btn" href="https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(s[0])}" target="_blank">Google Mapで開く</a>', unsafe_allow_html=True)
            if st.checkbox("採用", key=f"s_{i}"): st.session_state.selected_spots.append(s[0])
        st.divider()

    c_m1, c_m2 = st.columns(2)
    with c_m1:
        if st.button("➕ More (さらに10個リサーチ)"):
            prompt = f"{st.session_state.form_data['dest']}周辺で、別の実在スポットを10件。形式：名称|詳細解説|予算|住所"
            res = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}])
            st.session_state.found_spots.extend([l.split('|') for l in res.choices[0].message.content.split('\n') if '|' in l][:10])
            st.rerun()
    with c_m2:
        if st.button("✅ 5つのプランを生成", type="primary"): st.session_state.step = "final_plan"; st.rerun()

# --- STEP 3: プラン表示 (道順・ホテル・URL・日付) ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plans:
        with st.spinner("道順とホテルを含む詳細プランを5パターン作成中..."):
            for label in ["Plan A", "Plan B", "Plan C", "Plan D", "Plan E"]:
                prompt = f"""
                【重要】{st.session_state.form_data['days']}日間の全日程を作成。
                開始日：{st.session_state.form_data['start_date']}
                出発：{st.session_state.form_data['dep']} {st.session_state.form_data['dep_time']}
                採用スポット：{st.session_state.selected_spots}
                
                条件：
                1. 1日目の夜に、{st.session_state.form_data['dest']}周辺の「実在するホテル名」を必ず宿泊先として明記せよ。
                2. 移動は「〇〇駅〜〇〇線〜〇〇駅」のように路線名や具体的な道順を書け。
                3. 日付（1日目 〇/〇）を必ず見出しに入れ、時間ごとに細かく改行して書け。
                """
                res = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}])
                st.session_state.final_plans[label] = res.choices[0].message.content

    chosen = st.radio("プラン選択", list(st.session_state.final_plans.keys()), horizontal=True)
    st.markdown(f'<div class="plan-box">{st.session_state.final_plans[chosen]}</div>', unsafe_allow_html=True)

    # LINE共有
    line_url = f"https://line.me/R/msg/text/?{urllib.parse.quote('【Aipia】旅行プラン\n' + st.session_state.final_plans[chosen])}"
    st.markdown(f'<a href="{line_url}" class="line-button" target="_blank">LINEで共有する</a>', unsafe_allow_html=True)

    if st.button("🏠 最初に戻る"): st.session_state.clear(); st.session_state.step = "input"; st.rerun()
