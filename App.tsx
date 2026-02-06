
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { UserPreferences, TravelPlan, FavoriteItem, Recommendation, Language } from './types';
import { generatePlanDeViaje, fetchAIRecommendations, refinePlanWithAI, generateDetailedLogistics } from './geminiService';
import { translations } from './translations';
import Header from './components/Header';
import InputForm from './components/InputForm';
import PlanDisplay from './components/PlanDisplay';
import FavoriteList from './components/FavoriteList';
import HistoryList from './components/HistoryList';
import Recommendations from './components/Recommendations';
import MascotSlideshow from './components/MascotSlideshow';
import DetailedPlanView from './components/DetailedPlanView';

const NativeAd = ({ title, advertiser, desc }: { title: string; advertiser: string; desc: string }) => (
  <div className="bg-white border-b border-slate-200 p-6 hover:bg-slate-50 transition-colors cursor-pointer group mb-px">
    <div className="flex flex-col gap-4">
      <div className="w-full h-40 bg-slate-100 rounded-xl flex-shrink-0 flex items-center justify-center border border-slate-200 overflow-hidden relative">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-50 to-slate-200 opacity-50"></div>
        <svg className="w-12 h-12 text-slate-300 relative z-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </div>
      <div className="flex-grow min-w-0">
        <h4 className="text-[15px] font-bold text-slate-900 leading-snug mb-2 group-hover:text-blue-600 group-hover:underline line-clamp-2">
          {title}
        </h4>
        <p className="text-[12px] text-slate-500 line-clamp-3 leading-relaxed mb-4">
          {desc}
        </p>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-[9px] font-black text-slate-400 border border-slate-300 px-2 py-0.5 rounded-[3px] uppercase">AD</span>
            <span className="text-[11px] font-bold text-slate-400 truncate max-w-[130px]">{advertiser}</span>
          </div>
          <button className="text-[11px] font-black text-blue-600 uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-opacity">Visit Site</button>
        </div>
      </div>
    </div>
  </div>
);

