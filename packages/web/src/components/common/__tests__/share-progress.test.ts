import { describe, it, expect } from 'vitest';

/**
 * Tests for ShareProgress text generation logic.
 */

function generateShareText(params: {
  totalStudied: number;
  masteredCount: number;
  learningCount: number;
  streakDays: number;
  domainName?: string;
  totalMinutes?: number;
}): string {
  const { totalStudied, masteredCount, learningCount, streakDays, domainName, totalMinutes } = params;
  const lines = [
    `🧠 AI知识图谱 — 学习进度分享`,
    ``,
    `📊 总进度：${totalStudied} 个概念`,
    `✅ 已掌握：${masteredCount} 个`,
    `📖 学习中：${learningCount} 个`,
    `🔥 连续学习：${streakDays} 天`,
  ];
  if (domainName) lines.push(`🌐 当前领域：${domainName}`);
  if (totalMinutes && totalMinutes > 0) {
    const hours = Math.floor(totalMinutes / 60);
    const mins = totalMinutes % 60;
    lines.push(`⏱️ 累计学习：${hours > 0 ? `${hours}小时` : ''}${mins}分钟`);
  }
  lines.push(``);
  lines.push(`来和我一起学习吧！ → https://akg-web.pages.dev`);
  return lines.join('\n');
}

describe('ShareProgress text generation', () => {
  it('includes basic stats', () => {
    const text = generateShareText({ totalStudied: 42, masteredCount: 20, learningCount: 22, streakDays: 7 });
    expect(text).toContain('42 个概念');
    expect(text).toContain('20 个');
    expect(text).toContain('22 个');
    expect(text).toContain('7 天');
  });

  it('includes domain name when provided', () => {
    const text = generateShareText({ totalStudied: 10, masteredCount: 5, learningCount: 5, streakDays: 3, domainName: '编程基础' });
    expect(text).toContain('编程基础');
  });

  it('omits domain when not provided', () => {
    const text = generateShareText({ totalStudied: 10, masteredCount: 5, learningCount: 5, streakDays: 3 });
    expect(text).not.toContain('当前领域');
  });

  it('includes learning time when > 0', () => {
    const text = generateShareText({ totalStudied: 10, masteredCount: 5, learningCount: 5, streakDays: 3, totalMinutes: 130 });
    expect(text).toContain('2小时');
    expect(text).toContain('10分钟');
  });

  it('omits learning time when 0', () => {
    const text = generateShareText({ totalStudied: 10, masteredCount: 5, learningCount: 5, streakDays: 3, totalMinutes: 0 });
    expect(text).not.toContain('累计学习');
  });

  it('contains share URL', () => {
    const text = generateShareText({ totalStudied: 1, masteredCount: 0, learningCount: 1, streakDays: 0 });
    expect(text).toContain('https://akg-web.pages.dev');
  });

  it('handles zero progress gracefully', () => {
    const text = generateShareText({ totalStudied: 0, masteredCount: 0, learningCount: 0, streakDays: 0 });
    expect(text).toContain('0 个概念');
    expect(text).toContain('0 天');
  });
});
