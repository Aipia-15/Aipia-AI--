
import React from 'react';
import { TravelPlan, Language } from '../types';
import { translations } from '../translations';

interface DetailedPlanViewProps {
  plan: TravelPlan;
  language: Language;
  isBooked?: boolean;
  onBook?: () => void;
}

const DetailedPlanView: React.FC<DetailedPlanViewProps> = ({ plan, language, isBooked, onBook }) => {
  const t = translations[language];
  
  // 安全なデータ取得
  const accommodations = Array.isArray(plan.accommodations) ? plan.accommodations : [];
  const selectedHotel = accommodations.find(a => a.id === plan.selectedAccommodationId) || accommodations[0];

  const handleSendEmail = () => {
    const DEST_EMAIL = "2716soka@gmail.com";
    const subject = encodeURIComponent(`${t.planEmailSubject}: ${plan.theme}`);
    let bodyText = `テーマ: ${plan.theme}\n日程: ${plan.dateRange?.start} - ${plan.dateRange?.end}\n\n`;
    
    plan.days?.forEach(day => {
      bodyText += `[${day.dayNumber}日目]\n`;
      day.activities?.forEach(item => {
        bodyText += `- ${item.time}: ${item.action}\n  詳細: ${item.description}\n`;
      });
      bodyText += `\n`;
    });

    if (selectedHotel) {
      bodyText += `\n[宿泊施設]\n${selectedHotel.name}\nURL: ${selectedHotel.officialUrl}\n`;
    }
    const body = encodeURIComponent(bodyText);
    window.location.href = `mailto:${DEST_EMAIL}?subject=${subject}&body=${body}`;
  };

  return (
    <div className="bg-white border border-slate-200 rounded-[3.5rem] shadow-2xl overflow-hidden animate-in fade-in duration-1000">
      {/* Header */}
      <div className="bg-slate-950 p-10 md:p-20 text-white relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <svg className="w-full h-full" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14.5v-9l6 4.5-6 4.5z"/></svg>
        </div>
        <div className="relative z-10 flex flex-col md:flex-row justify-between items-center gap-12">
          <div className="space-y-6 text-center md:text-left">
            <div className="inline-block bg-orange-500 text-white px-5 py-1.5 rounded-full text-[10px] font-black uppercase tracking-[0.4em] shadow-lg shadow-orange-500/20">Official Travel Guide</div>
            <h2 className="text-5xl md:text-7xl font-black tracking-tighter leading-tight italic">{plan.theme}</h2>
            <div className="flex flex-wrap items-center justify-center md:justify-start gap-4 pt-4 text-xs font-black uppercase tracking-widest text-white/40">
              <span className="bg-white/5 px-5 py-2 rounded-2xl border border-white/5">{plan.dateRange?.start} - {plan.dateRange?.end}</span>
              <span className="bg-white/5 px-5 py-2 rounded-2xl border border-white/5 uppercase">{plan.durationDays} 日間</span>
            </div>
          </div>
          <button onClick={handleSendEmail} className="bg-white text-slate-900 font-black px-10 py-5 rounded-[2rem] flex items-center space-x-3 transition-all hover:bg-orange-500 hover:text-white shadow-2xl active:scale-95 group">
            <svg className="w-6 h-6 group-hover:rotate-12 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
            <span className="text-sm uppercase tracking-widest">メールで保存</span>
          </button>
        </div>
      </div>

      <div className="p-8 md:p-16 space-y-24">
        {/* Timeline */}
        <section className="space-y-20">
          {plan.days?.map((day, dIdx) => (
            <div key={dIdx} className="space-y-12">
               <div className="flex items-center space-x-6">
                  <div className="bg-slate-900 text-white px-10 py-4 rounded-3xl font-black text-2xl shadow-2xl rotate-1">{day.dayNumber}日目</div>
                  <div className="h-px bg-slate-100 flex-grow"></div>
               </div>

               <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                 {day.activities?.map((act, aIdx) => (
                   <div key={aIdx} className={`relative p-8 rounded-[3rem] border transition-all flex flex-col justify-between bg-slate-50 border-slate-100 shadow-lg shadow-slate-200/50 hover:shadow-xl`}>
                     <div className="mb-8">
                       <div className="text-[10px] font-black text-slate-400 mb-2 font-mono tracking-widest">{act.time}</div>
                       <h4 className="text-2xl font-black text-slate-900 mb-4 tracking-tight">{act.action}</h4>
                       <p className="text-sm text-slate-600 leading-relaxed font-medium mb-8">{act.description}</p>
                     </div>
                     
                     {act.line && (
                       <div className="mb-4 text-xs font-black text-blue-600 bg-blue-50 px-4 py-2 rounded-xl inline-block w-fit">
                         {act.line}
                       </div>
                     )}
                   </div>
                 ))}
               </div>
            </div>
          ))}
        </section>

        {/* Accommodation Section */}
        {selectedHotel && (
          <section className="bg-slate-950 rounded-[4rem] p-10 md:p-20 text-white relative overflow-hidden shadow-[0_40px_100px_rgba(0,0,0,0.3)]">
            <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-orange-600/10 blur-[150px] rounded-full"></div>
            <div className="relative z-10 flex flex-col xl:flex-row gap-16 items-center">
               <div className="w-full xl:w-3/5 aspect-video bg-white/5 rounded-[3rem] overflow-hidden shadow-3xl border border-white/10 group">
                  <img src={selectedHotel.imageUrl} className="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-105" alt={selectedHotel.name} />
               </div>
               <div className="w-full xl:w-2/5 space-y-8">
                  <div className="inline-flex items-center space-x-3 text-orange-400 text-[12px] font-black uppercase tracking-[0.4em]">
                    <div className="w-6 h-px bg-orange-400"></div>
                    <span>宿泊のご提案</span>
                  </div>
                  <h4 className="text-5xl font-black leading-tight italic tracking-tighter">{selectedHotel.name}</h4>
                  <p className="text-slate-400 leading-relaxed text-base font-medium">{selectedHotel.description}</p>
                  <div className="flex flex-col sm:flex-row items-center justify-between gap-8 pt-10 border-t border-white/10">
                     <div>
                       <div className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2">Estimated Stay</div>
                       <div className="text-4xl font-black text-orange-500 italic">¥{(selectedHotel.estimatedCost || 0).toLocaleString()}</div>
                     </div>
                     <a href={selectedHotel.officialUrl} target="_blank" rel="noopener noreferrer" className="w-full sm:w-auto bg-white text-slate-950 hover:bg-orange-500 hover:text-white font-black px-12 py-5 rounded-3xl shadow-2xl transition-all active:scale-95 uppercase tracking-[0.2em] text-xs text-center">
                       詳細を確認
                     </a>
                  </div>
               </div>
            </div>
          </section>
        )}

        {/* Advice Section */}
        {plan.proTips && plan.proTips.length > 0 && (
          <section className="bg-slate-50 rounded-[4rem] p-12 md:p-20 border border-slate-100 shadow-inner">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-8 mb-16">
               <div className="space-y-2">
                  <h3 className="text-3xl font-black text-slate-950 tracking-tighter italic">Concierge Pro-Tips</h3>
                  <p className="text-slate-400 text-sm font-bold uppercase tracking-widest">現地を100%楽しむためのアドバイス</p>
               </div>
               <div className="w-20 h-20 bg-slate-950 text-white rounded-[2rem] flex items-center justify-center font-black text-3xl shadow-2xl rotate-6">!</div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">
               {plan.proTips.map((tip, i) => (
                 <div key={i} className="group bg-white p-8 rounded-[2.5rem] shadow-xl border border-slate-100/50 hover:-translate-y-2 transition-all duration-500">
                    <div className="text-orange-500 font-black text-xl italic mb-4 opacity-30 group-hover:opacity-100 transition-opacity">0{i+1}</div>
                    <p className="text-slate-800 text-sm font-bold leading-relaxed">{tip}</p>
                 </div>
               ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
};

export default DetailedPlanView;
