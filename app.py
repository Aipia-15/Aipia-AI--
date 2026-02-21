import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import json
import re
import urllib.parse

# --- 1. 基本設定 ---
st.set_page_config(layout="wide", page_title="Aipia")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

PREFECTURES = [""] + ["北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県", "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県", "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県", "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県", "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"]

def call_groq_safe(prompt):
    for model_id in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]:
        try:
            res = client.chat.completions.create(model=model_id, messages=[{"role": "user", "content": prompt}], temperature=0.5, max_tokens=3000)
            if res.choices[0].message.content: return res.choices[0].message.content
        except: continue
    return None

def parse_json_safely(text):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match: return None
        json_str = match.group().replace('\n', ' ').replace('\r', '')
        return json.loads(json_str)
    except: return None

# --- 2. セッション管理 ---
keys = ["step", "found_spots", "selected_spots", "plans", "confirmed", "more_count", "form_data", "hotel_data"]
for k in keys:
    if k not in st.session_state:
        if k == "step": st.session_state[k] = "input"
        elif k in ["found_spots", "selected_spots", "plans"]: st.session_state[k] = []
        else: st.session_state[k] = None

# --- 3. デザイン定義 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&display=swap');
    .stApp { background-color: #FBF9F7; font-family: 'Noto Serif JP', serif; }
    .header-container { text-align: center; padding: 25px 0; border-bottom: 2px solid #D4AF37; background: #FFF; margin-bottom: 20px; }
    .aipia-logo { font-size: 2.8rem; color: #111; letter-spacing: 4px; margin: 0; font-weight: bold; }
    .aipia-sub { color: #D4AF37; font-weight: bold; font-size: 0.9rem; margin-top: -5px; }
    .spot-card { background: white; padding: 18px; border-radius: 12px; border-left: 6px solid #D4AF37; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    .time-step { background-color: #FFF; padding: 20px; border-radius: 10px; margin: 15px 0; border: 1px solid #E0E0E0; position: relative; border-left: 5px solid #1976D2; }
    .aipia-badge { position: absolute; top: -12px; right: 10px; background: #FFD700; color: #000; padding: 4px 12px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; border: 1px solid #B8860B; }
    .ai-advice-box { background-color: #E8F5E9; border-left: 5px solid #2E7D32; padding: 15px; border-radius: 4px; margin: 15px 0; font-size: 0.9rem; }
    .reserve-btn { display: inline-block; padding: 12px 24px; margin: 8px; border-radius: 6px; color: white !important; text-decoration: none; font-weight: bold; text-align: center; min-width: 150px; }
    .url-summary-box { background: #F0F4F8; padding: 15px; border-radius: 8px; margin-top: 15px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">-AIが創る、秘境への旅行プラン-</p></div>', unsafe_allow_html=True)

# --- STEP 1: ホーム画面 ---
if st.session_state.step == "input":
    col_k1, col_k2 = st.columns([3, 1])
    with col_k1: keyword = st.text_input("🔍 探したいキーワード", placeholder="例：絶景の滝、地元の名店、混雑を避けた温泉")
    with col_k2: transport = st.radio("🚃 交通手段", ["公共交通機関", "レンタカー・自家用車"], horizontal=True)

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1: dep_place = st.text_input("🛫 出発地点", value="新宿駅")
    with col2: date_range = st.date_input("📅 旅行日程", value=(datetime.now(), datetime.now() + timedelta(days=1)))
    with col3: dep_time = st.time_input("🕔 出発時刻", value=datetime.strptime("08:00", "%H:%M").time())

    col4, col5, col6 = st.columns(3)
    with col4: pref = st.selectbox("📍 都道府県", PREFECTURES)
    with col5: city = st.text_input("🏠 市区町村（任意）")
    with col6: budget = st.number_input("💰 予算/人", 5000, 500000, 50000)

    col7, col8, col9 = st.columns([2, 1, 1])
    with col7: purposes = st.multiselect("✨ 目的", ["秘境探索", "美食", "温泉", "歴史", "絶景", "バリアフリー"], default=["秘境探索"])
    with col8: adults = st.number_input("大人", 1, 20, 2)
    with col9: kids = st.number_input("小人", 0, 20, 0)
    
    walk_speed = st.select_slider("🚶‍♂️ 歩く速度", options=["ゆっくり", "普通", "早歩き"], value="普通")

    if st.button("⚜️ 秘境リサーチを開始する", use_container_width=True, type="primary"):
        st.session_state.form_data = {"dep": dep_place, "dest": f"{pref}{city}", "transport": transport, "speed": walk_speed, "purposes": purposes}
        res = call_groq_safe(f"{pref}{city}周辺で{keyword}の実在スポット10件。名称|解説|住所|公式サイトURL 形式。")
        if res:
            st.session_state.found_spots = [l.split('|') for l in res.strip().split('\n') if '|' in l]
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: スポット選択 ---
elif st.session_state.step == "select_spots":
    st.subheader(f"📍 {st.session_state.form_data['dest']} のリサーチ結果")
    for i, s in enumerate(st.session_state.found_spots):
        if len(s) < 2: continue
        st.markdown(f'<div class="spot-card"><b>{s[0]}</b><br><small>{s[1]}</small></div>', unsafe_allow_html=True)
        if st.checkbox(f"この場所を旅程に加える：{s[0]}", key=f"chk_{i}"):
            if s[0] not in st.session_state.selected_spots: st.session_state.selected_spots.append(s[0])
    
    col_more, col_next = st.columns(2)
    with col_more:
        if st.button("➕ スポットをさらに追加"):
            res = call_groq_safe(f"{st.session_state.form_data['dest']}の別の実在スポットを10件。名称|解説|住所|URL")
            if res:
                st.session_state.found_spots.extend([l.split('|') for l in res.strip().split('\n') if '|' in l])
                st.rerun()
    with col_next:
        if st.button("✅ 宿泊・詳細設定へ", type="primary"): st.session_state.step = "hotel_survey"; st.rerun()

# --- STEP 3: ホテル・バリアフリー設定 ---
elif st.session_state.step == "hotel_survey":
    st.subheader("🏨 宿泊と設備の最終希望")
    h_type = st.selectbox("宿泊スタイル", ["老舗旅館（実在）", "ラグジュアリーホテル", "バリアフリー完備の宿"])
    h_barrier = st.multiselect("必要なバリアフリー設備", ["段差なし", "車椅子対応トイレ", "エレベーター至近", "手すり完備"])
    
    if st.button("✨ 5つの詳細プランを生成", type="primary"):
        st.session_state.hotel_data = {"type": h_type, "barrier": h_barrier}
        st.session_state.step = "plan_gen"; st.rerun()

# --- STEP 4: プラン表示 (5案生成) ---
elif st.session_state.step == "plan_gen":
    if not st.session_state.plans:
        p_bar = st.progress(0)
        p_text = st.empty()
        
        temp_plans = []
        for i in range(5):
            p_text.text(f"プラン案 {i+1}/5 を最適ルートで構築中...")
            prompt = f"""
            出発地:{st.session_state.form_data['dep']}, 目的地:{st.session_state.form_data['dest']}, 交通:{st.session_state.form_data['transport']}
            選択スポット:{st.session_state.selected_spots}, 宿泊:{st.session_state.hotel_data['type']}, 配慮:{st.session_state.hotel_data['barrier']}
            
            【指示】
            1. 交通ルートは「最短」かつ「乗り換えが少なく」「無理のない」現実的なものを組む。
            2. ホテルは必ず実在するものを1つ選び、名称と住所を明記。
            3. 選ばれていないが地域で評判の「食事処」をAIが厳選して1つ以上追加し 'is_recommended' を true にする。
            4. 訪れる各場所（食事処含む）の公式サイトURLまたは地図URLを必ず含める。
            5. 1日目・2日目の全日程を詳細に作成。
            
            {{'route_summary': '移動のポイント', 'ai_advice': 'AIからの秘境攻略アドバイス', 'hotel': 'ホテル名', 'hotel_address': '住所', 'days': [{{'label': '1日目', 'steps': [{{'time': '09:00', 'content': '内容', 'url': '公式サイト等URL', 'is_recommended': false}}]}}]}}
            """
            res = call_groq_safe(prompt)
            parsed = parse_json_safely(res)
            if parsed and parsed.get('days'): temp_plans.append(parsed)
            p_bar.progress((i + 1) * 20)
        
        st.session_state.plans = temp_plans
        p_text.empty()
        st.rerun()

    if st.session_state.plans:
        p_idx = st.sidebar.radio("プランの比較・切り替え", range(len(st.session_state.plans)), format_func=lambda x: f"プラン案 {x+1}")
        data = st.session_state.plans[p_idx]
        
        st.success(f"🚃 **ルートのポイント:** {data.get('route_summary')}")
        st.markdown(f'<div class="ai-advice-box"><b>💡 AIアドバイス:</b><br>{data.get("ai_advice")}</div>', unsafe_allow_html=True)

        st.info(f"🏨 **提案ホテル:** {data.get('hotel')} ({data.get('hotel_address')})")

        for day in data.get("days", []):
            st.markdown(f"#### 📅 {day['label']}")
            for step in day.get("steps", []):
                badge = '<div class="aipia-badge">AIが選びました！</div>' if step.get('is_recommended') else ''
                st.markdown(f"""
                <div class="time-step">
                    {badge}
                    <b>{step["time"]}</b><br>{step["content"]}<br>
                    <a href="{step['url']}" target="_blank" style="color:#1976D2; font-size:0.8rem;">🌐 公式サイト・詳細はこちら</a>
                </div>
                """, unsafe_allow_html=True)

        if st.button("🏆 この内容で確定する", type="primary", use_container_width=True): 
            st.session_state.confirmed = data; st.session_state.step = "share"; st.rerun()

# --- STEP 5: 確定共有と予約サイト ---
elif st.session_state.step == "share":
    plan = st.session_state.confirmed
    h_name = plan.get('hotel')
    q = urllib.parse.quote(h_name)
    
    st.balloons()
    st.header(f"✨ 確定した旅のしおり：{h_name}")
    
    # 予約リンク
    st.markdown("### 🏨 ホテルを予約する")
    col_r, col_j, col_i = st.columns(3)
    with col_r: st.markdown(f'<a href="https://search.rakuten.co.jp/search/mall/{q}/" target="_blank" class="reserve-btn" style="background:#bf0000;">楽天トラベル</a>', unsafe_allow_html=True)
    with col_j: st.markdown(f'<a href="https://www.jalan.net/keyword/{q}/" target="_blank" class="reserve-btn" style="background:#ff7a00;">じゃらん</a>', unsafe_allow_html=True)
    with col_i: st.markdown(f'<a href="https://www.ikyu.com/search/?keyword={q}" target="_blank" class="reserve-btn" style="background:#003567;">一休.com</a>', unsafe_allow_html=True)

    # 見やすいプランまとめ
    st.markdown("### 📋 旅程のまとめ")
    for d in plan['days']:
        with st.expander(f"📍 {d['label']} の詳細", expanded=True):
            for s in d['steps']:
                st.write(f"**{s['time']}** : {s['content']}")
                if "http" in s['url']: st.caption(f"リンク: {s['url']}")

    st.subheader("📱 LINE共有用テキスト")
    share_text = f"【Aipia 秘境への旅プラン】\n宿泊先：{h_name}\n"
    for d in plan['days']:
        share_text += f"\n{d['label']}\n"
        for s in d['steps']: share_text += f"・{s['time']} {s['content']}\n"
    st.text_area("以下の内容をコピーして共有してください", share_text, height=200)

    if st.button("🏠 最初から作成する"): 
        for k in keys: st.session_state[k] = "input" if k == "step" else ([] if isinstance(st.session_state[k], list) else None)
        st.rerun()
