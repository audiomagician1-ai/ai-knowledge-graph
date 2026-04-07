import { test, expect } from '@playwright/test';

test.describe('Community Features', () => {
  test('Community page loads with correct heading', async ({ page }) => {
    await page.goto('/community');
    await expect(page.locator('h1:has-text("社区共建")')).toBeVisible({ timeout: 10000 });
  });

  test('Community page shows empty state', async ({ page }) => {
    await page.goto('/community');
    // Should show empty state or suggestions list
    const body = page.locator('body');
    await expect(body).toBeVisible();
    // Either empty state or suggestion cards
    const hasEmptyState = await page.locator('text=还没有社区建议').isVisible().catch(() => false);
    const hasSuggestions = await page.locator('text=条建议').isVisible().catch(() => false);
    expect(hasEmptyState || hasSuggestions).toBeTruthy();
  });

  test('Community page has submit button', async ({ page }) => {
    await page.goto('/community');
    const submitBtn = page.locator('button:has-text("提议")');
    await expect(submitBtn).toBeVisible({ timeout: 10000 });
  });

  test('Clicking submit opens form', async ({ page }) => {
    await page.goto('/community');
    await page.locator('button:has-text("提议")').click();
    // Form should appear with title input
    await expect(page.locator('text=提交新建议')).toBeVisible();
    await expect(page.locator('input[placeholder*="标题"]')).toBeVisible();
  });

  test('Admin mode toggle shows admin panel', async ({ page }) => {
    await page.goto('/community');
    // Click the shield icon to toggle admin mode
    const adminToggle = page.locator('button[title="管理员模式"]');
    await expect(adminToggle).toBeVisible({ timeout: 10000 });
    await adminToggle.click();
    // Admin panel should appear with token input
    await expect(page.locator('text=管理员模式')).toBeVisible();
    await expect(page.locator('input[placeholder*="管理员密钥"]')).toBeVisible();
  });

  test('Status filter buttons appear in admin mode', async ({ page }) => {
    await page.goto('/community');
    await page.locator('button[title="管理员模式"]').click();
    // Status filter buttons
    await expect(page.locator('button:has-text("全部")')).toBeVisible();
    await expect(page.locator('button:has-text("待审核")')).toBeVisible();
    await expect(page.locator('button:has-text("已通过")')).toBeVisible();
    await expect(page.locator('button:has-text("已拒绝")')).toBeVisible();
  });

  test('Navigating to community via home quick-nav', async ({ page }) => {
    await page.goto('/');
    const communityLink = page.locator('text=社区');
    if (await communityLink.isVisible().catch(() => false)) {
      await communityLink.click();
      await expect(page).toHaveURL(/\/community/);
    }
  });

  test('Escape key goes back to home', async ({ page }) => {
    await page.goto('/community');
    await expect(page.locator('h1:has-text("社区共建")')).toBeVisible({ timeout: 10000 });
    await page.keyboard.press('Escape');
    await expect(page).toHaveURL(/\/$/);
  });
});
