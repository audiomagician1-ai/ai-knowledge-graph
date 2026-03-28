/**
 * logger.ts — Unified Logging System (Vibe Coding Standard)
 *
 * Module-scoped loggers with ring buffer, structured data, env-based filtering.
 * Zero dependencies, works in browser + Node.js.
 *
 * Usage:
 *   import { createLogger } from '@/lib/utils/logger';
 *   const log = createLogger('Learning');
 *   log.info('Assessment recorded', { conceptId, score, mastered });
 */

// ── Types ──────────────────────────────────────────────────────────

export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

export interface LogEntry {
  ts: string;
  level: LogLevel;
  module: string;
  msg: string;
  data?: Record<string, unknown>;
}

export interface Logger {
  debug(msg: string, data?: Record<string, unknown>): void;
  info(msg: string, data?: Record<string, unknown>): void;
  warn(msg: string, data?: Record<string, unknown>): void;
  error(msg: string, data?: Record<string, unknown>): void;
}

// ── Config ─────────────────────────────────────────────────────────

const LOG_LEVELS: Record<LogLevel, number> = { debug: 0, info: 1, warn: 2, error: 3 };
const BUFFER_SIZE = 500;

function detectMinLevel(): LogLevel {
  try {
    if (
      (import.meta as unknown as Record<string, unknown>).env &&
      (import.meta as unknown as Record<string, Record<string, unknown>>).env.DEV
    )
      return 'debug';
  } catch {
    /* not Vite */
  }
  try {
    if (typeof process !== 'undefined' && process.env.NODE_ENV !== 'production') return 'debug';
  } catch {
    /* not Node */
  }
  return 'warn';
}

const MIN_LEVEL = detectMinLevel();

// ── Ring Buffer ────────────────────────────────────────────────────

const buffer: LogEntry[] = [];
let bufferIdx = 0;

function push(entry: LogEntry): void {
  if (buffer.length < BUFFER_SIZE) buffer.push(entry);
  else buffer[bufferIdx % BUFFER_SIZE] = entry;
  bufferIdx++;
}

// ── Console Output ─────────────────────────────────────────────────

const STYLE: Record<LogLevel, string> = {
  debug: 'color:#888',
  info: 'color:#4a9eff',
  warn: 'color:#f59e0b;font-weight:bold',
  error: 'color:#ef4444;font-weight:bold',
};

function emit(entry: LogEntry): void {
  if (LOG_LEVELS[entry.level] < LOG_LEVELS[MIN_LEVEL]) return;
  const tag = `%c[${entry.ts.slice(11, 23)}] [${entry.level.toUpperCase().padEnd(5)}] [${entry.module}]`;
  const fn = entry.level as 'debug' | 'info' | 'warn' | 'error';
  if (entry.data && Object.keys(entry.data).length > 0) {
    console[fn](tag, STYLE[entry.level], entry.msg, entry.data);
  } else {
    console[fn](tag, STYLE[entry.level], entry.msg);
  }
}

// ── Public API ─────────────────────────────────────────────────────

export function createLogger(module: string): Logger {
  function log(level: LogLevel, msg: string, data?: Record<string, unknown>): void {
    const entry: LogEntry = { ts: new Date().toISOString(), level, module, msg, data };
    push(entry);
    emit(entry);
  }
  return {
    debug: (msg, data) => log('debug', msg, data),
    info: (msg, data) => log('info', msg, data),
    warn: (msg, data) => log('warn', msg, data),
    error: (msg, data) => log('error', msg, data),
  };
}

/** Get all buffered entries in chronological order */
export function getLogBuffer(): LogEntry[] {
  if (buffer.length < BUFFER_SIZE) return [...buffer];
  const start = bufferIdx % BUFFER_SIZE;
  return [...buffer.slice(start), ...buffer.slice(0, start)];
}

/** Query entries by criteria */
export function queryLogs(opts: {
  level?: LogLevel;
  module?: string;
  since?: string;
  contains?: string;
}): LogEntry[] {
  const min = opts.level ? LOG_LEVELS[opts.level] : 0;
  return getLogBuffer().filter((e) => {
    if (LOG_LEVELS[e.level] < min) return false;
    if (opts.module && e.module !== opts.module) return false;
    if (opts.since && e.ts < opts.since) return false;
    if (opts.contains && !e.msg.includes(opts.contains) && !JSON.stringify(e.data ?? {}).includes(opts.contains))
      return false;
    return true;
  });
}

/** Clear buffer */
export function clearLogBuffer(): void {
  buffer.length = 0;
  bufferIdx = 0;
}

// ── Expose for E2E / debugging (non-production only) ───────────────

if (typeof globalThis !== 'undefined' && MIN_LEVEL !== 'warn') {
  (globalThis as Record<string, unknown>).__logger = {
    getBuffer: getLogBuffer,
    query: queryLogs,
    clear: clearLogBuffer,
    create: createLogger,
  };
}