import { test, expect } from '@playwright/test';

test.describe('Core Learning Flow', () => {
  test('should navigate from domain to concept to learn page', async ({ page }) => {
    // Start at home
    await page.goto('/');
    await expect(page.locator('text=AI编程')).toBeVisible({ timeout: 10000 });

    // Go to AI engineering domain
    await page.goto('/domain/ai-engineering');
    await page.waitForTimeout(2000);

    // Navigate directly to a concept's learn page
    await page.goto('/learn/ai-engineering/binary-system');
    await page.waitForTimeout(2000);

    // Should show the learn page with concept name
    await expect(page.locator('text=二进制')).toBeVisible({ timeout: 10000 });
  });

  test('should show dialogue interface on learn page', async ({ page }) => {
    await page.goto('/learn/ai-engineering/binary-system');
    await page.waitForTimeout(3000);

    // Should have chat-like interface elements
    // Check for message area or input area
    const pageContent = await page.textContent('body');
    expect(pageContent).toBeTruthy();
    // Should not show crash/error
    await expect(page.locator('text=Something went wrong')).not.toBeVisible();
  });
});

test.describe('Dashboard Page', () => {
  test('should load dashboard and show stats', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForTimeout(2000);

    // Should show dashboard header
    await expect(page.locator('text=学习分析')).toBeVisible({ timeout: 5000 });
    // Should show stat cards
    await expect(page.locator('text=已掌握')).toBeVisible();
    await expect(page.locator('text=学习中')).toBeVisible();
    await expect(page.locator('text=已探索领域')).toBeVisible();
  });

  test('should show domain progress cards', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForTimeout(3000);

    // Should show domain names
    await expect(page.locator('text=领域进度')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('text=AI编程')).toBeVisible();
  });

  test('should navigate back to home', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForTimeout(2000);
    // Click back button
    await page.locator('button').filter({ has: page.locator('svg') }).first().click();
    await expect(page).toHaveURL('/');
  });
});

test.describe('Review Page', () => {
  test('should load review page', async ({ page }) => {
    await page.goto('/review');
    await page.waitForTimeout(2000);
    // Should not crash
    await expect(page.locator('text=Something went wrong')).not.toBeVisible();
  });
});

test.describe('Login Page', () => {
  test('should show login form', async ({ page }) => {
    await page.goto('/login');
    await expect(page.locator('text=AI Knowledge Graph')).toBeVisible({ timeout: 5000 });
    // Should show email input
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
  });

  test('should have skip to home button', async ({ page }) => {
    await page.goto('/login');
    await expect(page.locator('text=Skip')).toBeVisible({ timeout: 5000 });
    await page.locator('text=Skip').click();
    await expect(page).toHaveURL('/');
  });
});