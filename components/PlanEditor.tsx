
import React, { useState, useEffect } from 'react';
import { FavoriteItem, UserPreferences, TravelPlan, Language } from '../types';
import { GoogleGenAI, Type, ThinkingLevel } from "@google/genai";
import MascotSlideshow from './MascotSlideshow';

interface PlanEditorProps {
  favorites: FavoriteItem[];
  searchPrefs: UserPreferences;
  onBack: () => void;
  onFinalize: (plan: TravelPlan) => void;
  language: Language;
}

const extractJson = (text: string): string => {
  try {
    const arrayMatch = text.match(/\[[\s\S]*\]/);
    if (arrayMatch) return arrayMatch[0];
    const objectMatch = text.match(/\{[\s\S]*\}/);
    if (objectMatch) return objectMatch[0];
    return text.replace(/```json/g, "").replace(/```/g, "").trim();
  } catch (e) {
    return "[]";
  }
};

async function callWithRetry<T>(fn: () => Promise<T>, retries = 2, delay = 1000): Promise<T> {
  try {
    return await fn();
  } catch (err: any) {
    if (retries > 0 && (err.message?.includes('429') || err.status === 'RESOURCE_EXHAUSTED')) {
      await new Promise(resolve => setTimeout(resolve, delay));
      return callWithRetry(fn, retries - 1, delay * 2);
    }
    throw err;
  }
}

