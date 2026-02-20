import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import re
import urllib.parse

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 2. 高級感 & 視認性向上のためのCSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');
    .stApp { background-color: #F8F6F4; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    
    .header-container { text-align: center; padding: 50px 0; border-bottom: 1px solid #D4AF37; background: #FFF; margin-bottom: 40px; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 4rem; color: #111; letter-spacing: 5px; margin: 0; }
    
    /* スポット選択カード（縦並び・サイズ調整） */
    .spot-selection-container { max-width: 800px; margin: 0 auto; }
    .spot-selection-card {
        background: #FFFFFF; border: 1px solid #E0D8C3; padding: 25px; border-radius: 12px;
        margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    .spot-title { font-size: 1.3rem; font-weight: bold; color: #111; margin-bottom: 8px; border-left: 4px solid #D4AF37; padding-left: 12px; }
    
    /* プラン表示用：角丸背景カード */
    .plan-outer-card {
        background: #FFFFFF; border-radius: 24px; border: 1px solid #EAEAEA; 
        padding: 50px; margin: 20px auto 60px auto; max-width: 900px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.05);
    }
    
    .day-header { font-family: 'Playfair Display', serif; font-size: 2.8rem; border-bottom: 1px solid #D4AF37; margin-bottom: 35px; margin-top: 20px; }
    .time-slot { display: flex; margin-bottom: 35px; border-left: 2px solid #D4AF37; padding-left: 30px; position: relative; }
    .time-slot::before { content: ''; position: absolute; left: -7px; top: 0; width: 12px; height: 12px; background: #D4AF37; border-radius: 50%; }
    
    .budget-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 30px 0; }
    .budget-item { border: 1px solid #F0EBE3; padding: 15px; text-align: center; background: #FDFCFB; border-radius: 8px; }
    
    .tips-box { background: #1A1A1A; color: #E0D8C3; padding: 40px; border-radius: 16px; margin-top: 40px; }
    .tips-title { color: #D4AF37; font-weight: bold; font-size: 1.3rem; margin-bottom: 20px; letter-spacing: 2px; }

    /* 共有ボタン */
    .share-button { 
        display: inline-block; padding: 12px 25px; border-radius: 30px; 
        text-decoration: none; font-weight: bold; color: white; margin: 10px;
    }

    .footer { background: #FFF; padding: 80px 0; border-top: 1px solid #D4AF37; text-align: center; margin-top: 100px; }
    </style>
""", unsafe_allow_html=True)

if "step" not in st.session_state: st.session_state.step = "input"
if "found_spots" not in st.session_state: st.session_state.found_spots = []
if "selected_spots" not in st.session_state: st.session_state.selected_spots = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p></div>', unsafe_allow_html=True)

# --- STEP 1: 条件入力 ---
if st.session_state.step == "input":
    st.markdown('<h3 style="text-align:center;">01. 旅のプロファイル</h3>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: dep = st.text_input("🛫 出発地", value="新宿駅")
    with c2: dest = st.text_input("📍 目的地", placeholder="例：下北半島、奥出雲")
    with c3: bud = st.text_input("💰 予算/人", value="5万円") # 初期値を5万円に設定
    
    c4, c5, c6 = st.columns(3)
    with c4: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now() + timedelta(days=2)))
    with c5: adults = st.number_input("大人人数", 1, 10, 2)
    with c6: kids = st.number_input("子供人数", 0, 10, 0)
    
    tags = st.multiselect("✨ 重視ポイント", ["秘境・絶景", "歴史・国宝", "ミシュラン美食", "温泉・隠れ家", "現代アート", "伝統工芸", "パワースポット"], default=["秘境・絶景"])

    if st.button("⚜️ このエリアのスポットを調査する", use_container_width=True, type="primary"):
        st.session_state.form_data = {
            "dep": dep, "dest": dest, "budget": bud, "tags": tags, 
            "days": (date_range[1]-date_range[0]).days + 1 if isinstance(date_range, tuple) and len(date_range)==2 else 1,
            "adults": adults, "kids": kids
        }
        with st.spinner("現地情報を精査中..."):
            prompt = f"{dest}周辺で{tags}に合う実在の施設を15件挙げてください。名称・解説・公式検索URL（Google検索）を。「名称：」「解説：」「URL：」の形式で。"
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            # パース処理
            raw = res.choices[0].message.content
            spots = []
            items = re.split(r'\n(?=名称[:：])', raw)
            for item in items:
                n = re.search(r"名称[:：]\s*(.*)", item)
                d = re.search(r"解説[:：]\s*(.*)", item)
                u = re.search(r"URL[:：]\s*(.*)", item)
                if n: spots.append({"name": n.group(1).strip(), "desc": d.group(1).strip() if d else "", "url": u.group(1).strip() if u else "#"})
            st.session_state.found_spots = spots
            st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: スポット選択（縦並び） ---
elif st.session_state.step == "select_spots":
    st.markdown(f'<h3 style="text-align:center;">02. {st.session_state.form_data["dest"]} の厳選スポット</h3>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="spot-selection-container">', unsafe_allow_html=True)
        temp_selected = []
        for i, spot in enumerate(st.session_state.found_spots):
            st.markdown(f"""
                <div class="spot-selection-card">
                    <div class="spot-title">{spot['name']}</div>
                    <p style="font-size:0.9rem; color:#444;">{spot['desc']}</p>
                    <a href="{spot['url']}" target="_blank" style="font-size:0.8rem; color:#D4AF37;">[ 公式情報を確認 ]</a>
                </div>
            """, unsafe_allow_html=True)
            if st.checkbox(f"{spot['name']} を旅程に採用", key=f"s_{i}"):
                temp_selected.append(spot['name'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.session_state.selected_spots = temp_selected
    if st.button("🏨 確定して詳細設定へ", use_container_width=True, type="primary"):
        if not temp_selected: st.error("スポットを1つ以上選択してください。")
        else: st.session_state.step = "select_details"; st.rerun()

# --- STEP 3: 詳細設定 ---
elif st.session_state.step == "select_details":
    st.markdown('<h3 style="text-align:center;">03. 宿泊とプランの最終調整</h3>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: speed = st.select_slider("🚶 歩行速度", options=["ゆったり", "標準", "アクティブ"], value="標準")
    with c2: h_pref = st.multiselect("🏨 宿泊のこだわり", ["露天風呂付客室", "離れ・一棟貸し", "歴史的建築", "部屋食", "美食の宿", "サウナ"])

    if st.button("⚜️ 5つのプランを同時編纂する", use_container_width=True, type="primary"):
        st.session_state.form_data.update({"speed": speed, "h_pref": h_pref})
        st.session_state.step = "final_plan"; st.rerun()

# --- STEP 4: 最終プラン表示 ---
elif st.session_state.step == "final_plan":
    f = st.session_state.form_data
    if not st.session_state.final_plans:
        with st.spinner("5通りの極上プランを生成中..."):
            for label in ["プランA", "プランB", "プランC", "プランD", "プランE"]:
                spots_str = "、".join(st.session_state.selected_spots)
                prompt = f"""一流コンシェルジュとして、{f['days']}日間のプランを作成せよ。
                【必須項目】選択スポット：{spots_str}、宿泊こだわり：{f['h_pref']}、予算：{f['budget']}。
                【出力形式】
                1. <div class="plan-outer-card"> で全体を囲む。
                2. 各日の宿泊先（実在する旅館・ホテル名）を必ず1日目の終わりまたは2日目の冒頭に組み込むこと。
                3. 各スポットに [公式URL] としてGoogle検索リンクを付与。
                4. タイムライン、予算4分割、裏技（紺色ボックス）を含む。
                """
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                st.session_state.final_plans[label] = res.choices[0].message.content

    tabs = st.tabs(list(st.session_state.final_plans.keys()))
    for label, tab in zip(st.session_state.final_plans.keys(), tabs):
        with tab:
            st.markdown(st.session_state.final_plans[label], unsafe_allow_html=True)
            
            # 共有・確定セクション
            encoded = urllib.parse.quote(st.session_state.final_plans[label])
            st.markdown(f"""
                <div style="text-align:center; padding:40px; background:white; border-radius:24px; border:1px solid #D4AF37;">
                    <h4 style="color:#D4AF37;">このプランで確定しますか？</h4>
                    <a href="https://social-plugins.line.me/lineit/share?text={encoded}" class="share-button" style="background:#06C755;">LINEで共有</a>
                    <a href="https://mail.google.com/mail/?view=cm&fs=1&body={encoded}" class="share-button" style="background:#DB4437;">Gmailで送る</a>
                </div>
            """, unsafe_allow_html=True)

    if st.button("条件をリセットして最初に戻る"): st.session_state.clear(); st.rerun()

st.markdown('<div class="footer"><div class="aipia-logo" style="font-size:1.5rem;">Aipia</div><div style="font-weight:bold; color:#D4AF37; margin-top:10px;">2025 AIPIA CONCIERGE</div></div>', unsafe_allow_html=True)
