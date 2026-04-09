import { useEffect, useRef, useState } from 'react';
import { createLogger } from '@/lib/utils/logger';
import { useParams } from 'react-router-dom';
import { useDialogueStore } from '@/lib/store/dialogue';
import { useLearningStore } from '@/lib/store/learning';
import { useAchievementStore } from '@/lib/store/achievements';
import { AlertTriangle } from 'lucide-react';
import { LearnAssessmentCard } from '@/components/chat/LearnAssessmentCard';
import { useLearningTimer } from '@/lib/hooks/useLearningTimer';
import { useSpeechRecognition, detectLanguage } from '@/lib/hooks/useSpeechRecognition';
import { LearnHeader } from '@/components/learn/LearnHeader';
import { LearnMessageBubble } from '@/components/learn/LearnMessageBubble';
import { LearnPostAssessment } from '@/components/learn/LearnPostAssessment';
import { LearnGuideCard, LearnLoadingIndicator } from '@/components/learn/LearnGuideCard';
import { LearnInputArea } from '@/components/learn/LearnInputArea';

const log = createLogger('LearnPage');

export function LearnPage() {
  const { conceptId, domainId } = useParams<{ conceptId: string; domainId: string }>();
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Track learning time while this page is active
  useLearningTimer();

  const {
    conversationId, conceptName, isMilestone,
    messages, isStreaming, isAssessing, isInitializing, suggestAssess, assessment, error,
    currentChoices,
    startConversation, sendMessage, selectChoice, requestAssessment, cancelStream, reset,
  } = useDialogueStore();

  const isBusy = isStreaming || isAssessing;
  const { startLearning, recordAssessment, recommendedIds } = useLearningStore();
  const { checkNewAchievements } = useAchievementStore();
  const recordedRef = useRef(false);

  // Voice input (Web Speech API)
  const voice = useSpeechRecognition('zh-CN', true); // continuous mode

  // Sync voice transcript into input field
  useEffect(() => {
    if (voice.transcript) {
      setInput((prev) => prev + voice.transcript);
      voice.resetTranscript();
    }
  }, [voice.transcript]);

  // Auto-detect language from user's recent messages
  useEffect(() => {
    if (messages.length < 2) return;
    const userMessages = messages.filter((m) => m.role === 'user').slice(-3);
    if (userMessages.length === 0) return;
    const recentText = userMessages.map((m) => m.content).join(' ');
    const detected = detectLanguage(recentText);
    if (detected !== voice.currentLang) {
      voice.switchLanguage(detected);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [messages.length]);

  useEffect(() => {
    if (conceptId) {
      startConversation(conceptId, domainId);
      startLearning(conceptId);
    }
    // M-01: Cancel active stream before reset to prevent stale callbacks
    return () => { cancelStream(); reset(); };
  }, [conceptId]);

  // M-02: Prevent duplicate recording if assessment object is re-created
  useEffect(() => {
    if (assessment && conceptId && !recordedRef.current) {
      recordedRef.current = true;
      recordAssessment(conceptId, conceptName || conceptId, assessment.overall_score, assessment.mastered);
      // Check for newly unlocked achievements after assessment
      checkNewAchievements();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [assessment, conceptId]);

  // Reset recorded flag when concept changes (new learning session)
  useEffect(() => {
    recordedRef.current = false;
  }, [conceptId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, assessment, currentChoices]);

  // Auto-dismiss error after 6 seconds
  useEffect(() => {
    if (!error) return;
    const timer = setTimeout(() => useDialogueStore.setState({ error: null }), 6000);
    return () => clearTimeout(timer);
  }, [error]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || isBusy) return;
    setInput('');
    await sendMessage(text);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const userTurns = messages.filter((m) => m.role === 'user').length;

  return (
    <div className="flex h-dvh" style={{ backgroundColor: 'var(--color-surface-0)' }}>

      {/* ── Main chat area ── */}
      <div className="flex-1 flex flex-col min-w-0">

        <LearnHeader
          conceptId={conceptId}
          domainId={domainId}
          conceptName={conceptName}
          isMilestone={isMilestone}
          userTurns={userTurns}
          suggestAssess={suggestAssess}
          assessment={assessment}
          isBusy={isBusy}
          isAssessing={isAssessing}
          onRequestAssessment={requestAssessment}
        />

        {/* Messages area */}
        <div className="flex-1 overflow-y-auto" style={{ backgroundColor: 'var(--color-surface-2)' }}>
            <div className="max-w-3xl mx-auto" style={{ padding: '32px 28px', display: 'flex', flexDirection: 'column', gap: 24 }}>

            <LearnGuideCard />

            {isInitializing && <LearnLoadingIndicator />}

            {messages.map((msg, idx) => (
              <LearnMessageBubble
                key={msg.id}
                msg={msg}
                idx={idx}
                isStreaming={isStreaming}
                conceptId={conceptId}
                domainId={domainId}
              />
            ))}

            {/* Assessment result */}
            {assessment && <LearnAssessmentCard result={assessment} conceptName={conceptName || ''} />}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {!assessment ? (
          <LearnInputArea
            input={input}
            setInput={setInput}
            onSend={handleSend}
            onKeyDown={handleKeyDown}
            isBusy={isBusy}
            conversationId={conversationId}
            currentChoices={currentChoices}
            onSelectChoice={selectChoice}
            voice={voice}
          />
        ) : (
          <LearnPostAssessment
            conceptId={conceptId}
            domainId={domainId}
            conceptName={conceptName}
            assessment={assessment}
            recommendedIds={recommendedIds}
            onRestart={() => { recordedRef.current = false; reset(); if (conceptId) { startConversation(conceptId, domainId); startLearning(conceptId); } }}
          />
        )}
      </div>

      {/* Error toast */}
      {error && (
        <div
          className="fixed top-4 left-1/2 -translate-x-1/2 z-50 glass-heavy rounded-xl px-5 py-3 flex items-center gap-3 animate-fade-in"
          style={{ maxWidth: 480 }}
        >
          <AlertTriangle size={16} style={{ color: 'var(--color-accent-rose)' }} />
          <span className="text-sm" style={{ color: 'var(--color-accent-rose)' }}>{error}</span>
        </div>
      )}
    </div>
  );
}


