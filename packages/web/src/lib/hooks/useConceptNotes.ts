import { useCallback, useMemo } from 'react';
import { useLocalStorage } from './useLocalStorage';

export interface ConceptNote {
  /** Note content (Markdown supported) */
  content: string;
  /** Last updated timestamp */
  updatedAt: number;
  /** Creation timestamp */
  createdAt: number;
}

const STORAGE_KEY = 'akg-concept-notes';

/**
 * Concept notes hook — save/retrieve personal notes per concept.
 * Stored in localStorage, ready for Supabase sync.
 */
export function useConceptNotes() {
  const [allNotes, setAllNotes] = useLocalStorage<Record<string, ConceptNote>>(
    STORAGE_KEY,
    {}
  );

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
    },
    [setAllNotes]
  );

  /** Delete a note */
  const deleteNote = useCallback(
    (conceptId: string) => {
      setAllNotes((prev) => {
        const next = { ...prev };
        delete next[conceptId];
        return next;
      });
    },
    [setAllNotes]
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
        return true;
      } catch {
        return false;
      }
    },
    [setAllNotes]
  );

  return {
    getNote,
    saveNote,
    deleteNote,
    noteCount,
    allNotesArray,
    exportNotes,
    importNotes,
  };
}
