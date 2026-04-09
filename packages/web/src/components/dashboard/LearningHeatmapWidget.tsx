import { useState, useEffect } from 'react';
import { Grid3X3, Flame } from 'lucide-react';

interface HeatmapCell {
  concept_id: string;
  name: string;
  difficulty: number;
  status: string;
  sessions: number;
  score: number;
  intensity: number;
}

interface SubdomainRow {
  subdomain_id: string;
  concepts: HeatmapCell[];
  count: number;
  avg_intensity: number;
  mastered_count: number;
}

interface HeatmapData {
  domain_id: string;
  subdomains: SubdomainRow[];
  summary: {
    total_concepts: number;
    active_concepts: number;
    mastered_concepts: number;
    coverage_pct: number;
    mastery_pct: number;
  };
}

function intensityColor(v: number): string {
  if (v >= 0.8) return 'bg-green-500/70';
  if (v >= 0.5) return 'bg-blue-500/50';
  if (v >= 0.2) return 'bg-purple-500/30';
  if (v > 0) return 'bg-white/15';
  return 'bg-white/5';
}

export default function LearningHeatmapWidget() {
  const [data, setData] = useState<HeatmapData | null>(null);
  const [domain, setDomain] = useState('ai-engineering');
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    const base = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    fetch(`${base}/api/analytics/learning-heatmap/${domain}`)
      .then(r => r.ok ? r.json() : null)
      .then(d => d && setData(d))
      .catch(() => {});
  }, [domain]);

  const sm = data?.summary;
  const rows = expanded ? data?.subdomains : data?.subdomains?.slice(0, 4);

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Grid3X3 className="w-4 h-4 text-orange-400" />
          <h3 className="text-sm font-semibold text-white/90">学习热力图</h3>
        </div>
        <select
          value={domain}
          onChange={e => setDomain(e.target.value)}
          className="bg-white/10 text-xs text-white/70 rounded px-2 py-1 outline-none"
        >
          {['ai-engineering', 'machine-learning', 'deep-learning', 'programming', 'software-engineering', 'game-design'].map(d => (
            <option key={d} value={d} className="bg-gray-900">{d}</option>
          ))}
        </select>
      </div>

      {sm && (
        <div className="flex gap-3 mb-3 text-[10px] text-white/50">
          <span>{sm.total_concepts} 概念</span>
          <span className="text-blue-400">{sm.coverage_pct}% 已接触</span>
          <span className="text-green-400">{sm.mastery_pct}% 已掌握</span>
        </div>
      )}

      {rows?.map(row => (
        <div key={row.subdomain_id} className="mb-2">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] text-white/40 truncate w-24">{row.subdomain_id}</span>
            <span className="text-[10px] text-white/30">{row.mastered_count}/{row.count}</span>
          </div>
          <div className="flex flex-wrap gap-[2px]">
            {row.concepts.map(cell => (
              <div
                key={cell.concept_id}
                className={`w-3 h-3 rounded-sm ${intensityColor(cell.intensity)} hover:ring-1 hover:ring-white/30 transition cursor-default`}
                title={`${cell.name} — ${cell.score}分 (${cell.sessions}次)`}
              />
            ))}
          </div>
        </div>
      ))}

      {data && data.subdomains.length > 4 && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-[10px] text-white/40 hover:text-white/60 mt-2"
        >
          {expanded ? '收起' : `展开全部 ${data.subdomains.length} 个子域`}
        </button>
      )}

      {/* Legend */}
      <div className="flex items-center gap-2 mt-3 text-[10px] text-white/30">
        <Flame className="w-3 h-3" />
        <div className="flex gap-1 items-center">
          {[0, 0.2, 0.5, 0.8].map(v => (
            <div key={v} className={`w-3 h-3 rounded-sm ${intensityColor(v)}`} />
          ))}
          <span className="ml-1">低→高</span>
        </div>
      </div>
    </div>
  );
}
