import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse
import time

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

PREFECTURES = [""] + ["北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県", "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県", "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県", "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県", "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"]

# CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    .catalog-card { background: #FFF; border: 1px solid #E0D8C3; border-radius: 12px; padding: 20px; margin-bottom: 15px; }
    .status-badge { display: inline-block; padding: 3px 10px; border-radius: 15px; font-size: 0.8rem; margin: 3px; background: #F1ECE4; color: #5D4037; font-weight: bold; }
    .plan-box { background: #FFF; border-left: 5px solid #D4AF37; padding: 20px; margin-bottom: 10px; border-radius: 5px; }
    .time-txt { color: #D4AF37; font-weight: bold; font-size: 1.1rem; }
    </style>
""", unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "plan_data" not in st.session_state: st.session_state.plan_data = []

# --- STEP 1: 入力（レイアウト適正化） ---
if st.session_state.step == "input":
    st.markdown("<h2 style='text-align:center;'>Aipia 旅行プロファイル</h2>", unsafe_allow_html=True)
    
    # 1列目：出発の基本
    r1_c1, r1_c2, r1_c3 = st.columns([2, 1, 1])
    with r1_c1: dep_place = st.text_input("🛫 出発地点", value="新宿駅")
    with r1_c2: dep_date = st.date_input("📅 出発日")
    with r1_c3: dep_time = st.time_input("🕔 出発時刻", value=datetime.strptime("08:00", "%H:%M").time())

    # 2列目：目的地（横並び修正）
    r2_c1, r2_c2 = st.columns(2)
    with r2_c1: pref = st.selectbox("📍 目的地（都道府県）", PREFECTURES)
    with r2_c2: city = st.text_input("🏠 市区町村エリア（詳細）", placeholder="例：松本市安曇、奥多摩町など")

    # 3列目：条件
    r3_c1, r3_c2, r3_c3 = st.columns(3)
    with r3_c1: keyword = st.text_input("🔍 キーワード")
    with r3_c2: purposes = st.multiselect("✨ 目的", ["秘境探索", "美食", "温泉", "歴史"], default=["秘境探索"])
    with r3_c3: budget = st.number_input("💰 予算/人", 5000, 500000, 50000, step=5000)

    # 4列目：人数
    r4_c1, r4_c2 = st.columns(2)
    with r4_c1: adults = st.number_input("大人", 1, 10, 2)
    with r4_c2: kids = st.number_input("小人", 0, 10, 0)

    if st.button("⚜️ この条件でスポットを探す", use_container_width=True, type="primary"):
        if not pref: st.error("都道府県を選択してください"); st.stop()
        st.session_state.form_data = {"dep": dep_place, "dep_time": dep_time, "dest": f"{pref}{city}", "budget": budget, "purposes": purposes}
        
        with st.spinner("実在するスポットを強制リサーチ中..."):
            # プロンプトの厳格化
            prompt = f"目的地{pref}{city}周辺で実在スポットを必ず5件。形式：名称|解説|費用|人気|混雑|バリアフリー|駐車場|周辺秘境|周辺食事"
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
            lines = [l.strip() for l in res.choices[0].message.content.split('\n') if '|' in l]
            
            st.session_state.found_spots = []
            for l in lines[:5]:
                p = l.split('|')
                if len(p) >= 9:
                    st.session_state.found_spots.append({"name": p[0], "desc": p[1], "fee": p[2], "pop": p[3], "bf": p[5], "park": p[6], "sub_h": p[7], "sub_f": p[8]})
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: 選択 ---
elif st.session_state.step == "select_spots":
    st.markdown(f"### 📍 {st.session_state.form_data['dest']} 周辺カタログ")
    for i, spot in enumerate(st.session_state.found_spots):
        with st.container():
            st.markdown(f"""<div class="catalog-card"><b>{spot['name']}</b><br><small>{spot['desc']}</small><br>
            <span class="status-badge">♿ {spot['bf']}</span><span class="status-badge">🚗 {spot['park']}</span><span class="status-badge">💰 {spot['fee']}</span></div>""", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            if c1.checkbox(f"「{spot['name']}」を採用", key=f"m_{i}"): st.session_state.selected_spots.append(spot['name'])
            if c2.checkbox(f"秘境：{spot['sub_h']}", key=f"h_{i}"): st.session_state.selected_spots.append(spot['sub_h'])
            if c3.checkbox(f"食事：{spot['sub_f']}", key=f"f_{i}"): st.session_state.selected_spots.append(spot['sub_f'])
    
    if st.button("✅ スポットを確定してプランを作る", type="primary", use_container_width=True):
        st.session_state.step = "final_plan"; st.rerun()

# --- STEP 3: 編集・再構成・共有 ---
elif st.session_state.step == "final_plan":
    if not st.session_state.plan_data:
        # 構造化された旅程をAIに作らせる
        prompt = f"{st.session_state.form_data['dep_time']}出発。ホテル宿泊必須。{st.session_state.selected_spots}を含む旅程を「時間|行動」の形式で出せ。"
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
        for l in res.choices[0].message.content.split('\n'):
            if '|' in l:
                t, act = l.split('|', 1)
                st.session_state.plan_data.append({"time": t.strip(), "action": act.strip()})

    st.markdown("### 🗓️ あなたの旅行プラン（編集モード）")
    st.info("💡 左側の入力欄で時間を変更したり、ゴミ箱ボタンで場所を削ったりできます。")

    new_plan = []
    for i, item in enumerate(st.session_state.plan_data):
        c_time, c_act, c_del = st.columns([1, 4, 1])
        with c_time:
            edit_time = st.text_input("時間", value=item['time'], key=f"t_ed_{i}")
        with c_act:
            edit_act = st.text_input("予定内容", value=item['action'], key=f"a_ed_{i}")
        with c_del:
            if not st.button("🗑️ 削除", key=f"del_{i}"):
                new_plan.append({"time": edit_time, "action": edit_act})
    
    st.session_state.plan_data = new_plan

    st.divider()
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        if st.button("🔄 全て再生成（AIに任せる）"):
            st.session_state.plan_data = []; st.rerun()
    with col_f2:
        # 共有機能：現在の編集済みデータをテキスト化
        final_text = "\n".join([f"{x['time']} - {x['action']}" for x in st.session_state.plan_data])
        st.download_button("📤 旅程をテキスト保存/共有", final_text, file_name="trip_plan.txt")

    if st.button("🏠 最初に戻る"):
        st.session_state.clear(); st.session_state.step = "input"; st.rerun()
