import { create } from 'zustand';
import { getLLMHeaders, useSettingsStore } from './settings';
import { directCreateConversation, directChatStream, directAssess, clearDirectConversation } from '../direct-llm';
import { syncConversationToCloud } from './supabase-sync';

export interface ChoiceOption {
  id: string;
  text: string;
  type: 'explore' | 'answer' | 'action' | 'level';
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  isChoice?: boolean;  // true if user clicked a preset choice
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

/** Saved conversation record for history browsing */
export interface SavedConversation {
  conversationId: string;
  conceptId: string;
  conceptName: string;
  messages: ChatMessage[];
  assessment: AssessmentResult | null;
  createdAt: number;
  updatedAt: number;
}

interface DialogueState {
  conversationId: string | null;
  conceptId: string | null;
  conceptName: string | null;
  isMilestone: boolean;
  messages: ChatMessage[];
  isStreaming: boolean;
  isAssessing: boolean;
  isInitializing: boolean;
  suggestAssess: boolean;
  assessment: AssessmentResult | null;
  error: string | null;

  /** V2: Current choices offered by AI */
  currentChoices: ChoiceOption[] | null;

  /** Persisted conversation history */
  savedConversations: SavedConversation[];

  // Actions
  startConversation: (conceptId: string, domainId?: string) => Promise<void>;
  sendMessage: (text: string, isChoice?: boolean) => Promise<void>;
  selectChoice: (choiceId: string) => Promise<void>;
  requestAssessment: () => Promise<void>;
  cancelStream: () => void;
  reset: () => void;
  /** Load a saved conversation into current state for viewing */
  loadSavedConversation: (convId: string) => void;
  /** Delete a saved conversation */
  deleteSavedConversation: (convId: string) => void;
  /** Import saved conversations from external data (merge) */
  importConversations: (convs: SavedConversation[]) => { imported: number };
  /** Replace all saved conversations */
  replaceConversations: (convs: SavedConversation[]) => void;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';
const CONV_HISTORY_KEY = 'akg-conversation-history';

function loadSavedConversations(): SavedConversation[] {
  try {
    const raw = localStorage.getItem(CONV_HISTORY_KEY);
    if (raw) return JSON.parse(raw);
  } catch { /* ignore */ }
  return [];
}

function persistConversations(convs: SavedConversation[]) {
  try {
    // Keep last 50 conversations
    const trimmed = convs.slice(-50);
    localStorage.setItem(CONV_HISTORY_KEY, JSON.stringify(trimmed));
  } catch { /* ignore */ }
}

/** Auto-save current conversation to history */
function autoSaveConversation(state: DialogueState) {
  if (!state.conversationId || !state.conceptId || state.messages.length < 2) return;
  const existing = state.savedConversations;
  const idx = existing.findIndex(c => c.conversationId === state.conversationId);
  const record: SavedConversation = {
    conversationId: state.conversationId,
    conceptId: state.conceptId,
    conceptName: state.conceptName || state.conceptId,
    messages: [...state.messages],
    assessment: state.assessment,
    createdAt: idx >= 0 ? existing[idx].createdAt : Date.now(),
    updatedAt: Date.now(),
  };
  const updated = idx >= 0
    ? existing.map((c, i) => i === idx ? record : c)
    : [...existing, record];
  persistConversations(updated);

  // Async sync to Supabase cloud (fire-and-forget, logged-in only)
  syncConversationToCloud(
    record.conversationId,
    record.conceptId,
    record.messages.map(m => ({ role: m.role, content: m.content, timestamp: m.timestamp })),
    record.assessment ? 'completed' : 'active',
  );

  return updated;
}

let msgCounter = 0;
function nextId() {
  return `msg-${Date.now()}-${msgCounter++}-${Math.random().toString(36).slice(2, 6)}`;
}

/** Extract user-friendly error message from a failed HTTP response.
 *  Backend returns { detail: "...", ... } with a Chinese-language message for 429/400/etc. */
async function extractErrorDetail(res: Response, fallback: string): Promise<string> {
  try {
    const body = await res.json();
    if (typeof body.detail === 'string') return body.detail;
  } catch { /* ignore parse errors */ }
  return fallback;
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
  isInitializing: false,
  suggestAssess: false,
  assessment: null,
  error: null,
  currentChoices: null,
  savedConversations: loadSavedConversations(),

  startConversation: async (conceptId: string, domainId?: string) => {
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
      isInitializing: true,
      suggestAssess: false,
      assessment: null,
      error: null,
      currentChoices: null,
    });

