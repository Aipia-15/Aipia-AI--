import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import re
import urllib.parse
import time

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 2. デザイン (CSS) - 高級感の強化
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&display=swap');
    
    .stApp { background-color: #F4F1EE; color: #2C2C2C; }
    .black-banner { 
        background: linear-gradient(135deg, #1A1A1A 0%, #333 100%); 
        padding: 60px 0; text-align: center; border-bottom: 3px solid #D4AF37;
    }
    .aipia-logo { 
        font-family: 'Playfair Display', serif; font-style: italic; 
        font-size: 5rem; font-weight: bold; color: #D4AF37; margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* 高級感のあるカード */
    .spot-card, .hotel-card { 
        background-color: #FFFFFF; padding: 30px; border-radius: 0px; 
        margin-bottom: 25px; border-left: 5px solid #D4AF37;
        box-shadow: 10px 10px 30px rgba(0,0,0,0.05);
    }
    
    /* プラン表示 */
    .plan-box { 
        background-color: #FFF; padding: 50px; border: 1px solid #E0E0E0;
        line-height: 2.2; font-family: 'Hiragino Mincho ProN', serif;
    }
    .day-header { 
        font-family: 'Playfair Display', serif; font-size: 3rem; color: #1A1A1A;
        border-bottom: 2px solid #D4AF37; margin: 60px 0 30px 0; text-align: left;
    }
    .meal-spot { color: #8B4513; font-weight: bold; border-bottom: 1px dotted #8B4513; }
    
    /* アニメーション用 */
    .loader-container { text-align: center; padding: 100px 0; }
    .luxury-loader { font-family: 'Playfair Display', serif; font-size: 24px; color: #D4AF37; font-style: italic; }
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
    quotes = ["最上の休息を、あなたに。", "歴史とモダンが交差する旅路。", "味覚が呼び覚ます、新しい自分。"]
    for i in range(12):
        q = quotes[i % len(quotes)]
        placeholder.markdown(f"""
            <div class="loader-container">
                <div class="luxury-loader">{text}</div>
                <p style="color:#999; margin-top:10px;">{q}</p>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(0.4)
    placeholder.empty()

st.markdown('<div class="black-banner no-print"><p class="aipia-logo">Aipia</p><p style="color:#D4AF37; letter-spacing:8px; font-size:0.8rem;">THE PRIVATE CONCIERGE</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力 ---
if st.session_state.step == "input":
    st.markdown("### 01. ご要望をお聞かせください")
    col1, col2, col3 = st.columns(3)
    with col1: departure = st.text_input("🛫 出発地", value="新宿駅")
    with col2: destination = st.text_input("📍 目的地", placeholder="例：軽井沢、伊勢志摩、京都")
    with col3: budget = st.text_input("💰 ご予算（一人当たり）", placeholder="20万円〜")

    col_date, col_tag = st.columns([1, 2])
    with col_date: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now() + timedelta(days=2)))
    with col_tag: tags = st.multiselect("旅の主題", ["重要文化財・遺跡", "名刹・古社", "ミシュラン・郷土名店", "絶景・秘境", "伝統工芸・芸術"], default=["絶景・秘境", "ミシュラン・郷土名店"])

    if st.button("⚜️ 旅の断片を探す", use_container_width=True, type="primary"):
        luxury_loading("至極のスポットを厳選しております...")
        st.session_state.form_data = {"departure": departure, "destination": destination, "budget": budget, "dates": f"{date_range[0]}〜{date_range[1]}", "tags": tags, "days": (date_range[1]-date_range[0]).days + 1}
        
        prompt = f"{destination}周辺で{tags}に合う「具体的な名称」の観光名所や飲食店を20件提案。名称、解説(100字)、URLの形式。"
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
        st.session_state.parsed_spots = re.findall(r"(名称[:：].*?)(?=名称[:：]|$)", re.sub(r'[」」「]', '', res.choices[0].message.content), re.DOTALL)
        st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: スポット選択 ---
elif st.session_state.step == "select_spots":
    st.markdown("### 02. 心惹かれる場所をお選びください")
    for i, spot_text in enumerate(st.session_state.parsed_spots[:10]):
        name = re.search(r"名称[:：]\s*(.*)", spot_text).group(1).split('\n')[0].strip() if "名称" in spot_text else f"Spot {i}"
        with st.container():
            st.markdown('<div class="spot-card">', unsafe_allow_html=True)
            c1, c2 = st.columns([1, 2])
            with c1: st.image(f"https://picsum.photos/seed/{name}/400/250", use_container_width=True)
            with c2:
                st.markdown(f'<h3 style="font-family:serif;">{name}</h3>', unsafe_allow_html=True)
                st.write(re.search(r"解説[:：]\s*(.*)", spot_text, re.DOTALL).group(1).split('URL')[0].strip() if "解説" in spot_text else "")
                st.checkbox("この地を訪ねる", key=f"sel_{i}", on_change=lambda n=name: st.session_state.selected_names.append(n) if n not in st.session_state.selected_names else None)
            st.markdown('</div>', unsafe_allow_html=True)

    if st.button("⚜️ 次へ：宿泊先の選定", use_container_width=True):
        luxury_loading("極上の宿をリストアップしております...")
        prompt = f"{st.session_state.form_data['destination']}周辺で、予算{st.session_state.form_data['budget']}に見合う最高級の宿を5つ提案。名称、特徴(100字)、URL。"
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
        st.session_state.parsed_hotels = re.findall(r"(名称[:：].*?)(?=名称[:：]|$)", res.choices[0].message.content, re.DOTALL)
        st.session_state.step = "select_hotel"; st.rerun()

# --- STEP 3: ホテル選択 ---
elif st.session_state.step == "select_hotel":
    st.markdown("### 03. 旅の拠点となる宿をお選びください")
    for i, hotel_text in enumerate(st.session_state.parsed_hotels):
        h_name = re.search(r"名称[:：]\s*(.*)", hotel_text).group(1).split('\n')[0].strip()
        with st.container():
            st.markdown('<div class="hotel-card">', unsafe_allow_html=True)
            c1, c2 = st.columns([1, 2])
            with c1: st.image(f"https://picsum.photos/seed/{h_name}/400/250", use_container_width=True)
            with c2:
                st.markdown(f'<h3 style="font-family:serif;">{h_name}</h3>', unsafe_allow_html=True)
                st.write(re.search(r"特徴[:：]\s*(.*)", hotel_text, re.DOTALL).group(1).split('URL')[0].strip())
                if st.button(f"{h_name}を予約する", key=f"h_{i}"):
                    st.session_state.selected_hotel = h_name
                    st.session_state.step = "final_plan"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# --- STEP 4: 最終プラン表示 ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plans:
        luxury_loading("究極の旅程を編纂しております...")
        f = st.session_state.form_data
        for label in ["プランA", "プランB", "プランC", "プランD", "プランE"]:
            prompt = f"""
            一流コンシェルジュとして、{f['dates']}の{f['days']}日間、{st.session_state.selected_hotel}に宿泊する旅程を執筆せよ。
            【条件】
            - 朝食、昼食、喫茶、夕食の場所を「具体的な実在店舗名」で明記。
            - タイムラインは1時間単位。移動手段(特急名等)を正確に。
            - 各日の合間に [IMAGE:風景] を挿入。
            - 改行を多くし、贅沢な余白を持たせること。
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
                    st.image(f"https://picsum.photos/seed/{part}/1200/500")
            st.markdown('</div>', unsafe_allow_html=True)
            st.button("最初に戻る", on_click=lambda: st.session_state.clear())
