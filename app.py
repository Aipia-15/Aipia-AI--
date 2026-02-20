import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse
import time

# 1. ページ基本設定
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

PREFECTURES = [""] + ["北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県", "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県", "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県", "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県", "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"]

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    .header-container { text-align: center; padding: 30px 0; border-bottom: 2px solid #D4AF37; background: #FFF; margin-bottom: 30px; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 3.5rem; color: #111; letter-spacing: 5px; margin: 0; }
    .catalog-card { background: #FFF; border: 1px solid #E0D8C3; border-radius: 12px; padding: 20px; margin-bottom: 15px; }
    .status-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; margin-right: 10px; background: #F1ECE4; color: #5D4037; font-weight: bold; }
    .plan-viewer { background: #FFF; border-radius: 15px; padding: 30px; border: 1px solid #D4AF37; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}
if "edit_mode" not in st.session_state: st.session_state.edit_mode = False

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力 (レイアウト維持・日程範囲) ---
if st.session_state.step == "input":
    st.markdown('<h3 style="text-align:center;">01. Travel Profile</h3>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1: dep_place = st.text_input("🛫 出発地点", value="新宿駅")
    with c2: date_range = st.date_input("📅 旅行日程", value=(datetime.now(), datetime.now() + timedelta(days=1)))
    with c3: dep_time = st.time_input("🕔 出発時刻", value=datetime.strptime("08:00", "%H:%M").time())

    c4, c5 = st.columns(2) # 横並び
    with c4: pref = st.selectbox("📍 目的地（都道府県）", PREFECTURES, index=0)
    with c5: city = st.text_input("🏠 市区町村・エリア", placeholder="例：松本市、伊勢市など")

    c6, c7, c8 = st.columns([1, 2, 1])
    with c6: keyword = st.text_input("🔍 自由キーワード")
    with c7: purposes = st.multiselect("✨ 旅の目的（タグ）", ["秘境探索", "美食・地酒", "歴史・文化", "温泉・癒やし", "アクティビティ"], default=["秘境探索"])
    with c8: budget = st.number_input("💰 予算/人(円)", 5000, 1000000, 50000, step=5000)

    c9, c10 = st.columns(2)
    with c9: adults = st.number_input("大人", 1, 20, 2)
    with c10: kids = st.number_input("小人", 0, 20, 0)

    if st.button("⚜️ カタログを生成する", use_container_width=True, type="primary"):
        if not pref: st.error("都道府県を選択してください"); st.stop()
        st.session_state.form_data = {"dep": dep_place, "dep_time": dep_time, "dest": f"{pref}{city}", "budget": budget, "purposes": purposes, "days": 2}
        
        with st.spinner("スポット情報を強制リサーチ中..."):
            prompt = f"目的地「{pref}{city}」周辺で「{keyword}」に関連し「{purposes}」に合う実在スポットを必ず5件出せ。形式：名称|解説|費用|人気|バリアフリー|駐車場|周辺秘境|周辺食事"
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
            lines = [l.strip() for l in res.choices[0].message.content.split('\n') if '|' in l]
            st.session_state.found_spots = []
            for l in lines[:5]:
                p = l.split('|')
                if len(p) >= 8: st.session_state.found_spots.append({"name": p[0], "desc": p[1], "fee": p[2], "pop": p[3], "bf": p[4], "park": p[5], "sub_h": p[6], "sub_f": p[7]})
            if not st.session_state.found_spots: st.error("スポットが見つかりませんでした。条件を変えてください。"); st.stop()
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: 選択 ---
elif st.session_state.step == "select_spots":
    st.markdown(f"### 📍 {st.session_state.form_data['dest']} 厳選カタログ")
    for i, spot in enumerate(st.session_state.found_spots):
        st.markdown(f"""<div class="catalog-card"><b>{spot['name']}</b><br><small>{spot['desc']}</small><br>
        <span class="status-badge">💰 {spot['fee']}</span><span class="status-badge">♿ {spot['bf']}</span><span class="status-badge">🚗 {spot['park']}</span></div>""", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        if c1.checkbox(f"「{spot['name']}」を採用", key=f"m_{i}"): st.session_state.selected_spots.append(spot['name'])
        if c2.checkbox(f"周辺秘境：{spot['sub_h']}", key=f"h_{i}"): st.session_state.selected_spots.append(spot['sub_h'])
        if c3.checkbox(f"周辺食事：{spot['sub_f']}", key=f"f_{i}"): st.session_state.selected_spots.append(spot['sub_f'])
    
    if st.button("✅ 旅程を5つのプランで生成する", use_container_width=True, type="primary"):
        st.session_state.step = "final_plan"; st.rerun()

# --- STEP 3: プラン表示・編集 ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plans:
        with st.spinner("5つのプラン（ホテル込）を編纂中..."):
            for label in ["Plan A", "Plan B", "Plan C", "Plan D", "Plan E"]:
                prompt = f"{st.session_state.form_data['dep']}を{st.session_state.form_data['dep_time']}に出発。ホテル宿泊を必ず含めろ。スポット：{st.session_state.selected_spots}。形式：時間|予定"
                res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
                items = []
                for l in res.choices[0].message.content.split('\n'):
                    if '|' in l:
                        t, a = l.split('|', 1)
                        items.append({"time": t.strip(), "action": a.strip()})
                st.session_state.final_plans[label] = items

    st.markdown("### 🗓️ 旅のしおり - 5つの提案")
    chosen = st.radio("プランを選択してください", list(st.session_state.final_plans.keys()), horizontal=True)
    
    # 閲覧モード
    if not st.session_state.edit_mode:
        st.markdown(f'<div class="plan-viewer"><h4>{chosen}</h4>', unsafe_allow_html=True)
        for item in st.session_state.final_plans[chosen]:
            st.write(f"**{item['time']}** : {item['action']}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("✏️ このプランを編集する"):
            st.session_state.edit_mode = True; st.rerun()
    
    # 編集モード
    else:
        st.markdown("#### 🛠️ プラン編集")
        new_items = []
        for i, item in enumerate(st.session_state.final_plans[chosen]):
            c_t, c_a, c_d = st.columns([1, 4, 1])
            t = c_t.text_input("時間", value=item['time'], key=f"ed_t_{i}")
            a = c_a.text_input("予定", value=item['action'], key=f"ed_a_{i}")
            if not c_d.button("🗑️", key=f"ed_d_{i}"):
                new_items.append({"time": t, "action": a})
        
        if st.button("💾 編集を保存して戻る"):
            st.session_state.final_plans[chosen] = new_items
            st.session_state.edit_mode = False; st.rerun()

    st.divider()
    if st.button("📤 旅程をテキスト出力（共有用）"):
        txt = "\n".join([f"{x['time']} : {x['action']}" for x in st.session_state.final_plans[chosen]])
        st.download_button("ファイルをダウンロード", txt, file_name="trip.txt")
