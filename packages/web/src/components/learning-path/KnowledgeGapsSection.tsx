import { useNavigate } from 'react-router-dom';
import { AlertTriangle } from 'lucide-react';

export interface KnowledgeGap {
  concept_id: string;
  name: string;
  blocked_count: number;
  difficulty: number;
  status: string;
}

interface KnowledgeGapsSectionProps {
  gaps: KnowledgeGap[];
  domainId?: string;
}

/**
 * Displays top knowledge gaps that block the most downstream concepts.
 */
export function KnowledgeGapsSection({ gaps, domainId }: KnowledgeGapsSectionProps) {
  const navigate = useNavigate();

  if (gaps.length === 0) return null;

  return (
    <section className="rounded-xl p-4" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <h3 className="text-sm font-semibold mb-2 flex items-center gap-2">
        <AlertTriangle size={14} style={{ color: '#f59e0b' }} />
        知识缺口
        <span className="text-xs opacity-50 font-normal">优先补齐这些概念可解锁更多内容</span>
      </h3>
      <div className="space-y-1.5">
        {gaps.map((gap) => (
          <button
            key={gap.concept_id}
            onClick={() => navigate(`/learn/${domainId}/${gap.concept_id}`)}
            className="w-full flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-white/5 transition-colors text-left"
            style={{ borderLeft: '3px solid #f59e0b' }}
          >
            <div className="flex-1 min-w-0">
              <span className="text-sm">{gap.name}</span>
              <span className="text-xs opacity-40 ml-2">难度 {gap.difficulty}</span>
            </div>
            <span className="text-xs px-1.5 py-0.5 rounded" style={{ backgroundColor: '#f59e0b20', color: '#f59e0b' }}>
              解锁 {gap.blocked_count} 个
            </span>
          </button>
        ))}
      </div>
    </section>
  );
}
