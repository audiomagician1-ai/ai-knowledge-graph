import { ArrowLeft, RotateCcw, ChevronRight, Sparkles } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { ConceptNoteEditor } from '@/components/common/ConceptNoteEditor';
import type { AssessmentResult } from '@/lib/store/dialogue';

interface LearnPostAssessmentProps {
  conceptId?: string;
  domainId?: string;
  conceptName: string | null;
  assessment: AssessmentResult;
  recommendedIds: Set<string>;
  onRestart: () => void;
}

export function LearnPostAssessment({
  conceptId, domainId, conceptName, assessment, recommendedIds, onRestart,
}: LearnPostAssessmentProps) {
  const navigate = useNavigate();

  return (
    <div
      className="shrink-0 border-t"
      style={{
        backgroundColor: 'var(--color-surface-1)',
        borderColor: 'var(--color-border)',
        paddingBottom: 'env(safe-area-inset-bottom, 0px)',
      }}
    >
      <div className="max-w-3xl mx-auto px-6 py-4 space-y-3">
        {assessment?.mastered && (
          <div className="flex items-center justify-center gap-2 py-2">
            <Sparkles size={14} style={{ color: 'var(--color-accent-emerald)' }} />
            <span className="text-[13px] font-medium" style={{ color: 'var(--color-accent-emerald)' }}>
              知识图谱又亮了一个节点！
            </span>
          </div>
        )}

        <div className="flex gap-3">
          <button
            onClick={() => navigate(domainId ? `/domain/${domainId}/${conceptId}` : '/')}
            className="btn-ghost flex-1 flex items-center justify-center gap-2 py-3"
          >
            <ArrowLeft size={16} />
            返回图谱
          </button>
          <button
            onClick={onRestart}
            className="btn-ghost flex-1 flex items-center justify-center gap-2 py-3"
          >
            <RotateCcw size={16} />
            再来一轮
          </button>
        </div>

        {conceptId && (
          <ConceptNoteEditor
            conceptId={conceptId}
            conceptName={conceptName || conceptId}
            compact
          />
        )}

        {recommendedIds.size > 0 && (
          <button
            onClick={() => {
              const nextId = Array.from(recommendedIds)[0];
              if (domainId) navigate(`/domain/${domainId}/${nextId}/learn`);
              else navigate(`/learn/${nextId}`);
            }}
            className="w-full flex items-center justify-center gap-2 py-3 rounded-xl text-[14px] font-semibold transition-all"
            style={{
              background: 'var(--color-accent-primary)',
              color: 'var(--color-text-on-accent)',
            }}
          >
            <ChevronRight size={16} />
            继续学习下一个知识点
          </button>
        )}
      </div>
    </div>
  );
}
