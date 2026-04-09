/**
 * V2.12 — Community split + Discussion subcomponents tests.
 */
import { describe, it, expect } from 'vitest';

// ── DiscussionForm ──
describe('DiscussionForm component', () => {
  it('exports DiscussionForm and TYPE_CONFIG', async () => {
    const mod = await import('../components/community/DiscussionForm');
    expect(mod.DiscussionForm).toBeDefined();
    expect(typeof mod.DiscussionForm).toBe('function');
    expect(mod.TYPE_CONFIG).toBeDefined();
    expect(Object.keys(mod.TYPE_CONFIG)).toEqual(['question', 'insight', 'resource', 'explanation']);
  });

  it('TYPE_CONFIG has correct structure', async () => {
    const { TYPE_CONFIG } = await import('../components/community/DiscussionForm');
    for (const [, cfg] of Object.entries(TYPE_CONFIG)) {
      expect(cfg).toHaveProperty('icon');
      expect(cfg).toHaveProperty('label');
      expect(cfg).toHaveProperty('color');
      expect(typeof cfg.label).toBe('string');
      expect(cfg.color).toMatch(/^#[0-9a-f]{6}$/i);
    }
  });
});

// ── DiscussionListItem ──
describe('DiscussionListItem component', () => {
  it('exports DiscussionListItem and types', async () => {
    const mod = await import('../components/community/DiscussionListItem');
    expect(mod.DiscussionListItem).toBeDefined();
    expect(typeof mod.DiscussionListItem).toBe('function');
  });
});

// ── Refactored ConceptDiscussionPanel ──
describe('ConceptDiscussionPanel (refactored)', () => {
  it('still exports ConceptDiscussionPanel', async () => {
    const mod = await import('../components/community/ConceptDiscussionPanel');
    expect(mod.ConceptDiscussionPanel).toBeDefined();
    expect(typeof mod.ConceptDiscussionPanel).toBe('function');
  });
});

// ── NotificationsPage still works ──
describe('NotificationsPage', () => {
  it('exports NotificationsPage', async () => {
    const mod = await import('../pages/NotificationsPage');
    expect(mod.NotificationsPage).toBeDefined();
  });
});

// ── ContentFeedbackButton still works ──
describe('ContentFeedbackButton', () => {
  it('exports ContentFeedbackButton', async () => {
    const mod = await import('../components/community/ContentFeedbackButton');
    expect(mod.ContentFeedbackButton).toBeDefined();
  });
});
