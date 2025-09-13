import { test } from '@playwright/test';

test('diagnostic: capture browser console and errors', async ({ page }) => {
  console.log('Starting diagnostic run: attaching listeners');

  page.on('console', msg => {
    const location = msg.location();
    console.log(`[browser console] ${msg.type()} ${msg.text()} ${location?.url || ''}:${location?.lineNumber || ''}`);
  });

  page.on('pageerror', err => {
    console.log(`[page error] ${err?.name}: ${err?.message}`);
    if (err?.stack) console.log(err.stack);
  });

  page.on('requestfailed', req => {
    console.log(`[request failed] ${req.method()} ${req.url()} - ${req.failure()?.errorText || 'unknown'}`);
  });

  page.on('response', resp => {
    // Log non-2xx responses for static assets
    if (resp.status() >= 400) {
      console.log(`[response ${resp.status()}] ${resp.url()}`);
    }
  });

  await page.goto('/');
  console.log('Navigated to /, waiting 20s to capture console output...');

  // Wait a bit to allow scripts to run and emit errors
  await page.waitForTimeout(20000);

  console.log('Diagnostic run complete');
});
