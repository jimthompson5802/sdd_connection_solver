import { defineConfig, devices } from '@playwright/test';

// Single-playwright config: starts frontend using `npm run start` and
// sets baseURL to http://localhost:8080 so tests using `page.goto('/')`
// will resolve correctly.
export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [['list'], ['html', { outputFolder: 'playwright-report' }]],
  use: {
    baseURL: 'http://localhost:8080',
    trace: 'on-first-retry',
    headless: true,
    viewport: { width: 1280, height: 720 },
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],
  webServer: {
    // Build first, then serve `dist/` with python3's http.server. Using
    // python3 avoids the `python` binary which may be missing on some macOS.
  command: 'npm run build && cd dist && python3 -m http.server 8080',
    cwd: __dirname,
    port: 8080,
    timeout: 180_000,
  reuseExistingServer: false,
  },
});
