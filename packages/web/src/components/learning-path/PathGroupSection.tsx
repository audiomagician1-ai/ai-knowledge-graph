import { useNavigate } from 'react-router-dom';
import {
  CheckCircle2, BookOpen, Lock, Target, Sparkles, Zap, ChevronRight,
} from 'lucide-react';

interface PathConcept {
  id: string;
  label: string;
  isMilestone: boolean;
  status: string;
  mastery: number;
}

interface PathGroup {
  name: string;
  concepts: PathConcept[];
}

interface PathGroupSectionProps {
  group: PathGroup;
  isExpanded: boolean;
  domainId?: string;
  domainColor?: string;
  nextRecommended: string | null;
  onToggle: () => void;
}

export type { PathConcept, PathGroup };

/**
 * A collapsible section showing a group of concepts in the learning path.
 */
export function PathGroupSection({ group, isExpanded, domainId, domainColor, nextRecommended, onToggle }: PathGroupSectionProps) {
  const navigate = useNavigate();
  const groupMastered = group.concepts.filter((c) => c.status === 'mastered').length;

  return (
    <section className="rounded-xl overflow-hidden" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between px-5 py-3 hover:bg-white/5 transition-colors"
      >
        <div className="flex items-center gap-2">
          <span className="font-medium">{group.name}</span>
          <span className="text-xs px-2 py-0.5 rounded-full" style={{ backgroundColor: 'var(--color-surface-3)' }}>
            {groupMastered}/{group.concepts.length}
          </span>
        </div>
        <ChevronRight
          size={16}
          style={{ transition: 'transform 0.2s', transform: isExpanded ? 'rotate(90deg)' : 'rotate(0)' }}
        />
      </button>

      {isExpanded && (
        <div className="px-5 pb-4 space-y-1">
          {group.concepts.map((concept, idx) => (
            <PathConceptRow
              key={concept.id}
              concept={concept}
              idx={idx}
              prevStatus={idx > 0 ? group.concepts[idx - 1].status : undefined}
              domainId={domainId}
              domainColor={domainColor}
              isNext={concept.id === nextRecommended}
              onNavigate={(id) => navigate(`/learn/${domainId}/${id}`)}
            />
          ))}
        </div>
      )}
    </section>
  );
}

interface PathConceptRowProps {
  concept: PathConcept;
  idx: number;
  prevStatus?: string;
  domainId?: string;
  domainColor?: string;
  isNext: boolean;
  onNavigate: (id: string) => void;
}

/**
 * A single concept row in the learning path.
 */
function PathConceptRow({ concept, idx, prevStatus, domainColor, isNext, onNavigate }: PathConceptRowProps) {
  const color = domainColor || '#3b82f6';

  return (
    <button
      onClick={() => onNavigate(concept.id)}
      className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/5 transition-colors text-left"
      style={{ border: isNext ? `1px solid ${color}` : '1px solid transparent' }}
    >
      {/* Status icon */}
      <div className="shrink-0">
        {concept.status === 'mastered' ? (
          <CheckCircle2 size={18} style={{ color: '#22c55e' }} />
        ) : concept.status === 'learning' ? (
          <BookOpen size={18} style={{ color: '#3b82f6' }} />
        ) : idx > 0 && prevStatus === 'not_started' ? (
          <Lock size={18} style={{ color: 'var(--color-text-tertiary)' }} />
        ) : (
          <Target size={18} style={{ color: 'var(--color-text-tertiary)' }} />
        )}
      </div>

      {/* Concept info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className={`text-sm ${concept.status === 'mastered' ? 'line-through opacity-50' : ''}`}>
            {concept.label}
          </span>
          {concept.isMilestone && <Sparkles size={12} style={{ color: '#f59e0b' }} />}
          {isNext && (
            <span className="text-[10px] px-1.5 py-0.5 rounded" style={{ backgroundColor: `${color}20`, color }}>
              推荐
            </span>
          )}
        </div>
        {concept.mastery > 0 && (
          <div className="flex items-center gap-2 mt-0.5">
            <div className="flex-1 h-1 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--color-surface-3)', maxWidth: 80 }}>
              <div
                className="h-full rounded-full"
                style={{ width: `${concept.mastery}%`, backgroundColor: concept.mastery >= 75 ? '#22c55e' : '#3b82f6' }}
              />
            </div>
            <span className="text-[10px] opacity-40">{concept.mastery}分</span>
          </div>
        )}
      </div>

      {/* Arrow */}
      {concept.status !== 'mastered' && <Zap size={14} style={{ color: 'var(--color-text-tertiary)' }} />}
    </button>
  );
}
