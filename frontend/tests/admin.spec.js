import { test, expect } from '@playwright/test';

// This test assumes a running dev server on localhost:3000 and backend on 8000.
// Set environment variables or ensure test admin credentials exist.
const ADMIN_EMAIL = process.env.TEST_ADMIN_EMAIL || 'admin@example.com';
const ADMIN_PW = process.env.TEST_ADMIN_PW || 'password123';

test('admin can acknowledge an alert from dashboard', async ({ page }) => {
  await page.goto('/login');
  await page.fill('input[placeholder="Enter your email"]', ADMIN_EMAIL);
  await page.fill('input[placeholder="Enter your password"]', ADMIN_PW);
  await page.click('button[type="submit"]');
  await page.waitForURL('**/admin', { timeout: 5000 }).catch(() => {});

  await page.evaluate(async () => {
    const token = localStorage.getItem('mindbloom_token');
    const res = await fetch('/api/admin/alerts/score', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ threshold: 0.8 }),
    });
    if (!res.ok) {
      throw new Error(`score endpoint failed: ${res.status}`);
    }
  });

  const alertsLoaded = page.waitForResponse((response) => response.request().method() === 'GET' && response.url().includes('/api/admin/alerts?status=new') && response.status() === 200);
  const statsLoaded = page.waitForResponse((response) => response.request().method() === 'GET' && response.url().includes('/api/admin/alerts/stats') && response.status() === 200);
  await page.goto('/admin');
  await Promise.all([alertsLoaded, statsLoaded]);

  const liveAlertsTable = page.getByRole('table', { name: 'Live alerts table' });
  await expect(liveAlertsTable).toBeVisible();

  const alertRows = liveAlertsTable.locator('tbody tr');
  await expect(alertRows.first()).toBeVisible();
  const beforeCount = await alertRows.count();
  await expect(beforeCount).toBeGreaterThan(0);

  const acknowledge = liveAlertsTable.locator('button', { hasText: 'Acknowledge' }).first();
  await expect(acknowledge).toBeVisible();
  await acknowledge.click();

  await page.getByRole('button', { name: 'Refresh', exact: true }).click();
  await page.waitForTimeout(500);
  await expect(alertRows).toHaveCount(beforeCount - 1);
  await expect(page.locator('.admin-panel-header').first()).toBeVisible();
});
