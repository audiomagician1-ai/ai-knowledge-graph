import { useDomainStore } from '@/lib/store/domain';
import { peekDomainProgress } from '@/lib/store/learning';
import { ArrowRight, Zap, BookOpen } from 'lucide-react';
import type { Domain } from '@akg/shared';
import type { ConceptProgress } from '@/lib/store/learning';

/** Format epoch ms as relative time (e.g., "3分钟前", "2天前") */
export function formatTimeAgo(epochMs: number): string {
  const diff = Date.now() - epochMs;
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return '刚刚';
  if (minutes < 60) return `${minutes}分钟前`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}小时前`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days}天前`;
  return `${Math.floor(days / 30)}个月前`;
}

/** Compact domain card for the right panel */
export function OtherDomainCard({ domain, onClick }: { domain: Domain; onClick: () => void }) {
  const conceptCount = domain.stats?.total_concepts ?? domain.concept_count ?? 0;
  const progress = peekDomainProgress(domain.id);
  const pct = conceptCount > 0 ? Math.round((progress.mastered / conceptCount) * 100) : 0;
  const accessHistory = useDomainStore((s) => s.accessHistory);
  const lastAccess = accessHistory[domain.id];
  const timeAgo = lastAccess ? formatTimeAgo(lastAccess) : null;

  return (
    <button
      onClick={onClick}
      className="w-full text-left rounded-lg transition-all"
      style={{ padding: '10px 12px', backgroundColor: 'var(--color-surface-2)', border: '1px solid var(--color-border)', cursor: 'pointer' }}
      onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = 'var(--color-surface-3)'; }}
      onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'var(--color-surface-2)'; }}
    >
      <div className="flex items-center gap-2.5">
        <span className="flex items-center justify-center shrink-0 rounded-md text-base"
          style={{ width: 30, height: 30, backgroundColor: `${domain.color}15` }}>
          {domain.icon}
        </span>
        <div className="flex-1 min-w-0">
          <div className="truncate" style={{ fontSize: 13, fontWeight: 600, color: 'var(--color-text-primary)' }}>{domain.name}</div>
          <div className="flex items-center gap-2 mt-0.5">
            <span style={{ fontSize: 10, color: 'var(--color-text-tertiary)' }}>{conceptCount} 概念</span>
            {progress.mastered > 0 && <span style={{ fontSize: 10, color: 'var(--color-accent-emerald)' }}>{progress.mastered} ✓</span>}
          </div>
        </div>
      </div>
      {conceptCount > 0 && (
        <div className="mt-2 flex items-center gap-2">
          <div className="flex-1 rounded-full overflow-hidden" style={{ height: 3, backgroundColor: 'var(--color-surface-4)' }}>
            <div style={{ height: '100%', borderRadius: 999, width: `${pct}%`, backgroundColor: domain.color, minWidth: pct > 0 ? 2 : 0, transition: 'width 0.4s ease' }} />
          </div>
          <span style={{ fontSize: 10, color: 'var(--color-text-tertiary)', minWidth: 22, textAlign: 'right' }} className="font-mono">{pct}%</span>
        </div>
      )}
      {timeAgo && <div style={{ fontSize: 10, color: 'var(--color-text-tertiary)', marginTop: 4 }}>{timeAgo}</div>}
    </button>
  );
}

/** Activity row for the recent-learning list */
export function ActivityRow({ item, nameMap, onNavigate }: { item: ConceptProgress; nameMap: Record<string, string>; onNavigate?: (conceptId: string) => void }) {
  const time = new Date(item.last_learn_at);
  const timeStr = `${time.getMonth() + 1}/${time.getDate()} ${String(time.getHours()).padStart(2, '0')}:${String(time.getMinutes()).padStart(2, '0')}`;
  const isMastered = item.status === 'mastered';
  const hasScore = (item.mastery_score || 0) > 0;
  const scoreColor = hasScore
    ? (item.mastery_score >= 80 ? 'var(--color-accent-emerald)' : item.mastery_score >= 60 ? 'var(--color-accent-primary)' : 'var(--color-accent-rose)')
    : 'var(--color-text-tertiary)';
  const displayName = nameMap[item.concept_id] || item.concept_id.replace(/-/g, ' ');
  const clickable = !!onNavigate;

  return (
    <button
      onClick={() => onNavigate?.(item.concept_id)}
      disabled={!clickable}
      className="w-full flex items-center transition-all group"
      style={{ gap: 10, borderRadius: 8, padding: '8px 12px', backgroundColor: 'transparent', border: 'none', cursor: clickable ? 'pointer' : 'default', textAlign: 'left' }}
      onMouseEnter={(e) => { if (clickable) e.currentTarget.style.backgroundColor = 'rgba(0,0,0,0.04)'; }}
      onMouseLeave={(e) => { if (clickable) e.currentTarget.style.backgroundColor = 'transparent'; }}
    >
      <div className="flex items-center justify-center shrink-0"
        style={{ width: 28, height: 28, borderRadius: 7, backgroundColor: isMastered ? 'rgba(16,185,129,0.1)' : 'rgba(245,158,11,0.1)', color: isMastered ? 'var(--color-accent-emerald)' : 'var(--color-accent-amber)' }}>
        {isMastered ? <Zap size={12} /> : <BookOpen size={12} />}
      </div>
      <div className="flex-1 min-w-0">
        <div className="truncate" style={{ fontSize: 13 }}>{displayName}</div>
        <div className="font-mono" style={{ fontSize: 11, marginTop: 2, color: 'var(--color-text-tertiary)' }}>{timeStr}</div>
      </div>
      {hasScore ? (
        <span className="font-bold font-mono" style={{ fontSize: 14, color: scoreColor }}>{item.mastery_score}</span>
      ) : (
        <span style={{ fontSize: 11, color: 'var(--color-accent-amber)' }}>学习中</span>
      )}
      {clickable && <ArrowRight size={13} className="opacity-0 group-hover:opacity-100 transition-opacity shrink-0" style={{ color: 'var(--color-text-tertiary)' }} />}
    </button>
  );
}
