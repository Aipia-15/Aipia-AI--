import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import json
import re
import urllib.parse

# --- 1. 基本設定 ---
st.set_page_config(layout="wide", page_title="Aipia")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def call_groq_safe(prompt):
    # 軽量モデルを優先的に使用して速度と安定性を確保
    for model_id in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]:
        try:
            res = client.chat.completions.create(model=model_id, messages=[{"role": "user", "content": prompt}], temperature=0.6)
            if res.choices[0].message.content: return res.choices[0].message.content
        except: continue
    return None

def parse_json_safely(text):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match: return None
        # 特殊文字や改行によるパースエラーを防ぐ
        clean_json = match.group().replace('\n', ' ').replace('\r', '')
        return json.loads(clean_json)
    except: return None

# --- 2. セッション状態の初期化 ---
keys = ["step", "found_spots", "selected_spots", "plans", "confirmed", "more_count", "form_data", "hotel_data"]
for k in keys:
    if k not in st.session_state:
        if k == "step": st.session_state[k] = "input"
        elif k in ["found_spots", "selected_spots", "plans"]: st.session_state[k] = []
        else: st.session_state[k] = None

# --- 3. デザイン定義 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:wght@700&display=swap');
    .stApp { background-color: #F8F6F4; font-family: 'Noto Serif JP', serif; }
    .header-container { text-align: center; padding: 30px 0; border-bottom: 2px solid #D4AF37; background: #FFF; margin-bottom: 20px; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 3rem; color: #111; letter-spacing: 4px; margin: 0; }
    .aipia-sub { color: #D4AF37; font-weight: bold; font-size: 0.9rem; margin-top: -5px; }
    .spot-card { background: white; padding: 15px; border-radius: 10px; border-left: 5px solid #D4AF37; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .time-step { background-color: #E3F2FD; padding: 15px; border-radius: 10px; margin: 10px 0; border: 1px solid #BBDEFB; position: relative; }
    .aipia-badge { position: absolute; top: -10px; right: -10px; background: #FFD700; color: #000; padding: 3px 12px; border-radius: 15px; font-size: 0.75rem; font-weight: bold; border: 1px solid #FFF; }
    .advice-card { background-color: #FFF3E0; border-left: 4px solid #FF9800; padding: 10px; border-radius: 4px; font-size: 0.85rem; }
    .reserve-btn { display: inline-block; padding: 8px 16px; margin: 4px; border-radius: 4px; color: white !important; text-decoration: none; font-weight: bold; font-size: 0.8rem; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">-AIが創る、秘境への旅行プラン-</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力 ---
if st.session_state.step == "input":
    with st.container():
        keyword = st.text_input("🔍 キーワード", placeholder="例：秘境の滝、地元の食事")
        col_t, col_s = st.columns([1, 1])
        with col_t: transport = st.radio("🚃 交通", ["公共交通", "車"], horizontal=True)
        with col_s: speed = st.select_slider("🚶‍♂️ 速度", options=["ゆっくり", "普通", "早歩き"], value="普通")
        
        col1, col2, col3 = st.columns(3)
        with col1: dep_place = st.text_input("🛫 出発地", value="新宿駅")
        with col2: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now() + timedelta(days=1)))
        with col3: pref = st.selectbox("📍 都道府県", ["東京都", "神奈川県", "長野県", "静岡県", "山梨県", "北海道", "京都府", "大阪府"]) # 短縮リスト
        
        if st.button("⚜️ 秘境リサーチ開始", use_container_width=True, type="primary"):
            st.session_state.form_data = {"dep": dep_place, "dest": pref, "transport": transport, "speed": speed}
            prompt = f"{pref}周辺で{keyword}に関連する実在観光スポット10件。名称|解説|URL 形式で。URLは必ず含めて。"
            res = call_groq_safe(prompt)
            if res:
                st.session_state.found_spots = [l.split('|') for l in res.strip().split('\n') if '|' in l]
                st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: スポット選択 ---
elif st.session_state.step == "select_spots":
    st.subheader(f"📍 {st.session_state.form_data['dest']} の候補")
    for i, s in enumerate(st.session_state.found_spots):
        if len(s) < 2: continue
        st.markdown(f'<div class="spot-card"><b>{s[0]}</b><br><small>{s[1]}</small></div>', unsafe_allow_html=True)
        if st.checkbox("採用", key=f"c_{i}"):
            if s[0] not in st.session_state.selected_spots: st.session_state.selected_spots.append(s[0])
    
    col_more, col_next = st.columns(2)
    with col_more:
        if st.button("➕ もっと見る"):
            # 差分だけをリクエストして軽量化
            res = call_groq_safe(f"{st.session_state.form_data['dest']}で別のスポットを5件。名称|解説|URL")
            if res:
                st.session_state.found_spots.extend([l.split('|') for l in res.strip().split('\n') if '|' in l])
                st.rerun()
    with col_next:
        if st.button("✅ 次へ", type="primary"): st.session_state.step = "hotel"; st.rerun()

# --- STEP 3: ホテル ---
elif st.session_state.step == "hotel":
    h_style = st.selectbox("宿泊スタイル", ["絶景旅館", "老舗宿", "モダンホテル"])
    if st.button("✨ 5つのプランを生成", type="primary"):
        st.session_state.hotel_data = {"style": h_style}
        st.session_state.step = "plan_gen"; st.rerun()

# --- STEP 4: プラン表示 ---
elif st.session_state.step == "plan_gen":
    if not st.session_state.plans:
        with st.spinner("プラン生成中..."):
            for _ in range(5):
                # 構造をシンプルにしてパースエラーを防止
                prompt = f"""
                出発:{st.session_state.form_data['dep']}, スポット:{st.session_state.selected_spots}, 宿泊:{st.session_state.hotel_data['style']}
                JSON形式で:
                {{'route': '経路', 'advices': ['A1', 'A2', 'A3'], 'hotel': '実在名', 'days': [{{'label': '1日目', 'steps': [{{'arrival': '10:00', 'departure': '11:00', 'content': '内容', 'is_rec': false}}]}}]}}
                ※食事処を1つ追加し is_rec: true に。
                """
                res = call_groq_safe(prompt)
                parsed = parse_json_safely(res)
                if parsed: st.session_state.plans.append(parsed)
    
    if st.session_state.plans:
        p_idx = st.sidebar.radio("プラン選択", range(len(st.session_state.plans)), format_func=lambda x: f"案 {x+1}")
        data = st.session_state.plans[p_idx]
        
        st.info(f"🚂 {data.get('route')}")
        cols = st.columns(3)
        for i, a in enumerate(data.get('advices', [])[:3]): cols[i].markdown(f'<div class="advice-card">💡 {a}</div>', unsafe_allow_html=True)
        st.markdown(f"### 🏨 {data.get('hotel')}")

        if st.toggle("🛠️ 編集"):
            for d in data.get('days', []):
                for s in d.get('steps', []): s['content'] = st.text_input(f"{s['arrival']}", s['content'])

        for day in data.get('days', []):
            st.markdown(f"#### {day['label']}")
            for step in day.get('steps', []):
                rec = '<div class="aipia-badge">Aipia厳選</div>' if step.get('is_rec') else ''
                st.markdown(f'<div class="time-step">{rec}<b>{step["arrival"]} - {step["departure"]}</b><br>{step["content"]}</div>', unsafe_allow_html=True)

        if st.button("🏆 確定・共有へ", type="primary"):
            st.session_state.confirmed = data; st.session_state.step = "share"; st.rerun()

# --- STEP 5: 共有 ---
elif st.session_state.step == "share":
    d = st.session_state.confirmed
    q = urllib.parse.quote(d['hotel'])
    st.balloons()
    st.header(f"✨ {d['hotel']}")
    st.markdown(f"""
        <a href="https://search.rakuten.co.jp/search/mall/{q}/" target="_blank" class="reserve-btn" style="background:#bf0000;">楽天</a>
        <a href="https://www.jalan.net/keyword/{q}/" target="_blank" class="reserve-btn" style="background:#ff7a00;">じゃらん</a>
    """, unsafe_allow_html=True)
    
    st.subheader("📱 コピー用")
    st.text_area("LINE等に貼り付け", f"【旅程】\nホテル:{d['hotel']}\n" + "\n".join([f"{s['arrival']} {s['content']}" for dy in d['days'] for s in dy['steps']]))
    
    if st.button("🏠 戻る"): st.session_state.step = "input"; st.rerun()
