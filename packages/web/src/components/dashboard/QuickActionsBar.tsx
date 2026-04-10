/**
 * QuickActionsBar — Smart contextual action shortcuts at Dashboard top.
 * V4.2: Reduces clicks for the 3 most common user actions.
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BookOpen, RefreshCw, Compass, Zap, ChevronRight } from 'lucide-react';

interface ActionData {
  reviewDue: number;
  continueId: string | null;
  continueName: string;
  continueDomain: string;
  exploreDomain: string | null;
  exploreName: string;
}

export function QuickActionsBar() {
  const navigate = useNavigate();
  const [data, setData] = useState<ActionData | null>(null);

  useEffect(() => {
    const base = import.meta.env.VITE_API_URL || '';
    // Fetch data for smart actions
    Promise.all([
      fetch(`${base}/api/learning/due?limit=1`).then(r => r.ok ? r.json() : null).catch(() => null),
      fetch(`${base}/api/analytics/study-plan?daily_minutes=30&days=1`).then(r => r.ok ? r.json() : null).catch(() => null),
      fetch(`${base}/api/analytics/domain-recommendation?limit=1`).then(r => r.ok ? r.json() : null).catch(() => null),
    ]).then(([due, plan, rec]) => {
      const reviewDue = due?.concepts?.length ?? due?.due_count ?? 0;

      // Find first "continue" item from study plan
      const planItems = plan?.plan?.[0]?.items ?? [];
      const continueItem = planItems.find((i: { type: string }) => i.type === 'continue') || planItems.find((i: { type: string }) => i.type === 'new');
      const continueId = continueItem?.concept_id ?? null;
      const continueName = continueItem?.name ?? '继续学习';
      const continueDomain = continueItem?.domain_id ?? '';

      // Explore recommendation
      const exploreDomain = rec?.recommendations?.[0]?.domain_id ?? null;
      const exploreName = rec?.recommendations?.[0]?.domain_name ?? '探索新领域';

      setData({ reviewDue, continueId, continueName, continueDomain, exploreDomain, exploreName });
    });
  }, []);

  if (!data) return null;

  const actions = [
    {
      show: data.reviewDue > 0,
      icon: <RefreshCw size={15} />,
      label: `复习 (${data.reviewDue})`,
      desc: '有待复习的概念',
      color: 'text-amber-400 border-amber-400/20 bg-amber-400/5',
      onClick: () => navigate('/review'),
    },
    {
      show: !!data.continueId,
      icon: <BookOpen size={15} />,
      label: data.continueName,
      desc: '继续上次学习',
      color: 'text-blue-400 border-blue-400/20 bg-blue-400/5',
      onClick: () => navigate(`/learn/${data.continueDomain}/${data.continueId}`),
    },
    {
      show: !!data.exploreDomain,
      icon: <Compass size={15} />,
      label: data.exploreName,
      desc: '推荐探索',
      color: 'text-emerald-400 border-emerald-400/20 bg-emerald-400/5',
      onClick: () => navigate(`/domain/${data.exploreDomain}`),
    },
  ].filter(a => a.show);

  if (actions.length === 0) return null;

  return (
    <div className="flex gap-3 flex-wrap">
      <div className="flex items-center gap-1.5 text-xs opacity-40">
        <Zap size={13} /> 快捷操作
      </div>
      {actions.map((a, i) => (
        <button
          key={i}
          onClick={a.onClick}
          className={`flex items-center gap-2 px-3 py-2 rounded-lg border transition-all hover:scale-[1.02] active:scale-[0.98] ${a.color}`}
        >
          {a.icon}
          <div className="text-left">
            <div className="text-xs font-medium truncate max-w-[120px]">{a.label}</div>
            <div className="text-[10px] opacity-50">{a.desc}</div>
          </div>
          <ChevronRight size={12} className="opacity-30" />
        </button>
      ))}
    </div>
  );
}
