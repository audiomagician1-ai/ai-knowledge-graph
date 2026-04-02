import { describe, it, expect } from 'vitest';
import { parseChoicesFromContent, windowMessages, parseAssessmentJSON, tokenLimitParam, getDomainSupplement, getAssessmentSupplement } from '../direct-llm';

describe('parseChoicesFromContent', () => {
  it('should return empty for empty/null input', () => {
    expect(parseChoicesFromContent('')).toEqual({ content: '', choices: [] });
    expect(parseChoicesFromContent(null as any)).toEqual({ content: '', choices: [] });
  });

  it('should parse valid choices block', () => {
    const text = `Hello world\n\n\`\`\`choices\n[{"id":"opt-1","text":"Option A","type":"explore"},{"id":"opt-2","text":"Option B","type":"answer"}]\n\`\`\``;
    const result = parseChoicesFromContent(text);
    expect(result.content).toBe('Hello world');
    expect(result.choices).toHaveLength(2);
    expect(result.choices[0]).toEqual({ id: 'opt-1', text: 'Option A', type: 'explore' });
  });

  it('should limit choices to max 4', () => {
    const choices = Array.from({ length: 6 }, (_, i) => ({ id: `opt-${i}`, text: `Choice ${i}`, type: 'explore' }));
    const text = `Content\n\n\`\`\`choices\n${JSON.stringify(choices)}\n\`\`\``;
    const result = parseChoicesFromContent(text);
    expect(result.choices).toHaveLength(4);
  });

  it('should truncate choice text to 60 chars', () => {
    const longText = 'A'.repeat(100);
    const text = `Content\n\n\`\`\`choices\n[{"id":"opt-1","text":"${longText}","type":"explore"},{"id":"opt-2","text":"Short","type":"answer"}]\n\`\`\``;
    const result = parseChoicesFromContent(text);
    expect(result.choices[0].text).toHaveLength(60);
  });

  it('should default type to explore for unknown types', () => {
    const text = `Content\n\n\`\`\`choices\n[{"id":"opt-1","text":"A","type":"unknown"},{"id":"opt-2","text":"B","type":"answer"}]\n\`\`\``;
    const result = parseChoicesFromContent(text);
    expect(result.choices[0].type).toBe('explore');
    expect(result.choices[1].type).toBe('answer');
  });

  it('should return no choices for invalid JSON', () => {
    const text = 'Hello\n\n```choices\nnot valid json\n```';
    const result = parseChoicesFromContent(text);
    expect(result.content).toBe('Hello');
    expect(result.choices).toEqual([]);
  });

  it('should require at least 2 valid choices', () => {
    const text = `Content\n\n\`\`\`choices\n[{"id":"opt-1","text":"Only one","type":"explore"}]\n\`\`\``;
    const result = parseChoicesFromContent(text);
    expect(result.choices).toEqual([]);
  });

  it('should filter out choices with empty text', () => {
    const text = `Content\n\n\`\`\`choices\n[{"id":"opt-1","text":"","type":"explore"},{"id":"opt-2","text":"Valid","type":"explore"},{"id":"opt-3","text":"Also valid","type":"answer"}]\n\`\`\``;
    const result = parseChoicesFromContent(text);
    expect(result.choices).toHaveLength(2);
  });

  it('should return text as-is when no choices block', () => {
    const text = 'Just plain text without choices';
    const result = parseChoicesFromContent(text);
    expect(result.content).toBe(text);
    expect(result.choices).toEqual([]);
  });
});

