const { defineConfig, devices } = require('@playwright/test');
module.exports = defineConfig({
  testDir: './tests/e2e',
  timeout: 45000,
  expect: { timeout: 10000 },
  fullyParallel: true,
  workers: 2,
  reporter: [['list'], ['html', { open: 'never', outputFolder: 'playwright-report' }]],
  use: {
    baseURL: 'http://127.0.0.1:8765',
    browserName: 'chromium',
    headless: true,
    // Animations off, so a click never races a sliding bar or a fading section.
    // One test turns motion back on to check that every animated section still appears.
    reducedMotion: 'reduce',
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure'
  },
  webServer: {
    command: 'python3 tests/e2e/serve.py',
    url: 'http://127.0.0.1:8765/students.html',
    timeout: 15000,
    reuseExistingServer: false
  }
});
