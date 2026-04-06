import { useCallback, useEffect, useMemo, useRef } from 'react';
import { useLocalStorage } from './useLocalStorage';
import { upsertNote, deleteNoteApi, bulkSyncNotes, fetchAllNotes } from '@/lib/api/notes-api';
import { createLogger } from '@/lib/utils/logger';

const log = createLogger('ConceptNotes');

export interface ConceptNote {
  /** Note content (Markdown supported) */
  content: string;
  /** Last updated timestamp */
  updatedAt: number;
  /** Creation timestamp */
  createdAt: number;
}

const STORAGE_KEY = 'akg-concept-notes';
const SYNC_KEY = 'akg-notes-last-sync';

/** Debounce delay for backend sync (ms) */
const SYNC_DEBOUNCE = 3000;

/**
 * Concept notes hook — save/retrieve personal notes per concept.
 * Dual storage: localStorage (instant) + backend API (durable).
 * Backend sync is best-effort and non-blocking.
 */
export function useConceptNotes() {
  const [allNotes, setAllNotes] = useLocalStorage<Record<string, ConceptNote>>(
    STORAGE_KEY,
    {}
  );

  // Track pending sync operations (debounced)
  const syncTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pendingOpsRef = useRef<Map<string, 'save' | 'delete'>>(new Map());

  /** Schedule a debounced backend sync */
  const scheduleSync = useCallback(() => {
    if (syncTimerRef.current) clearTimeout(syncTimerRef.current);
    syncTimerRef.current = setTimeout(async () => {
      const ops = new Map(pendingOpsRef.current);
      pendingOpsRef.current.clear();

      for (const [conceptId, op] of ops) {
        try {
          if (op === 'delete') {
            await deleteNoteApi(conceptId);
            log.debug(`Synced delete: ${conceptId}`);
          } else {
            // Read current local value
            const raw = localStorage.getItem(STORAGE_KEY);
            const notes: Record<string, ConceptNote> = raw ? JSON.parse(raw) : {};
            const note = notes[conceptId];
            if (note) {
              await upsertNote(conceptId, note.content);
              log.debug(`Synced save: ${conceptId}`);
            }
          }
        } catch (e) {
          log.warn(`Backend sync failed for ${conceptId}: ${e}`);
          // Re-queue for next sync attempt
          pendingOpsRef.current.set(conceptId, op);
        }
      }

      // Update last sync time
      try {
        localStorage.setItem(SYNC_KEY, Date.now().toString());
      } catch { /* quota */ }
    }, SYNC_DEBOUNCE);
  }, []);

  /** Get note for a specific concept */
  const getNote = useCallback(
    (conceptId: string): ConceptNote | null => {
      return allNotes[conceptId] || null;
    },
    [allNotes]
  );

  /** Save or update a note */
  const saveNote = useCallback(
    (conceptId: string, content: string) => {
      const now = Date.now();
      setAllNotes((prev) => ({
        ...prev,
        [conceptId]: {
          content,
          updatedAt: now,
          createdAt: prev[conceptId]?.createdAt || now,
        },
      }));
      // Queue backend sync
      pendingOpsRef.current.set(conceptId, 'save');
      scheduleSync();
    },
    [setAllNotes, scheduleSync]
  );

  /** Delete a note */
  const deleteNote = useCallback(
    (conceptId: string) => {
      setAllNotes((prev) => {
        const next = { ...prev };
        delete next[conceptId];
        return next;
      });
      // Queue backend sync
      pendingOpsRef.current.set(conceptId, 'delete');
      scheduleSync();
    },
    [setAllNotes, scheduleSync]
  );

  /** Count of total notes */
  const noteCount = useMemo(() => Object.keys(allNotes).length, [allNotes]);

  /** Get all notes with their concept IDs */
  const allNotesArray = useMemo(
    () =>
      Object.entries(allNotes)
        .map(([id, note]) => ({ conceptId: id, ...note }))
        .sort((a, b) => b.updatedAt - a.updatedAt),
    [allNotes]
  );

  /** Export all notes as JSON */
  const exportNotes = useCallback(() => {
    return JSON.stringify(allNotes, null, 2);
  }, [allNotes]);

  /** Import notes from JSON */
  const importNotes = useCallback(
    (json: string) => {
      try {
        const parsed = JSON.parse(json) as Record<string, ConceptNote>;
        setAllNotes((prev) => ({ ...prev, ...parsed }));
        // Bulk sync to backend
        const contentMap: Record<string, string> = {};
        for (const [id, note] of Object.entries(parsed)) {
          contentMap[id] = note.content;
        }
        bulkSyncNotes(contentMap).catch((e) => log.warn(`Bulk import sync failed: ${e}`));
        return true;
      } catch {
        return false;
      }
    },
    [setAllNotes]
  );

  /** Sync all local notes to backend (manual trigger) */
  const syncToBackend = useCallback(async () => {
    const contentMap: Record<string, string> = {};
    for (const [id, note] of Object.entries(allNotes)) {
      contentMap[id] = note.content;
    }
    if (Object.keys(contentMap).length === 0) return { synced: 0, total: 0 };
    const result = await bulkSyncNotes(contentMap);
    localStorage.setItem(SYNC_KEY, Date.now().toString());
    log.info(`Manual sync complete: ${result.synced} notes`);
    return result;
  }, [allNotes]);

  /** Pull notes from backend and merge (backend wins for newer) */
  const syncFromBackend = useCallback(async () => {
    try {
      const remote = await fetchAllNotes();
      if (remote.length === 0) return;

      setAllNotes((prev) => {
        const merged = { ...prev };
        for (const r of remote) {
          const local = merged[r.concept_id];
          // Backend wins if local doesn't exist or backend is newer
          if (!local || r.updated_at * 1000 > local.updatedAt) {
            merged[r.concept_id] = {
              content: r.content,
              updatedAt: r.updated_at * 1000,
              createdAt: r.created_at * 1000,
            };
          }
        }
        return merged;
      });
      log.info(`Pulled ${remote.length} notes from backend`);
    } catch (e) {
      log.warn(`Failed to pull from backend: ${e}`);
    }
  }, [setAllNotes]);

  // On mount: attempt to pull from backend (once)
  const didSync = useRef(false);
  useEffect(() => {
    if (didSync.current) return;
    didSync.current = true;
    syncFromBackend();
  }, [syncFromBackend]);

  return {
    getNote,
    saveNote,
    deleteNote,
    noteCount,
    allNotesArray,
    exportNotes,
    importNotes,
    syncToBackend,
    syncFromBackend,
  };
}
