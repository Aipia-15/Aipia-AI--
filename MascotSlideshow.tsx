
import React, { useState, useEffect } from 'react';
import { Language } from '../types';
import { translations } from '../translations';

interface Mascot {
  name: { [K in Language]?: string };
  prefecture: { [K in Language]?: string };
  description: { [K in Language]?: string };
  ad?: { [K in Language]?: string };
  color: string;
  neonColor: string;
  isTrend?: boolean;
}

const MASCOTS: Mascot[] = [
  { name: { ja: "キュンちゃん", en: "Kyun-chan" }, prefecture: { ja: "北海道", en: "Hokkaido" }, description: { ja: "エゾナキウサギがシカの被り物をしているよ。", en: "A pika wearing a deer hat." }, ad: { ja: "今なら北海道の秘境ツアーが10%OFF！", en: "10% OFF on Hokkaido hidden gem tours now!" }, color: "bg-blue-900", neonColor: "#00ffff" },
  { name: { ja: "いくべぇ", en: "Ikubee" }, prefecture: { ja: "青森県", en: "Aomori" }, description: { ja: "青森を旅する妖精. お尻のブナの葉がチャームポイント。", en: "A fairy traveling through Aomori." }, color: "bg-green-900", neonColor: "#7cfc00" },
  { name: { ja: "そばっち", en: "Sobacchi" }, prefecture: { ja: "岩手県", en: "Iwate" }, description: { ja: "わんこそばの精. のんびり屋だけど、おもてなしの心は熱いよ。", en: "The spirit of Wanko Soba noodles." }, color: "bg-red-900", neonColor: "#ff4500" },
  { name: { ja: "むすび丸", en: "Musubimaru" }, prefecture: { ja: "宮城県", en: "Miyagi" }, description: { ja: "おにぎりの顔に伊達政宗の兜. 宮城の食と文化をPR！", en: "An onigiri wearing Date Masamune's helmet." }, color: "bg-slate-800", neonColor: "#ffd700" },
  { name: { ja: "AIトレンド旅", en: "AI Travel Trend" }, prefecture: { ja: "TREND", en: "TREND" }, description: { ja: "今は「デジタルデトックス旅」が流行中。あえてスマホを見ない、真の秘境体験を。", en: "Digital Detox is the new trend. Experience true isolation without your phone." }, color: "bg-emerald-600", neonColor: "#ffffff", isTrend: true },
  { name: { ja: "んだっち", en: "Ndacchi" }, prefecture: { ja: "秋田県", en: "Akita" }, description: { ja: "ナマハゲをモチーフにした近未来型ロボットだよ。", en: "A futuristic robot inspired by Namahage." }, color: "bg-orange-900", neonColor: "#ff8c00" },
  { name: { ja: "きてけろくん", en: "Kitekero-kun" }, prefecture: { ja: "山形県", en: "Yamagata" }, description: { ja: "山形県の横顔の形をしている不思議なキャラクター。", en: "Shaped like the profile of Yamagata prefecture." }, color: "bg-emerald-900", neonColor: "#adff2f" },
  { name: { ja: "キビタン", en: "Kibitan" }, prefecture: { ja: "福島県", en: "Fukushima" }, description: { ja: "県の鳥「キビタキ」がモチーフ. 福島の魅力を発信中！", en: "Inspired by the narcissus flycatcher." }, color: "bg-yellow-900", neonColor: "#ffff00" },
  { name: { ja: "ぐんまちゃん", en: "Gunma-chan" }, prefecture: { ja: "群馬県", en: "Gunma" }, description: { ja: "永遠の7歳. ポニーをモチーフにした可愛らしい妖精だよ。", en: "Forever 7 years old pony fairy." }, color: "bg-amber-800", neonColor: "#deb887" },
  { name: { ja: "スマート・トランク", en: "Smart Travel" }, prefecture: { ja: "TECH", en: "TECH" }, description: { ja: "AIがあなたの好みを学習。次回のプランはさらに精度の高い「あなた専用」に進化します。", en: "AI learns your style. Your next trip will be even more personalized." }, color: "bg-indigo-900", neonColor: "#818cf8", isTrend: true },
  { name: { ja: "チーバくん", en: "Chiba-kun" }, prefecture: { ja: "千葉県", en: "Chiba" }, description: { ja: "横から見ると千葉県の形をしている真っ赤な不思議な生き物。", en: "A red creature shaped like Chiba's map." }, color: "bg-rose-900", neonColor: "#ff0000" },
  { name: { ja: "ふっかちゃん", en: "Fukka-chan" }, prefecture: { ja: "埼玉県", en: "Saitama" }, description: { ja: "深谷ねぎの角が特徴。愛くるしいルックスで大人気！", en: "Features Fukaya green onion horns." }, color: "bg-teal-900", neonColor: "#2dd4bf" },
  { name: { ja: "さのまる", en: "Sanomaru" }, prefecture: { ja: "栃木県", en: "Tochigi" }, description: { ja: "佐野ラーメンの丼をかぶり、いもフライの剣を持った侍。", en: "A samurai with a ramen bowl hat." }, color: "bg-slate-700", neonColor: "#f1f5f9" },
  { name: { ja: "しまねっこ", en: "Shimanekko" }, prefecture: { ja: "島根県", en: "Shimane" }, description: { ja: "出雲大社の屋根のような帽子をかぶった黄色い猫。", en: "A cat wearing a shrine-roof hat." }, color: "bg-amber-600", neonColor: "#fde68a" },
  { name: { ja: "サステナブル旅", en: "Eco Travel" }, prefecture: { ja: "ETHICAL", en: "ETHICAL" }, description: { ja: "「地産地消」と「ゴミゼロ」。地球に優しい旅が、今のエリート旅行者の新常識。", en: "Local food & Zero waste. The new standard for elite travelers." }, color: "bg-green-800", neonColor: "#4ade80", isTrend: true },
  { name: { ja: "くまモン", en: "Kumamoto" }, prefecture: { ja: "熊本県", en: "Kumamoto" }, description: { ja: "熊本県の営業部長. 美味しいものとサプライズが大好きだモン！", en: "Kumamoto's sales manager." }, color: "bg-black", neonColor: "#ff0000" },
];

