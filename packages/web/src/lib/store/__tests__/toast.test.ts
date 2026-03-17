/**
 * toast.ts store tests — notification system logic
 */
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { useToastStore, toast } from '@/lib/store/toast';

describe('useToastStore', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    useToastStore.setState({ toasts: [] });
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe('addToast', () => {
    it('should add a toast with unique id', () => {
      const { addToast } = useToastStore.getState();
      addToast('success', 'Test message');
      const { toasts } = useToastStore.getState();
      expect(toasts).toHaveLength(1);
      expect(toasts[0].type).toBe('success');
      expect(toasts[0].message).toBe('Test message');
      expect(toasts[0].id).toMatch(/^toast-/);
    });

    it('should add multiple toasts', () => {
      const { addToast } = useToastStore.getState();
      addToast('success', 'First');
      addToast('error', 'Second');
      addToast('info', 'Third');
      const { toasts } = useToastStore.getState();
      expect(toasts).toHaveLength(3);
      expect(toasts[0].message).toBe('First');
      expect(toasts[1].message).toBe('Second');
      expect(toasts[2].message).toBe('Third');
    });

    it('should auto-dismiss after default duration (3000ms)', () => {
      const { addToast } = useToastStore.getState();
      addToast('info', 'Auto-dismiss');
      expect(useToastStore.getState().toasts).toHaveLength(1);

      vi.advanceTimersByTime(2999);
      expect(useToastStore.getState().toasts).toHaveLength(1);

      vi.advanceTimersByTime(1);
      expect(useToastStore.getState().toasts).toHaveLength(0);
    });

    it('should auto-dismiss after custom duration', () => {
      const { addToast } = useToastStore.getState();
      addToast('warning', 'Custom duration', 5000);
      expect(useToastStore.getState().toasts).toHaveLength(1);

      vi.advanceTimersByTime(4999);
      expect(useToastStore.getState().toasts).toHaveLength(1);

      vi.advanceTimersByTime(1);
      expect(useToastStore.getState().toasts).toHaveLength(0);
    });

    it('should not auto-dismiss when duration is 0', () => {
      const { addToast } = useToastStore.getState();
      addToast('error', 'Persistent', 0);
      vi.advanceTimersByTime(60000);
      expect(useToastStore.getState().toasts).toHaveLength(1);
    });

    it('should generate unique ids for each toast', () => {
      const { addToast } = useToastStore.getState();
      addToast('info', 'A');
      addToast('info', 'B');
      const { toasts } = useToastStore.getState();
      expect(toasts[0].id).not.toBe(toasts[1].id);
    });
  });

  describe('removeToast', () => {
    it('should remove a specific toast by id', () => {
      const { addToast } = useToastStore.getState();
      addToast('success', 'Keep');
      addToast('error', 'Remove');
      const toasts = useToastStore.getState().toasts;
      const removeId = toasts[1].id;

      useToastStore.getState().removeToast(removeId);
      const remaining = useToastStore.getState().toasts;
      expect(remaining).toHaveLength(1);
      expect(remaining[0].message).toBe('Keep');
    });

    it('should do nothing for non-existent id', () => {
      const { addToast } = useToastStore.getState();
      addToast('info', 'Stays');
      useToastStore.getState().removeToast('non-existent');
      expect(useToastStore.getState().toasts).toHaveLength(1);
    });
  });

  describe('toast shorthand helpers', () => {
    it('toast.success should add success type', () => {
      toast.success('Done!');
      const { toasts } = useToastStore.getState();
      expect(toasts).toHaveLength(1);
      expect(toasts[0].type).toBe('success');
      expect(toasts[0].message).toBe('Done!');
    });

    it('toast.error should add error type with 5000ms duration', () => {
      toast.error('Failed!');
      const { toasts } = useToastStore.getState();
      expect(toasts[0].type).toBe('error');

      // Error toasts last 5000ms
      vi.advanceTimersByTime(4999);
      expect(useToastStore.getState().toasts).toHaveLength(1);
      vi.advanceTimersByTime(1);
      expect(useToastStore.getState().toasts).toHaveLength(0);
    });

    it('toast.info should add info type', () => {
      toast.info('FYI');
      expect(useToastStore.getState().toasts[0].type).toBe('info');
    });

    it('toast.warning should add warning type with 4000ms duration', () => {
      toast.warning('Watch out!');
      const { toasts } = useToastStore.getState();
      expect(toasts[0].type).toBe('warning');

      vi.advanceTimersByTime(3999);
      expect(useToastStore.getState().toasts).toHaveLength(1);
      vi.advanceTimersByTime(1);
      expect(useToastStore.getState().toasts).toHaveLength(0);
    });
  });
});
