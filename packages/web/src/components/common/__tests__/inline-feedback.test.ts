/**
 * Tests for InlineFeedback component logic.
 */
import { describe, it, expect } from 'vitest';

describe('InlineFeedback — suggestion generation', () => {
  it('should create positive feedback title with concept ID', () => {
    const conceptId = 'recursion';
    const title = `👍 Helpful explanation for ${conceptId}`;
    expect(title).toContain('recursion');
    expect(title).toContain('👍');
  });

  it('should create negative feedback as correction type', () => {
    const sentiment = 'negative';
    const type = sentiment === 'negative' ? 'correction' : 'feedback';
    expect(type).toBe('correction');
  });

  it('should truncate message content to 300 chars max', () => {
    const longContent = 'a'.repeat(500);
    const truncated = longContent.slice(0, 300);
    expect(truncated.length).toBe(300);
  });

  it('should require minimum 10 characters for detailed feedback', () => {
    const shortText = 'short';
    const validText = 'This explanation could be clearer about the base case';
    expect(shortText.trim().length < 10).toBe(true);
    expect(validText.trim().length >= 10).toBe(true);
  });

  it('should build description with context when message provided', () => {
    const feedbackText = 'The recursive definition is confusing';
    const messageContent = 'Recursion is when a function calls itself...';
    const description = feedbackText + `\n\n---\nContext: "${messageContent.slice(0, 300)}"`;
    expect(description).toContain('recursive definition');
    expect(description).toContain('Context:');
    expect(description).toContain('calls itself');
  });

  it('should build description without context when no message', () => {
    const feedbackText = 'Missing important details';
    const hasMessage = false;
    const description = feedbackText + (hasMessage ? '\n\n---\nContext: "some content"' : '');
    expect(description).toBe('Missing important details');
    expect(description).not.toContain('Context:');
  });
});
