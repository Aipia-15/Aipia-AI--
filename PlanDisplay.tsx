
import React, { useState } from 'react';
import { TravelPlan, TimelineItem, DayPlan, Language } from '../types';
import { translations } from '../translations';

interface PlanDisplayProps {
  plan: TravelPlan;
  isFavorite: boolean;
  onToggleFavorite: () => void;
  onUpdate?: (updatedPlan: TravelPlan) => void;
  isRefining?: boolean;
  language: Language;
}

const PlanDisplay: React.FC<PlanDisplayProps> = ({ 
  plan, 
  isFavorite, 
  onToggleFavorite, 
  onUpdate,
  isRefining,
  language
}) => {
  const t = translations[language];
  const [isEditing, setIsEditing] = useState(false);
  const [editedPlan, setEditedPlan] = useState<TravelPlan>(plan);

  const totalBudget = (Object.values(editedPlan.budgetBreakdown) as number[]).reduce((a, b) => a + b, 0);

  const handleSave = () => {
    if (onUpdate) onUpdate(editedPlan);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditedPlan(plan);
    setIsEditing(false);
  };

  const updateTimelineItem = (dayIdx: number, itemIdx: number, updates: Partial<TimelineItem>) => {
    const newDays = [...editedPlan.days];
    const newActivities = [...newDays[dayIdx].activities];
    newActivities[itemIdx] = { ...newActivities[itemIdx], ...updates };
    newDays[dayIdx] = { ...newDays[dayIdx], activities: newActivities };
    setEditedPlan({ ...editedPlan, days: newDays });
  };

  const updateAccommodation = (updates: Partial<typeof editedPlan.accommodation>) => {
    setEditedPlan({
      ...editedPlan,
      accommodation: { ...editedPlan.accommodation, ...updates }
    });
  };

  const addTimelineItem = (dayIdx: number) => {
    const newDays = [...editedPlan.days];
    const newItem: TimelineItem = { time: '12:00', action: 'New Spot', description: 'Edit this spot' };
    newDays[dayIdx] = { ...newDays[dayIdx], activities: [...newDays[dayIdx].activities, newItem] };
    setEditedPlan({ ...editedPlan, days: newDays });
  };

  const handleSendEmail = () => {
    const DEST_EMAIL = "2716soka@gmail.com";
    const subject = encodeURIComponent(`${t.planEmailSubject}: ${editedPlan.theme}`);
    
    let bodyText = `Theme: ${editedPlan.theme}\n`;
    bodyText += `Date: ${editedPlan.dateRange.start} - ${editedPlan.dateRange.end}\n\n`;
    
    editedPlan.days.forEach(day => {
      bodyText += `[${t.dayLabel} ${day.dayNumber}]\n`;
      day.activities.forEach(item => {
        bodyText += `- ${item.time}: ${item.action} (${item.description})\n`;
      });
      bodyText += `\n`;
    });

    bodyText += `\n[Accommodation]\nName: ${editedPlan.accommodation.name}\n${editedPlan.accommodation.description}\nCost: ${editedPlan.accommodation.estimatedCost}\nURL: ${editedPlan.accommodation.officialUrl || 'N/A'}\n`;
    bodyText += `\n[Est. Budget]\nTotal: ¥${totalBudget.toLocaleString()}\n`;
    
    const body = encodeURIComponent(bodyText);
    window.location.href = `mailto:${DEST_EMAIL}?subject=${subject}&body=${body}`;
  };

  if (isRefining) {
    return (
      <div className="bg-white border border-slate-200 rounded-3xl p-12 text-center space-y-6 shadow-xl animate-pulse">
        <h3 className="text-xl font-bold text-emerald-600">{t.aiRefining}</h3>
        <p className="text-slate-500 text-sm">{t.aiRefiningSub}</p>
      </div>
    );
  }

  return (
    <article className="animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="bg-white border border-slate-200 rounded-[2.5rem] overflow-hidden shadow-2xl">
        <div className="relative h-72 md:h-96">
          <img src={`https://picsum.photos/seed/${plan.id}/1200/800`} alt="Travel Theme" className="w-full h-full object-cover" />
          <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/40 to-transparent"></div>
          <div className="absolute bottom-8 left-8 right-8 flex items-end justify-between">
            <div className="max-w-2xl">
              <span className="text-emerald-400 text-[10px] font-black uppercase tracking-[0.4em] mb-2 block">{plan.durationDays} Days Uncharted Experience</span>
              <h3 className="text-4xl font-serif font-bold text-white leading-tight">{editedPlan.theme}</h3>
            </div>
            <div className="flex space-x-3 mb-1">
              <button onClick={handleSendEmail} title={t.sendPlanEmail} className="p-4 bg-white/10 backdrop-blur-md text-white border border-white/20 rounded-2xl hover:bg-white hover:text-emerald-600 transition-all shadow-xl active:scale-95">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </button>
              <button onClick={() => isEditing ? handleSave() : setIsEditing(true)} className={`p-4 backdrop-blur-md rounded-2xl shadow-xl transition-all border active:scale-95 ${isEditing ? 'bg-emerald-600 text-white border-emerald-500' : 'bg-white/10 text-white border-white/20 hover:bg-white hover:text-slate-900'}`}>
                {isEditing ? <span className="font-black text-lg">✓</span> : <span className="font-black text-lg">✎</span>}
              </button>
              <button 
                onClick={onToggleFavorite} 
                className={`p-4 backdrop-blur-md rounded-2xl shadow-xl transition-all flex items-center justify-center border active:scale-95 ${isFavorite ? 'bg-red-500 text-white border-red-400 scale-110 shadow-red-500/40 ring-4 ring-red-500/20' : 'bg-white/10 text-white border-white/20 hover:bg-white hover:text-red-500'}`}
              >
                <svg className="w-6 h-6" fill={isFavorite ? "currentColor" : "none"} stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <div className="p-8 md:p-12 space-y-16">
          {/* Timeline Section */}
          <section className="space-y-10">
            <h4 className="text-2xl font-bold text-slate-900 border-l-4 border-emerald-500 pl-4">{t.scheduleTitle}</h4>
            
            {editedPlan.days.map((day, dIdx) => (
              <div key={dIdx} className="space-y-6">
                <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                  <h5 className="text-xl font-black text-emerald-600 font-serif">
                    {language === 'ja' || language === 'ko' ? `${day.dayNumber}${t.dayLabel}` : `${t.dayLabel} ${day.dayNumber}`}
                  </h5>
                  {isEditing && (
                    <button onClick={() => addTimelineItem(dIdx)} className="text-emerald-600 text-sm font-bold hover:underline px-3 py-1 bg-emerald-50 rounded-lg">
                      + {t.addSpot}
                    </button>
                  )}
                </div>
                
                <div className="space-y-8 relative">
                  {day.activities.map((item, iIdx) => (
                    <div key={iIdx} className="relative pl-10">
                      {/* Vertical line connector */}
                      {iIdx !== day.activities.length - 1 && <div className="absolute left-[7px] top-6 bottom-[-32px] w-0.5 bg-slate-100"></div>}
                      <div className="absolute left-0 top-1.5 w-4 h-4 rounded-full border-4 border-white bg-emerald-500 shadow-sm z-10"></div>
                      
                      {isEditing ? (
                        <div className="space-y-3 bg-slate-50 p-6 rounded-2xl border border-slate-100">
                          <input value={item.time} onChange={(e) => updateTimelineItem(dIdx, iIdx, { time: e.target.value })} className="bg-white w-24 p-2 border border-slate-200 rounded-lg text-sm font-bold" />
                          <input value={item.action} onChange={(e) => updateTimelineItem(dIdx, iIdx, { action: e.target.value })} className="bg-white w-full p-2 border border-slate-200 rounded-lg text-lg font-bold" />
                          <textarea value={item.description} onChange={(e) => updateTimelineItem(dIdx, iIdx, { description: e.target.value })} className="bg-white w-full p-2 border border-slate-200 rounded-lg text-sm h-24" />
                        </div>
                      ) : (
                        <div className="space-y-3">
                          <div className="flex justify-between items-start gap-4">
                            <div>
                              <div className="text-emerald-600 text-xs font-black tracking-[0.2em] uppercase">{item.time}</div>
                              <div className="text-xl font-bold text-slate-900 leading-tight">{item.action}</div>
                            </div>
                            {item.officialUrl && (
                              <a 
                                href={item.officialUrl} 
                                target="_blank" 
                                rel="noopener noreferrer" 
                                className="flex-shrink-0 bg-white border border-slate-200 px-4 py-2 rounded-xl text-[10px] font-black text-emerald-600 uppercase tracking-widest hover:bg-emerald-600 hover:text-white transition-all whitespace-nowrap h-fit shadow-sm border-b-2"
                              >
                                {t.officialHP}
                              </a>
                            )}
                          </div>
                          <p className="text-slate-600 text-sm leading-relaxed max-w-2xl">{item.description}</p>
                          {item.departureStation && (
                            <div className="flex items-center space-x-2 text-[10px] text-emerald-800 font-black uppercase bg-emerald-50 border border-emerald-100/50 px-3 py-1.5 rounded-full w-fit">
                               <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M13 10V3L4 14h7v7l9-11h-7z" strokeWidth={2.5}/></svg>
                               <span>{item.departureStation} → {item.arrivalStation || '目的地'} | {item.detailedCost || '現地確認'}</span>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </section>

          {/* Accommodation Section */}
          <section className="space-y-6">
            <h4 className="text-2xl font-bold text-slate-900 border-l-4 border-emerald-500 pl-4">{t.accommodationTitle}</h4>
            <div className="bg-slate-50 p-8 rounded-[2rem] space-y-10 border border-slate-200 shadow-inner">
              {isEditing ? (
                <div className="space-y-6">
                  <div>
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block mb-2">Accommodation Name</label>
                    <input 
                      value={editedPlan.accommodation.name} 
                      onChange={(e) => updateAccommodation({ name: e.target.value })} 
                      className="bg-white w-full p-4 border border-slate-200 rounded-xl font-bold text-emerald-700 focus:ring-4 focus:ring-emerald-500/10 outline-none"
                    />
                  </div>
                  <div>
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block mb-2">Description</label>
                    <textarea 
                      value={editedPlan.accommodation.description} 
                      onChange={(e) => updateAccommodation({ description: e.target.value })} 
                      className="bg-white w-full p-4 border border-slate-200 rounded-xl text-slate-600 text-sm h-32 focus:ring-4 focus:ring-emerald-500/10 outline-none"
                    />
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block mb-2">Estimated Cost</label>
                      <input 
                        value={editedPlan.accommodation.estimatedCost} 
                        onChange={(e) => updateAccommodation({ estimatedCost: e.target.value })} 
                        className="bg-white w-full p-4 border border-slate-200 rounded-xl text-sm font-bold text-slate-900 focus:ring-4 focus:ring-emerald-500/10 outline-none"
                      />
                    </div>
                    <div>
                      <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block mb-2">Official Website URL</label>
                      <input 
                        value={editedPlan.accommodation.officialUrl || ''} 
                        onChange={(e) => updateAccommodation({ officialUrl: e.target.value })} 
                        className="bg-white w-full p-4 border border-slate-200 rounded-xl text-sm text-emerald-600 font-medium focus:ring-4 focus:ring-emerald-500/10 outline-none"
                      />
                    </div>
                  </div>
                </div>
              ) : (
                <div className="space-y-8">
                  <div className="flex justify-between items-start gap-8">
                    <div className="space-y-4">
                      <h5 className="text-4xl font-serif font-bold text-slate-900 leading-tight">{editedPlan.accommodation.name}</h5>
                      <p className="text-slate-600 text-sm leading-relaxed max-w-2xl">{editedPlan.accommodation.description}</p>
                    </div>
                  </div>
                  
                  <div className="flex flex-col sm:flex-row items-center gap-6">
                    <div className="bg-slate-900 text-white px-10 py-5 rounded-2xl flex items-center shadow-2xl w-full sm:w-auto">
                      <div className="mr-6 pr-6 border-r border-white/10">
                        <svg className="w-8 h-8 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                        </svg>
                      </div>
                      <div>
                        <span className="text-[10px] font-black uppercase tracking-[0.2em] opacity-50 block mb-1">Stay Budget</span>
                        <span className="text-3xl font-black">{editedPlan.accommodation.estimatedCost}</span>
                      </div>
                    </div>

                    {editedPlan.accommodation.officialUrl && (
                      <a 
                        href={editedPlan.accommodation.officialUrl} 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        className="bg-emerald-600 text-white px-10 py-5 rounded-2xl text-xs font-black uppercase tracking-[0.2em] flex items-center justify-center hover:bg-emerald-700 transition-all shadow-xl shadow-emerald-200 w-full sm:w-auto group whitespace-nowrap"
                      >
                        <span className="mr-3">{t.officialHP}</span>
                        <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                        </svg>
                      </a>
                    )}
                  </div>
                </div>
              )}
            </div>
          </section>

          {/* Budget Breakdown Section */}
          <section className="space-y-8">
            <h4 className="text-2xl font-bold text-slate-900 border-l-4 border-emerald-500 pl-4">{t.budgetBreakdown}</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              {[
                {label: t.budgetTransport, val: editedPlan.budgetBreakdown.transport, icon: '🚆'},
                {label: t.budgetAccommodation, val: editedPlan.budgetBreakdown.accommodation, icon: '🏨'},
                {label: t.budgetActivity, val: editedPlan.budgetBreakdown.activity, icon: '🏔️'},
                {label: t.budgetFood, val: editedPlan.budgetBreakdown.food, icon: '🍣'}
              ].map(item => (
                <div key={item.label} className="bg-white p-6 rounded-2xl border border-slate-100 text-center shadow-sm hover:shadow-md transition-all">
                  <div className="text-2xl mb-2">{item.icon}</div>
                  <div className="text-slate-400 text-[10px] font-black uppercase tracking-widest mb-1">{item.label}</div>
                  <div className="text-xl font-bold text-slate-900">¥{item.val.toLocaleString()}</div>
                </div>
              ))}
            </div>
            <div className="flex items-center justify-end space-x-4 border-t border-slate-100 pt-8">
              <span className="text-slate-400 font-bold uppercase tracking-widest text-xs">{t.totalBudget}</span>
              <span className="text-emerald-700 font-black text-4xl font-serif">¥{totalBudget.toLocaleString()}</span>
            </div>
          </section>

          {isEditing && (
            <div className="flex justify-end space-x-4 pt-8 border-t border-slate-100">
              <button onClick={handleCancel} className="px-8 py-3 bg-slate-100 rounded-xl font-black text-[10px] text-slate-500 uppercase tracking-widest hover:bg-slate-200 transition-all">{t.discard}</button>
              <button onClick={handleSave} className="px-8 py-3 bg-emerald-600 text-white rounded-xl font-black text-[10px] uppercase tracking-widest hover:bg-emerald-700 shadow-xl shadow-emerald-200 transition-all">{t.saveAndRefine}</button>
            </div>
          )}

          {/* Grounding Sources Section - Comply with Gemini Search grounding requirements */}
          {editedPlan.groundingSources && editedPlan.groundingSources.length > 0 && (
            <section className="space-y-6">
              <h4 className="text-2xl font-bold text-slate-900 border-l-4 border-emerald-500 pl-4">{t.grounding}</h4>
              <div className="flex flex-wrap gap-3">
                {editedPlan.groundingSources.map((source, idx) => (
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

          {/* Pro Tips Section */}
          <section className="bg-slate-900 rounded-[2.5rem] p-10 text-white relative overflow-hidden">
            <div className="absolute top-[-20%] right-[-10%] w-64 h-64 bg-emerald-500/20 blur-[100px] rounded-full"></div>
            <div className="relative z-10">
              <h4 className="text-xs font-black text-emerald-400 uppercase tracking-[0.4em] mb-8 flex items-center">
                <svg className="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 20 20"><path d="M11 3a1 1 0 10-2 0v1a1 1 0 102 0V3zM15.657 5.757a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707zM18 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM5.05 6.464A1 1 0 106.464 5.05l-.707-.707a1 1 0 00-1.414 1.414l.707.707zM5 10a1 1 0 01-1 1H3a1 1 0 110-2h1a1 1 0 011 1zM8 16v-1a1 1 0 112 0v1a1 1 0 11-2 0zM13 16v-1a1 1 0 112 0v1a1 1 0 11-2 0zM14.243 14.243a1 1 0 101.414-1.414l-.707-.707a1 1 0 10-1.414 1.414l.707.707zM5.757 14.243a1 1 0 10-1.414 1.414l.707.707a1 1 0 001.414-1.414l-.707-.707z" /></svg>
                {t.proTips}
              </h4>
              <ul className="space-y-6">
                {editedPlan.proTips.map((tip, idx) => (
                  <li key={idx} className="flex items-start group">
                    <span className="w-8 h-8 bg-white/10 rounded-xl flex items-center justify-center text-emerald-400 font-black text-xs mr-4 flex-shrink-0 group-hover:bg-emerald-500 group-hover:text-white transition-all">
                      {idx + 1}
                    </span>
                    <p className="text-slate-300 text-sm leading-relaxed pt-1">{tip}</p>
                  </li>
                ))}
              </ul>
            </div>
          </section>
        </div>
      </div>
    </article>
  );
};

export default PlanDisplay;