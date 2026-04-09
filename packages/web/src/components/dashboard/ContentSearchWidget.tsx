import { useState, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, FileText, ArrowRight } from 'lucide-react';

interface ContentResult {
  concept_id: string;
  name: string;
  domain_id: string;
  domain_name: string;
  subdomain: string;
  score: number;
  snippet: string;
  name_match: boolean;
}

/**
 * Content Search Widget — searches RAG document contents, not just concept names.
 * Powered by GET /api/analytics/content-search.
 */
export function ContentSearchWidget() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<ContentResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const navigate = useNavigate();

  const doSearch = useCallback(async (q: string) => {
    if (q.length < 2) {
      setResults([]);
      setSearched(false);
      return;
    }
    setLoading(true);
    setSearched(true);
    try {
      const settings = localStorage.getItem('akg-settings');
      const baseUrl = settings ? JSON.parse(settings)?.apiBaseUrl : '';
      if (!baseUrl) return;
      const resp = await fetch(`${baseUrl}/api/analytics/content-search?q=${encodeURIComponent(q)}&limit=8`);
      if (resp.ok) {
        const data = await resp.json();
        setResults(data.results || []);
      }
    } catch { /* silent */ } finally {
      setLoading(false);
    }
  }, []);

  const handleInput = useCallback((val: string) => {
    setQuery(val);
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => doSearch(val), 400);
  }, [doSearch]);

  return (
    <div className="bg-white/5 rounded-xl border border-white/10 p-4">
      <div className="flex items-center gap-2 mb-3">
        <FileText className="w-4 h-4 text-cyan-400" />
        <h3 className="text-sm font-medium text-white">知识内容搜索</h3>
      </div>

      {/* Search input */}
      <div className="flex items-center gap-2 bg-white/5 rounded-lg px-3 py-2 mb-3">
        <Search className="w-4 h-4 text-gray-500 flex-shrink-0" />
        <input
          type="text"
          value={query}
          onChange={(e) => handleInput(e.target.value)}
          placeholder="搜索知识文档内容..."
          className="flex-1 bg-transparent text-sm text-white outline-none placeholder:text-gray-500"
        />
      </div>

      {/* Results */}
      <div className="space-y-2 max-h-64 overflow-y-auto">
        {loading && (
          <div className="text-center py-3">
            <div className="w-5 h-5 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto" />
          </div>
        )}
        {!loading && searched && results.length === 0 && (
          <p className="text-xs text-gray-500 text-center py-2">未找到匹配内容</p>
        )}
        {!loading && results.map((r) => (
          <button
            key={`${r.domain_id}-${r.concept_id}`}
            onClick={() => navigate(`/learn/${r.domain_id}/${r.concept_id}`)}
            className="w-full text-left bg-white/5 hover:bg-white/10 rounded-lg p-3 transition-colors group"
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm text-white font-medium">{r.name}</span>
              <ArrowRight className="w-3.5 h-3.5 text-gray-500 group-hover:text-cyan-400 transition-colors" />
            </div>
            <div className="text-xs text-gray-400 mb-1">{r.domain_name} · {r.subdomain}</div>
            {r.snippet && (
              <p className="text-xs text-gray-500 line-clamp-2">{r.snippet}</p>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
