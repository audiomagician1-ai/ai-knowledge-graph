import { Compass, X, Star, ChevronRight, Loader } from 'lucide-react';
import type { GraphNode, GraphData } from '@akg/shared';

export interface Recommendation {
  concept_id: string;
  name: string;
  difficulty: number;
  estimated_minutes: number;
  is_milestone: boolean;
  score: number;
  reason: string;
  status: string;
}

interface GraphRecommendPanelProps {
  recommendations: Recommendation[];
  loading: boolean;
  chatOpen: boolean;
  graphData: GraphData | null;
  onNodeClick: (node: GraphNode) => void;
  onClose: () => void;
}

function difficultyLabel(d: number) {
  if (d <= 3) return { text: '入门', color: 'var(--color-accent-emerald)' };
  if (d <= 6) return { text: '进阶', color: 'var(--color-accent-primary)' };
  return { text: '高级', color: 'var(--color-accent-rose)' };
}

export function GraphRecommendPanel({ recommendations, loading, chatOpen, graphData, onNodeClick, onClose }: GraphRecommendPanelProps) {
  return (
    <div className="absolute pointer-events-auto animate-fade-in-scale transition-all duration-500 ease-out" style={{ width: 400, bottom: 100, zIndex: 25, ...(chatOpen ? { left: '25%', transform: 'translateX(-50%)' } : { left: '50%', transform: 'translateX(-50%)' }) }}>
      <div style={{
        borderRadius: 16, overflow: 'hidden', background: 'rgba(245,245,242,0.96)', backdropFilter: 'blur(20px)',
        border: '1px solid rgba(0,0,0,0.10)', boxShadow: '0 12px 48px rgba(0,0,0,0.1)',
      }}>
        <div className="flex items-center justify-between" style={{ padding: '18px 24px', borderBottom: '1px solid rgba(0,0,0,0.06)' }}>
          <div className="flex items-center gap-2">
            <Compass size={15} style={{ color: 'var(--color-accent-primary)' }} />
            <span className="text-sm font-semibold">推荐学习路径</span>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-full hover:bg-black/5" style={{ color: 'var(--color-text-tertiary)' }}><X size={14} /></button>
        </div>
        <div style={{ maxHeight: 320, overflowY: 'auto' }}>
          {loading ? (
            <div className="flex items-center justify-center py-8"><Loader size={18} className="animate-spin" style={{ color: 'var(--color-text-tertiary)' }} /></div>
          ) : recommendations.length === 0 ? (
            <p className="text-sm text-center py-8" style={{ color: 'var(--color-text-tertiary)' }}>暂无推荐</p>
          ) : recommendations.map((rec, idx) => {
            const diff = difficultyLabel(rec.difficulty);
            return (
              <button key={rec.concept_id} onClick={() => {
                const node = graphData?.nodes.find(n => n.id === rec.concept_id);
                if (node) { onNodeClick(node); onClose(); }
              }} className="w-full text-left flex items-start transition-colors"
                style={{ padding: '16px 24px', gap: 14, borderBottom: '1px solid rgba(0,0,0,0.04)' }}
                onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'rgba(0,0,0,0.03)')}
                onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}>
                <div className="shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                  style={{ backgroundColor: 'var(--color-accent-primary)', color: 'var(--color-text-on-accent)' }}>{idx + 1}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5 mb-0.5">
                    {rec.is_milestone && <Star size={11} fill="var(--color-accent-primary)" style={{ color: 'var(--color-accent-primary)' }} />}
                    <span className="text-sm font-medium truncate">{rec.name}</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                    <span style={{ color: diff.color }}>Lv.{rec.difficulty}</span>
                    <span>{rec.estimated_minutes}min</span>
                  </div>
                </div>
                <ChevronRight size={13} className="shrink-0 mt-1" style={{ color: 'var(--color-text-tertiary)' }} />
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}