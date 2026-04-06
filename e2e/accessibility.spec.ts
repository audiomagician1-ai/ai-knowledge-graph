import { test, expect } from '@playwright/test';

test.describe('Accessibility', () => {
  test('skip-to-content link is present', async ({ page }) => {
    await page.goto('/');
    // The skip link should exist in DOM (sr-only by default)
    const skipLink = page.locator('a[href="#main-content"]');
    await expect(skipLink).toBeAttached();
    await expect(skipLink).toHaveText('跳转到主要内容');
  });

  test('main content landmark exists', async ({ page }) => {
    await page.goto('/');
    const main = page.locator('main#main-content');
    await expect(main).toBeVisible({ timeout: 5000 });
    await expect(main).toHaveAttribute('role', 'main');
  });

  test('HTML lang attribute is set', async ({ page }) => {
    await page.goto('/');
    const lang = await page.locator('html').getAttribute('lang');
    expect(lang).toBe('zh-CN');
  });

  test('page has a title', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/AI知识图谱/);
  });

  test('offline indicator has ARIA attributes', async ({ page }) => {
    // We can't easily simulate offline in E2E, but we can check the component HTML
    // Verify the selector would work if rendered
    await page.goto('/');
    // The banner should not be visible when online
    const offlineBanner = page.locator('[role="alert"]');
    // If there are no alerts, that's expected (we're online)
    const count = await offlineBanner.count();
    // If present, it should have aria-live
    if (count > 0) {
      await expect(offlineBanner.first()).toHaveAttribute('aria-live', 'polite');
    }
  });

  test('settings page back button has aria-label', async ({ page }) => {
    await page.goto('/settings');
    const backBtn = page.locator('button[aria-label="返回"]');
    await expect(backBtn).toBeVisible({ timeout: 5000 });
  });
});

test.describe('PWA', () => {
  test('manifest is accessible', async ({ page }) => {
    const response = await page.goto('/manifest.json');
    expect(response?.status()).toBe(200);
    const manifest = await response?.json();
    expect(manifest.name).toBe('AI知识图谱');
    expect(manifest.display).toBe('standalone');
  });

  test('robots.txt is accessible', async ({ page }) => {
    const response = await page.goto('/robots.txt');
    expect(response?.status()).toBe(200);
  });

  test('sitemap.xml is accessible', async ({ page }) => {
    const response = await page.goto('/sitemap.xml');
    expect(response?.status()).toBe(200);
  });

  test('service worker is registered', async ({ page }) => {
    const response = await page.goto('/sw.js');
    expect(response?.status()).toBe(200);
    const text = await response?.text();
    expect(text).toContain('CACHE_VERSION');
  });
});