    const isDirect = useSettingsStore.getState().isDirectMode();

    try {
      let data: any;

      if (isDirect) {
        // Direct mode: create conversation with LLM-generated opening
        const result = await directCreateConversation(conceptId);
        if (!result) throw new Error(`概念不存在: ${conceptId}`);
        data = result;
      } else {
        // Proxy mode: create via backend API
        const res = await fetch(`${API_BASE}/dialogue/conversations`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', ...getLLMHeaders() },
          body: JSON.stringify({ concept_id: conceptId, domain_id: domainId || 'ai-engineering' }),
        });
        if (!res.ok) throw new Error(await extractErrorDetail(res, `创建对话失败 (${res.status})`));
        data = await res.json();
      }

      // Simulate streaming for the opening message to give a smooth typing effect
      const openingMsgId = nextId();
      set({
        isInitializing: false,
        conversationId: data.conversation_id,
        conceptName: data.concept_name,
        isMilestone: data.is_milestone || false,
        messages: [
          {
            id: openingMsgId,
            role: 'assistant',
            content: '',
            timestamp: Date.now(),
          },
        ],
        isStreaming: true,
        currentChoices: null,
      });

      // Reveal opening message progressively (simulate streaming)
      const fullText = data.opening_message || '';
      const myConvId = data.conversation_id;
      const CHUNK_SIZE = 3; // characters per tick
      const TICK_MS = 18;   // milliseconds between ticks
      let offset = 0;
      await new Promise<void>((resolve) => {
        const timer = setInterval(() => {
          // Stop if conversation changed
          if (get().conversationId !== myConvId) {
            clearInterval(timer);
            resolve();
            return;
          }
          offset = Math.min(offset + CHUNK_SIZE, fullText.length);
          set((s) => {
            const msgs = [...s.messages];
            const idx = msgs.findIndex((m) => m.id === openingMsgId);
            if (idx >= 0) {
              msgs[idx] = { ...msgs[idx], content: fullText.slice(0, offset) };
            }
            return { messages: msgs };
          });
          if (offset >= fullText.length) {
            clearInterval(timer);
            resolve();
          }
        }, TICK_MS);
      });

