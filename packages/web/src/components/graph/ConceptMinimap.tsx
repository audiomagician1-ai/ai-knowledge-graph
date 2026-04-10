import { useMemo } from 'react';
import { useGraphStore } from '@/lib/store/graph';
import { useLearningStore } from '@/lib/store/learning';

interface ConceptMinimapProps {
  conceptId: string;
  domainColor?: string;
  onConceptClick?: (conceptId: string) => void;
}

/**
 * A compact minimap showing all concepts in the same subdomain as the selected concept.
 * Concepts are rendered as small dots with color indicating mastery status.
 * The current concept is highlighted. Clicking a dot navigates to that concept.
 */
export function ConceptMinimap({ conceptId, domainColor = '#8b5cf6', onConceptClick }: ConceptMinimapProps) {
  const graphData = useGraphStore((s) => s.graphData);
  const progress = useLearningStore((s) => s.progress);

  const { siblings, currentIndex, subdomainName } = useMemo(() => {
    if (!graphData) return { siblings: [], currentIndex: -1, subdomainName: '' };

    const currentNode = graphData.nodes.find((n) => n.id === conceptId);
    if (!currentNode) return { siblings: [], currentIndex: -1, subdomainName: '' };

    const subdomain = currentNode.subdomain_id;
    const sameSubdomain = graphData.nodes
      .filter((n) => n.subdomain_id === subdomain)
      .sort((a, b) => a.difficulty - b.difficulty || a.label.localeCompare(b.label));

    return {
      siblings: sameSubdomain,
      currentIndex: sameSubdomain.findIndex((n) => n.id === conceptId),
      subdomainName: subdomain?.replace(/-/g, ' ') || '',
    };
  }, [graphData, conceptId]);

  if (siblings.length <= 1) return null;

  const getStatusColor = (id: string) => {
    const p = progress[id];
    if (p?.status === 'mastered') return '#22c55e';
    if (p?.status === 'learning') return '#f59e0b';
    return 'rgba(0,0,0,0.15)';
  };

  return (
    <div
      className="rounded-xl"
      style={{
        backgroundColor: 'var(--color-surface-1)',
        border: '1px solid rgba(0,0,0,0.08)',
        boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
        padding: '16px 20px',
      }}
    >
      <div className="flex items-center justify-between" style={{ marginBottom: 12 }}>
        <span
          className="text-xs font-bold uppercase tracking-wide"
          style={{ color: domainColor }}
        >
          {subdomainName}
        </span>
        <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
          {currentIndex + 1}/{siblings.length}
        </span>
      </div>

      {/* Dot grid */}
      <div className="flex flex-wrap gap-1.5">
        {siblings.map((node, i) => {
          const isCurrent = node.id === conceptId;
          const color = isCurrent ? domainColor : getStatusColor(node.id);
          return (
            <button
              key={node.id}
              onClick={() => onConceptClick?.(node.id)}
              title={`${node.label} (Lv.${node.difficulty})`}
              className="transition-all"
              style={{
                width: isCurrent ? 14 : 10,
                height: isCurrent ? 14 : 10,
                borderRadius: '50%',
                backgroundColor: color,
                border: isCurrent ? `2px solid ${domainColor}` : '1px solid rgba(0,0,0,0.06)',
                boxShadow: isCurrent ? `0 0 6px ${domainColor}40` : 'none',
                cursor: 'pointer',
                transform: isCurrent ? 'scale(1.2)' : 'scale(1)',
              }}
              aria-label={`${node.label}${isCurrent ? ' (当前)' : ''}`}
            />
          );
        })}
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 mt-3" style={{ fontSize: 10, color: 'var(--color-text-tertiary)' }}>
        <div className="flex items-center gap-1">
          <div style={{ width: 6, height: 6, borderRadius: '50%', backgroundColor: '#22c55e' }} />
          已掌握
        </div>
        <div className="flex items-center gap-1">
          <div style={{ width: 6, height: 6, borderRadius: '50%', backgroundColor: '#f59e0b' }} />
          学习中
        </div>
        <div className="flex items-center gap-1">
          <div style={{ width: 6, height: 6, borderRadius: '50%', backgroundColor: 'rgba(0,0,0,0.15)' }} />
          未开始
        </div>
      </div>
    </div>
  );
}