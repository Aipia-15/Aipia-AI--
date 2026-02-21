import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import json
import re

# --- 1. 基本設定 ---
st.set_page_config(layout="wide", page_title="Aipia")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

PREFECTURES = [""] + ["北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県", "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県", "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県", "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県", "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"]

def call_groq_safe(prompt):
    target_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    for model_id in target_models:
        try:
            res = client.chat.completions.create(model=model_id, messages=[{"role": "user", "content": prompt}], temperature=0.7)
            if res.choices[0].message.content: return res.choices[0].message.content
        except: continue
    return None

def parse_json_safely(text):
    """JSONパースエラーを防ぐための堅牢な関数"""
    try:
        # JSON部分を抽出
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match: return None
        json_str = match.group()
        # 制御文字や余計なカンマなどの微修正
        json_str = re.sub(r",\s*}", "}", json_str)
        json_str = re.sub(r",\s*]", "]", json_str)
        return json.loads(json_str)
    except:
        return None

# --- 2. スタイル定義 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:wght@700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    .header-container { text-align: center; padding: 40px 0; border-bottom: 2px solid #D4AF37; background: #FFF; margin-bottom: 30px; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 3.5rem; color: #111; letter-spacing: 5px; margin: 0; }
    .aipia-sub { color: #D4AF37; font-weight: bold; letter-spacing: 2px; font-size: 1rem; margin-top: -5px; }
    .spot-card { margin-bottom: 30px; padding: 25px; background: #FFF; border-radius: 15px; border-left: 6px solid #D4AF37; }
    .day-box { background: linear-gradient(90deg, #E8F5E9, #FFF); padding: 12px 25px; border-radius: 8px; font-weight: bold; margin: 35px 0 15px 0; color: #2E7D32; border-left: 5px solid #2E7D32; }
    .time-step { background-color: #E3F2FD; padding: 20px; border-radius: 10px; margin: 10px 0; border: 1px solid #BBDEFB; position: relative; }
    .aipia-badge { position: absolute; top: -10px; right: -10px; background: #FFD700; color: #000; padding: 5px 15px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; border: 2px solid #FFF; }
    .advice-box { background-color: #FFF3E0; border-left: 5px solid #FF9800; padding: 15px; margin: 20px 0; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">-AIが創る、秘境への旅行プラン-</p></div>', unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "plans" not in st.session_state: st.session_state.plans = []

# --- STEP 1: ホーム画面 ---
if st.session_state.step == "input":
    col_k1, col_k2 = st.columns([3, 1])
    with col_k1: keyword = st.text_input("🔍 キーワード検索")
    with col_k2: transport = st.radio("🚃 交通手段", ["電車・公共交通", "車・レンタカー"], horizontal=True)
    
    walk_speed = st.select_slider("🚶‍♂️ 歩く速度", options=["ゆっくり", "普通", "早歩き"], value="普通")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1: dep_place = st.text_input("🛫 出発地点", value="新宿駅")
    with col2: date_range = st.date_input("📅 旅行日程", value=(datetime.now(), datetime.now() + timedelta(days=1)))
    with col3: dep_time = st.time_input("🕔 出発時刻", value=datetime.strptime("08:00", "%H:%M").time())
    
    col4, col5, col6 = st.columns([2, 2, 2])
    with col4: pref = st.selectbox("📍 都道府県", PREFECTURES)
    with col5: city = st.text_input("🏠 市区町村")
    with col6: budget = st.number_input("💰 予算/人", 5000, 500000, 50000)
    
    col7, col8, col9 = st.columns([2, 1, 1])
    with col7: purposes = st.multiselect("✨ 目的", ["秘境探索", "美食", "温泉", "歴史", "絶景", "海・水辺", "街歩き"], default=["秘境探索"])
    with col8: adults = st.number_input("大人", 1, 20, 2)
    with col9: kids = st.number_input("小人", 0, 20, 0)

    if st.button("⚜️ 秘境リサーチを開始する", use_container_width=True, type="primary"):
        st.session_state.form_data = {"dep": dep_place, "dest": f"{pref}{city}", "transport": transport, "speed": walk_speed, "people": f"大人{adults}名,小人{kids}名", "purposes": purposes}
        prompt = f"{pref}{city}周辺で{keyword}に関連するスポットを10件。名称|解説(公式URL等)|住所|おすすめ度1-5|混雑度1-5。山に偏らない多様なジャンルで。"
        content = call_groq_safe(prompt)
        if content:
            st.session_state.found_spots = [l.split('|') for l in content.strip().split('\n') if '|' in l]
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: スポット選択 ---
elif st.session_state.step == "select_spots":
    st.markdown(f"### 📍 {st.session_state.form_data['dest']} 候補スポット")
    for i, s in enumerate(st.session_state.found_spots):
        if len(s) < 2: continue
        st.markdown(f'''<div class="spot-card"><h4>{s[0]}</h4><p>{s[1]}</p></div>''', unsafe_allow_html=True)
        if st.checkbox("採用する", key=f"s_{i}"):
            if s[0] not in st.session_state.selected_spots: st.session_state.selected_spots.append(s[0])
    
    col_more, col_next = st.columns(2)
    with col_more:
        if st.button("➕ スポットをもっと見る"):
            res = call_groq_safe(f"{st.session_state.form_data['dest']}の別の秘境候補を10件。名称|解説|住所|4|2")
            if res: st.session_state.found_spots.extend([l.split('|') for l in res.split('\n') if '|' in l]); st.rerun()
    with col_next:
        if st.button("✅ ホテル・プラン生成へ", type="primary"): st.session_state.step = "hotel_survey"; st.rerun()

# --- STEP 3: ホテル希望 ---
elif st.session_state.step == "hotel_survey":
    st.markdown("### 🏨 宿泊の希望")
    h_type = st.selectbox("宿泊タイプ", ["絶景の宿", "老舗旅館", "バリアフリー完備の宿", "モダンホテル"])
    h_barrier = st.multiselect("必要な設備", ["段差なし", "車椅子対応", "手すり"])
    if st.button("✨ 5つのプランを生成する", type="primary"):
        st.session_state.hotel_data = {"type": h_type, "barrier": h_barrier}
        st.session_state.step = "plan_gen"; st.rerun()

# --- STEP 4: プラン表示 (JSONエラー対策版) ---
elif st.session_state.step == "plan_gen":
    if not st.session_state.plans:
        with st.spinner("5つのプランを構築中... 少々お待ちください"):
            for i in range(5):
                prompt = f"""
                旅行者:{st.session_state.form_data['people']}, 目的:{st.session_state.form_data['purposes']}
                出発:{st.session_state.form_data['dep']}, 交通:{st.session_state.form_data['transport']}, 速度:{st.session_state.form_data['speed']}
                スポット:{st.session_state.selected_spots}
                宿泊:{st.session_state.hotel_data['type']}
                上記条件で2日間プランを1つ作成し、必ず以下の純粋なJSON形式で返せ。
                {{'advice': '一言アドバイス', 'days': [{{'label': '1日目', 'steps': [{{'arrival': '09:00', 'departure': '10:00', 'content': '内容', 'is_recommended': false}}]}}]}}
                ※Aipia独自の「おすすめスポット」を1つ混ぜ、そのis_recommendedをtrueにすること。
                """
                res = call_groq_safe(prompt)
                parsed = parse_json_safely(res)
                if parsed: st.session_state.plans.append(parsed)

    if st.session_state.plans:
        plan_idx = st.sidebar.selectbox("プランを比較", [f"プラン {i+1}" for i in range(len(st.session_state.plans))])
        current_data = st.session_state.plans[int(plan_idx[-1])-1]

        st.markdown(f'<div class="advice-box">💡 <b>Aipiaのアドバイス:</b><br>{current_data.get("advice", "")}</div>', unsafe_allow_html=True)

        if st.toggle("🛠️ プランを手動編集する"):
            for d_idx, day in enumerate(current_data.get("days", [])):
                for s_idx, step in enumerate(day.get("steps", [])):
                    c1, c2, c3 = st.columns([1, 1, 3])
                    step['arrival'] = c1.text_input(f"着 {d_idx}-{s_idx}", step.get('arrival', ''))
                    step['departure'] = c2.text_input(f"出 {d_idx}-{s_idx}", step.get('departure', ''))
                    step['content'] = c3.text_area(f"内容 {d_idx}-{s_idx}", step.get('content', ''))

        for day in current_data.get("days", []):
            st.markdown(f'<div class="day-box">{day.get("label")}</div>', unsafe_allow_html=True)
            for step in day.get("steps", []):
                rec_badge = '<div class="aipia-badge">Aipiaおすすめ！</div>' if step.get('is_recommended') else ''
                st.markdown(f'''<div class="time-step">{rec_badge}
                    <b>{step.get('arrival')}着 / {step.get('departure')}発</b><br>{step.get('content')}</div>''', unsafe_allow_html=True)
        
        if st.button("🏆 最終確定・共有へ", type="primary"): 
            st.session_state.confirmed_plan = current_data
            st.session_state.step = "share"; st.rerun()
    else:
        st.error("プランの生成に失敗しました。もう一度「生成する」を押してください。")
        if st.button("🔄 再試行"): st.rerun()

elif st.session_state.step == "share":
    st.success("🎉 プランが確定しました！")
    plan = st.session_state.confirmed_plan
    st.markdown("### 🏨 宿泊予約リンク")
    st.markdown(f'<a href="https://www.google.com/search?q={st.session_state.hotel_data["type"]}+予約+最安値" target="_blank" style="background:#B71C1C; color:white; padding:10px 20px; text-decoration:none; border-radius:5px;">最安値を検索</a>', unsafe_allow_html=True)
    for day in plan.get("days", []):
        st.subheader(day.get("label"))
        for step in day.get("steps", []):
            st.info(f"🕒 {step.get('arrival')} - {step.get('departure')}\n\n{step.get('content')}")
    if st.button("🏠 ホームへ"): st.session_state.clear(); st.rerun()
