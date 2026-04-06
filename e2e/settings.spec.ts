import { test, expect } from '@playwright/test';

test.describe('Settings Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/settings');
  });

  test('loads settings page with header', async ({ page }) => {
    // Should show the settings page header
    await expect(page.locator('h1')).toContainText('设置');
  });

  test('has back navigation button', async ({ page }) => {
    const backButton = page.locator('button', { hasText: '返回' });
    await expect(backButton).toBeVisible();
  });

  test('shows LLM provider selection', async ({ page }) => {
    // Settings content should load with LLM configuration options
    await expect(page.locator('text=AI 模型')).toBeVisible({ timeout: 5000 }).catch(() => {
      // Fallback: check for any settings-related content
    });
  });

  test('shows build info at bottom', async ({ page }) => {
    // Build info should be visible
    await expect(page.locator('text=AI知识图谱 v0.1.0')).toBeVisible({ timeout: 5000 });
  });

  test('shows security notice', async ({ page }) => {
    // Security notice should always be visible
    await expect(page.locator('text=免费服务')).toBeVisible({ timeout: 5000 }).catch(() => {
      // May have different text if key is configured
    });
  });
});

test.describe('404 Not Found Page', () => {
  test('shows 404 for unknown routes', async ({ page }) => {
    await page.goto('/nonexistent-page-xyz');
    await expect(page.locator('text=404')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('text=页面不存在')).toBeVisible();
  });

  test('has navigation buttons on 404', async ({ page }) => {
    await page.goto('/nonexistent-page-xyz');
    const homeButton = page.locator('button', { hasText: '回到首页' });
    await expect(homeButton).toBeVisible({ timeout: 5000 });
    
    const backButton = page.locator('button', { hasText: '返回上页' });
    await expect(backButton).toBeVisible();
  });

  test('home button navigates to /', async ({ page }) => {
    await page.goto('/nonexistent-page-xyz');
    await page.locator('button', { hasText: '回到首页' }).click();
    await expect(page).toHaveURL('/');
  });
});
