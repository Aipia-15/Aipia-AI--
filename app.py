import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import re
import urllib.parse
import time

# 1. ページ設定とスタイル
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# スクリーンショットのモダンなUIを再現するCSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap');

    .stApp { background-color: #FFFFFF; color: #333; font-family: 'Noto Sans JP', sans-serif; }
    
    /* ヘッダー・ロゴ */
    .header-container { text-align: center; padding: 40px 0; border-bottom: 1px solid #EEE; margin-bottom: 40px; }
    .aipia-logo { font-size: 3rem; font-weight: bold; color: #1A1A1A; margin: 0; }
    .aipia-sub { color: #666; font-size: 0.9rem; margin-top: 10px; }

    /* プランカード：スクリーンショットのスタイル */
    .plan-card {
        max-width: 600px; margin: 0 auto 40px auto; background: #FDFDFD;
        border-radius: 24px; border: 1px solid #EAEAEA; overflow: hidden;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
    }
    .plan-header-img { width: 100%; height: 250px; object-fit: cover; }
    .plan-body { padding: 30px; }
    
    /* タイムライン・スポット */
    .day-num { color: #007B5E; font-size: 1.5rem; font-weight: bold; margin: 30px 0 20px 0; border-bottom: 2px solid #007B5E; display: inline-block; }
    .time-slot { display: flex; margin-bottom: 25px; border-left: 2px solid #007B5E; padding-left: 20px; position: relative; }
    .time-slot::before { 
        content: ''; position: absolute; left: -6px; top: 0; 
        width: 10px; height: 10px; background: #007B5E; border-radius: 50%; 
    }
    .time-val { font-weight: bold; color: #007B5E; font-size: 0.9rem; width: 60px; }
    .spot-name { font-size: 1.2rem; font-weight: bold; color: #111; margin: 0 0 8px 0; }
    .spot-desc { font-size: 0.95rem; color: #555; line-height: 1.6; }
    .official-site { font-size: 0.8rem; color: #007B5E; border: 1px solid #007B5E; padding: 2px 8px; border-radius: 12px; margin-left: 10px; text-decoration: none; }
    
    /* 交通費・移動チップ */
    .transport-chip { background: #E6F4F1; color: #007B5E; padding: 8px 15px; border-radius: 15px; font-size: 0.85rem; margin-top: 10px; display: inline-block; }

    /* 予算セクション */
    .budget-section { background: #FFF; padding: 30px; border-radius: 20px; margin-top: 30px; }
    .budget-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 20px; }
    .budget-item { background: #F9F9F9; padding: 15px; border-radius: 15px; text-align: center; }
    .budget-label { font-size: 0.8rem; color: #888; display: block; }
    .budget-val { font-size: 1.1rem; font-weight: bold; color: #111; }
    .total-budget { font-size: 2rem; font-weight: bold; color: #005F48; text-align: center; margin-top: 20px; }

    /* 裏技セクション */
    .tips-box { background: #0A192F; color: #FFF; padding: 30px; border-radius: 20px; margin-top: 30px; }
    .tips-title { color: #4ADE80; font-weight: bold; margin-bottom: 15px; display: flex; align-items: center; }
    .tip-item { display: flex; margin-bottom: 15px; font-size: 0.9rem; line-height: 1.6; }
    .tip-num { background: #4ADE80; color: #0A192F; width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 15px; flex-shrink: 0; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# セッション状態
if "step" not in st.session_state: st.session_state.step = "input"
if "parsed_spots" not in st.session_state: st.session_state.parsed_spots = []
if "selected_hotel" not in st.session_state: st.session_state.selected_hotel = ""
if "final_plans" not in st.session_state: st.session_state.final_plans = {}

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">AIが創る、秘境への旅行プラン</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力 ---
if st.session_state.step == "input":
    with st.container():
        c1, c2 = st.columns(2)
        with c1: departure = st.text_input("🛫 出発地", value="東京駅")
        with c2: destination = st.text_input("📍 目的地", placeholder="例：青森 下北半島、和歌山 熊野")
        
        c3, c4 = st.columns(2)
        with c3: budget = st.text_input("💰 予算/人", value="10万円")
        with c4: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now() + timedelta(days=2)))
        
        tags = st.multiselect("カテゴリー", ["絶景", "歴史・国宝", "美食", "秘湯", "現代アート"], default=["絶景", "美食"])

    if st.button("⚜️ この条件でプランを生成する", use_container_width=True, type="primary"):
        st.session_state.form_data = {
            "departure": departure, "destination": destination, "budget": budget,
            "days": (date_range[1]-date_range[0]).days + 1, "tags": tags
        }
        
        # 具体的なスポットを20件出すためのプロンプト
        with st.spinner("秘境のデータを照合中..."):
            prompt = f"""
            {destination}において、{tags}に合致する「具体的な施設・名所」を20件挙げてください。
            ※「長野市」といった広い地域ではなく、「善光寺 宿坊」「戸隠神社 奥社」など具体的な場所を。
            各スポットの名称、文化的背景（なぜ有名か）、公式URL（または参考URL）を箇条書きで。
            """
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            st.session_state.parsed_spots = res.choices[0].message.content
            st.session_state.step = "final_plan"; st.rerun()

# --- STEP 4: 最終プラン表示 ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plans:
        with st.spinner("UIを構成し、5つのプランを作成中..."):
            f = st.session_state.form_data
            for label in ["プランA", "プランB", "プランC", "プランD", "プランE"]:
                prompt = f"""
                一流の旅コンシェルジュとして、{f['destination']}の旅を提案。
                
                【構成指示】
                1. 以下のJSON形式を参考に、HTMLタグを混ぜて1つの完全なプランを書いてください。
                2. タイムラインは「具体的スポット名」を使い、バスや電車の運賃・所要時間も入れる。
                3. 「予算の内訳」を具体的に（交通、宿泊、体験、食費）。
                4. 「コンシェルジュの裏技」を3点。
                5. 「宿泊スポット」の紹介。
                6. 以下の情報を含めること:
                候補スポット：{st.session_state.parsed_spots}
                
                【出力形式の例】
                <div class="plan-card">
                  <img src="https://picsum.photos/seed/{label}/600/300" class="plan-header-img">
                  <div class="plan-body">
                    <h2>{label}: [旅のタイトル]</h2>
                    <div class="day-num">1日目</div>
                    <div class="time-slot">
                      <div class="time-val">09:00</div>
                      <div>
                        <div class="spot-name">具体的スポット名 <a href="#" class="official-site">公式サイト</a></div>
                        <div class="spot-desc">解説テキスト。歴史や見どころ。</div>
                        <div class="transport-chip">✨ 移動：バス30分 (500円)</div>
                      </div>
                    </div>
                    <div class="budget-section">
                      <h3>予算の内訳</h3>
                      <div class="budget-grid">
                        <div class="budget-item"><span class="budget-label">交通費</span><span class="budget-val">¥20,000</span></div>
                        </div>
                      <div class="total-budget">合計概算 ¥50,000</div>
                    </div>
                    <div class="tips-box">
                      <div class="tips-title">💡 コンシェルジュの裏技</div>
                      <div class="tip-item"><div class="tip-num">1</div>冬季の注意事項など...</div>
                    </div>
                  </div>
                </div>
                """
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                st.session_state.final_plans[label] = res.choices[0].message.content

    tabs = st.tabs(list(st.session_state.final_plans.keys()))
    for label, tab in zip(st.session_state.final_plans.keys(), tabs):
        with tab:
            st.markdown(st.session_state.final_plans[label], unsafe_allow_html=True)
            
    if st.button("最初からやり直す"):
        st.session_state.clear()
        st.rerun()
