
import React, { useState } from 'react';
import { UserPreferences, Language } from '../types';
import { translations } from '../translations';

interface InputFormProps {
  onSubmit: (prefs: UserPreferences) => void;
  isLoading: boolean;
  language: Language;
}

const InputForm: React.FC<InputFormProps> = ({ onSubmit, isLoading, language }) => {
  const t = translations[language];
  
  const today = new Date().toISOString().split('T')[0];
  const tomorrow = new Date(Date.now() + 86400000).toISOString().split('T')[0];

  const [prefs, setPrefs] = useState<UserPreferences>({
    departure: '', 
    adults: 2,
    children: 0,
    genre: '未指定',
    prefecture: '',
    budget: 100000,
    startDate: today,
    endDate: tomorrow,
    keywords: '',
    language: language,
    walkingSpeed: 'normal'
  });

  return (
    <form onSubmit={(e) => { e.preventDefault(); onSubmit(prefs); }} className="flex flex-col items-center space-y-6 w-full max-w-5xl mx-auto px-1">
      {/* 検索キーワード */}
      <div className="relative w-full group">
        <div className="absolute -inset-1 bg-gradient-to-r from-orange-400 to-orange-600 rounded-2xl blur opacity-25 group-focus-within:opacity-50 transition duration-1000"></div>
        <input 
          type="text" 
          value={prefs.keywords}
          onChange={(e) => setPrefs({ ...prefs, keywords: e.target.value })}
          className="relative w-full bg-white border-2 border-slate-900 rounded-2xl px-6 py-5 pr-16 text-slate-900 font-black text-lg md:text-xl focus:ring-0 outline-none shadow-xl placeholder:text-slate-300"
          placeholder="キーワード・やりたいことでスポットを検索"
        />
        <button type="submit" className="absolute right-3 top-1/2 -translate-y-1/2 bg-slate-900 text-white p-3 rounded-xl hover:bg-orange-500 shadow-lg transition-all active:scale-95">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" strokeWidth={3}/></svg>
        </button>
      </div>

      {/* 詳細条件コンテナ */}
      <div className="w-full bg-white border-2 border-slate-100 rounded-[2rem] shadow-2xl flex flex-col divide-y divide-slate-100 overflow-hidden">
        
        {/* 出発・目的エリア */}
        <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-slate-100">
          <div className="px-6 py-5">
            <label className="text-[10px] font-black text-slate-400 uppercase mb-1 block tracking-widest">出発地</label>
            <div className="flex items-center space-x-3">
              <svg className="w-5 h-5 text-orange-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/></svg>
              <input 
                value={prefs.departure} 
                onChange={(e) => setPrefs({...prefs, departure: e.target.value})} 
                className="bg-transparent font-black text-slate-900 outline-none w-full text-base placeholder:text-slate-200" 
                placeholder="例：新宿駅" 
              />
            </div>
          </div>
          <div className="px-6 py-5">
            <label className="text-[10px] font-black text-slate-400 uppercase mb-1 block tracking-widest">目的地</label>
            <div className="flex items-center space-x-3">
              <svg className="w-5 h-5 text-cyan-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L16 4m0 13V4m0 0L9 7"/></svg>
              <input 
                value={prefs.prefecture} 
                onChange={(e) => setPrefs({...prefs, prefecture: e.target.value})} 
                className="bg-transparent font-black text-slate-900 outline-none w-full text-base placeholder:text-slate-200" 
                placeholder="指定なし（全国）" 
              />
            </div>
          </div>
        </div>

        {/* 日程・人数・予算 */}
        <div className="grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-slate-100">
          {/* 日程欄の完全修正 */}
          <div className="px-4 py-5">
            <label className="text-[10px] font-black text-slate-400 uppercase mb-2 block tracking-widest">日程</label>
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
              <input 
                type="date" 
                value={prefs.startDate} 
                min={today}
                onChange={(e) => setPrefs({...prefs, startDate: e.target.value})} 
                className="flex-1 min-w-0 bg-slate-50 rounded-xl px-2 py-2.5 font-black text-slate-900 outline-none text-[11px] border border-slate-100 focus:border-orange-500 transition-all" 
              />
              <span className="hidden sm:inline text-slate-300 font-black">~</span>
              <input 
                type="date" 
                value={prefs.endDate} 
                min={prefs.startDate || today}
                onChange={(e) => setPrefs({...prefs, endDate: e.target.value})} 
                className="flex-1 min-w-0 bg-slate-50 rounded-xl px-2 py-2.5 font-black text-slate-900 outline-none text-[11px] border border-slate-100 focus:border-orange-500 transition-all" 
              />
            </div>
          </div>

          <div className="px-6 py-5">
            <label className="text-[10px] font-black text-slate-400 uppercase mb-1 block tracking-widest">人数</label>
            <div className="flex items-center gap-2">
              <div className="flex items-center space-x-2 bg-slate-50 px-2 py-2 rounded-xl flex-1 justify-center border border-slate-100 min-w-0">
                <span className="text-[8px] font-black text-slate-400 uppercase">大人</span>
                <input 
                  type="number" 
                  value={prefs.adults} 
                  min="1" 
                  onChange={(e) => setPrefs({...prefs, adults: parseInt(e.target.value)})} 
                  className="w-full bg-transparent font-black text-slate-900 text-xs outline-none text-center" 
                />
              </div>
              <div className="flex items-center space-x-2 bg-slate-50 px-2 py-2 rounded-xl flex-1 justify-center border border-slate-100 min-w-0">
                <span className="text-[8px] font-black text-slate-400 uppercase">小人</span>
                <input 
                  type="number" 
                  value={prefs.children} 
                  min="0" 
                  onChange={(e) => setPrefs({...prefs, children: parseInt(e.target.value)})} 
                  className="w-full bg-transparent font-black text-slate-900 text-xs outline-none text-center" 
                />
              </div>
            </div>
          </div>

          <div className="px-6 py-5">
            <label className="text-[10px] font-black text-slate-400 uppercase mb-1 block tracking-widest">平均予算 (1人あたり)</label>
            <div className="flex items-center bg-slate-50 px-4 py-2 rounded-xl border border-slate-100">
              <span className="text-slate-400 font-black text-sm mr-2">¥</span>
              <input 
                type="number" 
                step="10000" 
                value={prefs.budget} 
                onChange={(e) => setPrefs({...prefs, budget: parseInt(e.target.value)})} 
                className="bg-transparent font-black text-slate-900 text-base w-full text-right outline-none" 
              />
              <span className="text-[9px] font-black text-slate-300 ml-2 uppercase">MAX</span>
            </div>
          </div>
        </div>
      </div>

      <button 
        type="submit" 
        disabled={isLoading} 
        className="w-full md:w-auto px-16 py-5 bg-slate-900 text-white rounded-2xl font-black text-sm uppercase tracking-widest shadow-2xl hover:bg-orange-600 active:scale-95 disabled:opacity-50 transition-all"
      >
        <span className="flex items-center justify-center gap-3">
          {isLoading ? (
            <>
              <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              <span>Analyzing...</span>
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M13 5l7 7-7 7M5 5l7 7-7 7"/></svg>
              <span>究極のスポットを探す</span>
            </>
          )}
        </span>
      </button>
    </form>
  );
};

export default InputForm;
