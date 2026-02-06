
import React, { useState, useEffect } from 'react';
import { UserPreferences, Language, WalkingSpeed } from '../types';
import { translations } from '../translations';

interface InputFormProps {
  onSubmit: (prefs: UserPreferences) => void;
  isLoading: boolean;
  language: Language;
}

const InputForm: React.FC<InputFormProps> = ({ onSubmit, isLoading, language }) => {
  const t = translations[language];

  const getLocalDateString = (date: Date) => {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  };

  const now = new Date();
  const today = getLocalDateString(now);
  const maxDateObj = new Date();
  maxDateObj.setFullYear(now.getFullYear() + 10);
  const maxDate = getLocalDateString(maxDateObj);

  const [prefs, setPrefs] = useState<UserPreferences>({
    departure: '',
    adults: 0,
    children: 0,
    genre: '未指定',
    prefecture: '',
    budget: 50000,
    startDate: '',
    endDate: '',
    keywords: '',
    language: language,
    walkingSpeed: 'normal'
  });

  useEffect(() => {
    setPrefs(prev => ({ 
      ...prev, 
      language
    }));
  }, [language]);

  const handleStartDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newStartDate = e.target.value;
    setPrefs(prev => ({ 
      ...prev, 
      startDate: newStartDate,
      endDate: newStartDate 
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!prefs.keywords.trim() && !prefs.prefecture.trim()) {
      alert(language === 'ja' ? '「目的地」または「キーワード」を入力してください。' : 'Please enter destination or keywords.');
      return;
    }
    if (!prefs.startDate || !prefs.endDate) {
      alert(language === 'ja' ? '日程を入力してください。' : 'Please enter dates.');
      return;
    }
    onSubmit(prefs);
  };

  const getGenreList = (lang: Language) => {
    switch(lang) {
      case 'ko': return ['미지정', '온천과 자연', '비경 및 폐허 탐색', '역사와 건축', '최고의 현지 음식', '아웃도어/모험'];
      case 'es': return ['No especificado', 'Termas y Naturaleza', 'Lugares Ocultos', 'Historia y Arquitectura', 'Gastronomía Local', 'Aventura'];
      case 'de': return ['Nicht angegeben', 'Onsen & Natur', 'Geheimtipps', 'Geschichte & Architektur', 'Lokale Gourmet', 'Abenteuer'];
      case 'fr': return ['Non spécifié', 'Onsen & Nature', 'Lieux cachés', 'Histoire & Architecture', 'Gourmet local', 'Aventure'];
      case 'en': return ['Not Specified', 'Onsen & Nature', 'Hidden Sites', 'History & Architecture', 'Local Gourmet', 'Adventure'];
      default: return ['未指定', '温泉と自然', '秘境・廃墟探索', '歴史と建築', '絶品ローカルフード', 'アウトドア・冒険'];
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white border border-slate-200 p-6 md:p-10 rounded-[2.5rem] space-y-8 shadow-2xl shadow-slate-200/50 relative">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="space-y-2">
          <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">{t.departure}</label>
          <input 
            type="text" 
            value={prefs.departure}
            onChange={(e) => setPrefs({ ...prefs, departure: e.target.value })}
            className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-5 py-4 text-slate-900 font-bold focus:ring-4 focus:ring-emerald-500/10 outline-none transition-all placeholder:text-slate-300"
            placeholder={t.departurePlaceholder}
            required
          />
        </div>

        <div className="space-y-2">
          <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">{t.destination} <span className="text-[8px] font-normal ml-2">{t.optional}</span></label>
          <input 
            type="text" 
            value={prefs.prefecture}
            onChange={(e) => setPrefs({ ...prefs, prefecture: e.target.value })}
            className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-5 py-4 text-slate-900 font-bold focus:ring-4 focus:ring-emerald-500/10 outline-none transition-all"
          />
        </div>

        <div className="space-y-2">
          <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">{t.startDate}</label>
          <input 
            type="date" 
            min={today}
            max={maxDate}
            value={prefs.startDate}
            onChange={handleStartDateChange}
            className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-5 py-4 text-slate-900 font-bold focus:ring-4 focus:ring-emerald-500/10 outline-none transition-all"
            required
          />
        </div>

        <div className="space-y-2">
          <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">{t.endDate}</label>
          <input 
            type="date" 
            min={prefs.startDate || today}
            max={maxDate}
            value={prefs.endDate}
            onChange={(e) => setPrefs({ ...prefs, endDate: e.target.value })}
            className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-5 py-4 text-slate-900 font-bold focus:ring-4 focus:ring-emerald-500/10 outline-none transition-all"
            required
          />
        </div>

        <div className="space-y-2 md:col-span-2">
          <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">{t.walkingSpeed}</label>
          <div className="grid grid-cols-3 gap-3">
            {(['slow', 'normal', 'fast'] as WalkingSpeed[]).map((speed) => (
              <button
                key={speed}
                type="button"
                onClick={() => setPrefs({ ...prefs, walkingSpeed: speed })}
                className={`py-3 px-4 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all border ${prefs.walkingSpeed === speed ? 'bg-emerald-600 text-white border-emerald-600 shadow-lg' : 'bg-white text-slate-400 border-slate-200 hover:border-emerald-200'}`}
              >
                {speed === 'slow' ? t.speedSlow : speed === 'fast' ? t.speedFast : t.speedNormal}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-2 md:col-span-2">
          <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">{t.genre}</label>
          <select 
            value={prefs.genre}
            onChange={(e) => setPrefs({ ...prefs, genre: e.target.value })}
            className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-5 py-4 text-slate-900 font-bold focus:ring-4 focus:ring-emerald-500/10 outline-none transition-all appearance-none"
          >
            {getGenreList(language).map(g => <option key={g} value={g}>{g}</option>)}
          </select>
        </div>

        <div className="space-y-2 md:col-span-2">
          <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1 flex justify-between items-center">
            <span>{t.budget}</span>
            <span className="text-emerald-600 font-serif font-bold text-xl">¥{prefs.budget.toLocaleString()} {t.budgetSuffix}</span>
          </label>
          <input 
            type="range" min="1000" max="500000" step="1000" value={prefs.budget}
            onChange={(e) => setPrefs({ ...prefs, budget: parseInt(e.target.value) })}
            className="w-full h-2 bg-slate-100 rounded-lg appearance-none cursor-pointer accent-emerald-600"
          />
        </div>

        <div className="space-y-2 md:col-span-2">
          <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">{t.keywords}</label>
          <input 
            type="text" 
            value={prefs.keywords}
            onChange={(e) => setPrefs({ ...prefs, keywords: e.target.value })}
            className="w-full bg-slate-50 border-2 border-emerald-100/50 rounded-2xl px-6 py-5 text-slate-900 font-bold focus:ring-4 focus:ring-emerald-500/10 outline-none transition-all shadow-inner"
            placeholder="例：絶景、地ビール、静かな宿"
          />
          <p className="text-[9px] text-slate-400 mt-1 ml-1">{t.keywordsSub}</p>
        </div>
      </div>

      <button 
        type="submit" disabled={isLoading}
        className="w-full bg-slate-900 hover:bg-emerald-600 text-white font-black py-5 rounded-2xl shadow-2xl transition-all flex items-center justify-center space-x-3 disabled:opacity-50 uppercase tracking-[0.2em] text-xs"
      >
        {isLoading ? (
          <>
            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
            <span>{t.searching}</span>
          </>
        ) : (
          <>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" strokeWidth={3}/></svg>
            <span>{t.submit}</span>
          </>
        )}
      </button>
    </form>
  );
};

export default InputForm;
