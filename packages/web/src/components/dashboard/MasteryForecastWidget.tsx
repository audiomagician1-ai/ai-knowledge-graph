/**
 * MasteryForecastWidget — Predicted domain mastery completion timeline.
 * V3.2: Backend-powered via /api/analytics/mastery-forecast/{domain_id}.
 */
import { useState, useEffect } from 'react';
import { useDomainStore } from '@/lib/store/domain';
import { Calendar, TrendingUp, Clock } from 'lucide-react';
import { fetchWithRetry } from '@/lib/utils/fetch-retry';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

interface SubForecast { subdomain_id: string; remaining: number; estimated_hours: number; estimated_days: number }

interface ForecastData {
  domain_id: string;
  domain_name: string;
  total_concepts: number;
  mastered: number;
  remaining: number;
  completion_pct: number;
  estimated_days: number;
  estimated_hours: number;
  confidence: string;
  subdomain_forecast: SubForecast[];
}

const CONF_COLORS: Record<string, string> = { high: '#22c55e', medium: '#f59e0b', low: '#ef4444' };
const CONF_LABELS: Record<string, string> = { high: '高', medium: '中', low: '低' };

export function MasteryForecastWidget() {
  const activeDomain = useDomainStore((s) => s.activeDomain);
  const [data, setData] = useState<ForecastData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!activeDomain) return;
    setLoading(true);
    fetchWithRetry(`${API_BASE}/analytics/mastery-forecast/${activeDomain}`, { retries: 1 })
      .then((r) => r.ok ? r.json() : null)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [activeDomain]);

  if (loading) {
    return (
      <div className="rounded-xl p-4" style={{ backgroundColor: 'var(--color-surface-1)' }}>
        <h3 className="text-sm font-semibold flex items-center gap-2 mb-2">
          <Calendar size={16} style={{ color: 'var(--color-accent)' }} /> 掌握预测
        </h3>
        <div className="animate-pulse h-16 rounded-lg" style={{ backgroundColor: 'var(--color-surface-2)' }} />
      </div>
    );
  }

  if (!data || data.remaining === 0) return null;

  const confColor = CONF_COLORS[data.confidence] || '#888';

  return (
    <div className="rounded-xl p-4" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <h3 className="text-sm font-semibold flex items-center gap-2 mb-3">
        <Calendar size={16} style={{ color: 'var(--color-accent)' }} />
        掌握预测
        <span className="text-[10px] font-normal ml-auto px-1.5 py-0.5 rounded" style={{ backgroundColor: `${confColor}20`, color: confColor }}>
          置信度: {CONF_LABELS[data.confidence] || data.confidence}
        </span>
      </h3>

      {/* Progress */}
      <div className="mb-3">
        <div className="flex justify-between text-xs mb-1">
          <span className="opacity-60">{data.mastered}/{data.total_concepts} 已掌握</span>
          <span className="font-mono">{data.completion_pct}%</span>
        </div>
        <div className="h-2 rounded-full" style={{ backgroundColor: 'var(--color-surface-2)' }}>
          <div className="h-full rounded-full transition-all" style={{ width: `${data.completion_pct}%`, backgroundColor: 'var(--color-accent)' }} />
        </div>
      </div>

      {/* Forecast */}
      <div className="grid grid-cols-2 gap-2 mb-3">
        <div className="flex items-center gap-1.5 text-xs">
          <TrendingUp size={12} className="text-blue-400" />
          <span className="opacity-60">预计 <strong>{data.estimated_days}</strong> 天</span>
        </div>
        <div className="flex items-center gap-1.5 text-xs">
          <Clock size={12} className="text-purple-400" />
          <span className="opacity-60">约 <strong>{data.estimated_hours}</strong> 小时</span>
        </div>
      </div>

      {/* Top subdomains */}
      {data.subdomain_forecast.length > 0 && (
        <div className="space-y-1">
          {data.subdomain_forecast.slice(0, 4).map((sf) => (
            <div key={sf.subdomain_id} className="flex items-center gap-2 text-[10px] opacity-50">
              <span className="flex-1 truncate">{sf.subdomain_id}</span>
              <span className="font-mono">{sf.remaining}剩余 · {sf.estimated_days}天</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
