import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import urllib.parse

# --- 変数定義 ---
PREFECTURES = [""] + ["北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県", "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県", "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県", "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県", "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"]

# --- ページ設定 ---
st.set_page_config(layout="wide", page_title="Aipia - Hotel & Route Plan")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
MODEL = "llama-3.3-70b-versatile" 

# CSS: 視認性大幅向上（ホテルと移動を差別化）
st.markdown("""
    <style>
    .stApp { background-color: #F4F7F6; font-family: 'Noto Serif JP', serif; }
    .plan-container { max-width: 800px; margin: auto; }
    
    /* 日付ヘッダー */
    .day-header { background: #1A237E; color: white; padding: 10px 20px; border-radius: 8px; margin-top: 30px; font-size: 1.2rem; }
    
    /* 移動・道順のデザイン */
    .route-step { border-left: 3px dashed #9E9E9E; margin-left: 30px; padding: 10px 20px; color: #616161; font-size: 0.9rem; position: relative; }
    .route-step::before { content: '↓'; position: absolute; left: -11px; top: 0; background: #F4F7F6; }

    /* 目的地のデザイン */
    .spot-card { background: white; border-radius: 12px; padding: 20px; margin: 10px 0; border-left: 6px solid #00695C; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    
    /* ホテルのデザイン（特別仕様） */
    .hotel-card { background: #FFF9C4; border-radius: 12px; padding: 25px; margin: 15px 0; border: 2px solid #FBC02D; box-shadow: 0 6px 10px rgba(0,0,0,0.1); }
    .hotel-label { background: #FBC02D; color: #333; font-weight: bold; padding: 2px 10px; border-radius: 4px; font-size: 0.8rem; }
    
    .price-tag { color: #D32F2F; font-weight: bold; float: right; }
    .map-link { color: #1A237E; font-weight: bold; text-decoration: none; font-size: 0.85rem; border-bottom: 1px solid; }
    </style>
""", unsafe_allow_html=True)

# --- ロジック部 ---
if "step" not in st.session_state: st.session_state.step = "input"

st.title("⚜️ Aipia Luxury Travel Planner")

if st.session_state.step == "input":
    with st.form("input_form"):
        c1, c2 = st.columns(2)
        with c1: 
            dep = st.text_input("🛫 出発地", "新宿駅")
            dates = st.date_input("📅 日程", [datetime.now(), datetime.now() + timedelta(days=1)])
        with c2:
            pref = st.selectbox("📍 行き先(都道府県)", PREFECTURES)
            city = st.text_input("詳細エリア", "箱根")
        
        submitted = st.form_submit_button("この条件でホテルとルートを検索")
        if submitted:
            st.session_state.start_date = dates[0]
            st.session_state.dest = f"{pref}{city}"
            st.session_state.step = "generate"
            st.rerun()

elif st.session_state.step == "generate":
    with st.spinner("ホテルを確保し、移動ルートを計算中..."):
        # AIへの指示：移動手段、ホテル、日付を明確にする
        prompt = f"""
        {st.session_state.dest}への2日間の旅行プランを作成してください。
        開始日：{st.session_state.start_date.strftime('%Y年%m月%d日')}
        
        【条件】
        1. 1日目の夜に実在する「ホテル名」を必ず含め、そこを宿泊先として明記すること。
        2. 移動は「新宿駅〜小田急線〜箱根湯本駅」のように、路線名や道順を具体的に書くこと。
        3. 形式は必ず以下のパイプ区切りで出力すること。
        日付|時間|種別(移動/スポット/ホテル)|内容|具体的な道順・詳細|予算
        """
        
        res = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}])
        st.session_state.raw_plan = [l.split('|') for l in res.choices[0].message.content.split('\n') if '|' in l]
        st.session_state.step = "display"
        st.rerun()

elif st.session_state.step == "display":
    st.subheader(f"📍 {st.session_state.dest} 旅程表")
    
    current_day = ""
    for item in st.session_state.raw_plan:
        if len(item) < 5: continue
        day, time, category, title, detail, price = item[0], item[1], item[2], item[3], item[4], item[5]
        
        # 日付が変わったらヘッダーを表示
        if day != current_day:
            current_day = day
            st.markdown(f'<div class="day-header">📅 {day}</div>', unsafe_allow_html=True)
        
        # 種別ごとにデザインを出し分け
        if "移動" in category:
            st.markdown(f'<div class="route-step"><b>{time}</b>：{title}<br><small>{detail}</small></div>', unsafe_allow_html=True)
            
        elif "ホテル" in category or "宿泊" in title:
            st.markdown(f"""
            <div class="hotel-card">
                <span class="hotel-label">STAY / 宿泊</span>
                <span class="price-tag">{price}</span>
                <h3>🏨 {title}</h3>
                <p>{detail}</p>
                <a href="https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(title)}" class="map-link" target="_blank">📍 地図・空室状況を確認</a>
            </div>
            """, unsafe_allow_html=True)
            
        else: # スポット
            st.markdown(f"""
            <div class="spot-card">
                <span class="price-tag">{price}</span>
                <b>{time}</b>
                <h4>📍 {title}</h4>
                <p>{detail}</p>
                <a href="https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(title)}" class="map-link" target="_blank">Googleマップで道順を見る</a>
            </div>
            """, unsafe_allow_html=True)

    if st.button("条件を変えて作り直す"):
        st.session_state.step = "input"
        st.rerun()
