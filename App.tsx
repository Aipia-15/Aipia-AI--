
import React, { useState, useEffect, useCallback } from 'react';
import { UserPreferences, TravelPlan, FavoriteItem, Recommendation, Language } from './types';
import { generatePlanDeViaje, fetchAIRecommendations } from './geminiService';
import { translations } from './translations';
import InputForm from './components/InputForm';
import PlanDisplay from './components/PlanDisplay';
import FavoriteList from './components/FavoriteList';
import HistoryList from './components/HistoryList';
import Recommendations from './components/Recommendations';
import MascotSlideshow from './components/MascotSlideshow';
import PlanEditor from './components/PlanEditor';
import DetailedPlanView from './components/DetailedPlanView';

const App: React.FC = () => {
  const [language, setLanguage] = useState<Language>('ja');
  const [activeTab, setActiveTab] = useState<'planner' | 'favorites' | 'history'>('planner');
  const [loading, setLoading] = useState(false);
  const [currentPlans, setCurrentPlans] = useState<TravelPlan[]>([]);
  const [favorites, setFavorites] = useState<FavoriteItem[]>([]);
  const [history, setHistory] = useState<TravelPlan[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loadingRecs, setLoadingRecs] = useState(false);
  
  const [isEditingPlan, setIsEditingPlan] = useState(false);
  const [isShowingPrep, setIsShowingPrep] = useState(false); // プラン生成前の詳細設定表示
  const [finalizedPlan, setFinalizedPlan] = useState<TravelPlan | null>(null);

  const [searchPrefs, setSearchPrefs] = useState<UserPreferences>({
    departure: '', adults: 2, children: 0, genre: '未指定', prefecture: '', budget: 100000,
    startDate: '', endDate: '', keywords: '', language: 'ja', walkingSpeed: 'normal'
  });

  useEffect(() => {
    const savedFavs = localStorage.getItem('plandeviaje_favorites');
    if (savedFavs) {
      try { setFavorites(JSON.parse(savedFavs)); } catch (e) {}
    }
    const loadInitialRecs = async () => {
      setLoadingRecs(true);
      try {
        const recs = await fetchAIRecommendations(language, 8);
        setRecommendations(recs);
      } catch (e) {}
      setLoadingRecs(false);
    };
    loadInitialRecs();
  }, [language]);

  const handleGeneratePlan = async (prefs: UserPreferences) => {
    setLoading(true);
    setCurrentPlans([]);
    setFinalizedPlan(null);
    setSearchPrefs(prefs);
    try {
      const plans = await generatePlanDeViaje(prefs);
      setCurrentPlans(plans);
      if (plans.length > 0) setHistory(prev => [plans[0], ...prev].slice(0, 20));
    } catch (err: any) {
      alert("プラン生成中にエラーが発生しました。");
    } finally {
      setLoading(false);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const toggleFavorite = useCallback((plan: TravelPlan) => {
    setFavorites(prev => {
      const exists = prev.find(f => f.plan.id === plan.id);
      const newFavs = exists ? prev.filter(f => f.plan.id !== plan.id) : [{ id: crypto.randomUUID(), plan }, ...prev];
      localStorage.setItem('plandeviaje_favorites', JSON.stringify(newFavs));
      return newFavs;
    });
  }, []);

  const handleFinalizePlan = (plan: TravelPlan) => {
    setFinalizedPlan(plan);
    setIsEditingPlan(false);
    setActiveTab('planner');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const startPlanEditing = (prepPrefs: Partial<UserPreferences>) => {
    setSearchPrefs(prev => ({ ...prev, ...prepPrefs }));
    setIsShowingPrep(false);
    setIsEditingPlan(true);
  };

  if (isEditingPlan) {
    return <PlanEditor 
      favorites={favorites} 
      searchPrefs={searchPrefs} 
      onBack={() => setIsEditingPlan(false)} 
      onFinalize={handleFinalizePlan}
      language={language} 
    />;
  }

  return (
    <div className="min-h-screen flex flex-col relative overflow-x-hidden font-sans bg-[#fffbeb]">
      {/* Detail Prep Modal */}
      {isShowingPrep && (
        <div className="fixed inset-0 z-[1000] bg-slate-900/60 backdrop-blur-md flex items-center justify-center p-4 animate-in fade-in duration-300">
          <div className="bg-white w-full max-w-lg rounded-[2.5rem] p-8 md:p-12 shadow-2xl space-y-8 animate-in zoom-in-95 duration-300">
            <h2 className="text-2xl font-black italic tracking-tighter text-slate-900 text-center">こだわりを最終確認</h2>
            <div className="space-y-6">
              <div>
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block mb-2">宿泊スタイル</label>
                <div className="grid grid-cols-2 gap-2">
                  {['旅館（和風）', 'ホテル（洋風）', 'コスパ重視', '最高級ラグジュアリー'].map(t => (
                    <button key={t} onClick={() => setSearchPrefs(p => ({...p, accommodationType: t}))} className={`px-4 py-3 rounded-xl text-xs font-bold transition-all ${searchPrefs.accommodationType === t ? 'bg-orange-500 text-white shadow-lg' : 'bg-slate-50 text-slate-600 hover:bg-slate-100'}`}>{t}</button>
                  ))}
                </div>
              </div>
              <div>
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block mb-2">移動の優先順位</label>
                <div className="grid grid-cols-2 gap-2">
                  {['公共交通機関', 'タクシー・送迎', '徒歩・散策多め', '効率重視'].map(m => (
                    <button key={m} onClick={() => setSearchPrefs(p => ({...p, transportPreference: m}))} className={`px-4 py-3 rounded-xl text-xs font-bold transition-all ${searchPrefs.transportPreference === m ? 'bg-orange-500 text-white shadow-lg' : 'bg-slate-50 text-slate-600 hover:bg-slate-100'}`}>{m}</button>
                  ))}
                </div>
              </div>
            </div>
            <div className="flex gap-4">
              <button onClick={() => setIsShowingPrep(false)} className="flex-1 py-4 bg-slate-100 text-slate-600 rounded-2xl font-black text-xs uppercase tracking-widest">キャンセル</button>
              <button onClick={() => startPlanEditing({})} className="flex-2 py-4 bg-slate-950 text-white rounded-2xl font-black text-xs uppercase tracking-widest shadow-xl active:scale-95 transition-all">プランを5案生成</button>
            </div>
          </div>
        </div>
      )}

      <div className="relative z-10 flex flex-col min-h-screen">
        <nav className="sticky top-0 z-[100] bg-white/70 backdrop-blur-2xl border-b border-white shadow-sm px-6 md:px-12 h-20 flex items-center justify-between">
          <div className="flex items-center space-x-12">
            <button onClick={() => {setCurrentPlans([]); setFinalizedPlan(null); setActiveTab('planner');}} className="text-3xl font-black text-slate-900 tracking-tighter italic hover:scale-105 transition-transform">Aipia</button>
            <div className="hidden md:flex items-center space-x-8">
              <button onClick={() => {setFinalizedPlan(null); setActiveTab('planner');}} className={`text-xs font-black uppercase tracking-[0.2em] transition-all ${activeTab === 'planner' && !finalizedPlan ? 'text-orange-600 border-b-2 border-orange-600 pb-1' : 'text-slate-400 hover:text-slate-600'}`}>Planner</button>
              <button onClick={() => {setFinalizedPlan(null); setActiveTab('favorites');}} className={`text-xs font-black uppercase tracking-[0.2em] transition-all ${activeTab === 'favorites' ? 'text-orange-600 border-b-2 border-orange-600 pb-1' : 'text-slate-400 hover:text-slate-600'}`}>Favorites</button>
              <button onClick={() => {setFinalizedPlan(null); setActiveTab('history');}} className={`text-xs font-black uppercase tracking-[0.2em] transition-all ${activeTab === 'history' ? 'text-orange-600 border-b-2 border-orange-600 pb-1' : 'text-slate-400 hover:text-slate-600'}`}>History</button>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value as Language)}
              className="bg-slate-50 border border-slate-200 rounded-full px-5 py-2.5 text-[10px] font-black text-slate-700 outline-none"
            >
              <option value="ja">🇯🇵 日本語</option>
              <option value="en">🇺🇸 English</option>
            </select>
          </div>
        </nav>

        <main className="flex-grow pb-32 md:pb-12">
          {activeTab === 'planner' ? (
            <div className="w-full">
              {finalizedPlan ? (
                <div className="container mx-auto px-4 py-8">
                  <DetailedPlanView plan={finalizedPlan} language={language} isBooked={false} />
                </div>
              ) : (
                <>
                  {currentPlans.length > 0 && (
                    <div className="w-full bg-white/90 backdrop-blur-xl border-b border-slate-100 px-4 md:px-8 py-3 sticky top-20 z-50 shadow-lg flex flex-col md:flex-row items-center gap-3 animate-in slide-in-from-top duration-500">
                       <div className="flex flex-wrap items-center justify-center md:justify-start gap-2 flex-grow overflow-hidden">
                          <div className="bg-slate-50 border border-slate-100 px-3 py-1.5 rounded-xl text-[9px] font-black text-slate-600 truncate max-w-[120px]">🚩 {searchPrefs.prefecture || '日本全国'}</div>
                          <div className="bg-slate-50 border border-slate-100 px-3 py-1.5 rounded-xl text-[9px] font-black text-slate-600 whitespace-nowrap">📅 {searchPrefs.startDate || '--'} ~</div>
                       </div>
                       <div className="flex space-x-2 flex-shrink-0 w-full md:w-auto">
                          <button onClick={() => setCurrentPlans([])} className="flex-1 md:flex-none px-4 py-2 bg-white border-2 border-slate-900 text-slate-900 rounded-lg text-[9px] font-black uppercase tracking-widest">変更</button>
                          <button onClick={() => setIsShowingPrep(true)} className="flex-2 md:flex-none px-4 py-2 bg-orange-500 text-white rounded-lg text-[9px] font-black uppercase tracking-widest shadow-xl shadow-orange-500/20 active:scale-95 transition-all">プラン作成</button>
                       </div>
                    </div>
                  )}

                  {currentPlans.length === 0 && !loading && (
                    <div className="max-w-6xl mx-auto px-4 pt-16">
                      <div className="text-center mb-12 space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-700">
                        <h1 className="text-7xl md:text-8xl font-black text-slate-900 tracking-tighter italic">Aipia</h1>
                        <p className="text-sm md:text-base font-black text-slate-400 uppercase tracking-[0.3em]">-AIが創る、秘境への旅行プラン-</p>
                      </div>
                      <div className="bg-white/90 border-2 border-white rounded-[4rem] p-10 md:p-16 shadow-[0_50px_100px_-20px_rgba(0,0,0,0.05)] mb-20 backdrop-blur-xl">
                        <InputForm onSubmit={handleGeneratePlan} isLoading={loading} language={language} />
                      </div>
                      <Recommendations items={recommendations} language={language} onSelect={(rec) => handleGeneratePlan({ ...searchPrefs, prefecture: rec.prefecture, keywords: rec.title })} isLoading={loadingRecs} />
                    </div>
                  )}

                  {loading && <div className="flex flex-col items-center justify-center py-32"><MascotSlideshow language={language} /></div>}

                  {currentPlans.length > 0 && !loading && (
                    <div className="container mx-auto px-4 py-20 grid grid-cols-1 gap-12">
                      {currentPlans.map((plan) => (
                        <PlanDisplay key={plan.id} plan={plan} isFavorite={!!favorites.find(f => f.plan.id === plan.id)} onToggleFavorite={() => toggleFavorite(plan)} language={language} />
                      ))}
                    </div>
                  )}
                </>
              )}
            </div>
          ) : activeTab === 'favorites' ? (
            <div className="container mx-auto px-4 py-16">
               <div className="flex justify-between items-end mb-16">
                 <h2 className="text-5xl font-black text-slate-900 italic tracking-tighter">My Favorites</h2>
                 <button onClick={() => setIsShowingPrep(true)} className="px-12 py-5 bg-orange-500 text-white rounded-[2rem] font-black text-sm shadow-2xl shadow-orange-500/30">これらでプランを生成</button>
               </div>
               <FavoriteList favorites={favorites} onRemove={(id) => setFavorites(f => f.filter(x => x.id !== id))} onSelect={(plan) => { setCurrentPlans([plan]); setActiveTab('planner'); }} onFinalize={() => {}} onBook={() => {}} language={language} />
            </div>
          ) : (
            <div className="container mx-auto px-4 py-16">
              <h2 className="text-5xl font-black text-slate-900 italic tracking-tighter mb-12">History</h2>
              <HistoryList history={history} onSelect={(plan) => { setCurrentPlans([plan]); setActiveTab('planner'); }} onClear={() => setHistory([])} onToggleFavorite={toggleFavorite} favorites={favorites} language={language} />
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default App;
