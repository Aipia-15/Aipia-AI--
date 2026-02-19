
import React, { useState } from 'react';
import { GoogleGenAI } from '@google/genai';
import { Language } from '../types';
import { translations } from '../translations';

interface InquiryFormProps {
  language: Language;
}

const InquiryForm: React.FC<InquiryFormProps> = ({ language }) => {
  const t = translations[language];
  // 管理者用メールアドレス
  const DEST_EMAIL = "2716soka@gmail.com";
  // 送信先エンドポイント（※開発時は有効なIDへの差し替えが必要です）
  const FORMSPREE_ENDPOINT = "https://formspree.io/f/xvgzvypn";
  
  const [formData, setFormData] = useState({
    name: '',
    gender: '',
    age: '',
    occupation: '',
    email: '',
    message: ''
  });
  
  const [step, setStep] = useState<'idle' | 'processing' | 'success' | 'error'>('idle');
  const [statusMessage, setStatusMessage] = useState("");
  const [aiSummary, setAiSummary] = useState("");
  const [copyDone, setCopyDone] = useState(false);

  const genders = [
    { value: 'male', label: t.genderMale },
    { value: 'female', label: t.genderFemale },
    { value: 'other', label: t.genderOther }
  ];

  const ages = [
    { value: '10s', label: t.age10s },
    { value: '20s', label: t.age20s },
    { value: '30s', label: t.age30s },
    { value: '40s', label: t.age40s },
    { value: '50s', label: t.age50s },
    { value: '60s+', label: t.age60s }
  ];

  const occupations = [
    { value: 'employee', label: t.occEmployee },
    { value: 'self', label: t.occSelf },
    { value: 'student', label: t.occStudent },
    { value: 'part-time', label: t.occPart },
    { value: 'other', label: t.occOther }
  ];

  const getFullReportText = () => {
    return `【AI要約レポート】\n${aiSummary}\n\n` +
           `--- 相談者情報 ---\n` +
           `氏名: ${formData.name}\n` +
           `属性: ${formData.gender} / ${formData.age} / ${formData.occupation}\n` +
           `返信先: ${formData.email}\n\n` +
           `【メッセージ本文】\n${formData.message}`;
  };

  const handleManualCopy = () => {
    navigator.clipboard.writeText(getFullReportText()).then(() => {
      setCopyDone(true);
      setTimeout(() => setCopyDone(false), 3000);
    });
  };

  const handleAISubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name || !formData.email || !formData.message) {
      alert("必須項目を入力してください。");
      return;
    }

    setStep('processing');
    setStatusMessage("AIが内容を分析・要約しています...");
    
    let summaryText = "";

    try {
      // 1. AIによる要約
      const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
      const prompt = `
        旅行アプリへの問い合わせを、管理者のために3行で要約してください。
        名前: ${formData.name}
        属性: ${formData.gender}, ${formData.age}, ${formData.occupation}
        内容: ${formData.message}
        
        形式:
        【要約】
        [内容]
        【優先度】
        [高/中/低]
      `;

      const aiResponse = await ai.models.generateContent({
        model: 'gemini-3-flash-preview',
        contents: prompt
      });
      summaryText = aiResponse.text || "AI要約を作成できませんでした。";
      setAiSummary(summaryText);

      // 2. データ送信 (AJAX)
      setStatusMessage("クラウド経由でコンシェルジュへ送信中...");
      
      const response = await fetch(FORMSPREE_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          name: formData.name,
          email: formData.email,
          message: formData.message,
          attributes: `${formData.gender}, ${formData.age}, ${formData.occupation}`,
          ai_summary: summaryText,
          _subject: `[Plan De Viaje] お問い合わせ: ${formData.name}様`
        })
      });

      if (response.ok) {
        setStep('success');
      } else {
        const errorData = await response.json().catch(() => ({}));
        console.error("Transmission Error Response:", errorData);
        throw new Error('Server returned error');
      }

    } catch (err: any) {
      console.error("Submission failed", err);
      setStep('error');
      setStatusMessage("現在クラウド送信が利用できません。手動送信モードに切り替えます。");
    }
  };

  if (step === 'success') {
    return (
      <div className="bg-white border border-slate-200 rounded-[2.5rem] p-8 md:p-12 shadow-2xl animate-in zoom-in-95 duration-500 text-center space-y-8 max-w-2xl mx-auto">
        <div className="w-24 h-24 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto mb-6 shadow-inner">
          <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <div className="space-y-4">
          <h2 className="text-3xl font-serif font-bold text-slate-900">送信が完了しました</h2>
          <p className="text-slate-500 text-sm max-w-md mx-auto leading-relaxed">
            ご相談を承りました。<br/>
            順次、ご入力いただいたメールアドレスへ回答させていただきます。
          </p>
        </div>
        <button 
          onClick={() => { setStep('idle'); setFormData({ name: '', gender: '', age: '', occupation: '', email: '', message: '' }); }}
          className="w-full py-4 bg-slate-900 text-white font-bold hover:bg-slate-800 rounded-2xl transition-all shadow-xl"
        >
          新しいお問い合わせを作成
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white border border-slate-200 rounded-[2.5rem] p-8 md:p-12 shadow-2xl animate-in fade-in duration-500 relative overflow-hidden max-w-3xl mx-auto">
      {/* 処理中オーバーレイ */}
      {step === 'processing' && (
        <div className="absolute inset-0 z-50 bg-white/95 backdrop-blur-sm flex flex-col items-center justify-center p-8 text-center">
          <div className="w-full max-w-xs space-y-6">
            <div className="flex justify-center">
               <div className="w-20 h-20 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
            <div className="space-y-2">
              <p className="text-xl font-bold text-slate-800 italic">{statusMessage}</p>
              <p className="text-xs text-slate-400">通信を維持しています。そのままお待ちください。</p>
            </div>
          </div>
        </div>
      )}

      {/* エラー（手動送信モード）オーバーレイ */}
      {step === 'error' && (
        <div className="absolute inset-0 z-50 bg-white/98 backdrop-blur-md flex flex-col items-center justify-center p-8 md:p-12 animate-in fade-in duration-300">
          <div className="max-w-md w-full space-y-8">
            <div className="text-center space-y-3">
              <div className="w-16 h-16 bg-amber-100 text-amber-600 rounded-full flex items-center justify-center mx-auto">
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-slate-900">自動送信に失敗しました</h3>
              <p className="text-slate-500 text-xs">
                サーバーへの接続が制限されています。<br/>
                作成されたAI要約をコピーして、直接 <b>{DEST_EMAIL}</b> 宛にメールまたはSNSで送信してください。
              </p>
            </div>

            <div className="bg-slate-50 border border-slate-200 rounded-2xl p-5 space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">送信先アドレス</span>
                <button 
                  onClick={() => { navigator.clipboard.writeText(DEST_EMAIL); alert("アドレスをコピーしました"); }}
                  className="text-[10px] font-bold text-emerald-600 underline"
                >
                  アドレスをコピー
                </button>
              </div>
              <p className="text-sm font-mono font-bold text-slate-800 bg-white p-3 rounded-lg border border-slate-100">{DEST_EMAIL}</p>
              
              <div className="space-y-2">
                 <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest block">AI要約付きレポート全文</span>
                 <div className="bg-white p-3 rounded-lg border border-slate-100 max-h-32 overflow-y-auto text-[10px] text-slate-600 whitespace-pre-wrap">
                   {getFullReportText()}
                 </div>
              </div>

              <button 
                onClick={handleManualCopy}
                className={`w-full py-4 rounded-xl font-bold text-sm transition-all shadow-md ${copyDone ? 'bg-emerald-600 text-white' : 'bg-slate-900 text-white hover:bg-slate-800'}`}
              >
                {copyDone ? "✓ レポートをコピーしました" : "レポートを全文コピー"}
              </button>
            </div>

            <button onClick={() => setStep('idle')} className="w-full text-slate-400 text-xs font-bold hover:text-slate-600">入力画面に戻る</button>
          </div>
        </div>
      )}

      <div className="space-y-2 mb-10 text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-emerald-50 text-emerald-600 rounded-full mb-4">
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </div>
        <h2 className="text-3xl font-serif font-bold text-slate-900">{t.inquiry}</h2>
        <p className="text-slate-500 text-sm">
          AIが内容を分析し、直接コンシェルジュデスクへ送信します。
        </p>
      </div>

      <form onSubmit={handleAISubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="text-xs font-black text-slate-400 uppercase tracking-widest ml-1">{t.inquiryName} *</label>
            <input 
              type="text" required value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-slate-900 font-bold focus:ring-4 focus:ring-emerald-500/10 outline-none transition-all"
              placeholder="例：山田 太郎"
            />
          </div>

          <div className="space-y-2">
            <label className="text-xs font-black text-slate-400 uppercase tracking-widest ml-1">{t.inquiryEmail} *</label>
            <input 
              type="email" required value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-slate-900 font-bold focus:ring-4 focus:ring-emerald-500/10 outline-none transition-all"
              placeholder="example@mail.com"
            />
          </div>

          <div className="space-y-2">
            <label className="text-xs font-black text-slate-400 uppercase tracking-widest ml-1">{t.inquiryGender} *</label>
            <select 
              required value={formData.gender}
              onChange={(e) => setFormData({...formData, gender: e.target.value})}
              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-slate-900 font-bold focus:ring-4 focus:ring-emerald-500/10 outline-none transition-all"
            >
              <option value="">選択してください</option>
              {genders.map(g => <option key={g.value} value={g.label}>{g.label}</option>)}
            </select>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-black text-slate-400 uppercase tracking-widest ml-1">{t.inquiryAge} *</label>
            <select 
              required value={formData.age}
              onChange={(e) => setFormData({...formData, age: e.target.value})}
              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-slate-900 font-bold focus:ring-4 focus:ring-emerald-500/10 outline-none transition-all"
            >
              <option value="">選択してください</option>
              {ages.map(a => <option key={a.value} value={a.label}>{a.label}</option>)}
            </select>
          </div>

          <div className="space-y-2 md:col-span-2">
            <label className="text-xs font-black text-slate-400 uppercase tracking-widest ml-1">{t.inquiryOccupation} *</label>
            <select 
              required value={formData.occupation}
              onChange={(e) => setFormData({...formData, occupation: e.target.value})}
              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-slate-900 font-bold focus:ring-4 focus:ring-emerald-500/10 outline-none transition-all"
            >
              <option value="">選択してください</option>
              {occupations.map(o => <option key={o.value} value={o.label}>{o.label}</option>)}
            </select>
          </div>
        </div>

        <div className="space-y-2">
          <label className="text-xs font-black text-slate-400 uppercase tracking-widest ml-1">{t.inquiryMessage} *</label>
          <textarea 
            required rows={5} value={formData.message}
            onChange={(e) => setFormData({...formData, message: e.target.value})}
            className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-slate-900 font-bold focus:ring-4 focus:ring-emerald-500/10 outline-none transition-all resize-none"
            placeholder="相談内容を入力してください..."
          />
        </div>

        <button 
          type="submit" 
          disabled={step === 'processing'}
          className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-5 rounded-2xl shadow-xl shadow-emerald-200 transition-all flex flex-col items-center justify-center group active:scale-[0.98] disabled:opacity-50"
        >
          <div className="flex items-center space-x-2 mb-1">
            <svg className="w-6 h-6 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
            <span className="text-lg">AI要約して直接送信する</span>
          </div>
          <span className="text-[10px] text-emerald-100 font-medium uppercase tracking-[0.2em]">Secure Cloud Submission</span>
        </button>
      </form>
    </div>
  );
};

export default InquiryForm;
