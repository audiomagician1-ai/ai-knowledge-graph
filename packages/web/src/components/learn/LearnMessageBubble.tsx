import { Brain } from 'lucide-react';
import { MarkdownRenderer } from '@/components/chat/MarkdownRenderer';
import { stripChoicesBlock } from '@/lib/utils/text';
import { InlineFeedback } from '@/components/common/InlineFeedback';

interface MessageData {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

interface LearnMessageBubbleProps {
  msg: MessageData;
  idx: number;
  isStreaming: boolean;
  conceptId?: string;
  domainId?: string;
}

export function LearnMessageBubble({ msg, idx, isStreaming, conceptId, domainId }: LearnMessageBubbleProps) {
  return (
    <div
      className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}
      style={{ animationDelay: `${Math.min(idx * 30, 200)}ms` }}
    >
      {msg.role === 'assistant' && (
        <div
          className="w-7 h-7 rounded-md flex items-center justify-center shrink-0 mr-3 mt-1"
          style={{ backgroundColor: 'var(--color-surface-3)' }}
        >
          <Brain size={13} style={{ color: 'var(--color-text-secondary)' }} />
        </div>
      )}
      <div
        style={{
          maxWidth: '78%',
          borderRadius: msg.role === 'user' ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
          padding: '20px 24px',
          fontSize: 14,
          lineHeight: 1.85,
          ...(msg.role === 'user'
            ? {
                backgroundColor: '#d4edda',
                color: 'var(--color-text-primary)',
                border: '1px solid rgba(16, 185, 129, 0.25)',
              }
            : {
                backgroundColor: '#ffffff',
                color: 'var(--color-text-primary)',
                border: '1px solid rgba(0, 0, 0, 0.1)',
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.08)',
              }),
        }}
      >
        {msg.role === 'assistant' ? (
          <>
            {msg.content ? (
              <MarkdownRenderer content={stripChoicesBlock(msg.content)} />
            ) : isStreaming ? (
              <div className="flex items-center gap-1 mt-1">
                <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ backgroundColor: 'var(--color-accent-primary)' }} />
                <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ backgroundColor: 'var(--color-text-tertiary)', animationDelay: '150ms' }} />
                <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ backgroundColor: 'var(--color-text-tertiary)', animationDelay: '300ms' }} />
              </div>
            ) : null}
            {msg.content && !isStreaming && idx > 0 && (
              <InlineFeedback
                conceptId={conceptId}
                domainId={domainId}
                messageContent={msg.content.slice(0, 300)}
                compact
              />
            )}
          </>
        ) : (
          <div className="whitespace-pre-wrap break-words">{msg.content}</div>
        )}
      </div>
    </div>
  );
}
