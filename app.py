import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import re
import urllib.parse
import time

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - Executive Concierge")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 2. 究極の高級感 & スクリーンショット再現 CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');

    .stApp { background-color: #F4F1EE; color: #1A1A1A; font-family: 'Noto Serif JP', serif; }
    
    /* ヘッダー：圧倒的気品 */
    .header-container { text-align: center; padding: 60px 0; border-bottom: 1px solid #D4AF37; margin-bottom: 50px; background: #FFF; }
    .aipia-logo { font-family: 'Playfair Display', serif; font-size: 5rem; color: #111; letter-spacing: 5px; margin: 0; }
    .aipia-sub { letter-spacing: 12px; color: #D4AF37; font-size: 0.8rem; margin-top: -10px; }

    /* 重視ポイント & 人数表示セクション */
    .info-bar { 
        max-width: 850px; margin: 0 auto 20px auto; display: flex; justify-content: space-between; 
        align-items: center; background: white; padding: 20px 30px; border-radius: 12px; border: 1px solid #E0D8C3;
    }
    .priority-tag { background: #00896C; color: white; padding: 4px 12px; border-radius: 4px; font-size: 0.75rem; margin-right: 5px; }

    /* プランカード：見本のUIを完全再現 */
    .plan-card {
        max-width: 850px; margin: 0 auto 60px auto; background: #FFFFFF;
        border-radius: 0px; border: 1px solid #D1C9B8; overflow: hidden;
        box-shadow: 20px 20px 60px rgba(0,0,0,0.05);
    }
    .plan-body { padding: 60px; }
    
    /* タイムライン */
    .day-header { font-family: 'Playfair Display', serif; font-size: 3rem; color: #111; border-bottom: 1px solid #D4AF37; margin-bottom: 40px; }
    .time-slot { display: flex; margin-bottom: 45px; border-left: 1px solid #D4AF37; padding-left: 35px; position: relative; }
    .time-slot::before { 
        content: ''; position: absolute; left: -6px; top: 0; 
        width: 11px; height: 11px; background: #D4AF37; border-radius: 50%; 
    }
    .time-val { font-family: 'Playfair Display', serif; font-weight: bold; color: #111; font-size: 1.1rem; min-width: 70px; }
    .spot-name { font-size: 1.5rem; font-weight: bold; color: #111; margin-bottom: 12px; letter-spacing: 1px; }
    .spot-desc { font-size: 1.05rem; color: #333; line-height: 2.2; }
    .transport-chip { background: #F8F5F2; color: #888; padding: 8px 18px; border: 1px solid #EEE; border-radius: 0; font-size: 0.8rem; margin-top: 15px; display: inline-block; }

    /* 予算内訳 (見本再現) */
    .budget-section { background: #FFF; padding: 40px; border: 1px solid #EEE; margin-top: 50px; text-align: center; }
    .budget-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 20px; }
    .budget-item { border: 1px solid #EEE; padding: 15px; }
    .total-budget { font-size: 2.5rem; font-weight: bold; color: #111; border-top: 2px solid #D4AF37; display: inline-block; padding-top: 10px; margin-top: 30px; }

    /* 裏技ボックス (紺色再現) */
    .tips-box { background: #1A1A1A; color: #E0D8C3; padding: 45px; margin-top: 50px; }
    .tips-title { color: #D4AF37; font-size: 1.3rem; margin-bottom: 25px; letter-spacing: 2px; }
    .tip-item { display: flex; margin-bottom: 20px; font-size: 0.95rem; line-height: 1.8; }
    .tip-num { color: #D4AF37; margin-right: 15px; font-weight: bold; }

    /* フッター */
    .footer { background: #FFF; padding: 80px 0; border-top: 1px solid #D4AF37; text-align: center; margin-top: 100px; }
    </style>
    """, unsafe_allow_html=True)

# セッション管理
if "step" not in st.session_state: st.session_state.step = "input"
if "parsed_spots" not in st.session_state: st.session_state.parsed_spots = ""
if "final_plans" not in st.session_state: st.session_state.final_plans = {}

st.markdown('<div class="header-container"><p class="aipia-logo">Aipia</p><p class="aipia-sub">EXECUTIVE TRAVEL DESIGNER</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力 ---
if st.session_state.step == "input":
    st.markdown('<h2 style="text-align:center;">01. Travel Profile</h2>', unsafe_allow_html=True)
    with st.container():
        c1, c2, c3 = st.columns(3)
        with c1: dep = st.text_input("🛫 出発地", value="新宿駅")
        with c2: dest = st.text_input("📍 目的地", placeholder="例：下北半島、奥出雲")
        with c3: bud = st.text_input("💰 予算/人", value="15万円")
        
        c4, c5, c6 = st.columns(3)
        with c4: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now() + timedelta(days=2)))
        with c5: adults = st.number_input("大人", 1, 10, 2)
        with c6: kids = st.number_input("子供", 0, 10, 0)
        
        speed = st.select_slider("🚶 歩行速度", options=["ゆったり", "標準", "アクティブ"], value="標準")
        tags = st.multiselect("✨ 重視ポイント", ["秘境・絶景", "歴史・国宝", "美食・郷土料理", "現代アート", "温泉・癒やし"], default=["秘境・絶景", "美食・郷土料理"])
        h_pref = st.multiselect("🏨 宿泊のこだわり", ["露天風呂付客室", "離れ・一棟貸し", "部屋食"])

    if st.button("⚜️ この条件で極上の旅程を編纂する", use_container_width=True, type="primary"):
        st.session_state.form_data = {
            "dep": dep, "dest": dest, "bud": bud, "speed": speed, "adults": adults, "kids": kids,
            "days": (date_range[1]-date_range[0]).days + 1, "tags": tags, "h_pref": h_pref
        }
        # 【重要】スポット飛ばし防止の1段目：強制リサーチ
        with st.spinner("現地を徹底調査し、具体的な施設を厳選しています..."):
            prompt_spots = f"{dest}周辺で、{tags}に合う実在の「施設名・店名」を20件、歴史的背景と共にリサーチせよ。広域地名は禁止。"
            res_spots = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt_spots}])
            st.session_state.parsed_spots = res_spots.choices[0].message.content
            st.session_state.step = "final_plan"; st.rerun()

# --- STEP 2: 最終プラン表示 ---
elif st.session_state.step == "final_plan":
    f = st.session_state.form_data
    
    # 情報バー（重視ポイント & 人数表示）
    tag_html = "".join([f'<span class="priority-tag">#{t}</span>' for t in f['tags']])
    st.markdown(f"""
        <div class="info-bar">
            <div>{tag_html}</div>
            <div style="font-size:0.9rem; color:#666;">
                <b>人数：</b> 大人 {f['adults']}名 / 子供 {f['kids']}名 &nbsp;&nbsp; <b>予算：</b> {f['bud']}/人
            </div>
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state.final_plans:
        with st.spinner("5つのプランを緻密に構成中..."):
            for label in ["プランA", "プランB", "プランC", "プランD", "プランE"]:
                prompt_main = f"""
                一流のコンシェルジュとして執筆せよ。
                {f['dep']}発、{f['dest']}行き、{f['days']}日間。
                重視：{f['tags']} / 宿泊：{f['h_pref']} / 人数：大人{f['adults']}、子供{f['kids']}
                候補スポット：{st.session_state.parsed_spots}

                【HTML構成の絶対厳守】
                1. 各日のタイトルは <div class="day-header">DAY X: [Title]</div>
                2. タイムラインは <div class="time-slot"> 内に、時刻・店名（具体的）・解説を。
                3. 移動は <div class="transport-chip">移動：電車XX分(XX円)</div>
                4. 予算内訳は <div class="budget-section"> 内に、交通・宿泊・食費・体験の4グリッド。
                5. 裏技は <div class="tips-box">（紺色背景）に。
                """
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt_main}])
                st.session_state.final_plans[label] = res.choices[0].message.content

    tabs = st.tabs(list(st.session_state.final_plans.keys()))
    for label, tab in zip(st.session_state.final_plans.keys(), tabs):
        with tab:
            st.markdown(st.session_state.final_plans[label], unsafe_allow_html=True)
            
            # 書き出し
            encoded = urllib.parse.quote(st.session_state.final_plans[label])
            st.markdown(f"""
                <div style="text-align:center; padding:20px;">
                    <a href="https://social-plugins.line.me/lineit/share?text={encoded}" target="_blank" style="background:#06C755; color:white; padding:12px 30px; border-radius:4px; text-decoration:none; font-weight:bold;">LINEへ送信</a>
                </div>
            """, unsafe_allow_html=True)

    if st.button("条件をリセットして最初に戻る"):
        st.session_state.clear(); st.rerun()

# 4. フッター
st.markdown("""
    <div class="footer">
        <div class="aipia-logo" style="font-size:2rem;">Aipia</div>
        <div style="font-weight:bold; color:#D4AF37; margin-top:20px; letter-spacing:3px;">2025-2026 / AIPIA / GCIS</div>
    </div>
""", unsafe_allow_html=True)
