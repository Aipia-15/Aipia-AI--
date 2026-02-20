import streamlit as st
from openai import OpenAI

# 1. APIキーの設定（管理画面から後で入力します）
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("My AI App (OpenAI Edition)")

# 2. AI Studioから持ってきた「指示」をここに貼る
SYSTEM_PROMPT = """import React from 'react';
import { TravelPlan, Language, FavoriteItem } from '../types';
import { translations } from '../translations';

interface HistoryListProps {
  history: TravelPlan[];
  onSelect: (plan: TravelPlan) => void;
  onClear: () => void;
  onToggleFavorite: (plan: TravelPlan) => void;
  favorites: FavoriteItem[];
  language: Language;
}

const HistoryList: React.FC<HistoryListProps> = ({ history, onSelect, onClear, onToggleFavorite, favorites, language }) => {
  const t = translations[language];

  if (history.length === 0) {
    return (
      <div className="text-center py-20 space-y-4">
        <h3 className="text-xl font-bold text-slate-900">{t.noHistory}</h3>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-2xl font-serif font-bold text-slate-900">{t.history}</h2>
        <button 
          onClick={onClear}
          className="text-xs font-bold text-red-500 hover:text-red-700 transition-colors uppercase tracking-widest"
        >
          {t.clearHistory}
        </button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {history.map((plan) => {
          const isFavorite = !!favorites.find(f => f.plan.id === plan.id);
          return (
            <div 
              key={plan.id} 
              className="bg-white border border-slate-100 rounded-2xl p-4 flex items-center space-x-4 hover:shadow-lg hover:border-emerald-200 transition-all group"
            >
              <div 
                className="w-16 h-16 rounded-xl overflow-hidden flex-shrink-0 cursor-pointer"
                onClick={() => onSelect(plan)}
              >
                <img src={`https://picsum.photos/seed/${plan.id}/200/200`} alt="" className="w-full h-full object-cover group-hover:scale-110 transition-transform" />
              </div>
              
              <div className="flex-grow min-w-0">
                <h3 
                  className="font-bold text-slate-900 truncate cursor-pointer hover:text-emerald-600 transition-colors"
                  onClick={() => onSelect(plan)}
                >
                  {plan.theme}
                </h3>
                <div className="flex items-center text-[10px] text-slate-400 font-bold space-x-2">
                  <span>{plan.dateRange.start}</span>
                  <span className="w-1 h-1 bg-slate-200 rounded-full"></span>
                  <span>{plan.durationDays} Days</span>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <button 
                  onClick={() => onToggleFavorite(plan)}
                  className={`p-2 rounded-full transition-all ${isFavorite ? 'bg-red-50 text-red-500' : 'bg-slate-50 text-slate-300 hover:text-red-400'}`}
                >
                  <svg className="w-5 h-5" fill={isFavorite ? "currentColor" : "none"} stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                </button>
                <button 
                  onClick={() => onSelect(plan)}
                  className="p-2 bg-emerald-50 text-emerald-600 rounded-full hover:bg-emerald-100 transition-all"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};"""

export default HistoryList;
" 

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# チャット履歴の表示
for msg in st.session_state.messages:
    if msg["role"] != "system":
        st.chat_message(msg["role"]).write(msg["content"])

# 入力処理
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # OpenAIで回答生成
    response = client.chat.completions.create(
        model="gpt-4o-mini", # 安くて賢いモデル
        messages=st.session_state.messages
    )
    
    answer = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)
