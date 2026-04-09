import { ArrowLeft, Star, BarChart3 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface LearnHeaderProps {
  conceptId?: string;
  domainId?: string;
  conceptName: string | null;
  isMilestone: boolean;
  userTurns: number;
  suggestAssess: boolean;
  assessment: unknown;
  isBusy: boolean;
  isAssessing: boolean;
  onRequestAssessment: () => void;
}

export function LearnHeader({
  conceptId, domainId, conceptName, isMilestone, userTurns,
  suggestAssess, assessment, isBusy, isAssessing, onRequestAssessment,
}: LearnHeaderProps) {
  const navigate = useNavigate();

  return (
    <header
      className="flex items-center gap-4 px-6 shrink-0 border-b"
      style={{
        height: '64px',
        backgroundColor: 'var(--color-surface-1)',
        borderColor: 'var(--color-border)',
      }}
    >
      <button
        onClick={() => navigate(domainId ? `/domain/${domainId}/${conceptId}` : '/')}
        className="flex items-center justify-center w-9 h-9 rounded-md transition-colors"
        style={{ color: 'var(--color-text-secondary)' }}
        onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--color-surface-3)')}
        onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
      >
        <ArrowLeft size={18} />
      </button>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          {isMilestone && <Star size={14} fill="var(--color-accent-amber)" style={{ color: 'var(--color-accent-amber)' }} />}
          <h1 className="text-[15px] font-bold truncate" style={{ color: 'var(--color-text-primary)' }}>
            {conceptName || conceptId}
          </h1>
        </div>
        <p className="text-[12px]" style={{ color: 'var(--color-text-tertiary)' }}>
          对话学习 · 第 {userTurns} 轮
        </p>
      </div>

      {suggestAssess && !assessment && (
        <button
          onClick={onRequestAssessment}
          disabled={isBusy}
          className="btn-primary flex items-center gap-2 px-4 py-2 text-[13px]"
          style={{ opacity: isBusy ? 0.5 : 1 }}
        >
          <BarChart3 size={14} />
          {isAssessing ? '评估中...' : '理解度评估'}
        </button>
      )}
    </header>
  );
}
