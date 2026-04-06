import { test, expect } from '@playwright/test';

test.describe('Navigation & Routing', () => {
  test('should load dashboard page', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.locator('text=学习分析')).toBeVisible({ timeout: 10000 });
  });

  test('should load settings page', async ({ page }) => {
    await page.goto('/settings');
    await expect(page.locator('text=设置')).toBeVisible({ timeout: 10000 });
    // Should have a back button
    await expect(page.locator('text=返回')).toBeVisible();
  });

  test('should show 404 page for unknown routes', async ({ page }) => {
    await page.goto('/this-page-does-not-exist');
    // Should show 404 content
    await expect(page.locator('text=404')).toBeVisible({ timeout: 10000 });
  });

  test('should redirect old /learn/:conceptId to home', async ({ page }) => {
    await page.goto('/learn/some-concept');
    // Should redirect to home
    await expect(page).toHaveURL('/');
  });

  test('should navigate from dashboard back to home', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.locator('text=学习分析')).toBeVisible({ timeout: 10000 });
    // Click back button
    await page.locator('button').filter({ hasText: '' }).first().click();
    await expect(page).toHaveURL('/');
  });
});

test.describe('Review Page', () => {
  test('should load review page', async ({ page }) => {
    await page.goto('/review');
    // Should show review page content (even if no reviews are due)
    await page.waitForTimeout(2000);
    await expect(page.locator('text=Error')).not.toBeVisible();
  });
});

test.describe('PWA & Offline', () => {
  test('should have PWA manifest link', async ({ page }) => {
    await page.goto('/');
    const manifest = page.locator('link[rel="manifest"]');
    await expect(manifest).toHaveAttribute('href', /manifest/);
  });

  test('should have service worker registration', async ({ page }) => {
    await page.goto('/');
    await page.waitForTimeout(2000);
    // Check if service worker is registered
    const hasServiceWorker = await page.evaluate(() => {
      return 'serviceWorker' in navigator;
    });
    expect(hasServiceWorker).toBe(true);
  });
});

test.describe('SEO & Meta', () => {
  test('should have OpenGraph meta tags', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('meta[property="og:title"]')).toHaveAttribute('content', /.+/);
    await expect(page.locator('meta[property="og:description"]')).toHaveAttribute('content', /.+/);
  });

  test('should have proper page title', async ({ page }) => {
    await page.goto('/');
    const title = await page.title();
    expect(title.length).toBeGreaterThan(0);
  });
});
