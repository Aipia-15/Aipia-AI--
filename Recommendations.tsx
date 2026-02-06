
import React, { useState } from 'react';
import { Recommendation, Language } from '../types';
import { translations } from '../translations';

interface RecommendationsProps {
  items: Recommendation[];
  onSelect: (rec: Recommendation) => void;
  isLoading: boolean;
  language: Language;
  onLoadMore?: () => void;
}

const Recommendations: React.FC<RecommendationsProps> = ({ items, onSelect, isLoading, language, onLoadMore }) => {
  const t = translations[language];
  const [isExpanded, setIsExpanded] = useState(false);

  const handleToggleExpand = () => {
    // データが10件未満で、まだ読み込める場合は読み込む
    if (!isExpanded && onLoadMore && items.length < 10) {
      onLoadMore();
    }
    setIsExpanded(!isExpanded);
  };

  const Card = ({ item }: { item: Recommendation }) => (
    <div 
      className="group bg-white border border-slate-200 rounded-[2rem] md:rounded-[2.5rem] overflow-hidden hover:border-emerald-500 hover:shadow-2xl hover:shadow-emerald-500/10 transition-all duration-500 flex flex-col shadow-sm w-full"
    >
      <div className="relative h-32 md:h-44 overflow-hidden cursor-pointer" onClick={() => onSelect(item)}>
        <img 
          src={item.imageUrl} 
          alt={item.title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-slate-900/60 via-transparent to-transparent opacity-60"></div>
        <div className="absolute bottom-3 left-3 md:bottom-4 md:left-4">
          <span className="bg-emerald-600/90 backdrop-blur-sm text-white text-[8px] md:text-[9px] font-black px-2 py-0.5 md:px-2.5 md:py-1 rounded-full uppercase tracking-widest">
            {item.genre}
          </span>
        </div>
      </div>

      <div className="p-4 md:p-6 flex-grow flex flex-col justify-between space-y-3 md:space-y-4">
        <div className="space-y-1 md:space-y-2 cursor-pointer" onClick={() => onSelect(item)}>
          <div className="flex items-center text-[8px] md:text-[10px] font-black text-emerald-600 uppercase tracking-widest space-x-1 md:space-x-2">
            <div className="flex items-center flex-shrink-0">
              <svg className="w-3 h-3 md:w-3.5 md:h-3.5 mr-0.5 md:mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span className="truncate max-w-[60px] md:max-w-none">{item.prefecture}</span>
            </div>
            <span className="text-slate-300">|</span>
            <span className="text-slate-600 font-bold bg-slate-50 px-1.5 py-0.5 rounded border border-slate-100 truncate max-w-[50px] md:max-w-[80px]">
              {(item as any).shortTitle || item.title.substring(0, 6)}
            </span>
          </div>

          <h4 className="text-sm md:text-xl font-bold text-slate-900 leading-tight group-hover:text-emerald-700 transition-colors line-clamp-1">
            {item.title}
          </h4>
          <p className="text-slate-500 text-[10px] md:text-xs leading-relaxed line-clamp-2">
            {item.description}
          </p>
        </div>

        <div className="space-y-3">
          {/* Grounding Sources - List URLs from groundingChunks as required */}
          {item.groundingSources && item.groundingSources.length > 0 && (
            <div className="flex flex-wrap gap-1.5 pt-1">
              {item.groundingSources.slice(0, 2).map((source, idx) => (
                <a 
                  key={idx} 
                  href={source.uri} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-[8px] md:text-[9px] text-slate-400 hover:text-emerald-600 underline truncate max-w-full"
                  onClick={(e) => e.stopPropagation()}
                >
                  {source.title}
                </a>
              ))}
            </div>
          )}

          <div 
            onClick={() => onSelect(item)}
            className="flex items-center text-emerald-600 text-[9px] md:text-[11px] font-black uppercase tracking-widest pt-2 md:pt-3 border-t border-slate-100 cursor-pointer"
          >
            <span>プランを生成</span>
            <span className="ml-1 md:ml-2 transition-transform group-hover:translate-x-1">→</span>
          </div>
        </div>
      </div>
    </div>
  );

  if (isLoading && items.length === 0) {
    return (
      <div className="flex space-x-4 overflow-x-hidden py-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="min-w-[280px] md:min-w-[320px] bg-slate-100 animate-pulse h-56 rounded-[2.5rem]"></div>
        ))}
      </div>
    );
  }

  return (
    <section className="space-y-4">
      {/* Header with Toggle Button */}
      <div className="flex items-center justify-between border-b border-slate-200 pb-2">
        <div className="flex items-center space-x-2">
          <div className="text-emerald-600 flex items-center justify-center p-0">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M5 2a1 1 0 011 1v1h1a1 1 0 010 2H6v1a1 1 0 01-2 0V6H3a1 1 0 010-2h1V3a1 1 0 011-1zm0 10a1 1 0 011 1v1h1a1 1 0 110 2H6v1a1 1 0 11-2 0v-1H3a1 1 0 110-2h1v-1a1 1 0 011-1zM12 2a1 1 0 01.967.744L14.146 7.2 17.5 9.134a1 1 0 010 1.732l-3.354 1.935-1.18 4.455a1 1 0 01-1.933 0L9.854 12.8 6.5 10.866a1 1 0 010-1.732l3.354-1.935 1.18-4.455A1 1 0 0112 2z" clipRule="evenodd" />
            </svg>
          </div>
          <h3 className="text-lg font-black text-slate-900 tracking-tight leading-none">
            {t.recsTitle}
          </h3>
        </div>
        <button 
          onClick={handleToggleExpand}
          className="text-[10px] font-black text-emerald-600 uppercase tracking-widest hover:text-emerald-700 flex items-center bg-emerald-50 px-3 py-1 rounded-full transition-all active:scale-95 shadow-sm border border-emerald-100"
        >
          {isExpanded ? '閉じる' : 'もっと見る'}
          <svg className={`ml-1 w-3 h-3 transition-transform duration-300 ${isExpanded ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>
      
      {!isExpanded ? (
        <div className="custom-scrollbar-container flex space-x-4 overflow-x-auto pb-6 -mx-4 px-4 scroll-smooth">
          {items.slice(0, 3).map((item) => (
            <div key={item.id} className="min-w-[280px] md:min-w-[320px] flex">
              <Card item={item} />
            </div>
          ))}
          {/* データが他にもある場合にトリガーを表示 */}
          {items.length > 3 && (
            <div 
              onClick={handleToggleExpand}
              className="min-w-[120px] md:min-w-[160px] bg-emerald-50 border-2 border-dashed border-emerald-200 rounded-[2.5rem] flex flex-col items-center justify-center text-emerald-600 cursor-pointer hover:bg-emerald-100 transition-all group active:scale-95"
            >
              <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center shadow-sm mb-2 group-hover:scale-110 transition-transform">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
              </div>
              <span className="text-[10px] font-black uppercase tracking-widest">More</span>
            </div>
          )}
          
          {isLoading && (
            <div className="min-w-[280px] bg-slate-50 animate-pulse h-72 rounded-[2.5rem] flex items-center justify-center text-slate-300 font-bold text-xs uppercase tracking-widest">
              Fetching...
            </div>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4 md:gap-6 pb-6 animate-in fade-in slide-in-from-top-4 duration-500">
          {items.map((item) => (
            <div key={item.id} className="flex">
              <Card item={item} />
            </div>
          ))}
          {isLoading && [1, 2, 3, 4].map(n => (
            <div key={n} className="bg-slate-50 animate-pulse h-48 md:h-72 rounded-[2.5rem]"></div>
          ))}
        </div>
      )}

      {/* 展開時のみ表示されるフッターボタン */}
      {isExpanded && items.length > 0 && (
        <div className="flex justify-center pb-4">
           <button 
             onClick={handleToggleExpand}
             className="px-8 py-3 bg-slate-100 text-slate-500 font-black text-[10px] uppercase tracking-widest rounded-full hover:bg-slate-200 transition-all active:scale-95"
           >
             閉じる
           </button>
        </div>
      )}

      <style>{`
        .custom-scrollbar-container::-webkit-scrollbar {
          height: 5px;
        }
        .custom-scrollbar-container::-webkit-scrollbar-track {
          background: #f1f5f9;
          border-radius: 10px;
        }
        .custom-scrollbar-container::-webkit-scrollbar-thumb {
          background: #cbd5e1;
          border-radius: 10px;
        }
        .custom-scrollbar-container::-webkit-scrollbar-thumb:hover {
          background: #94a3b8;
        }
      `}</style>
    </section>
  );
};

export default Recommendations;