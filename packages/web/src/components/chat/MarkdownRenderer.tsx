import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Components } from 'react-markdown';

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

const components: Components = {
  // Headings
  h1: ({ children }) => (
    <h1 className="text-2xl font-bold mt-4 mb-2" style={{ color: 'var(--color-text-primary)' }}>{children}</h1>
  ),
  h2: ({ children }) => (
    <h2 className="text-xl font-bold mt-3 mb-1.5" style={{ color: 'var(--color-text-primary)' }}>{children}</h2>
  ),
  h3: ({ children }) => (
    <h3 className="text-lg font-bold mt-2 mb-1" style={{ color: 'var(--color-text-primary)' }}>{children}</h3>
  ),

  // Paragraph
  p: ({ children }) => (
    <p className="mb-3 last:mb-0 leading-[1.85]">{children}</p>
  ),

  // Lists
  ul: ({ children }) => (
    <ul className="mb-3 pl-5 space-y-1.5 list-disc" style={{ color: 'var(--color-text-secondary)' }}>{children}</ul>
  ),
  ol: ({ children }) => (
    <ol className="mb-3 pl-5 space-y-1.5 list-decimal" style={{ color: 'var(--color-text-secondary)' }}>{children}</ol>
  ),
  li: ({ children }) => (
    <li className="leading-[1.85]">{children}</li>
  ),

  // Inline code
  code: ({ children, className }) => {
    const isBlock = className?.startsWith('language-');
    if (isBlock) {
      return (
        <code
          className="block text-[17px] font-mono leading-relaxed whitespace-pre-wrap break-words"
          style={{ color: '#e2e8f0' }}
        >
          {children}
        </code>
      );
    }
    return (
      <code
        className="text-[17px] font-mono px-1.5 py-0.5 rounded-md"
        style={{
          backgroundColor: '#1e293b',
          color: '#e2e8f0',
        }}
      >
        {children}
      </code>
    );
  },

  // Code block
  pre: ({ children }) => (
    <pre
      className="mb-2 rounded-lg px-4 py-3 overflow-x-auto text-[17px] leading-relaxed"
      style={{
        backgroundColor: '#1e293b',
        border: '1px solid rgba(0, 0, 0, 0.15)',
      }}
    >
      {children}
    </pre>
  ),

  // Bold
  strong: ({ children }) => (
    <strong className="font-bold" style={{ color: 'var(--color-text-primary)' }}>{children}</strong>
  ),

  // Italic
  em: ({ children }) => (
    <em className="italic" style={{ color: 'var(--color-accent-amber)' }}>{children}</em>
  ),

  // Blockquote
  blockquote: ({ children }) => (
    <blockquote
      className="mb-2 pl-3 border-l-2"
      style={{
        borderColor: 'var(--color-accent-indigo)',
        color: 'var(--color-text-secondary)',
      }}
    >
      {children}
    </blockquote>
  ),

  // Horizontal rule
  hr: () => (
    <hr className="my-3" style={{ borderColor: 'var(--color-border)' }} />
  ),

  // Table
  table: ({ children }) => (
    <div className="mb-2 overflow-x-auto rounded-lg" style={{ border: '1px solid var(--color-border)' }}>
      <table className="w-full text-sm">{children}</table>
    </div>
  ),
  thead: ({ children }) => (
    <thead style={{ backgroundColor: 'var(--color-surface-3)' }}>{children}</thead>
  ),
  th: ({ children }) => (
    <th className="px-3 py-2 text-left text-xs font-semibold" style={{ color: 'var(--color-text-secondary)', borderBottom: '1px solid var(--color-border)' }}>{children}</th>
  ),
  td: ({ children }) => (
    <td className="px-3 py-2 text-sm" style={{ color: 'var(--color-text-primary)', borderBottom: '1px solid var(--color-border-subtle, var(--color-border))' }}>{children}</td>
  ),

  // Links
  a: ({ children, href }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="underline underline-offset-2 transition-colors"
      style={{ color: 'var(--color-accent-indigo)' }}
    >
      {children}
    </a>
  ),
};

export function MarkdownRenderer({ content, className }: MarkdownRendererProps) {
  return (
    <div className={className}>
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {content}
      </ReactMarkdown>
    </div>
  );
}