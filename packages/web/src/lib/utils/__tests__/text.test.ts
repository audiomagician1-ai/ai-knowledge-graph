import { describe, it, expect } from 'vitest';
import { stripChoicesBlock } from '../text';

describe('stripChoicesBlock', () => {
  it('should strip complete choices block', () => {
    const text = 'Hello world\n```choices\n[{"id":"opt-1","text":"A","type":"explore"}]\n```';
    expect(stripChoicesBlock(text)).toBe('Hello world');
  });

  it('should strip incomplete/in-progress choices block', () => {
    const text = 'Hello world\n```choices\n[{"id":"opt-1"';
    expect(stripChoicesBlock(text)).toBe('Hello world');
  });

  it('should return original text when no choices block', () => {
    const text = 'Just regular content here';
    expect(stripChoicesBlock(text)).toBe('Just regular content here');
  });

  it('should handle empty string', () => {
    expect(stripChoicesBlock('')).toBe('');
  });

  it('should trim whitespace after stripping', () => {
    const text = '  Hello world  \n```choices\n[]\n```\n  ';
    expect(stripChoicesBlock(text)).toBe('Hello world');
  });
});
