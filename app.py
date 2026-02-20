import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse
import time

# --- 1. 定数・変数定義 ---
PREFECTURES = [""] + ["北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県", "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県", "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県", "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県", "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"]

# --- 2. ページ基本設定 ---
st.set_page_config(layout="wide", page_title="Aipia - AI秘境旅行プラン")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def call_groq_safe(prompt):
    target_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    for model_id in target_models:
        try:
            res = client.chat.completions.create(model=model_id, messages=[{"role": "user", "content": prompt}], temperature=0.7)
            return res.choices[0].message.content
        except Exception as e:
            if any(code in str(e) for code in ["429", "400", "rate_limit"]): continue 
            return None
    return "接続制限中です。数分後にお試しください。"

# CSS (URLボタンのデザイン追加)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    .header-container { text-align: center; padding: 30px 0; border-bottom: 2px solid #D4AF37; background: #FFF; margin-bottom: 30px; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 3.5rem; color: #111; letter-spacing: 5px; margin: 0; }
    .aipia-sub { color: #D4AF37; font-weight: bold; letter-spacing: 3px; font-size: 0.9rem; margin-top: -10px; }
    .plan-box { background: white; padding: 25px; border-left: 5px solid #D4AF37; border-radius: 8px; margin-bottom: 20px; white-space: pre-wrap; line-height: 1.8; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
    .btn-container { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 15px; }
    .official-btn { background-color: #00695C; color: white !important; padding: 6px 14px; border-radius: 4px; text-decoration: none; font-size: 0.8rem; font-weight: bold; }
    .reserve-btn { background-color: #D32F2F; color: white !important; padding: 6px 14px; border-radius: 4px; text-decoration: none; font-size: 0.8rem; font-weight: bold; }
    .line-button { background-color: #06C755; color: white !important; padding: 15px; border-radius: 10px; text-align: center; display: block; text-decoration: none; font-weight: bold; margin-top: 20px; }
    </style>
""", unsafe_allow_html=True)

if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">-AIが創る、秘境への旅行プラン-</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力 ---
if st.session_state.step == "input":
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1: dep_place = st.text_input("🛫 出発地点", value="新宿駅")
    with c2: date_range = st.date_input("📅 旅行日程", value=(datetime.now(), datetime.now() + timedelta(days=1)))
    with c3: dep_time = st.time_input("🕔 出発時刻", value=datetime.strptime("08:00", "%H:%M").time())
    c4, c5 = st.columns(2)
    with c4: pref = st.selectbox("📍 目的地", PREFECTURES)
    with c5: city = st.text_input("🏠 市区町村・詳細")
    c6, c7, c8 = st.columns([1, 2, 1])
    with c6: keyword = st.text_input("🔍 自由入力")
    with c7: purposes = st.multiselect("✨ 目的", ["秘境探索", "美食", "温泉", "歴史"], default=["秘境探索"])
    with c8: budget = st.number_input("💰 予算/人", 5000, 500000, 50000)
    c9, c10 = st.columns(2)
    with c9: adults = st.number_input("大人", 1, 20, 2)
    with c10: kids = st.number_input("小人", 0, 20, 0)

    if st.button("⚜️ 秘境リサーチ開始", use_container_width=True, type="primary"):
        st.session_state.form_data = {"dep": dep_place, "dest": f"{pref}{city}", "days": (date_range[1]-date_range[0]).days+1 if len(date_range)==2 else 1, "start_date": date_range[0]}
        prompt = f"{pref}{city}の秘境・観光スポットを10件。形式：名称|解説|住所"
        content = call_groq_safe(prompt)
        if content:
            st.session_state.found_spots = [l.split('|') for l in content.split('\n') if '|' in l][:10]
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: カタログ (URL付与) ---
elif st.session_state.step == "select_spots":
    st.markdown(f"### 📍 {st.session_state.form_data['dest']} スポット")
    for i, s in enumerate(st.session_state.found_spots):
        with st.container():
            st.markdown(f"#### {s[0]}")
            st.write(s[1])
            # 公式サイト検索リンク
            q = urllib.parse.quote(f"{s[0]} 公式サイト")
            st.markdown(f'<div class="btn-container"><a href="https://www.google.com/search?q={q}" class="official-btn" target="_blank">🔍 公式サイトを検索</a></div>', unsafe_allow_html=True)
            if st.checkbox("旅程に採用", key=f"s_{i}"):
                if s[0] not in st.session_state.selected_spots: st.session_state.selected_spots.append(s[0])
        st.divider()

    c_m1, c_m2 = st.columns(2)
    with c_m1:
        if st.button("➕ More (10個追加)"):
            prompt = f"{st.session_state.form_data['dest']}の別の秘境を10件。形式：名称|解説|住所"
            content = call_groq_safe(prompt)
            if content: st.session_state.found_spots.extend([l.split('|') for l in content.split('\n') if '|' in l][:10]); st.rerun()
    with c_m2:
        if st.button("✅ プランを生成", type="primary"): st.session_state.step = "final_plan"; st.rerun()

# --- STEP 3: プラン表示 (公式サイト・予約サイトURL) ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plans:
        with st.spinner("ホテルとURLを精査中..."):
            for label in ["Plan A", "Plan B"]:
                prompt = f"【重要】{st.session_state.form_data['dest']}の{st.session_state.form_data['days']}日間プラン。1日目に実在の「ホテル名」を必ず入れ、採用スポット{st.session_state.selected_spots}と道順を詳しく。"
                content = call_groq_safe(prompt)
                if content: st.session_state.final_plans[label] = content

    chosen = st.radio("プラン選択", list(st.session_state.final_plans.keys()), horizontal=True)
    
    # 抽出してURLボタンを生成
    plan_text = st.session_state.final_plans[chosen]
    st.markdown(f'<div class="plan-box">{plan_text}</div>', unsafe_allow_html=True)
    
    st.markdown("### 🔗 このプランの予約・詳細確認")
    # 宿泊施設とスポットのURLを生成
    for spot in st.session_state.selected_spots:
        sq = urllib.parse.quote(f"{spot} 公式サイト")
        st.markdown(f'**{spot}**: <a href="https://www.google.com/search?q={sq}" class="official-btn" target="_blank">公式サイト</a>', unsafe_allow_html=True)
    
    # ホテル予約用（AIが生成したテキストから「ホテル」という単語の周辺をリンク化する簡易ボタン）
    st.info("※宿泊予約は各プラン内のホテル名をコピーして下記ボタンから検索してください。")
    hotel_q = urllib.parse.quote(f"{st.session_state.form_data['dest']} ホテル 予約 楽天トラベル")
    jalan_q = urllib.parse.quote(f"{st.session_state.form_data['dest']} ホテル 予約 じゃらん")
    st.markdown(f"""
    <div class="btn-container">
        <a href="https://www.google.com/search?q={hotel_q}" class="reserve-btn" target="_blank">🏨 楽天トラベルで最安予約</a>
        <a href="https://www.google.com/search?q={jalan_q}" class="reserve-btn" target="_blank">🏨 じゃらんで宿泊検索</a>
    </div>
    """, unsafe_allow_html=True)

    line_url = f"https://line.me/R/msg/text/?{urllib.parse.quote('【Aipia 旅行プラン】' + plan_text)}"
    st.markdown(f'<a href="{line_url}" class="line-button" target="_blank">LINEでプランを保存</a>', unsafe_allow_html=True)

    if st.button("🏠 ホームに戻る"): st.session_state.clear(); st.session_state.step = "input"; st.rerun()
