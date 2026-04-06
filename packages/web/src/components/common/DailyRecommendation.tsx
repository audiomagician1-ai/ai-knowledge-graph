/**
 * DailyRecommendation — "Today's Concept" card for the homepage footer area.
 * Behavior design: Tiny Habits 配方2 — "完成复习后 → 看今日推荐 → 知识版图+1"
 * Principle: Variable reward (new concept each day) + SDT competence (always achievable).
 *
 * Uses a deterministic daily rotation (date hash → concept index) so all users
 * see the same "concept of the day" — enables social proof ("大家今天都在学X").
 */
import { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lightbulb, ChevronRight } from 'lucide-react';

/** Curated "best of" concepts — diverse domains, entry-level difficulty */
const DAILY_POOL = [
  { domain: 'ai-engineering', concept: 'neural-network-basics', name: '神经网络基础', icon: '🤖' },
  { domain: 'mathematics', concept: 'set-theory', name: '集合论', icon: '📐' },
  { domain: 'physics', concept: 'newtons-laws', name: '牛顿运动定律', icon: '⚛️' },
  { domain: 'psychology', concept: 'cognitive-bias', name: '认知偏差', icon: '🧠' },
  { domain: 'economics', concept: 'supply-demand', name: '供给与需求', icon: '📈' },
  { domain: 'biology', concept: 'cell-structure', name: '细胞结构', icon: '🧬' },
  { domain: 'history', concept: 'industrial-revolution', name: '工业革命', icon: '📜' },
  { domain: 'philosophy', concept: 'logic-basics', name: '逻辑学基础', icon: '💭' },
  { domain: 'machine-learning', concept: 'supervised-learning', name: '监督学习', icon: '📊' },
  { domain: 'english', concept: 'tenses', name: '英语时态', icon: '🌍' },
  { domain: 'chemistry', concept: 'periodic-table', name: '元素周期表', icon: '🧪' },
  { domain: 'statistics', concept: 'probability-basics', name: '概率基础', icon: '🎲' },
  { domain: 'data-science', concept: 'data-cleaning', name: '数据清洗', icon: '🔧' },
  { domain: 'algorithms', concept: 'sorting-algorithms', name: '排序算法', icon: '🔢' },
  { domain: 'game-design', concept: 'game-loop', name: '游戏循环', icon: '🎮' },
  { domain: 'astronomy', concept: 'solar-system', name: '太阳系', icon: '🌌' },
  { domain: 'music', concept: 'music-theory-basics', name: '乐理基础', icon: '🎵' },
  { domain: 'sociology', concept: 'social-stratification', name: '社会分层', icon: '🏛️' },
  { domain: 'art', concept: 'color-theory', name: '色彩理论', icon: '🎨' },
  { domain: 'literature', concept: 'narrative-structure', name: '叙事结构', icon: '📚' },
  { domain: 'systems-theory', concept: 'system-definition', name: '系统的定义', icon: '🔄' },
  { domain: 'cybernetics', concept: 'cybernetics-overview', name: '控制论概述', icon: '🎛️' },
  { domain: 'finance', concept: 'compound-interest', name: '复利', icon: '💰' },
  { domain: 'graphics', concept: 'rendering-pipeline', name: '渲染管线', icon: '🖥️' },
  { domain: 'robotics', concept: 'robot-kinematics', name: '机器人运动学', icon: '🦾' },
  { domain: 'education', concept: 'learning-theories', name: '学习理论', icon: '📖' },
  { domain: 'linguistics', concept: 'phonetics', name: '语音学', icon: '🗣️' },
  { domain: 'security', concept: 'encryption-basics', name: '加密基础', icon: '🔒' },
  { domain: 'ux-design', concept: 'user-research', name: '用户研究', icon: '🎯' },
  { domain: 'law', concept: 'rule-of-law', name: '法治原则', icon: '⚖️' },
];

function getDailyIndex(): number {
  const now = new Date();
  // Day-based hash: year * 366 + month * 31 + day
  const dayHash = now.getFullYear() * 366 + now.getMonth() * 31 + now.getDate();
  return dayHash % DAILY_POOL.length;
}

export function DailyRecommendation() {
  const nav = useNavigate();

  const today = useMemo(() => {
    const idx = getDailyIndex();
    return DAILY_POOL[idx];
  }, []);

  return (
    <div
      className="absolute left-0 right-0 flex justify-center pointer-events-auto"
      style={{ bottom: 24, zIndex: 10 }}
    >
      <button
        onClick={() => nav(`/domain/${today.domain}`)}
        className="flex items-center gap-3 px-5 py-3 rounded-2xl shadow-lg
                   border border-gray-200/60 backdrop-blur-md
                   hover:shadow-xl hover:scale-[1.02] transition-all group"
        style={{
          backgroundColor: 'rgba(255, 255, 255, 0.85)',
          maxWidth: '90vw',
        }}
      >
        <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-amber-50">
          <Lightbulb size={18} className="text-amber-500" />
        </div>
        <div className="text-left min-w-0">
          <div className="text-xs text-gray-400 font-medium">今日推荐</div>
          <div className="text-sm font-semibold text-gray-800 flex items-center gap-1.5">
            <span>{today.icon}</span>
            <span className="truncate">{today.name}</span>
          </div>
        </div>
        <ChevronRight size={16} className="text-gray-300 group-hover:text-amber-400 transition-colors ml-1 shrink-0" />
      </button>
    </div>
  );
}
