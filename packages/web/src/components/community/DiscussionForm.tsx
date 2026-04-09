/**
 * DiscussionForm — New discussion creation form with type selector.
 * Extracted from ConceptDiscussionPanel (V2.12 Code Health).
 */

import { HelpCircle, Lightbulb, Link2, BookOpen, Send } from 'lucide-react';

export const TYPE_CONFIG: Record<string, { icon: typeof HelpCircle; label: string; color: string }> = {
  question: { icon: HelpCircle, label: '提问', color: '#3b82f6' },
  insight: { icon: Lightbulb, label: '洞见', color: '#f59e0b' },
  resource: { icon: Link2, label: '资源', color: '#22c55e' },
  explanation: { icon: BookOpen, label: '解释', color: '#8b5cf6' },
};

interface DiscussionFormProps {
  formType: string;
  formTitle: string;
  formContent: string;
  onTypeChange: (t: string) => void;
  onTitleChange: (v: string) => void;
  onContentChange: (v: string) => void;
  onSubmit: () => void;
  onCancel: () => void;
}

export function DiscussionForm({
  formType, formTitle, formContent,
  onTypeChange, onTitleChange, onContentChange,
  onSubmit, onCancel,
}: DiscussionFormProps) {
  return (
    <div className="rounded-lg p-3 space-y-2" style={{ backgroundColor: 'var(--color-surface-0)' }}>
      <div className="flex gap-1">
        {Object.entries(TYPE_CONFIG).map(([key, cfg]) => {
          const Icon = cfg.icon;
          return (
            <button
              key={key}
              onClick={() => onTypeChange(key)}
              className="flex items-center gap-1 px-2 py-1 rounded text-xs transition-colors"
              style={{
                backgroundColor: formType === key ? `${cfg.color}20` : 'transparent',
                color: formType === key ? cfg.color : 'var(--color-text-secondary)',
              }}
            >
              <Icon size={12} /> {cfg.label}
            </button>
          );
        })}
      </div>
      <input
        value={formTitle}
        onChange={e => onTitleChange(e.target.value)}
        placeholder="标题..."
        className="w-full text-sm px-3 py-1.5 rounded-md bg-transparent border outline-none"
        style={{ borderColor: 'var(--color-border)', color: 'var(--color-text-primary)' }}
      />
      <textarea
        value={formContent}
        onChange={e => onContentChange(e.target.value)}
        placeholder="详细内容..."
        rows={3}
        className="w-full text-sm px-3 py-1.5 rounded-md bg-transparent border outline-none resize-none"
        style={{ borderColor: 'var(--color-border)', color: 'var(--color-text-primary)' }}
      />
      <div className="flex justify-end gap-2">
        <button onClick={onCancel} className="text-xs px-3 py-1.5 rounded-md hover:bg-white/10 transition-colors"
          style={{ color: 'var(--color-text-secondary)' }}>取消</button>
        <button
          onClick={onSubmit}
          disabled={!formTitle.trim() || !formContent.trim()}
          className="flex items-center gap-1 text-xs px-3 py-1.5 rounded-md text-white transition-colors disabled:opacity-40"
          style={{ backgroundColor: '#8b5cf6' }}
        >
          <Send size={12} /> 发布
        </button>
      </div>
    </div>
  );
}
