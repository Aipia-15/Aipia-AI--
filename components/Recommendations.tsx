
import React from 'react';
import { Recommendation, Language } from '../types';

interface RecommendationsProps {
  items: Recommendation[];
  onSelect: (rec: Recommendation) => void;
  isLoading: boolean;
  language: Language;
}

const Recommendations: React.FC<RecommendationsProps> = ({ items, onSelect, isLoading }) => {
  if (isLoading && items.length === 0) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {[...Array(8)].map((_, i) => (
          <div key={i} className="aspect-square bg-slate-100 animate-pulse rounded-2xl"></div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-6 md:gap-8">
      {items.map((item, idx) => (
        <div 
          key={item.id}
          onClick={() => onSelect(item)}
          className="group cursor-pointer flex flex-col relative"
        >
          {/* 画像コンテナ */}
          <div className="aspect-square overflow-hidden border-[6px] border-white shadow-xl rounded-2xl relative transition-all duration-300 group-hover:shadow-2xl">
            <img 
              src={`${item.imageUrl}${item.imageUrl.includes('?') ? '&' : '?'}lock=${idx}`} 
              alt={item.title}
              className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
              loading="lazy"
            />
          </div>
          
          {/* テキストエリア */}
          <div className="relative -mt-10 mx-2 z-10">
            <div className="bg-slate-900/95 backdrop-blur-md p-3 rounded-xl border border-white/20 shadow-lg transform transition-transform group-hover:-translate-y-1">
              <h4 className="text-sm font-bold text-white leading-tight line-clamp-2 mb-1 group-hover:text-orange-400 transition-colors">
                {item.title}
              </h4>
              <div className="flex items-center text-[8px] font-black uppercase tracking-[0.2em]">
                <span className="text-orange-400">{item.prefecture}</span>
                <span className="mx-2 text-white/30">/</span>
                <span className="text-white/60">{item.genre}</span>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default Recommendations;
