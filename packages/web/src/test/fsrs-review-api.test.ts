import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  apiFetchDueReviews, apiSubmitReview,
  type DueReviewsResponse, type ReviewResult,
} from '@/lib/api/learning-api';

// ── FSRS API Client Tests ──

describe('FSRS Review API', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  describe('apiFetchDueReviews', () => {
    it('should fetch due reviews with correct params', async () => {
      const mockResponse: DueReviewsResponse = {
        due_count: 3,
        items: [
          {
            concept_id: 'neural-networks',
            status: 'mastered',
            mastery_score: 85,
            fsrs_state: 2,
            fsrs_stability: 10.5,
            fsrs_difficulty: 5.2,
            fsrs_due: Date.now() / 1000 - 86400,
            fsrs_reps: 3,
            fsrs_lapses: 0,
            overdue_days: 1.0,
          },
        ],
      };

      vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await apiFetchDueReviews(20, 'ai-engineering');
      expect(result).toEqual(mockResponse);
      expect(result!.due_count).toBe(3);
      expect(result!.items[0].concept_id).toBe('neural-networks');

      const call = vi.mocked(fetch).mock.calls[0];
      expect(call[0]).toContain('/learning/due');
      expect(call[0]).toContain('limit=20');
      expect(call[0]).toContain('domain=ai-engineering');
    });

    it('should return null on fetch failure', async () => {
      vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
        ok: false,
        status: 500,
      } as Response);

      const result = await apiFetchDueReviews();
      expect(result).toBeNull();
    });

    it('should return null on network error', async () => {
      vi.spyOn(globalThis, 'fetch').mockRejectedValueOnce(new Error('Network error'));
      const result = await apiFetchDueReviews();
      expect(result).toBeNull();
    });

    it('should use default limit when not specified', async () => {
      vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
        ok: true,
        json: async () => ({ due_count: 0, items: [] }),
      } as Response);

      await apiFetchDueReviews();
      const call = vi.mocked(fetch).mock.calls[0];
      expect(call[0]).toContain('limit=20');
    });
  });

  describe('apiSubmitReview', () => {
    it('should submit review with correct payload', async () => {
      const mockResult: ReviewResult = {
        success: true,
        concept_id: 'neural-networks',
        rating: 3,
        card: {
          state: 2,
          stability: 15.3,
          difficulty: 4.8,
          due: Date.now() / 1000 + 86400 * 15,
          scheduled_days: 15,
          reps: 4,
          lapses: 0,
          retrievability: 0.9,
        },
        achievements_unlocked: [],
      };

      vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
        ok: true,
        json: async () => mockResult,
      } as Response);

      const result = await apiSubmitReview('neural-networks', 3);
      expect(result).toEqual(mockResult);
      expect(result!.success).toBe(true);
      expect(result!.card.scheduled_days).toBe(15);

      const call = vi.mocked(fetch).mock.calls[0];
      expect(call[0]).toContain('/learning/review');
      expect(call[1]?.method).toBe('POST');
      const body = JSON.parse(call[1]?.body as string);
      expect(body.concept_id).toBe('neural-networks');
      expect(body.rating).toBe(3);
    });

    it('should return null on server error', async () => {
      vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
        ok: false,
        status: 422,
      } as Response);

      const result = await apiSubmitReview('bad-concept', 5);
      expect(result).toBeNull();
    });

    it('should return null on network error', async () => {
      vi.spyOn(globalThis, 'fetch').mockRejectedValueOnce(new Error('timeout'));
      const result = await apiSubmitReview('concept', 3);
      expect(result).toBeNull();
    });

    it('should accept all valid ratings (1-4)', async () => {
      for (const rating of [1, 2, 3, 4]) {
        vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, concept_id: 'test', rating, card: {}, achievements_unlocked: [] }),
        } as Response);

        const result = await apiSubmitReview('test', rating);
        expect(result!.rating).toBe(rating);
      }
    });
  });
});