import { CheckCircle2, AlertTriangle, ArrowLeft, RotateCcw } from 'lucide-react';

/* ── Error state ── */
interface ReviewErrorProps { error: string; onRetry: () => void }
export function ReviewError({ error, onRetry }: ReviewErrorProps) {
  return (
    <div className="flex flex-col items-center gap-4">
      <AlertTriangle size={32} style={{ color: 'var(--color-accent-rose)' }} />
      <p className="text-sm" style={{ color: 'var(--color-accent-rose)' }}>{error}</p>
      <button onClick={onRetry} className="btn-primary px-4 py-2 text-sm">重新加载</button>
    </div>
  );
}

/* ── Empty queue — nothing to review ── */
interface ReviewEmptyProps { onBack: () => void }
export function ReviewEmpty({ onBack }: ReviewEmptyProps) {
  return (
    <div className="flex flex-col items-center gap-4 text-center">
      <div className="w-16 h-16 rounded-2xl flex items-center justify-center"
        style={{ backgroundColor: 'rgba(16,185,129,0.1)' }}>
        <CheckCircle2 size={32} style={{ color: 'var(--color-accent-primary)' }} />
      </div>
      <h2 className="text-lg font-bold" style={{ color: 'var(--color-text-primary)' }}>全部复习完成！</h2>
      <p className="text-sm max-w-xs" style={{ color: 'var(--color-text-secondary)' }}>
        目前没有待复习的概念。继续学习新知识，系统会自动安排复习。
      </p>
      <button onClick={onBack} className="btn-primary px-5 py-2.5 text-sm flex items-center gap-2">
        <ArrowLeft size={14} /> 返回图谱
      </button>
    </div>
  );
}

/* ── All done — session completed ── */
interface ReviewCompleteProps { completedCount: number; onRetry: () => void; onBack: () => void }
export function ReviewComplete({ completedCount, onRetry, onBack }: ReviewCompleteProps) {
  return (
    <div className="flex flex-col items-center gap-4 text-center animate-fade-in">
      <div className="w-16 h-16 rounded-2xl flex items-center justify-center"
        style={{ backgroundColor: 'rgba(16,185,129,0.1)' }}>
        <CheckCircle2 size={32} style={{ color: 'var(--color-accent-primary)' }} />
      </div>
      <h2 className="text-lg font-bold" style={{ color: 'var(--color-text-primary)' }}>本轮复习完成！</h2>
      <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>共复习 {completedCount} 个概念</p>
      <div className="flex gap-3 mt-2">
        <button onClick={onRetry} className="btn-ghost px-4 py-2.5 text-sm flex items-center gap-2">
          <RotateCcw size={14} /> 检查更多
        </button>
        <button onClick={onBack} className="btn-primary px-4 py-2.5 text-sm flex items-center gap-2">
          <ArrowLeft size={14} /> 返回图谱
        </button>
      </div>
    </div>
  );
}
