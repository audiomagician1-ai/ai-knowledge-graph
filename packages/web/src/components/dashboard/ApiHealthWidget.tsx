/**
 * ApiHealthWidget — Shows API health summary: endpoint count, latency, errors.
 * V4.1: Provides at-a-glance system health for the Dashboard.
 */
import { useState, useEffect } from 'react';
import { Activity, AlertTriangle, Clock, Server } from 'lucide-react';

interface LatencyReport {
  uptime_seconds: number;
  total_requests: number;
  global_error_rate: string;
  global_avg_ms: number;
  slowest_endpoints: { path: string; avg_ms: number; requests: number; error_rate: string }[];
  high_error_endpoints: { path: string; error_rate: string; requests: number }[];
  total_tracked: number;
}

interface CatalogSummary {
  total_endpoints: number;
  total_tags: number;
}

export function ApiHealthWidget() {
  const [latency, setLatency] = useState<LatencyReport | null>(null);
  const [catalog, setCatalog] = useState<CatalogSummary | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const base = import.meta.env.VITE_API_URL || '';
    Promise.all([
      fetch(`${base}/api/health/latency-report`).then(r => r.json()),
      fetch(`${base}/api/health/api-catalog`).then(r => r.json()),
    ]).then(([lat, cat]) => {
      setLatency(lat);
      setCatalog(cat);
    }).catch(() => setError('无法加载 API 健康数据'));
  }, []);

  if (error) return <div className="text-xs text-red-400 p-3">{error}</div>;
  if (!latency || !catalog) return <div className="animate-pulse h-24 rounded-xl bg-white/5" />;

  const upH = Math.floor(latency.uptime_seconds / 3600);
  const upM = Math.floor((latency.uptime_seconds % 3600) / 60);

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4 space-y-3">
      <div className="flex items-center gap-2">
        <Server size={16} className="text-green-400" />
        <h3 className="text-sm font-semibold">API 系统健康</h3>
        <span className="ml-auto text-[10px] opacity-30">运行 {upH}h {upM}m</span>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-4 gap-3 text-center">
        <div>
          <div className="text-lg font-bold">{catalog.total_endpoints}</div>
          <div className="text-[10px] opacity-40">端点总数</div>
        </div>
        <div>
          <div className="text-lg font-bold">{latency.total_requests}</div>
          <div className="text-[10px] opacity-40">请求总数</div>
        </div>
        <div>
          <div className="text-lg font-bold">{latency.global_avg_ms}ms</div>
          <div className="text-[10px] opacity-40">平均延迟</div>
        </div>
        <div>
          <div className={`text-lg font-bold ${parseFloat(latency.global_error_rate) > 5 ? 'text-red-400' : 'text-green-400'}`}>
            {latency.global_error_rate}
          </div>
          <div className="text-[10px] opacity-40">错误率</div>
        </div>
      </div>

      {/* Slowest endpoints */}
      {latency.slowest_endpoints.length > 0 && (
        <div className="space-y-1">
          <div className="flex items-center gap-1 text-[10px] opacity-40 uppercase tracking-wider">
            <Clock size={10} /> 最慢端点
          </div>
          {latency.slowest_endpoints.slice(0, 3).map(ep => (
            <div key={ep.path} className="flex items-center justify-between text-xs py-0.5">
              <span className="truncate opacity-60 max-w-[60%]">{ep.path.replace('/api/', '')}</span>
              <span className="tabular-nums">{ep.avg_ms}ms <span className="opacity-30">({ep.requests})</span></span>
            </div>
          ))}
        </div>
      )}

      {/* Error alerts */}
      {latency.high_error_endpoints.length > 0 && (
        <div className="space-y-1">
          <div className="flex items-center gap-1 text-[10px] text-red-400/60 uppercase tracking-wider">
            <AlertTriangle size={10} /> 高错误率
          </div>
          {latency.high_error_endpoints.slice(0, 2).map(ep => (
            <div key={ep.path} className="flex items-center justify-between text-xs text-red-400/80 py-0.5">
              <span className="truncate max-w-[60%]">{ep.path.replace('/api/', '')}</span>
              <span className="tabular-nums">{ep.error_rate}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