describe('windowMessages', () => {
  it('should return messages as-is when under limit', () => {
    const msgs = [{ role: 'assistant', content: 'hi' }, { role: 'user', content: 'hello' }];
    expect(windowMessages(msgs)).toEqual(msgs);
  });

  it('should keep first message + last N when over limit', () => {
    const msgs = Array.from({ length: 25 }, (_, i) => ({
      role: i % 2 === 0 ? 'assistant' : 'user',
      content: `msg-${i}`,
    }));
    const result = windowMessages(msgs);
    // Should be 20 messages: first + last 19
    expect(result).toHaveLength(20);
    expect(result[0].content).toBe('msg-0');
    expect(result[result.length - 1].content).toBe('msg-24');
  });

  it('should not modify array at exactly limit', () => {
    const msgs = Array.from({ length: 20 }, (_, i) => ({
      role: 'user',
      content: `msg-${i}`,
    }));
    expect(windowMessages(msgs)).toHaveLength(20);
  });
});

describe('parseAssessmentJSON', () => {
  it('should parse direct JSON and validate', () => {
    const json = JSON.stringify({
      completeness: 80, accuracy: 85, depth: 70, examples: 75,
      overall_score: 78, gaps: [], feedback: 'Good', mastered: true,
    });
    const result = parseAssessmentJSON(json);
    expect(result).not.toBeNull();
    expect(result.overall_score).toBe(78);
    expect(result.mastered).toBe(true);
  });

  it('should clamp scores in direct JSON path', () => {
    const json = JSON.stringify({
      completeness: 150, accuracy: -10, depth: 200, examples: 50,
      overall_score: 120, gaps: [], feedback: 'test',
    });
    const result = parseAssessmentJSON(json);
    expect(result).not.toBeNull();
    expect(result.completeness).toBe(100);
    expect(result.accuracy).toBe(0);
    expect(result.overall_score).toBe(100);
    // mastered recalculated: overall 100>=75 but accuracy 0<60 → false
    expect(result.mastered).toBe(false);
  });

  it('should recalculate mastered in direct JSON path (LLM lies)', () => {
    // LLM says mastered:true but depth is below threshold
    const json = JSON.stringify({
      completeness: 80, accuracy: 80, depth: 55, examples: 80,
      overall_score: 76, gaps: [], feedback: 'ok', mastered: true,
    });
    const result = parseAssessmentJSON(json);
    expect(result).not.toBeNull();
    expect(result.mastered).toBe(false); // depth 55 < 60 → overridden
  });

  it('should parse JSON inside ```json block and validate', () => {
    const text = 'Here is my assessment:\n```json\n{"completeness":90,"accuracy":85,"depth":80,"examples":75,"overall_score":83,"gaps":[],"feedback":"Great","mastered":true}\n```\nDone.';
    const result = parseAssessmentJSON(text);
    expect(result).not.toBeNull();
    expect(result.overall_score).toBe(83);
    expect(result.mastered).toBe(true);
  });

  it('should clamp scores in ```json block path', () => {
    const text = '```json\n{"completeness":999,"accuracy":-50,"depth":80,"examples":80,"overall_score":80}\n```';
    const result = parseAssessmentJSON(text);
    expect(result).not.toBeNull();
    expect(result.completeness).toBe(100);
    expect(result.accuracy).toBe(0);
    // mastered: overall 80>=75 but accuracy 0<60 → false
    expect(result.mastered).toBe(false);
    // gaps should be filled in
    expect(result.gaps).toEqual([]);
    expect(result.feedback).toBe('评估完成');
  });

  it('should extract JSON from mixed text using brace matching', () => {
    const text = 'The assessment: {"completeness":60,"accuracy":55,"depth":50,"examples":45,"overall_score":52,"gaps":["low depth"],"feedback":"Need improvement","mastered":false} end.';
    const result = parseAssessmentJSON(text);
    expect(result).not.toBeNull();
    expect(result.overall_score).toBe(52);
    // mastered should be recalculated: 52 < 75, so false
    expect(result.mastered).toBe(false);
  });

  it('should clamp scores in brace-match path', () => {
    const json = JSON.stringify({
      completeness: 150, accuracy: -10, depth: 200, examples: 50,
      overall_score: 120, gaps: [], feedback: 'test',
    });
    const text = `Assessment: ${json} done`;
    const result = parseAssessmentJSON(text);
    expect(result).not.toBeNull();
    expect(result.completeness).toBe(100);
    expect(result.accuracy).toBe(0);
    expect(result.overall_score).toBe(100);
  });

  it('should recalculate mastered based on scores', () => {
    // overall >= 75 but one dim < 60 → should NOT be mastered
    const text = `X {"completeness":80,"accuracy":80,"depth":55,"examples":80,"overall_score":76,"gaps":[],"feedback":"ok"} Y`;
    const result = parseAssessmentJSON(text);
    expect(result).not.toBeNull();
    expect(result.mastered).toBe(false); // depth 55 < 60
  });

  it('should handle non-numeric score values gracefully', () => {
    // LLM returns string instead of number — should fallback to 50
    const json = JSON.stringify({
      completeness: 'high', accuracy: null, depth: undefined, examples: true,
      overall_score: 'excellent', gaps: [], feedback: 'ok',
    });
    const result = parseAssessmentJSON(json);
    expect(result).not.toBeNull();
    // 'high' → NaN → fallback 50, null → fallback 50 (matches Python TypeError → defaults), true → Number(true)=1
    expect(result.completeness).toBe(50);
    expect(result.accuracy).toBe(50);
    expect(result.examples).toBe(1);
    expect(result.overall_score).toBe(50);
    expect(result.mastered).toBe(false);
  });

  it('should return null for completely unparseable text', () => {
    expect(parseAssessmentJSON('no json here')).toBeNull();
    expect(parseAssessmentJSON('')).toBeNull();
  });

  it('should fill in missing gaps and feedback', () => {
    const text = `X {"completeness":80,"accuracy":80,"depth":80,"examples":80,"overall_score":80} Y`;
    const result = parseAssessmentJSON(text);
    expect(result).not.toBeNull();
    expect(result.gaps).toEqual([]);
    expect(result.feedback).toBe('评估完成');
    expect(result.mastered).toBe(true);
  });
});

