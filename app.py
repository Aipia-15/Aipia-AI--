import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse
import time

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 47都道府県リスト
PREFECTURES = [
    "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
    "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
    "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県",
    "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県",
    "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県",
    "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県",
    "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"
]

# 2. デザイン (CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    .header-container { text-align: center; padding: 40px 0; border-bottom: 1px solid #D4AF37; background: #FFF; margin-bottom: 40px; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 3.5rem; color: #111; letter-spacing: 5px; margin: 0; }
    .aipia-sub { letter-spacing: 3px; color: #D4AF37; font-size: 1.0rem; margin-top: 5px; font-weight: bold; }
    .catalog-card { background: #FFF; border: 1px solid #E0D8C3; border-radius: 12px; padding: 25px; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
    .catalog-title { font-size: 1.6rem; font-weight: bold; color: #111; border-bottom: 2px solid #D4AF37; margin-bottom: 15px; }
    .status-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; margin-right: 10px; margin-bottom: 10px; background: #F1ECE4; color: #5D4037; font-weight: bold; }
    .timeline-item { background: #FFF; border-left: 5px solid #D4AF37; padding: 25px; margin-bottom: 20px; border-radius: 0 12px 12px 0; }
    .time-range { color: #D4AF37; font-weight: bold; font-family: 'Playfair Display', serif; font-size: 1.3rem; display: block; margin-bottom: 10px; }
    .chuuni-title { font-size: 1.8rem; font-style: italic; color: #111; text-align: center; margin-bottom: 30px; border-bottom: 2px solid #D4AF37; padding-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}
if "city_list" not in st.session_state: st.session_state.city_list = []

# ロゴ
if st.session_state.step != "input":
    if st.button("← 検索をやり直す"):
        st.session_state.clear()
        st.session_state.step = "input"; st.rerun()

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">- AIが創る、日本全国の秘境旅 -</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力 (全県・全市町村対応) ---
if st.session_state.step == "input":
    st.markdown('<h3 style="text-align:center;">01. Travel Profile</h3>', unsafe_allow_html=True)
    
    # 1段目：移動の基本情報
    c1, c2, c3 = st.columns(3)
    with c1:
        dep = st.text_input("🛫 出発地", value="新宿駅")
    with c2:
        # 47都道府県すべてを選択可能
        pref = st.selectbox("📍 目的地（都道府県）", PREFECTURES, index=12) # 初期値:東京都
    with c3:
        # AIを使ってその都道府県の主要な市区町村リストを動的に生成（または自由入力）
        city = st.text_input("🏠 市区町村・エリア", placeholder="例：松本市、奥多摩町、京都市東山区など")

    # 2段目：キーワードと目的タグ
    c4, c5 = st.columns([1, 2])
    with c4:
        keyword = st.text_input("🔍 自由キーワード", placeholder="例：絶景、地酒、古民家")
    with c5:
        purposes = st.multiselect("✨ 旅の目的（タグ）", 
                                ["秘境探索", "美食・地酒", "歴史・重要文化財", "温泉・癒やし", "現代アート", "アウトドア", "家族旅行"], 
                                default=["秘境探索"])

    # 3段目：日程・人数・予算
    c6, c7, c8, c9 = st.columns([1.5, 1, 1, 1.5])
    with c6:
        date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now() + timedelta(days=2)))
    with c7:
        adults = st.number_input("大人", 1, 20, 2)
    with c8:
        kids = st.number_input("小人", 0, 20, 0)
    with c9:
        budget_amount = st.number_input("💰 予算総額 (1人あたり/円)", min_value=5000, step=5000, value=50000)

    if st.button("⚜️ 日本全国から秘境をリサーチする", use_container_width=True, type="primary"):
        st.session_state.form_data = {
            "dep": dep,
            "dest": f"{pref}{city}",
            "days": (date_range[1]-date_range[0]).days + 1 if isinstance(date_range, tuple) and len(date_range)==2 else 1,
            "keyword": keyword,
            "purposes": purposes,
            "people": f"大人{adults}名、小人{kids}名",
            "budget": f"{budget_amount}円"
        }
        with st.spinner(f"{pref}{city} の情報を精査中..."):
            prompt = f"""
            出発地「{dep}」、目的地「{pref}{city}」周辺で、「{keyword}」に関連し、目的「{purposes}」に完璧に合致する実在の施設を5件厳選せよ。
            予算「{budget_amount}円」、人数「大人{adults}名、小人{kids}名」に最適な提案を行え。
            出力形式を死守せよ：名称|解説|推定費用|人気度(1-5)|混雑度(1-5)|おすすめ度(★1-5)|周辺の秘境|周辺の食事処
            """
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
            lines = res.choices[0].message.content.strip().split("\n")
            st.session_state.found_spots = []
            for l in lines:
                if "|" in l and len(l.split("|")) >= 8:
                    p = l.split("|")
                    st.session_state.found_spots.append({
                        "name": p[0].strip("- "), "desc": p[1], "fee": p[2], 
                        "pop": p[3], "crowd": p[4], "star": p[5], 
                        "sub_h": p[6], "sub_f": p[7]
                    })
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: カタログ選択 ---
elif st.session_state.step == "select_spots":
    st.markdown(f'<h4 style="text-align:center;">{st.session_state.form_data["dest"]} 究極カタログ</h4>', unsafe_allow_html=True)
    
    for i, spot in enumerate(st.session_state.found_spots):
        st.markdown(f"""
        <div class="catalog-card">
            <div class="catalog-title">{spot['name']}</div>
            <p>{spot['desc']}</p>
            <span class="status-badge">💰 予算目安：{spot['fee']}</span>
            <span class="status-badge">🔥 人気: {spot['pop']}/5</span>
            <span class="status-badge">👥 混雑: {spot['crowd']}/5</span>
            <span class="status-badge">✨ おすすめ: {spot['star']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.checkbox(f"「{spot['name']}」を採用", key=f"m_{i}"):
                if spot['name'] not in st.session_state.selected_spots: st.session_state.selected_spots.append(spot['name'])
        with c2:
            if st.checkbox(f"周辺秘境：{spot['sub_h']} を追加", key=f"h_{i}"):
                if spot['sub_h'] not in st.session_state.selected_spots: st.session_state.selected_spots.append(spot['sub_h'])
        with c3:
            if st.checkbox(f"周辺食事：{spot['sub_f']} を追加", key=f"f_{i}"):
                if spot['sub_f'] not in st.session_state.selected_spots: st.session_state.selected_spots.append(spot['sub_f'])
        st.markdown("---")

    if st.button("🏨 選択した全スポットで旅程を編纂する", use_container_width=True, type="primary"):
        st.session_state.step = "final_plan"; st.rerun()

# --- STEP 3: 最終プラン ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plans:
        with st.spinner("日本全国のデータを元に、旅程を構築中..."):
            for label in ["Plan A", "Plan B", "Plan C", "Plan D", "Plan E"]:
                try:
                    p_prompt = f"""
                    一流コンシェルジュとして{st.session_state.form_data['days']}日間の旅程を作成せよ。
                    出発地：{st.session_state.form_data['dep']} / 目的地：{st.session_state.form_data['dest']}
                    予算：1人あたり{st.session_state.form_data['budget']} / 構成：{st.session_state.form_data['people']}
                    1. 冒頭に <div class='chuuni-title'>旅のタイトル（厨二病風）</div>
                    2. 各行動は <div class='timeline-item'> で囲む。
                    3. 時間は独立行：<span class='time-range'>09:00 - 10:00</span>
                    4. スポット名は [名称](https://www.google.com/search?q=名称) 形式。
                    採用スポット：{', '.join(st.session_state.selected_spots)}
                    """
                    res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": p_prompt}])
                    st.session_state.final_plans[label] = res.choices[0].message.content
                    time.sleep(0.5)
                except: continue

    tabs = st.tabs(list(st.session_state.final_plans.keys()))
    for label, tab in zip(st.session_state.final_plans.keys(), tabs):
        with tab: st.markdown(st.session_state.final_plans[label], unsafe_allow_html=True)

st.markdown('<div class="footer" style="text-align:center; padding:50px; color:#999;">&copy; 2026 AIPIA - All Japan Secrets</div>', unsafe_allow_html=True)
