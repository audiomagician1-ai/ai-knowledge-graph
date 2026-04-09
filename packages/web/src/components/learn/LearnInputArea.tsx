import { Send, Mic, MicOff } from 'lucide-react';
import { ChoiceButtons } from '@/components/chat/ChoiceButtons';
import type { ChoiceOption } from '@/lib/store/dialogue';
import { SPEECH_LANGUAGES, type SpeechLangCode } from '@/lib/hooks/useSpeechRecognition';

interface VoiceState {
  isSupported: boolean;
  isListening: boolean;
  interimTranscript: string;
  currentLang: SpeechLangCode;
  toggleListening: () => void;
  switchLanguage: (lang: SpeechLangCode) => void;
}

interface LearnInputAreaProps {
  input: string;
  setInput: (v: string) => void;
  onSend: () => void;
  onKeyDown: (e: React.KeyboardEvent) => void;
  isBusy: boolean;
  conversationId: string | null;
  currentChoices: ChoiceOption[] | null;
  onSelectChoice: (choiceId: string) => void;
  voice: VoiceState;
}

export function LearnInputArea({
  input, setInput, onSend, onKeyDown, isBusy,
  conversationId, currentChoices, onSelectChoice, voice,
}: LearnInputAreaProps) {
  const isUserTyping = input.length > 0;

  return (
    <div
      className="shrink-0 border-t"
      style={{
        backgroundColor: 'var(--color-surface-1)',
        borderColor: 'var(--color-border)',
        paddingBottom: 'env(safe-area-inset-bottom, 0px)',
      }}
    >
      <div className="max-w-3xl mx-auto px-8 py-5 space-y-4">
        {currentChoices && currentChoices.length > 0 && !isBusy && (
          <ChoiceButtons
            choices={currentChoices}
            onSelect={onSelectChoice}
            disabled={isBusy}
            dimmed={isUserTyping}
          />
        )}

        <div
          className="flex items-end gap-3 rounded-xl px-5 py-4 transition-all"
          style={{
            backgroundColor: 'var(--color-surface-2)',
            border: '1px solid rgba(0, 0, 0, 0.12)',
          }}
        >
          <textarea
            value={input + (voice.interimTranscript ? voice.interimTranscript : '')}
            onChange={(e) => {
              setInput(e.target.value);
              e.target.style.height = 'auto';
              e.target.style.height = Math.min(e.target.scrollHeight, 150) + 'px';
            }}
            onKeyDown={onKeyDown}
            placeholder={currentChoices ? "也可以用自己的话回答..." : "用你自己的话解释这个概念..."}
            rows={3}
            aria-label="输入你的回答"
            className="flex-1 bg-transparent text-[14px] outline-none resize-none leading-relaxed"
            style={{
              color: 'var(--color-text-primary)',
              minHeight: '4.5em',
              maxHeight: '150px',
            }}
            disabled={isBusy || !conversationId}
          />
          {voice.isSupported && (
            <div className="flex items-center gap-1 shrink-0">
              {voice.isListening && (
                <select
                  value={voice.currentLang}
                  onChange={(e) => voice.switchLanguage(e.target.value as SpeechLangCode)}
                  className="text-[10px] bg-transparent rounded px-1 py-0.5 outline-none"
                  style={{ color: 'var(--color-text-tertiary)', border: '1px solid var(--color-border)', maxWidth: 60 }}
                  title="切换语音识别语言"
                >
                  {SPEECH_LANGUAGES.map((l) => (
                    <option key={l.code} value={l.code}>{l.flag} {l.label}</option>
                  ))}
                </select>
              )}
              <button
                onClick={voice.toggleListening}
                disabled={isBusy || !conversationId}
                aria-label={voice.isListening ? '停止语音输入' : '开始语音输入'}
                title={voice.isListening ? '点击停止录音' : '点击语音输入'}
                className="shrink-0 w-9 h-9 rounded-md flex items-center justify-center transition-all"
                style={{
                  background: voice.isListening ? '#ef4444' : 'var(--color-surface-3)',
                  color: voice.isListening ? '#ffffff' : 'var(--color-text-secondary)',
                  opacity: isBusy ? 0.4 : 1,
                  animation: voice.isListening ? 'pulse 1.5s ease-in-out infinite' : 'none',
                }}
              >
                {voice.isListening ? <MicOff size={16} /> : <Mic size={16} />}
              </button>
            </div>
          )}
          <button
            onClick={onSend}
            disabled={isBusy || !input.trim() || !conversationId}
            aria-label="发送消息"
            className="shrink-0 w-9 h-9 rounded-md flex items-center justify-center transition-all"
            style={{
              background: !input.trim() || isBusy ? 'var(--color-surface-3)' : 'var(--color-accent-primary)',
              color: '#ffffff',
              opacity: !input.trim() || isBusy ? 0.4 : 1,
            }}
          >
            <Send size={16} />
          </button>
        </div>
        <p className="text-[11px] mt-2 text-center font-mono" style={{ color: 'var(--color-text-tertiary)' }}>
          {currentChoices ? '点选上方选项或自由输入 · Enter 发送' : 'Enter 发送 · Shift+Enter 换行 · 对话 4 轮后可评估理解度'}
        </p>
      </div>
    </div>
  );
}
