import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { fetchWithRetry } from '../utils/fetch-retry';

// Mock global fetch
const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

beforeEach(() => {
  mockFetch.mockReset();
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe('fetchWithRetry', () => {
  it('should return response on successful fetch', async () => {
    mockFetch.mockResolvedValueOnce(new Response('OK', { status: 200 }));
    const res = await fetchWithRetry('/api/test');
    expect(res.status).toBe(200);
    expect(mockFetch).toHaveBeenCalledTimes(1);
  });

  it('should return 4xx responses without retry', async () => {
    mockFetch.mockResolvedValueOnce(new Response('Not Found', { status: 404 }));
    const res = await fetchWithRetry('/api/test', { retries: 3 });
    expect(res.status).toBe(404);
    expect(mockFetch).toHaveBeenCalledTimes(1);
  });

  it('should retry on 500 errors', async () => {
    mockFetch.mockResolvedValueOnce(new Response('Error', { status: 500 }));
    mockFetch.mockResolvedValueOnce(new Response('OK', { status: 200 }));
    const res = await fetchWithRetry('/api/test', { retries: 2, baseDelay: 10 });
    expect(res.status).toBe(200);
    expect(mockFetch).toHaveBeenCalledTimes(2);
  });

  it('should retry on 429 Too Many Requests', async () => {
    mockFetch.mockResolvedValueOnce(new Response('Rate Limited', { status: 429 }));
    mockFetch.mockResolvedValueOnce(new Response('OK', { status: 200 }));
    const res = await fetchWithRetry('/api/test', { retries: 2, baseDelay: 10 });
    expect(res.status).toBe(200);
    expect(mockFetch).toHaveBeenCalledTimes(2);
  });

  it('should retry on network errors', async () => {
    mockFetch.mockRejectedValueOnce(new TypeError('Failed to fetch'));
    mockFetch.mockResolvedValueOnce(new Response('OK', { status: 200 }));
    const res = await fetchWithRetry('/api/test', { retries: 2, baseDelay: 10 });
    expect(res.status).toBe(200);
    expect(mockFetch).toHaveBeenCalledTimes(2);
  });

  it('should exhaust retries and throw on persistent network error', async () => {
    const err = new TypeError('Failed to fetch');
    mockFetch.mockRejectedValue(err);
    await expect(fetchWithRetry('/api/test', { retries: 2, baseDelay: 10 })).rejects.toThrow('Failed to fetch');
    expect(mockFetch).toHaveBeenCalledTimes(3); // initial + 2 retries
  });

  it('should return last 5xx response if all retries fail', async () => {
    mockFetch.mockResolvedValue(new Response('Error', { status: 503 }));
    const res = await fetchWithRetry('/api/test', { retries: 2, baseDelay: 10 });
    expect(res.status).toBe(503);
    expect(mockFetch).toHaveBeenCalledTimes(3);
  });

  it('should respect external abort signal', async () => {
    const controller = new AbortController();
    controller.abort();
    await expect(fetchWithRetry('/api/test', { signal: controller.signal, retries: 3 })).rejects.toThrow();
  });

  it('should not retry when retries is 0', async () => {
    mockFetch.mockResolvedValueOnce(new Response('Error', { status: 500 }));
    const res = await fetchWithRetry('/api/test', { retries: 0 });
    expect(res.status).toBe(500);
    expect(mockFetch).toHaveBeenCalledTimes(1);
  });

  it('should forward request options', async () => {
    mockFetch.mockResolvedValueOnce(new Response('OK', { status: 200 }));
    await fetchWithRetry('/api/test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ key: 'value' }),
    });
    expect(mockFetch).toHaveBeenCalledWith('/api/test', expect.objectContaining({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ key: 'value' }),
    }));
  });

  it('should handle Retry-After header (seconds)', async () => {
    const headers = new Headers({ 'Retry-After': '1' });
    mockFetch.mockResolvedValueOnce(new Response('Rate Limited', { status: 429, headers }));
    mockFetch.mockResolvedValueOnce(new Response('OK', { status: 200 }));
    const start = Date.now();
    const res = await fetchWithRetry('/api/test', { retries: 2, baseDelay: 10, maxDelay: 2000 });
    expect(res.status).toBe(200);
    // Should have waited ~1000ms due to Retry-After: 1
    expect(Date.now() - start).toBeGreaterThanOrEqual(900);
  });

  it('should retry on 408 Request Timeout', async () => {
    mockFetch.mockResolvedValueOnce(new Response('Timeout', { status: 408 }));
    mockFetch.mockResolvedValueOnce(new Response('OK', { status: 200 }));
    const res = await fetchWithRetry('/api/test', { retries: 1, baseDelay: 10 });
    expect(res.status).toBe(200);
    expect(mockFetch).toHaveBeenCalledTimes(2);
  });
});
