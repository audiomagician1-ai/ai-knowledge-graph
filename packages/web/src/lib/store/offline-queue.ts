/**
 * offline-queue.ts — Offline write queue for Supabase-first persistence.
 * 
 * When a Supabase write fails (network error, timeout, etc.), the operation
 * is queued in localStorage and retried when connectivity is restored.
 * 
 * Queue entries are typed and self-describing so replay is idempotent.
 */

const QUEUE_KEY = 'akg-offline-queue';
import { createLogger } from '@/lib/utils/logger';

const log = createLogger('OfflineQueue');
const MAX_QUEUE_SIZE = 200;

// ════════════════════════════════════════════
// Types
// ════════════════════════════════════════════

export interface QueuedProgressWrite {
  type: 'progress';
  concept_id: string;
  /** Full row data for upsert */
  data: Record<string, unknown>;
  created_at: number;
}

export interface QueuedHistoryWrite {
  type: 'history';
  concept_id: string;
  concept_name: string;
  score: number;
  mastered: boolean;
  created_at: number;
}

export interface QueuedConversationWrite {
  type: 'conversation';
  conv_id: string;
  concept_id: string;
  messages: unknown[];
  status: string;
  created_at: number;
}

export type QueuedWrite = QueuedProgressWrite | QueuedHistoryWrite | QueuedConversationWrite;

// ════════════════════════════════════════════
// Queue operations
// ════════════════════════════════════════════

/** Load the pending writes queue from localStorage */
export function loadQueue(): QueuedWrite[] {
  try {
    const raw = localStorage.getItem(QUEUE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

/** Save the queue to localStorage */
function saveQueue(queue: QueuedWrite[]): void {
  try {
    // Keep only the most recent entries if queue grows too large
    const trimmed = queue.slice(-MAX_QUEUE_SIZE);
    localStorage.setItem(QUEUE_KEY, JSON.stringify(trimmed));
  } catch (e) {
    log.warn('Failed to save queue', { err: (e as Error).message });
  }
}

/** Enqueue a write operation for later retry */
export function enqueue(write: QueuedWrite): void {
  const queue = loadQueue();
  
  // Deduplicate: for progress writes, replace existing entry for same concept_id
  if (write.type === 'progress') {
    const idx = queue.findIndex(
      (w) => w.type === 'progress' && w.concept_id === write.concept_id
    );
    if (idx >= 0) {
      queue[idx] = write; // Replace with newer data
    } else {
      queue.push(write);
    }
  } else {
    queue.push(write);
  }
  
  saveQueue(queue);
}

/** Remove all entries from the queue */
export function clearQueue(): void {
  try {
    localStorage.removeItem(QUEUE_KEY);
  } catch { /* ignore */ }
}

/** Get the number of pending writes */
export function queueSize(): number {
  return loadQueue().length;
}

/** Remove processed entries (by index range) and save */
export function dequeueProcessed(count: number): void {
  const queue = loadQueue();
  queue.splice(0, count);
  saveQueue(queue);
}

// ════════════════════════════════════════════
// Flush: Replay queued writes when online
// ════════════════════════════════════════════

/** Guard against concurrent flushes */
let _flushing = false;

/**
 * Flush pending writes to Supabase. Returns the number of successfully replayed entries.
 * Each entry is replayed via the write* functions from supabase-sync.
 * Successfully replayed entries are removed from the queue; failures remain for next attempt.
 *
 * Accepts writer functions as parameters to avoid circular imports.
 */
export async function flushQueue(writers: {
  writeProgress: (data: Record<string, unknown>) => Promise<boolean>;
  writeHistory: (conceptId: string, conceptName: string, score: number, mastered: boolean) => Promise<boolean>;
}): Promise<number> {
  if (_flushing) return 0;
  _flushing = true;
  try {
    const queue = loadQueue();
    if (queue.length === 0) return 0;

    let replayed = 0;
    const remaining: QueuedWrite[] = [];

    for (const entry of queue) {
      let ok = false;
      try {
        if (entry.type === 'progress') {
          ok = await writers.writeProgress(entry.data);
        } else if (entry.type === 'history') {
          ok = await writers.writeHistory(entry.concept_id, entry.concept_name, entry.score, entry.mastered);
        }
        // conversation type — not yet implemented, keep in queue
      } catch {
        ok = false;
      }
      if (ok) {
        replayed++;
      } else {
        remaining.push(entry);
      }
    }

    saveQueue(remaining);
    if (replayed > 0) {
      log.info('Flushed queued writes', { replayed, total: queue.length });
    }
    return replayed;
  } finally {
    _flushing = false;
  }
}

/**
 * Register the browser 'online' event listener to auto-flush when connectivity is restored.
 * Call this once at app startup. Accepts writers to avoid circular imports.
 */
export function registerOnlineFlush(writers: Parameters<typeof flushQueue>[0]): void {
  if (typeof window === 'undefined') return;
  window.addEventListener('online', () => {
    log.info('Network restored, flushing queue...');
    flushQueue(writers).catch(() => {});
  });
  // Also flush on visibility change (e.g. user switches back to tab after being offline)
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible' && navigator.onLine) {
      flushQueue(writers).catch(() => {});
    }
  });
}
