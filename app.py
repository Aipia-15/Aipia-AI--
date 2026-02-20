import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse
import json

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
        except Exception:
            continue
    return None

# CSS (ご指定のUIデザインを反映)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    .header-container { text-align: center; padding: 30px 0; border-bottom: 2px solid #D4AF37; background: #FFF; margin-bottom: 20px; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 3.5rem; color: #111; letter-spacing: 5px; margin: 0; }
    .aipia-sub { color: #D4AF37; font-weight: bold; letter-spacing: 3px; font-size: 0.9rem; margin-top: -10px; }
    
    /* プラン表示用UI */
    .day-box { background-color: #E8F5E9; padding: 12px 25px; border-radius: 15px; display: inline-block; font-weight: bold; margin: 25px 0 10px 0; border: 1px solid #C8E6C9; color: #2E7D32; font-size: 1.1rem; }
    .time-step { background-color: #E3F2FD; padding: 18px; border-radius: 5px; margin: 5px 0; border: 1px solid #BBDEFB; position: relative; line-height: 1.6; }
    .arrow { text-align: center; font-size: 1.8rem; color: #90CAF9; margin: 2px 0; font-weight: bold; }
    .ai-badge { background-color: #FF5252; color: white; font-size: 0.75rem; padding: 2px 8px; border-radius: 4px; float: right; font-weight: bold; margin-left: 10px; }
    .hotel-highlight { font-size: 1.8rem; font-weight: bold; color: #1A237E; margin: 15px 0; border-bottom: 2px solid #1A237E; display: inline-block; }
    .reserve-btn { background-color: #D32F2F; color: white !important; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "final_json" not in st.session_state: st.session_state.final_json = None

# ヘッダー
st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">-AIが創る、秘境への旅行プラン-</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力 (レイアウト修正) ---
if st.session_state.step == "input":
    # 1. キーワード検索（ロゴのすぐ下、横は空ける）
    keyword = st.text_input("🔍 キーワード検索（例：秘境、滝、古民家）", help="探したい雰囲気や特定の場所を入力してください")
    st.write("") # スペース

    # 2. メイン入力エリア（従来のブロックを配置）
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1: dep_place = st.text_input("🛫 出発地点", value="新宿駅")
    with col2: date_range = st.date_input("📅 旅行日程", value=(datetime.now(), datetime.now() + timedelta(days=1)))
    with col3: dep_time = st.time_input("🕔 出発時刻", value=datetime.strptime("08:00", "%H:%M").time())

    col4, col5, col6 = st.columns([2, 2, 2])
    with col4: pref = st.selectbox("📍 目的地（都道府県）", PREFECTURES)
    with col5: city = st.text_input("🏠 市区町村・詳細エリア")
    with col6: budget = st.number_input("💰 予算/人", 5000, 500000, 50000)

    # 3. 人数入力（復活）
    col7, col8, col9 = st.columns([2, 1, 1])
    with col7: purposes = st.multiselect("✨ 目的", ["秘境探索", "美食", "温泉", "歴史", "絶景", "癒やし"], default=["秘境探索"])
    with col8: adults = st.number_input("大人 (中学生以上)", 1, 20, 2)
    with col9: kids = st.number_input("小人 (小学生以下)", 0, 20, 0)

    if st.button("⚜️ 秘境リサーチを開始する", use_container_width=True, type="primary"):
        if not pref: st.error("都道府県を選択してください"); st.stop()
        st.session_state.form_data = {
            "dep": dep_place, "dest": f"{pref}{city}", "start_date": date_range[0],
            "adults": adults, "kids": kids, "purposes": purposes, "keyword": keyword
        }
        prompt = f"{pref}{city}周辺で{keyword}に関連する秘境スポットを10件。名称|解説|住所"
        content = call_groq_safe(prompt)
        if content:
            st.session_state.found_spots = [l.split('|') for l in content.split('\n') if '|' in l][:10]
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: カタログ ---
elif st.session_state.step == "select_spots":
    st.markdown(f"### 📍 {st.session_state.form_data['dest']} 厳選スポット")
    for i, s in enumerate(st.session_state.found_spots):
        with st.container():
            c_s1, c_s2 = st.columns([5, 1])
            with c_s1:
                st.markdown(f"**{s[0]}**")
                st.write(s[1])
            with c_s2:
                if st.checkbox("採用", key=f"s_{i}"):
                    if s[0] not in st.session_state.selected_spots: st.session_state.selected_spots.append(s[0])
        st.divider()
    
    if st.button("✅ ホテルの希望調査へ進む", type="primary"):
        st.session_state.step = "hotel_survey"; st.rerun()

# --- STEP 3: ホテル希望調査 ---
elif st.session_state.step == "hotel_survey":
    st.markdown("### 🏨 宿泊の希望")
    h_type = st.selectbox("ホテルのタイプ", ["絶景が見える宿", "歴史ある老舗旅館", "モダンな隠れ家ホテル", "自然に囲まれたコテージ", "コスパ重視の宿"])
    h_dinner = st.radio("夕食のスタイル", ["地産地消のフルコース/会席", "賑やかなビュッフェ", "外の地元の名店で食べる"])
    
    if st.button("✨ この条件で全日程プランを生成", type="primary"):
        st.session_state.hotel_wish = f"{h_type}で、夕食は{h_dinner}"
        with st.spinner("AIが最適なルートと時間の埋め合わせを計算中..."):
            prompt = f"""
            2日間の旅行プランを厳密なJSON形式で作成せよ。
            目的地：{st.session_state.form_data['dest']}
            採用：{st.session_state.selected_spots}
            ホテル希望：{st.session_state.hotel_wish}
            
            JSONルール：
            {{
              "hotel_info": {{"name": "実在のホテル名", "address": "住所"}},
              "days": [
                {{
                  "label": "一日目",
                  "steps": [
                    {{"time": "09:00", "content": "内容", "is_ai_suggested": false}},
                    {{"time": "11:30", "content": "AIおすすめのランチスポット", "is_ai_suggested": true}}
                  ]
                }}
              ]
            }}
            """
            res = call_groq_safe(prompt)
            try:
                start = res.find('{')
                end = res.rfind('}') + 1
                st.session_state.final_json = json.loads(res[start:end])
                st.session_state.step = "display"; st.rerun()
            except:
                st.error("プラン生成に失敗しました。もう一度お試しください。")

# --- STEP 4: 表示 (指定UI反映) ---
elif st.session_state.step == "display":
    data = st.session_state.final_json
    
    for day in data['days']:
        st.markdown(f'<div class="day-box">{day["label"]}</div>', unsafe_allow_html=True)
        for i, step in enumerate(day['steps']):
            ai_tag = '<span class="ai-badge">AIおすすめ</span>' if step.get('is_ai_suggested') else ""
            st.markdown(f"""
                <div class="time-step">
                    {ai_tag}
                    <small><b>{step['time']}</b></small><br>
                    {step['content']}
                </div>
            """, unsafe_allow_html=True)
            if i < len(day['steps']) - 1:
                st.markdown('<div class="arrow">↓</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("### 🏨 宿泊・詳細情報")
    h_name = data['hotel_info']['name']
    st.markdown(f'<div class="hotel-highlight">宿泊：{h_name}</div>', unsafe_allow_html=True)
    st.write(f"📍 住所：{data['hotel_info']['address']}")
    
    hq = urllib.parse.quote(f"{h_name} 公式サイト 予約")
    st.markdown(f'<a href="https://www.google.com/search?q={hq}" class="reserve-btn" target="_blank">🏨 ホテル詳細・予約サイトへ</a>', unsafe_allow_html=True)

    if st.button("🏠 ホームへ戻る"):
        st.session_state.clear(); st.rerun()
