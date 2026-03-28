import { create } from 'zustand';
import type { Domain } from '@akg/shared';
import { fetchDomains as apiFetchDomains } from '@/lib/api/graph-api';
import { createLogger } from '@/lib/utils/logger';

const log = createLogger('Domain');

const STORAGE_KEY = 'akg_active_domain';
const HISTORY_KEY = 'akg_domain_access_history';
const DEFAULT_DOMAIN = 'ai-engineering';

/** Domain access timestamp map: { domainId: epoch_ms } */
type DomainAccessHistory = Record<string, number>;

interface DomainState {
  /** All available knowledge domains */
  domains: Domain[];
  /** Currently active domain ID */
  activeDomain: string;
  /** Loading state for domain list fetch */
  loading: boolean;
  /** Error message */
  error: string | null;
  /** Per-domain last-access timestamps (epoch ms) */
  accessHistory: DomainAccessHistory;

  /** Fetch domain list from backend */
  fetchDomains: () => Promise<void>;
  /** Switch to a different domain */
  switchDomain: (domainId: string) => void;
  /** Get the active Domain object (or undefined if not loaded) */
  getActiveDomainInfo: () => Domain | undefined;
  /** Get domains sorted by most-recently-accessed (excluding the given domainId) */
  getOtherDomainsByRecency: (excludeId?: string) => Domain[];
}

function loadSavedDomain(): string {
  try {
    return localStorage.getItem(STORAGE_KEY) || DEFAULT_DOMAIN;
  } catch {
    return DEFAULT_DOMAIN;
  }
}

function loadAccessHistory(): DomainAccessHistory {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

function saveAccessHistory(h: DomainAccessHistory) {
  try { localStorage.setItem(HISTORY_KEY, JSON.stringify(h)); } catch { /* */ }
}

export const useDomainStore = create<DomainState>((set, get) => ({
  domains: [],
  activeDomain: loadSavedDomain(),
  loading: false,
  error: null,
  accessHistory: loadAccessHistory(),

  fetchDomains: async () => {
    set({ loading: true, error: null });
    try {
      const domains = await apiFetchDomains();
      set({ domains, loading: false });
    } catch (err) {
      log.error('fetchDomains failed', { err: err instanceof Error ? err.message : 'Unknown' });
      set({ error: err instanceof Error ? err.message : '获取领域列表失败', loading: false });
    }
  },

  switchDomain: (domainId: string) => {
    // Record access timestamp
    const accessHistory = { ...get().accessHistory, [domainId]: Date.now() };
    saveAccessHistory(accessHistory);
    set({ activeDomain: domainId, accessHistory });
    try {
      localStorage.setItem(STORAGE_KEY, domainId);
    } catch { /* localStorage unavailable — ignore */ }
    // Sync learning store to the new domain (lazy import to avoid circular dependency)
    import('./learning').then(({ useLearningStore }) => {
      useLearningStore.getState().switchDomain(domainId);
    });
  },

  getActiveDomainInfo: () => {
    const { domains, activeDomain } = get();
    return domains.find((d) => d.id === activeDomain);
  },

  getOtherDomainsByRecency: (excludeId?: string) => {
    const { domains, accessHistory } = get();
    const exclude = excludeId ?? get().activeDomain;
    return domains
      .filter((d) => d.id !== exclude && d.is_active !== false)
      .sort((a, b) => (accessHistory[b.id] || 0) - (accessHistory[a.id] || 0));
  },
}));
