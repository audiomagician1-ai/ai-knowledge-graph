import { create } from 'zustand';
import { getLLMHeaders } from './settings';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

export interface AssessmentResult {
  completeness: number;
  accuracy: number;
  depth: number;
  examples: number;
  overall_score: number;
  gaps: string[];
  feedback: string;
  mastered: boolean;
}

interface DialogueState {
  conversationId: string | null;
  conceptId: string | null;
  conceptName: string | null;
  isMilestone: boolean;
  messages: ChatMessage[];
  isStreaming: boolean;
  suggestAssess: boolean;
  assessment: AssessmentResult | null;
  error: string | null;

  // Actions
  startConversation: (conceptId: string) => Promise<void>;
  sendMessage: (text: string) => Promise<void>;
  requestAssessment: () => Promise<void>;
  reset: () => void;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

let msgCounter = 0;
function nextId() {
  return `msg-${Date.now()}-${++msgCounter}`;
}

export const useDialogueStore = create<DialogueState>((set, get) => ({
  conversationId: null,
  conceptId: null,
  conceptName: null,
  isMilestone: false,
  messages: [],
  isStreaming: false,
  suggestAssess: false,
  assessment: null,
  error: null,

  startConversation: async (conceptId: string) => {
    set({
      conversationId: null,
      conceptId,
      conceptName: null,
      isMilestone: false,
      messages: [],
      isStreaming: false,
      suggestAssess: false,
      assessment: null,
      error: null,
    });

    try {
      const res = await fetch(`${API_BASE}/dialogue/conversations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ concept_id: conceptId }),
      });

      if (!res.ok) throw new Error('Failed to create conversation');

      const data = await res.json();
      set({
        conversationId: data.conversation_id,
        conceptName: data.concept_name,
        isMilestone: data.is_milestone || false,
        messages: [
          {
            id: nextId(),
            role: 'assistant',
            content: data.opening_message,
            timestamp: Date.now(),
          },
        ],
      });
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Unknown error' });
    }
  },

  sendMessage: async (text: string) => {
    const { conversationId } = get();
    if (!conversationId || get().isStreaming) return;

    // Add user message
    const userMsg: ChatMessage = {
      id: nextId(),
      role: 'user',
      content: text,
      timestamp: Date.now(),
    };

    // Add placeholder for assistant response
    const assistantMsg: ChatMessage = {
      id: nextId(),
      role: 'assistant',
      content: '',
      timestamp: Date.now(),
    };

    set((s) => ({
      messages: [...s.messages, userMsg, assistantMsg],
      isStreaming: true,
      error: null,
    }));

    try {
      const res = await fetch(`${API_BASE}/dialogue/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...getLLMHeaders() },
        body: JSON.stringify({
          conversation_id: conversationId,
          message: text,
        }),
      });

      if (!res.ok) throw new Error('Chat failed');

      const reader = res.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) throw new Error('No response body');

      let buffer = '';
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          try {
            const payload = JSON.parse(line.slice(6));

            if (payload.type === 'chunk') {
              set((s) => {
                const msgs = [...s.messages];
                const last = msgs[msgs.length - 1];
                if (last.role === 'assistant') {
                  msgs[msgs.length - 1] = { ...last, content: last.content + payload.content };
                }
                return { messages: msgs };
              });
            } else if (payload.type === 'done') {
              set({
                isStreaming: false,
                suggestAssess: payload.suggest_assess || false,
              });
            }
          } catch {
            // ignore parse errors
          }
        }
      }

      // Ensure streaming is marked done
      set({ isStreaming: false });
    } catch (err) {
      set({
        isStreaming: false,
        error: err instanceof Error ? err.message : 'Unknown error',
      });
    }
  },

  requestAssessment: async () => {
    const { conversationId } = get();
    if (!conversationId) return;

    set({ isStreaming: true, error: null });

    try {
      const res = await fetch(`${API_BASE}/dialogue/assess`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...getLLMHeaders() },
        body: JSON.stringify({ conversation_id: conversationId }),
      });

      if (!res.ok) throw new Error('Assessment failed');
      const data = await res.json();

      if (data.error) {
        set({ isStreaming: false, error: data.error });
        return;
      }

      set({
        assessment: {
          completeness: data.completeness,
          accuracy: data.accuracy,
          depth: data.depth,
          examples: data.examples,
          overall_score: data.overall_score,
          gaps: data.gaps || [],
          feedback: data.feedback || '',
          mastered: data.mastered || false,
        },
        isStreaming: false,
      });
    } catch (err) {
      set({
        isStreaming: false,
        error: err instanceof Error ? err.message : 'Unknown error',
      });
    }
  },

  reset: () =>
    set({
      conversationId: null,
      conceptId: null,
      conceptName: null,
      isMilestone: false,
      messages: [],
      isStreaming: false,
      suggestAssess: false,
      assessment: null,
      error: null,
    }),
}));