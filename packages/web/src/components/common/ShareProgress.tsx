import { useState, useCallback } from 'react';
import { Share2, Copy, Check, Twitter, Download } from 'lucide-react';
import { useLearningStore } from '@/lib/store/learning';
import { readLearningTime } from '@/lib/hooks/useLearningTimer';

interface ShareProgressProps {
  domainName?: string;
  domainId?: string;
}

/**
 * Share learning progress card with copy-to-clipboard, Twitter share, and image download.
 * Generates a text summary of the user's learning progress.
 */
export function ShareProgress({ domainName }: ShareProgressProps) {
  const [open, setOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const progress = useLearningStore((s) => s.progress);
  const streak = useLearningStore((s) => s.streak);

  const progressEntries = Object.values(progress);
  const masteredCount = progressEntries.filter((p) => p.status === 'mastered').length;
  const learningCount = progressEntries.filter((p) => p.status === 'learning').length;
  const totalStudied = masteredCount + learningCount;

  const generateShareText = useCallback(() => {
    const timeData = readLearningTime();
    const totalMin = Math.round(timeData.totalSeconds / 60);

    const lines = [
      `🧠 AI知识图谱 — 学习进度分享`,
      ``,
      `📊 总进度：${totalStudied} 个概念`,
      `✅ 已掌握：${masteredCount} 个`,
      `📖 学习中：${learningCount} 个`,
      `🔥 连续学习：${streak.current} 天`,
    ];
    if (domainName) {
      lines.push(`🌐 当前领域：${domainName}`);
    }
    if (totalMin > 0) {
      const hours = Math.floor(totalMin / 60);
      const mins = totalMin % 60;
      lines.push(`⏱️ 累计学习：${hours > 0 ? `${hours}小时` : ''}${mins}分钟`);
    }
    lines.push(``);
    lines.push(`来和我一起学习吧！ → https://akg-web.pages.dev`);
    return lines.join('\n');
  }, [totalStudied, masteredCount, learningCount, streak.current, domainName]);

  const handleCopy = async () => {
    const text = generateShareText();
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = text;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleTwitter = () => {
    const text = encodeURIComponent(
      `🧠 在AI知识图谱上已掌握 ${masteredCount} 个概念，连续学习 ${streak.current} 天！ #AI知识图谱 #学习打卡`
    );
    const url = encodeURIComponent('https://akg-web.pages.dev');
    window.open(`https://twitter.com/intent/tweet?text=${text}&url=${url}`, '_blank');
  };

  const handleDownloadText = () => {
    const text = generateShareText();
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `akg-progress-${new Date().toISOString().slice(0, 10)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="flex items-center gap-2 text-sm rounded-lg transition-colors px-3 py-2"
        style={{
          color: 'var(--color-accent-primary)',
          backgroundColor: 'rgba(16,185,129,0.08)',
          border: '1px solid rgba(16,185,129,0.15)',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = 'rgba(16,185,129,0.15)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = 'rgba(16,185,129,0.08)';
        }}
      >
        <Share2 size={14} />
        分享进度
      </button>
    );
  }

  return (
    <div
      className="rounded-xl animate-fade-in"
      style={{
        backgroundColor: 'var(--color-surface-1)',
        border: '1px solid var(--color-border)',
        boxShadow: '0 4px 16px rgba(0,0,0,0.08)',
        padding: '20px 24px',
      }}
    >
      <div className="flex items-center justify-between" style={{ marginBottom: 16 }}>
        <div className="flex items-center gap-2">
          <Share2 size={16} style={{ color: 'var(--color-accent-primary)' }} />
          <span className="text-sm font-bold" style={{ color: 'var(--color-text-primary)' }}>
            分享学习进度
          </span>
        </div>
        <button
          onClick={() => setOpen(false)}
          className="text-xs px-2 py-1 rounded-md hover:bg-black/5"
          style={{ color: 'var(--color-text-tertiary)' }}
        >
          关闭
        </button>
      </div>

      {/* Preview card */}
      <div
        className="rounded-lg"
        style={{
          padding: '16px 20px',
          backgroundColor: '#f8faf9',
          border: '1px solid rgba(16,185,129,0.12)',
          marginBottom: 16,
          fontSize: 13,
          lineHeight: 1.8,
          color: 'var(--color-text-secondary)',
          whiteSpace: 'pre-line',
        }}
      >
        {generateShareText()}
      </div>

      {/* Action buttons */}
      <div className="flex items-center gap-3">
        <button
          onClick={handleCopy}
          className="flex items-center gap-2 text-sm font-medium rounded-lg px-4 py-2.5 transition-colors"
          style={{
            backgroundColor: copied ? 'rgba(16,185,129,0.15)' : 'rgba(0,0,0,0.04)',
            color: copied ? 'var(--color-accent-emerald)' : 'var(--color-text-primary)',
          }}
        >
          {copied ? <Check size={14} /> : <Copy size={14} />}
          {copied ? '已复制' : '复制'}
        </button>
        <button
          onClick={handleTwitter}
          className="flex items-center gap-2 text-sm font-medium rounded-lg px-4 py-2.5 transition-colors"
          style={{ backgroundColor: 'rgba(29,155,240,0.1)', color: '#1d9bf0' }}
        >
          <Twitter size={14} />
          推特
        </button>
        <button
          onClick={handleDownloadText}
          className="flex items-center gap-2 text-sm font-medium rounded-lg px-4 py-2.5 transition-colors"
          style={{ backgroundColor: 'rgba(0,0,0,0.04)', color: 'var(--color-text-secondary)' }}
        >
          <Download size={14} />
          下载
        </button>
      </div>
    </div>
  );
}