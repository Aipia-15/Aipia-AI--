
import { GoogleGenAI, Type, ThinkingLevel } from "@google/genai";
import { UserPreferences, TravelPlan, Recommendation } from "./types";

function extractJson(text: string): string {
  try {
    const arrayMatch = text.match(/\[[\s\S]*\]/);
    if (arrayMatch) return arrayMatch[0];
    const objectMatch = text.match(/\{[\s\S]*\}/);
    if (objectMatch) return objectMatch[0];
    return text.replace(/```json/g, "").replace(/```/g, "").trim();
  } catch (e) {
    return "[]";
  }
}

async function callWithRetry<T>(fn: () => Promise<T>, retries = 2, delay = 100): Promise<T> {
  try {
    return await fn();
  } catch (err: any) {
    if (retries > 0) {
      await new Promise(resolve => setTimeout(resolve, delay));
      return callWithRetry(fn, retries - 1, delay * 2);
    }
    throw err;
  }
}

export const generatePlanDeViaje = async (prefs: UserPreferences): Promise<TravelPlan[]> => {
  const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY || process.env.API_KEY });
  
  const prompt = `日本(出発:${prefs.departure},地域:${prefs.prefecture},キーワード:${prefs.keywords})の「穴場・秘境」を厳選して10件教えてください。
必ず以下のJSON形式の配列で出力してください。
[
  { "theme": "名称", "address": "住所", "description": "100文字程度の解説", "activityCost": 5000, "imageKeyword": "english keyword" }
]`;

  return await callWithRetry(async () => {
    const response = await ai.models.generateContent({
      model: 'gemini-3-flash-preview',
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        tools: [{ googleSearch: {} }],
        responseSchema: {
          type: Type.ARRAY,
          items: {
            type: Type.OBJECT,
            properties: {
              theme: { type: Type.STRING },
              address: { type: Type.STRING },
              description: { type: Type.STRING },
              activityCost: { type: Type.NUMBER },
              imageKeyword: { type: Type.STRING }
            },
            required: ["theme", "description", "imageKeyword", "address"]
          }
        }
      }
    });

    const groundingSources = response.candidates?.[0]?.groundingMetadata?.groundingChunks
      ?.map((chunk: any) => ({
        title: chunk.web?.title || '参照元',
        uri: chunk.web?.uri || ''
      }))
      .filter((link: any) => link.uri) || [];

    const text = response.text || "[]";
    const rawSpots = JSON.parse(extractJson(text));
    
    if (!Array.isArray(rawSpots)) return [];

    return rawSpots.map((spot: any) => ({
      id: crypto.randomUUID(),
      theme: spot.theme || "名称未設定",
      days: [{
        dayNumber: 1,
        activities: [{
          id: crypto.randomUUID(),
          time: "11:00",
          action: spot.theme || "観光",
          description: spot.description || "",
          departureStation: spot.address || "",
          arrivalStation: "",
          cost: spot.activityCost || 0,
          officialUrl: `https://www.google.com/search?q=${encodeURIComponent(spot.theme || "")}`
        }]
      }],
      budgetBreakdown: { transport: 0, accommodation: 0, activity: spot.activityCost || 0, food: 0 },
      accommodations: [],
      nearbySpots: [],
      proTips: [`${spot.theme}は現地でも非常に珍しい穴場です。`],
      groundingSources: groundingSources,
      createdAt: new Date().toISOString(),
      durationDays: 1,
      dateRange: { start: prefs.startDate, end: prefs.endDate },
      imageKeyword: spot.imageKeyword || "japan hidden gem"
    }));
  });
};

export const fetchAIRecommendations = async (language: string, count: number = 8): Promise<Recommendation[]> => {
  const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY || process.env.API_KEY });
  return await callWithRetry(async () => {
    const response = await ai.models.generateContent({
      model: "gemini-3-flash-preview",
      contents: `日本全国の穴場スポットを${count}件提案してください。必ずJSON形式の配列で出力してください。言語は${language === 'ja' ? '日本語' : 'English'}でお願いします。`,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.ARRAY,
          items: {
            type: Type.OBJECT,
            properties: {
              title: { type: Type.STRING },
              description: { type: Type.STRING },
              prefecture: { type: Type.STRING },
              genre: { type: Type.STRING }
            },
            required: ["title", "description", "prefecture", "genre"]
          }
        }
      }
    });
    const text = response.text || "[]";
    const items = JSON.parse(extractJson(text));
    if (!Array.isArray(items)) return [];
    
    return items.map((item: any, idx: number) => ({
      ...item,
      id: `rec-${idx}-${Date.now()}`,
      imageUrl: `https://picsum.photos/seed/${idx + 500}/600/400`
    }));
  });
};
