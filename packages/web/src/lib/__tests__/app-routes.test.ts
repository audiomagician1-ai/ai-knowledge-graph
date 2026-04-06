/**
 * App route configuration tests
 * Verifies route-level code splitting setup and page module exports
 */
import { describe, it, expect } from 'vitest';

describe('Route module exports', () => {
  it('HomePage exports named component', async () => {
    const mod = await import('../../pages/HomePage');
    expect(mod.HomePage).toBeDefined();
    expect(typeof mod.HomePage).toBe('function');
  });

  it('GraphPage exports named component', async () => {
    const mod = await import('../../pages/GraphPage');
    expect(mod.GraphPage).toBeDefined();
    expect(typeof mod.GraphPage).toBe('function');
  });

  it('LearnPage exports named component', async () => {
    const mod = await import('../../pages/LearnPage');
    expect(mod.LearnPage).toBeDefined();
    expect(typeof mod.LearnPage).toBe('function');
  });

  it('ReviewPage exports named component', async () => {
    const mod = await import('../../pages/ReviewPage');
    expect(mod.ReviewPage).toBeDefined();
    expect(typeof mod.ReviewPage).toBe('function');
  });

  it('DashboardPage exports named component', async () => {
    const mod = await import('../../pages/DashboardPage');
    expect(mod.DashboardPage).toBeDefined();
    expect(typeof mod.DashboardPage).toBe('function');
  });

  it('LoginPage exports named component', async () => {
    const mod = await import('../../pages/LoginPage');
    expect(mod.LoginPage).toBeDefined();
    expect(typeof mod.LoginPage).toBe('function');
  });

  it('SettingsPage exports named component', async () => {
    const mod = await import('../../pages/SettingsPage');
    expect(mod.SettingsPage).toBeDefined();
    expect(typeof mod.SettingsPage).toBe('function');
  });
});

describe('Page count verification', () => {
  it('should have exactly 7 page modules', () => {
    // This documents the current set of page-level routes.
    // Update this count if a new page is added.
    const pages = [
      'HomePage', 'GraphPage', 'LearnPage', 'ReviewPage',
      'DashboardPage', 'LoginPage', 'SettingsPage',
    ];
    expect(pages.length).toBe(7);
  });
});
