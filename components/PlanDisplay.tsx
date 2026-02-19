
import React, { useMemo } from 'react';
import { TravelPlan, Language } from '../types';

interface PlanDisplayProps {
  plan: TravelPlan;
  isFavorite: boolean;
  onToggleFavorite: () => void;
  language: Language;
}

const PlanDisplay: React.FC<PlanDisplayProps> = ({ plan, isFavorite, onToggleFavorite }) => {
  const activity = plan.days[0].activities[0];
  
  const imageUrl = useMemo(() => {
    const keywords = (plan.imageKeyword || "japan landscape").split(' ').join(',');
    const seed = Math.abs(plan.theme.split('').reduce((a, b) => { a = ((a << 5) - a) + b.charCodeAt(0); return a & a; }, 0) % 1000);
    return `https://loremflickr.com/800/600/${encodeURIComponent(keywords)},nature/all?lock=${seed}`;
  }, [plan.id, plan.theme, plan.imageKeyword]);

  return (
    <div className="w-full flex items-center justify-center p-4 lg:p-6 animate-in zoom-in-95 duration-500">
      <div className="bg-white w-full max-w-5xl rounded-[3rem] overflow-hidden shadow-[0_30px_60px_rgba(0,0,0,0.08)] relative border border-white hover:shadow-2xl transition-all duration-500 group">
        <div className="grid grid-cols-1 lg:grid-cols-2">
          <div className="aspect-[4/3] lg:aspect-auto relative overflow-hidden bg-slate-100">
            <img 
              src={imageUrl} 
              className="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-105" 
              alt={plan.theme} 
              onError={(e) => {
                (e.target as HTMLImageElement).src = `https://loremflickr.com/800/600/japan,nature?lock=${plan.id.length}`;
              }}
            />
            <div className="absolute top-6 left-6 bg-orange-600 text-white px-5 py-2 rounded-2xl text-[10px] font-black uppercase tracking-[0.2em] shadow-2xl backdrop-blur-md bg-opacity-90">
               Premium Choice
            </div>
            <div className="absolute inset-0 bg-gradient-to-t from-black/30 via-transparent to-transparent pointer-events-none"></div>
          </div>

          <div className="p-8 md:p-12 flex flex-col bg-white">
            <div className="flex justify-between items-start mb-8">
              <div className="space-y-2 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-orange-500 rounded-full"></span>
                  <span className="text-[11px] font-black text-slate-400 uppercase tracking-[0.3em] truncate">{activity.arrivalStation || "目的地"}</span>
                </div>
                <h3 className="text-3xl md:text-4xl font-black text-slate-900 tracking-tighter leading-tight italic group-hover:text-orange-600 transition-colors truncate">
                  {plan.theme}
                </h3>
              </div>
              <button 
                onClick={onToggleFavorite} 
                className={`p-3 md:p-4 rounded-[1.5rem] transition-all transform hover:scale-110 shadow-xl flex-shrink-0 ${isFavorite ? 'bg-orange-500 text-white' : 'bg-slate-50 text-slate-200 hover:text-orange-400 border border-slate-100'}`}
              >
                <svg className="w-6 h-6 md:w-7 md:h-7 fill-current" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              </button>
            </div>

            <p className="text-slate-500 text-sm md:text-base leading-relaxed font-medium mb-8 line-clamp-3 md:line-clamp-4">
              {activity.description}
            </p>

            <div className="space-y-4 mb-8">
               <div className="flex items-start gap-4">
                  <div className="w-8 h-8 md:w-10 md:h-10 rounded-2xl bg-orange-50 flex items-center justify-center text-orange-600 flex-shrink-0 border border-orange-100/50">
                    <svg className="w-4 h-4 md:w-5 md:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/></svg>
                  </div>
                  <div className="min-w-0">
                    <p className="text-[9px] font-black text-slate-300 uppercase tracking-widest mb-1.5">Highlights</p>
                    <div className="flex flex-wrap gap-2">
                       {activity.nearbyFood && <span className="text-[10px] font-bold text-slate-700 bg-slate-50 px-3 py-1 rounded-lg border border-slate-100 truncate max-w-[120px]">🍴 {activity.nearbyFood}</span>}
                       {activity.nearbyLandmark && <span className="text-[10px] font-bold text-slate-700 bg-slate-50 px-3 py-1 rounded-lg border border-slate-100 truncate max-w-[120px]">📸 {activity.nearbyLandmark}</span>}
                       {activity.nearbySecret && <span className="text-[10px] font-bold text-purple-700 bg-purple-50 px-3 py-1 rounded-lg border border-purple-100 italic truncate max-w-[120px]">✨ {activity.nearbySecret}</span>}
                    </div>
                  </div>
               </div>
            </div>

            <div className="mt-auto flex items-end justify-between pt-8 border-t border-slate-100">
               <div>
                  <span className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Cost</span>
                  <div className="flex items-baseline gap-1">
                    <span className="text-3xl font-black text-slate-900 italic tracking-tighter">¥{(plan.budgetBreakdown?.activity || 0).toLocaleString()}</span>
                    <span className="text-[9px] font-bold text-slate-300 italic uppercase">/pp</span>
                  </div>
               </div>
               <button 
                  onClick={onToggleFavorite}
                  className={`px-8 py-4 rounded-[2rem] text-[10px] font-black uppercase tracking-widest transition-all active:scale-95 shadow-lg ${isFavorite ? 'bg-orange-50 text-orange-600 border border-orange-200' : 'bg-slate-950 text-white hover:bg-orange-600'}`}
               >
                  {isFavorite ? 'Saved' : 'Select'}
               </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PlanDisplay;
