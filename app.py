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
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    .header-container { text-align: center; padding: 20px 0; border-bottom: 2px solid #D4AF37; background: #FFF; margin-bottom: 30px; }
    .spot-card { background: #FFF; border: 1px solid #E0D8C3; border-radius: 12px; padding: 15px; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
    .status-badge { display: inline-block; padding: 3px 10px; border-radius: 15px; font-size: 0.8rem; margin: 3px; background: #F1ECE4; color: #5D4037; font-weight: bold; }
    .plan-box { background: #FFF; padding: 25px; border: 1px solid #D4AF37; border-radius: 15px; }
    </style>
""", unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}
if "edit_mode" not in st.session_state: st.session_state.edit_mode = False

st.markdown('<div class="header-container"><h1 style="font-family:serif; letter-spacing:8px;">Aipia</h1></div>', unsafe_allow_html=True)

# --- STEP 1: 入力 ---
if st.session_state.step == "input":
    st.markdown('<h3 style="text-align:center;">Travel Profile</h3>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1: dep_place = st.text_input("🛫 出発地点", value="新宿駅")
    with c2: date_range = st.date_input("📅 旅行日程", value=(datetime.now(), datetime.now() + timedelta(days=1)))
    with c3: dep_time = st.time_input("🕔 出発時刻", value=datetime.strptime("08:00", "%H:%M").time())

    c4, c5 = st.columns(2) # 都道府県・市区町村 横並び
    with c4: pref = st.selectbox("📍 目的地（都道府県）", PREFECTURES)
    with c5: city = st.text_input("🏠 市区町村エリア")

    c6, c7, c8 = st.columns([1, 2, 1])
    with c6: keyword = st.text_input("🔍 自由キーワード")
    with c7: purposes = st.multiselect("✨ 目的", ["秘境探索", "美食", "温泉", "歴史"], default=["秘境探索"])
    with c8: budget = st.number_input("💰 予算/人", 5000, 500000, 50000)

    if st.button("⚜️ 10個の厳選スポットをリサーチする", use_container_width=True, type="primary"):
        if not pref: st.error("都道府県を選んでください"); st.stop()
        st.session_state.form_data = {"dep": dep_place, "dep_time": dep_time, "dest": f"{pref}{city}", "budget": budget}
        with st.spinner("日本全国のデータベースから10件を強制抽出中..."):
            prompt = f"{pref}{city}周辺で実在スポットを必ず「10件」出せ。形式：名称|詳細な場所説明(200字程度)|費用|バリアフリー|駐車場|画像キーワード"
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
            lines = [l.strip() for l in res.choices[0].message.content.split('\n') if '|' in l]
            st.session_state.found_spots = []
            for l in lines[:10]:
                p = l.split('|')
                if len(p) >= 6:
                    st.session_state.found_spots.append({"name": p[0], "desc": p[1], "fee": p[2], "bf": p[3], "park": p[4], "img": p[5]})
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: スポットカタログ (10個表示) ---
elif st.session_state.step == "select_spots":
    st.markdown(f"### 📍 {st.session_state.form_data['dest']} 周辺スポット (10選)")
    
    for i, spot in enumerate(st.session_state.found_spots):
        with st.container():
            col_img, col_txt = st.columns([1, 2])
            with col_img:
                # プレースホルダー画像（Unsplashを使用）
                img_url = f"https://images.unsplash.com/photo-1506744038136-46273834b3fb?q=80&w=400&auto=format&fit=crop" # 実際はキーワードで可変
                st.image(img_url, caption=spot['name'], use_column_width=True)
            with col_txt:
                st.markdown(f"#### {spot['name']}")
                st.write(spot['desc'])
                st.markdown(f'<span class="status-badge">💰 {spot['fee']}</span><span class="status-badge">♿ {spot['bf']}</span><span class="status-badge">🚗 {spot['park']}</span>', unsafe_allow_html=True)
                if st.checkbox("このスポットを旅程に入れる", key=f"sel_{i}"):
                    if spot['name'] not in st.session_state.selected_spots: st.session_state.selected_spots.append(spot['name'])
        st.divider()

    if st.button("✅ 確定して5つのプランを作成", use_container_width=True, type="primary"):
        st.session_state.step = "final_plan"; st.rerun()

# --- STEP 3: 5プラン表示・編集 ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plans:
        with st.spinner("5通りの極上プランを編纂中..."):
            for label in ["Plan A", "Plan B", "Plan C", "Plan D", "Plan E"]:
                prompt = f"{st.session_state.form_data['dep']}を{st.session_state.form_data['dep_time']}に出発。ホテル宿泊を必ず含む旅程。スポット：{st.session_state.selected_spots}。形式：時間|予定"
                res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
                items = [{"time": l.split('|')[0].strip(), "action": l.split('|')[1].strip()} for l in res.choices[0].message.content.split('\n') if '|' in l]
                st.session_state.final_plans[label] = items

    st.markdown("### 🗓️ 旅のしおり - 5つの提案")
    chosen = st.radio("プラン選択", list(st.session_state.final_plans.keys()), horizontal=True)
    
    if not st.session_state.edit_mode:
        st.markdown(f'<div class="plan-box"><h4>{chosen}</h4>', unsafe_allow_html=True)
        for item in st.session_state.final_plans[chosen]:
            st.write(f"**{item['time']}** : {item['action']}")
        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("✏️ プランを細かく調整（編集）"): st.session_state.edit_mode = True; st.rerun()
    else:
        st.markdown("#### 🛠️ 自由編集")
        new_items = []
        for i, item in enumerate(st.session_state.final_plans[chosen]):
            c_t, c_a, c_d = st.columns([1, 4, 1])
            t = c_t.text_input("時間", item['time'], key=f"t_{i}")
            a = c_a.text_input("予定", item['action'], key=f"a_{i}")
            if not c_d.button("🗑️", key=f"d_{i}"): new_items.append({"time": t, "action": a})
        if st.button("💾 保存"): st.session_state.final_plans[chosen] = new_items; st.session_state.edit_mode = False; st.rerun()

    st.divider()
    if st.button("📤 共有用テキストを出力"):
        txt = "\n".join([f"{x['time']} : {x['action']}" for x in st.session_state.final_plans[chosen]])
        st.download_button("ダウンロード", txt, file_name="plan.txt")
