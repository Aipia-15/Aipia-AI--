import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

PREFECTURES = [""] + ["北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県", "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県", "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県", "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県", "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"]

# デザイン（CSS）
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&display=swap');
    .stApp { background-color: #FBF9F7; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    .header-container { text-align: center; padding: 25px 0; border-bottom: 2px solid #D4AF37; background: #FFF; margin-bottom: 30px; }
    .spot-card { background: #FFF; border: 1px solid #E0D8C3; border-radius: 15px; padding: 20px; margin-bottom: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); }
    .line-button { background-color: #06C755; color: white !important; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 10px; }
    .plan-text { white-space: pre-wrap; line-height: 1.8; background: #FFF; padding: 20px; border: 1px solid #D4AF37; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# セッション状態の初期化
if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}
if "edit_mode" not in st.session_state: st.session_state.edit_mode = False

st.markdown('<div class="header-container"><h1 style="letter-spacing:10px; font-family:serif; margin:0;">Aipia</h1><p style="color:#D4AF37; margin:0;">- AI Executive Travel Concierge -</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力 ---
if st.session_state.step == "input":
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1: dep_place = st.text_input("🛫 出発地", value="新宿駅")
    with c2: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now() + timedelta(days=1)))
    with c3: dep_time = st.time_input("🕔 出発時刻", value=datetime.strptime("08:00", "%H:%M").time())

    c4, c5 = st.columns(2) # 都道府県と市区町村の横並び
    with c4: pref = st.selectbox("📍 目的地（都道府県）", PREFECTURES)
    with c5: city = st.text_input("🏠 目的地（市区町村・エリア）")

    c6, c7 = st.columns([3, 1])
    with c6: keyword = st.text_input("🔍 旅のテーマ・キーワード（例：歴史ある温泉街、絶景の滝）")
    with c7: budget = st.number_input("💰 予算/人", 5000, 500000, 50000)

    if st.button("⚜️ 10個の厳選スポットをリサーチする", use_container_width=True, type="primary"):
        if not pref: st.error("都道府県を選択してください"); st.stop()
        st.session_state.form_data = {"dep": dep_place, "dep_time": dep_time, "dest": f"{pref}{city}", "budget": budget}
        
        with st.spinner("実在するスポット10件を解析中..."):
            prompt = f"""目的地「{pref}{city}」で実在するスポットを必ず10件挙げよ。
            形式：名称|詳細な場所解説(200字以上)|費用|バリアフリー情報|駐車場の有無|Googleマップ検索URL
            ※嘘の情報は厳禁。実在する施設のみ。"""
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
            lines = [l.strip() for l in res.choices[0].message.content.split('\n') if '|' in l]
            st.session_state.found_spots = []
            for l in lines[:10]:
                p = l.split('|')
                if len(p) >= 6:
                    st.session_state.found_spots.append({"name": p[0], "desc": p[1], "fee": p[2], "bf": p[3], "park": p[4], "url": p[5]})
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: 10スポット表示 ---
elif st.session_state.step == "select_spots":
    st.markdown(f"### 📍 {st.session_state.form_data['dest']} の厳選スポット（10選）")
    for i, spot in enumerate(st.session_state.found_spots):
        with st.container():
            col_img, col_txt = st.columns([1, 3])
            with col_img:
                st.image(f"https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?q=80&w=400", use_column_width=True)
            with col_txt:
                st.markdown(f"#### [{spot['name']}]({spot['url']})")
                st.write(spot['desc'])
                st.markdown(f"💰 {spot['fee']} | ♿ {spot['bf']} | 🚗 {spot['park']}")
                if st.checkbox("このスポットを旅程に採用", key=f"sel_{i}"):
                    if spot['name'] not in st.session_state.selected_spots: st.session_state.selected_spots.append(spot['name'])
        st.divider()

    if st.button("✅ 5通りのプランを生成する", use_container_width=True, type="primary"):
        st.session_state.step = "final_plan"; st.rerun()

# --- STEP 3: 5プラン生成・編集・共有 ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plans:
        with st.spinner("詳細な5つのプラン（ホテル・改行込）を作成中..."):
            for label in ["Plan A (王道)", "Plan B (穴場)", "Plan C (ゆったり)", "Plan D (アクティブ)", "Plan E (グルメ)"]:
                prompt = f"""{st.session_state.form_data['dep']}を{st.session_state.form_data['dep_time']}に出発。
                {st.session_state.form_data['dest']}周辺のホテル・旅館宿泊を必ず含めろ。
                採用スポット：{st.session_state.selected_spots}。
                各スポットには詳細な滞在時間と改行を入れ、ホテルの予約検索用URLも末尾に付けろ。"""
                res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
                st.session_state.final_plans[label] = res.choices[0].message.content

    chosen = st.radio("プランを比較", list(st.session_state.final_plans.keys()), horizontal=True)

    if not st.session_state.edit_mode:
        st.markdown(f"### {chosen}")
        st.markdown(f'<div class="plan-text">{st.session_state.final_plans[chosen]}</div>', unsafe_allow_html=True)
        if st.button("✏️ このプランを編集（削除・時間調整）"):
            st.session_state.edit_mode = True; st.rerun()
    else:
        edited_text = st.text_area("プランを自由に編集してください（改行も反映されます）", value=st.session_state.final_plans[chosen], height=500)
        if st.button("💾 編集内容を確定"):
            st.session_state.final_plans[chosen] = edited_text
            st.session_state.edit_mode = False; st.rerun()

    st.divider()
    # LINE共有
    share_msg = f"【Aipia】私の旅行プラン - {chosen}\n\n" + st.session_state.final_plans[chosen]
    line_url = f"https://line.me/R/msg/text/?{urllib.parse.quote(share_msg)}"
    st.markdown(f'<a href="{line_url}" target="_blank" class="line-button">LINEで旅程を共有する</a>', unsafe_allow_html=True)

    if st.button("🏠 ホームへ戻る"):
        st.session_state.clear(); st.session_state.step = "input"; st.rerun()
