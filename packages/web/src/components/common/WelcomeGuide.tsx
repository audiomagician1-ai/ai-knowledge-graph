/**
 * WelcomeGuide — First-visit overlay with value proposition + quick start.
 * Behavior design: P0 止血 — 解决首页"看不懂、选不了、走不进来"问题。
 * Principles: S1-first value framing, default recommendation, single clear CTA.
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, BookOpen, Brain, ChevronRight, X } from 'lucide-react';

const STORAGE_KEY = 'akg-welcome-dismissed';

/** Recommended starter domains — curated for broad appeal */
const STARTER_DOMAINS = [
  { id: 'ai-engineering', name: 'AI编程', desc: '从零到AI系统设计', color: '#8B7EC8', icon: '🤖' },
  { id: 'mathematics', name: '数学', desc: '从算术到高等数学', color: '#7FA4C9', icon: '📐' },
  { id: 'psychology', name: '心理学', desc: '理解人类行为与认知', color: '#B89DBF', icon: '🧠' },
  { id: 'english', name: '英语', desc: '系统学习英语体系', color: '#C9B87A', icon: '🌍' },
  { id: 'physics', name: '物理', desc: '探索自然的基本规律', color: '#7AB5AD', icon: '⚛️' },
];

export function WelcomeGuide() {
  const nav = useNavigate();
  const [show, setShow] = useState(false);
  const [step, setStep] = useState(0); // 0: value prop, 1: pick domain

  useEffect(() => {
    const dismissed = localStorage.getItem(STORAGE_KEY);
    if (!dismissed) setShow(true);
  }, []);

  const dismiss = () => {
    localStorage.setItem(STORAGE_KEY, Date.now().toString());
    setShow(false);
  };

  const pickDomain = (id: string) => {
    dismiss();
    nav(`/domain/${id}`);
  };

  if (!show) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/40 backdrop-blur-sm"
         onClick={(e) => { if (e.target === e.currentTarget) dismiss(); }}>
      <div className="relative w-[90vw] max-w-md bg-white rounded-xl shadow-md overflow-hidden"
           style={{ animation: 'fadeInScale 0.3s ease-out' }}>
        {/* Close button */}
        <button onClick={dismiss}
                className="absolute top-3 right-3 p-1.5 rounded-full hover:bg-gray-100 transition-colors z-10"
                aria-label="关闭">
          <X size={18} className="text-gray-400" />
        </button>

        {step === 0 ? (
          /* Step 0: Value Proposition */
          <div className="px-6 pt-8 pb-6">
            <div className="flex items-center gap-2 mb-4">
              <Sparkles size={24} className="text-purple-500" />
              <h2 className="text-xl font-bold text-gray-900">AI知识图谱</h2>
            </div>

            <p className="text-base text-gray-700 mb-6 leading-relaxed">
              通过<strong>AI对话</strong>学会任何知识 — 不是死记硬背，
              而是像和老师聊天一样<strong>真正理解</strong>。
            </p>

            {/* 3 key features */}
            <div className="space-y-3 mb-6">
              <div className="flex items-start gap-3">
                <div className="mt-0.5 p-1.5 rounded-lg bg-purple-50">
                  <Brain size={16} className="text-purple-500" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">AI引导式学习</p>
                  <p className="text-xs text-gray-500">AI先讲解，再用选择题检验你的理解</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="mt-0.5 p-1.5 rounded-lg bg-blue-50">
                  <BookOpen size={16} className="text-blue-500" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">36个知识领域</p>
                  <p className="text-xs text-gray-500">6,300+知识点，从AI编程到心理学</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="mt-0.5 p-1.5 rounded-lg bg-green-50">
                  <Sparkles size={16} className="text-green-500" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">点亮知识图谱</p>
                  <p className="text-xs text-gray-500">每掌握一个知识点，技能树就亮一个节点</p>
                </div>
              </div>
            </div>

            <button onClick={() => setStep(1)}
                    className="w-full py-3 px-4 rounded-xl text-white font-semibold text-sm
                               bg-gradient-to-r from-purple-500 to-blue-500
                               hover:from-purple-600 hover:to-blue-600
                               transition-all shadow-lg shadow-purple-200
                               flex items-center justify-center gap-2">
              开始学习
              <ChevronRight size={16} />
            </button>

            <p className="text-center text-xs text-gray-400 mt-3">
              无需注册 · 完全免费 · 随时开始
            </p>
          </div>
        ) : (
          /* Step 1: Pick a starter domain */
          <div className="px-6 pt-6 pb-6">
            <h3 className="text-lg font-bold text-gray-900 mb-1">选一个感兴趣的领域</h3>
            <p className="text-xs text-gray-500 mb-4">推荐从这些热门领域开始，之后可以随时切换</p>

            <div className="space-y-2 mb-4">
              {STARTER_DOMAINS.map(d => (
                <button key={d.id}
                        onClick={() => pickDomain(d.id)}
                        className="w-full flex items-center gap-3 p-3 rounded-xl border border-gray-100
                                   hover:border-purple-200 hover:bg-purple-50/50 transition-all text-left group">
                  <span className="text-2xl">{d.icon}</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-gray-900">{d.name}</p>
                    <p className="text-xs text-gray-500">{d.desc}</p>
                  </div>
                  <ChevronRight size={16} className="text-gray-300 group-hover:text-purple-400 transition-colors" />
                </button>
              ))}
            </div>

            <button onClick={dismiss}
                    className="w-full text-center text-xs text-gray-400 hover:text-gray-600 py-2">
              我自己逛逛
            </button>
          </div>
        )}

        <style>{`
          @keyframes fadeInScale {
            from { opacity: 0; transform: scale(0.95); }
            to { opacity: 1; transform: scale(1); }
          }
        `}</style>
      </div>
    </div>
  );
}
