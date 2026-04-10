import { useState, useEffect } from 'react';
import { Camera, Trophy, Flame, BarChart3, Download } from 'lucide-react';

interface SnapshotData {
  snapshot_version: string;
  overview: {
    total_concepts: number;
    mastered: number;
    learning: number;
    completion_pct: number;
    avg_score: number;
    total_sessions: number;
  };
  streak: { current: number; longest: number };
  efficiency: { avg_sessions_to_master: number; mastery_rate: number };
  top_domains: Array<{ domain_id: string; domain_name: string; mastered: number; total: number; percentage: number }>;
  recent_mastered: Array<{ concept_id: string; name: string; domain_id: string; score: number }>;
  domains_started: number;
  domains_total: number;
}

const API = import.meta.env.VITE_API_URL || '';

export function ProgressSnapshotWidget() {
  const [data, setData] = useState<SnapshotData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/api/analytics/progress-snapshot`)
      .then(r => r.json())
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="animate-pulse h-48 bg-white/5 rounded-xl" />;
  if (!data) return null;

  const { overview, streak, efficiency, top_domains } = data;

  const handleExport = () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `progress-snapshot-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="bg-white/5 rounded-xl p-4 border border-white/10">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Camera className="w-4 h-4 text-cyan-400" />
          <h3 className="text-sm font-semibold text-white/90">Progress Snapshot</h3>
        </div>
        <button
          onClick={handleExport}
          className="p-1.5 rounded-lg hover:bg-white/10 transition-colors"
          title="Export JSON"
        >
          <Download className="w-3.5 h-3.5 text-white/50" />
        </button>
      </div>

      <div className="grid grid-cols-2 gap-2 mb-3">
        <div className="bg-white/5 rounded-lg p-2 text-center">
          <div className="text-lg font-bold text-emerald-400">{overview.mastered}</div>
          <div className="text-[10px] text-white/50">Mastered</div>
        </div>
        <div className="bg-white/5 rounded-lg p-2 text-center">
          <div className="text-lg font-bold text-cyan-400">{overview.completion_pct}%</div>
          <div className="text-[10px] text-white/50">Complete</div>
        </div>
        <div className="bg-white/5 rounded-lg p-2 text-center flex items-center justify-center gap-1">
          <Flame className="w-3 h-3 text-orange-400" />
          <span className="text-sm font-bold text-orange-400">{streak.current}d</span>
          <span className="text-[10px] text-white/40">streak</span>
        </div>
        <div className="bg-white/5 rounded-lg p-2 text-center flex items-center justify-center gap-1">
          <BarChart3 className="w-3 h-3 text-purple-400" />
          <span className="text-sm font-bold text-purple-400">{overview.avg_score}</span>
          <span className="text-[10px] text-white/40">avg</span>
        </div>
      </div>

      {top_domains.length > 0 && (
        <div className="space-y-1.5">
          <div className="text-[10px] text-white/40 uppercase tracking-wider flex items-center gap-1">
            <Trophy className="w-3 h-3" /> Top Domains
          </div>
          {top_domains.slice(0, 3).map(d => (
            <div key={d.domain_id} className="flex items-center gap-2">
              <div className="flex-1 text-xs text-white/70 truncate">{d.domain_name}</div>
              <div className="w-16 h-1.5 bg-white/10 rounded-full overflow-hidden">
                <div
                  className="h-full bg-emerald-500 rounded-full"
                  style={{ width: `${d.percentage}%` }}
                />
              </div>
              <div className="text-[10px] text-white/50 w-8 text-right">{d.percentage}%</div>
            </div>
          ))}
        </div>
      )}

      <div className="mt-2 pt-2 border-t border-white/5 flex justify-between text-[10px] text-white/30">
        <span>{efficiency.avg_sessions_to_master} avg sessions/mastery</span>
        <span>{data.domains_started}/{data.domains_total} domains</span>
      </div>
    </div>
  );
}
