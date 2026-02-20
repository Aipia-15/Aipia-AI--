import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 2. CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    
    .top-nav { position: absolute; top: 10px; left: 20px; z-index: 999; }
    .header-container { text-align: center; padding: 40px 0; border-bottom: 1px solid #D4AF37; background: #FFF; margin-bottom: 40px; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 3.5rem; color: #111; letter-spacing: 5px; margin: 0; }
    .aipia-sub { letter-spacing: 3px; color: #D4AF37; font-size: 1.0rem; margin-top: 5px; font-weight: bold; }

    .spot-selection-card {
        background: #FFFFFF; border: 1px solid #E0D8C3; border-radius: 16px;
        margin-bottom: 25px; overflow: hidden; display: flex; flex-direction: row;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
    }
    .spot-image { width: 280px; height: 180px; object-fit: cover; background: #EEE; }
    .spot-content { padding: 20px; flex: 1; }
    .spot-title { font-size: 1.3rem; font-weight: bold; color: #111; margin-bottom: 8px; }

    .plan-outer-card {
        background: #FFFFFF; border-radius: 24px; border: 1px solid #EAEAEA; 
        padding: 40px; margin: 20px auto; max-width: 950px;
        box-shadow: 0 15px 50px rgba(0,0,0,0.06); color: #1A1A1A;
    }
    .base-hotel-card {
        background: #F0F4F8; border: 2px solid #D4AF37; border-radius: 12px;
        padding: 20px; margin-bottom: 30px; text-align: center;
    }
    
    .footer { background: #FFF; padding: 60px 0; border-top: 1px solid #D4AF37; text-align: center; margin-top: 80px; }
    </style>
""", unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}

# 左上のロゴ
st.markdown('<div class="top-nav">', unsafe_allow_html=True)
if st.button("Aipia", key="home_btn"):
    st.session_state.clear()
    st.session_state.step = "input"
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">- AIが創る、秘境への旅行プラン -</p></div>', unsafe_allow_html=True)

# スポット取得関数（修正版：パースロジックの強化）
def get_spots(dest, tags, count=10, exclude_names=[]):
    exclude_text = f"ただし、以下のスポットは既に挙げたので除外してください：{', '.join(exclude_names)}" if exclude_names else ""
    prompt = f"""
    {dest}周辺でテーマ「{tags}」に合う実在の観光スポットや飲食店を必ず{count}件リストアップしてください。
    各スポットを必ず以下の区切り文字「@@@」で区切り、項目を「|」で区切って出力してください。
    形式：
    @@@名称|解説|写真検索用英語名@@@
    
    例：
    @@@兼六園|日本三名園の一つ。四季折々の美しさ。|Kenrokuen Garden@@@
    
    {exclude_text}
    """
    res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
    raw_content = res.choices[0].message.content
    
    results = []
    items = raw_content.split("@@@")
    for item in items:
        if "|" in item:
            parts = item.split("|")
            if len(parts) >= 2:
                name = parts[0].strip()
                desc = parts[1].strip()
                key = parts[2].strip() if len(parts) > 2 else name
                results.append({
                    "name": name,
                    "desc": desc,
                    "img": f"https://images.unsplash.com/photo-1542051841857-5f90071e7989?q=80&w=800&auto=format&fit=crop&q={urllib.parse.quote(key)}" # 安定した画像生成
                })
    return results[:count]

# STEP 1: 入力
if st.session_state.step == "input":
    st.markdown('<h3 style="text-align:center;">01. Travel Profile</h3>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: dep = st.text_input("🛫 出発地", value="新宿駅")
    with c2: dest = st.text_input("📍 目的地", placeholder="例：上高地、伊勢志摩")
    with c3: bud = st.text_input("💰 予算/人", value="5万円")
    c4, c5, c6 = st.columns(3)
    with c4: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now() + timedelta(days=2)))
    with c5: adults = st.number_input("大人", 1, 10, 2)
    with c6: kids = st.number_input("子供", 0, 10, 0)
    c7, c8 = st.columns(2)
    with c7: start_time = st.time_input("⏰ 出発希望時間", value=datetime.strptime("08:00", "%H:%M").time())
    with c8: tags = st.multiselect("✨ 重視ポイント", ["秘境・絶景", "歴史・国宝", "ミシュラン美食", "温泉", "現代アート"], default=["秘境・絶景"])

    if st.button("⚜️ 厳選スポットを調査する", use_container_width=True, type="primary"):
        st.session_state.form_data = {"dep": dep, "dest": dest, "budget": bud, "tags": tags, "adults": adults, "kids": kids, "start_time": start_time.strftime("%H:%M"), "days": (date_range[1]-date_range[0]).days + 1 if isinstance(date_range, tuple) and len(date_range)==2 else 1}
        with st.spinner("現地情報を精査中..."):
            st.session_state.found_spots = get_spots(dest, tags, 10)
            st.session_state.step = "select_spots"; st.rerun()

# STEP 2: スポット選択
elif st.session_state.step == "select_spots":
    st.markdown(f'<h3 style="text-align:center;">02. {st.session_state.form_data["dest"]} の候補地</h3>', unsafe_allow_html=True)
    
    if not st.session_state.found_spots:
        st.error("スポットが見つかりませんでした。もう一度お試しください。")
        if st.button("戻る"): st.session_state.step = "input"; st.rerun()
    else:
        for i, spot in enumerate(st.session_state.found_spots):
            st.markdown(f"""
                <div class="spot-selection-card">
                    <img src="{spot['img']}" class="spot-image">
                    <div class="spot-content">
                        <div class="spot-title">{spot['name']}</div>
                        <p style="color:#555;">{spot['desc']}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.checkbox(f"{spot['name']} を採用", key=f"check_{i}", value=spot['name'] in st.session_state.selected_spots):
                if spot['name'] not in st.session_state.selected_spots: st.session_state.selected_spots.append(spot['name'])
            else:
                if spot['name'] in st.session_state.selected_spots: st.session_state.selected_spots.remove(spot['name'])

        c_more, c_next = st.columns(2)
        with c_more:
            if st.button("➕ More（さらに10個出す）", use_container_width=True):
                with st.spinner("追加スポットを探索中..."):
                    existing = [s['name'] for s in st.session_state.found_spots]
                    st.session_state.found_spots.extend(get_spots(st.session_state.form_data["dest"], st.session_state.form_data["tags"], 10, existing))
                    st.rerun()
        with c_next:
            if st.button("🏨 確定して詳細設定へ", use_container_width=True, type="primary"): 
                if not st.session_state.selected_spots: st.warning("スポットを選択してください")
                else: st.session_state.step = "select_details"; st.rerun()

# STEP 3: 詳細設定
elif st.session_state.step == "select_details":
    st.markdown('<h3 style="text-align:center;">03. プランニング・ポリシー</h3>', unsafe_allow_html=True)
    speed = st.select_slider("🚶 歩行速度", options=["ゆったり", "標準", "アクティブ"], value="標準")
    h_pref = st.multiselect("🏨 宿泊のこだわり", ["バリアフリー対応（車椅子・段差配慮）", "露天風呂付客室", "離れ・一棟貸し", "歴史的建築", "サウナ", "美食の宿"], default=["露天風呂付客室"])
    if st.button("⚜️ 5つの緻密なプランを生成する", use_container_width=True, type="primary"):
        st.session_state.form_data.update({"speed": speed, "h_pref": h_pref})
        st.session_state.step = "final_plan"; st.rerun()

# STEP 4: 最終プラン
elif st.session_state.step == "final_plan":
    f = st.session_state.form_data
    if not st.session_state.final_plans:
        with st.spinner("究極の旅程を編纂中..."):
            for label in ["プランA", "プランB", "プランC", "プランD", "プランE"]:
                prompt = f"一流コンシェルジュとして、{f['days']}日間の緻密なプランを作成。出発：{f['dep']}（{f['start_time']}発）、拠点：{f['dest']}。選択スポット：{', '.join(st.session_state.selected_spots)}。宿泊こだわり：{f['h_pref']}。宿泊は1拠点固定とし冒頭に<div class='base-hotel-card'>でホテル名明記。30分単位のタイムライン、全体を<div class='plan-outer-card'>で囲みHTML形式で出力。"
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                st.session_state.final_plans[label] = res.choices[0].message.content
    
    tabs = st.tabs(list(st.session_state.final_plans.keys()))
    for label, tab in zip(st.session_state.final_plans.keys(), tabs):
        with tab:
            with st.expander("🛠️ プランの微調整・再生成"):
                edited = st.text_area("内容(HTML編集)", value=st.session_state.final_plans[label], height=300, key=f"edit_{label}")
                if st.button("✨ 変更を保存", key=f"save_{label}"): st.session_state.final_plans[label] = edited; st.rerun()
                if st.button("🔄 再生成", key=f"regen_{label}"): del st.session_state.final_plans[label]; st.rerun()
            st.markdown(st.session_state.final_plans[label], unsafe_allow_html=True)
            encoded = urllib.parse.quote(st.session_state.final_plans[label])
            st.markdown(f'<div style="text-align:center; padding:20px;"><a href="https://social-plugins.line.me/lineit/share?text={encoded}" style="background:#06C755; color:white; padding:12px 25px; border-radius:30px; text-decoration:none; font-weight:bold;">LINEで送信</a></div>', unsafe_allow_html=True)

st.markdown('<div class="footer"><div class="aipia-logo" style="font-size:1.5rem;">Aipia</div><div style="font-weight:bold; color:#D4AF37; margin-top:10px;">2025-2026 / AIPIA / GCIS</div></div>', unsafe_allow_html=True)
