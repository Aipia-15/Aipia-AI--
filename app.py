import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import re
import urllib.parse
import time

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 2. スクリーンショットのUIを完全再現するCSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&family=Noto+Serif+JP:wght@700&display=swap');

    .stApp { background-color: #F8F9FA; color: #333; font-family: 'Noto Sans JP', sans-serif; }
    
    /* ヘッダー */
    .header-container { text-align: center; padding: 30px 0; background: white; border-bottom: 1px solid #EEE; margin-bottom: 30px; }
    .aipia-logo { font-family: 'Noto Serif JP', serif; font-size: 3rem; font-weight: bold; color: #1A1A1A; margin: 0; }

    /* プランカード */
    .plan-card {
        max-width: 800px; margin: 0 auto 50px auto; background: #FFFFFF;
        border-radius: 24px; border: 1px solid #EAEAEA; overflow: hidden;
        box-shadow: 0 12px 40px rgba(0,0,0,0.08);
    }
    .plan-body { padding: 40px; }
    
    /* タイムライン・スポット (UI再現) */
    .day-num { color: #00896C; font-size: 1.6rem; font-weight: bold; margin: 40px 0 20px 0; border-bottom: 2px solid #00896C; display: inline-block; }
    .time-slot { display: flex; margin-bottom: 30px; border-left: 2px solid #00896C; padding-left: 25px; position: relative; }
    .time-slot::before { 
        content: ''; position: absolute; left: -6px; top: 0; 
        width: 12px; height: 12px; background: #00896C; border-radius: 50%; 
    }
    .time-val { font-weight: bold; color: #00896C; font-size: 1rem; min-width: 60px; }
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
        st.markdown("### 01. 旅のプロファイル")
        c1, c2, c3 = st.columns(3)
        with c1: dep = st.text_input("🛫 出発地", value="新宿駅")
        with c2: dest = st.text_input("📍 目的地", placeholder="例：長野、和歌山、金沢")
        with c3: bud = st.text_input("💰 予算/人", value="15万円")
        
        c4, c5, c6 = st.columns(3)
        with c4: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now() + timedelta(days=2)))
        with c5: adults = st.number_input("大人", 1, 10, 2)
        with c6: kids = st.number_input("子供", 0, 10, 0)
        
        speed = st.select_slider("🚶 歩行速度", options=["ゆったり", "標準", "アクティブ"], value="標準")
        
        st.markdown("#### 🏨 宿泊へのこだわり")
        h1, h2 = st.columns(2)
        with h1: hotel_pref = st.multiselect("客室・設備", ["露天風呂付客室", "離れ・一棟貸し", "部屋食希望", "オーシャンビュー"])
        with h2: bf_pref = st.multiselect("バリアフリー", ["車椅子アクセス", "段差なし", "手すり完備", "エレベーター至近"])

    if st.button("⚜️ 秘境の断片を探し出す", use_container_width=True, type="primary"):
        st.session_state.form_data = {
            "dep": dep, "dest": dest, "bud": bud, "speed": speed,
            "days": (date_range[1]-date_range[0]).days + 1,
            "hotel_pref": hotel_pref, "bf_pref": bf_pref, "adults": adults, "kids": kids
        }
        
        # 【重要】具体的スポットを出すための前処理検索
        with st.spinner("現地コンシェルジュと連絡を取り、スポットを厳選しています..."):
            prompt_spots = f"""
            {dest}周辺で、歴史、文化、絶景、美食の観点から「具体的なスポット・店名」を20件挙げてください。
            ※「長野市」といった広域ではなく、「戸隠神社 奥社」「藤屋御本陳」などピンポイントな名称を。
            """
            res_spots = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt_spots}])
            st.session_state.parsed_spots = res_spots.choices[0].message.content
            st.session_state.step = "final_plan"; st.rerun()

# --- STEP 2: 最終プラン生成 (5つ一気に生成) ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plans:
        with st.spinner("一分一秒を慈しむ、5つの異なる旅程を編纂中..."):
            f = st.session_state.form_data
            for label in ["プランA", "プランB", "プランC", "プランD", "プランE"]:
                prompt_main = f"""
                一流の旅コンシェルジュとして、以下の情報を基にHTML形式で旅行プランを書いてください。
                
                【条件】
                - 出発地: {f['dep']} / 目的地: {f['dest']} / 日数: {f['days']}日間 / 予算: {f['bud']}
                - 歩行速度: {f['speed']} / 人数: 大人{f['adults']}名、子供{f['kids']}名
                - 宿泊希望: {f['hotel_pref']}
                - バリアフリー: {f['bf_pref']}
                - 候補スポットリスト: {st.session_state.parsed_spots}
                
                【出力ルール（厳守）】
                1. 各日の食事（朝・昼・カフェ・晩）は実在する店名を出すこと。
                2. 以下のHTML構造を維持すること:
                   <div class="plan-card">
                     <div class="plan-body">
                       <h2>{label}: [旅のテーマ]</h2>
                       <div class="day-num">1日目</div>
                       <div class="time-slot">
                         <div class="time-val">09:00</div>
                         <div>
                           <div class="spot-name">具体的スポット名</div>
                           <div class="spot-desc">解説テキスト</div>
                           <div class="transport-chip">✨ 移動：特急・バスなど</div>
                         </div>
                       </div>
                       <div class="budget-section">
                         <div class="budget-grid">
                           <div class="budget-item"><span class="budget-label">交通費</span><span class="budget-val">¥XX,XXX</span></div>
                           <div class="budget-item"><span class="budget-label">宿泊費</span><span class="budget-val">¥XX,XXX</span></div>
                         </div>
                         <div class="total-budget">概算合計 ¥XXX,XXX</div>
                       </div>
                       <div class="tips-box">
                         <div class="tips-title">💡 コンシェルジュの裏技</div>
                         <div class="tip-item"><div class="tip-num">1</div>内容...</div>
                       </div>
                     </div>
                   </div>
                """
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt_main}])
                st.session_state.final_plans[label] = res.choices[0].message.content

    tabs = st.tabs(list(st.session_state.final_plans.keys()))
    for label, tab in zip(st.session_state.final_plans.keys(), tabs):
        with tab:
            st.markdown(st.session_state.final_plans[label], unsafe_allow_html=True)
            
            # 共有
            plan_encoded = urllib.parse.quote(st.session_state.final_plans[label])
            line_url = f"https://social-plugins.line.me/lineit/share?text={plan_encoded}"
            st.markdown(f'<a href="{line_url}" target="_blank" style="background:#06C755; color:white; padding:10px 20px; border-radius:30px; text-decoration:none;">LINEで送る</a>', unsafe_allow_html=True)

    if st.button("最初に戻る"):
        st.session_state.clear()
        st.rerun()
