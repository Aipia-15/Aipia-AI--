import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse
import json
import re

# --- 1. 基本設定 ---
st.set_page_config(layout="wide", page_title="Aipia - AI秘境旅行プラン")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

PREFECTURES = [""] + ["北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県", "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県", "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県", "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県", "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"]

def call_groq_safe(prompt):
    target_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    for model_id in target_models:
        try:
            res = client.chat.completions.create(model=model_id, messages=[{"role": "user", "content": prompt}], temperature=0.7)
            return res.choices[0].message.content
        except: continue
    return None

# CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:wght@700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    .header-container { text-align: center; padding: 20px 0; border-bottom: 2px solid #D4AF37; background: #FFF; margin-bottom: 10px; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 3rem; color: #111; letter-spacing: 5px; margin: 0; }
    .aipia-sub { color: #D4AF37; font-weight: bold; letter-spacing: 2px; font-size: 0.8rem; margin-top: -5px; }
    .day-box { background-color: #E8F5E9; padding: 10px 25px; border-radius: 12px; display: inline-block; font-weight: bold; margin: 25px 0 10px 0; color: #2E7D32; border: 1px solid #C8E6C9; }
    .time-step { background-color: #E3F2FD; padding: 15px; border-radius: 8px; margin: 5px 0; border: 1px solid #BBDEFB; line-height: 1.6; }
    .arrow { text-align: center; font-size: 1.8rem; color: #90CAF9; margin: 2px 0; font-weight: bold; }
    .ai-badge { background-color: #FF5252; color: white; font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; float: right; font-weight: bold; }
    .advice-box { background-color: #F1F8E9; padding: 20px; border-radius: 10px; border: 1px solid #C8E6C9; margin: 30px 0; }
    .hotel-highlight { font-size: 1.8rem; font-weight: bold; color: #1A237E; margin: 15px 0; border-bottom: 2px solid #1A237E; display: inline-block; }
    .spot-img { width: 100%; border-radius: 10px; margin-bottom: 10px; object-fit: cover; height: 180px; background: #EEE; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    .reserve-btn { background-color: #D32F2F; color: white !important; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; text-align: center; }
    .url-link { font-size: 0.8rem; color: #00695C; text-decoration: underline; margin-right: 10px; }
    </style>
""", unsafe_allow_html=True)

if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "plans" not in st.session_state: st.session_state.plans = []
if "confirmed_plan" not in st.session_state: st.session_state.confirmed_plan = None

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">-AIが創る、秘境への旅行プラン-</p></div>', unsafe_allow_html=True)

# --- STEP 1: ホーム画面 ---
if st.session_state.step == "input":
    walk_speed = st.select_slider("🚶‍♂️ 歩く速度", options=["ゆっくり", "普通", "早歩き"], value="普通")
    keyword = st.text_input("🔍 キーワード検索（例：雲海が見える場所、ジブリのような世界観）")
    st.write("---")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1: dep_place = st.text_input("🛫 出発地点", value="新宿駅")
    with col2: date_range = st.date_input("📅 旅行日程", value=(datetime.now(), datetime.now() + timedelta(days=1)))
    with col3: dep_time = st.time_input("🕔 出発時刻", value=datetime.strptime("08:00", "%H:%M").time())
    
    col4, col5, col6 = st.columns([2, 2, 2])
    with col4: pref = st.selectbox("📍 都道府県", PREFECTURES)
    with col5: city = st.text_input("🏠 市区町村・詳細")
    with col6: budget = st.number_input("💰 予算/人", 5000, 500000, 50000)
    
    col7, col8, col9 = st.columns([2, 1, 1])
    with col7: 
        purposes = st.multiselect("✨ 目的 (複数選択可)", 
            ["秘境探索", "美食・地産地消", "源泉かけ流し温泉", "歴史・重要文化財", "絶景・カメラ旅", 
             "パワースポット", "癒やし・マインドフルネス", "ドライブ", "アート巡り", "穴場スポット", 
             "地元体験・工房", "高級感・ラグジュアリー", "レトロ・ノスタルジック", "夜景", "登山・ハイキング"], 
            default=["秘境探索"])
    with col8: adults = st.number_input("大人", 1, 20, 2)
    with col9: kids = st.number_input("小人", 0, 20, 0)

    if st.button("⚜️ 秘境リサーチを開始する", use_container_width=True, type="primary"):
        if not pref: st.error("都道府県を選択してください"); st.stop()
        st.session_state.form_data = {"dep": dep_place, "dest": f"{pref}{city}", "speed": walk_speed}
        with st.spinner("隠れた名所を探索中..."):
            prompt = f"{pref}{city}周辺の{keyword}や{purposes}に合うスポットを10件教えろ。必ず『名称|解説|住所|画像検索単語』の形式で、1行に1施設書け。"
            content = call_groq_safe(prompt)
            if content:
                lines = content.strip().split('\n')
                st.session_state.found_spots = [l.split('|') for l in lines if '|' in l]
                if not st.session_state.found_spots:
                    st.error("スポットが見つかりませんでした。条件を変えてお試しください。")
                else:
                    st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: スポット選択 ---
elif st.session_state.step == "select_spots":
    st.markdown(f"### 📍 {st.session_state.form_data['dest']} 厳選カタログ")
    for i, s in enumerate(st.session_state.found_spots):
        if len(s) < 3: continue
        col_img, col_txt = st.columns([1, 3])
        with col_img:
            st.markdown(f'<img src="https://source.unsplash.com/featured/?{urllib.parse.quote(s[3] if len(s)>3 else s[0])}" class="spot-img">', unsafe_allow_html=True)
        with col_txt:
            st.markdown(f"**{s[0]}**")
            st.caption(s[1])
            st.markdown(f'<a href="https://www.google.com/search?q={urllib.parse.quote(s[0]+ " 公式サイト")}" target="_blank" class="url-link">公式サイト</a>', unsafe_allow_html=True)
            if st.checkbox("旅程に入れる", key=f"s_{i}"):
                if s[0] not in st.session_state.selected_spots: st.session_state.selected_spots.append(s[0])
    
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        if st.button("➕ 別のスポットをもっと見る"):
            prompt = f"{st.session_state.form_data['dest']}の別の秘境を10件。名称|解説|住所|画像検索単語"
            content = call_groq_safe(prompt)
            if content: st.session_state.found_spots.extend([l.split('|') for l in content.split('\n') if '|' in l]); st.rerun()
    with c_m2:
        if st.button("✅ ホテルの希望へ進む", type="primary"): st.session_state.step = "hotel_survey"; st.rerun()

# --- STEP 3: ホテル調査 ---
elif st.session_state.step == "hotel_survey":
    st.markdown("### 🏨 宿泊のこだわり")
    h_type = st.selectbox("ホテルのタイプ", ["絶景が見える宿", "歴史ある老舗旅館", "モダンな隠れ家ホテル", "コスパ・利便性重視"])
    h_barriers = st.multiselect("バリアフリー・設備（複数選択可）", ["段差なし", "車椅子対応トイレ", "エレベーター完備", "手すりあり", "部屋食可能"])
    
    if st.button("✨ 5つのプランを同時生成", type="primary"):
        st.session_state.hotel_wish = f"{h_type} (設備要望: {', '.join(h_barriers)})"
        st.session_state.step = "plan_gen"; st.rerun()

# --- STEP 4: プラン生成 ---
elif st.session_state.step == "plan_gen":
    if not st.session_state.plans:
        with st.spinner("分刻みの旅程を5パターン作成しています..."):
            for i in range(5):
                prompt = f"""
                2日間のプランをJSON形式で出力。
                採用：{st.session_state.selected_spots}
                速度：{st.session_state.form_data['speed']}
                ホテル希望：{st.session_state.hotel_wish}
                ルール：
                1. 各地点(スポット・ランチ・駅)に『到着時間』と『出発時間』を必ずセットで記載。
                2. 実在するホテル名を決め、夕方の『ホテルチェックイン時間』を記載。
                3. AIおすすめランチは具体的店名。
                4. 特急利用時は予約サイト(えきねっと等)と手順。
                JSON: {{"days": [{{"label": "一日目", "steps": [{{"time": "到着00:00 - 出発00:00", "content": "名称と内容", "is_ai_suggested": false}}]}}], "hotel": {{"name": "ホテル名", "address": "住所"}}}}
                """
                res = call_groq_safe(prompt)
                try: 
                    clean_res = re.search(r"\{.*\}", res, re.DOTALL).group()
                    st.session_state.plans.append(json.loads(clean_res))
                except: continue
    st.session_state.step = "display"; st.rerun()

# --- STEP 5: 表示・確定 ---
elif st.session_state.step == "display":
    plan_idx_str = st.sidebar.selectbox("プラン比較", [f"プラン {i+1}" for i in range(len(st.session_state.plans))])
    idx = int(plan_idx_str.split()[-1]) - 1
    data = st.session_state.plans[idx]
    
    for day in data['days']:
        st.markdown(f'<div class="day-box">{day["label"]}</div>', unsafe_allow_html=True)
        for i, step in enumerate(day['steps']):
            ai_tag = '<span class="ai-badge">AIおすすめ</span>' if step.get('is_ai_suggested') else ""
            st.markdown(f'<div class="time-step">{ai_tag}<small><b>{step["time"]}</b></small><br>{step["content"]}</div>', unsafe_allow_html=True)
            # 各ステップの内容から検索URL生成
            name = step["content"].split('：')[0]
            st.markdown(f'<a href="https://www.google.com/search?q={urllib.parse.quote(name)}" target="_blank" class="url-link">🔗詳細を検索</a>', unsafe_allow_html=True)
            if i < len(day['steps']) - 1: st.markdown('<div class="arrow">↓</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="hotel-highlight">宿泊：{data["hotel"]["name"]}</div>', unsafe_allow_html=True)
    
    if st.button("🏆 このプランで確定する", use_container_width=True, type="primary"):
        st.session_state.confirmed_plan = data
        st.session_state.step = "share"; st.rerun()

# --- STEP 6: 共有ページ ---
elif st.session_state.step == "share":
    st.success("🎉 旅のプランが確定しました！")
    data = st.session_state.confirmed_plan
    
    # 確定プランの清書表示
    for day in data['days']:
        st.markdown(f'### {day["label"]}')
        for step in day['steps']:
            st.info(f"🕒 {step['time']} \n\n {step['content']}")
            
    st.markdown(f"### 🏨 宿泊先: {data['hotel']['name']}")
    st.write(f"住所: {data['hotel']['address']}")
    
    st.markdown("""<div class="advice-box"><b>💡 Aipiaの旅のアドバイス</b><br>
    1. 秘境の店舗は休業日が不定期なことが多いため、前日に電話確認を。 <br>
    2. 特急券予約（えきねっと等）は早割をチェック！ <br>
    3. モバイルバッテリーは必須です。</div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<a href="https://line.me/R/msg/text/?Aipiaで作成した旅プラン：{data["hotel"]["name"]}泊" class="reserve-btn" style="background-color:#06C755; width:100%;" target="_blank">LINEでプランを共有</a>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<a href="https://mail.google.com/mail/?view=cm&fs=1" class="reserve-btn" style="background-color:#EA4335; width:100%;" target="_blank">Gmailでプランを共有</a>', unsafe_allow_html=True)
    
    if st.button("🏠 最初に戻る"): st.session_state.clear(); st.rerun()
