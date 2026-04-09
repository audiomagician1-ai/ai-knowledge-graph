import type { SavedConversation } from '@/lib/store/dialogue';
import { History, Brain, Trash2, MessageSquare, X } from 'lucide-react';

interface ChatHistoryViewProps {
  conceptName: string;
  conversations: SavedConversation[];
  onClose: () => void;
  onLoad: (conversationId: string) => void;
  onDelete: (conversationId: string) => void;
}

export function ChatHistoryView({
  conceptName, conversations, onClose, onLoad, onDelete,
}: ChatHistoryViewProps) {
  return (
    <div className="flex flex-col h-full">
      <div
        className="flex items-center justify-between px-8 py-6 shrink-0"
        style={{ borderBottom: '1px solid var(--color-border)' }}
      >
        <div className="flex items-center gap-3">
          <History size={18} style={{ color: 'var(--color-accent-primary)' }} />
          <span className="text-base font-bold" style={{ color: 'var(--color-text-primary)' }}>
            "{conceptName}" 的对话记录
          </span>
        </div>
        <button
          onClick={onClose}
          className="w-10 h-10 flex items-center justify-center rounded-xl transition-colors hover:bg-white/5"
          style={{ color: 'var(--color-text-tertiary)' }}
        >
          <X size={18} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {conversations.length === 0 ? (
          <div className="p-8 text-center">
            <MessageSquare size={32} className="mx-auto mb-4" style={{ color: 'var(--color-text-tertiary)' }} />
            <p className="text-base" style={{ color: 'var(--color-text-tertiary)' }}>暂无对话记录</p>
          </div>
        ) : (
          <div className="p-4 space-y-3">
            {conversations.map((conv) => (
              <div
                key={conv.conversationId}
                className="group flex items-center gap-4 rounded-xl px-6 py-5 cursor-pointer transition-all"
                style={{ border: '1px solid var(--color-border)', backgroundColor: 'var(--color-surface-2)' }}
                onClick={() => onLoad(conv.conversationId)}
                onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--color-border-accent)'; }}
                onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--color-border)'; }}
              >
                <Brain size={20} style={{ color: 'var(--color-accent-primary)', flexShrink: 0 }} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3">
                    <span className="text-[15px]" style={{ color: 'var(--color-text-secondary)' }}>
                      {conv.messages.length} 条消息
                    </span>
                    {conv.assessment && (
                      <span
                        className="text-[15px] font-bold"
                        style={{ color: conv.assessment.mastered ? 'var(--color-accent-emerald)' : 'var(--color-accent-amber)' }}
                      >
                        {conv.assessment.overall_score}分 {conv.assessment.mastered ? '✓' : ''}
                      </span>
                    )}
                  </div>
                  <span className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>
                    {new Date(conv.updatedAt).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                <button
                  onClick={(e) => { e.stopPropagation(); onDelete(conv.conversationId); }}
                  className="opacity-0 group-hover:opacity-100 w-10 h-10 flex items-center justify-center rounded-xl transition-all"
                  style={{ color: 'var(--color-accent-rose)' }}
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
