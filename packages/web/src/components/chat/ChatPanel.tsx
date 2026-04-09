import { useEffect, useRef, useState } from 'react';
import { useDialogueStore } from '@/lib/store/dialogue';
import { useLearningStore } from '@/lib/store/learning';
import { useAchievementStore } from '@/lib/store/achievements';
import type { ConceptProgress } from '@/lib/store/learning';
import { ChatHistoryView } from './ChatHistoryView';
import { ChatIdleView } from './ChatIdleView';
import { ChatView } from './ChatView';
import { useNavigate, useParams } from 'react-router-dom';

interface ChatPanelProps {
  conceptId: string;
  conceptName: string;
  domainId?: string;
}

type PanelView = 'idle' | 'chat' | 'history';

export function ChatPanel({ conceptId, conceptName, domainId }: ChatPanelProps) {
  const [input, setInput] = useState('');
  const [view, setView] = useState<PanelView>('idle');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const prevConceptRef = useRef<string | null>(null);
  const navigate = useNavigate();
  const { domainId: urlDomainId } = useParams<{ domainId: string }>();

  const {
    conversationId, messages, isStreaming, isAssessing, isInitializing, suggestAssess, assessment, error,
    currentChoices,
    startConversation, sendMessage, selectChoice, requestAssessment, cancelStream, reset,
    savedConversations, loadSavedConversation, deleteSavedConversation,
  } = useDialogueStore();

  const isBusy = isStreaming || isAssessing;
  const { progress, startLearning, recordAssessment, newlyUnlockedIds } = useLearningStore();
  const { checkNewAchievements } = useAchievementStore();
  const [showCelebration, setShowCelebration] = useState(false);
  const recordedConvRef = useRef<string | null>(null);

  useEffect(() => { return () => { cancelStream(); reset(); }; }, []);

  useEffect(() => {
    if (conceptId && conceptId !== prevConceptRef.current) {
      prevConceptRef.current = conceptId;
      recordedConvRef.current = null;
      reset(); setView('idle'); setInput('');
    }
  }, [conceptId]);

  useEffect(() => {
    if (assessment && conceptId && conversationId && recordedConvRef.current !== conversationId) {
      recordedConvRef.current = conversationId;
      recordAssessment(conceptId, conceptName || conceptId, assessment.overall_score, assessment.mastered);
      checkNewAchievements();
      if (assessment.mastered) {
        setShowCelebration(true);
        const timer = setTimeout(() => setShowCelebration(false), 4000);
        return () => clearTimeout(timer);
      }
    }
  }, [assessment, conversationId]);

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, assessment, currentChoices]);

  useEffect(() => {
    if (!error) return;
    const timer = setTimeout(() => useDialogueStore.setState({ error: null }), 6000);
    return () => clearTimeout(timer);
  }, [error]);

  const handleStartLearning = () => { startConversation(conceptId, domainId); startLearning(conceptId); setView('chat'); };
  const handleSend = async () => { const text = input.trim(); if (!text || isBusy) return; setInput(''); await sendMessage(text); };

  const userTurns = messages.filter((m) => m.role === 'user').length;
  const conceptConvHistory = savedConversations.filter(c => c.conceptId === conceptId).sort((a, b) => b.updatedAt - a.updatedAt);
  const nodeProgress: ConceptProgress | null = progress[conceptId] || null;
  const handleConceptClick = (id: string) => navigate(`/domain/${urlDomainId || domainId}/${id}`);

  if (view === 'history') {
    return (
      <ChatHistoryView conceptName={conceptName} conversations={conceptConvHistory}
        onClose={() => setView('idle')} onLoad={(id) => { loadSavedConversation(id); setView('chat'); }} onDelete={deleteSavedConversation} />
    );
  }

  if (view === 'idle') {
    return (
      <ChatIdleView conceptId={conceptId} conceptName={conceptName} domainId={domainId} urlDomainId={urlDomainId}
        nodeProgress={nodeProgress} conversations={conceptConvHistory}
        onStartLearning={handleStartLearning} onViewHistory={() => setView('history')}
        onLoadConversation={(id) => { loadSavedConversation(id); setView('chat'); }} onConceptClick={handleConceptClick} />
    );
  }

  return (
    <>
      <ChatView
        conceptName={conceptName} messages={messages}
        isStreaming={isStreaming} isAssessing={isAssessing} isInitializing={isInitializing} isBusy={isBusy}
        suggestAssess={suggestAssess} assessment={assessment} currentChoices={currentChoices} conversationId={conversationId}
        input={input} userTurns={userTurns} showCelebration={showCelebration} newlyUnlockedIds={newlyUnlockedIds}
        messagesEndRef={messagesEndRef}
        onInputChange={setInput} onSend={handleSend} onRequestAssessment={requestAssessment} onSelectChoice={selectChoice}
        onViewHistory={() => setView('history')} onBack={() => setView('idle')} onRestart={() => { reset(); handleStartLearning(); }}
      />
      {error && (
        <div className="absolute bottom-24 left-5 right-5 z-50 rounded-xl px-4 py-3 text-sm animate-fade-in"
          style={{ backgroundColor: 'rgba(244,63,94,0.12)', color: 'var(--color-accent-rose)', border: '1px solid rgba(244,63,94,0.2)' }}>
          {error}
        </div>
      )}
    </>
  );
}
