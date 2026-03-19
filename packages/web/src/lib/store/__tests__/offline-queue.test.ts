/**
 * offline-queue.ts store tests — offline write queue for Supabase-first persistence
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  loadQueue, enqueue, clearQueue, queueSize, dequeueProcessed, flushQueue,
  type QueuedProgressWrite, type QueuedHistoryWrite, type QueuedConversationWrite,
} from '@/lib/store/offline-queue';

// Mock localStorage
const storage: Record<string, string> = {};
vi.stubGlobal('localStorage', {
  getItem: (key: string) => storage[key] ?? null,
  setItem: (key: string, value: string) => { storage[key] = value; },
  removeItem: (key: string) => { delete storage[key]; },
  clear: () => { Object.keys(storage).forEach(k => delete storage[k]); },
});

beforeEach(() => {
  localStorage.clear();
});

describe('offline-queue', () => {
  // ════════════════════════════════════════
  // loadQueue
  // ════════════════════════════════════════
  describe('loadQueue', () => {
    it('should return empty array when no queue exists', () => {
      expect(loadQueue()).toEqual([]);
    });

    it('should return empty array when localStorage has invalid JSON', () => {
      localStorage.setItem('akg-offline-queue', 'not-json');
      expect(loadQueue()).toEqual([]);
    });

    it('should return empty array when localStorage has non-array value', () => {
      localStorage.setItem('akg-offline-queue', JSON.stringify({ foo: 1 }));
      expect(loadQueue()).toEqual([]);
    });

    it('should return parsed queue entries', () => {
      const entry: QueuedProgressWrite = {
        type: 'progress', concept_id: 'test', data: { concept_id: 'test' }, created_at: 1000,
      };
      localStorage.setItem('akg-offline-queue', JSON.stringify([entry]));
      const queue = loadQueue();
      expect(queue).toHaveLength(1);
      expect(queue[0]).toEqual(entry);
    });
  });

  // ════════════════════════════════════════
  // enqueue
  // ════════════════════════════════════════
  describe('enqueue', () => {
    it('should add a history entry to the queue', () => {
      const entry: QueuedHistoryWrite = {
        type: 'history', concept_id: 'c1', concept_name: 'C1', score: 80, mastered: true, created_at: 1000,
      };
      enqueue(entry);
      expect(queueSize()).toBe(1);
      expect(loadQueue()[0]).toEqual(entry);
    });

    it('should deduplicate progress entries by concept_id', () => {
      const entry1: QueuedProgressWrite = {
        type: 'progress', concept_id: 'c1', data: { status: 'learning' }, created_at: 1000,
      };
      const entry2: QueuedProgressWrite = {
        type: 'progress', concept_id: 'c1', data: { status: 'mastered' }, created_at: 2000,
      };
      enqueue(entry1);
      enqueue(entry2);
      expect(queueSize()).toBe(1);
      // Should keep the newer entry
      expect(loadQueue()[0]).toEqual(entry2);
    });

    it('should NOT deduplicate history entries with same concept_id', () => {
      const entry1: QueuedHistoryWrite = {
        type: 'history', concept_id: 'c1', concept_name: 'C1', score: 70, mastered: false, created_at: 1000,
      };
      const entry2: QueuedHistoryWrite = {
        type: 'history', concept_id: 'c1', concept_name: 'C1', score: 85, mastered: true, created_at: 2000,
      };
      enqueue(entry1);
      enqueue(entry2);
      expect(queueSize()).toBe(2);
    });

    it('should trim queue to MAX_QUEUE_SIZE (200) on save', () => {
      // Enqueue 210 history entries
      for (let i = 0; i < 210; i++) {
        enqueue({
          type: 'history', concept_id: `c${i}`, concept_name: `C${i}`, score: 50, mastered: false, created_at: i,
        });
      }
      // Should keep only last 200
      expect(queueSize()).toBe(200);
      // First 10 should be trimmed, first remaining should be c10
      expect(loadQueue()[0].concept_id).toBe('c10');
    });
  });

  // ════════════════════════════════════════
  // clearQueue / queueSize
  // ════════════════════════════════════════
  describe('clearQueue', () => {
    it('should remove all entries', () => {
      enqueue({ type: 'history', concept_id: 'c1', concept_name: 'C1', score: 80, mastered: true, created_at: 1000 });
      expect(queueSize()).toBe(1);
      clearQueue();
      expect(queueSize()).toBe(0);
      expect(loadQueue()).toEqual([]);
    });
  });

  describe('queueSize', () => {
    it('should return 0 for empty queue', () => {
      expect(queueSize()).toBe(0);
    });
  });

  // ════════════════════════════════════════
  // dequeueProcessed
  // ════════════════════════════════════════
  describe('dequeueProcessed', () => {
    it('should remove first N entries from the queue', () => {
      enqueue({ type: 'history', concept_id: 'c1', concept_name: 'C1', score: 70, mastered: false, created_at: 1 });
      enqueue({ type: 'history', concept_id: 'c2', concept_name: 'C2', score: 80, mastered: true, created_at: 2 });
      enqueue({ type: 'history', concept_id: 'c3', concept_name: 'C3', score: 90, mastered: true, created_at: 3 });
      expect(queueSize()).toBe(3);
      dequeueProcessed(2);
      expect(queueSize()).toBe(1);
      expect(loadQueue()[0].concept_id).toBe('c3');
    });

    it('should handle dequeuing more than queue size', () => {
      enqueue({ type: 'history', concept_id: 'c1', concept_name: 'C1', score: 70, mastered: false, created_at: 1 });
      dequeueProcessed(5);
      expect(queueSize()).toBe(0);
    });
  });

  // ════════════════════════════════════════
  // flushQueue
  // ════════════════════════════════════════
  describe('flushQueue', () => {
    it('should return 0 for empty queue', async () => {
      const writers = {
        writeProgress: vi.fn(),
        writeHistory: vi.fn(),
      };
      const result = await flushQueue(writers);
      expect(result).toBe(0);
      expect(writers.writeProgress).not.toHaveBeenCalled();
      expect(writers.writeHistory).not.toHaveBeenCalled();
    });

    it('should replay progress entries via writeProgress', async () => {
      const data = { concept_id: 'c1', status: 'mastered' };
      enqueue({ type: 'progress', concept_id: 'c1', data, created_at: 1000 });

      const writers = {
        writeProgress: vi.fn().mockResolvedValue(true),
        writeHistory: vi.fn(),
      };
      const result = await flushQueue(writers);
      expect(result).toBe(1);
      expect(writers.writeProgress).toHaveBeenCalledWith(data);
      // Queue should be empty after successful flush
      expect(queueSize()).toBe(0);
    });

    it('should replay history entries via writeHistory', async () => {
      enqueue({
        type: 'history', concept_id: 'c1', concept_name: 'C1', score: 85, mastered: true, created_at: 1000,
      });

      const writers = {
        writeProgress: vi.fn(),
        writeHistory: vi.fn().mockResolvedValue(true),
      };
      const result = await flushQueue(writers);
      expect(result).toBe(1);
      expect(writers.writeHistory).toHaveBeenCalledWith('c1', 'C1', 85, true);
      expect(queueSize()).toBe(0);
    });

    it('should keep failed entries in the queue', async () => {
      enqueue({ type: 'progress', concept_id: 'c1', data: { concept_id: 'c1' }, created_at: 1 });
      enqueue({ type: 'history', concept_id: 'c2', concept_name: 'C2', score: 70, mastered: false, created_at: 2 });

      const writers = {
        writeProgress: vi.fn().mockResolvedValue(false), // fail
        writeHistory: vi.fn().mockResolvedValue(true),   // success
      };
      const result = await flushQueue(writers);
      expect(result).toBe(1); // only history succeeded
      expect(queueSize()).toBe(1); // progress entry remains
      expect(loadQueue()[0].type).toBe('progress');
    });

    it('should keep conversation entries in queue (not yet implemented)', async () => {
      const convEntry: QueuedConversationWrite = {
        type: 'conversation', conv_id: 'cv1', concept_id: 'c1', messages: [], status: 'active', created_at: 1,
      };
      enqueue(convEntry);

      const writers = {
        writeProgress: vi.fn(),
        writeHistory: vi.fn(),
      };
      const result = await flushQueue(writers);
      expect(result).toBe(0);
      // Conversation entry should remain in queue
      expect(queueSize()).toBe(1);
      expect(loadQueue()[0].type).toBe('conversation');
    });

    it('should handle writer exceptions gracefully', async () => {
      enqueue({ type: 'progress', concept_id: 'c1', data: { concept_id: 'c1' }, created_at: 1 });

      const writers = {
        writeProgress: vi.fn().mockRejectedValue(new Error('network error')),
        writeHistory: vi.fn(),
      };
      const result = await flushQueue(writers);
      expect(result).toBe(0);
      expect(queueSize()).toBe(1); // entry remains for retry
    });

    it('should guard against concurrent flushes', async () => {
      enqueue({ type: 'history', concept_id: 'c1', concept_name: 'C1', score: 80, mastered: true, created_at: 1 });

      let resolveFirst!: () => void;
      const firstCallPromise = new Promise<void>(r => { resolveFirst = r; });

      const writers = {
        writeProgress: vi.fn(),
        writeHistory: vi.fn().mockImplementation(async () => {
          await firstCallPromise;
          return true;
        }),
      };

      // Start first flush (will block on writeHistory)
      const flush1 = flushQueue(writers);
      // Start second flush immediately (should return 0 due to _flushing guard)
      const flush2 = flushQueue(writers);

      const result2 = await flush2;
      expect(result2).toBe(0); // concurrent call returns 0 immediately

      // Resolve first flush
      resolveFirst();
      const result1 = await flush1;
      expect(result1).toBe(1);
    });
  });
});