const App: React.FC = () => {
  const [language, setLanguage] = useState<Language>('ja');
  const [activeTab, setActiveTab] = useState<'planner' | 'favorites' | 'history'>('planner');
  const [loading, setLoading] = useState(false);
  const [isResearching, setIsResearching] = useState(false);
  const [isConfirmingDeparture, setIsConfirmingDeparture] = useState(false);
  const [pendingFinalizeItem, setPendingFinalizeItem] = useState<FavoriteItem | null>(null);
  const [tempDeparture, setTempDeparture] = useState("");
  
  const [refiningId, setRefiningId] = useState<string | null>(null);
  const [currentPlans, setCurrentPlans] = useState<TravelPlan[]>([]);
  const [selectedPlanIndex, setSelectedPlanIndex] = useState(0);
  const [favorites, setFavorites] = useState<FavoriteItem[]>([]);
  const [history, setHistory] = useState<TravelPlan[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loadingRecs, setLoadingRecs] = useState(false);
  const [error, setError] = useState<{ message: string; type: 'quota' | 'general' } | null>(null);
  const [lastPrefs, setLastPrefs] = useState<UserPreferences | null>(null);
  const [isOffline, setIsOffline] = useState(!navigator.onLine);
  
  const [finalizedPlanId, setFinalizedPlanId] = useState<string | null>(null);
  const [bookedPlanId, setBookedPlanId] = useState<string | null>(null);

  const activeDetailedPlanItem = favorites.find(f => f.plan.id === finalizedPlanId);
  const planDisplayRef = useRef<HTMLDivElement>(null);
  const t = translations[language];

  useEffect(() => {
    const handleOnline = () => setIsOffline(false);
    const handleOffline = () => setIsOffline(true);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    const savedFavs = localStorage.getItem('plandeviaje_favorites');
    if (savedFavs) {
      try { setFavorites(JSON.parse(savedFavs)); } catch (e) { console.error(e); }
    }
    const savedHist = localStorage.getItem('plandeviaje_history');
    if (savedHist) {
      try { setHistory(JSON.parse(savedHist)); } catch (e) { console.error(e); }
    }
    const savedLang = localStorage.getItem('plandeviaje_lang') as Language;
    if (savedLang) setLanguage(savedLang);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  useEffect(() => {
    localStorage.setItem('plandeviaje_favorites', JSON.stringify(favorites));
  }, [favorites]);

  useEffect(() => {
    localStorage.setItem('plandeviaje_history', JSON.stringify(history));
  }, [history]);

  useEffect(() => {
    localStorage.setItem('plandeviaje_lang', language);
    if (!isOffline) {
      const loadInitialRecs = async () => {
        setLoadingRecs(true);
        try {
          const recs = await fetchAIRecommendations(language, 10);
          setRecommendations(recs);
        } catch (e) {
          console.warn("Recommendations skipped.");
        }
        setLoadingRecs(false);
      };
      loadInitialRecs();
    }
  }, [language, isOffline]);

  const loadMoreRecommendations = async () => {
    if (loadingRecs || isOffline || recommendations.length >= 10) return;
    setLoadingRecs(true);
    try {
      const moreRecs = await fetchAIRecommendations(language, 10);
      setRecommendations(moreRecs);
    } catch (e) {
      console.warn("Failed to load more recommendations");
    } finally {
      setLoadingRecs(false);
    }
  };

  const handleGeneratePlan = async (prefs: UserPreferences) => {
    setLoading(true);
    setError(null);
    setCurrentPlans([]);
    setSelectedPlanIndex(0);
    setLastPrefs(prefs);
    setTempDeparture(prefs.departure);
    setFinalizedPlanId(null);
    setBookedPlanId(null);
    try {
      const plans = await generatePlanDeViaje(prefs);
      setCurrentPlans(plans);
      setHistory(prev => {
        const newHist = [...plans, ...prev];
        return newHist.slice(0, 20);
      });
    } catch (err: any) {
      setError({ message: "生成エラーが発生しました。", type: 'general' });
    } finally {
      setLoading(false);
    }
  };

  const toggleFavorite = useCallback((plan: TravelPlan) => {
    setFavorites(prev => {
      const exists = prev.find(f => f.plan.id === plan.id);
      if (exists) return prev.filter(f => f.plan.id !== plan.id);
      return [{ id: crypto.randomUUID(), plan }, ...prev];
    });
  }, []);

  const onFinalizeClick = (item: FavoriteItem) => {
    setPendingFinalizeItem(item);
    setTempDeparture(""); // 出発地を完全に空白にする
    setIsConfirmingDeparture(true);
  };

  const handleFinalizeConfirmed = async () => {
    if (!pendingFinalizeItem || !lastPrefs) return;
    setIsConfirmingDeparture(false);
    setIsResearching(true);
    setFinalizedPlanId(pendingFinalizeItem.plan.id);
    const prefsWithNewDeparture = { ...lastPrefs, departure: tempDeparture || lastPrefs.departure };
    try {
      const detailed = await generateDetailedLogistics(pendingFinalizeItem.plan, prefsWithNewDeparture);
      setFavorites(prev => prev.map(item => 
        item.plan.id === pendingFinalizeItem.plan.id 
          ? { ...item, isFinalized: true, detailedPlan: detailed } 
          : item
      ));
    } catch (err) {
      console.error("Research failed", err);
    } finally {
      setIsResearching(false);
      setPendingFinalizeItem(null);
    }
  };

  return (
    <div className="min-h-screen flex flex-col pb-safe bg-[#f9fafb]">
      {/* Header naturally flows with page */}
      <Header activeTab={activeTab} onTabChange={(tab) => { setActiveTab(tab); setFinalizedPlanId(null); setBookedPlanId(null); }} language={language} onLanguageChange={setLanguage} />

      {/* Main Grid: Sync Scroll Layout - sidebars flow naturally with main content */}
      <div className="flex-grow flex justify-center items-start container mx-auto px-4 max-w-[1500px] gap-10 py-6 relative">
        
        {/* LEFT SIDEBAR (Equal Width: w-72) */}
        <aside className="hidden xl:block w-72 flex-shrink-0 space-y-6 pt-4">
          <div className="bg-white border border-slate-200 rounded-3xl overflow-hidden shadow-sm">
            <div className="px-5 py-3 bg-slate-50 border-b border-slate-200">
              <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.25em]">Featured Ad</span>
            </div>
            <NativeAd 
              title="【限定】今、大人が選ぶべき最高峰のプライベート温泉宿10選"
              advertiser="LuxuryTravel.jp"
              desc="大切な人と過ごす、一生に一度の贅沢。AIコンシェルジュが選んだ極上の宿を特別価格で。"
            />
            <NativeAd 
              title="秘境巡りに最適。スマホ1つで荷物をホテルへ配送するスマート旅術"
              advertiser="EasyCargo Service"
              desc="重い荷物からの解放。全国どこでも当日配送可能な新サービス。未知の景色を身軽に体験。"
            />
          </div>
          
          <div className="bg-slate-900 rounded-[2.5rem] p-8 text-white shadow-xl relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/20 blur-3xl group-hover:bg-emerald-500/30 transition-all"></div>
            <h4 className="font-serif font-bold text-2xl mb-4 relative z-10 italic tracking-tight">Premium</h4>
            <p className="text-xs text-slate-400 leading-relaxed mb-8 relative z-10">
              より深い秘境データへのアクセス機能。
            </p>
            <button className="w-full py-4 bg-emerald-600 text-white font-black text-[11px] uppercase tracking-widest rounded-2xl hover:bg-emerald-500 transition-all relative z-10 shadow-lg shadow-emerald-900/40 active:scale-95">
              Explore
            </button>
          </div>
        </aside>

        {/* MAIN CONTENT AREA */}
        <main className="flex-grow max-w-4xl min-w-0 pt-4">
          {isResearching ? (
            <div className="flex flex-col items-center justify-center py-20 space-y-10">
              <div className="text-center space-y-4">
                <h2 className="text-4xl font-serif font-bold text-emerald-600 italic">{t.researchingDetail}</h2>
                <p className="text-slate-500 text-sm max-w-md mx-auto leading-relaxed">{t.researchingSub}</p>
              </div>
              <MascotSlideshow language={language} />
            </div>
          ) : activeDetailedPlanItem && activeDetailedPlanItem.detailedPlan ? (
            <div className="space-y-10">
              <button onClick={() => { setFinalizedPlanId(null); setBookedPlanId(null); }} className="flex items-center text-slate-500 font-bold text-sm hover:text-emerald-600 transition-colors bg-white px-6 py-3 rounded-full border border-slate-200 shadow-sm w-fit active:scale-95">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
                {t.backToList}
              </button>
              <DetailedPlanView 
                plan={activeDetailedPlanItem.detailedPlan} 
                language={language} 
                isBooked={activeDetailedPlanItem.plan.id === bookedPlanId} 
                onBook={() => setBookedPlanId(activeDetailedPlanItem.plan.id)}
              />
            </div>
          ) : activeTab === 'planner' ? (
            <div className="space-y-12">
              <section className="text-center space-y-8 mb-8 pt-4">
                <h2 className="text-6xl md:text-8xl font-serif font-bold text-slate-900 tracking-tighter italic leading-tight">
                  {t.heroTitle}
                </h2>
                <p className="text-slate-500 text-lg md:text-xl font-serif font-medium tracking-widest max-w-3xl mx-auto border-t border-b border-slate-200 py-8 uppercase text-[13px] md:text-[15px] opacity-80 leading-loose">
                  {t.heroSub}
                </p>
              </section>
              
              <Recommendations 
                items={recommendations} 
                language={language} 
                onSelect={(rec) => handleGeneratePlan({ departure: '', adults: 2, children: 0, genre: rec.genre, prefecture: rec.prefecture, budget: 50000, startDate: new Date(Date.now() + 7 * 86400000).toISOString().split('T')[0], endDate: new Date(Date.now() + 9 * 86400000).toISOString().split('T')[0], keywords: rec.title, language: language, walkingSpeed: 'normal' })} 
                isLoading={loadingRecs}
                onLoadMore={loadMoreRecommendations}
              />
              
              <div className="space-y-8">
                 <h3 className="text-3xl font-serif font-bold text-slate-900 italic tracking-tight">Custom Travel Design</h3>
                 <InputForm onSubmit={handleGeneratePlan} isLoading={loading} language={language} />
              </div>

              {loading && (
                <div className="flex flex-col items-center justify-center py-20 space-y-10">
                  <p className="text-3xl font-serif italic text-emerald-600 animate-pulse">{t.thinking}</p>
                  <MascotSlideshow language={language} />
                </div>
              )}
              
              {currentPlans.length > 0 && (
                <div ref={planDisplayRef} className="space-y-16 pt-6">
                  <div className="flex justify-center space-x-5 overflow-x-auto no-scrollbar pb-4">
                    {currentPlans.map((plan, idx) => (
                      <button key={plan.id} onClick={() => setSelectedPlanIndex(idx)} className={`px-10 py-4 rounded-full text-[11px] font-black uppercase tracking-[0.35em] border transition-all ${selectedPlanIndex === idx ? 'bg-emerald-600 text-white border-emerald-600 shadow-2xl scale-105' : 'bg-white text-slate-500 border-slate-200 hover:border-emerald-300 shadow-sm'}`}>Proposal {idx + 1}</button>
                    ))}
                  </div>
                  {currentPlans[selectedPlanIndex] && <PlanDisplay plan={currentPlans[selectedPlanIndex]} isFavorite={!!favorites.find(f => f.plan.id === currentPlans[selectedPlanIndex].id)} onToggleFavorite={() => toggleFavorite(currentPlans[selectedPlanIndex])} onUpdate={(p) => setCurrentPlans(prev => prev.map(old => old.id === p.id ? p : old))} isRefining={refiningId === currentPlans[selectedPlanIndex].id} language={language} />}
                </div>
              )}
            </div>
          ) : activeTab === 'favorites' ? (
            <FavoriteList favorites={favorites} onRemove={(id) => setFavorites(f => f.filter(item => item.id !== id))} onSelect={(plan) => { setCurrentPlans([plan]); setSelectedPlanIndex(0); setActiveTab('planner'); }} onFinalize={onFinalizeClick} onBook={(id) => setBookedPlanId(id)} language={language} />
          ) : (
            <HistoryList history={history} onSelect={(plan) => { setCurrentPlans([plan]); setSelectedPlanIndex(0); setActiveTab('planner'); }} onClear={() => setHistory([])} onToggleFavorite={toggleFavorite} favorites={favorites} language={language} />
          )}
        </main>

        {/* RIGHT SIDEBAR (Equal Width: w-72) */}
        <aside className="hidden xl:block w-72 flex-shrink-0 space-y-6 pt-4">
          <div className="bg-white border border-slate-200 rounded-3xl overflow-hidden shadow-sm">
            <div className="px-5 py-3 bg-slate-50 border-b border-slate-200">
              <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.25em]">Concierge Pick</span>
            </div>
            <NativeAd 
              title="地元の人が通う、本当の名店。裏路地の隠れ家レストランをAIが発見"
              advertiser="Gourmet Search AI"
              desc="観光客向けではない、真の郷土料理。当日キャンセル枠をリアルタイムで通知します。"
            />
            <NativeAd 
              title="【衝撃】秘境でのデジタルデトックスが脳に与える驚きの効果とは？"
              advertiser="Mindfulness Travel"
              desc="スマホを置いて、自然の音に身を委ねる。現代人に必要な「何もしない贅沢」を。"
            />
          </div>
          
          <div className="bg-emerald-50 border border-emerald-100 rounded-[2.5rem] p-8 shadow-inner">
            <h4 className="font-serif font-bold text-xl text-emerald-900 mb-4 italic">Update Info</h4>
            <div className="w-full h-1.5 bg-white rounded-full overflow-hidden shadow-sm">
              <div className="h-full w-4/5 bg-emerald-500"></div>
            </div>
          </div>
        </aside>
      </div>

      {/* FOOTER AREA - Shorter margin as requested */}
      <footer className="mt-8 border-t border-slate-200 bg-white py-16 relative overflow-hidden">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-6xl h-px bg-gradient-to-r from-transparent via-slate-200 to-transparent"></div>
        <div className="container mx-auto px-4 max-w-4xl text-center space-y-10">
          <div className="space-y-6">
             <h2 className="text-5xl md:text-6xl font-serif font-bold text-slate-900 tracking-tighter italic">Aipia</h2>
             <div className="space-y-4">
               <p className="text-slate-600 text-sm md:text-lg font-serif font-medium max-w-2xl mx-auto leading-loose italic opacity-90">
                 あなたの望む秘境への旅行プランをAIが提案します。<br className="hidden md:block" />
                 人生を変えるような新たなAIの新境地をぜひご体験ください。
               </p>
             </div>
          </div>
          <div className="pt-8 border-t border-slate-100 flex flex-col items-center space-y-4">
             <div className="flex items-center space-x-6">
               <span className="w-10 h-px bg-slate-200"></span>
               <span className="text-[11px] font-black text-slate-400 uppercase tracking-[0.45em]">2025-2026 / Aipia / GCIS</span>
               <span className="w-10 h-px bg-slate-200"></span>
             </div>
             <p className="text-[10px] text-slate-300 font-bold uppercase tracking-[0.2em] opacity-80">Digital Sanctuary for Modern Travelers</p>
          </div>
        </div>
      </footer>

      {isConfirmingDeparture && (
        <div className="fixed inset-0 z-[100] bg-slate-900/80 backdrop-blur-xl flex items-center justify-center p-4">
          <div className="bg-white rounded-[3.5rem] p-12 md:p-16 w-full max-w-2xl shadow-2xl animate-in zoom-in-95 duration-500 space-y-10 border border-slate-100">
            <div className="text-center space-y-4">
              <h2 className="text-4xl font-serif font-bold text-slate-900 italic tracking-tight">{t.confirmDepartureTitle}</h2>
              <p className="text-slate-500 text-base leading-relaxed">{t.confirmDepartureSub}</p>
            </div>
            <div className="space-y-4">
              <label className="text-[11px] font-black text-slate-400 uppercase tracking-[0.35em] ml-3">{t.departure}</label>
              <input 
                type="text" 
                value={tempDeparture}
                onChange={(e) => setTempDeparture(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-3xl px-8 py-6 text-slate-900 font-bold text-lg focus:ring-8 focus:ring-emerald-500/10 outline-none transition-all placeholder:text-slate-300 shadow-inner"
                placeholder={t.departurePlaceholder}
                autoFocus
              />
            </div>
            <div className="flex flex-col space-y-5 pt-4">
              <button 
                onClick={handleFinalizeConfirmed}
                className="w-full py-6 bg-emerald-600 text-white font-black text-[13px] uppercase tracking-widest rounded-[2rem] hover:bg-emerald-500 transition-all shadow-2xl shadow-emerald-200 active:scale-[0.98]"
              >
                {t.confirmFinalize}
              </button>
              <button 
                onClick={() => setIsConfirmingDeparture(false)}
                className="w-full py-6 bg-slate-100 text-slate-500 font-black text-[13px] uppercase tracking-widest rounded-[2rem] hover:bg-slate-200 transition-all"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
