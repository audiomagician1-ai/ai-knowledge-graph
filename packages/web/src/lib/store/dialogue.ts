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
  isAssessing: boolean;
  suggestAssess: boolean;
  assessment: AssessmentResult | null;
  error: string | null;

  // Actions
  startConversation: (conceptId: string) => Promise<void>;
  sendMessage: (text: string) => Promise<void>;
  requestAssessment: () => Promise<void>;
  cancelStream: () => void;
  reset: () => void;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

let msgCounter = 0;
function nextId() {
  return `msg-${Date.now()}-${msgCounter++}-${Math.random().toString(36).slice(2, 6)}`;
}

// Module-level AbortController for SSE cancellation
let _streamAbort: AbortController | null = null;

function abortCurrentStream() {
  if (_streamAbort) {
    _streamAbort.abort();
    _streamAbort = null;
  }
}

/** Process remaining SSE data in buffer after stream ends */
function flushBuffer(buffer: string, handler: (payload: Record<string, unknown>) => void) {
  if (!buffer.trim()) return;
  const lines = buffer.split('\n\n');
  for (const line of lines) {
    if (!line.startsWith('data: ')) continue;
    try {
      handler(JSON.parse(line.slice(6)));
    } catch { /* ignore */ }
  }
}

export const useDialogueStore = create<DialogueState>((set, get) => ({
  conversationId: null,
  conceptId: null,
  conceptName: null,
  isMilestone: false,
  messages: [],
  isStreaming: false,
  isAssessing: false,
  suggestAssess: false,
  assessment: null,
  error: null,

  startConversation: async (conceptId: string) => {
    // Cancel any in-flight SSE stream
    abortCurrentStream();

    set({
      conversationId: null,
      conceptId,
      conceptName: null,
      isMilestone: false,
      messages: [],
      isStreaming: false,
      isAssessing: false,
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
    const { conversationId, isStreaming, isAssessing } = get();
    if (!conversationId || isStreaming || isAssessing) return;

    // Abort any previous stream (safety net)
    abortCurrentStream();

    // Create a new AbortController for this request
    const controller = new AbortController();
    _streamAbort = controller;

    // Capture conversation ID to detect stale callbacks
    const myConvId = conversationId;

    // Add user message
    const userMsg: ChatMessage = {
      id: nextId(),
      role: 'user',
      content: text,
      timestamp: Date.now(),
    };

    // Add placeholder for assistant response
    const assistantMsgId = nextId();
    const assistantMsg: ChatMessage = {
      id: assistantMsgId,
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
        signal: controller.signal,
      });

      if (!res.ok) throw new Error('Chat failed');

      const reader = res.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) throw new Error('No response body');

      const handlePayload = (payload: Record<string, unknown>) => {
        // Guard: ignore if conversation changed
        if (get().conversationId !== myConvId) return;

        if (payload.type === 'chunk') {
          set((s) => {
            const msgs = [...s.messages];
            const idx = msgs.findIndex((m) => m.id === assistantMsgId);
            if (idx >= 0) {
              msgs[idx] = { ...msgs[idx], content: msgs[idx].content + (payload.content as string) };
            }
            return { messages: msgs };
          });
        } else if (payload.type === 'done') {
          set({
            isStreaming: false,
            suggestAssess: (payload.suggest_assess as boolean) || false,
          });
        }
      };

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
            handlePayload(JSON.parse(line.slice(6)));
          } catch { /* ignore parse errors */ }
        }
      }

      // Flush remaining buffer (fix: last SSE frame could be missed)
      flushBuffer(buffer, handlePayload);

      // Ensure streaming is marked done (safety)
      if (get().conversationId === myConvId) {
        set({ isStreaming: false });
      }
    } catch (err) {
      // Ignore AbortError — it's intentional cancellation
      if (err instanceof DOMException && err.name === 'AbortError') {
        return;
      }
      if (get().conversationId === myConvId) {
        set({
          isStreaming: false,
          error: err instanceof Error ? err.message : 'Unknown error',
        });
      }
    } finally {
      if (_streamAbort === controller) {
        _streamAbort = null;
      }
    }
  },

  requestAssessment: async () => {
    const { conversationId, isStreaming, isAssessing } = get();
    if (!conversationId || isStreaming || isAssessing) return;

    set({ isAssessing: true, error: null });

    try {
      const res = await fetch(`${API_BASE}/dialogue/assess`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...getLLMHeaders() },
        body: JSON.stringify({ conversation_id: conversationId }),
      });

      if (!res.ok) throw new Error('Assessment failed');
      const data = await res.json();

      if (data.error) {
        set({ isAssessing: false, error: data.error });
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
        isAssessing: false,
      });
    } catch (err) {
      set({
        isAssessing: false,
        error: err instanceof Error ? err.message : 'Unknown error',
      });
    }
  },

  cancelStream: () => {
    abortCurrentStream();
    set({ isStreaming: false });
  },

  reset: () => {
    abortCurrentStream();
    set({
      conversationId: null,
      conceptId: null,
      conceptName: null,
      isMilestone: false,
      messages: [],
      isStreaming: false,
      isAssessing: false,
      suggestAssess: false,
      assessment: null,
      error: null,
    });
  },
}));