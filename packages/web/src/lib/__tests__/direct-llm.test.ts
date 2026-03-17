import { describe, it, expect } from 'vitest';
import { parseChoicesFromContent, windowMessages, parseAssessmentJSON } from '../direct-llm';

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
  it('should parse direct JSON', () => {
    const json = JSON.stringify({
      completeness: 80, accuracy: 85, depth: 70, examples: 75,
      overall_score: 78, gaps: [], feedback: 'Good', mastered: true,
    });
    const result = parseAssessmentJSON(json);
    expect(result).not.toBeNull();
    expect(result.overall_score).toBe(78);
    expect(result.mastered).toBe(true);
  });

  it('should parse JSON inside ```json block', () => {
    const text = 'Here is my assessment:\n```json\n{"completeness":90,"accuracy":85,"depth":80,"examples":75,"overall_score":83,"gaps":[],"feedback":"Great","mastered":true}\n```\nDone.';
    const result = parseAssessmentJSON(text);
    expect(result).not.toBeNull();
    expect(result.overall_score).toBe(83);
  });

  it('should extract JSON from mixed text using brace matching', () => {
    const text = 'The assessment: {"completeness":60,"accuracy":55,"depth":50,"examples":45,"overall_score":52,"gaps":["low depth"],"feedback":"Need improvement","mastered":false} end.';
    const result = parseAssessmentJSON(text);
    expect(result).not.toBeNull();
    expect(result.overall_score).toBe(52);
    // mastered should be recalculated: 52 < 75, so false
    expect(result.mastered).toBe(false);
  });

  it('should clamp scores to 0-100', () => {
    const json = JSON.stringify({
      completeness: 150, accuracy: -10, depth: 200, examples: 50,
      overall_score: 120, gaps: [], feedback: 'test',
    });
    // Direct JSON parse won't trigger clamping, only brace-match path does
    // Wrap in text to trigger brace-match path
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
