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

# CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    .header-container { text-align: center; padding: 30px 0; border-bottom: 2px solid #D4AF37; background: #FFF; margin-bottom: 30px; }
    .aipia-logo { font-size: 3.5rem; color: #111; letter-spacing: 5px; margin: 0; font-weight: bold; }
    .aipia-sub { color: #D4AF37; font-weight: bold; letter-spacing: 3px; font-size: 0.9rem; margin-top: -10px; }
    
    /* 日付ボックス */
    .day-box { background-color: #E8F5E9; padding: 10px 20px; border-radius: 15px; display: inline-block; font-weight: bold; margin: 20px 0 10px 0; border: 1px solid #C8E6C9; }
    
    /* タイムスケジュールボックス */
    .time-step { background-color: #E3F2FD; padding: 15px; border-radius: 5px; margin: 5px 0; border: 1px solid #BBDEFB; position: relative; }
    .arrow { text-align: center; font-size: 1.5rem; color: #90CAF9; margin: 2px 0; }
    
    /* AIおすすめバッジ */
    .ai-badge { background-color: #FF5252; color: white; font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; float: right; font-weight: bold; }
    
    /* ホテル強調 */
    .hotel-name { font-size: 1.5rem; font-weight: bold; color: #1A237E; margin: 10px 0; }
    
    .official-btn { background-color: #00695C; color: white !important; padding: 6px 14px; border-radius: 4px; text-decoration: none; font-size: 0.8rem; }
    .reserve-btn { background-color: #D32F2F; color: white !important; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "final_json" not in st.session_state: st.session_state.final_json = None

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
    with c7: purposes = st.multiselect("✨ 目的", ["秘境探索", "美食", "温泉", "歴史", "絶景", "癒やし"], default=["秘境探索"])
    with c8: budget = st.number_input("💰 予算/人", 5000, 500000, 50000)
    
    if st.button("⚜️ 秘境リサーチ開始", use_container_width=True, type="primary"):
        st.session_state.form_data = {"dep": dep_place, "dest": f"{pref}{city}", "days": 2, "start_date": date_range[0]}
        prompt = f"{pref}{city}の秘境スポットを10件。名称|解説|住所"
        content = call_groq_safe(prompt)
        if content:
            st.session_state.found_spots = [l.split('|') for l in content.split('\n') if '|' in l][:10]
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: カタログ ---
elif st.session_state.step == "select_spots":
    st.markdown(f"### 📍 {st.session_state.form_data['dest']} スポット選択")
    for i, s in enumerate(st.session_state.found_spots):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{s[0]}**")
            st.caption(s[1])
        with col2:
            if st.checkbox("採用", key=f"s_{i}"):
                if s[0] not in st.session_state.selected_spots: st.session_state.selected_spots.append(s[0])
    
    if st.button("✅ ホテルの希望調査へ進む", type="primary"):
        st.session_state.step = "hotel_survey"; st.rerun()

# --- STEP 3: ホテル希望調査 ---
elif st.session_state.step == "hotel_survey":
    st.markdown("### 🏨 宿泊の希望をお聞かせください")
    hotel_pref = st.radio("ホテルのタイプ", ["絶景が見える宿", "老舗旅館", "モダンな隠れ家ホテル", "コスパ重視の快適な宿"])
    hotel_dinner = st.radio("夕食の希望", ["地元の食材を活かした会席", "ビュッフェ形式", "外で自由に食べる"])
    
    if st.button("✨ 全日程のプランを生成", type="primary"):
        st.session_state.hotel_wish = f"{hotel_pref}、夕食は{hotel_dinner}"
        with st.spinner("2日間の全行程を計算中..."):
            prompt = f"""
            以下の条件で2日間の旅行プランをJSON形式で作成してください。
            出発：{st.session_state.form_data['dep']}
            目的地：{st.session_state.form_data['dest']}
            採用スポット：{st.session_state.selected_spots}
            ホテルの希望：{st.session_state.hotel_wish}

            JSON構造：
            {{
              "hotel_name": "実在するホテル名",
              "hotel_url": "URL",
              "days": [
                {{
                  "day_label": "一日目",
                  "steps": [
                    {{"time": "08:00-09:30", "content": "移動内容・道順", "is_ai_suggested": false}},
                    {{"time": "10:00", "content": "スポット名", "is_ai_suggested": true}}
                  ]
                }}
              ]
            }}
            ※時間の埋め合わせに[AIおすすめ]スポットを適宜挿入してください。
            """
            res = call_groq_safe(prompt)
            # JSON部分のみ抽出
            try:
                start = res.find('{')
                end = res.rfind('}') + 1
                st.session_state.final_json = json.loads(res[start:end])
                st.session_state.step = "display"; st.rerun()
            except:
                st.error("プラン生成に失敗しました。もう一度お試しください。")

# --- STEP 4: 表示 ---
elif st.session_state.step == "display":
    data = st.session_state.final_json
    
    for day in data['days']:
        st.markdown(f'<div class="day-box">{day["day_label"]}</div>', unsafe_allow_html=True)
        for i, step in enumerate(day['steps']):
            ai_tag = '<span class="ai-badge">AIおすすめ</span>' if step.get('is_ai_suggested') else ""
            st.markdown(f"""
                <div class="time-step">
                    {ai_tag}
                    <small>{step['time']}</small><br>
                    <b>{step['content']}</b>
                </div>
            """, unsafe_allow_html=True)
            if i < len(day['steps']) - 1:
                st.markdown('<div class="arrow">↓</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("### 🏨 本日の宿泊先")
    st.markdown(f'<div class="hotel-name">{data["hotel_name"]}</div>', unsafe_allow_html=True)
    
    hq = urllib.parse.quote(f"{data['hotel_name']} 予約")
    st.markdown(f"""
    <div style="margin-top:20px;">
        <a href="https://www.google.com/search?q={hq}" class="reserve-btn" target="_blank">宿泊プランを確認・予約する</a>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🏠 最初に戻る"):
        st.session_state.clear(); st.rerun()
