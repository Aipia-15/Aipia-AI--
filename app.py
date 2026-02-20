import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import re
import urllib.parse
import time

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 2. UI再現 CSS (重視ポイント・タイムライン・予算・裏技)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&family=Noto+Serif+JP:wght@700&display=swap');

    .stApp { background-color: #F8F9FA; color: #333; font-family: 'Noto Sans JP', sans-serif; }
    
    /* ヘッダー */
    .header-container { text-align: center; padding: 30px 0; background: white; border-bottom: 1px solid #EEE; margin-bottom: 30px; }
    .aipia-logo { font-family: 'Noto Serif JP', serif; font-size: 3rem; font-weight: bold; color: #1A1A1A; margin: 0; }

    /* 重視ポイントのバッジ表示 */
    .priority-tag {
        display: inline-block; background: #E6F4F1; color: #00896C; 
        padding: 5px 15px; border-radius: 15px; font-size: 0.85rem; 
        font-weight: bold; margin-right: 8px; margin-bottom: 8px; border: 1px solid #00896C;
    }

    /* プランカード */
    .plan-card {
        max-width: 850px; margin: 0 auto 50px auto; background: #FFFFFF;
        border-radius: 24px; border: 1px solid #EAEAEA; overflow: hidden;
        box-shadow: 0 12px 40px rgba(0,0,0,0.08);
    }
    .plan-body { padding: 40px; }
    
    /* タイムライン (UI再現) */
    .day-num { color: #00896C; font-size: 1.6rem; font-weight: bold; margin: 40px 0 20px 0; border-bottom: 2px solid #00896C; display: inline-block; }
    .time-slot { display: flex; margin-bottom: 30px; border-left: 2px solid #00896C; padding-left: 25px; position: relative; }
    .time-slot::before { 
        content: ''; position: absolute; left: -6px; top: 0; 
        width: 12px; height: 12px; background: #00896C; border-radius: 50%; 
    }
    .time-val { font-weight: bold; color: #00896C; font-size: 1rem; min-width: 65px; }
    .spot-name { font-size: 1.3rem; font-weight: bold; color: #111; margin-bottom: 8px; }
    .spot-desc { font-size: 1rem; color: #444; line-height: 1.7; }
    .transport-chip { background: #F0F7F5; color: #00896C; padding: 6px 15px; border-radius: 20px; font-size: 0.85rem; margin-top: 10px; display: inline-block; font-weight: bold; }

    /* 予算内訳 (UI再現) */
    .budget-section { background: #F9F9F9; padding: 30px; border-radius: 20px; margin-top: 40px; border: 1px solid #EEE; }
    .budget-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-top: 15px; }
    .budget-item { background: white; padding: 15px; border-radius: 12px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.02); }
    .budget-label { font-size: 0.8rem; color: #888; display: block; }
    .budget-val { font-size: 1.1rem; font-weight: bold; color: #111; }
    .total-budget { font-size: 2.2rem; font-weight: bold; color: #00896C; text-align: center; margin-top: 25px; }

    /* 裏技ボックス (UI再現) */
    .tips-box { background: #0F172A; color: #F8FAFC; padding: 35px; border-radius: 20px; margin-top: 40px; }
    .tips-title { color: #2DD4BF; font-size: 1.2rem; font-weight: bold; margin-bottom: 20px; display: flex; align-items: center; }
    .tip-item { display: flex; margin-bottom: 15px; font-size: 0.95rem; line-height: 1.6; }
    .tip-num { background: #2DD4BF; color: #0F172A; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 15px; flex-shrink: 0; font-weight: bold; font-size: 0.8rem; }

    /* フッター */
    .footer { background: #F8F9FA; padding: 60px 0; border-top: 1px solid #EEE; text-align: center; margin-top: 50px; }
    .footer-logo { font-family: 'Noto Serif JP', serif; font-size: 2rem; color: #1A1A1A; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# セッション状態
if "step" not in st.session_state: st.session_state.step = "input"
if "parsed_spots" not in st.session_state: st.session_state.parsed_spots = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力 ---
if st.session_state.step == "input":
    with st.container():
        st.markdown("### 01. 旅のプロファイル構築")
        c1, c2, c3 = st.columns(3)
        with c1: dep = st.text_input("🛫 出発地", value="東京駅")
        with c2: dest = st.text_input("📍 目的地", placeholder="例：青森 下北半島、伊勢志摩")
        with c3: bud = st.text_input("💰 予算/人", value="15万円")
        
        c4, c5 = st.columns(2)
        with c4: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now() + timedelta(days=2)))
        with c5: speed = st.select_slider("🚶 歩行速度", options=["ゆったり", "標準", "アクティブ"], value="標準")
        
        st.markdown("#### ✨ 重視するポイント（複数選択）")
        priority_tags = st.multiselect("カテゴリー", ["絶景・秘境", "歴史・神社仏閣", "美食・郷土料理", "現代アート", "温泉・癒やし", "文化体験"], default=["絶景・秘境", "美食・郷土料理"])
        
        st.markdown("#### 🏨 宿泊・バリアフリーのこだわり")
        h1, h2 = st.columns(2)
        with h1: hotel_pref = st.multiselect("客室・設備", ["露天風呂付客室", "離れ・一棟貸し", "部屋食希望", "マウンテンビュー"])
        with h2: bf_pref = st.multiselect("バリアフリー", ["車椅子アクセス", "段差なし", "手すり完備", "貸切家族風呂"])

    if st.button("⚜️ この条件でプランを生成する", use_container_width=True, type="primary"):
        st.session_state.form_data = {
            "dep": dep, "dest": dest, "bud": bud, "speed": speed,
            "days": (date_range[1]-date_range[0]).days + 1,
            "tags": priority_tags, "hotel_pref": hotel_pref, "bf_pref": bf_pref
        }
        
        with st.spinner("現地情報をリサーチし、具体的なスポットを厳選中..."):
            # スポット20件の事前リサーチ
            prompt_spots = f"{dest}周辺で{priority_tags}に合う具体的な施設・名所を20件、歴史やURLと共に挙げてください。"
            res_spots = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt_spots}])
            st.session_state.parsed_spots = res_spots.choices[0].message.content
            st.session_state.step = "final_plan"; st.rerun()

# --- STEP 2: 最終プラン生成 (5プラン) ---
elif st.session_state.step == "final_plan":
    f = st.session_state.form_data
    
    # 画面上部に重視ポイントを表示
    st.markdown("### あなたが重視したポイント")
    tag_html = "".join([f'<span class="priority-tag">#{t}</span>' for t in f['tags']])
    if f['hotel_pref']: tag_html += "".join([f'<span class="priority-tag">🏨{h}</span>' for h in f['hotel_pref']])
    if f['bf_pref']: tag_html += "".join([f'<span class="priority-tag">♿{b}</span>' for b in f['bf_pref']])
    st.markdown(f'<div>{tag_html}</div><br>', unsafe_allow_html=True)

    if not st.session_state.final_plans:
        with st.spinner("5通りの究極の旅程を編纂中..."):
            for label in ["プランA", "プランB", "プランC", "プランD", "プランE"]:
                prompt_main = f"""
                一流コンシェルジュとして執筆。{f['dep']}発、{f['dest']}行き、{f['days']}日間。
                重視：{f['tags']}、宿泊：{f['hotel_pref']}、バリアフリー：{f['bf_pref']}。
                具体的スポット候補：{st.session_state.parsed_spots}

                【出力HTMLルール】
                1. 各日の食事・喫茶は実在の具体的店名。
                2. <div class="plan-card">の中に<div class="plan-body">を入れ、
                   <div class="day-num">、<div class="time-slot">、
                   <div class="budget-section">（交通/宿泊/体験/食費）、
                   <div class="tips-box">を正確に構成すること。
                """
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt_main}])
                st.session_state.final_plans[label] = res.choices[0].message.content

    tabs = st.tabs(list(st.session_state.final_plans.keys()))
    for label, tab in zip(st.session_state.final_plans.keys(), tabs):
        with tab:
            st.markdown(st.session_state.final_plans[label], unsafe_allow_html=True)
            
            # 書き出し機能
            encoded = urllib.parse.quote(st.session_state.final_plans[label])
            line_url = f"https://social-plugins.line.me/lineit/share?text={encoded}"
            gmail_url = f"https://mail.google.com/mail/?view=cm&fs=1&to=&su=Aipia旅行プラン&body={encoded}"
            st.markdown(f'<div style="text-align:center;"><a href="{line_url}" target="_blank" style="background:#06C755; color:white; padding:10px 25px; border-radius:30px; text-decoration:none; margin-right:10px;">LINEで共有</a><a href="{gmail_url}" target="_blank" style="background:#DB4437; color:white; padding:10px 25px; border-radius:30px; text-decoration:none;">Gmailで送る</a></div>', unsafe_allow_html=True)

    if st.button("条件を変えて作り直す"):
        st.session_state.clear()
        st.rerun()

# 4. フッター (見本再現)
st.markdown("""
    <div class="footer">
        <div class="footer-logo">Aipia</div>
        <div style="color:#888; font-size:0.9rem;">
            あなたの望む秘境への旅行プランをAIが提案します。<br>
            人生を変えるような新たなAIの新境地をぜひご体験ください。
        </div>
        <div style="font-weight:bold; color:#5D7EA3; margin-top:20px;">2025-2026 / AIPIA / GCIS</div>
    </div>
""", unsafe_allow_html=True)
