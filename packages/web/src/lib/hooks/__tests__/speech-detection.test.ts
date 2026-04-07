/**
 * Tests for speech recognition language auto-detection.
 */
import { describe, it, expect } from 'vitest';
import { detectLanguage } from '../useSpeechRecognition';

describe('detectLanguage — CJK scripts', () => {
  it('should detect Chinese (zh-CN) from Mandarin text', () => {
    expect(detectLanguage('我想学习编程')).toBe('zh-CN');
    expect(detectLanguage('这个概念很有意思')).toBe('zh-CN');
  });

  it('should detect Japanese (ja-JP) from hiragana/katakana', () => {
    expect(detectLanguage('プログラミングを学びたい')).toBe('ja-JP');
    expect(detectLanguage('これはとても面白いです')).toBe('ja-JP');
  });

  it('should detect Korean (ko-KR) from hangul', () => {
    expect(detectLanguage('프로그래밍을 배우고 싶습니다')).toBe('ko-KR');
    expect(detectLanguage('안녕하세요 세계')).toBe('ko-KR');
  });
});

describe('detectLanguage — Latin scripts', () => {
  it('should detect English (en-US) from plain English', () => {
    expect(detectLanguage('I want to learn about recursion')).toBe('en-US');
    expect(detectLanguage('How does this algorithm work')).toBe('en-US');
  });

  it('should detect German (de-DE) from German markers', () => {
    expect(detectLanguage('Das ist ein sehr guter Algorithmus')).toBe('de-DE');
    expect(detectLanguage('Ich möchte nicht aufhören zu lernen')).toBe('de-DE');
  });

  it('should detect French (fr-FR) from French markers', () => {
    expect(detectLanguage('Les algorithmes sont très utiles pour les données')).toBe('fr-FR');
    expect(detectLanguage('Que pensez-vous de cette approche')).toBe('fr-FR');
  });

  it('should detect Spanish (es-ES) from Spanish markers', () => {
    expect(detectLanguage('Los algoritmos son muy útiles para los datos')).toBe('es-ES');
    expect(detectLanguage('Qué piensas del problema con más datos también')).toBe('es-ES');
  });
});

describe('detectLanguage — edge cases', () => {
  it('should return zh-CN for empty/short text', () => {
    expect(detectLanguage('')).toBe('zh-CN');
    expect(detectLanguage('a')).toBe('zh-CN');
  });

  it('should return en-US for numbers/symbols only', () => {
    expect(detectLanguage('12345 @#$%')).toBe('en-US');
  });

  it('should handle mixed CJK + Latin (CJK dominant)', () => {
    expect(detectLanguage('我正在学习Python编程语言')).toBe('zh-CN');
  });
});