const PlanEditor: React.FC<PlanEditorProps> = ({ favorites, searchPrefs, onBack, onFinalize, language }) => {
  const [loading, setLoading] = useState(true);
  const [plans, setPlans] = useState<TravelPlan[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [localFavorites, setLocalFavorites] = useState(favorites);
  const [error, setError] = useState<string | null>(null);

  const startDate = new Date(searchPrefs.startDate || new Date());
  const endDate = new Date(searchPrefs.endDate || new Date(Date.now() + 86400000));
  const durationDays = Math.max(1, Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 3600 * 24)) + 1);

  const generateFullPlan = async (currentFavs = localFavorites) => {
    if (currentFavs.length === 0) {
      setError("スポットが選択されていません。お気に入りを選んでからプランを作成してください。");
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);

    const timeoutPromise = new Promise((_, reject) =>
      setTimeout(() => reject(new Error("TIMEOUT")), 90000) // Increase to 90s for safety
    );

    try {
      const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY || process.env.API_KEY });
      const spotList = currentFavs.map(f => f.plan.theme).join('、');
      
      const prompt = `あなたは日本旅行のプロコンシェルジュです。
【必須スポット】: ${spotList}
上記を巡る「${durationDays}日間」の旅行プランを【2つの異なるパターン（案A, B）】で作成してください。
必ず指定されたJSON形式の配列で出力してください。

【条件】
1. 出発地: ${searchPrefs.departure || '最寄り駅'}
2. 各日3〜4つの主要な予定を記述。
3. 宿泊先(accommodations)を実名で提案。
4. 全て日本語で回答。`;

      const fetchPromise = callWithRetry(async () => {
        return await ai.models.generateContent({
          model: "gemini-3-flash-preview",
          contents: prompt,
          config: {
            thinkingConfig: { thinkingLevel: ThinkingLevel.LOW },
            responseMimeType: "application/json",
            responseSchema: {
              type: Type.ARRAY,
              items: {
                type: Type.OBJECT,
                properties: {
                  theme: { type: Type.STRING },
                  totalCost: { type: Type.NUMBER },
                  days: {
                    type: Type.ARRAY,
                    items: {
                      type: Type.OBJECT,
                      properties: {
                        dayNumber: { type: Type.NUMBER },
                        activities: {
                          type: Type.ARRAY,
                          items: {
                            type: Type.OBJECT,
                            properties: {
                              time: { type: Type.STRING },
                              action: { type: Type.STRING },
                              description: { type: Type.STRING },
                              line: { type: Type.STRING },
                              cost: { type: Type.NUMBER }
                            },
                            required: ["time", "action", "description"]
                          }
                        }
                      }
                    }
                  },
                  accommodations: {
                    type: Type.ARRAY,
                    items: {
                      type: Type.OBJECT,
                      properties: {
                        name: { type: Type.STRING },
                        description: { type: Type.STRING },
                        estimatedCost: { type: Type.NUMBER },
                        imageUrl: { type: Type.STRING },
                        officialUrl: { type: Type.STRING }
                      },
                      required: ["name", "description", "estimatedCost"]
                    }
                  },
                  proTips: { type: Type.ARRAY, items: { type: Type.STRING } }
                },
                required: ["theme", "totalCost", "days", "accommodations"]
              }
            }
          }
        });
      });

      const response = await Promise.race([fetchPromise, timeoutPromise]) as any;

      const text = response.text || "[]";
      const jsonStr = extractJson(text);
      const data = JSON.parse(jsonStr);
      
      if (Array.isArray(data) && data.length > 0) {
        const validatedData = data.map((p: any) => ({
          ...p,
          id: crypto.randomUUID(),
          durationDays,
          dateRange: { start: searchPrefs.startDate, end: searchPrefs.endDate },
          accommodations: (p.accommodations || []).map((acc: any) => ({
            ...acc,
            id: acc.name || crypto.randomUUID(),
            imageUrl: acc.imageUrl || `https://picsum.photos/seed/${Math.random()}/800/600`,
            officialUrl: acc.officialUrl || `https://www.google.com/search?q=${encodeURIComponent(acc.name || "ホテル")}`
          })),
          selectedAccommodationId: p.accommodations?.[0]?.name || '',
          budgetBreakdown: { 
            transport: (p.totalCost || 0) * 0.2, 
            accommodation: (p.totalCost || 0) * 0.4, 
            activity: (p.totalCost || 0) * 0.2, 
            food: (p.totalCost || 0) * 0.2 
          },
          nearbySpots: [],
          groundingSources: []
        }));
        setPlans(validatedData);
      } else {
        throw new Error("Invalid response format");
      }
    } catch (e: any) {
      console.error(e);
      if (e.message === "TIMEOUT") {
        setError("プラン生成がタイムアウトしました。通信環境を確認するか、スポット数を減らして再度お試しください。");
      } else if (e.message?.includes('429') || e.status === 'RESOURCE_EXHAUSTED') {
        setError("APIの利用制限に達しました。しばらく時間を置いてから再度お試しください。");
      } else {
        setError("AIがプランを作成中にエラーが発生しました。もう一度「再試行」を押すか、ホームに戻ってください。");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    generateFullPlan();
  }, []);

  const currentPlan = plans[selectedIndex];
  const planLabels = ['A', 'B', 'C'];

  if (loading) {
    return (
      <div className="fixed inset-0 bg-[#fffbeb] z-[1000] flex flex-col items-center justify-center p-6 text-center">
        <MascotSlideshow language={language} />
        <div className="mt-8 space-y-2">
          <p className="text-slate-900 font-black text-2xl italic animate-pulse">爆速で{durationDays}日間をプランニング中...</p>
          <p className="text-slate-400 text-[10px] font-black uppercase tracking-[0.4em]">選択したスポットを繋いでいます（最大60秒）</p>
        </div>
      </div>
    );
  }

  if (error || !currentPlan) {
    return (
      <div className="fixed inset-0 bg-slate-950 flex flex-col items-center justify-center p-8 text-center text-white z-[2000]">
        <div className="max-w-md bg-white/5 p-10 rounded-[3rem] border border-white/10 backdrop-blur-2xl">
          <h2 className="text-2xl font-black mb-4 italic text-orange-500">生成に失敗しました</h2>
          <p className="text-slate-400 mb-8 text-sm">{error || "プランを生成できませんでした。"}</p>
          <div className="flex flex-col gap-3">
            <button onClick={() => generateFullPlan()} className="px-8 py-5 bg-orange-600 rounded-2xl font-black shadow-2xl hover:bg-orange-700 transition-all uppercase tracking-widest">もう一度生成する</button>
            <button onClick={onBack} className="px-8 py-5 bg-white/10 rounded-2xl font-black hover:bg-white/20 transition-all uppercase tracking-widest text-xs">ホームに戻る</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col p-4 md:p-10 relative overflow-x-hidden">
      <div className="fixed top-0 right-0 w-[800px] h-[800px] bg-orange-600/10 blur-[150px] rounded-full -translate-y-1/2 translate-x-1/2 pointer-events-none"></div>

      <div className="w-full max-w-[1500px] mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8 relative z-10">
        
        {/* LEFT: Plan Selector */}
        <aside className="lg:col-span-2 flex flex-col gap-4">
           <div className="bg-white/95 backdrop-blur-3xl rounded-[2.5rem] p-4 flex flex-col gap-2 border border-white shadow-2xl">
              <div className="p-4 border-b border-slate-100 mb-2">
                 <div className="text-[10px] font-black text-slate-300 uppercase tracking-widest">案を選択</div>
              </div>
              {plans.map((p, i) => (
                <button 
                  key={i} 
                  onClick={() => setSelectedIndex(i)}
                  className={`w-full p-5 text-left rounded-2xl transition-all border-2 flex flex-col gap-1 ${selectedIndex === i ? 'bg-slate-900 border-slate-900 text-white shadow-xl scale-[1.05]' : 'bg-white border-transparent text-slate-400 hover:bg-slate-50'}`}
                >
                  <div className="text-xl font-black italic">案 {planLabels[i]}</div>
                  <div className="text-[10px] font-bold">¥{(p.totalCost || 0).toLocaleString()}</div>
                </button>
              ))}
           </div>
        </aside>

        {/* CENTER: Timeline */}
        <main className="lg:col-span-10">
           <div className="bg-white rounded-[4rem] p-8 md:p-16 shadow-2xl min-h-screen border border-white/50">
              <div className="mb-16 border-b border-slate-50 pb-12 flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
                 <div className="space-y-2">
                    <h2 className="text-4xl md:text-5xl font-black text-slate-900 italic tracking-tighter">{currentPlan.theme}</h2>
                    <p className="text-orange-500 font-black uppercase tracking-[0.4em] text-[10px]">
                       {durationDays}日間の特別フルプラン
                    </p>
                 </div>
                 <div className="bg-slate-50 px-8 py-4 rounded-3xl border border-slate-100 text-right">
                    <p className="text-[10px] font-black text-slate-300 uppercase tracking-widest mb-1">想定総予算</p>
                    <p className="text-3xl font-black text-slate-900 italic">¥{(currentPlan.totalCost || 0).toLocaleString()}</p>
                 </div>
              </div>

              <div className="space-y-20">
                 {currentPlan.days.map((day, dIdx) => (
                   <div key={dIdx} className="relative">
                      <div className="flex items-center gap-6 mb-12 sticky top-0 z-20 bg-white/90 backdrop-blur-md py-4">
                         <div className="bg-slate-950 text-white px-10 py-4 rounded-[2rem] font-black italic text-2xl shadow-xl">{day.dayNumber}日目</div>
                         <div className="h-px bg-slate-100 flex-grow"></div>
                      </div>
                      
                      <div className="space-y-0">
                         {day.activities.map((act, aIdx) => (
                           <div key={aIdx} className="relative pl-16 md:pl-24 pb-20 border-l-4 border-dashed border-slate-100 ml-8 md:ml-12 last:border-0">
                              <div className={`absolute -left-[14px] md:-left-[18px] top-0 w-6 h-6 md:w-8 md:h-8 rounded-full border-4 md:border-[6px] border-white shadow-xl ${aIdx === 0 ? 'bg-orange-500' : 'bg-slate-950'}`}></div>
                              
                              <div className="space-y-8">
                                 <div className="flex flex-col md:flex-row md:items-center gap-4 md:gap-8">
                                    <div className="text-2xl font-mono font-black text-slate-900 bg-slate-50 px-6 py-2 rounded-2xl border border-slate-100 shadow-sm inline-block">{act.time}</div>
                                    <h4 className="text-2xl md:text-3xl font-black text-slate-800 tracking-tight">{act.action}</h4>
                                 </div>

                                 {act.line && (
                                    <div className="bg-blue-600 text-white rounded-[2rem] p-6 shadow-xl flex items-center gap-5">
                                       <div className="w-10 h-10 bg-white/20 backdrop-blur-md rounded-xl flex items-center justify-center">
                                          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" strokeWidth={2.5}/></svg>
                                       </div>
                                       <p className="font-black text-lg">{act.line}</p>
                                    </div>
                                 )}

                                 <div className="bg-white border-2 border-slate-50 p-8 rounded-[3rem] shadow-sm flex flex-col md:flex-row gap-10 hover:shadow-xl transition-all">
                                    <div className="w-full md:w-40 h-40 bg-slate-100 rounded-[2rem] overflow-hidden flex-shrink-0">
                                       <img src={`https://loremflickr.com/500/500/japan?lock=${day.dayNumber * 10 + aIdx}`} className="w-full h-full object-cover" alt={act.action} />
                                    </div>
                                    <div className="flex flex-col justify-center">
                                       <p className="text-slate-500 text-base font-medium leading-relaxed">{act.description}</p>
                                    </div>
                                 </div>
                              </div>
                           </div>
                         ))}
                      </div>
                   </div>
                 ))}
              </div>

              {/* Accommodations Highlight */}
              {currentPlan.accommodations && currentPlan.accommodations.length > 0 && (
                <div className="mt-24 p-12 bg-slate-950 rounded-[4rem] text-white relative overflow-hidden shadow-2xl">
                   <h3 className="text-3xl font-black italic mb-12">おすすめの宿泊施設</h3>
                   <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                      {currentPlan.accommodations.map((acc, idx) => (
                        <div key={idx} className="bg-white/5 p-8 rounded-[3rem] border border-white/10 flex flex-col gap-6">
                           <div className="w-full h-56 rounded-[2rem] overflow-hidden">
                              <img src={acc.imageUrl} className="w-full h-full object-cover" />
                           </div>
                           <div className="space-y-4">
                              <h4 className="text-2xl font-black">{acc.name}</h4>
                              <p className="text-sm text-slate-400 leading-relaxed">{acc.description}</p>
                              <div className="flex justify-between items-center pt-6 border-t border-white/10">
                                 <span className="text-orange-400 font-black text-xl">¥{(acc.estimatedCost || 0).toLocaleString()}〜</span>
                                 <a href={acc.officialUrl} target="_blank" className="text-[10px] font-black uppercase underline opacity-50">詳細</a>
                              </div>
                           </div>
                        </div>
                      ))}
                   </div>
                </div>
              )}

              <div className="mt-24 pt-16 border-t flex flex-col md:flex-row justify-between items-center gap-10">
                 <button 
                   onClick={() => onFinalize(currentPlan)} 
                   className="w-full md:w-auto px-20 py-8 bg-slate-950 text-white rounded-[2.5rem] font-black text-xl shadow-2xl hover:bg-orange-600 transition-all active:scale-95 uppercase tracking-[0.2em]"
                 >
                   プランを確定する
                 </button>
              </div>
           </div>
        </main>
      </div>
    </div>
  );
};

export default PlanEditor;
