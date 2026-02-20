import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse
import re
import time

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 都道府県リスト
PREFECTURES = ["北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県", "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県", "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県", "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県", "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"]

# 2. デザイン (CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    .top-nav { position: absolute; top: 10px; left: 20px; z-index: 999; }
    .header-container { text-align: center; padding: 40px 0; border-bottom: 1px solid #D4AF37; background: #FFF; margin-bottom: 40px; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 3.5rem; color: #111; letter-spacing: 5px; margin: 0; }
    .aipia-sub { letter-spacing: 3px; color: #D4AF37; font-size: 1.0rem; margin-top: 5px; font-weight: bold; }
    
    /* カタログカード */
    .catalog-card { background: #FFF; border: 1px solid #E0D8C3; border-radius: 12px; padding: 25px; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
    .catalog-title { font-size: 1.6rem; font-weight: bold; border-bottom: 2px solid #D4AF37; margin-bottom: 15px; }
    .status-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; margin-right: 10px; margin-bottom: 10px; background: #F1ECE4; color: #5D4037; }
    .sub-spot-box { background: #F9F9F9; border: 1px dashed #D4AF37; padding: 15px; border-radius: 8px; margin-top: 15px; }
    
    .timeline-item { background: #FFF; border-left: 5px solid #D4AF37; padding: 25px; margin-bottom: 20px; border-radius: 0 12px 12px 0; }
    .time-range { color: #D4AF37; font-weight: bold; font-family: 'Playfair Display', serif; font-size: 1.3rem; display: block; margin-bottom: 10px; }
    .chuuni-title { font-size: 1.8rem; font-style: italic; color: #111; text-align: center; margin-bottom: 30px; border-bottom: 2px solid #D4AF37; padding-bottom: 10px; }
    .ai-recommend-box { background-color: #E8F5E9; border-left: 5px solid #2E7D32; padding: 25px; margin: 30px 0; border-radius: 8px; color: #1B5E20; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# セッション
if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}

# ロゴ
st.markdown('<div class="top-nav">', unsafe_allow_html=True)
if st.button("Aipia", key="home_btn"):
    st.session_state.clear()
    st.session_state.step = "input"
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">- AIが創る、秘境への旅行プラン -</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力 ---
if st.session_state.step == "input":
    st.markdown('<h3 style="text-align:center;">01. Travel Profile</h3>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: dep = st.text_input("🛫 出発地", value="新宿駅")
    with c2: dest_pref = st.selectbox("📍 目的地（都道府県）", PREFECTURES, index=12)
    with c3: dest_detail = st.text_input("🏠 市区町村・詳細住所", placeholder="例：松本市安曇")
    
    c4, c5, c6 = st.columns(3)
    with c4: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now() + timedelta(days=2)))
    with c5: adults = st.number_input("大人", 1, 10, 2)
    with c6: kids = st.number_input("子供", 0, 10, 0)
    
    full_dest = f"{dest_pref}{dest_detail}"

    if st.button("⚜️ 秘境カタログを生成する", use_container_width=True, type="primary"):
        st.session_state.form_data = {"dest": full_dest, "days": (date_range[1]-date_range[0]).days + 1 if isinstance(date_range, tuple) and len(date_range)==2 else 1}
        try:
            # 構造化データを生成させる
            prompt = f"""「{full_dest}」周辺の具体的観光施設を5件、以下の形式で出力せよ。
            名称|解説|料金|人気度(1-5)|混雑度(1-5)|おすすめ度(★1-5)|周辺秘境名|周辺食事処
            """
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
            lines = res.choices[0].message.content.strip().split("\n")
            st.session_state.found_spots = []
            for l in lines:
                if "|" in l:
                    p = l.split("|")
                    if len(p) >= 8:
                        st.session_state.found_spots.append({
                            "name": p[0].strip("- "), "desc": p[1], "fee": p[2], "pop": p[3], "crowd": p[4], "star": p[5], "sub_h": p[6], "sub_f": p[7]
                        })
            st.session_state.step = "select_spots"; st.rerun()
        except: st.error("混雑中...")

# --- STEP 2: カタログ選択 ---
elif st.session_state.step == "select_spots":
    st.markdown(f'<h4 style="text-align:center;">{st.session_state.form_data["dest"]} 厳選カタログ</h4>', unsafe_allow_html=True)
    
    for i, spot in enumerate(st.session_state.found_spots):
        with st.container():
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
                if st.checkbox(f"「{spot['name']}」を採用", key=f"main_{i}"):
                    if spot['name'] not in st.session_state.selected_spots: st.session_state.selected_spots.append(spot['name'])
            with c2:
                if st.checkbox(f"周辺秘境：{spot['sub_h']} も行く", key=f"subh_{i}"):
                    if spot['sub_h'] not in st.session_state.selected_spots: st.session_state.selected_spots.append(spot['sub_h'])
            with c3:
                if st.checkbox(f"周辺食事：{spot['sub_f']} も行く", key=f"subf_{i}"):
                    if spot['sub_f'] not in st.session_state.selected_spots: st.session_state.selected_spots.append(spot['sub_f'])
            st.markdown("---")

    if st.button("🏨 選択したスポットでプランを創る", use_container_width=True, type="primary"):
        st.session_state.step = "final_plan"; st.rerun()

# --- STEP 3: 最終プラン ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plans:
        with st.spinner("究極の旅路を編纂中..."):
            for label in ["プランA", "プランB", "プランC", "プランD", "プランE"]:
                try:
                    p_prompt = f"""
                    一流コンシェルジュとして{st.session_state.form_data['days']}日間の旅程を作成せよ。
                    1. 冒頭に <div class='chuuni-title'>旅のタイトル（厨二病風）</div>
                    2. 各行動は <div class='timeline-item'> で囲む。
                    3. 時間表記は独立：<span class='time-range'>09:00 - 10:00</span>
                    4. [名称](https://www.google.com/search?q=名称) 形式。
                    5. 最後に <div class='ai-recommend-box'>AIおすすめ情報</div>
                    採用スポット：{', '.join(st.session_state.selected_spots)}
                    """
                    res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": p_prompt}])
                    st.session_state.final_plans[label] = res.choices[0].message.content
                    time.sleep(1)
                except: continue

    if st.session_state.final_plans:
        tabs = st.tabs(list(st.session_state.final_plans.keys()))
        for label, tab in zip(st.session_state.final_plans.keys(), tabs):
            with tab: st.markdown(st.session_state.final_plans[label], unsafe_allow_html=True)
    else:
        st.error("エラーが発生しました。")
        if st.button("ホームへ"): st.session_state.step = "input"; st.rerun()

st.markdown('<div class="footer">2025-2026 / AIPIA</div>', unsafe_allow_html=True)
