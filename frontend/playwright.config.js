import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 60_000,
  expect: { timeout: 5000 },
  use: { headless: true, baseURL: 'http://localhost:3001' },
  projects: [ { name: 'chromium', use: { browserName: 'chromium' } } ],
});
