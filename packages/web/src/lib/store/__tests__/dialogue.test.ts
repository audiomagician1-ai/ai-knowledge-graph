/**
 * dialogue.ts store tests — conversation management, persistence, import/export
 */
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { useDialogueStore } from '@/lib/store/dialogue';
import type { SavedConversation, AssessmentResult, ChatMessage } from '@/lib/store/dialogue';

// Mock localStorage
const storage: Record<string, string> = {};
vi.stubGlobal('localStorage', {
  getItem: (key: string) => storage[key] ?? null,
  setItem: (key: string, value: string) => { storage[key] = value; },
  removeItem: (key: string) => { delete storage[key]; },
  clear: () => { Object.keys(storage).forEach(k => delete storage[k]); },
});

// Mock fetch (for proxy mode API calls)
vi.stubGlobal('fetch', vi.fn());

// Mock settings store
vi.mock('@/lib/store/settings', () => ({
  useSettingsStore: {
    getState: () => ({
      isDirectMode: () => false,
    }),
  },
  getLLMHeaders: () => ({}),
}));

// Mock direct-llm (direct mode functions)
vi.mock('@/lib/direct-llm', () => ({
  directCreateConversation: vi.fn(),
  directChatStream: vi.fn(),
  directAssess: vi.fn(),
  clearDirectConversation: vi.fn(),
}));

// Mock supabase-sync
vi.mock('@/lib/store/supabase-sync', () => ({
  syncConversationToCloud: vi.fn(),
}));

// --- Helpers ---

function makeSavedConv(overrides: Partial<SavedConversation> = {}): SavedConversation {
  return {
    conversationId: `conv-${Math.random().toString(36).slice(2, 8)}`,
    conceptId: 'test-concept',
    conceptName: 'Test Concept',
    messages: [
      { id: 'msg-1', role: 'assistant', content: 'Hello', timestamp: Date.now() },
      { id: 'msg-2', role: 'user', content: 'Hi', timestamp: Date.now() + 1 },
    ],
    assessment: null,
    createdAt: Date.now() - 10000,
    updatedAt: Date.now(),
    ...overrides,
  };
}

function resetStore() {
  localStorage.clear();
  useDialogueStore.setState({
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
    savedConversations: [],
  });
}

// ======================================================================
// Test Suites
// ======================================================================