describe('tokenLimitParam', () => {
  it('should return max_tokens for standard models', () => {
    expect(tokenLimitParam('gpt-4o', 800)).toEqual({ max_tokens: 800 });
    expect(tokenLimitParam('deepseek-chat', 512)).toEqual({ max_tokens: 512 });
    expect(tokenLimitParam('claude-3.5-sonnet', 1024)).toEqual({ max_tokens: 1024 });
  });

  it('should return max_completion_tokens for o1/o3 series (bare name)', () => {
    expect(tokenLimitParam('o1', 800)).toEqual({ max_completion_tokens: 800 });
    expect(tokenLimitParam('o1-mini', 512)).toEqual({ max_completion_tokens: 512 });
    expect(tokenLimitParam('o3', 1024)).toEqual({ max_completion_tokens: 1024 });
    expect(tokenLimitParam('o3-pro', 600)).toEqual({ max_completion_tokens: 600 });
  });

  it('should return max_completion_tokens for vendor-prefixed o1/o3', () => {
    expect(tokenLimitParam('openai/o1', 800)).toEqual({ max_completion_tokens: 800 });
    expect(tokenLimitParam('openai/o3-pro', 1024)).toEqual({ max_completion_tokens: 1024 });
  });

  it('should return max_completion_tokens for chatgpt- series', () => {
    expect(tokenLimitParam('chatgpt-4o-latest', 800)).toEqual({ max_completion_tokens: 800 });
    expect(tokenLimitParam('openai/chatgpt-5', 1024)).toEqual({ max_completion_tokens: 1024 });
  });

  it('should return max_completion_tokens for gpt-5+ series', () => {
    expect(tokenLimitParam('gpt-5', 800)).toEqual({ max_completion_tokens: 800 });
    expect(tokenLimitParam('gpt-5.2', 1024)).toEqual({ max_completion_tokens: 1024 });
    expect(tokenLimitParam('gpt-5-turbo', 512)).toEqual({ max_completion_tokens: 512 });
    expect(tokenLimitParam('gpt-6', 800)).toEqual({ max_completion_tokens: 800 });
    expect(tokenLimitParam('gpt-10', 800)).toEqual({ max_completion_tokens: 800 });
    expect(tokenLimitParam('openai/gpt-5.2', 1024)).toEqual({ max_completion_tokens: 1024 });
  });

  it('should be case-insensitive', () => {
    expect(tokenLimitParam('O1-Mini', 512)).toEqual({ max_completion_tokens: 512 });
    expect(tokenLimitParam('CHATGPT-4o-latest', 800)).toEqual({ max_completion_tokens: 800 });
    expect(tokenLimitParam('GPT-5.2', 1024)).toEqual({ max_completion_tokens: 1024 });
  });

  it('should NOT match models containing o1/o3 as substring', () => {
    // "gpt-4o" should NOT match (4o != o4, but starts with o-check)
    expect(tokenLimitParam('gpt-4o-mini', 800)).toEqual({ max_tokens: 800 });
    expect(tokenLimitParam('gpt-4o', 800)).toEqual({ max_tokens: 800 });
    expect(tokenLimitParam('modelo1', 800)).toEqual({ max_tokens: 800 });
  });
});

