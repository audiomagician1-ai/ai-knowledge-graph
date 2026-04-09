/**
 * Onboarding API client — intelligent domain recommendations for new users.
 * Backend: apps/api/routers/onboarding.py (V3.0)
 */
import { fetchWithRetry } from '@/lib/utils/fetch-retry';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

export interface DomainRecommendation {
  domain_id: string;
  name: string;
  icon: string;
  color: string;
  total_concepts: number;
  avg_difficulty: number;
  entry_concepts: number;
  est_first_session_min: number;
  beginner_score: number;
  reason: string;
}

export interface RecommendedStartResponse {
  recommendations: DomainRecommendation[];
  total_domains: number;
}

export interface EntryConceptPreview {
  id: string;
  name: string;
  difficulty: number;
  estimated_minutes: number;
  content_type: string;
  subdomain: string;
}

export interface DomainPreviewResponse {
  domain_id: string;
  total_concepts: number;
  total_edges: number;
  total_subdomains: number;
  entry_concepts: EntryConceptPreview[];
  difficulty_distribution: { level: number; count: number }[];
  subdomain_summary: { id: string; name: string; concept_count: number }[];
  estimated_total_hours: number;
  avg_difficulty: number;
}

/** Fetch recommended starting domains for new users */
export async function fetchRecommendedStart(): Promise<RecommendedStartResponse> {
  const res = await fetchWithRetry(`${API_BASE}/onboarding/recommended-start`, { retries: 1 });
  if (!res.ok) throw new Error(`Failed to fetch recommendations: ${res.status}`);
  return res.json();
}

/** Fetch domain preview for a specific domain */
export async function fetchDomainPreview(domainId: string): Promise<DomainPreviewResponse> {
  const res = await fetchWithRetry(
    `${API_BASE}/onboarding/domain-preview/${encodeURIComponent(domainId)}`,
    { retries: 1 },
  );
  if (!res.ok) throw new Error(`Failed to fetch domain preview: ${res.status}`);
  return res.json();
}