
import React from 'react';
import { Language } from '../types';
import { translations } from '../translations';

interface HeaderProps {
  activeTab: 'planner' | 'favorites' | 'history';
  onTabChange: (tab: 'planner' | 'favorites' | 'history') => void;
  language: Language;
  onLanguageChange: (lang: Language) => void;
}

const Header: React.FC<HeaderProps> = ({ activeTab, onTabChange, language, onLanguageChange }) => {
  const t = translations[language];

  const languageOptions: { value: Language; label: string; flag: string }[] = [
    { value: 'ja', label: '日本語', flag: '🇯🇵' },
    { value: 'en', label: 'English', flag: '🇺🇸' },
    { value: 'ko', label: '한국어', flag: '🇰🇷' },
    { value: 'es', label: 'Español', flag: '🇪🇸' },
    { value: 'de', label: 'Deutsch', flag: '🇩🇪' },
    { value: 'fr', label: 'Français', flag: '🇫🇷' },
  ];

  return (
    <header className="relative z-50 bg-white border-b border-slate-200 w-full">
      <div className="container mx-auto px-4 h-24 flex items-center justify-between max-w-[1500px]">
        <button 
          onClick={() => onTabChange('planner')}
          className="flex items-center space-x-5 hover:opacity-80 transition-all group"
        >
          <div className="w-14 h-14 bg-emerald-600 rounded-2xl flex items-center justify-center shadow-xl shadow-emerald-600/20 group-hover:scale-105 transition-transform">
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <span className="text-4xl font-serif font-black text-slate-900 tracking-tighter italic">Aipia</span>
        </button>

        <nav className="hidden md:flex items-center space-x-12">
          <button 
            onClick={() => onTabChange('planner')}
            className={`text-[12px] font-black uppercase tracking-widest transition-colors ${activeTab === 'planner' ? 'text-emerald-600 underline underline-offset-8' : 'text-slate-500 hover:text-slate-900'}`}
          >
            {t.planner}
          </button>
          <button 
            onClick={() => onTabChange('history')}
            className={`text-[12px] font-black uppercase tracking-widest transition-colors ${activeTab === 'history' ? 'text-emerald-600 underline underline-offset-8' : 'text-slate-500 hover:text-slate-900'}`}
          >
            {t.history}
          </button>
          <button 
            onClick={() => onTabChange('favorites')}
            className={`text-[12px] font-black uppercase tracking-widest transition-colors ${activeTab === 'favorites' ? 'text-emerald-600 underline underline-offset-8' : 'text-slate-500 hover:text-slate-900'}`}
          >
            {t.favorites}
          </button>
        </nav>

        <div className="flex items-center">
          <div className="relative">
            <select
              value={language}
              onChange={(e) => onLanguageChange(e.target.value as Language)}
              className="appearance-none bg-slate-50 border border-slate-200 rounded-xl pl-5 pr-12 py-3 text-[12px] font-black text-slate-700 focus:ring-8 focus:ring-emerald-500/10 cursor-pointer transition-all hover:bg-white shadow-sm"
            >
              {languageOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.flag} {opt.label}
                </option>
              ))}
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-4">
              <svg className="h-4 w-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