describe('getDomainSupplement', () => {
  it('should return supplement for all 11 active domains', () => {
    expect(getDomainSupplement('mathematics')).toContain('数学教学特殊规则');
    expect(getDomainSupplement('english')).toContain('英语教学特殊规则');
    expect(getDomainSupplement('physics')).toContain('物理教学特殊规则');
    expect(getDomainSupplement('product-design')).toContain('产品设计教学特殊规则');
    expect(getDomainSupplement('finance')).toContain('金融理财教学特殊规则');
    expect(getDomainSupplement('psychology')).toContain('心理学教学特殊规则');
    expect(getDomainSupplement('philosophy')).toContain('哲学教学特殊规则');
    expect(getDomainSupplement('biology')).toContain('生物学教学特殊规则');
    expect(getDomainSupplement('economics')).toContain('经济学教学特殊规则');
    expect(getDomainSupplement('writing')).toContain('写作教学特殊规则');
    expect(getDomainSupplement('game-design')).toContain('游戏设计教学特殊规则');
  });

  it('should return empty for unknown/default domain', () => {
    expect(getDomainSupplement('ai-engineering')).toBe('');
    expect(getDomainSupplement('nonexistent')).toBe('');
    expect(getDomainSupplement(undefined)).toBe('');
  });
});

describe('getAssessmentSupplement', () => {
  it('should return assessment supplement for all 11 active domains', () => {
    expect(getAssessmentSupplement('mathematics')).toContain('数学领域评估特殊指标');
    expect(getAssessmentSupplement('english')).toContain('英语领域评估特殊指标');
    expect(getAssessmentSupplement('physics')).toContain('物理领域评估特殊指标');
    expect(getAssessmentSupplement('product-design')).toContain('产品设计领域评估特殊指标');
    expect(getAssessmentSupplement('finance')).toContain('金融理财领域评估特殊指标');
    expect(getAssessmentSupplement('psychology')).toContain('心理学领域评估特殊指标');
    expect(getAssessmentSupplement('philosophy')).toContain('哲学领域评估特殊指标');
    expect(getAssessmentSupplement('biology')).toContain('生物学领域评估特殊指标');
    expect(getAssessmentSupplement('economics')).toContain('经济学领域评估特殊指标');
    expect(getAssessmentSupplement('writing')).toContain('写作领域评估特殊指标');
    expect(getAssessmentSupplement('game-design')).toContain('游戏设计领域评估特殊指标');
  });

  it('should return empty for unknown/default domain', () => {
    expect(getAssessmentSupplement('ai-engineering')).toBe('');
    expect(getAssessmentSupplement('nonexistent')).toBe('');
    expect(getAssessmentSupplement(undefined)).toBe('');
  });
});
