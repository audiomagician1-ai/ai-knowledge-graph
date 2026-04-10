/**
 * KnowledgeMapWidget — Knowledge graph exploration stats + gamification.
 * V4.4: Coverage %, depth vs breadth profile, difficulty breakdown, top domains.
 */
import { useState, useEffect } from 'react';
import { Map, Compass, Layers, Trophy } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface CoverageData {
  total_concepts: number; started: number; mastered: number;
  learning: number; coverage_pct: number; mastery_pct: number;
}
interface DomainTop { domain_id: string; name: string; mastered: number; learning: number }
interface MapData {
  coverage: CoverageData;
  domains: { total: number; explored: number; exploration_pct: number; top: DomainTop[] };
  difficulty_breakdown: { difficulty: number; mastered: number }[];
  exploration_profile: { depth_score: number; breadth_score: number; style: string };
}

const STYLE_ICONS: Record<string, React.ReactNode> = {
  '深度型': <Layers size={12} className="text-purple-400" />,
  '广度型': <Compass size={12} className="text-blue-400" />,
  '均衡型': <Trophy size={12} className="text-amber-400" />,
};

export function KnowledgeMapWidget() {
  const [data, setData] = useState<MapData | null>(null);
  const nav = useNavigate();

  useEffect(() => {
    fetch('/api/analytics/knowledge-map-stats')
      .then(r => r.ok ? r.json() : null)
      .then(d => d && setData(d))
      .catch(() => {});
  }, []);

  if (!data) return null;

  const { coverage: c, domains: d, exploration_profile: ep } = data;

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4">
      <div className="flex items-center gap-2 mb-3">
        <Map size={16} className="text-blue-400" />
        <h3 className="text-sm font-semibold">知识图谱探索</h3>
        <span className="ml-auto flex items-center gap-1 text-[10px] opacity-60">
          {STYLE_ICONS[ep.style]}{ep.style}
        </span>
      </div>

      {/* Coverage progress bar */}
      <div className="mb-3">
        <div className="flex justify-between text-[10px] mb-1">
          <span className="opacity-40">覆盖率</span>
          <span>{c.started} / {c.total_concepts} ({c.coverage_pct}%)</span>
        </div>
        <div className="w-full bg-white/10 rounded-full h-2">
          <div className="h-full rounded-full bg-gradient-to-r from-blue-500 to-emerald-400 transition-all"
            style={{ width: `${Math.min(c.coverage_pct, 100)}%` }} />
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-4 gap-2 mb-3 text-center">
        <div className="bg-white/5 rounded-lg p-1.5">
          <div className="text-sm font-bold text-emerald-400">{c.mastered}</div>
          <div className="text-[10px] opacity-40">掌握</div>
        </div>
        <div className="bg-white/5 rounded-lg p-1.5">
          <div className="text-sm font-bold text-amber-400">{c.learning}</div>
          <div className="text-[10px] opacity-40">进行中</div>
        </div>
        <div className="bg-white/5 rounded-lg p-1.5">
          <div className="text-sm font-bold">{d.explored}/{d.total}</div>
          <div className="text-[10px] opacity-40">领域</div>
        </div>
        <div className="bg-white/5 rounded-lg p-1.5">
          <div className="text-sm font-bold">{ep.depth_score}%</div>
          <div className="text-[10px] opacity-40">深度</div>
        </div>
      </div>

      {/* Top domains */}
      {d.top.length > 0 && (
        <div className="space-y-1.5 mb-3">
          <div className="text-[10px] opacity-40">探索领域 TOP</div>
          {d.top.slice(0, 4).map(dom => (
            <button key={dom.domain_id} onClick={() => nav(`/graph?domain=${dom.domain_id}`)}
              className="w-full flex items-center gap-2 p-1.5 hover:bg-white/10 rounded-lg transition-colors text-left">
              <span className="text-xs truncate flex-1">{dom.name}</span>
              <span className="text-[10px] text-emerald-400">{dom.mastered} 掌握</span>
              <span className="text-[10px] opacity-40">{dom.learning} 进行</span>
            </button>
          ))}
        </div>
      )}

      {/* Difficulty breakdown mini bars */}
      {data.difficulty_breakdown.length > 0 && (
        <div>
          <div className="text-[10px] opacity-40 mb-1">难度分布</div>
          <div className="flex items-end gap-[3px] h-6">
            {data.difficulty_breakdown.map(d => {
              const maxM = Math.max(...data.difficulty_breakdown.map(x => x.mastered), 1);
              const h = Math.max(Math.round((d.mastered / maxM) * 24), 2);
              return (
                <div key={d.difficulty} className="flex-1 flex flex-col items-center gap-0.5">
                  <div className="w-full bg-emerald-500/50 rounded-t-sm" style={{ height: `${h}px` }} />
                  <span className="text-[8px] opacity-30">{d.difficulty}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
