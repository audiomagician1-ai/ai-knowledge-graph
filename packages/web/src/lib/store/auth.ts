import { create } from 'zustand';
import type { Session, User, Provider, Subscription } from '@supabase/supabase-js';
import { supabase } from '../api/supabase';

/** Track active auth subscription to avoid leaks on re-init (HMR / StrictMode) */
let _authSubscription: Subscription | null = null;

interface AuthState {
  session: Session | null;
  user: User | null;
  loading: boolean;
  /** Whether a Supabase cloud instance is configured (not localhost fallback) */
  supabaseConfigured: boolean;

  initialize: () => Promise<void>;
  signInWithEmail: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, displayName: string) => Promise<void>;
  signInWithOAuth: (provider: Provider) => Promise<void>;
  signOut: () => Promise<void>;

  /** Convenience: true when user is logged in */
  isAuthenticated: () => boolean;
  /** Display name from user metadata or email prefix */
  displayName: () => string;
}

/** Check if Supabase is configured with real credentials (not localhost fallback) */
function isSupabaseConfigured(): boolean {
  const url = import.meta.env.VITE_SUPABASE_URL || '';
  return !!url && !url.includes('localhost') && url !== 'http://localhost:54321';
}

/** Callback registry for post-login sync — avoids circular imports */
const _onLoginCallbacks: Array<(userId: string) => Promise<void>> = [];

/** Register a callback to run after successful login (used by supabase-sync). Returns unsubscribe function. */
export function onAuthLogin(cb: (userId: string) => Promise<void>) {
  if (!_onLoginCallbacks.includes(cb)) _onLoginCallbacks.push(cb);
  return () => {
    const i = _onLoginCallbacks.indexOf(cb);
    if (i >= 0) _onLoginCallbacks.splice(i, 1);
  };
}

async function _runLoginCallbacks(userId: string) {
  for (const cb of _onLoginCallbacks) {
    try {
      await cb(userId);
    } catch (err) {
      console.warn('[auth] Post-login callback failed:', err);
    }
  }
}

export const useAuthStore = create<AuthState>((set, get) => ({
  session: null,
  user: null,
  loading: true,
  supabaseConfigured: isSupabaseConfigured(),

  initialize: async () => {
    if (!isSupabaseConfigured()) {
      set({ loading: false });
      return;
    }
    try {
      // Unsubscribe previous listener (HMR / double-init guard)
      _authSubscription?.unsubscribe();

      const { data: { session } } = await supabase.auth.getSession();
      set({ session, user: session?.user ?? null, loading: false });

      // If already logged in, trigger sync
      if (session?.user) {
        _runLoginCallbacks(session.user.id).catch(() => {});
      }

      const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
        const prevUser = get().user;
        set({ session, user: session?.user ?? null });

        // Trigger sync on fresh sign-in (not on token refresh)
        if (session?.user && !prevUser && (event === 'SIGNED_IN')) {
          _runLoginCallbacks(session.user.id).catch(() => {});
        }
      });
      _authSubscription = subscription;
    } catch {
      set({ loading: false });
    }
  },

  signInWithEmail: async (email, password) => {
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) throw error;
  },

  signUp: async (email, password, displayName) => {
    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: { data: { display_name: displayName } },
    });
    if (error) throw error;
  },

  signInWithOAuth: async (provider: Provider) => {
    const { error } = await supabase.auth.signInWithOAuth({
      provider,
      options: {
        redirectTo: `${window.location.origin}/graph`,
      },
    });
    if (error) throw error;
  },

  signOut: async () => {
    await supabase.auth.signOut();
    set({ session: null, user: null });
  },

  isAuthenticated: () => !!get().session?.user,

  displayName: () => {
    const user = get().user;
    if (!user) return '';
    return user.user_metadata?.display_name
      || user.user_metadata?.full_name
      || user.user_metadata?.name
      || user.email?.split('@')[0]
      || '';
  },
}));
