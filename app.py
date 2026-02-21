import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import json
import re
import urllib.parse

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
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match: return None
        json_str = match.group().replace("'", '"')
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
    .spot-card { margin-bottom: 20px; padding: 20px; background: #FFF; border-radius: 12px; border-left: 6px solid #D4AF37; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    .day-box { background: linear-gradient(90deg, #E8F5E9, #FFF); padding: 12px 25px; border-radius: 8px; font-weight: bold; margin: 30px 0 10px 0; color: #2E7D32; border-left: 5px solid #2E7D32; }
    .time-step { background-color: #E3F2FD; padding: 20px; border-radius: 10px; margin: 10px 0; border: 1px solid #BBDEFB; position: relative; }
    .aipia-badge { position: absolute; top: -10px; right: -10px; background: #FFD700; color: #000; padding: 5px 15px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; border: 2px solid #FFF; }
    .advice-container { display: flex; gap: 10px; margin: 20px 0; flex-wrap: wrap; }
    .advice-card { flex: 1; min-width: 250px; background-color: #FFF3E0; border-left: 5px solid #FF9800; padding: 15px; border-radius: 5px; font-size: 0.9rem; }
    .reserve-btn { display: inline-block; padding: 10px 20px; margin: 5px; border-radius: 5px; color: white !important; text-decoration: none !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">-AIが創る、秘境への旅行プラン-</p></div>', unsafe_allow_html=True)

if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "plans" not in st.session_state: st.session_state.plans = []

# --- STEP 1: 入力 ---
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
    
    col_pur, col_people = st.columns([3, 2])
    with col_pur: purposes = st.multiselect("✨ 目的", ["秘境探索", "美食", "温泉", "歴史", "絶景", "バリアフリー重視"], default=["秘境探索"])
    with col_people:
        a_count = st.number_input("大人", 1, 10, 2)
        k_count = st.number_input("小人", 0, 10, 0)

    if st.button("⚜️ 秘境リサーチを開始する", use_container_width=True, type="primary"):
        st.session_state.form_data = {"dep": dep_place, "dest": f"{pref}{city}", "transport": transport, "speed": walk_speed, "people": f"大人{a_count}名,小人{k_count}名", "purposes": purposes}
        prompt = f"{pref}{city}周辺の{keyword}スポットを10件。必ず公式URLや情報サイトのURLを含めて。形式：名称|解説|住所|URL|ジャンル"
        res = call_groq_safe(prompt)
        if res:
            st.session_state.found_spots = [l.split('|') for l in res.strip().split('\n') if '|' in l]
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: スポット選択 ---
elif st.session_state.step == "select_spots":
    st.markdown(f"### 📍 {st.session_state.form_data['dest']} 候補スポット")
    for i, s in enumerate(st.session_state.found_spots):
        if len(s) < 2: continue
        url_link = f'<br><a href="{s[3]}" target="_blank">🌐 公式・関連サイトを見る</a>' if len(s)>3 and "http" in s[3] else ""
        st.markdown(f'<div class="spot-card"><h4>{s[0]}</h4><p>{s[1]}{url_link}</p></div>', unsafe_allow_html=True)
        if st.checkbox("このスポットを採用", key=f"s_{i}"):
            if s[0] not in st.session_state.selected_spots: st.session_state.selected_spots.append(s[0])
    
    col_more, col_next = st.columns(2)
    with col_more:
        if st.button("➕ スポットをもっと見る"):
            res = call_groq_safe(f"{st.session_state.form_data['dest']}の未紹介の秘境をさらに10件。名称|解説|住所|URL|ジャンル")
            if res: st.session_state.found_spots.extend([l.split('|') for l in res.strip().split('\n') if '|' in l]); st.rerun()
    with col_next:
        if st.button("✅ ホテル・プラン生成へ", type="primary"): st.session_state.step = "hotel_survey"; st.rerun()

# --- STEP 3: ホテル希望 ---
elif st.session_state.step == "hotel_survey":
    st.markdown("### 🏨 宿泊とバリアフリーの希望")
    h_style = st.selectbox("宿泊スタイル", ["絶景の宿", "老舗旅館", "バリアフリー完備の宿", "モダンラグジュアリー"])
    h_barrier = st.multiselect("必要な配慮", ["車椅子対応", "段差なし", "貸切風呂", "エレベーター至近"])
    if st.button("✨ 5つの詳細プランを生成", type="primary"):
        st.session_state.hotel_data = {"style": h_style, "barrier": h_barrier}
        st.session_state.step = "plan_gen"; st.rerun()

# --- STEP 4: プラン表示 (全日程・チェックイン・編集) ---
elif st.session_state.step == "plan_gen":
    if not st.session_state.plans:
        with st.spinner("実在する宿泊施設とチェックイン時間を調査中..."):
            for i in range(5):
                prompt = f"""
                旅行者:{st.session_state.form_data['people']}, 目的:{st.session_state.form_data['purposes']}
                出発:{st.session_state.form_data['dep']}, スポット:{st.session_state.selected_spots}, 宿泊:{st.session_state.hotel_data['style']}
                
                【厳守】
                1. 1日目と2日目、全日程を網羅すること。
                2. 実在するホテル名を 'hotel_name' に入れる。
                3. 1日目の宿泊行程には、必ず「15:00 チェックイン」のように時間を明記すること。
                4. Aipia独自の専門アドバイスを3個、'advices'配列に入れること。
                5. スポットごとに情報URLを 'url' キーで含めること（不明ならGoogle検索URL）。
                
                {{'advices': ['...', '...', '...'], 'hotel_name': '具体的施設名', 'days': [{{'label': '1日目', 'steps': [{{'arrival': '15:00', 'departure': '翌09:00', 'content': '...', 'url': '...', 'is_recommended': false}}]}}]}}
                """
                res = call_groq_safe(prompt)
                parsed = parse_json_safely(res)
                if parsed: st.session_state.plans.append(parsed)

    if st.session_state.plans:
        plan_idx = st.sidebar.selectbox("プランを比較", [f"プラン {i+1}" for i in range(len(st.session_state.plans))])
        current_data = st.session_state.plans[int(plan_idx[-1])-1]

        # アドバイス
        advs = current_data.get("advices", ["計画的な移動を。", "地元の味を大切に。", "景色を楽しみましょう。"])
        st.markdown('<div class="advice-container">' + "".join([f'<div class="advice-card">💡 {a}</div>' for a in advs[:3]]) + '</div>', unsafe_allow_html=True)
        
        st.info(f"🏨 **提案ホテル:** {current_data.get('hotel_name')}")

        if st.toggle("🛠️ プランを編集する"):
            for d_idx, day in enumerate(current_data.get("days", [])):
                for s_idx, step in enumerate(day.get("steps", [])):
                    c1, c2, c3 = st.columns([1, 1, 3])
                    step['arrival'] = c1.text_input(f"着 {d_idx}-{s_idx}", step.get('arrival'))
                    step['departure'] = c2.text_input(f"出 {d_idx}-{s_idx}", step.get('departure'))
                    step['content'] = c3.text_area(f"内容 {d_idx}-{s_idx}", step.get('content'))

        for day in current_data.get("days", []):
            st.markdown(f'<div class="day-box">{day.get("label")}</div>', unsafe_allow_html=True)
            for step in day.get("steps", []):
                rec = '<div class="aipia-badge">Aipia厳選！</div>' if step.get('is_recommended') else ''
                url_btn = f'<br><a href="{step.get("url", "#")}" target="_blank" style="font-size:0.8rem; color:#1976D2;">🔗 詳細情報を見る</a>'
                st.markdown(f'<div class="time-step">{rec}<b>{step.get("arrival")}着 / {step.get("departure")}発</b><br>{step.get("content")}{url_btn}</div>', unsafe_allow_html=True)
        
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("🔄 案を再生成"): st.session_state.plans = []; st.rerun()
        with col_b2:
            if st.button("🏆 最終確定・予約", type="primary"): 
                st.session_state.confirmed_plan = current_data
                st.session_state.step = "share"; st.rerun()

elif st.session_state.step == "share":
    plan = st.session_state.confirmed_plan
    h_name = plan.get("hotel_name", "宿泊施設")
    q_h = urllib.parse.quote(h_name)
    
    st.success(f"🎉 完璧な旅程が完成しました。")
    st.markdown(f"### 🏨 宿泊予約：{h_name}")
    
    # 大手サイトへのクイックアクセスボタン
    st.markdown(f"""
        <div style="margin-bottom:20px;">
            <a href="https://hb.afl.rakuten.co.jp/hgc/share/search?pc=https%3A%2F%2Fsearch.rakuten.co.jp%2Fsearch%2Fmall%2F{q_h}%2F" target="_blank" class="reserve-btn" style="background:#bf0000;">楽天トラベルで予約</a>
            <a href="https://www.jalan.net/keyword/{q_h}/" target="_blank" class="reserve-btn" style="background:#ff7a00;">じゃらんで予約</a>
            <a href="https://www.ikyu.com/search/?keyword={q_h}" target="_blank" class="reserve-btn" style="background:#003567;">一休.comで予約</a>
        </div>
    """, unsafe_allow_html=True)

    for day in plan.get("days", []):
        st.subheader(day.get("label"))
        for step in day.get("steps", []):
            st.info(f"🕒 {step.get('arrival')} - {step.get('departure')}\n\n{step.get('content')}")
    
    if st.button("🏠 ホームへ戻る"): st.session_state.clear(); st.rerun()
