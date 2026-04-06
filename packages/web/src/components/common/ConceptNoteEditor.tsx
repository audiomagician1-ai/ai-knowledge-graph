import { useState, useEffect, useRef } from 'react';
import { useConceptNotes } from '@/lib/hooks/useConceptNotes';
import { StickyNote, Save, Trash2, ChevronDown, ChevronUp } from 'lucide-react';

interface ConceptNoteEditorProps {
  conceptId: string;
  conceptName: string;
  /** Compact mode for inline display (default: false) */
  compact?: boolean;
}

/**
 * Inline note editor for a specific concept.
 * Shows a collapsible textarea for quick note-taking during learning.
 */
export function ConceptNoteEditor({ conceptId, conceptName, compact = false }: ConceptNoteEditorProps) {
  const { getNote, saveNote, deleteNote } = useConceptNotes();
  const [isOpen, setIsOpen] = useState(false);
  const [text, setText] = useState('');
  const [saved, setSaved] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Load existing note when opened
  useEffect(() => {
    if (isOpen) {
      const existing = getNote(conceptId);
      setText(existing?.content || '');
      // Auto-focus
      setTimeout(() => textareaRef.current?.focus(), 100);
    }
  }, [isOpen, conceptId, getNote]);

  const handleSave = () => {
    if (text.trim()) {
      saveNote(conceptId, text.trim());
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    }
  };

  const handleDelete = () => {
    deleteNote(conceptId);
    setText('');
    setIsOpen(false);
  };

  const existingNote = getNote(conceptId);
  const hasNote = !!existingNote;

  return (
    <div className="rounded-lg overflow-hidden" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      {/* Toggle header */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center gap-2 px-4 py-2.5 text-left hover:bg-white/5 transition-colors"
      >
        <StickyNote size={14} style={{ color: hasNote ? '#f59e0b' : 'var(--color-text-tertiary)' }} />
        <span className="text-sm font-medium" style={{ color: 'var(--color-text-secondary)' }}>
          {compact ? '笔记' : `我的笔记${hasNote ? ' ✏️' : ''}`}
        </span>
        {hasNote && !isOpen && (
          <span className="text-xs opacity-40 truncate flex-1 ml-2">
            {existingNote.content.slice(0, 40)}...
          </span>
        )}
        <span className="ml-auto">
          {isOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </span>
      </button>

      {/* Editor body */}
      {isOpen && (
        <div className="px-4 pb-3 space-y-2">
          <textarea
            ref={textareaRef}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={`记录你对「${conceptName}」的理解、疑问或联想…`}
            rows={compact ? 3 : 5}
            className="w-full bg-transparent text-sm outline-none resize-none rounded-lg p-3"
            style={{
              color: 'var(--color-text-primary)',
              border: '1px solid var(--color-border)',
              minHeight: compact ? '60px' : '100px',
            }}
          />
          <div className="flex items-center gap-2">
            <button
              onClick={handleSave}
              disabled={!text.trim()}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
              style={{
                backgroundColor: saved ? '#22c55e' : 'var(--color-accent-primary)',
                color: '#fff',
                opacity: text.trim() ? 1 : 0.4,
              }}
            >
              <Save size={12} />
              {saved ? '已保存 ✓' : '保存笔记'}
            </button>
            {hasNote && (
              <button
                onClick={handleDelete}
                className="flex items-center gap-1 px-2 py-1.5 rounded-lg text-xs transition-colors hover:bg-red-500/10"
                style={{ color: '#ef4444' }}
              >
                <Trash2 size={12} />
                删除
              </button>
            )}
            {existingNote && (
              <span className="ml-auto text-[10px] opacity-30">
                上次: {new Date(existingNote.updatedAt).toLocaleDateString('zh-CN')}
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
