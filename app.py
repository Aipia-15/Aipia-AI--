import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import re
import urllib.parse
import time

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - AIが創る、秘境への旅行プラン")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 2. デザイン (CSS) - 見本UIの完全再現
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&display=swap');

    .stApp { background-color: #F0F2F5; font-family: 'Noto Serif JP', serif; }
    
    /* ヘッダー */
    .header-bar {
        display: flex; justify-content: space-between; align-items: center;
        padding: 10px 40px; background: white; border-bottom: 1px solid #E0E0E0;
        position: sticky; top: 0; z-index: 1000;
    }
    .header-title { font-family: 'Playfair Display', serif; font-size: 24px; font-weight: bold; }
    .header-nav a { margin: 0 15px; text-decoration: none; color: #666; font-size: 14px; font-weight: bold; }
    .header-nav a.active { color: #00896C; border-bottom: 2px solid #00896C; padding-bottom: 18px; }

    /* サイドバー・カード */
    .plan-sidebar { background: white; border: 1px solid #DDD; border-radius: 4px; }
    .plan-item { padding: 15px; border-bottom: 1px solid #EEE; cursor: pointer; }
    .plan-item.active { background: #E8F4F1; border-left: 4px solid #00896C; }
    .main-plan-card { background: white; border-radius: 20px; padding: 40px; border: 1px solid #DDD; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }
    .day-header { font-family: 'Playfair Display', serif; font-size: 32px; color: #111; border-bottom: 1px solid #D4AF37; margin-bottom: 30px; }

    /* 共有ボタン */
    .btn-line { background-color: #06C755; color: white !important; padding: 12px 25px; border-radius: 30px; text-decoration: none; font-weight: bold; display: inline-block; margin: 5px; }
    .btn-gmail { background-color: #DB4437; color: white !important; padding: 12px 25px; border-radius: 30px; text-decoration: none; font-weight: bold; display: inline-block; margin: 5px; }

    /* フッター */
    .footer-section { background: #F8F9FA; padding: 80px 0; border-top: 1px solid #E0E0E0; text-align: center; margin-top: 60px; }
    .footer-logo { font-family: 'Playfair Display', serif; font-size: 40px; color: #1A1A1A; margin-bottom: 15px; }
    .footer-copyright { color: #BBB; font-size: 12px; letter-spacing: 2px; margin-top: 20px; }

    .loader { text-align: center; padding: 100px; font-family: 'Playfair Display', serif; font-size: 24px; color: #D4AF37; }
    </style>
""", unsafe_allow_html=True)

# 共通関数：アニメーション
def luxury_loading(text):
    placeholder = st.empty()
    for _ in range(5):
        placeholder.markdown(f'<div class="loader">{text}...</div>', unsafe_allow_html=True)
        time.sleep(0.4)
    placeholder.empty()

# 3. ヘッダー
st.markdown("""
    <div class="header-bar no-print">
        <div class="header-title">Aipia</div>
        <div class="header-nav">
            <a href="#" class="active">プラン作成</a>
            <a href="#">履歴</a>
            <a href="#">お気に入り</a>
        </div>
        <div style="font-size: 12px; border: 1px solid #DDD; padding: 5px 12px; border-radius: 4px;">🇯🇵 日本語 ∨</div>
    </div>
""", unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "selected_names" not in st.session_state: st.session_state.selected_names = []
if "parsed_spots" not in st.session_state: st.session_state.parsed_spots = []
if "parsed_hotels" not in st.session_state: st.session_state.parsed_hotels = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}

# --- STEP 1: 入力 ---
if st.session_state.step == "input":
    st.markdown("<div style='text-align:center; padding:60px 0;'><h1 style='font-family:Playfair Display; font-size:80px;'>Aipia</h1><p style='letter-spacing:5px; color:#888;'>AI が 創 る 、 秘 境 へ の 旅 行 プ ラ ン</p></div>", unsafe_allow_html=True)
    with st.container():
        st.markdown("### 01. 旅のプロファイル")
        c1, c2, c3 = st.columns(3)
        with c1: dep = st.text_input("🛫 出発地", value="鷹の台駅")
        with c2: dest = st.text_input("📍 目的地", placeholder="例：信州、伊勢")
        with c3: bud = st.text_input("💰 予算/人", placeholder="15万円〜")
        
        c4, c5, c6 = st.columns(3)
        with c4: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now() + timedelta(days=2)))
        with c5: adults = st.number_input("大人", 1, 10, 2)
        with c6: kids = st.number_input("子供", 0, 10, 0)

        tags = st.multiselect("旅の主題", ["絶景・秘境", "歴史・神社仏閣", "美食・郷土料理", "現代アート", "バリアフリー重視"], default=["絶景・秘境"])
        speed = st.select_slider("🚶 歩行速度", options=["ゆったり", "標準", "アクティブ"])

    if st.button("⚜️ スポットを提案する", use_container_width=True, type="primary"):
        luxury_loading("至極のスポットを探索中")
        st.session_state.form_data = {"departure": dep, "destination": dest, "budget": bud, "tags": tags, "speed": speed, "days": (date_range[1]-date_range[0]).days + 1}
        prompt = f"{dest}周辺で{tags}に合う実在のスポットを20件。名称、解説、URL形式。"
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
        st.session_state.parsed_spots = re.findall(r"(名称[:：].*?)(?=名称[:：]|$)", res.choices[0].message.content, re.DOTALL)
        st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: スポット選択 ---
elif st.session_state.step == "select_spots":
    col_l, col_m, col_r = st.columns([1, 2.5, 1])
    with col_m:
        st.markdown("### 02. スポットを選択")
        for i, spot in enumerate(st.session_state.parsed_spots[:10]):
            name = re.search(r"名称[:：]\s*(.*)", spot).group(1).split('\n')[0].strip()
            st.markdown(f'<div class="main-plan-card"><h4>{name}</h4></div>', unsafe_allow_html=True)
            if st.checkbox(f"{name} を追加", key=f"s_{i}"):
                if name not in st.session_state.selected_names: st.session_state.selected_names.append(name)
        
        if st.button("🏨 ホテルの提案へ", use_container_width=True):
            luxury_loading("こだわり条件で宿をリサーチ中")
            prompt = f"{st.session_state.form_data['destination']}周辺の高級宿を5つ。名称、理由、URL。"
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            st.session_state.parsed_hotels = re.findall(r"(名称[:：].*?)(?=名称[:：]|$)", res.choices[0].message.content, re.DOTALL)
            st.session_state.step = "select_hotel"; st.rerun()

# --- STEP 3: ホテル選択 ---
elif st.session_state.step == "select_hotel":
    st.markdown("### 03. 宿泊先の選定")
    for i, hotel in enumerate(st.session_state.parsed_hotels):
        h_name = re.search(r"名称[:：]\s*(.*)", hotel).group(1).split('\n')[0].strip()
        st.markdown(f'<div class="main-plan-card"><h4>{h_name}</h4></div>', unsafe_allow_html=True)
        if st.button(f"{h_name} を拠点にする", key=f"h_{i}"):
            st.session_state.selected_hotel = h_name
            st.session_state.step = "final_plan"; st.rerun()

# --- STEP 4: 最終プラン & 共有 ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plans:
        f = st.session_state.form_data
        prompt = f"{f['days']}日間の詳細旅程。{st.session_state.selected_hotel}宿泊。実在の喫茶店・食事処を明記。タイムライン形式。"
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
        st.session_state.final_plans["プランA"] = res.choices[0].message.content

    content = st.session_state.final_plans["プランA"]
    st.markdown('<div class="main-plan-card">', unsafe_allow_html=True)
    st.markdown(content.replace("\n", "<br>"), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 共有ボタン
    encoded = urllib.parse.quote(content)
    line_url = f"https://social-plugins.line.me/lineit/share?text={encoded}"
    gmail_url = f"https://mail.google.com/mail/?view=cm&fs=1&to=&su=Aipia旅行プラン&body={encoded}"
    
    st.markdown(f"""
        <div style="text-align:center; padding:40px;">
            <a href="{line_url}" target="_blank" class="btn-line">LINEで送る</a>
            <a href="{gmail_url}" target="_blank" class="btn-gmail">Gmailで送る</a>
        </div>
    """, unsafe_allow_html=True)
    if st.button("最初に戻る"): st.session_state.clear(); st.rerun()

# 4. フッター
st.markdown("""
    <div class="footer-section no-print">
        <div class="footer-logo">Aipia</div>
        <div class="footer-desc">人生を変えるような新たなAIの新境地をぜひご体験ください。</div>
        <div style="font-weight:bold; color:#5D7EA3;">2025-2026 / AIPIA / GCIS</div>
        <div class="footer-copyright">DIGITAL SANCTUARY FOR MODERN TRAVELERS</div>
    </div>
""", unsafe_allow_html=True)
