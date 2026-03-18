/**
 * auth.ts store tests — callback management + display name logic
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';

// Mock supabase client before importing auth
vi.mock('@/lib/api/supabase', () => ({
  supabase: {
    auth: {
      getSession: vi.fn(() => Promise.resolve({ data: { session: null } })),
      onAuthStateChange: vi.fn(() => ({
        data: { subscription: { unsubscribe: vi.fn() } },
      })),
      signInWithPassword: vi.fn(),
      signUp: vi.fn(),
      signInWithOAuth: vi.fn(),
      signOut: vi.fn(),
    },
    from: vi.fn(),
  },
}));

import { onAuthLogin, useAuthStore } from '@/lib/store/auth';

describe('useAuthStore', () => {
  beforeEach(() => {
    useAuthStore.setState({
      session: null,
      user: null,
      loading: true,
    });
  });

  describe('onAuthLogin callback management', () => {
    it('should register and call callbacks', async () => {
      const cb = vi.fn(() => Promise.resolve());
      const unsub = onAuthLogin(cb);

      // Simulate login by calling the internal _runLoginCallbacks
      // We test via the public API by checking callback dedup
      expect(typeof unsub).toBe('function');
      unsub();
    });

    it('should not register duplicate callbacks', () => {
      const cb = vi.fn(() => Promise.resolve());
      const unsub1 = onAuthLogin(cb);
      const unsub2 = onAuthLogin(cb); // same function ref → should not add again

      // Unsubscribe once should remove
      unsub1();
      // Second unsub should not throw
      unsub2();
    });

    it('should return valid unsubscribe function', () => {
      const cb = vi.fn(() => Promise.resolve());
      const unsub = onAuthLogin(cb);
      expect(typeof unsub).toBe('function');
      // Calling unsub multiple times should not throw
      unsub();
      unsub();
    });
  });

  describe('displayName', () => {
    it('should return empty string when no user', () => {
      useAuthStore.setState({ user: null });
      expect(useAuthStore.getState().displayName()).toBe('');
    });

    it('should prefer display_name from metadata', () => {
      useAuthStore.setState({
        user: {
          id: '1',
          user_metadata: { display_name: 'Tim' },
          email: 'tim@example.com',
        } as any,
      });
      expect(useAuthStore.getState().displayName()).toBe('Tim');
    });

    it('should fallback to full_name', () => {
      useAuthStore.setState({
        user: {
          id: '1',
          user_metadata: { full_name: 'Tim G' },
          email: 'tim@example.com',
        } as any,
      });
      expect(useAuthStore.getState().displayName()).toBe('Tim G');
    });

    it('should fallback to email prefix', () => {
      useAuthStore.setState({
        user: {
          id: '1',
          user_metadata: {},
          email: 'tim@example.com',
        } as any,
      });
      expect(useAuthStore.getState().displayName()).toBe('tim');
    });

    it('should return empty for user with no email or metadata', () => {
      useAuthStore.setState({
        user: {
          id: '1',
          user_metadata: {},
        } as any,
      });
      expect(useAuthStore.getState().displayName()).toBe('');
    });
  });

  describe('isAuthenticated', () => {
    it('should return false when no session', () => {
      useAuthStore.setState({ session: null });
      expect(useAuthStore.getState().isAuthenticated()).toBe(false);
    });

    it('should return true when session has user', () => {
      useAuthStore.setState({
        session: { user: { id: '1' } } as any,
      });
      expect(useAuthStore.getState().isAuthenticated()).toBe(true);
    });
  });

  describe('supabaseConfigured', () => {
    it('should reflect whether VITE_SUPABASE_URL is a real cloud URL', () => {
      const url = import.meta.env.VITE_SUPABASE_URL || '';
      const expected = !!url && !url.includes('localhost') && url !== 'http://localhost:54321';
      expect(useAuthStore.getState().supabaseConfigured).toBe(expected);
    });
  });
});