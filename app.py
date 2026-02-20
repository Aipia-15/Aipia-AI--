import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import re
import urllib.parse
import time

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 2. 高級感あふれるデザイン (CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&display=swap');

    .stApp { background-color: #F8F5F2; color: #1A1A1A; font-family: 'Noto+Serif+JP', serif; }
    .black-banner { 
        background: linear-gradient(135deg, #0F0F0F 0%, #2A2A2A 100%); 
        padding: 50px 0; text-align: center; border-bottom: 2px solid #D4AF37; margin-bottom: 40px;
    }
    .aipia-logo { 
        font-family: 'Playfair Display', serif; font-size: 5.5rem; color: #D4AF37; margin: 0;
        letter-spacing: 2px; text-shadow: 3px 3px 6px rgba(0,0,0,0.4);
    }
    .sub-logo { color: #D4AF37; letter-spacing: 10px; font-size: 0.9rem; margin-top: -10px; opacity: 0.8; }

    /* カード・ボックスデザイン */
    .spot-card, .hotel-card { 
        background: #FFF; padding: 35px; border-radius: 4px; margin-bottom: 30px; 
        border: 1px solid #E0D8C3; border-left: 6px solid #D4AF37;
        box-shadow: 15px 15px 40px rgba(0,0,0,0.03);
    }
    .plan-box { 
        background: #FFF; padding: 60px; border: 1px solid #D1C9B8;
        line-height: 2.4; font-size: 1.1rem; color: #333;
    }
    
    /* セクションタイトル */
    .section-title { font-family: 'Playfair Display', serif; font-size: 2.5rem; color: #111; margin-bottom: 30px; text-align: center; }
    .day-header { 
        font-family: 'Playfair Display', serif; font-size: 3.2rem; color: #111;
        border-bottom: 1px solid #D4AF37; margin: 70px 0 40px 0; padding-bottom: 10px;
    }

    /* アニメーション用 */
    .luxury-loader { text-align: center; padding: 120px 0; font-family: 'Playfair Display', serif; font-style: italic; font-size: 28px; color: #D4AF37; }
    @media print { .no-print { display: none !important; } }
    </style>
    """, unsafe_allow_html=True)

# セッション状態の管理
if "step" not in st.session_state: st.session_state.step = "input"
if "parsed_spots" not in st.session_state: st.session_state.parsed_spots = []
if "parsed_hotels" not in st.session_state: st.session_state.parsed_hotels = []
if "selected_names" not in st.session_state: st.session_state.selected_names = []
if "selected_hotel" not in st.session_state: st.session_state.selected_hotel = ""
if "final_plans" not in st.session_state: st.session_state.final_plans = {}

def luxury_loading(text):
    placeholder = st.empty()
    quotes = ["時間は、最も贅沢な贈り物。", "風景は、心の鏡。", "本物の価値は、ディテールに宿る。"]
    for i in range(12):
        q = quotes[i % len(quotes)]
        placeholder.markdown(f'<div class="luxury-loader">{text}<br><span style="font-size:16px; color:#999; font-style:normal;">{q}</span></div>', unsafe_allow_html=True)
        time.sleep(0.4)
    placeholder.empty()

st.markdown('<div class="black-banner no-print"><p class="aipia-logo">Aipia</p><p class="sub-logo">PREMIUM TRAVEL DESIGNER</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力 ---
if st.session_state.step == "input":
    st.markdown('<p class="section-title">01. Travel Profile</p>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1: departure = st.text_input("🛫 出発地", value="新宿駅")
    with c2: destination = st.text_input("📍 目的地", placeholder="例：箱根、飛騨高山、直島")
    with c3: budget = st.text_input("💰 予算/人", placeholder="20万円〜")

    c4, c5, c6 = st.columns(3)
    with c4: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now() + timedelta(days=2)))
    with c5: adults = st.number_input("大人", 1, 10, 2)
    with c6: kids = st.number_input("子供", 0, 10, 0)
    
    walking_speed = st.select_slider("🚶 歩行速度", options=["ゆったり", "標準", "アクティブ"], value="標準")

    st.markdown("#### ✨ 旅の主題")
    tags = st.multiselect("カテゴリー", ["国宝・世界遺産", "秘境・絶景", "ミシュラン名店・美食", "老舗旅館・名湯", "現代アート・建築", "歴史の面影・遺跡", "大人の隠れ家"], default=["秘境・絶景", "ミシュラン名店・美食"])

    st.markdown("#### 🏨 宿泊へのこだわり")
    h1, h2 = st.columns(2)
    with h1: hotel_pref = st.multiselect("客室・設備", ["露天風呂付客室", "離れ・一棟貸し", "サウナ完備", "部屋食希望", "オーシャンビュー", "マウンテンビュー"])
    with h2: bf_pref = st.multiselect("バリアフリー・サポート", ["車椅子アクセス", "段差なし", "手すり完備", "エレベーター至近", "貸切家族風呂", "刻み食対応"])

    if st.button("⚜️ 秘境の断片を探し出す", use_container_width=True, type="primary"):
        luxury_loading("至高のスポットを厳選しております...")
        st.session_state.form_data = {
            "departure": departure, "destination": destination, "budget": budget, 
            "adults": adults, "kids": kids, "speed": walking_speed,
            "dates": f"{date_range[0]}〜{date_range[1]}", "tags": tags, 
            "hotel_pref": hotel_pref, "bf_pref": bf_pref,
            "days": (date_range[1]-date_range[0]).days + 1
        }
        prompt = f"{destination}周辺で{tags}に合致する「具体的な施設名・名所」を20件提案。各名所の背景や文化を詳しく解説し、URLを添えて。"
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
        st.session_state.parsed_spots = re.findall(r"(名称[:：].*?)(?=名称[:：]|$)", re.sub(r'[」」「]', '', res.choices[0].message.content), re.DOTALL)
        st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: スポット選択 ---
elif st.session_state.step == "select_spots":
    st.markdown('<p class="section-title">02. Spot Selection</p>', unsafe_allow_html=True)
    for i, spot_text in enumerate(st.session_state.parsed_spots[:10]):
        name = re.search(r"名称[:：]\s*(.*)", spot_text).group(1).split('\n')[0].strip() if "名称" in spot_text else f"Spot {i}"
        with st.container():
            st.markdown('<div class="spot-card">', unsafe_allow_html=True)
            c1, c2 = st.columns([1, 2])
            with c1: st.image(f"https://picsum.photos/seed/{name}/400/250", use_container_width=True)
            with c2:
                st.markdown(f'<h3 style="font-family:serif; color:#111;">{name}</h3>', unsafe_allow_html=True)
                st.write(re.search(r"解説[:：]\s*(.*)", spot_text, re.DOTALL).group(1).split('URL')[0].strip() if "解説" in spot_text else "")
                if st.checkbox("この地を訪ねる", key=f"sel_{i}"):
                    if name not in st.session_state.selected_names: st.session_state.selected_names.append(name)
            st.markdown('</div>', unsafe_allow_html=True)

    if st.button("⚜️ 次へ：宿泊先の選定", use_container_width=True):
        luxury_loading("ご希望に沿う最高級の宿を調査しております...")
        f = st.session_state.form_data
        prompt = f"{f['destination']}周辺で、予算{f['budget']}に見合い、こだわり({f['hotel_pref']})とバリアフリー({f['bf_pref']})を完璧に満たす実在の最高級宿を5つ提案せよ。名称、選定理由、URL。"
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
        st.session_state.parsed_hotels = re.findall(r"(名称[:：].*?)(?=名称[:：]|$)", res.choices[0].message.content, re.DOTALL)
        st.session_state.step = "select_hotel"; st.rerun()

# --- STEP 3: ホテル選択 ---
elif st.session_state.step == "select_hotel":
    st.markdown('<p class="section-title">03. The Sanctuary</p>', unsafe_allow_html=True)
    for i, hotel_text in enumerate(st.session_state.parsed_hotels):
        h_name = re.search(r"名称[:：]\s*(.*)", hotel_text).group(1).split('\n')[0].strip()
        with st.container():
            st.markdown('<div class="hotel-card">', unsafe_allow_html=True)
            c1, c2 = st.columns([1, 2])
            with c1: st.image(f"https://picsum.photos/seed/{h_name}/400/250", use_container_width=True)
            with c2:
                st.markdown(f'<h3 style="font-family:serif;">{h_name}</h3>', unsafe_allow_html=True)
                st.write(re.search(r"理由[:：]\s*(.*)", hotel_text, re.DOTALL).group(1).split('URL')[0].strip() if "理由" in hotel_text else "")
                if st.button(f"{h_name} を拠点に選ぶ", key=f"h_{i}"):
                    st.session_state.selected_hotel = h_name
                    st.session_state.step = "final_plan"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# --- STEP 4: 最終プラン表示 ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plans:
        luxury_loading("一分一秒を慈しむ究極の旅程を編纂中...")
        f = st.session_state.form_data
        for label in ["プランA", "プランB", "プランC", "プランD", "プランE"]:
            prompt = f"""
            一流コンシェルジュとして執筆。{f['departure']}発着、{f['days']}日間、{st.session_state.selected_hotel}滞在。
            歩行速度は{f['speed']}、人数は大人{f['adults']}名、子供{f['kids']}名。
            
            【必須項目】
            - 朝・昼・晩、および「午後の喫茶」の場所を具体的な「実在店舗名」で明記。
            - タイムラインを1時間刻みで。各日の見出しを <div class="day-header">DAY X: [Title]</div> とせよ。
            - スポット間に [IMAGE:キーワード] を挿入。
            - 改行を多用し、美しい余白を持たせること。
            """
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            st.session_state.final_plans[label] = res.choices[0].message.content

    tabs = st.tabs(list(st.session_state.final_plans.keys()))
    for label, tab in zip(st.session_state.final_plans.keys(), tabs):
        with tab:
            content = st.session_state.final_plans[label]
            parts = re.split(r"\[IMAGE:(.*?)\]", content)
            st.markdown('<div class="plan-box">', unsafe_allow_html=True)
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    st.markdown(part.replace("\n", "<br>"), unsafe_allow_html=True)
                else:
                    st.image(f"https://picsum.photos/seed/{part}/1200/500", caption=f"Scenario: {part}")
            st.markdown('</div>', unsafe_allow_html=True)
            st.button("最初に戻る", on_click=lambda: st.session_state.clear())
