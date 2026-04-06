import { useCallback, useEffect, useRef, useState } from 'react';
import { createLogger } from '@/lib/utils/logger';

const log = createLogger('SpeechRecognition');

/**
 * Web Speech API hook for voice-to-text input.
 * Falls back gracefully when unsupported (returns isSupported=false).
 *
 * @param lang - BCP-47 language tag (default: 'zh-CN')
 * @param continuous - keep listening after pause (default: false)
 */
export function useSpeechRecognition(lang = 'zh-CN', continuous = false) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  const isSupported =
    typeof window !== 'undefined' &&
    ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window);

  // Initialize recognition instance
  useEffect(() => {
    if (!isSupported) return;

    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = lang;
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
      } else {
        setError(`语音识别错误: ${event.error}`);
      }
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;

    return () => {
      recognition.abort();
    };
  }, [isSupported, lang, continuous]);

  const startListening = useCallback(() => {
    if (!recognitionRef.current || isListening) return;
    setError(null);
    setInterimTranscript('');
    try {
      recognitionRef.current.start();
      setIsListening(true);
      log.info('Voice recognition started');
    } catch (e) {
      log.error('Failed to start recognition', { err: String(e) });
      setError('无法启动语音识别');
    }
  }, [isListening]);

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

  return {
    isSupported,
    isListening,
    transcript,
    interimTranscript,
    error,
    startListening,
    stopListening,
    toggleListening,
    resetTranscript,
  };
}
