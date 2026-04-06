import { test, expect } from '@playwright/test';

test.describe('Dashboard — Learning Analytics', () => {
  test('should load dashboard page', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.locator('text=学习分析')).toBeVisible({ timeout: 10000 });
  });

  test('should show global stats cards', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.locator('text=已掌握')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=学习中')).toBeVisible();
    await expect(page.locator('text=已探索领域')).toBeVisible();
    await expect(page.locator('text=连续学习')).toBeVisible();
  });

  test('should show mastery distribution chart', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.locator('text=掌握度分布')).toBeVisible({ timeout: 10000 });
  });

  test('should show streak calendar', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.locator('text=学习日历')).toBeVisible({ timeout: 10000 });
  });

  test('should show domain progress section', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.locator('text=领域进度')).toBeVisible({ timeout: 10000 });
  });

  test('should navigate back to homepage', async ({ page }) => {
    await page.goto('/dashboard');
    // Click back button
    await page.locator('button').first().click();
    await expect(page).toHaveURL('/');
  });
});
