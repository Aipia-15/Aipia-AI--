import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import re
import urllib.parse

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 2. スタイル定義（高級感とスポット視認性を重視）
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');
    .stApp { background-color: #F4F1EE; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    
    .header-container { text-align: center; padding: 40px 0; border-bottom: 1px solid #D4AF37; background: #FFF; margin-bottom: 40px; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 4rem; color: #111; letter-spacing: 5px; margin: 0; }
    
    /* スポット選択カード */
    .spot-selection-card {
        background: #FFFFFF; border: 1px solid #D1C9B8; padding: 20px; border-radius: 4px;
        margin-bottom: 20px; transition: transform 0.2s;
    }
    .spot-selection-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.05); }
    .spot-title { font-size: 1.2rem; font-weight: bold; color: #111; margin-bottom: 10px; border-left: 3px solid #D4AF37; padding-left: 10px; }
    
    /* プラン表示用パーツ */
    .day-header { font-family: 'Playfair Display', serif; font-size: 2.5rem; border-bottom: 1px solid #D4AF37; margin-bottom: 30px; margin-top: 50px; }
    .time-slot { display: flex; margin-bottom: 35px; border-left: 1px solid #D4AF37; padding-left: 30px; position: relative; }
    .time-slot::before { content: ''; position: absolute; left: -6px; top: 0; width: 11px; height: 11px; background: #D4AF37; border-radius: 50%; }
    .tips-box { background: #1A1A1A; color: #E0D8C3; padding: 40px; margin-top: 40px; }
    .tips-title { color: #D4AF37; font-weight: bold; font-size: 1.2rem; margin-bottom: 20px; }
    
    /* ボタン調整 */
    .stButton>button { border-radius: 0px; border: 1px solid #D4AF37; background: #FFF; color: #111; padding: 10px 20px; }
    .stButton>button:hover { background: #D4AF37; color: #FFF; }
    </style>
""", unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p></div>', unsafe_allow_html=True)

# --- STEP 1: 条件入力 ---
if st.session_state.step == "input":
    st.markdown('<h3 style="text-align:center;">01. 旅のプロファイルを入力</h3>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: dep = st.text_input("🛫 出発地", value="新宿駅")
    with c2: dest = st.text_input("📍 目的地", placeholder="例：箱根、京都嵐山、下北半島")
    with c3: bud = st.text_input("💰 予算/人", value="15万円")
    
    c4, c5, c6 = st.columns(3)
    with c4: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now() + timedelta(days=2)))
    with c5: adults = st.number_input("大人人数", 1, 10, 2)
    with c6: kids = st.number_input("子供人数", 0, 10, 0)
    
    tags = st.multiselect("✨ 重視ポイント", ["秘境・絶景", "歴史・国宝", "ミシュラン美食", "温泉・隠れ家", "現代アート", "伝統工芸", "パワースポット"], default=["秘境・絶景", "ミシュラン美食"])

    if st.button("⚜️ このエリアのスポットを調査する", use_container_width=True):
        st.session_state.form_data = {
            "dep": dep, "dest": dest, "budget": bud, "tags": tags, 
            "days": (date_range[1]-date_range[0]).days + 1 if isinstance(date_range, tuple) and len(date_range)==2 else 1,
            "adults": adults, "kids": kids
        }
        with st.spinner(f"{dest} 周辺の厳選スポットを特定中..."):
            # 【重要】具体的スポットをJSON形式っぽく抽出させる
            prompt = f"""
            {dest}周辺で「{tags}」のテーマに合致する、実在する具体的な観光施設、飲食店、絶景ポイントを15件挙げてください。
            広域な地名ではなく、必ず「○○寺」「レストラン○○」といった固有名詞で出してください。
            返答は以下の形式で統一してください：
            【名称】スポット名
            【解説】その場所の魅力や歴史（100字程度）
            【URL】https://www.google.com/search?q=スポット名
            ---
            """
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            content = res.choices[0].message.content
            
            # テキストからスポット情報をパース
            spots = []
            raw_spots = content.split("---")
            for rs in raw_spots:
                name = re.search(r"【名称】(.*)", rs)
                desc = re.search(r"【解説】(.*)", rs)
                if name:
                    spots.append({"name": name.group(1).strip(), "desc": desc.group(1).strip() if desc else ""})
            
            st.session_state.found_spots = spots
            st.session_state.step = "select_spots"
            st.rerun()

# --- STEP 2: スポット表示 & 選択 ---
elif st.session_state.step == "select_spots":
    st.markdown(f"### 02. {st.session_state.form_data['dest']} の厳選スポット（{len(st.session_state.found_spots)}件）")
    st.write("気になるスポットにチェックを入れてください。それらを軸に最高のプランを組み上げます。")
    
    selected_names = []
    # 3列でカードを表示
    cols = st.columns(3)
    for i, spot in enumerate(st.session_state.found_spots):
        with cols[i % 3]:
            st.markdown(f"""
                <div class="spot-selection-card">
                    <div class="spot-title">{spot['name']}</div>
                    <p style="font-size:0.85rem; line-height:1.6; color:#555;">{spot['desc']}</p>
                </div>
            """, unsafe_allow_html=True)
            if st.checkbox("旅程に含める", key=f"check_{i}"):
                selected_names.append(spot['name'])
    
    st.session_state.selected_spots = selected_names

    if st.button("🏨 次へ：詳細設定とホテル選び", use_container_width=True):
        if not selected_names:
            st.error("少なくとも1つのスポットを選択してください。")
        else:
            st.session_state.step = "select_details"; st.rerun()

# --- STEP 3: 詳細設定 ---
elif st.session_state.step == "select_details":
    st.markdown("### 03. 宿泊とプランの微調整")
    c1, c2 = st.columns(2)
    with c1:
        speed = st.select_slider("🚶 歩行速度", options=["ゆったり", "標準", "アクティブ"], value="標準")
    with c2:
        h_pref = st.multiselect("🏨 宿泊のこだわり", ["露天風呂付客室", "離れ・一棟貸し", "歴史的建築", "サウナ完備", "部屋食", "美食の宿"])

    if st.button("⚜️ このスポットを軸にプランを編纂する", use_container_width=True):
        st.session_state.form_data.update({"speed": speed, "h_pref": h_pref})
        st.session_state.step = "final_plan"; st.rerun()

# --- STEP 4: プラン表示 ---
elif st.session_state.step == "final_plan":
    f = st.session_state.form_data
    spots_str = "、".join(st.session_state.selected_spots)
    
    st.markdown(f"### 04. 究極の旅程（{f['adults']}名 / {f['budget']}）")
    
    if not st.session_state.get("final_plans"):
        with st.spinner("選択されたスポットを結び、最適なルートを計算中..."):
            plans = {}
            for label in ["プランA", "プランB", "プランC"]:
                prompt = f"""
                一流コンシェルジュとして執筆せよ。
                出発：{f['dep']}、目的地：{f['dest']}、{f['days']}日間。
                必須スポット：{spots_str}
                人数：大人{f['adults']}名 子供{f['kids']}名 / 予算：{f['budget']} / 宿泊：{f['h_pref']}
                
                【構成】
                - <div class="day-header">DAY X</div>
                - タイムライン (<div class="time-slot">)
                - 具体的店名、移動時間、費用
                - 予算内訳（4グリッド）
                - 裏技（紺色 <div class="tips-box">)
                """
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                plans[label] = res.choices[0].message.content
            st.session_state.final_plans = plans

    tabs = st.tabs(list(st.session_state.final_plans.keys()))
    for label, tab in zip(st.session_state.final_plans.keys(), tabs):
        with tab:
            st.markdown(st.session_state.final_plans[label], unsafe_allow_html=True)

    if st.button("最初に戻る"):
        st.session_state.clear(); st.rerun()

st.markdown('<div class="footer"><div class="aipia-logo" style="font-size:1.5rem;">Aipia</div><div style="font-weight:bold; color:#D4AF37; margin-top:10px;">2025 AIPIA CONCIERGE</div></div>', unsafe_allow_html=True)
