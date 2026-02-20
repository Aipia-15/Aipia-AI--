import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import re
import urllib.parse
import time

# 1. ページ設定
st.set_page_config(layout="wide", page_title="Aipia - AI秘境コンシェルジュ")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 2. デザイン (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #FCF9F2; }
    .black-banner { background-color: #111; width: 100%; padding: 40px 0; text-align: center; margin-bottom: 20px; }
    .aipia-logo { font-family: 'Georgia', serif; font-style: italic; font-size: 8vw; font-weight: bold; color: #FCF9F2; line-height: 1.0; margin: 0; }
    
    /* スポット・プランのカードデザイン */
    .spot-card { background-color: white; padding: 25px; border-radius: 20px; margin-bottom: 20px; border: 1px solid #eee; box-shadow: 0 10px 20px rgba(0,0,0,0.05); }
    .plan-box { background-color: white; border-radius: 20px; padding: 40px; border: 1px solid #ddd; line-height: 2.0; margin-bottom: 30px; color: #222; font-size: 17px; }
    
    /* タイポグラフィ */
    .day-header { 
        font-family: 'Impact', sans-serif; font-size: 40px; color: #fff; background: #111; 
        padding: 15px 30px; display: block; margin: 40px 0 20px 0; text-align: center;
        clip-path: polygon(0% 0%, 100% 0%, 95% 100%, 5% 100%);
    }
    .time-slot { font-weight: bold; color: #D4AF37; font-size: 20px; border-bottom: 1px solid #D4AF37; margin-top: 25px; padding-bottom: 5px; }
    .advice-section { background: #fffdf0; border: 2px dashed #D4AF37; padding: 20px; border-radius: 15px; margin-top: 30px; }
    
    /* アニメーション待機画面 */
    .loading-text { font-size: 24px; font-weight: bold; color: #111; text-align: center; animation: pulse 2s infinite; }
    @keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }
    
    @media print { .no-print { display: none !important; } }
    </style>
    """, unsafe_allow_html=True)

# セッション状態
if "step" not in st.session_state: st.session_state.step = "input"
if "parsed_spots" not in st.session_state: st.session_state.parsed_spots = []
if "display_count" not in st.session_state: st.session_state.display_count = 10
if "selected_names" not in st.session_state: st.session_state.selected_names = []
if "final_plans" not in st.session_state: st.session_state.final_plans = {}

def loading_animation(text="秘境を探索中..."):
    quotes = ["「旅とは、目的地ではなく、新しいものの見方を見つけることだ」", "「道がどこへ続くかではなく、道のないところに足跡を残せ」", "「美味しい食事と絶景は、魂を浄化する」"]
    placeholder = st.empty()
    for i in range(10):
        q = quotes[i % len(quotes)]
        placeholder.markdown(f'<div class="loading-text"><p>{text}</p><p style="font-size:16px; font-weight:normal; color:#666;">{q}</p></div>', unsafe_allow_html=True)
        time.sleep(0.5)
    placeholder.empty()

st.markdown('<div class="black-banner no-print"><p class="aipia-logo">Aipia</p></div>', unsafe_allow_html=True)

# --- STEP 1: 入力 ---
if st.session_state.step == "input":
    st.markdown("### 1. あなたの理想の旅をデザインする")
    col1, col2, col3 = st.columns(3)
    with col1: departure = st.text_input("🛫 出発地", value="新宿駅")
    with col2: destination = st.text_input("📍 目的地（未定でも可）", placeholder="例：信州、四国、伊勢など")
    with col3: budget = st.text_input("💰 予算/人", placeholder="10万円")

    col_date, col_pa, col_pc = st.columns([3, 1, 1])
    with col_date: date_range = st.date_input("📅 日程", value=(datetime.now(), datetime.now() + timedelta(days=2)))
    with col_pa: adults = st.number_input("大人", 1, 10, 2)
    with col_pc: kids = st.number_input("子供", 0, 10, 0)

    st.markdown("#### ✨ 旅の目的・こだわり（複数選択可）")
    tags = st.multiselect("カテゴリー", ["歴史・神社仏閣", "絶景・自然", "郷土料理・美食", "温泉・癒やし", "文化・芸術・遺跡", "体験・アクティビティ"], default=["絶景・自然", "郷土料理・美食"])
    
    h1, h2 = st.columns(2)
    with h1: hotel_style = st.selectbox("宿泊希望", ["こだわらない", "高級老舗旅館", "絶景リゾート", "古民家宿", "グランピング"])
    with h2: barrier_free = st.multiselect("バリアフリー設定", ["車椅子対応", "段差なし", "手すりあり", "貸切家族風呂"])

    if st.button("✨ 秘境スポットを厳選する", use_container_width=True, type="primary"):
        loading_animation("あなたにぴったりの「点」のスポットをリサーチ中...")
        st.session_state.form_data = {"departure": departure, "destination": destination, "budget": budget, "adults": adults, "kids": kids, "dates": f"{date_range[0]}〜{date_range[1]}", "tags": tags, "hotel": hotel_style, "bf": barrier_free, "days": (date_range[1]-date_range[0]).days + 1}
        
        prompt = f"{destination}周辺で、{tags}に合致する具体的な観光名所、遺跡、神社、飲食店を20件提案。日本語のみ。URL必須。名称、解説、URLを1件ずつ出力。"
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
        st.session_state.parsed_spots = re.findall(r"(名称[:：].*?)(?=名称[:：]|$)", re.sub(r'[」」「]', '', res.choices[0].message.content), re.DOTALL)
        st.session_state.step = "select_spots"; st.rerun()

# --- STEP 2: スポット選択 ---
elif st.session_state.step == "select_spots":
    st.markdown("## SPOT DISCOVERY")
    for i in range(min(st.session_state.display_count, len(st.session_state.parsed_spots))):
        spot_text = st.session_state.parsed_spots[i]
        name = re.search(r"名称[:：]\s*(.*)", spot_text).group(1).split('\n')[0].strip() if "名称" in spot_text else f"スポット{i}"
        with st.container():
            st.markdown('<div class="spot-card">', unsafe_allow_html=True)
            c1, c2 = st.columns([1, 2])
            with c1: st.image(f"https://picsum.photos/seed/{name}/400/250", use_container_width=True)
            with c2:
                st.markdown(f'### {name}')
                st.write(re.search(r"解説[:：]\s*(.*)", spot_text, re.DOTALL).group(1).split('URL')[0].strip() if "解説" in spot_text else "")
                if st.checkbox(f"このスポットをプランに組み込む", key=f"sel_{i}"):
                    if name not in st.session_state.selected_names: st.session_state.selected_names.append(name)
            st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.display_count < len(st.session_state.parsed_spots) and st.button("🔽 他のスポットも見る"):
        st.session_state.display_count += 10; st.rerun()

    if st.button("🚀 超詳細な5つの旅程を生成", use_container_width=True, type="primary"):
        st.session_state.step = "final_plan"; st.rerun()

# --- STEP 3: 最終プラン表示 ---
elif st.session_state.step == "final_plan":
    if not st.session_state.final_plans:
        loading_animation("全日程を分刻みでシミュレーション中...")
        f = st.session_state.form_data
        for label in ["プランA", "プランB", "プランC", "プランD", "プランE"]:
            prompt = f"""
            一流旅行誌の編集者として作成。{f['dates']}の{f['days']}日間、{f['departure']}発着。
            予算{f['budget']}、目的{f['tags']}。選択：{f['selected_names'] if 'selected_names' in f else st.session_state.selected_names}。
            
            【執筆ルール】
            1. 各日のタイトルを <div class="day-header">DAY X: [魅力的なタイトル]</div> で始める。
            2. 「08:00 | 出発」のように、改行を多用して読みやすくすること。
            3. 各日の昼食と夕食は、その土地の「遺跡・文化・郷土料理」に関連する具体的な店や料理名を出すこと。
            4. 定期的に [IMAGE:地名や料理] を挿入。
            5. 最後に <div class="advice-section">AipiaAiのアドバイス</div> として、3つの具体的な秘境・文化の楽しみ方を書く。
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
                    # 改行をHTMLの<br>に変換してさらに読みやすく
                    st.markdown(part.replace("\n", "<br>"), unsafe_allow_html=True)
                else:
                    st.image(f"https://picsum.photos/seed/{part}/1200/500", caption=f"風景イメージ: {part}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="no-print" style="text-align:center; padding:20px;">
                    <a href="https://twitter.com/intent/tweet?text=Aipiaで最高の旅を計画しました！" target="_blank" style="background:#1DA1F2; color:white; padding:15px 30px; border-radius:30px; text-decoration:none; font-weight:bold;">X で共有</a>
                    <button onclick="window.print()" style="background:#111; color:white; padding:15px 30px; border:none; border-radius:30px; font-weight:bold; cursor:pointer; margin-left:10px;">PDF保存 / 印刷</button>
                </div>
            """, unsafe_allow_html=True)

    if st.button("最初に戻る"): st.session_state.step = "input"; st.session_state.final_plans = {}; st.rerun()
