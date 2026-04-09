import { useState } from 'react';
import { TYPE_META } from './SuggestionCard';
import type { Suggestion } from './SuggestionCard';

interface SuggestionFormProps {
  onSubmit: (type: Suggestion['type'], title: string, description: string, domainId: string) => Promise<void>;
  onClose: () => void;
}

export function SuggestionForm({ onSubmit, onClose }: SuggestionFormProps) {
  const [formType, setFormType] = useState<Suggestion['type']>('concept');
  const [title, setTitle] = useState('');
  const [desc, setDesc] = useState('');
  const [domain, setDomain] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!title.trim() || !desc.trim() || desc.trim().length < 10) return;
    setSubmitting(true);
    try {
      await onSubmit(formType, title.trim(), desc.trim(), domain);
      setTitle(''); setDesc(''); onClose();
    } finally { setSubmitting(false); }
  };

  return (
    <div className="rounded-xl p-5 space-y-4" style={{ backgroundColor: 'var(--color-surface-1)', border: '1px solid var(--color-border)' }}>
      <h3 className="text-sm font-semibold">提交新建议</h3>
      <div className="flex gap-2 flex-wrap">
        {(Object.entries(TYPE_META) as [Suggestion['type'], typeof TYPE_META[keyof typeof TYPE_META]][]).map(([key, meta]) => (
          <button key={key} onClick={() => setFormType(key)}
            className="px-3 py-1.5 rounded-lg text-xs font-medium transition-all"
            style={{
              backgroundColor: formType === key ? meta.color + '33' : 'var(--color-surface-2)',
              border: `1px solid ${formType === key ? meta.color : 'var(--color-border)'}`,
              color: formType === key ? meta.color : 'var(--color-text-secondary)',
            }}>
            {meta.label}
          </button>
        ))}
      </div>
      <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="标题 (至少3个字符)"
        className="w-full px-4 py-2.5 rounded-xl text-sm bg-transparent outline-none"
        style={{ border: '1px solid var(--color-border)', color: 'var(--color-text-primary)' }} />
      <input type="text" value={domain} onChange={(e) => setDomain(e.target.value)} placeholder="相关知识域 (可选, 如 programming)"
        className="w-full px-4 py-2.5 rounded-xl text-sm bg-transparent outline-none"
        style={{ border: '1px solid var(--color-border)', color: 'var(--color-text-primary)' }} />
      <textarea value={desc} onChange={(e) => setDesc(e.target.value)} placeholder="详细描述 (至少10个字符)…" rows={4}
        className="w-full bg-transparent text-sm outline-none resize-none rounded-xl p-4"
        style={{ border: '1px solid var(--color-border)', color: 'var(--color-text-primary)' }} />
      <div className="flex gap-3">
        <button onClick={handleSubmit} disabled={submitting || title.trim().length < 3 || desc.trim().length < 10}
          className="px-4 py-2 rounded-lg text-sm font-medium"
          style={{ backgroundColor: 'var(--color-accent-primary)', color: '#fff', opacity: (submitting || title.trim().length < 3 || desc.trim().length < 10) ? 0.4 : 1 }}>
          {submitting ? '提交中…' : '提交建议'}
        </button>
        <button onClick={onClose} className="px-4 py-2 rounded-lg text-sm hover:bg-white/10">取消</button>
      </div>
    </div>
  );
}
