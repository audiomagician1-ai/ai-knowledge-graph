/**
 * SubdomainFilter — Dropdown list of subdomains within the active domain.
 * Clicking a subdomain highlights those nodes; clicking again clears the filter.
 */
import { useMemo, useState, useRef, useEffect } from 'react';
import { Filter, ChevronDown, X, CheckCircle } from 'lucide-react';
import type { GraphNode } from '@akg/shared';

interface SubdomainFilterProps {
  nodes: GraphNode[];
  activeSubdomain: string | null;
  onSubdomainChange: (subdomain: string | null) => void;
  domainColor: string;
}

export function SubdomainFilter({ nodes, activeSubdomain, onSubdomainChange, domainColor }: SubdomainFilterProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  // Close on outside click
  useEffect(() => {
    if (!open) return;
    const handleClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [open]);

  // Compute subdomain stats
  const subdomains = useMemo(() => {
    const map = new Map<string, { total: number; mastered: number }>();
    for (const n of nodes) {
      const sub = n.subdomain_id || 'other';
      const entry = map.get(sub) || { total: 0, mastered: 0 };
      entry.total++;
      if (n.status === 'mastered') entry.mastered++;
      map.set(sub, entry);
    }
    return Array.from(map.entries())
      .map(([id, stats]) => ({ id, ...stats, pct: Math.round((stats.mastered / stats.total) * 100) }))
      .sort((a, b) => a.id.localeCompare(b.id));
  }, [nodes]);

  const activeLabel = activeSubdomain
    ? subdomains.find(s => s.id === activeSubdomain)?.id || activeSubdomain
    : null;

  return (
    <div ref={ref} className="absolute top-4 right-4 z-10 pointer-events-auto">
      {/* Toggle button */}
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 px-3 py-2 rounded-xl bg-white/90 dark:bg-gray-900/90 backdrop-blur-sm shadow-lg border border-gray-200/60 dark:border-gray-700/60 hover:bg-white dark:hover:bg-gray-800 transition-colors"
        aria-label="筛选子域"
      >
        <Filter size={14} style={{ color: activeSubdomain ? domainColor : '#9ca3af' }} />
        <span className="text-xs font-medium text-gray-700 dark:text-gray-200 max-w-[120px] truncate">
          {activeLabel || '筛选子域'}
        </span>
        {activeSubdomain ? (
          <button
            onClick={(e) => { e.stopPropagation(); onSubdomainChange(null); }}
            className="p-0.5 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700"
            aria-label="清除筛选"
          >
            <X size={12} className="text-gray-400" />
          </button>
        ) : (
          <ChevronDown size={12} className="text-gray-400" />
        )}
      </button>

      {/* Dropdown */}
      {open && (
        <div className="absolute top-full right-0 mt-2 w-56 bg-white/95 dark:bg-gray-900/95 backdrop-blur-sm rounded-xl shadow-xl border border-gray-200/60 dark:border-gray-700/60 overflow-hidden animate-fade-in">
          <div className="max-h-[300px] overflow-y-auto py-1">
            {/* "All" option */}
            <button
              onClick={() => { onSubdomainChange(null); setOpen(false); }}
              className={`w-full text-left flex items-center gap-2 px-3 py-2 text-xs transition-colors ${
                !activeSubdomain ? 'bg-gray-100 dark:bg-gray-800' : 'hover:bg-gray-50 dark:hover:bg-gray-800'
              }`}
            >
              <span className="font-medium text-gray-700 dark:text-gray-200">全部显示</span>
              <span className="ml-auto text-gray-400">{nodes.length}</span>
            </button>

            <div className="border-t border-gray-100 dark:border-gray-700 my-1" />

            {/* Subdomain items */}
            {subdomains.map(sub => (
              <button
                key={sub.id}
                onClick={() => { onSubdomainChange(sub.id === activeSubdomain ? null : sub.id); setOpen(false); }}
                className={`w-full text-left flex items-center gap-2 px-3 py-2 text-xs transition-colors ${
                  sub.id === activeSubdomain ? 'bg-gray-100 dark:bg-gray-800' : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                }`}
              >
                {/* Color dot */}
                <div
                  className="w-2 h-2 rounded-full flex-shrink-0"
                  style={{ backgroundColor: sub.id === activeSubdomain ? domainColor : '#d1d5db' }}
                />
                <span className="font-medium text-gray-700 dark:text-gray-200 truncate flex-1">{sub.id}</span>
                {/* Progress */}
                <div className="flex items-center gap-1.5 flex-shrink-0">
                  {sub.mastered > 0 && (
                    <span className="flex items-center gap-0.5 text-emerald-500">
                      <CheckCircle size={10} />
                      {sub.mastered}
                    </span>
                  )}
                  <span className="text-gray-400">{sub.total}</span>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
