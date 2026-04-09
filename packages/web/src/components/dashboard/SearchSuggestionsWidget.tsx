import { useState, useCallback } from 'react';
import { Search, Sparkles } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface Suggestion {
  concept_id: string;
  name: string;
  domain_id: string;
  domain_name: string;
  difficulty: number;
  relevance: number;
}

const API = import.meta.env.VITE_API_URL || '';

export default function SearchSuggestionsWidget() {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const fetchSuggestions = useCallback(async (q: string) => {
    if (q.length < 2) { setSuggestions([]); return; }
    setLoading(true);
    try {
      const resp = await fetch(`${API}/api/analytics/search-suggestions?q=${encodeURIComponent(q)}&limit=6`);
      const data = await resp.json();
      setSuggestions(data.suggestions || []);
    } catch { setSuggestions([]); }
    finally { setLoading(false); }
  }, []);

  const handleInput = (val: string) => {
    setQuery(val);
    // Simple debounce via setTimeout
    const id = setTimeout(() => fetchSuggestions(val), 250);
    return () => clearTimeout(id);
  };

  const diffColor = (d: number) =>
    d <= 3 ? 'text-emerald-400' : d <= 6 ? 'text-yellow-400' : 'text-red-400';

  return (
    <div className="bg-white/5 rounded-xl p-4 border border-white/10">
      <div className="flex items-center gap-2 mb-3">
        <Sparkles className="w-4 h-4 text-amber-400" />
        <h3 className="text-sm font-semibold text-white/90">Smart Search</h3>
      </div>

      <div className="relative">
        <Search className="absolute left-2.5 top-2 w-3.5 h-3.5 text-white/30" />
        <input
          value={query}
          onChange={e => handleInput(e.target.value)}
          placeholder="Search concepts (fuzzy)..."
          className="w-full pl-8 pr-3 py-1.5 bg-white/5 border border-white/10 rounded-lg text-xs text-white/80 placeholder:text-white/30 focus:outline-none focus:border-cyan-500/50"
        />
      </div>

      {loading && <div className="mt-2 text-[10px] text-white/30 animate-pulse">Searching...</div>}

      {suggestions.length > 0 && (
        <div className="mt-2 space-y-1">
          {suggestions.map(s => (
            <button
              key={s.concept_id}
              onClick={() => navigate(`/graph/${s.domain_id}?concept=${s.concept_id}`)}
              className="w-full flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-white/5 transition-colors text-left"
            >
              <div className="flex-1 min-w-0">
                <div className="text-xs text-white/80 truncate">{s.name}</div>
                <div className="text-[10px] text-white/40 truncate">{s.domain_name}</div>
              </div>
              <span className={`text-[10px] font-mono ${diffColor(s.difficulty)}`}>
                D{s.difficulty}
              </span>
            </button>
          ))}
        </div>
      )}

      {query.length >= 2 && !loading && suggestions.length === 0 && (
        <div className="mt-2 text-[10px] text-white/30 text-center py-2">No matches found</div>
      )}
    </div>
  );
}