      // Streaming done — reveal choices
      if (get().conversationId === myConvId) {
        set({
          isStreaming: false,
          currentChoices: data.opening_choices || null,
        });
      }
    } catch (err) {
      set({ isInitializing: false, isStreaming: false, error: err instanceof Error ? err.message : 'Unknown error' });
    }
  },

  sendMessage: async (text: string, isChoice = false) => {
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
      currentChoices: null,  // Clear choices when user sends
    }));

    try {
      const isDirect = useSettingsStore.getState().isDirectMode();
      let reader: ReadableStreamDefaultReader<Uint8Array> | undefined;

      if (isDirect) {
        // Direct mode: stream from browser → LLM
        const stream = directChatStream(conversationId, text, controller.signal);
        reader = stream.getReader();
      } else {
        // Proxy mode: stream via Worker
        const res = await fetch(`${API_BASE}/dialogue/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', ...getLLMHeaders() },
          body: JSON.stringify({
            conversation_id: conversationId,
            message: text,
            is_choice: isChoice,
          }),
          signal: controller.signal,
        });
        if (!res.ok) throw new Error(await extractErrorDetail(res, `发送消息失败 (${res.status})`));
        reader = res.body?.getReader();
      }
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
        } else if (payload.type === 'choices') {
          set({
            currentChoices: (payload.choices as ChoiceOption[]) || null,
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

      // Ensure streaming is marked done + auto-save (single set() to avoid double re-render)
      if (get().conversationId === myConvId) {
        set({ isStreaming: false });
        // Read updated state after isStreaming is set, then save+set in one go
        const saved = autoSaveConversation(get());
        if (saved) set({ savedConversations: saved });
      }
    } catch (err) {
      // Ignore AbortError — it's intentional cancellation
      if (err instanceof DOMException && err.name === 'AbortError') {
        // Reset isStreaming + remove empty assistant placeholder to prevent blank bubbles
        if (get().conversationId === myConvId) {
          set((s) => ({
            isStreaming: false,
            messages: s.messages.filter(m => !(m.id === assistantMsgId && m.content === '')),
          }));
        }
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

    // Capture conversation ID for stale guard
    const myConvId = conversationId;
    set({ isAssessing: true, error: null });

    try {
      const isDirect = useSettingsStore.getState().isDirectMode();
      let data: any;

      if (isDirect) {
        data = await directAssess(conversationId);
      } else {
        const res = await fetch(`${API_BASE}/dialogue/assess`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', ...getLLMHeaders() },
          body: JSON.stringify({ conversation_id: conversationId }),
        });
        if (!res.ok) throw new Error(await extractErrorDetail(res, `评估请求失败 (${res.status})`));
        data = await res.json();
      }

      // Stale guard: ignore if conversation changed during assessment
      if (get().conversationId !== myConvId) return;

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
      // Auto-save after assessment
      const saved = autoSaveConversation(get());
      if (saved) set({ savedConversations: saved });
    } catch (err) {
      // Stale guard
      if (get().conversationId !== myConvId) return;
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

  selectChoice: async (choiceId: string) => {
    const { currentChoices, sendMessage } = get();
    if (!currentChoices) return;
    const choice = currentChoices.find(c => c.id === choiceId);
    if (!choice) return;
    await sendMessage(choice.text, true);
  },

  reset: () => {
    // Auto-save before clearing
    const saved = autoSaveConversation(get());
    // Clean up direct conversation memory
    const convId = get().conversationId;
    if (convId) clearDirectConversation(convId);
    abortCurrentStream();
    set({
      conversationId: null,
      conceptId: null,
      conceptName: null,
      isMilestone: false,
      messages: [],
      isStreaming: false,
      isAssessing: false,
      isInitializing: false,
      suggestAssess: false,
      assessment: null,
      error: null,
      currentChoices: null,
      ...(saved ? { savedConversations: saved } : {}),
    });
  },

  loadSavedConversation: (convId: string) => {
    const { savedConversations } = get();
    const conv = savedConversations.find(c => c.conversationId === convId);
    if (!conv) return;
    abortCurrentStream();
    set({
      conversationId: conv.conversationId,
      conceptId: conv.conceptId,
      conceptName: conv.conceptName,
      isMilestone: false,
      messages: conv.messages,
      isStreaming: false,
      isAssessing: false,
      isInitializing: false,
      suggestAssess: false,
      assessment: conv.assessment,
      error: null,
      currentChoices: null,  // Clear stale choices when loading saved conversation
    });
  },

  deleteSavedConversation: (convId: string) => {
    const { savedConversations } = get();
    const updated = savedConversations.filter(c => c.conversationId !== convId);
    persistConversations(updated);
    set({ savedConversations: updated });
  },

  importConversations: (convs: SavedConversation[]) => {
    const { savedConversations } = get();
    const existingIds = new Set(savedConversations.map(c => c.conversationId));
    let imported = 0;
    const merged = [...savedConversations];
    for (const conv of convs) {
      if (!conv.conversationId || !conv.conceptId || !Array.isArray(conv.messages)) continue;
      if (!existingIds.has(conv.conversationId)) {
        merged.push(conv);
        existingIds.add(conv.conversationId);
        imported++;
      }
    }
    merged.sort((a, b) => (a.createdAt || 0) - (b.createdAt || 0));
    persistConversations(merged);
    set({ savedConversations: merged });
    return { imported };
  },

  replaceConversations: (convs: SavedConversation[]) => {
    const valid = convs.filter(c => c.conversationId && c.conceptId && Array.isArray(c.messages));
    persistConversations(valid);
    set({ savedConversations: valid });
  },
}));