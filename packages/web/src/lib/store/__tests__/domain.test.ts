/**
 * domain.ts store tests — domain state management
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useDomainStore } from '@/lib/store/domain';
import type { Domain } from '@akg/shared';

// Mock the graph-api module
vi.mock('@/lib/api/graph-api', () => ({
  fetchDomains: vi.fn(),
}));

import { fetchDomains as mockFetchDomains } from '@/lib/api/graph-api';

const mockDomains: Domain[] = [
  {
    id: 'ai-engineering',
    name: 'AI工程',
    description: '从编程基础到AI系统设计',
    icon: '🟣',
    color: '#8b5cf6',
    concept_count: 400,
  },
  {
    id: 'mathematics',
    name: '数学',
    description: '高中到大学数学',
    icon: '🔵',
    color: '#3b82f6',
    concept_count: 300,
  },
];

describe('useDomainStore', () => {
  beforeEach(() => {
    useDomainStore.setState({
      domains: [],
      activeDomain: 'ai-engineering',
      loading: false,
      error: null,
    });
    vi.clearAllMocks();
    try { localStorage.removeItem('akg_active_domain'); } catch { /* ignore */ }
  });

  describe('initial state', () => {
    it('should have empty domains, ai-engineering as default, loading=false', () => {
      const state = useDomainStore.getState();
      expect(state.domains).toEqual([]);
      expect(state.activeDomain).toBe('ai-engineering');
      expect(state.loading).toBe(false);
      expect(state.error).toBeNull();
    });
  });

  describe('fetchDomains', () => {
    it('should fetch and set domains list', async () => {
      vi.mocked(mockFetchDomains).mockResolvedValue(mockDomains);

      await useDomainStore.getState().fetchDomains();
      const state = useDomainStore.getState();

      expect(state.domains).toEqual(mockDomains);
      expect(state.loading).toBe(false);
      expect(state.error).toBeNull();
    });

    it('should handle fetch error', async () => {
      vi.mocked(mockFetchDomains).mockRejectedValue(new Error('Network error'));

      await useDomainStore.getState().fetchDomains();
      const state = useDomainStore.getState();

      expect(state.domains).toEqual([]);
      expect(state.loading).toBe(false);
      expect(state.error).toBe('Network error');
    });

    it('should set loading=true during fetch', async () => {
      let resolvePromise: (v: Domain[]) => void;
      vi.mocked(mockFetchDomains).mockImplementation(
        () => new Promise<Domain[]>((resolve) => { resolvePromise = resolve; })
      );

      const fetchPromise = useDomainStore.getState().fetchDomains();
      expect(useDomainStore.getState().loading).toBe(true);

      resolvePromise!(mockDomains);
      await fetchPromise;
      expect(useDomainStore.getState().loading).toBe(false);
    });
  });

  describe('switchDomain', () => {
    it('should update activeDomain', () => {
      useDomainStore.getState().switchDomain('mathematics');
      expect(useDomainStore.getState().activeDomain).toBe('mathematics');
    });

    it('should persist to localStorage', () => {
      useDomainStore.getState().switchDomain('mathematics');
      expect(localStorage.getItem('akg_active_domain')).toBe('mathematics');
    });

    it('should be able to switch back', () => {
      useDomainStore.getState().switchDomain('mathematics');
      useDomainStore.getState().switchDomain('ai-engineering');
      expect(useDomainStore.getState().activeDomain).toBe('ai-engineering');
    });
  });

  describe('getActiveDomainInfo', () => {
    it('should return undefined when domains are empty', () => {
      expect(useDomainStore.getState().getActiveDomainInfo()).toBeUndefined();
    });

    it('should return the active domain info', () => {
      useDomainStore.setState({ domains: mockDomains, activeDomain: 'mathematics' });
      const info = useDomainStore.getState().getActiveDomainInfo();
      expect(info?.id).toBe('mathematics');
      expect(info?.name).toBe('数学');
    });

    it('should return undefined for non-existent domain', () => {
      useDomainStore.setState({ domains: mockDomains, activeDomain: 'physics' });
      expect(useDomainStore.getState().getActiveDomainInfo()).toBeUndefined();
    });
  });

  describe('domain color for graph theming (Phase 7.4)', () => {
    it('should provide color for active domain', () => {
      useDomainStore.setState({ domains: mockDomains, activeDomain: 'ai-engineering' });
      const info = useDomainStore.getState().getActiveDomainInfo();
      expect(info?.color).toBe('#8b5cf6');
    });

    it('should provide different color when switching domains', () => {
      useDomainStore.setState({ domains: mockDomains, activeDomain: 'ai-engineering' });
      const color1 = useDomainStore.getState().getActiveDomainInfo()?.color;

      useDomainStore.getState().switchDomain('mathematics');
      const color2 = useDomainStore.getState().getActiveDomainInfo()?.color;

      expect(color1).toBe('#8b5cf6');
      expect(color2).toBe('#3b82f6');
      expect(color1).not.toBe(color2);
    });

    it('should return undefined color when domains not loaded', () => {
      const info = useDomainStore.getState().getActiveDomainInfo();
      expect(info?.color).toBeUndefined();
    });

    it('should provide icon for domain switcher display', () => {
      useDomainStore.setState({ domains: mockDomains, activeDomain: 'mathematics' });
      const info = useDomainStore.getState().getActiveDomainInfo();
      expect(info?.icon).toBe('🔵');
    });
  });
});
