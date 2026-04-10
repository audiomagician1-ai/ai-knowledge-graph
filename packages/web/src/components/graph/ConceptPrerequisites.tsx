import { useMemo } from 'react';
import { useGraphStore } from '@/lib/store/graph';
import { useLearningStore } from '@/lib/store/learning';
import { ArrowLeft, ArrowRight, Check, BookOpen, Lock } from 'lucide-react';

interface ConceptPrerequisitesProps {
  conceptId: string;
  onConceptClick?: (conceptId: string) => void;
}

/**
 * Shows prerequisite and dependent concepts for a given node,
 * using the graph edges from the store. Renders in a compact card layout.
 */
export function ConceptPrerequisites({ conceptId, onConceptClick }: ConceptPrerequisitesProps) {
  const graphData = useGraphStore((s) => s.graphData);
  const progress = useLearningStore((s) => s.progress);

  const { prerequisites, dependents } = useMemo(() => {
    if (!graphData) return { prerequisites: [], dependents: [] };

    const nodeMap = new Map(graphData.nodes.map((n) => [n.id, n]));

    // Prerequisites: edges where target = conceptId, relation = prerequisite
    // meaning source is a prerequisite OF conceptId
    const prereqs = graphData.edges
      .filter((e) => e.target === conceptId && e.relation_type === 'prerequisite')
      .map((e) => nodeMap.get(e.source))
      .filter(Boolean)
      .sort((a, b) => (a!.difficulty || 0) - (b!.difficulty || 0));

    // Dependents: edges where source = conceptId, relation = prerequisite
    // meaning conceptId is a prerequisite FOR target
    const deps = graphData.edges
      .filter((e) => e.source === conceptId && e.relation_type === 'prerequisite')
      .map((e) => nodeMap.get(e.target))
      .filter(Boolean)
      .sort((a, b) => (a!.difficulty || 0) - (b!.difficulty || 0));

    return { prerequisites: prereqs, dependents: deps };
  }, [graphData, conceptId]);

  if (prerequisites.length === 0 && dependents.length === 0) return null;

  const getStatusIcon = (id: string) => {
    const p = progress[id];
    if (p?.status === 'mastered') return <Check size={12} style={{ color: 'var(--color-accent-emerald)' }} />;
    if (p?.status === 'learning') return <BookOpen size={12} style={{ color: 'var(--color-accent-amber)' }} />;
    return <Lock size={12} style={{ color: 'var(--color-text-tertiary)' }} />;
  };

  const getStatusColor = (id: string) => {
    const p = progress[id];
    if (p?.status === 'mastered') return 'var(--color-accent-emerald)';
    if (p?.status === 'learning') return 'var(--color-accent-amber)';
    return 'var(--color-text-tertiary)';
  };

  const allPrereqsMastered = prerequisites.every(
    (n) => progress[n!.id]?.status === 'mastered'
  );

  return (
    <div
      className="rounded-xl"
      style={{
        backgroundColor: 'var(--color-surface-1)',
        border: '1px solid rgba(0,0,0,0.08)',
        boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
        padding: '20px 24px',
      }}
    >
      {/* Prerequisites section */}
      {prerequisites.length > 0 && (
        <div style={{ marginBottom: dependents.length > 0 ? 16 : 0 }}>
          <div className="flex items-center gap-2" style={{ marginBottom: 12 }}>
            <ArrowLeft size={14} style={{ color: 'var(--color-accent-primary)' }} />
            <span className="text-sm font-bold" style={{ color: 'var(--color-text-secondary)' }}>
              前置知识
            </span>
            {allPrereqsMastered && prerequisites.length > 0 && (
              <span
                className="text-xs px-2 py-0.5 rounded-full"
                style={{ backgroundColor: 'rgba(16,185,129,0.1)', color: 'var(--color-accent-emerald)' }}
              >
                全部掌握 ✓
              </span>
            )}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {prerequisites.map((node) => (
              <button
                key={node!.id}
                onClick={() => onConceptClick?.(node!.id)}
                className="flex items-center gap-3 rounded-lg transition-all text-left"
                style={{
                  padding: '10px 14px',
                  backgroundColor: '#f5f5f3',
                  border: '1px solid transparent',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#eeeeec';
                  e.currentTarget.style.borderColor = 'rgba(0,0,0,0.1)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#f5f5f3';
                  e.currentTarget.style.borderColor = 'transparent';
                }}
              >
                {getStatusIcon(node!.id)}
                <span
                  className="text-sm flex-1 truncate"
                  style={{ color: 'var(--color-text-primary)' }}
                >
                  {node!.label}
                </span>
                <span
                  className="text-xs"
                  style={{ color: getStatusColor(node!.id) }}
                >
                  Lv.{node!.difficulty}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Dependents section */}
      {dependents.length > 0 && (
        <div>
          {prerequisites.length > 0 && (
            <div style={{ borderTop: '1px solid rgba(0,0,0,0.06)', marginBottom: 12, paddingTop: 16 }} />
          )}
          <div className="flex items-center gap-2" style={{ marginBottom: 12 }}>
            <ArrowRight size={14} style={{ color: 'var(--color-accent-cyan, #06b6d4)' }} />
            <span className="text-sm font-bold" style={{ color: 'var(--color-text-secondary)' }}>
              后续解锁
            </span>
            <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
              ({dependents.length})
            </span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {dependents.slice(0, 5).map((node) => (
              <button
                key={node!.id}
                onClick={() => onConceptClick?.(node!.id)}
                className="flex items-center gap-3 rounded-lg transition-all text-left"
                style={{
                  padding: '10px 14px',
                  backgroundColor: '#f5f5f3',
                  border: '1px solid transparent',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#eeeeec';
                  e.currentTarget.style.borderColor = 'rgba(0,0,0,0.1)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#f5f5f3';
                  e.currentTarget.style.borderColor = 'transparent';
                }}
              >
                {getStatusIcon(node!.id)}
                <span
                  className="text-sm flex-1 truncate"
                  style={{ color: 'var(--color-text-primary)' }}
                >
                  {node!.label}
                </span>
                <span
                  className="text-xs"
                  style={{ color: getStatusColor(node!.id) }}
                >
                  Lv.{node!.difficulty}
                </span>
              </button>
            ))}
            {dependents.length > 5 && (
              <div className="text-center text-xs py-2" style={{ color: 'var(--color-text-tertiary)' }}>
                还有 {dependents.length - 5} 个后续概念
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}