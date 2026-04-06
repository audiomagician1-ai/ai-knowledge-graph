import { useCallback, useEffect, useRef, useState } from 'react';
import { createLogger } from '@/lib/utils/logger';

const log = createLogger('SpeechRecognition');

/** Supported languages for speech recognition */
export const SPEECH_LANGUAGES = [
  { code: 'zh-CN', label: '中文', flag: '🇨🇳' },
  { code: 'en-US', label: 'English', flag: '🇺🇸' },
  { code: 'ja-JP', label: '日本語', flag: '🇯🇵' },
  { code: 'ko-KR', label: '한국어', flag: '🇰🇷' },
  { code: 'de-DE', label: 'Deutsch', flag: '🇩🇪' },
  { code: 'fr-FR', label: 'Français', flag: '🇫🇷' },
  { code: 'es-ES', label: 'Español', flag: '🇪🇸' },
] as const;

export type SpeechLangCode = (typeof SPEECH_LANGUAGES)[number]['code'];

/**
 * Web Speech API hook for voice-to-text input.
 * Falls back gracefully when unsupported (returns isSupported=false).
 *
 * @param lang - BCP-47 language tag (default: 'zh-CN')
 * @param continuous - keep listening after pause (default: false)
 */
export function useSpeechRecognition(lang: SpeechLangCode = 'zh-CN', continuous = false) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [currentLang, setCurrentLang] = useState<SpeechLangCode>(lang);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  const isSupported =
    typeof window !== 'undefined' &&
    ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window);

  // Initialize recognition instance (rebuilds on lang/continuous change)
  useEffect(() => {
    if (!isSupported) return;

    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = currentLang;
    recognition.continuous = continuous;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let interim = '';
      let final = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          final += result[0].transcript;
        } else {
          interim += result[0].transcript;
        }
      }
      if (final) {
        setTranscript((prev) => prev + final);
        setInterimTranscript('');
      } else {
        setInterimTranscript(interim);
      }
    };

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      log.warn('Speech recognition error', { error: event.error });
      if (event.error === 'not-allowed') {
        setError('麦克风权限被拒绝，请在浏览器设置中允许麦克风访问');
      } else if (event.error === 'no-speech') {
        setError('未检测到语音，请对着麦克风说话');
      } else if (event.error === 'aborted') {
        // Silently handle abort (e.g. from language switch)
        setError(null);
      } else {
        setError(`语音识别错误: ${event.error}`);
      }
      setIsListening(false);
    };

    recognition.onend = () => {
      // In continuous mode, auto-restart if still supposed to be listening
      if (continuous && isListening) {
        try {
          recognition.start();
          return;
        } catch {
          // fall through to stop
        }
      }
      setIsListening(false);
    };

    recognitionRef.current = recognition;

    return () => {
      recognition.abort();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isSupported, currentLang, continuous]);

  const startListening = useCallback(() => {
    if (!recognitionRef.current || isListening) return;
    setError(null);
    setInterimTranscript('');
    try {
      recognitionRef.current.start();
      setIsListening(true);
      log.info('Voice recognition started', { lang: currentLang, continuous });
    } catch (e) {
      log.error('Failed to start recognition', { err: String(e) });
      setError('无法启动语音识别');
    }
  }, [isListening, currentLang, continuous]);

  const stopListening = useCallback(() => {
    if (!recognitionRef.current || !isListening) return;
    recognitionRef.current.stop();
    setIsListening(false);
    log.info('Voice recognition stopped');
  }, [isListening]);

  const toggleListening = useCallback(() => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  }, [isListening, startListening, stopListening]);

  /** Reset accumulated transcript */
  const resetTranscript = useCallback(() => {
    setTranscript('');
    setInterimTranscript('');
  }, []);

  /** Switch recognition language (stops current session if active) */
  const switchLanguage = useCallback(
    (newLang: SpeechLangCode) => {
      if (newLang === currentLang) return;
      if (isListening && recognitionRef.current) {
        recognitionRef.current.abort();
        setIsListening(false);
      }
      setCurrentLang(newLang);
      log.info('Language switched', { from: currentLang, to: newLang });
    },
    [currentLang, isListening]
  );

  return {
    isSupported,
    isListening,
    transcript,
    interimTranscript,
    error,
    currentLang,
    startListening,
    stopListening,
    toggleListening,
    resetTranscript,
    switchLanguage,
    languages: SPEECH_LANGUAGES,
  };
}
