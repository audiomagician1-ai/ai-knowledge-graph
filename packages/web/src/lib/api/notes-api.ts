/**
 * Notes API client — sync local concept notes with backend.
 *
 * Backend: apps/api/routers/notes.py
 * Frontend: useConceptNotes (localStorage) ↔ notes-api (backend)
 */
import { fetchWithRetry } from '@/lib/utils/fetch-retry';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

export interface NoteResponse {
  concept_id: string;
  content: string;
  created_at: number;
  updated_at: number;
}

/** Fetch all notes from backend */
export async function fetchAllNotes(): Promise<NoteResponse[]> {
  const res = await fetchWithRetry(`${API_BASE}/notes?limit=1000`, { retries: 1 });
  if (!res.ok) throw new Error(`Failed to fetch notes: ${res.status}`);
  return res.json();
}

/** Fetch a single note */
export async function fetchNote(conceptId: string): Promise<NoteResponse | null> {
  const res = await fetchWithRetry(`${API_BASE}/notes/${encodeURIComponent(conceptId)}`, { retries: 1 });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`Failed to fetch note: ${res.status}`);
  return res.json();
}

/** Create or update a note */
export async function upsertNote(conceptId: string, content: string): Promise<NoteResponse> {
  const res = await fetchWithRetry(`${API_BASE}/notes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ concept_id: conceptId, content }),
    retries: 2,
  });
  if (!res.ok) throw new Error(`Failed to save note: ${res.status}`);
  return res.json();
}

/** Delete a note */
export async function deleteNoteApi(conceptId: string): Promise<void> {
  const res = await fetchWithRetry(`${API_BASE}/notes/${encodeURIComponent(conceptId)}`, {
    method: 'DELETE',
    retries: 1,
  });
  if (!res.ok && res.status !== 404) throw new Error(`Failed to delete note: ${res.status}`);
}

/** Bulk sync: push all local notes to backend */
export async function bulkSyncNotes(notes: Record<string, string>): Promise<{ synced: number; total: number }> {
  const res = await fetchWithRetry(`${API_BASE}/notes/bulk`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(notes),
    retries: 2,
  });
  if (!res.ok) throw new Error(`Bulk sync failed: ${res.status}`);
  return res.json();
}

/** Get notes stats */
export async function fetchNotesStats(): Promise<{ total_notes: number; total_characters: number; avg_length: number }> {
  const res = await fetchWithRetry(`${API_BASE}/notes/stats/summary`, { retries: 1 });
  if (!res.ok) throw new Error(`Failed to fetch stats: ${res.status}`);
  return res.json();
}
