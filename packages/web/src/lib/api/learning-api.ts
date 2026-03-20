/**
 * Learning API client — communicates with backend SQLite persistence layer.
 * All calls are fire-and-forget async (write) or lazy-loaded (read).
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

/** POST /api/learning/start */
export async function apiStartLearning(conceptId: string): Promise<void> {
  try {
    await fetch(`${API_BASE}/learning/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ concept_id: conceptId }),
    });
  } catch { /* fire-and-forget */ }
}

/** POST /api/learning/assess */
export async function apiRecordAssessment(
  conceptId: string, conceptName: string, score: number, mastered: boolean
): Promise<void> {
  try {
    await fetch(`${API_BASE}/learning/assess`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ concept_id: conceptId, concept_name: conceptName, score, mastered }),
    });
  } catch { /* fire-and-forget */ }
}

/** GET /api/learning/progress — all concept progress from backend */
export async function apiFetchAllProgress(): Promise<Record<string, any>> {
  try {
    const res = await fetch(`${API_BASE}/learning/progress`);
    if (!res.ok) return {};
    const list: any[] = await res.json();
    const map: Record<string, any> = {};
    for (const p of list) {
      map[p.concept_id] = p;
    }
    return map;
  } catch { return {}; }
}

/** GET /api/learning/stats */
export async function apiFetchStats(totalConcepts: number): Promise<any | null> {
  try {
    const res = await fetch(`${API_BASE}/learning/stats?total_concepts=${totalConcepts}`);
    if (!res.ok) return null;
    return await res.json();
  } catch { return null; }
}

/** GET /api/learning/history */
export async function apiFetchHistory(limit = 100): Promise<any[]> {
  try {
    const res = await fetch(`${API_BASE}/learning/history?limit=${limit}`);
    if (!res.ok) return [];
    return await res.json();
  } catch { return []; }
}

/** GET /api/learning/streak */
export async function apiFetchStreak(): Promise<any | null> {
  try {
    const res = await fetch(`${API_BASE}/learning/streak`);
    if (!res.ok) return null;
    return await res.json();
  } catch { return null; }
}

/** GET /api/learning/recommend — smart next-node recommendations */
export async function apiFetchRecommendations(topK = 5, domain?: string): Promise<{
  recommendations: Array<{
    concept_id: string;
    name: string;
    subdomain_id: string;
    difficulty: number;
    estimated_minutes: number;
    is_milestone: boolean;
    score: number;
    reason: string;
    status: string;
  }>;
  current_level: number;
  mastered_count: number;
  total_concepts: number;
} | null> {
  try {
    const params = new URLSearchParams({ top_k: String(topK) });
    if (domain) params.set('domain', domain);
    const res = await fetch(`${API_BASE}/learning/recommend?${params}`);
    if (!res.ok) return null;
    return await res.json();
  } catch { return null; }
}
export async function apiSyncToBackend(data: {
  progress: Record<string, any>;
  history: any[];
  streak: any;
}): Promise<{ success: boolean; synced_progress: number; synced_history: number } | null> {
  try {
    const res = await fetch(`${API_BASE}/learning/sync`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) return null;
    return await res.json();
  } catch { return null; }
}
