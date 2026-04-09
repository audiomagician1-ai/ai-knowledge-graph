import { describe, it, expect } from 'vitest';

describe('V2.13 Final FE Code Health — extracted components', () => {
  describe('LoginPageParts', () => {
    it('exports BackgroundDecoration, FeaturePills, LoginEmailForm', async () => {
      const mod = await import('@/components/auth/LoginPageParts');
      expect(mod.BackgroundDecoration).toBeDefined();
      expect(mod.FeaturePills).toBeDefined();
      expect(mod.LoginEmailForm).toBeDefined();
    });
  });

  describe('useHomeCanvas hook', () => {
    it('exports useHomeCanvas function', async () => {
      const mod = await import('@/lib/hooks/useHomeCanvas');
      expect(typeof mod.useHomeCanvas).toBe('function');
    });
  });

  describe('useGraphEffects hook', () => {
    it('exports useGraphEffects function', async () => {
      const mod = await import('@/lib/hooks/useGraphEffects');
      expect(typeof mod.useGraphEffects).toBe('function');
    });
  });

  describe('ReviewStates', () => {
    it('exports ReviewError, ReviewEmpty, ReviewComplete', async () => {
      const mod = await import('@/components/review/ReviewStates');
      expect(mod.ReviewError).toBeDefined();
      expect(mod.ReviewEmpty).toBeDefined();
      expect(mod.ReviewComplete).toBeDefined();
    });
  });

  describe('HistoryItemRow', () => {
    it('exports HistoryItemRow, ACTION_LABELS, ACTION_ICONS, ACTION_COLORS', async () => {
      const mod = await import('@/components/history/HistoryItemRow');
      expect(mod.HistoryItemRow).toBeDefined();
      expect(mod.ACTION_LABELS).toHaveProperty('mastered', '掌握');
      expect(mod.ACTION_LABELS).toHaveProperty('assessment', '评估');
      expect(mod.ACTION_ICONS).toHaveProperty('mastered');
      expect(mod.ACTION_COLORS).toHaveProperty('mastered');
    });
  });

  describe('ReportParts', () => {
    it('exports StatCard and ReportData type structure', async () => {
      const mod = await import('@/components/report/ReportParts');
      expect(mod.StatCard).toBeDefined();
    });
  });

  describe('SettingsProxyGuide', () => {
    it('exports SettingsProxyActions', async () => {
      const mod = await import('@/components/settings/SettingsProxyGuide');
      expect(mod.SettingsProxyActions).toBeDefined();
    });
  });

  describe('RadarSVG', () => {
    it('exports RadarSVG component', async () => {
      const mod = await import('@/components/dashboard/RadarSVG');
      expect(mod.RadarSVG).toBeDefined();
    });
  });

  describe('NoteCard', () => {
    it('exports NoteCard component', async () => {
      const mod = await import('@/components/notes/NoteCard');
      expect(mod.NoteCard).toBeDefined();
    });
  });

  describe('ConceptSearchTypes', () => {
    it('can import SearchResult type module', async () => {
      const mod = await import('@/components/common/ConceptSearchTypes');
      expect(mod).toBeDefined();
    });
  });
});
