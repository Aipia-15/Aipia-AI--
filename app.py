import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse
import time

# 1. ページ基本設定
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

PREFECTURES = [""] + ["北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県", "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県", "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県", "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県", "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"]

# デザイン定義
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    .header-container { text-align: center; padding: 30px 0; border-bottom: 1px solid #D4AF37; background: #FFF; margin-bottom: 30px; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 3.5rem; color: #111; letter-spacing: 5px; margin: 0; }
    .catalog-card { background: #FFF; border: 1px solid #E0D8C3; border-radius: 12px; padding: 25px; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
    .status-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; margin-right: 10px; background: #F1ECE4; color: #5D4037; font-weight: bold; }
    .chuuni-title { font-size: 2rem; font-style: italic; color: #111; text-align: center; margin-bottom: 30px; border-bottom: 2px solid #D4AF37; }
    </style>
""", unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "plan_data" not in st.session_state: st.session_state.plan_data = []

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p style="color:#D4AF37; font-weight:bold; letter-spacing:3px;">- AI Executive Concierge -</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力 (ホーム画面レイアウト修正) ---
if st.session_state.step == "input":
    st.markdown('<h3 style="text-align:center;">01. Travel Profile</h3>', unsafe_allow_html=True)
    
    # 段組1: 出発基本
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1: dep_place = st.text_input("🛫 出発地点", value="新宿駅")
    with c2: 
        # 日程を範囲選択（カレンダーから2点選べる）に戻しました
        date_range = st.date_input("📅 旅行日程", value=(datetime.now(), datetime.now() + timedelta(days=1)))
    with c3: dep_time = st.time_input("🕔 出発時刻", value=datetime.strptime("08:00", "%H:%M").time())

    # 段組2: 目的地 (横並び完全復元)
    c4, c5 = st.columns(2)
    with c4: pref = st.selectbox("📍 目的地（都道府県）", PREFECTURES, index=0)
    with c5: city = st.text_input("🏠 市区町村・エリア", placeholder="例：松本市、伊勢市など")

    # 段組3: 条件・タグ
    c6, c7, c8 = st.columns([1, 2, 1])
    with c6: keyword = st.text_input("🔍 自由キーワード")
    with c7: purposes = st.multiselect("✨ 旅の目的（タグ）", ["秘境探索", "美食・地酒", "歴史・文化", "温泉・癒やし", "アクティビティ"], default=["秘境探索"])
    with c8: budget = st.number_input("💰 予算/人(円)", 5000, 1000000, 50000, step=5000)

    # 段組4: 人数
    c9, c10 = st.columns(2)
    with c9: adults = st.number_input("大人 (中学生以上)", 1, 20, 2)
    with c10: kids = st.number_input("小人 (小学生以下)", 0, 20, 0)

    if st.button("⚜️ 秘境カタログを召喚する", use_container_width=True, type="primary"):
        if not pref:
            st.error("都道府県を選択してください。")
        else:
            st.session_state.form_data = {
                "dep": dep_place, "dep_time": dep_time, "dest": f"{pref}{city}", "budget": budget, 
                "purposes": purposes, "people": f"大人{adults}名,小人{kids}名",
                "days": (date_range[1]-date_range[0]).days + 1 if isinstance(date_range, tuple) and len(date_range)==2 else 1
            }
            with st.spinner("スポット情報を強制解析中..."):
                prompt = f"""目的地「{pref}{city}」で「{keyword}」に関連し「{purposes}」に合う実在スポットを必ず5件出せ。
                「見つからない」は厳禁。形式を死守せよ：名称|解説|費用|人気|バリアフリー|駐車場|周辺秘境|周辺食事"""
                res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
                # パース処理の強化
                lines = [l.strip() for l in res.choices[0].message.content.split('\n') if '|' in l]
                st.session_state.found_spots = []
                for l in lines[:5]:
                    p = l.split('|')
                    if len(p) >= 8:
                        st.session_state.found_spots.append({"name": p[0], "desc": p[1], "fee": p[2], "pop": p[3], "bf": p[4], "park": p[5], "sub_h": p[6], "sub_f": p[7]})
                st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: カタログ選択 ---
elif st.session_state.step == "select_spots":
    st.markdown(f"### 📍 {st.session_state.form_data['dest']} 厳選カタログ")
    for i, spot in enumerate(st.session_state.found_spots):
        st.markdown(f"""<div class="catalog-card"><b>{spot['name']}</b><br><small>{spot['desc']}</small><br>
        <span class="status-badge">💰 {spot['fee']}</span><span class="status-badge">♿ {spot['bf']}</span><span class="status-badge">🚗 {spot['park']}</span></div>""", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        if c1.checkbox(f"「{spot['name']}」を採用", key=f"m_{i}"): st.session_state.selected_spots.append(spot['name'])
        if c2.checkbox(f"周辺秘境：{spot['sub_h']}", key=f"h_{i}"): st.session_state.selected_spots.append(spot['sub_h'])
        if c3.checkbox(f"周辺食事：{spot['sub_f']}", key=f"f_{i}"): st.session_state.selected_spots.append(spot['sub_f'])
    
    if st.button("✅ 選択を確定して旅程を作る", use_container_width=True, type="primary"):
        st.session_state.step = "final_plan"; st.rerun()

# --- STEP 3: 旅程編集・共有 ---
elif st.session_state.step == "final_plan":
    if not st.session_state.plan_data:
        with st.spinner("詳細な旅程を編纂中..."):
            prompt = f"""出発{st.session_state.form_data['dep']}、時刻{st.session_state.form_data['dep_time']}。
            {st.session_state.form_data['days']}日間の旅程を「時間|行動」の形式で出せ。宿泊施設(ホテル)を必ず含めろ。
            採用スポット：{st.session_state.selected_spots}"""
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
            for l in res.choices[0].message.content.split('\n'):
                if '|' in l:
                    t, a = l.split('|', 1)
                    st.session_state.plan_data.append({"time": t.strip(), "action": a.strip()})

    st.markdown("### 🗓️ 旅のしおり（自由編集モード）")
    st.info("時間をずらしたり、不要な予定を削除・修正できます。")

    # 編集用UI
    edited_plan = []
    for i, item in enumerate(st.session_state.plan_data):
        c_t, c_a, c_d = st.columns([1, 4, 1])
        with c_t: new_t = st.text_input("時間", value=item['time'], key=f"t_{i}")
        with c_a: new_a = st.text_input("予定", value=item['action'], key=f"a_{i}")
        with c_d:
            if not st.button("🗑️", key=f"d_{i}"):
                edited_plan.append({"time": new_t, "action": new_a})
    
    st.session_state.plan_data = edited_plan

    st.divider()
    col_1, col_2 = st.columns(2)
    with col_1:
        if st.button("🔄 AIで最初から作り直す"):
            st.session_state.plan_data = []; st.rerun()
    with col_2:
        # 共有用テキスト生成
        share_content = "\n".join([f"{x['time']} : {x['action']}" for x in st.session_state.plan_data])
        st.download_button("📤 旅程を保存・共有", share_content, file_name="my_trip_plan.txt")

    if st.button("🏠 ホームへ戻る"):
        st.session_state.clear(); st.session_state.step = "input"; st.rerun()
