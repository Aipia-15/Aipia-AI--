import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse
import time

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 都道府県と主要市区町村の簡易マッピング（拡張可能）
CITY_MAP = {
    "東京都": ["新宿区", "渋谷区", "奥多摩町", "八丈島", "武蔵野市"],
    "長野県": ["松本市", "長野市", "安曇野市", "軽井沢町", "白馬村", "駒ヶ根市"],
    "北海道": ["札幌市", "函館市", "小樽市", "富良野市", "知床", "美瑛町"],
    "京都府": ["京都市", "宇治市", "宮津市（天橋立）", "舞鶴市", "伊根町"],
    "神奈川県": ["横浜市", "鎌倉市", "箱根町", "藤沢市", "逗子市"],
    "石川県": ["金沢市", "輪島市", "加賀市", "能登町"],
}
# マップにない県のためのデフォルト
DEFAULT_CITIES = ["中心部", "北部エリア", "南部エリア", "隠れた名所エリア"]

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

# ホームへ戻るボタン
if st.session_state.step != "input":
    if st.button("← 条件をやり直す"):
        st.session_state.step = "input"; st.session_state.final_plans = {}; st.rerun()

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">- AIが創る、秘境への旅行プラン -</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力 ---
if st.session_state.step == "input":
    st.markdown('<h3 style="text-align:center;">01. Travel Profile</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        pref = st.selectbox("📍 都道府県", list(CITY_MAP.keys()) + ["その他..."])
        city_options = CITY_MAP.get(pref, DEFAULT_CITIES)
        city = st.selectbox("市町村エリア", city_options)
    with col2:
        keyword = st.text_input("🔍 キーワード検索", placeholder="例：絶景、地酒、古民家、滝")
        purpose = st.multiselect("✨ 旅の目的", ["秘境探索", "美食・地酒", "歴史・文化", "温泉・癒やし", "アクティビティ"], default=["秘境探索"])
    
    col3, col4, col5 = st.columns(3)
    with col3: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now() + timedelta(days=2)))
    with col4: budget = st.selectbox("💰 予算感", ["節約", "標準", "贅沢", "至高"])
    with col5: people = st.number_input("人数", 1, 10, 2)

    if st.button("⚜️ カタログを編纂する", use_container_width=True, type="primary"):
        st.session_state.form_data = {
            "dest": f"{pref}{city}",
            "days": (date_range[1]-date_range[0]).days + 1 if isinstance(date_range, tuple) and len(date_range)==2 else 1,
            "keyword": keyword,
            "purpose": purpose
        }
        with st.spinner("周辺の秘境をリサーチ中..."):
            prompt = f"""
            目的地「{pref}{city}」周辺で、「{keyword}」に関連し、かつ「{purpose}」の目的に合う実在の観光施設を5件、厳格に以下の形式で出力せよ。
            名称|解説|料金|人気度(1-5)|混雑度(1-5)|おすすめ度(★1-5)|周辺秘境|周辺食事処
            """
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
            lines = res.choices[0].message.content.strip().split("\n")
            st.session_state.found_spots = [
                {"name": l.split("|")[0].strip("- "), "desc": l.split("|")[1], "fee": l.split("|")[2], 
                 "pop": l.split("|")[3], "crowd": l.split("|")[4], "star": l.split("|")[5], 
                 "sub_h": l.split("|")[6], "sub_f": l.split("|")[7]} 
                for l in lines if "|" in l and len(l.split("|")) >= 8
            ]
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: カタログ選択 ---
elif st.session_state.step == "select_spots":
    st.markdown(f'<h4 style="text-align:center;">{st.session_state.form_data["dest"]} エグゼクティブ・カタログ</h4>', unsafe_allow_html=True)
    
    for i, spot in enumerate(st.session_state.found_spots):
        st.markdown(f"""
        <div class="catalog-card">
            <div class="catalog-title">{spot['name']}</div>
            <p>{spot['desc']}</p>
            <span class="status-badge">💰 {spot['fee']}</span>
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
            if st.checkbox(f"周辺秘境：{spot['sub_h']}", key=f"h_{i}"):
                if spot['sub_h'] not in st.session_state.selected_spots: st.session_state.selected_spots.append(spot['sub_h'])
        with c3:
            if st.checkbox(f"周辺食事：{spot['sub_f']}", key=f"f_{i}"):
                if spot['sub_f'] not in st.session_state.selected_spots: st.session_state.selected_spots.append(spot['sub_f'])
        st.markdown("---")

    if st.button("🏨 究極の旅程を生成する", use_container_width=True, type="primary"):
        st.session_state.step = "final_plan"; st.rerun()

# --- STEP 3: 最終プラン ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plans:
        with st.spinner("時空を越えたプランを構築中..."):
            for label in ["Plan Alpha", "Plan Beta", "Plan Gamma", "Plan Delta", "Plan Epsilon"]:
                try:
                    p_prompt = f"""
                    一流コンシェルジュとして{st.session_state.form_data['days']}日間の旅程を作成せよ。
                    1. 冒頭に <div class='chuuni-title'>旅のタイトル（厨二病風）</div>
                    2. 各行動は <div class='timeline-item'> で囲む。
                    3. 時間は独立行：<span class='time-range'>09:00 - 10:00</span>
                    4. スポット名は [名称](https://www.google.com/search?q=名称) 形式。
                    採用スポット：{', '.join(st.session_state.selected_spots)}
                    目的：{st.session_state.form_data['purpose']}
                    """
                    res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": p_prompt}])
                    st.session_state.final_plans[label] = res.choices[0].message.content
                    time.sleep(0.5)
                except: continue

    tabs = st.tabs(list(st.session_state.final_plans.keys()))
    for label, tab in zip(st.session_state.final_plans.keys(), tabs):
        with tab: st.markdown(st.session_state.final_plans[label], unsafe_allow_html=True)

st.markdown('<div class="footer" style="text-align:center; padding:50px; color:#999;">&copy; 2026 AIPIA Concierge Services</div>', unsafe_allow_html=True)
