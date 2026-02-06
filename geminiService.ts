
import { GoogleGenAI, Type } from "@google/genai";
import { UserPreferences, TravelPlan, GroundingLink, Recommendation } from "./types";

/**
 * 強力な指数バックオフを用いたリトライ処理
 */
async function callWithRetry<T>(fn: () => Promise<T>, retries = 3, delay = 2500): Promise<T> {
  try {
    return await fn();
  } catch (err: any) {
    const errorMsg = err?.message?.toLowerCase() || "";
    const isQuotaError = 
      errorMsg.includes('exceeded quota') || 
      errorMsg.includes('429') || 
      errorMsg.includes('too many requests') ||
      errorMsg.includes('rate limit');
    
    if (isQuotaError && retries > 0) {
      console.warn(`[Gemini Quota] Limit hit. Retrying in ${delay}ms... (${retries} attempts left)`);
      await new Promise(resolve => setTimeout(resolve, delay));
      return callWithRetry(fn, retries - 1, delay * 2);
    }
    throw err;
  }
}

const getLanguageName = (lang: string) => {
  switch (lang) {
    case 'en': return 'English';
    case 'ko': return 'Korean';
    case 'es': return 'Spanish';
    case 'de': return 'German';
    case 'fr': return 'French';
    default: return 'Japanese';
  }
};

export const generatePlanDeViaje = async (prefs: UserPreferences): Promise<TravelPlan[]> => {
  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
  const langName = getLanguageName(prefs.language);
  
  const start = new Date(prefs.startDate);
  const end = new Date(prefs.endDate);
  const durationDays = Math.max(1, Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)) + 1);

  // 歩行速度に応じた指示
  const speedNote = prefs.walkingSpeed === 'slow' 
    ? "ユーザーの歩行速度は「のんびり」です。スポット間の移動時間は標準より+20%長く見積もり、ゆとりのあるスケジュールにしてください。"
    : prefs.walkingSpeed === 'fast'
    ? "ユーザーの歩行速度は「せっかち」です。移動時間はタイトに見積もり、多くのスポットを回れる効率的なプランにしてください。"
    : "ユーザーの歩行速度は「標準」です。";

  const prompt = `
    あなたは「Aipia」という旅行計画代行コンシェルジュのAIです。
    ユーザーの要望に基づいて、実在する観光地・宿泊施設を含む最高の旅行プランを提案してください。
    
    【重要：時刻とホテルのルール】
    1. 各アクティビティの時刻(time)は必ず「HH:mm」形式（例 09:00, 14:30）で、時系列順に分刻みで正確に記載してください。
    2. 宿泊施設(accommodation)は必ず実在する具体的な施設名を記載し、その魅力を3文以上で詳しく説明してください。
    3. 移動時間の考慮: ${speedNote}
    4. 「不明」「N/A」は一切禁止。Google Searchを使用して最新情報を特定してください。

    【リクエスト内容】
    - 出発地点: ${prefs.departure}
    - 目的地: ${prefs.prefecture || '最適解を提案'}
    - 日程: ${prefs.startDate} 〜 ${prefs.endDate} (${durationDays}日間)
    - 予算: ${prefs.budget.toLocaleString()}円以内
    - キーワード: ${prefs.keywords || 'なし'}
    - ジャンル: ${prefs.genre}

    出力言語: ${langName}
  `;

  return await callWithRetry(async () => {
    const response = await ai.models.generateContent({
      model: "gemini-3-flash-preview", 
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.ARRAY,
          items: {
            type: Type.OBJECT,
            properties: {
              theme: { type: Type.STRING },
              days: {
                type: Type.ARRAY,
                items: {
                  type: Type.OBJECT,
                  properties: {
                    dayNumber: { type: Type.INTEGER },
                    activities: {
                      type: Type.ARRAY,
                      items: {
                        type: Type.OBJECT,
                        properties: {
                          time: { type: Type.STRING, description: "HH:mm format" },
                          action: { type: Type.STRING },
                          description: { type: Type.STRING },
                          transport: { type: Type.STRING },
                          departureStation: { type: Type.STRING },
                          arrivalStation: { type: Type.STRING },
                          detailedCost: { type: Type.STRING },
                          officialUrl: { type: Type.STRING }
                        }
                      }
                    }
                  }
                }
              },
              accommodation: {
                type: Type.OBJECT,
                properties: {
                  name: { type: Type.STRING },
                  description: { type: Type.STRING },
                  estimatedCost: { type: Type.STRING },
                  officialUrl: { type: Type.STRING }
                },
                required: ["name", "description", "estimatedCost"]
              },
              budgetBreakdown: {
                type: Type.OBJECT,
                properties: {
                  transport: { type: Type.NUMBER },
                  accommodation: { type: Type.NUMBER },
                  activity: { type: Type.NUMBER },
                  food: { type: Type.NUMBER }
                }
              },
              nearbySpots: {
                type: Type.ARRAY,
                items: {
                  type: Type.OBJECT,
                  properties: {
                    name: { type: Type.STRING },
                    address: { type: Type.STRING },
                    type: { type: Type.STRING }
                  }
                }
              },
              proTips: {
                type: Type.ARRAY,
                items: { type: Type.STRING }
              }
            }
          }
        },
        tools: [{ googleSearch: {} }]
      }
    });

    const rawPlans = JSON.parse(response.text || "[]");
    
    // Extract grounding sources from search results
    const groundingSources: GroundingLink[] = response.candidates?.[0]?.groundingMetadata?.groundingChunks
      ?.filter((chunk: any) => chunk.web)
      ?.map((chunk: any) => ({
        title: chunk.web.title,
        uri: chunk.web.uri
      })) || [];

    return rawPlans.map((plan: any) => ({
      ...plan,
      id: crypto.randomUUID(),
      createdAt: new Date().toISOString(),
      durationDays,
      dateRange: { start: prefs.startDate, end: prefs.endDate },
      groundingSources
    }));
  });
};

