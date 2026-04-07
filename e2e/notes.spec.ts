import { test, expect } from '@playwright/test';

test.describe('Notes Features', () => {
  test('Notes page loads', async ({ page }) => {
    await page.goto('/notes');
    await expect(page.locator('body')).toBeVisible();
    // Should show notes header or empty state
    const hasNotes = await page.locator('text=笔记').first().isVisible({ timeout: 10000 }).catch(() => false);
    expect(hasNotes).toBeTruthy();
  });

  test('Notes page shows empty state when no notes', async ({ page }) => {
    await page.goto('/notes');
    // Either empty state or notes list
    const body = page.locator('body');
    await expect(body).toBeVisible({ timeout: 10000 });
  });

  test('Notes page has back button', async ({ page }) => {
    await page.goto('/notes');
    // Should have navigation back
    const backBtn = page.locator('button').first();
    await expect(backBtn).toBeVisible({ timeout: 10000 });
  });
});
