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
      className="w-full text-left rounded-lg transition-all p-2.5 bg-[var(--color-surface-2)] border border-[var(--color-border)] cursor-pointer hover:bg-[var(--color-surface-3)]"
    >
      <div className="flex items-center gap-2.5">
        <span className="flex items-center justify-center shrink-0 rounded-md text-base"
          style={{ width: 30, height: 30, backgroundColor: `${domain.color}15` }}>
          {domain.icon}
        </span>
        <div className="flex-1 min-w-0">
          <div className="truncate text-sm font-semibold text-[var(--color-text-primary)]">{domain.name}</div>
          <div className="flex items-center gap-2 mt-0.5">
            <span className="text-[10px] text-[var(--color-text-tertiary)]">{conceptCount} 概念</span>
            {progress.mastered > 0 && <span className="text-[10px] text-[var(--color-accent-emerald)]">{progress.mastered} ✓</span>}
          </div>
        </div>
      </div>
      {conceptCount > 0 && (
        <div className="mt-2 flex items-center gap-2">
          <div className="flex-1 rounded-full overflow-hidden" style={{ height: 3, backgroundColor: 'var(--color-surface-4)' }}>
            <div style={{ height: '100%', borderRadius: 999, width: `${pct}%`, backgroundColor: domain.color, minWidth: pct > 0 ? 2 : 0, transition: 'width 0.4s ease' }} />
          </div>
          <span className="text-[10px] text-[var(--color-text-tertiary)] min-w-[22px] text-right font-mono">{pct}%</span>
        </div>
      )}
      {timeAgo && <div className="text-[10px] text-[var(--color-text-tertiary)] mt-1">{timeAgo}</div>}
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
      className="w-full flex items-center gap-2.5 rounded-lg py-2 px-3 bg-transparent border-none text-left transition-all group hover:bg-black/5" style={{ cursor: clickable ? 'pointer' : 'default' }}
    >
      <div className="flex items-center justify-center shrink-0 w-7 h-7 rounded-lg"
        style={{ backgroundColor: isMastered ? 'var(--color-tint-emerald)' : 'var(--color-tint-amber)', color: isMastered ? 'var(--color-accent-emerald)' : 'var(--color-accent-amber)' }}>
        {isMastered ? <Zap size={12} /> : <BookOpen size={12} />}
      </div>
      <div className="flex-1 min-w-0">
        <div className="truncate text-sm">{displayName}</div>
        <div className="font-mono text-[11px] mt-0.5 text-[var(--color-text-tertiary)]">{timeStr}</div>
      </div>
      {hasScore ? (
        <span className="font-bold font-mono text-sm" style={{ color: scoreColor }}>{item.mastery_score}</span>
      ) : (
        <span className="text-[11px] text-[var(--color-accent-amber)]">学习中</span>
      )}
      {clickable && <ArrowRight size={13} className="opacity-0 group-hover:opacity-100 transition-opacity shrink-0" style={{ color: 'var(--color-text-tertiary)' }} />}
    </button>
  );
}
