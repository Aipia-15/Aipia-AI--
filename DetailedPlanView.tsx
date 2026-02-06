
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

  const handleSendEmail = () => {
    const DEST_EMAIL = "2716soka@gmail.com";
    const subject = encodeURIComponent(`${t.planEmailSubject}: ${plan.theme}`);
    
    let bodyText = `Theme: ${plan.theme}\n`;
    bodyText += `Date: ${plan.dateRange.start} - ${plan.dateRange.end}\n\n`;
    
    plan.days.forEach(day => {
      bodyText += `[${t.dayLabel} ${day.dayNumber}]\n`;
      day.activities.forEach(item => {
        bodyText += `- ${item.time}: ${item.action} (${item.description})\n`;
        if (item.transport) bodyText += `  Transport: ${item.departureStation || 'N/A'} -> ${item.arrivalStation || 'N/A'} (${item.departureTime || 'N/A'} - ${item.arrivalTime || 'N/A'})\n`;
      });
      bodyText += `\n`;
    });

    bodyText += `\n[Accommodation]\n${plan.accommodation.name}\n${plan.accommodation.description}\nCost: ${plan.accommodation.estimatedCost}\n`;
    
    const body = encodeURIComponent(bodyText);
    window.location.href = `mailto:${DEST_EMAIL}?subject=${subject}&body=${body}`;
  };

  return (
    <div className="bg-white border border-slate-200 rounded-[2.5rem] shadow-2xl overflow-hidden animate-in fade-in duration-700">
      {/* Booking Status Header */}
      {isBooked ? (
        <div className="bg-slate-900 text-white p-8 md:p-12 text-center space-y-4">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-emerald-500 rounded-full mb-2 shadow-lg animate-bounce">
            <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-3xl font-serif font-bold tracking-tight">{t.bookingSuccess}</h2>
          <p className="text-slate-400 text-sm max-w-lg mx-auto leading-relaxed">{t.bookingSuccessSub}</p>
          
          <div className="flex flex-wrap justify-center gap-4 pt-4">
            <a href="https://www.eki-net.com/pc/personal/top/index.html" target="_blank" rel="noopener noreferrer" className="bg-white/10 hover:bg-white/20 border border-white/20 px-6 py-3 rounded-2xl text-xs font-bold transition-all">
              {t.shinkansenBooking}
            </a>
            <a href="https://www.jalan.net/" target="_blank" rel="noopener noreferrer" className="bg-white/10 hover:bg-white/20 border border-white/20 px-6 py-3 rounded-2xl text-xs font-bold transition-all">
              {t.hotelBooking}
            </a>
            <a href="https://rent.toyota.co.jp/" target="_blank" rel="noopener noreferrer" className="bg-white/10 hover:bg-white/20 border border-white/20 px-6 py-3 rounded-2xl text-xs font-bold transition-all">
              {t.carRentalBooking}
            </a>
          </div>
        </div>
      ) : (
        <div className="bg-slate-50 border-b border-slate-200 p-6 md:p-8 flex flex-col md:flex-row items-center justify-between gap-4">
           <div className="flex items-center space-x-3">
             <div className="w-10 h-10 bg-amber-100 text-amber-600 rounded-full flex items-center justify-center">
               <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m0 0v2m0-2h2m-2 0H10m12-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
             </div>
             <div>
               <p className="text-sm font-bold text-slate-900">予約がまだ完了していません</p>
               <p className="text-xs text-slate-500">このプランで最終手続きへ進みますか？</p>
             </div>
           </div>
           <button 
             onClick={onBook}
             className="bg-emerald-600 hover:bg-emerald-700 text-white font-black px-8 py-4 rounded-2xl shadow-xl transition-all active:scale-95 flex items-center space-x-2 uppercase tracking-widest text-xs"
           >
             <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
             <span>{t.bookNow}</span>
           </button>
        </div>
      )}

      {/* Main Header */}
      <div className="bg-emerald-600 p-8 md:p-12 text-white relative overflow-hidden">
        <div className="absolute top-0 right-0 p-8 opacity-10">
          <svg className="w-32 h-32" fill="currentColor" viewBox="0 0 24 24">
            <path d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L16 4m0 13V4m0 0L9 7" />
          </svg>
        </div>
        <div className="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div className="space-y-2">
            <span className="text-emerald-100 text-[10px] font-black uppercase tracking-[0.3em]">{t.confirmedReview}</span>
            <h2 className="text-3xl md:text-5xl font-serif font-bold leading-tight">{plan.theme}</h2>
            <div className="flex items-center space-x-4 pt-2 opacity-90 text-sm font-medium">
              <span className="bg-white/20 px-3 py-1 rounded-full">{plan.dateRange.start} 〜 {plan.dateRange.end}</span>
              <span className="bg-white/20 px-3 py-1 rounded-full">{plan.durationDays} Days</span>
            </div>
          </div>
          <button 
            onClick={handleSendEmail}
            className="flex-shrink-0 bg-white/20 hover:bg-white/30 text-white font-bold px-6 py-3 rounded-2xl flex items-center space-x-2 transition-all border border-white/20"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            <span>{t.sendPlanEmail}</span>
          </button>
        </div>
      </div>

      <div className="p-6 md:p-12 space-y-16">
        {/* Detailed Timeline */}
        <section className="space-y-12">
          <h3 className="text-2xl font-bold text-slate-900 border-l-4 border-emerald-500 pl-4">{t.scheduleTitle}</h3>
          
          <div className="space-y-16">
            {plan.days.map((day, dayIdx) => (
              <div key={dayIdx} className="space-y-8">
                <div className="flex items-center space-x-4">
                  <div className="bg-emerald-600 text-white px-6 py-2 rounded-full font-serif font-bold">
                    {language === 'ja' || language === 'ko' ? `${day.dayNumber}${t.dayLabel}` : `${t.dayLabel} ${day.dayNumber}`}
                  </div>
                  <div className="h-px bg-slate-100 flex-grow"></div>
                </div>

                <div className="space-y-0">
                  {day.activities.map((item, idx) => (
                    <div key={idx} className="relative group">
                      {/* Connector line */}
                      {idx !== day.activities.length - 1 && (
                        <div className="absolute left-[39px] top-10 bottom-0 w-0.5 bg-slate-100 group-hover:bg-emerald-100 transition-colors"></div>
                      )}
                      
                      <div className="flex items-start space-x-6 pb-12">
                        <div className="flex-shrink-0 w-20 text-right pt-2">
                          <span className="text-emerald-600 font-serif font-bold text-lg">{item.time}</span>
                        </div>
                        
                        <div className="flex-shrink-0 relative z-10 pt-2.5">
                          <div className="w-4 h-4 rounded-full border-4 border-white bg-emerald-500 shadow-sm"></div>
                        </div>

                        <div className="flex-grow space-y-4 bg-slate-50/50 p-6 rounded-2xl group-hover:bg-emerald-50/50 transition-all border border-transparent hover:border-emerald-100">
                          <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                            <div className="space-y-1">
                              <h4 className="text-xl font-bold text-slate-900">{item.action}</h4>
                              <p className="text-slate-500 text-sm leading-relaxed">{item.description}</p>
                            </div>
                            
                            {item.officialUrl && (
                              <a 
                                href={item.officialUrl} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="flex-shrink-0 inline-flex items-center px-4 py-2 bg-white border border-slate-200 rounded-xl text-[10px] font-black text-emerald-600 hover:bg-emerald-600 hover:text-white transition-all shadow-sm h-fit whitespace-nowrap uppercase tracking-widest"
                              >
                                {t.officialHP}
                                <svg className="ml-1.5 w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                </svg>
                              </a>
                            )}
                          </div>

                          {/* Detailed Transport Box */}
                          {(item.transport || item.departureStation) && (
                            <div className="bg-white rounded-xl p-4 border border-slate-100 shadow-sm flex flex-col space-y-3">
                              <div className="flex items-center space-x-2 text-emerald-600">
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                </svg>
                                <span className="text-xs font-black uppercase tracking-widest">Transport Detail</span>
                              </div>
                              
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="flex justify-between items-center border-b border-slate-50 pb-2 md:border-b-0 md:pb-0">
                                  <div className="space-y-0.5">
                                    <p className="text-[10px] text-slate-400 font-bold uppercase">{t.stationDept}</p>
                                    <p className="text-sm font-bold text-slate-700">{item.departureStation || '近隣地点'}</p>
                                    <p className="text-xs text-emerald-600 font-serif font-bold">{item.departureTime || '-'}</p>
                                  </div>
                                  <svg className="w-4 h-4 text-slate-300 mx-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                                  </svg>
                                  <div className="space-y-0.5 text-right">
                                    <p className="text-[10px] text-slate-400 font-bold uppercase">{t.stationArr}</p>
                                    <p className="text-sm font-bold text-slate-700">{item.arrivalStation || '目的地'}</p>
                                    <p className="text-xs text-emerald-600 font-serif font-bold">{item.arrivalTime || '-'}</p>
                                  </div>
                                </div>
                                <div className="flex flex-col justify-center items-end bg-slate-50 p-3 rounded-lg">
                                  <p className="text-[10px] text-slate-400 font-bold uppercase">{t.cost}</p>
                                  <p className="text-sm font-serif font-bold text-slate-900">{item.detailedCost || '現地確認'}</p>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Accommodation Section */}
        <section className="space-y-6">
          <h3 className="text-2xl font-bold text-slate-900 border-l-4 border-emerald-500 pl-4">{t.accommodationTitle}</h3>
          <div className="bg-slate-900 rounded-3xl p-8 md:p-12 text-white relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-600/20 blur-[100px] rounded-full group-hover:bg-emerald-600/30 transition-all duration-700"></div>
            <div className="relative z-10 flex flex-col md:flex-row justify-between items-start gap-8">
              <div className="space-y-4">
                <h4 className="text-3xl font-serif font-bold text-emerald-400">{plan.accommodation.name}</h4>
                <p className="text-slate-300 max-w-xl leading-relaxed">{plan.accommodation.description}</p>
                <div className="inline-block px-4 py-2 bg-white/10 rounded-xl text-sm font-bold text-white">
                  Estimated Cost: <span className="text-emerald-400 ml-2">{plan.accommodation.estimatedCost}</span>
                </div>
              </div>
              
              {plan.accommodation.officialUrl && (
                <a 
                  href={plan.accommodation.officialUrl} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="bg-emerald-600 hover:bg-emerald-700 text-white font-black px-8 py-4 rounded-2xl transition-all shadow-xl shadow-emerald-900/40 flex items-center space-x-2 whitespace-nowrap uppercase text-xs tracking-widest border border-white/10"
                >
                  <span>{t.officialHP}</span>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              )}
            </div>
          </div>
        </section>

        {/* Grounding Sources Section - MUST ALWAYS list sources when Google Search is used */}
        {plan.groundingSources && plan.groundingSources.length > 0 && (
          <section className="space-y-6">
            <h3 className="text-2xl font-bold text-slate-900 border-l-4 border-emerald-500 pl-4">{t.grounding}</h3>
            <div className="flex flex-wrap gap-3">
              {plan.groundingSources.map((source, idx) => (
                <a 
                  key={idx} 
                  href={source.uri} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="bg-slate-50 border border-slate-200 px-4 py-2 rounded-xl text-xs font-medium text-slate-600 hover:bg-emerald-50 hover:text-emerald-600 transition-all flex items-center space-x-2 shadow-sm"
                >
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                  <span>{source.title}</span>
                </a>
              ))}
            </div>
          </section>
        )}

        {/* REFINED AD BANNER AT THE END (Yahoo-style) */}
        <section className="bg-white border border-slate-200 p-8 rounded-3xl flex flex-col sm:flex-row items-center gap-8 group cursor-pointer hover:bg-slate-50 transition-colors">
           <div className="w-full sm:w-48 h-32 bg-slate-100 rounded-lg flex-shrink-0 flex items-center justify-center border border-slate-200">
              <svg className="w-12 h-12 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
              </svg>
           </div>
           <div className="flex-grow space-y-3">
             <div className="flex items-center space-x-2">
               <span className="text-[10px] font-bold text-slate-400 border border-slate-300 px-1.5 py-0.5 rounded-[2px] uppercase">Ad</span>
               <span className="text-[11px] font-bold text-slate-400 uppercase tracking-widest">CKAWA Adventure Gear</span>
             </div>
             <h4 className="text-2xl font-bold text-slate-900 group-hover:text-blue-600 group-hover:underline leading-tight">
               秘境へ挑む。あなたの勇気を支える、最高品質のトラベルギア。
             </h4>
             <p className="text-slate-500 text-sm leading-relaxed">
               Aipiaコンシェルジュが推奨する「CKAWA」シリーズ。極限状態でも快適さを失わない、プロ仕様の装備を今すぐチェック。
             </p>
             <button className="text-[12px] font-black text-emerald-600 uppercase pt-2 group-hover:translate-x-1 transition-transform inline-flex items-center">
               <span>詳細を見る</span>
               <svg className="ml-1 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
             </button>
           </div>
        </section>

        {/* Pro Tips Footer */}
        <section className="bg-emerald-50/50 rounded-3xl p-8 border border-emerald-100">
          <h3 className="text-xs font-black text-emerald-600 uppercase tracking-[0.3em] mb-6">{t.proTips}</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {plan.proTips.map((tip, idx) => (
              <div key={idx} className="flex items-start space-x-3">
                <span className="flex-shrink-0 w-6 h-6 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center text-xs font-bold">{idx + 1}</span>
                <p className="text-slate-700 text-sm leading-relaxed">{tip}</p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
};

export default DetailedPlanView;