
import React from 'react';
import { FavoriteItem, TravelPlan, Language } from '../types';
import { translations } from '../translations';

interface FavoriteListProps {
  favorites: FavoriteItem[];
  onRemove: (id: string) => void;
  onSelect: (plan: TravelPlan) => void;
  onFinalize: (item: FavoriteItem) => void;
  onBook: (planId: string) => void;
  language: Language;
}

const FavoriteList: React.FC<FavoriteListProps> = ({ favorites, onRemove, onSelect, onFinalize, onBook, language }) => {
  const t = translations[language];

  const handleBookNow = (item: FavoriteItem) => {
    onBook(item.plan.id);
  };

  if (favorites.length === 0) {
    return (
      <div className="text-center py-20 space-y-4">
        <h3 className="text-xl font-bold text-slate-900">{t.noFavorites}</h3>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-serif font-bold text-slate-900 mb-8">{t.favorites}</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {favorites.map((item) => (
          <div 
            key={item.id} 
            className={`group bg-white border rounded-3xl overflow-hidden hover:shadow-xl transition-all flex flex-col ${item.isFinalized ? 'border-emerald-500 ring-2 ring-emerald-500/20 shadow-lg' : 'border-slate-200'}`}
          >
            <div className="relative h-40 cursor-pointer" onClick={() => onSelect(item.plan)}>
              <img src={`https://picsum.photos/seed/${item.plan.id}/600/400`} alt={item.plan.theme} className="w-full h-full object-cover" />
              <button 
                onClick={(e) => { e.stopPropagation(); onRemove(item.id); }} 
                className="absolute top-3 right-3 p-2 bg-white/90 hover:bg-white text-slate-500 hover:text-red-500 rounded-full shadow-sm transition-colors"
              >
                ✕
              </button>
              {item.isFinalized && (
                <div className="absolute top-3 left-3 px-3 py-1 bg-emerald-600 text-white text-[10px] font-black uppercase rounded-full shadow-lg">
                  Finalized
                </div>
              )}
            </div>
            
            <div className="p-6 flex-grow flex flex-col justify-between space-y-4">
              <div className="cursor-pointer" onClick={() => onSelect(item.plan)}>
                <h3 className="text-lg font-bold text-slate-900 line-clamp-2 leading-tight mb-2">{item.plan.theme}</h3>
                <div className="text-emerald-600 text-xs font-bold uppercase tracking-wider">{t.backToPlanner}</div>
              </div>
              
              <div className="space-y-2">
                <button 
                  onClick={() => onFinalize(item)}
                  className={`w-full py-3 rounded-xl font-bold text-sm transition-all shadow-sm ${
                    item.isFinalized 
                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-200 hover:bg-emerald-100' 
                    : 'bg-emerald-600 text-white hover:bg-emerald-700 shadow-emerald-200'
                  }`}
                >
                  {item.isFinalized ? t.finalizedHeader : t.finalize}
                </button>
                {item.isFinalized && (
                  <button 
                    onClick={() => handleBookNow(item)}
                    className="w-full py-3 bg-slate-900 text-white hover:bg-slate-800 rounded-xl font-bold text-sm transition-all shadow-md active:scale-95 flex items-center justify-center space-x-2"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                    </svg>
                    <span>{t.bookNow}</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FavoriteList;
