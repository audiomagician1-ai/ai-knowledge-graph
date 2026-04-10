/**
 * ApiExplorerPage — Interactive API catalog + try-it interface.
 * V4.6: Leverages /api/health/api-catalog to list all endpoints,
 *        grouped by tag with search/filter and inline try-it panels.
 */
import { useState, useEffect, useMemo } from 'react';
import { Search, ChevronDown, ChevronUp, Play, Loader2, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const API_BASE = import.meta.env.VITE_API_URL || '';

interface Endpoint {
  method: string;
  path: string;
  name: string;
  summary: string;
}
interface CatalogResponse {
  total_endpoints: number;
  total_tags: number;
  tags: Record<string, { count: number; endpoints: Endpoint[] }>;
}

export function ApiExplorerPage() {
  const navigate = useNavigate();
  const [catalog, setCatalog] = useState<CatalogResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [openTags, setOpenTags] = useState<Set<string>>(new Set());
  const [tryResult, setTryResult] = useState<{ path: string; data: unknown; ms: number } | null>(null);
  const [trying, setTrying] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/health/api-catalog`)
      .then(r => r.json())
      .then(d => { setCatalog(d); setOpenTags(new Set(Object.keys(d.tags || {}).slice(0, 3))); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const filtered = useMemo(() => {
    if (!catalog) return {};
    const q = search.toLowerCase();
    const result: Record<string, Endpoint[]> = {};
    for (const [tag, group] of Object.entries(catalog.tags)) {
      const eps = group.endpoints || [];
      const match = eps.filter(e => !q || e.path.toLowerCase().includes(q) || e.name.toLowerCase().includes(q) || (e.summary || '').toLowerCase().includes(q));
      if (match.length > 0) result[tag] = match;
    }
    return result;
  }, [catalog, search]);

  const toggleTag = (tag: string) => {
    setOpenTags(prev => { const n = new Set(prev); n.has(tag) ? n.delete(tag) : n.add(tag); return n; });
  };

  const tryEndpoint = async (ep: Endpoint) => {
    if (ep.method !== 'GET') return;
    const key = `${ep.method}:${ep.path}`;
    setTrying(key);
    const t0 = performance.now();
    try {
      const r = await fetch(`${API_BASE}${ep.path}`);
      const data = await r.json();
      setTryResult({ path: ep.path, data, ms: Math.round(performance.now() - t0) });
    } catch (e) {
      setTryResult({ path: ep.path, data: { error: String(e) }, ms: Math.round(performance.now() - t0) });
    } finally {
      setTrying(null);
    }
  };

  const methodColor: Record<string, string> = {
    GET: '#22c55e', POST: '#3b82f6', PUT: '#f59e0b', DELETE: '#ef4444', PATCH: '#a855f7',
  };
  const totalFiltered = Object.values(filtered).reduce((s, e) => s + e.length, 0);

  return (
    <div className="min-h-screen p-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <button onClick={() => navigate(-1)} className="p-1.5 rounded-lg hover:bg-white/5">
          <ArrowLeft size={18} className="opacity-50" />
        </button>
        <div>
          <h1 className="text-xl font-bold">API Explorer</h1>
          <p className="text-xs opacity-40">
            {catalog ? `${catalog.total_endpoints} endpoints` : 'Loading...'}
            {search && ` · ${totalFiltered} matched`}
          </p>
        </div>
      </div>

      {/* Search */}
      <div className="relative mb-6">
        <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 opacity-30" />
        <input
          type="text"
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search endpoints... (path, name, summary)"
          className="w-full pl-9 pr-4 py-2.5 rounded-xl text-sm"
          style={{ backgroundColor: 'var(--color-surface-1)', border: '1px solid rgba(255,255,255,0.06)' }}
        />
      </div>

      {loading && (
        <div className="text-center py-12 opacity-40">
          <Loader2 size={24} className="mx-auto mb-2 animate-spin" />
          <p className="text-sm">Loading API catalog...</p>
        </div>
      )}

      {/* Tag groups */}
      <div className="space-y-3">
        {Object.entries(filtered).map(([tag, endpoints]) => (
          <div key={tag} className="rounded-xl overflow-hidden" style={{ backgroundColor: 'var(--color-surface-1)' }}>
            <button
              onClick={() => toggleTag(tag)}
              className="w-full flex items-center gap-3 p-3 text-left hover:bg-white/5 transition-colors"
            >
              <span className="text-sm font-semibold flex-1">{tag}</span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-white/10">{endpoints.length}</span>
              {openTags.has(tag) ? <ChevronUp size={14} className="opacity-30" /> : <ChevronDown size={14} className="opacity-30" />}
            </button>
            {openTags.has(tag) && (
              <div className="border-t border-white/5">
                {endpoints.map((ep, i) => {
                  const key = `${ep.method}:${ep.path}`;
                  return (
                    <div key={i} className="flex items-center gap-3 px-4 py-2.5 border-b border-white/[0.03] last:border-0 hover:bg-white/[0.02]">
                      <span
                        className="text-[10px] font-bold px-1.5 py-0.5 rounded shrink-0"
                        style={{ backgroundColor: (methodColor[ep.method] || '#666') + '22', color: methodColor[ep.method] || '#999' }}
                      >
                        {ep.method}
                      </span>
                      <div className="flex-1 min-w-0">
                        <div className="text-xs font-mono truncate opacity-80">{ep.path}</div>
                        {ep.summary && <div className="text-[10px] opacity-40 truncate">{ep.summary}</div>}
                      </div>
                      {ep.method === 'GET' && !ep.path.includes('{') && (
                        <button
                          onClick={() => tryEndpoint(ep)}
                          disabled={trying === key}
                          className="shrink-0 px-2 py-1 rounded-lg text-[10px] font-medium flex items-center gap-1 transition-colors hover:bg-green-500/20"
                          style={{ color: '#22c55e' }}
                        >
                          {trying === key ? <Loader2 size={10} className="animate-spin" /> : <Play size={10} />}
                          Try
                        </button>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Try-it result panel */}
      {tryResult && (
        <div className="fixed bottom-4 right-4 left-4 md:left-auto md:w-[500px] max-h-[40vh] overflow-auto rounded-xl p-4 shadow-md z-50"
          style={{ backgroundColor: 'var(--color-surface-1)', border: '1px solid rgba(255,255,255,0.1)' }}>
          <div className="flex items-center justify-between mb-2">
            <div className="text-xs font-mono opacity-60">{tryResult.path}</div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] opacity-40">{tryResult.ms}ms</span>
              <button onClick={() => setTryResult(null)} className="text-xs opacity-40 hover:opacity-70">✕</button>
            </div>
          </div>
          <pre className="text-[10px] leading-relaxed overflow-auto max-h-[30vh] whitespace-pre-wrap opacity-70">
            {JSON.stringify(tryResult.data, null, 2).slice(0, 5000)}
          </pre>
        </div>
      )}
    </div>
  );
}