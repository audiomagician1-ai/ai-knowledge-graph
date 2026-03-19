import { create } from 'zustand';
import type { Domain } from '@akg/shared';
import { fetchDomains as apiFetchDomains } from '@/lib/api/graph-api';

const STORAGE_KEY = 'akg_active_domain';
const DEFAULT_DOMAIN = 'ai-engineering';

interface DomainState {
  /** All available knowledge domains */
  domains: Domain[];
  /** Currently active domain ID */
  activeDomain: string;
  /** Loading state for domain list fetch */
  loading: boolean;
  /** Error message */
  error: string | null;

  /** Fetch domain list from backend */
  fetchDomains: () => Promise<void>;
  /** Switch to a different domain */
  switchDomain: (domainId: string) => void;
  /** Get the active Domain object (or undefined if not loaded) */
  getActiveDomainInfo: () => Domain | undefined;
}

function loadSavedDomain(): string {
  try {
    return localStorage.getItem(STORAGE_KEY) || DEFAULT_DOMAIN;
  } catch {
    return DEFAULT_DOMAIN;
  }
}

export const useDomainStore = create<DomainState>((set, get) => ({
  domains: [],
  activeDomain: loadSavedDomain(),
  loading: false,
  error: null,

  fetchDomains: async () => {
    set({ loading: true, error: null });
    try {
      const domains = await apiFetchDomains();
      set({ domains, loading: false });
    } catch (err) {
      set({ error: err instanceof Error ? err.message : '获取领域列表失败', loading: false });
    }
  },

  switchDomain: (domainId: string) => {
    set({ activeDomain: domainId });
    try {
      localStorage.setItem(STORAGE_KEY, domainId);
    } catch { /* localStorage unavailable — ignore */ }
  },

  getActiveDomainInfo: () => {
    const { domains, activeDomain } = get();
    return domains.find((d) => d.id === activeDomain);
  },
}));
