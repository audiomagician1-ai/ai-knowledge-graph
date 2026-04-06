/**
 * Resilient fetch utility with exponential backoff retry.
 * 
 * Features:
 * - Configurable retry count and delay
 * - Exponential backoff with jitter
 * - Abort signal forwarding
 * - Only retries on network errors and 5xx responses (not 4xx)
 * - Respects Retry-After headers
 * 
 * Usage:
 *   import { fetchWithRetry } from '@/lib/utils/fetch-retry';
 *   const res = await fetchWithRetry('/api/data', { retries: 3 });
 */
import { createLogger } from './logger';

const log = createLogger('FetchRetry');

export interface FetchRetryOptions extends RequestInit {
  /** Maximum number of retry attempts (default: 2) */
  retries?: number;
  /** Base delay in ms before first retry (default: 1000) */
  baseDelay?: number;
  /** Maximum delay in ms (default: 10000) */
  maxDelay?: number;
  /** Timeout per request in ms (default: 30000) */
  timeout?: number;
}

/** HTTP status codes that should trigger a retry */
function isRetryable(status: number): boolean {
  return status >= 500 || status === 408 || status === 429;
}

/** Calculate delay with exponential backoff + jitter */
function getDelay(attempt: number, baseDelay: number, maxDelay: number, retryAfter?: number): number {
  if (retryAfter && retryAfter > 0) return Math.min(retryAfter * 1000, maxDelay);
  const exponential = baseDelay * Math.pow(2, attempt);
  const jitter = Math.random() * baseDelay * 0.5;
  return Math.min(exponential + jitter, maxDelay);
}

/** Parse Retry-After header (seconds or HTTP-date) */
function parseRetryAfter(header: string | null): number | undefined {
  if (!header) return undefined;
  const seconds = Number(header);
  if (!Number.isNaN(seconds)) return seconds;
  const date = Date.parse(header);
  if (!Number.isNaN(date)) return Math.max(0, (date - Date.now()) / 1000);
  return undefined;
}

/**
 * Fetch with automatic retry on network errors and 5xx responses.
 * 
 * @param input - URL or Request object
 * @param options - Extended fetch options with retry config
 * @returns Response from successful fetch
 * @throws Last error if all retries exhausted
 */
export async function fetchWithRetry(
  input: string | URL | Request,
  options: FetchRetryOptions = {},
): Promise<Response> {
  const {
    retries = 2,
    baseDelay = 1000,
    maxDelay = 10000,
    timeout = 30000,
    signal: externalSignal,
    ...fetchOptions
  } = options;

  let lastError: Error | null = null;

  for (let attempt = 0; attempt <= retries; attempt++) {
    // Create per-request timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    // Link external abort signal
    const onExternalAbort = () => controller.abort();
    externalSignal?.addEventListener('abort', onExternalAbort);

    try {
      const res = await fetch(input, {
        ...fetchOptions,
        signal: controller.signal,
      });

      // Don't retry on client errors (4xx), only on retryable errors
      if (!isRetryable(res.status) || attempt >= retries) {
        return res;
      }

      // Retryable status — will retry
      const retryAfter = parseRetryAfter(res.headers.get('Retry-After'));
      const delay = getDelay(attempt, baseDelay, maxDelay, retryAfter);
      
      log.warn(`HTTP ${res.status}, retrying in ${Math.round(delay)}ms`, {
        url: typeof input === 'string' ? input : (input as Request).url || String(input),
        attempt: attempt + 1,
        maxRetries: retries,
      });

      await sleep(delay);
    } catch (err) {
      lastError = err as Error;

      // Don't retry if the user aborted
      if (externalSignal?.aborted) throw lastError;
      if ((err as Error).name === 'AbortError' && !externalSignal?.aborted) {
        // Timeout — retry
        if (attempt < retries) {
          const delay = getDelay(attempt, baseDelay, maxDelay);
          log.warn(`Request timeout, retrying in ${Math.round(delay)}ms`, {
            url: typeof input === 'string' ? input : String(input),
            attempt: attempt + 1,
          });
          await sleep(delay);
          continue;
        }
      }

      // Network error — retry if attempts remain
      if (attempt < retries) {
        const delay = getDelay(attempt, baseDelay, maxDelay);
        log.warn(`Network error, retrying in ${Math.round(delay)}ms`, {
          url: typeof input === 'string' ? input : String(input),
          attempt: attempt + 1,
          err: (err as Error).message,
        });
        await sleep(delay);
        continue;
      }

      throw lastError;
    } finally {
      clearTimeout(timeoutId);
      externalSignal?.removeEventListener('abort', onExternalAbort);
    }
  }

  // Should not reach here, but just in case
  throw lastError || new Error('fetchWithRetry: all retries exhausted');
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}
