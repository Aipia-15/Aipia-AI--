import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse

# 1. ページ基本設定
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

PREFECTURES = [""] + ["北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県", "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県", "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県", "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県", "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"]

# CSSデザイン
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    .header-container { text-align: center; padding: 30px 0; border-bottom: 2px solid #D4AF37; background: #FFF; margin-bottom: 30px; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 3.5rem; color: #111; letter-spacing: 5px; margin: 0; }
    .aipia-sub { color: #D4AF37; font-weight: bold; letter-spacing: 3px; font-size: 0.9rem; }
    .spot-card { background: #FFF; border: 1px solid #E0D8C3; border-radius: 12px; padding: 20px; margin-bottom: 20px; }
    .line-button { background-color: #06C755; color: white !important; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; }
    .plan-text { white-space: pre-wrap; line-height: 1.8; background: #FFF; padding: 20px; border: 1px solid #D4AF37; border-radius: 10px; font-size: 1rem; }
    </style>
""", unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "show_all_spots" not in st.session_state: st.session_state.show_all_spots = False
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}
if "edit_mode" not in st.session_state: st.session_state.edit_mode = False

# ロゴとサブタイトル（固定）
st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">- AI Executive Concierge -</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力 ---
if st.session_state.step == "input":
    st.markdown('<h3 style="text-align:center;">Travel Profile</h3>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1: dep_place = st.text_input("🛫 出発地点", value="新宿駅")
    with c2: date_range = st.date_input("📅 旅行日程", value=(datetime.now(), datetime.now() + timedelta(days=1)))
    with c3: dep_time = st.time_input("🕔 出発時刻", value=datetime.strptime("08:00", "%H:%M").time())

    c4, c5 = st.columns(2) # 都道府県・市区町村 横並び
    with c4: pref = st.selectbox("📍 目的地（都道府県）", PREFECTURES)
    with c5: city = st.text_input("🏠 市区町村・エリア詳細")

    c6, c7, c8 = st.columns([1, 2, 1])
    with c6: keyword = st.text_input("🔍 キーワード")
    with c7: purposes = st.multiselect("✨ 目的", ["秘境探索", "美食", "温泉", "歴史"], default=["秘境探索"])
    with c8: budget = st.number_input("💰 予算/人", 5000, 500000, 50000)

    # 人数入力欄（復元）
    c9, c10 = st.columns(2)
    with c9: adults = st.number_input("大人 (中学生以上)", 1, 20, 2)
    with c10: kids = st.number_input("小人 (小学生以下)", 0, 20, 0)

    if st.button("⚜️ 10個の厳選スポットをリサーチする", use_container_width=True, type="primary"):
        if not pref: st.error("都道府県を選んでください"); st.stop()
        st.session_state.form_data = {"dep": dep_place, "dep_time": dep_time, "dest": f"{pref}{city}", "budget": budget, "adults": adults, "kids": kids}
        
        with st.spinner("実在する10件のスポットを解析中..."):
            prompt = f"{pref}{city}周辺で実在スポットを必ず10件挙げよ。形式：名称|場所詳細・魅力(200字)|費用|バリアフリー|駐車場|マップURL"
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
            lines = [l.strip() for l in res.choices[0].message.content.split('\n') if '|' in l]
            st.session_state.found_spots = []
            for l in lines[:10]:
                p = l.split('|')
                if len(p) >= 6: st.session_state.found_spots.append({"name": p[0], "desc": p[1], "fee": p[2], "bf": p[3], "park": p[4], "url": p[5]})
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: スポットカタログ（More機能付） ---
elif st.session_state.step == "select_spots":
    st.markdown(f"### 📍 {st.session_state.form_data['dest']} カタログ")
    
    # 最初は5件表示、Moreボタンで10件に増やす
    display_count = 10 if st.session_state.show_all_spots else 5
    for i in range(min(display_count, len(st.session_state.found_spots))):
        spot = st.session_state.found_spots[i]
        with st.container():
            col_img, col_txt = st.columns([1, 3])
            with col_img: st.image("https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=400", use_column_width=True)
            with col_txt:
                st.markdown(f"#### [{spot['name']}]({spot['url']})")
                st.write(spot['desc'])
                st.markdown(f"💰 {spot['fee']} | ♿ {spot['bf']} | 🚗 {spot['park']}")
                if st.checkbox("採用", key=f"sel_{i}"):
                    if spot['name'] not in st.session_state.selected_spots: st.session_state.selected_spots.append(spot['name'])
        st.divider()

    if not st.session_state.show_all_spots:
        if st.button("More（他の候補も見る）"):
            st.session_state.show_all_spots = True; st.rerun()

    if st.button("✅ 確定して5つのプランを生成", use_container_width=True, type="primary"):
        st.session_state.step = "final_plan"; st.rerun()

# --- STEP 3: 5プラン生成・ホテルURL・LINE共有 ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plans:
        with st.spinner("ホテル・改行を含む5つのプランを編纂中..."):
            for label in ["Plan A (王道)", "Plan B (穴場)", "Plan C (ゆったり)", "Plan D (アクティブ)", "Plan E (グルメ)"]:
                prompt = f"{st.session_state.form_data['dep']}発 {st.session_state.form_data['dep_time']}。宿泊施設(ホテル)を必ず含め、時間・場所ごとに改行を多用して詳しく書け。スポット：{st.session_state.selected_spots}。最後にホテル予約URLも添えろ。"
                res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
                st.session_state.final_plans[label] = res.choices[0].message.content

    chosen = st.radio("プラン選択", list(st.session_state.final_plans.keys()), horizontal=True)

    if not st.session_state.edit_mode:
        st.markdown(f'<div class="plan-text">{st.session_state.final_plans[chosen]}</div>', unsafe_allow_html=True)
        if st.button("✏️ このプランを編集（削除・調整）"): st.session_state.edit_mode = True; st.rerun()
    else:
        edited = st.text_area("プラン編集（改行や時間を自由に変更してください）", value=st.session_state.final_plans[chosen], height=500)
        if st.button("💾 保存"):
            st.session_state.final_plans[chosen] = edited
            st.session_state.edit_mode = False; st.rerun()

    st.divider()
    share_msg = f"【Aipia 旅行プラン】\n{st.session_state.final_plans[chosen]}"
    line_url = f"https://line.me/R/msg/text/?{urllib.parse.quote(share_msg)}"
    st.markdown(f'<a href="{line_url}" target="_blank" class="line-button">LINEで旅程を共有する</a>', unsafe_allow_html=True)

    if st.button("🏠 ホームへ戻る"):
        st.session_state.clear(); st.session_state.step = "input"; st.rerun()
