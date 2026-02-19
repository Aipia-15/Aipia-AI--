
import React, { useState, useEffect } from 'react';
import { Language } from '../types';

interface Mascot {
  name: { [K in Language]?: string };
  prefecture: { [K in Language]?: string };
  description: { [K in Language]?: string };
  color: string;
  neonColor: string;
}

const MASCOTS: Mascot[] = [
  { name: { ja: "キュンちゃん", en: "Kyun-chan" }, prefecture: { ja: "北海道", en: "Hokkaido" }, description: { ja: "エゾナキウサギがシカの被り物をしている旅の妖精。", en: "A pika wearing a deer hat traveling Hokkaido." }, color: "bg-blue-900", neonColor: "#00ffff" },
  { name: { ja: "そばっち", en: "Sobacchi" }, prefecture: { ja: "岩手県", en: "Iwate" }, description: { ja: "わんこそばをモチーフにした、おもてなし好きなキャラ。", en: "Based on Wanko Soba, loves hospitality." }, color: "bg-red-900", neonColor: "#ff4500" },
  { name: { ja: "むすび丸", en: "Musubimaru" }, prefecture: { ja: "宮城県", en: "Miyagi" }, description: { ja: "おにぎりの顔に伊達政宗の兜。宮城の食をPR中。", en: "An onigiri wearing a samurai helmet." }, color: "bg-slate-800", neonColor: "#ffd700" },
  { name: { ja: "チーバくん", en: "Chiba-kun" }, prefecture: { ja: "千葉県", en: "Chiba" }, description: { ja: "横から見ると千葉県の形をしている真っ赤な生き物。", en: "A red creature shaped like Chiba's map." }, color: "bg-rose-900", neonColor: "#ff0000" },
  { name: { ja: "ひこにゃん", en: "Hikonyan" }, prefecture: { ja: "滋賀県", en: "Shiga" }, description: { ja: "彦根藩の赤い兜を被った白猫。ゆるキャラの元祖！", en: "A white cat in a samurai helmet." }, color: "bg-red-800", neonColor: "#ffffff" },
  { name: { ja: "しまねっこ", en: "Shimanekko" }, prefecture: { ja: "島根県", en: "Shimane" }, description: { ja: "出雲大社の屋根のような帽子を被った可愛い猫。", en: "A cat wearing an Izumo-style roof hat." }, color: "bg-yellow-500", neonColor: "#333333" },
  { name: { ja: "くまモン", en: "Kumamon" }, prefecture: { ja: "熊本県", en: "Kumamoto" }, description: { ja: "熊本県の営業部長。サプライズが大好きだモン！", en: "Kumamoto's famous sales manager." }, color: "bg-black", neonColor: "#ff0000" }
];

const TRIVIA_LIST = [
  { ja: "登録されたスポットを繋ぐ、最適な移動ルートを構築中...", en: "Routing your selected spots for the best experience..." },
  { ja: "現地の時刻表と最新のイベント情報を照合しています。", en: "Checking local schedules and event info." },
  { ja: "プランA〜Eの5つのバリエーションを作成しています。", en: "Creating 5 different variations for your trip." }
];

const MascotSlideshow: React.FC<{ language: Language }> = ({ language }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [triviaIndex, setTriviaIndex] = useState(0);
  const [progress, setProgress] = useState(0);
  const SLIDE_DURATION = 8000;
  const PROGRESS_INTERVAL = 50;

  useEffect(() => {
    setCurrentIndex(Math.floor(Math.random() * MASCOTS.length));
    setTriviaIndex(Math.floor(Math.random() * TRIVIA_LIST.length));
  }, []);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % MASCOTS.length);
      setTriviaIndex((prev) => (prev + 1) % TRIVIA_LIST.length);
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
  const trivia = TRIVIA_LIST[triviaIndex];

  const getLabel = (obj?: { [K in Language]?: string }) => {
    if (!obj) return '';
    return obj[language] || obj['en'] || obj['ja'] || '';
  };

  const isLight = mascot.color === 'bg-yellow-500';

  return (
    <div className="w-full max-w-lg mx-auto bg-white rounded-[3rem] overflow-hidden shadow-2xl border border-slate-200">
      <div className={`h-64 flex items-center justify-center relative transition-colors duration-1000 ${mascot.color}`}>
        <div className="absolute top-6 left-6 flex items-center space-x-2 z-20">
           <div className="w-2 h-2 bg-red-500 rounded-full animate-ping"></div>
           <span className={`text-[10px] font-black uppercase tracking-widest ${isLight ? 'text-slate-800' : 'text-white'}`}>Processing...</span>
        </div>
        <div className="absolute inset-0 opacity-40 blur-[100px]" style={{ backgroundColor: mascot.neonColor }}></div>
        
        <div className={`relative z-10 text-center p-8 rounded-3xl backdrop-blur-xl border border-white/20 ${isLight ? 'bg-white/10' : 'bg-black/20 shadow-inner'}`}>
          <span className={`text-[11px] font-black tracking-[0.6em] block mb-2 uppercase ${isLight ? 'text-slate-800' : 'text-white/80'}`}>{getLabel(mascot.prefecture)}</span>
          <h2 className="text-4xl md:text-5xl font-serif font-bold tracking-widest leading-tight" style={{ color: isLight ? '#111' : '#fff', textShadow: isLight ? 'none' : '0 2px 20px rgba(0,0,0,0.5)' }}>
            {getLabel(mascot.name)}
          </h2>
        </div>
      </div>
      
      <div className="p-10 space-y-6 text-center bg-white">
        <div className="space-y-4">
           <div>
             <div className="text-[10px] font-black text-orange-600 uppercase tracking-widest mb-1">Regional Guide</div>
             <p className="text-slate-800 text-sm font-bold leading-relaxed">{getLabel(mascot.description)}</p>
           </div>
           <div className="h-px bg-slate-100 w-1/4 mx-auto"></div>
           <div>
             <div className="text-[10px] font-black text-cyan-600 uppercase tracking-widest mb-1">Loading Status</div>
             <p className="text-slate-500 text-[11px] font-bold truncate px-4">{getLabel(trivia as any)}</p>
           </div>
        </div>
        
        <div className="pt-4 space-y-3">
          <div className="h-2 w-full bg-slate-50 rounded-full overflow-hidden border">
            <div className="h-full transition-all duration-50" style={{ width: `${progress}%`, backgroundColor: mascot.neonColor }}></div>
          </div>
          <p className="text-[9px] font-black text-slate-400 uppercase tracking-[0.3em] truncate">
            Generating plans using your selected spots
          </p>
        </div>
      </div>
    </div>
  );
};

export default MascotSlideshow;
