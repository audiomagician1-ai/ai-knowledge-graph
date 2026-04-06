import { useState, useCallback, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, X } from 'lucide-react';
import { useDomainStore } from '@/lib/store/domain';

interface SearchResult {
  conceptId: string;
  conceptName: string;
  domainId: string;
  domainName: string;
}

/**
 * Global concept search overlay — triggered by Ctrl+K.
 * Searches across all loaded domain seed graphs for concept names.
 */
export function ConceptSearch() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [selectedIdx, setSelectedIdx] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const domains = useDomainStore((s) => s.domains);

  // Global keyboard shortcut: Ctrl+K to open
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setOpen(true);
      }
      if (e.key === 'Escape' && open) {
        e.preventDefault();
        setOpen(false);
      }
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [open]);

  // Focus input when opened
  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 50);
      setQuery('');
      setResults([]);
      setSelectedIdx(0);
    }
  }, [open]);

  // Search through domain concepts (local data)
  const handleSearch = useCallback((q: string) => {
    setQuery(q);
    setSelectedIdx(0);
    if (q.length < 2) {
      setResults([]);
      return;
    }

    const lower = q.toLowerCase();
    const matched: SearchResult[] = [];

    // Search through available domain data
    for (const d of domains) {
      if (!d.id) continue;
      try {
        const key = `akg-graph:${d.id}`;
        const raw = localStorage.getItem(key);
        if (!raw) continue;
        const graph = JSON.parse(raw);
        const concepts = graph?.concepts || graph?.nodes || [];
        for (const c of concepts) {
          const name = c.name || c.label || '';
          const id = c.id || '';
          if (name.toLowerCase().includes(lower) || id.toLowerCase().includes(lower)) {
            matched.push({
              conceptId: id,
              conceptName: name,
              domainId: d.id,
              domainName: d.name,
            });
          }
          if (matched.length >= 20) break;
        }
      } catch { /* skip domains without cached data */ }
      if (matched.length >= 20) break;
    }

    setResults(matched);
  }, [domains]);

  const handleSelect = useCallback((result: SearchResult) => {
    setOpen(false);
    navigate(`/learn/${result.domainId}/${result.conceptId}`);
  }, [navigate]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIdx(prev => Math.min(prev + 1, results.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIdx(prev => Math.max(prev - 1, 0));
    } else if (e.key === 'Enter' && results[selectedIdx]) {
      handleSelect(results[selectedIdx]);
    }
  }, [results, selectedIdx, handleSelect]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-[100] flex items-start justify-center pt-[15vh] bg-black/50 backdrop-blur-sm"
      onClick={() => setOpen(false)}
      role="dialog"
      aria-label="搜索概念"
    >
      <div
        className="bg-[#1e293b] rounded-xl border border-white/10 shadow-2xl w-[90vw] max-w-lg mx-4 overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search input */}
        <div className="flex items-center gap-3 px-4 py-3 border-b border-white/10">
          <Search className="w-5 h-5 text-gray-400 flex-shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => handleSearch(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="搜索知识概念..."
            className="flex-1 bg-transparent text-white text-sm outline-none placeholder:text-gray-500"
            aria-label="搜索知识概念"
          />
          {query && (
            <button onClick={() => handleSearch('')} className="text-gray-400 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          )}
          <kbd className="hidden sm:block px-2 py-0.5 text-xs font-mono text-gray-500 bg-white/5 border border-white/10 rounded">
            Esc
          </kbd>
        </div>

        {/* Results */}
        <div className="max-h-[40vh] overflow-y-auto">
          {results.length === 0 && query.length >= 2 && (
            <div className="px-4 py-6 text-center text-sm text-gray-500">
              未找到匹配的概念
            </div>
          )}
          {results.length === 0 && query.length < 2 && (
            <div className="px-4 py-6 text-center text-sm text-gray-500">
              输入至少 2 个字符开始搜索
            </div>
          )}
          {results.map((r, i) => (
            <button
              key={`${r.domainId}-${r.conceptId}`}
              onClick={() => handleSelect(r)}
              className={`w-full text-left px-4 py-3 flex items-center justify-between transition-colors ${
                i === selectedIdx ? 'bg-white/10' : 'hover:bg-white/5'
              }`}
            >
              <div>
                <div className="text-sm text-white font-medium">{r.conceptName}</div>
                <div className="text-xs text-gray-400">{r.domainName}</div>
              </div>
              <span className="text-xs text-gray-500 ml-2 flex-shrink-0">
                Enter
              </span>
            </button>
          ))}
        </div>

        {/* Footer hint */}
        <div className="px-4 py-2 border-t border-white/10 flex items-center justify-between text-xs text-gray-500">
          <span>↑↓ 选择 · Enter 确认 · Esc 关闭</span>
          <span>Ctrl+K 打开搜索</span>
        </div>
      </div>
    </div>
  );
}