const MascotSlideshow: React.FC<{ language: Language }> = ({ language }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [progress, setProgress] = useState(0);
  const SLIDE_DURATION = 5000;
  const PROGRESS_INTERVAL = 30;

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % MASCOTS.length);
      setProgress(0);
    }, SLIDE_DURATION);

    const progressTimer = setInterval(() => {
      setProgress((prev) => {
        const next = prev + (100 / (SLIDE_DURATION / PROGRESS_INTERVAL));
        return next >= 100 ? 0 : next;
      });
    }, PROGRESS_INTERVAL);

    return () => { clearInterval(timer); clearInterval(progressTimer); };
  }, [currentIndex]);

  const mascot = MASCOTS[currentIndex];
  const t = translations[language];

  const getLabel = (obj?: { [K in Language]?: string }) => {
    if (!obj) return '';
    return obj[language] || obj['en'] || obj['ja'] || '';
  };

  return (
    <div className="w-full max-w-lg mx-auto bg-white rounded-[2.5rem] overflow-hidden shadow-2xl border border-slate-100 transition-all duration-1000">
      <div className={`h-56 flex items-center justify-center relative overflow-hidden transition-colors duration-1000 ${mascot.color}`}>
        {mascot.isTrend && <div className="absolute top-4 left-4 bg-white/20 backdrop-blur-md px-3 py-1 rounded-full text-[8px] font-black text-white uppercase tracking-widest">Global Trend</div>}
        <div className="absolute inset-0 opacity-20 blur-[100px]" style={{ backgroundColor: mascot.neonColor }}></div>
        <div className="relative z-10 text-center select-none p-4">
          <span className="text-[10px] text-white/50 font-black tracking-[0.5em] block mb-2 uppercase">{getLabel(mascot.prefecture)}</span>
          <h2 className="text-4xl md:text-5xl font-serif font-bold tracking-widest" style={{ color: '#fff', textShadow: `0 0 7px #fff, 0 0 42px ${mascot.neonColor}` }}>
            {getLabel(mascot.name)}
          </h2>
        </div>
      </div>
      <div className="p-8 space-y-4 text-center">
        <h3 className="text-xl font-bold text-slate-800">{getLabel(mascot.prefecture)}</h3>
        <p className="text-slate-500 text-sm leading-relaxed min-h-[4rem]">{getLabel(mascot.description)}</p>
        
        <div className="pt-4 space-y-3">
          <div className="h-1 w-full bg-slate-100 rounded-full overflow-hidden">
            <div className="h-full transition-all duration-30" style={{ width: `${progress}%`, backgroundColor: mascot.neonColor, boxShadow: `0 0 10px ${mascot.neonColor}` }}></div>
          </div>
          <p className="text-[9px] font-black text-slate-300 uppercase tracking-[0.3em]">{t.loadingMascot}</p>
        </div>
      </div>
    </div>
  );
};

export default MascotSlideshow;
