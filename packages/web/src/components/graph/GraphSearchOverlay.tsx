import { useState, useMemo } from 'react';
import { Search, X, Star, ChevronRight } from 'lucide-react';
import type { GraphNode, GraphData } from '@akg/shared';

interface GraphSearchOverlayProps {
  graphData: GraphData | null;
  onNodeClick: (node: GraphNode) => void;
}

export function GraphSearchOverlay({ graphData, onNodeClick }: GraphSearchOverlayProps) {
  const [searchQuery, setSearchQuery] = useState('');

  const searchResults = useMemo(() => {
    if (!searchQuery.trim() || !graphData) return [];
    return graphData.nodes
      .filter((n) => n.label.toLowerCase().includes(searchQuery.toLowerCase()) || n.id.toLowerCase().includes(searchQuery.toLowerCase()))
      .slice(0, 8);
  }, [searchQuery, graphData]);

  return (
    <div className="absolute top-5 left-1/2 -translate-x-1/2 z-20 pointer-events-auto" style={{ width: 'min(420px, 90vw)' }}>
      <div className="relative">
        <div className="flex items-center gap-2" style={{
          height: 48, padding: '0 20px', borderRadius: 16, background: 'rgba(245,245,242,0.92)', backdropFilter: 'blur(16px)',
          border: '1px solid rgba(0,0,0,0.10)', boxShadow: '0 2px 16px rgba(0,0,0,0.06)',
        }}>
          <Search size={15} style={{ color: 'var(--color-text-tertiary)', flexShrink: 0 }} />
          <input type="text" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} placeholder="搜索知识节点..."
            className="flex-1 bg-transparent text-sm outline-none" style={{ color: 'var(--color-text-primary)', border: 'none' }} />
          {searchQuery && (
            <button onClick={() => setSearchQuery('')} className="shrink-0 p-1 rounded-full hover:bg-white/5">
              <X size={13} style={{ color: 'var(--color-text-tertiary)' }} />
            </button>
          )}
        </div>
        {searchResults.length > 0 && (
          <div className="absolute top-full left-0 right-0 animate-fade-in-scale" style={{
            marginTop: 8, borderRadius: 16, padding: 8, maxHeight: 320, overflowY: 'auto', background: 'rgba(245,245,242,0.96)', backdropFilter: 'blur(16px)',
            border: '1px solid rgba(0,0,0,0.10)', boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
          }}>
            {searchResults.map((node) => (
              <button key={node.id} onClick={() => { onNodeClick(node); setSearchQuery(''); }}
                className="w-full text-left flex items-center transition-colors"
                style={{ gap: 10, padding: '12px 16px', borderRadius: 10, fontSize: 14 }}
                onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'rgba(0,0,0,0.04)')}
                onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}>
                {node.is_milestone && <Star size={13} fill="var(--color-accent-primary)" style={{ color: 'var(--color-accent-primary)' }} />}
                <span className="flex-1 truncate" style={{ color: 'var(--color-text-primary)' }}>{node.label}</span>
                <ChevronRight size={13} style={{ color: 'var(--color-text-tertiary)' }} />
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}