import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse

# 1. ページ設定とGroqクライアント（高精度モデル指定）
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
MODEL = "llama-3.3-70b-specdec" # 質を落とさないための高推論モデル

PREFECTURES = [""] + ["北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県", "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県", "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県", "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県", "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"]

# CSS定義
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    .header-container { text-align: center; padding: 30px 0; border-bottom: 2px solid #D4AF37; background: #FFF; margin-bottom: 30px; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 3.5rem; color: #111; letter-spacing: 5px; margin: 0; }
    .aipia-sub { color: #D4AF37; font-weight: bold; letter-spacing: 3px; font-size: 0.9rem; margin-top: -10px; }
    .spot-card { background: white; border-radius: 12px; padding: 20px; border: 1px solid #E0D8C3; margin-bottom: 20px; }
    .line-button { background-color: #06C755; color: white !important; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; }
    .day-header { background: #111; color: #D4AF37; padding: 5px 15px; border-radius: 5px; margin: 20px 0 10px; }
    </style>
""", unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}
if "edit_mode" not in st.session_state: st.session_state.edit_mode = False

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">- AI Executive Concierge -</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力 ---
if st.session_state.step == "input":
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1: dep_place = st.text_input("🛫 出発地点", value="新宿駅")
    with c2: date_range = st.date_input("📅 旅行日程", value=(datetime.now(), datetime.now() + timedelta(days=1)))
    with c3: dep_time = st.time_input("🕔 出発時刻", value=datetime.strptime("08:00", "%H:%M").time())

    c4, c5 = st.columns(2)
    with c4: pref = st.selectbox("📍 目的地（都道府県）", PREFECTURES)
    with c5: city = st.text_input("🏠 目的地（詳細エリア）")

    c6, c7, c8 = st.columns([1, 2, 1])
    with c6: keyword = st.text_input("🔍 キーワード")
    with c7: purposes = st.multiselect("✨ 目的", ["秘境探索", "美食", "温泉", "歴史"], default=["秘境探索"])
    with c8: budget = st.number_input("💰 予算/人", 5000, 500000, 50000)

    c9, c10 = st.columns(2)
    with c9: adults = st.number_input("大人 (中学生以上)", 1, 20, 2)
    with c10: kids = st.number_input("小人 (小学生以下)", 0, 20, 0)

    if st.button("⚜️ 10個の厳選スポットをリサーチする", use_container_width=True, type="primary"):
        if not pref: st.error("都道府県を選んでください"); st.stop()
        days = (date_range[1] - date_range[0]).days + 1 if isinstance(date_range, tuple) and len(date_range) == 2 else 1
        st.session_state.form_data = {"dep": dep_place, "dep_time": dep_time, "dest": f"{pref}{city}", "budget": budget, "days": days}
        
        # 最初の10個取得
        prompt = f"実在する{pref}{city}周辺の観光スポットを10件出せ。形式：名称|詳細説明|予算|バリアフリー|駐車場|住所"
        res = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}])
        st.session_state.found_spots = [l.split('|') for l in res.choices[0].message.content.split('\n') if '|' in l][:10]
        st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: スポットカタログ（Moreで10個ずつ追加） ---
elif st.session_state.step == "select_spots":
    st.markdown(f"### 📍 {st.session_state.form_data['dest']} スポットカタログ")
    
    for i, s in enumerate(st.session_state.found_spots):
        with st.container():
            col1, col2 = st.columns([1, 3])
            col1.image(f"https://source.unsplash.com/featured/?{urllib.parse.quote(s[0])}", use_column_width=True)
            with col2:
                st.markdown(f"#### {s[0]} <small>({s[5]})</small>", unsafe_allow_html=True)
                st.write(s[1]); st.markdown(f"💰 {s[2]} | ♿ {s[3]} | 🚗 {s[4]}")
                if st.checkbox("採用", key=f"sel_{i}"):
                    if s[0] not in st.session_state.selected_spots: st.session_state.selected_spots.append(s[0])
        st.divider()

    c_m1, c_m2 = st.columns(2)
    with c_m1:
        if st.button("➕ More（さらに10個リサーチ）", use_container_width=True):
            prompt = f"実在する{st.session_state.form_data['dest']}周辺の、まだ挙げていないスポットをさらに10件出せ。形式：名称|詳細説明|予算|バリアフリー|駐車場|住所"
            res = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}])
            new_spots = [l.split('|') for l in res.choices[0].message.content.split('\n') if '|' in l][:10]
            st.session_state.found_spots.extend(new_spots); st.rerun()
    with c_m2:
        if st.button("✅ プラン生成（5つ）", use_container_width=True, type="primary"):
            st.session_state.step = "final_plan"; st.rerun()

# --- STEP 3: 5つのプラン生成（2日目以降・ホテル死守） ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plans:
        with st.spinner(f"{st.session_state.form_data['days']}日間の全日程プランを5パターン作成中..."):
            for label in ["Plan A", "Plan B", "Plan C", "Plan D", "Plan E"]:
                prompt = f"""
                【重要】{st.session_state.form_data['days']}日間の旅程をすべて作成せよ。
                出発：{st.session_state.form_data['dep']} {st.session_state.form_data['dep_time']}
                採用スポット：{st.session_state.selected_spots}
                条件：
                1. 各日の日程を「1日目」「2日目」と明示して改行して書くこと。
                2. 1日目の夜には、必ず{st.session_state.form_data['dest']}周辺の具体的な宿泊施設(ホテル名)を組み込むこと。
                3. 形式は「時間 | 予定」とし、非常に細かく、読みやすく改行を入れること。
                """
                res = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}])
                st.session_state.final_plans[label] = res.choices[0].message.content

    chosen = st.radio("プラン切替", list(st.session_state.final_plans.keys()), horizontal=True)

    if not st.session_state.edit_mode:
        st.markdown(f"### {chosen}")
        st.markdown(f'<div style="white-space: pre-wrap; background:white; padding:20px; border-radius:10px;">{st.session_state.final_plans[chosen]}</div>', unsafe_allow_html=True)
        if st.button("✏️ 編集する"): st.session_state.edit_mode = True; st.rerun()
    else:
        edited = st.text_area("内容を編集（2日目以降やホテルも自由に調整可能）", value=st.session_state.final_plans[chosen], height=600)
        if st.button("💾 保存"): st.session_state.final_plans[chosen] = edited; st.session_state.edit_mode = False; st.rerun()

    st.divider()
    share_txt = f"【Aipia】旅行プラン - {chosen}\n\n{st.session_state.final_plans[chosen]}"
    st.markdown(f'<a href="https://line.me/R/msg/text/?{urllib.parse.quote(share_txt)}" class="line-button">LINEで全日程を共有</a>', unsafe_allow_html=True)

    if st.button("🏠 最初に戻る"): st.session_state.clear(); st.session_state.step = "input"; st.rerun()