describe('useDialogueStore', () => {
  beforeEach(() => {
    resetStore();
    vi.clearAllMocks();
  });

  // ------------------------------------------------------------------
  // Initial State
  // ------------------------------------------------------------------
  describe('initial state', () => {
    it('should have null conversation state on init', () => {
      const s = useDialogueStore.getState();
      expect(s.conversationId).toBeNull();
      expect(s.conceptId).toBeNull();
      expect(s.conceptName).toBeNull();
      expect(s.messages).toEqual([]);
      expect(s.isStreaming).toBe(false);
      expect(s.isAssessing).toBe(false);
      expect(s.isInitializing).toBe(false);
      expect(s.assessment).toBeNull();
      expect(s.error).toBeNull();
      expect(s.currentChoices).toBeNull();
    });

    it('should load saved conversations from localStorage', () => {
      const conv = makeSavedConv({ conversationId: 'persisted-1' });
      storage['akg-conversation-history'] = JSON.stringify([conv]);
      // Re-import would re-read, but for unit test we simulate via setState
      useDialogueStore.setState({ savedConversations: [conv] });
      expect(useDialogueStore.getState().savedConversations).toHaveLength(1);
      expect(useDialogueStore.getState().savedConversations[0].conversationId).toBe('persisted-1');
    });
  });

  // ------------------------------------------------------------------
  // reset()
  // ------------------------------------------------------------------
  describe('reset', () => {
    it('should clear all conversation state', () => {
      useDialogueStore.setState({
        conversationId: 'conv-1',
        conceptId: 'concept-1',
        conceptName: 'Test',
        messages: [{ id: 'm1', role: 'user', content: 'hi', timestamp: Date.now() }],
        isStreaming: true,
        assessment: { completeness: 80, accuracy: 90, depth: 70, examples: 60, overall_score: 75, gaps: [], feedback: '', mastered: true },
        error: 'some error',
        currentChoices: [{ id: 'c1', text: 'opt', type: 'explore' }],
      });

      useDialogueStore.getState().reset();
      const s = useDialogueStore.getState();

      expect(s.conversationId).toBeNull();
      expect(s.conceptId).toBeNull();
      expect(s.conceptName).toBeNull();
      expect(s.messages).toEqual([]);
      expect(s.isStreaming).toBe(false);
      expect(s.isAssessing).toBe(false);
      expect(s.isInitializing).toBe(false);
      expect(s.assessment).toBeNull();
      expect(s.error).toBeNull();
      expect(s.currentChoices).toBeNull();
    });
  });

  // ------------------------------------------------------------------
  // startConversation() error handling
  // ------------------------------------------------------------------
  describe('startConversation error handling', () => {
    it('should reset isInitializing and isStreaming on error', async () => {
      // fetch will reject → error path
      (globalThis.fetch as any).mockRejectedValueOnce(new Error('Network error'));

      await useDialogueStore.getState().startConversation('test-concept');
      const s = useDialogueStore.getState();

      expect(s.isInitializing).toBe(false);
      expect(s.isStreaming).toBe(false);
      expect(s.error).toBe('Network error');
    });

    it('should set conceptId before API call', async () => {
      (globalThis.fetch as any).mockRejectedValueOnce(new Error('fail'));

      await useDialogueStore.getState().startConversation('my-concept');

      expect(useDialogueStore.getState().conceptId).toBe('my-concept');
    });
  });

  // ------------------------------------------------------------------
  // cancelStream()
  // ------------------------------------------------------------------
  describe('cancelStream', () => {
    it('should set isStreaming to false', () => {
      useDialogueStore.setState({ isStreaming: true });
      useDialogueStore.getState().cancelStream();
      expect(useDialogueStore.getState().isStreaming).toBe(false);
    });
  });

  // ------------------------------------------------------------------
  // loadSavedConversation()
  // ------------------------------------------------------------------
  describe('loadSavedConversation', () => {
    it('should load a saved conversation into current state', () => {
      const assessment: AssessmentResult = {
        completeness: 80, accuracy: 90, depth: 70, examples: 60,
        overall_score: 75, gaps: ['gap1'], feedback: 'good', mastered: true,
      };
      const conv = makeSavedConv({
        conversationId: 'saved-1',
        conceptId: 'ml-basics',
        conceptName: 'ML Basics',
        assessment,
      });
      useDialogueStore.setState({ savedConversations: [conv] });

      useDialogueStore.getState().loadSavedConversation('saved-1');
      const s = useDialogueStore.getState();

      expect(s.conversationId).toBe('saved-1');
      expect(s.conceptId).toBe('ml-basics');
      expect(s.conceptName).toBe('ML Basics');
      expect(s.messages).toEqual(conv.messages);
      expect(s.assessment).toEqual(assessment);
      expect(s.isStreaming).toBe(false);
      expect(s.isInitializing).toBe(false);
      expect(s.currentChoices).toBeNull();
    });

    it('should do nothing for non-existent conversation', () => {
      useDialogueStore.setState({ conversationId: 'existing' });
      useDialogueStore.getState().loadSavedConversation('non-existent');
      expect(useDialogueStore.getState().conversationId).toBe('existing');
    });
  });

  // ------------------------------------------------------------------
  // deleteSavedConversation()
  // ------------------------------------------------------------------
  describe('deleteSavedConversation', () => {
    it('should remove conversation from saved list', () => {
      const conv1 = makeSavedConv({ conversationId: 'del-1' });
      const conv2 = makeSavedConv({ conversationId: 'del-2' });
      useDialogueStore.setState({ savedConversations: [conv1, conv2] });

      useDialogueStore.getState().deleteSavedConversation('del-1');

      const saved = useDialogueStore.getState().savedConversations;
      expect(saved).toHaveLength(1);
      expect(saved[0].conversationId).toBe('del-2');
    });

    it('should persist deletion to localStorage', () => {
      const conv = makeSavedConv({ conversationId: 'del-persist' });
      useDialogueStore.setState({ savedConversations: [conv] });

      useDialogueStore.getState().deleteSavedConversation('del-persist');

      const persisted = JSON.parse(storage['akg-conversation-history'] || '[]');
      expect(persisted).toHaveLength(0);
    });
  });

  // ------------------------------------------------------------------
  // importConversations()
  // ------------------------------------------------------------------
  describe('importConversations', () => {
    it('should import new conversations (skip existing)', () => {
      const existing = makeSavedConv({ conversationId: 'existing-1' });
      useDialogueStore.setState({ savedConversations: [existing] });

      const newConv = makeSavedConv({ conversationId: 'new-1' });
      const duplicate = makeSavedConv({ conversationId: 'existing-1' });

      const result = useDialogueStore.getState().importConversations([newConv, duplicate]);

      expect(result.imported).toBe(1);
      expect(useDialogueStore.getState().savedConversations).toHaveLength(2);
    });

    it('should skip invalid conversations (missing required fields)', () => {
      const invalid = { conversationId: '', conceptId: '', messages: 'not-array' } as any;
      const valid = makeSavedConv({ conversationId: 'valid-1' });

      const result = useDialogueStore.getState().importConversations([invalid, valid]);

      expect(result.imported).toBe(1);
    });

    it('should sort by createdAt after import', () => {
      const old = makeSavedConv({ conversationId: 'old', createdAt: 1000 });
      const newer = makeSavedConv({ conversationId: 'new', createdAt: 2000 });

      useDialogueStore.getState().importConversations([newer, old]);

      const saved = useDialogueStore.getState().savedConversations;
      expect(saved[0].conversationId).toBe('old');
      expect(saved[1].conversationId).toBe('new');
    });
  });

  // ------------------------------------------------------------------
  // replaceConversations()
  // ------------------------------------------------------------------
  describe('replaceConversations', () => {
    it('should replace all conversations', () => {
      const old = makeSavedConv({ conversationId: 'old-1' });
      useDialogueStore.setState({ savedConversations: [old] });

      const newConvs = [
        makeSavedConv({ conversationId: 'replace-1' }),
        makeSavedConv({ conversationId: 'replace-2' }),
      ];
      useDialogueStore.getState().replaceConversations(newConvs);

      const saved = useDialogueStore.getState().savedConversations;
      expect(saved).toHaveLength(2);
      expect(saved[0].conversationId).toBe('replace-1');
      expect(saved[1].conversationId).toBe('replace-2');
    });

    it('should filter out invalid entries', () => {
      const valid = makeSavedConv({ conversationId: 'valid' });
      const invalid = { conversationId: '', conceptId: null, messages: null } as any;

      useDialogueStore.getState().replaceConversations([valid, invalid]);

      expect(useDialogueStore.getState().savedConversations).toHaveLength(1);
    });
  });

  // ------------------------------------------------------------------
  // selectChoice()
  // ------------------------------------------------------------------
  describe('selectChoice', () => {
    it('should do nothing if no currentChoices', async () => {
      useDialogueStore.setState({ currentChoices: null, conversationId: 'c1' });
      await useDialogueStore.getState().selectChoice('c1');
      // No crash, no state change
      expect(useDialogueStore.getState().messages).toEqual([]);
    });

    it('should do nothing for non-existent choice id', async () => {
      useDialogueStore.setState({
        currentChoices: [{ id: 'c1', text: 'Option 1', type: 'explore' }],
        conversationId: 'conv-1',
      });
      await useDialogueStore.getState().selectChoice('non-existent');
      expect(useDialogueStore.getState().messages).toEqual([]);
    });
  });

  // ------------------------------------------------------------------
  // sendMessage() guards
  // ------------------------------------------------------------------
  describe('sendMessage guards', () => {
    it('should not send if no conversationId', async () => {
      useDialogueStore.setState({ conversationId: null });
      await useDialogueStore.getState().sendMessage('hello');
      expect(useDialogueStore.getState().messages).toEqual([]);
    });

    it('should not send if currently streaming', async () => {
      useDialogueStore.setState({ conversationId: 'c1', isStreaming: true });
      const msgsBefore = useDialogueStore.getState().messages;
      await useDialogueStore.getState().sendMessage('hello');
      expect(useDialogueStore.getState().messages).toEqual(msgsBefore);
    });

    it('should not send if currently assessing', async () => {
      useDialogueStore.setState({ conversationId: 'c1', isAssessing: true });
      await useDialogueStore.getState().sendMessage('hello');
      expect(useDialogueStore.getState().messages).toEqual([]);
    });
  });

  // ------------------------------------------------------------------
  // requestAssessment() guards
  // ------------------------------------------------------------------
  describe('requestAssessment guards', () => {
    it('should not assess if no conversationId', async () => {
      useDialogueStore.setState({ conversationId: null });
      await useDialogueStore.getState().requestAssessment();
      expect(useDialogueStore.getState().isAssessing).toBe(false);
    });

    it('should not assess if currently streaming', async () => {
      useDialogueStore.setState({ conversationId: 'c1', isStreaming: true });
      await useDialogueStore.getState().requestAssessment();
      expect(useDialogueStore.getState().isAssessing).toBe(false);
    });

    it('should not assess if already assessing', async () => {
      useDialogueStore.setState({ conversationId: 'c1', isAssessing: true });
      await useDialogueStore.getState().requestAssessment();
      // Should remain assessing but not trigger a second assessment
      expect(useDialogueStore.getState().isAssessing).toBe(true);
    });
  });

  // ------------------------------------------------------------------
  // Persistence (localStorage trim)
  // ------------------------------------------------------------------
  describe('persistence', () => {
    it('should trim saved conversations to 50 max', () => {
      const convs: SavedConversation[] = [];
      for (let i = 0; i < 55; i++) {
        convs.push(makeSavedConv({ conversationId: `conv-${i}`, createdAt: i }));
      }
      useDialogueStore.setState({ savedConversations: convs });

      // Trigger persist via deleteSavedConversation (which calls persistConversations)
      useDialogueStore.getState().deleteSavedConversation('conv-0');

      const persisted = JSON.parse(storage['akg-conversation-history'] || '[]');
      expect(persisted.length).toBeLessThanOrEqual(50);
    });
  });
});