export const fetchAIRecommendations = async (language: string, count: number = 3): Promise<Recommendation[]> => {
  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
  const langName = getLanguageName(language);
  
  const prompt = `
    日本のあまり知られていない秘境や穴場スポット（Hidden Gems）を ${count} つ提案してください。
    Google Searchを使用して、実在する具体的な場所を選んでください。
    出力言語: ${langName}
  `;
  
  return await callWithRetry(async () => {
    const response = await ai.models.generateContent({
      model: "gemini-3-flash-preview",
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.ARRAY,
          items: {
            type: Type.OBJECT,
            properties: {
              title: { type: Type.STRING },
              shortTitle: { type: Type.STRING },
              description: { type: Type.STRING },
              prefecture: { type: Type.STRING },
              genre: { type: Type.STRING }
            },
            required: ["title", "shortTitle", "description", "prefecture", "genre"]
          }
        },
        tools: [{ googleSearch: {} }]
      }
    });
    
    const items = JSON.parse(response.text || "[]");
    
    // Extract grounding sources
    const groundingSources: GroundingLink[] = response.candidates?.[0]?.groundingMetadata?.groundingChunks
      ?.filter((chunk: any) => chunk.web)
      ?.map((chunk: any) => ({
        title: chunk.web.title,
        uri: chunk.web.uri
      })) || [];

    return items.map((item: any, idx: number) => ({
      ...item,
      id: `rec-${idx}-${Date.now()}`,
      imageUrl: `https://picsum.photos/seed/travel-japan-${encodeURIComponent(item.title)}-${idx}/600/400`,
      groundingSources
    }));
  }, 2, 1000);
};

export const generateDetailedLogistics = async (plan: TravelPlan, prefs: UserPreferences): Promise<TravelPlan> => {
  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
  const langName = getLanguageName(prefs.language);
  const prompt = `
    Google Searchを使用して、このプランの具体的な交通ダイヤとURLを特定してください。
    時刻は必ず「HH:mm」形式で上書きしてください。ユーザーの歩行速度「${prefs.walkingSpeed}」を考慮してください。
    言語: ${langName}
    プラン内容: ${JSON.stringify(plan)}
  `;

  return await callWithRetry(async () => {
    const response = await ai.models.generateContent({
      model: "gemini-3-flash-preview",
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        tools: [{ googleSearch: {} }]
      }
    });
    const detailedData = JSON.parse(response.text || "{}");
    
    // Extract grounding sources
    const newGroundingSources: GroundingLink[] = response.candidates?.[0]?.groundingMetadata?.groundingChunks
      ?.filter((chunk: any) => chunk.web)
      ?.map((chunk: any) => ({
        title: chunk.web.title,
        uri: chunk.web.uri
      })) || [];

    return { 
      ...plan, 
      ...detailedData, 
      groundingSources: [...(plan.groundingSources || []), ...newGroundingSources]
    };
  });
};

export const refinePlanWithAI = async (plan: TravelPlan): Promise<TravelPlan> => {
  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
  const prompt = `以下の旅行プランをブラッシュアップしてください。時刻はHH:mm形式を維持すること。JSON形式で出力してください。: ${JSON.stringify(plan)}`;
  
  return await callWithRetry(async () => {
    const response = await ai.models.generateContent({
      model: "gemini-3-flash-preview",
      contents: prompt,
      config: { responseMimeType: "application/json" }
    });
    return { ...plan, ...JSON.parse(response.text || "{}") };
  });
};