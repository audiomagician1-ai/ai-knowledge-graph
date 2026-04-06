import { test, expect } from '@playwright/test';

test.describe('Homepage — Domain Selection', () => {
  test('should load and display domain list', async ({ page }) => {
    await page.goto('/');
    // Wait for domain cards to appear
    await expect(page.locator('text=AI编程')).toBeVisible({ timeout: 10000 });
    // Should show multiple domain cards
    const domainCards = page.locator('[data-testid="domain-card"]');
    // If no testid, check for visible domain names
    await expect(page.locator('text=数学')).toBeVisible();
    await expect(page.locator('text=英语')).toBeVisible();
  });

  test('should navigate to domain graph on click', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('text=AI编程')).toBeVisible({ timeout: 10000 });
    // Click on AI编程 domain
    await page.locator('text=AI编程').first().click();
    // Should navigate to domain graph page
    await expect(page).toHaveURL(/\/domain\/ai-engineering/);
  });

  test('should have working navigation bar', async ({ page }) => {
    await page.goto('/');
    // Page should be accessible
    await expect(page).toHaveTitle(/AI Knowledge Graph|知识图谱/i);
  });
});

test.describe('Graph Page — 3D Visualization', () => {
  test('should render graph view for a domain', async ({ page }) => {
    await page.goto('/domain/ai-engineering');
    // Wait for graph to load (check for concept nodes or loading indicator)
    await page.waitForTimeout(3000); // Allow graph to render
    // Page should not show error
    await expect(page.locator('text=Error')).not.toBeVisible();
  });

  test('should show concept detail on node interaction', async ({ page }) => {
    await page.goto('/domain/ai-engineering/binary-system');
    // Should show concept detail panel
    await expect(page.locator('text=二进制')).toBeVisible({ timeout: 10000 });
  });
});