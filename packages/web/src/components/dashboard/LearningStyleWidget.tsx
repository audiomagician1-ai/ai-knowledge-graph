import { useState, useEffect } from 'react';
import { User, Clock, BarChart3 } from 'lucide-react';

interface Trait {
  trait: string;
  description: string;
  icon: string;
}

interface StyleData {
  style: string;
  traits: Trait[];
  metrics: {
    total_mastered: number;
    total_sessions: number;
    avg_sessions_to_master: number;
    active_domains: number;
    consistency_pct: number;
    active_days_30d: number;
    peak_hour: number;
    time_preference: string;
    current_streak: number;
  };
  time_distribution: {
    morning: number;
    afternoon: number;
    evening: number;
    night: number;
  };
}

export default function LearningStyleWidget() {
  const [data, setData] = useState<StyleData | null>(null);

  useEffect(() => {
    const base = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    fetch(`${base}/api/analytics/learning-style`)
      .then(r => r.ok ? r.json() : null)
      .then(d => d && setData(d))
      .catch(() => {});
  }, []);

  if (!data) return null;

  const m = data.metrics;
  const td = data.time_distribution;
  const maxTd = Math.max(td.morning, td.afternoon, td.evening, td.night, 1);

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4">
      <div className="flex items-center gap-2 mb-3">
        <User className="w-4 h-4 text-amber-400" />
        <h3 className="text-sm font-semibold text-white/90">学习风格</h3>
        <span className="ml-auto px-2 py-0.5 bg-amber-500/20 text-amber-300 rounded-full text-[10px] font-medium">
          {data.style}
        </span>
      </div>

      {/* Traits */}
      {data.traits.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-3">
          {data.traits.map((t, i) => (
            <div key={i} className="bg-white/5 rounded-lg px-2.5 py-1.5 text-xs" title={t.description}>
              <span className="mr-1">{t.icon}</span>
              <span className="text-white/70">{t.trait}</span>
            </div>
          ))}
        </div>
      )}

      {/* Time distribution mini bar */}
      <div className="flex items-center gap-2 mb-3">
        <Clock className="w-3 h-3 text-white/30" />
        <div className="flex-1 flex items-end gap-1 h-6">
          {([['早', td.morning], ['午', td.afternoon], ['晚', td.evening], ['夜', td.night]] as [string, number][]).map(([label, val]) => (
            <div key={label} className="flex-1 flex flex-col items-center">
              <div className="w-full bg-amber-500/30 rounded-t" style={{ height: `${Math.max(2, (val / maxTd) * 24)}px` }} />
              <span className="text-[8px] text-white/30 mt-0.5">{label}</span>
            </div>
          ))}
        </div>
        <span className="text-[10px] text-white/40">峰值 {m.peak_hour}:00</span>
      </div>

      {/* Quick stats */}
      <div className="grid grid-cols-3 gap-2">
        {[
          { icon: BarChart3, label: '一致性', value: `${m.consistency_pct}%` },
          { icon: User, label: '领域数', value: m.active_domains },
          { icon: Clock, label: '均次掌握', value: `${m.avg_sessions_to_master}次` },
        ].map(({ icon: Icon, label, value }) => (
          <div key={label} className="bg-white/5 rounded-lg p-2 text-center">
            <Icon className="w-3 h-3 text-white/30 mx-auto mb-0.5" />
            <div className="text-xs font-bold text-white/80">{value}</div>
            <div className="text-[9px] text-white/30">{label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
