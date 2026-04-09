import { Star, X, Clock, BookOpen, Zap, Trophy } from 'lucide-react';
import type { GraphNode } from '@akg/shared';

interface GraphConceptHeaderProps {
  node: GraphNode;
  progress: Record<string, { status: string }>;
  onClose: () => void;
}

function difficultyLabel(d: number) {
  if (d <= 3) return { text: '入门', color: 'var(--color-accent-emerald)' };
  if (d <= 6) return { text: '进阶', color: 'var(--color-accent-primary)' };
  return { text: '高级', color: 'var(--color-accent-rose)' };
}

export function GraphConceptHeader({ node, progress, onClose }: GraphConceptHeaderProps) {
  const diff = difficultyLabel(node.difficulty);
  const nodeProgress = progress[node.id];

  return (
    <div className="shrink-0 flex items-start justify-between" style={{ padding: '24px 28px', gap: 16, backgroundColor: 'var(--color-surface-1)', borderBottom: '1px solid var(--color-border-subtle)' }}>
      <div className="flex-1 min-w-0">
        <div className="flex items-center" style={{ gap: 10, marginBottom: 10 }}>
          {node.is_milestone && <Star size={16} fill="var(--color-accent-primary)" style={{ color: 'var(--color-accent-primary)' }} />}
          <h3 className="font-bold truncate" style={{ fontSize: 18 }}>{node.label}</h3>
        </div>
        <div className="flex items-center flex-wrap" style={{ gap: 14 }}>
          <span className="inline-flex items-center gap-1.5 rounded-lg px-3 py-1 text-sm font-medium" style={{ backgroundColor: diff.color + '14', color: diff.color }}>
            Lv.{node.difficulty} {diff.text}
          </span>
          {node.estimated_minutes && (
            <span className="inline-flex items-center gap-1.5 text-sm" style={{ color: 'var(--color-text-tertiary)' }}><Clock size={13} /> {node.estimated_minutes}min</span>
          )}
          {nodeProgress?.status === 'mastered' ? (
            <span className="inline-flex items-center gap-1.5 text-sm font-semibold" style={{ color: 'var(--color-accent-emerald)' }}><Trophy size={13} /> 已掌握</span>
          ) : nodeProgress?.status === 'learning' ? (
            <span className="inline-flex items-center gap-1.5 text-sm font-semibold" style={{ color: 'var(--color-accent-primary)' }}><BookOpen size={13} /> 学习中</span>
          ) : node.is_recommended ? (
            <span className="inline-flex items-center gap-1.5 text-sm font-semibold" style={{ color: 'var(--color-accent-cyan)' }}><Zap size={13} /> 推荐</span>
          ) : null}
        </div>
      </div>
      <button onClick={onClose}
        className="shrink-0 w-9 h-9 flex items-center justify-center rounded-full transition-colors"
        style={{ color: 'var(--color-text-tertiary)' }}
        onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'rgba(0,0,0,0.06)')}
        onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}>
        <X size={16} />
      </button>
    </div>
  );
}