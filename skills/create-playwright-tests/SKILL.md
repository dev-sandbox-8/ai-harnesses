---
name: create-playwright-tests
description: >
  Generates or updates Playwright end-to-end tests for a web application. Initializes
  config if needed, places tests pragmatically, and follows best practices: correct
  HTTP methods, no default values, manual actions preferred over mocks.
invocation: manual
---

# Create Playwright Tests Skill

Write or update end-to-end tests using Playwright. The skill adapts to project size and structure.

## Usage

```
/create-playwright-tests [target] [options]
```

- `target` — optional path. Defaults to the current working directory.
- `options`:
  - `--scenarios` — comma-separated scenario names to generate
  - `--update` — update existing test file instead of creating new
  - `--force-pom` — force Page Object Model (default: decide based on project size)

## Pre-flight Checks

1. Check if `package.json` exists. If not, create a minimal one.
2. Check if `playwright.config.ts` exists. If not, create it with sensible defaults.
3. Determine test location:
   - If `e2e/` or `tests/e2e/` exists, use that directory
   - If `tests/` exists, create `tests/playwright/` subdirectory
   - If neither exists, create `tests/playwright/`
4. Scan for existing Playwright tests to understand current patterns and naming conventions.
5. Identify the target application's tech stack (React, Vue, Angular, vanilla) to tailor test code.

## Step 1: Initialize Playwright (if needed)

If `package.json` lacks Playwright:

```json
"devDependencies": {
  "@playwright/test": "^1.40.0"
},
"scripts": {
  "test:e2e": "playwright test",
  "test:e2e:ui": "playwright test --ui",
  "test:e2e:debug": "playwright test --debug"
}
```

Create `playwright.config.ts` with:

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/playwright',
  timeout: 30_000,
  expect: { timeout: 5_000 },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [['html'], ['list']],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],
});
```

Install dependencies with `npm install` or equivalent.

## Step 2: Decide Test Architecture

Measure project size by counting testable pages/components:

- **Small (< 5 pages)**: Use direct locators in spec files. Simpler, less boilerplate.
- **Medium (5-15 pages)**: Use Page Object Model with shared components.
- **Large (> 15 pages) or `--force-pom`**: Use full Page Object Model with component-based locators.

## Step 3: Generate Test Spec

For each scenario, create a test file following this structure:

### Template (Small Projects)

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature: <feature-name>', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('<route>');
  });

  test('should <expected-behavior>', async ({ page }) => {
    // Manual action preferred over mocks
    // Navigate and interact directly with the UI
    
    // If API interaction is required:
    // - Use the correct HTTP method (POST for create, PUT/PATCH for update, DELETE for delete, GET for read)
    // - Do NOT use default values from UI — explicitly set unique test values to catch special cases
    
    await page.getByRole('button', { name: /submit/i }).click();
    await expect(page).toHaveURL(/success/);
    await expect(page.getByRole('status')).toContainText('Success');
  });
});
```

### Template (POM - Medium/Large Projects)

```
tests/playwright/
├── pages/
│   ├── <feature>Page.ts
│   └── components/
├── fixtures/
│   └── test-data.ts
└── <feature>.spec.ts
```

Create `pages/<feature>Page.ts`:

```typescript
import { Locator, Page } from '@playwright/test';

export class <Feature>Page {
  readonly page: Page;
  readonly submitButton: Locator;
  readonly inputField: Locator;
  readonly statusMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.submitButton = page.getByRole('button', { name: /submit/i });
    this.inputField = page.getByLabel('Input');
    this.statusMessage = page.getByRole('status');
  }

  async goto() {
    await this.page.goto('/<route>');
  }

  async fillInput(value: string) {
    // Do not use default values — explicitly set unique test data
    await this.inputField.fill(value);
  }

  async submit() {
    await this.submitButton.click();
  }
}
```

## Step 4: HTTP Method Enforcement

When tests involve API calls, always use the correct method:

| Operation | Method | Example |
|---|---|---|
| Create resource | `POST` | `apiContext.post('/users', data)` |
| Read resource | `GET` | `apiContext.get('/users/123')` |
| Update resource | `PUT` or `PATCH` | `apiContext.patch('/users/123', data)` |
| Delete resource | `DELETE` | `apiContext.delete('/users/123')` |
| Search/filter | `GET` with query params | `apiContext.get('/users?role=admin')` |

Never use GET for writes. Never use POST for reads.

## Step 5: Test Data Strategy

**Do not use default values shown in the UI** — they hide bugs. Instead:

```typescript
// BAD: Uses default 'Admin' from dropdown
await page.selectOption('#role', 'Admin');

// GOOD: Uses non-default value to test special cases
await page.selectOption('#role', 'Super Admin');
```

Generate unique test data when possible:

```typescript
const uniqueEmail = `test-${Date.now()}@example.com`;
const uniqueName = `Test User ${Math.random().toString(36).slice(2, 8)}`;
```

## Step 6: Manual Actions Over Mocks

Prefer real interactions:

```typescript
// PREFERRED: Real UI interaction
await page.getByRole('textbox', { name: 'Email' }).fill('new-user@example.com');
await page.getByRole('button', { name: 'Create Account' }).click();
await expect(page).toHaveURL(/\/dashboard/);

// AVOID: Mocking network calls unless absolutely necessary
// await page.route('**/api/users', route => route.fulfill({...}));
```

Only mock when:
- External service is unavailable in test environment
- Test would have side effects on real data
- Rate limiting makes real calls impractical

## Step 7: Generate Scenarios

If `--scenarios` not provided, derive scenarios from:

1. Page routes in the application
2. User stories in `Planning/` or `docs/user-stories.md`
3. Feature flags or menus in the UI
4. API endpoints in OpenAPI specs or REST clients

Default scenarios to always generate if applicable:

- Login/authentication flow
- Primary user journey (core feature)
- Form submission with validation
- Error state handling
- Data listing and pagination (if applicable)

## Step 8: Write Tests

Create test files in `<test-dir>/` following the project's naming convention:

- `<feature>.spec.ts` for feature tests
- `<feature>.page.ts` for Page Objects (if POM)
- `api-client.ts` for API helpers (if needed)

Each test should:

1. Have a clear, descriptive name
2. Be independent (no order dependency)
3. Clean up after itself (delete test data, reset state)
4. Use role-based selectors (`getByRole`) over CSS selectors when possible
5. Include assertions for both success and failure paths

## Step 9: Validate and Report

After writing tests:

1. Run `npx playwright test --dry-run` to check syntax.
2. Verify no default values are used in assertions or inputs.
3. Confirm HTTP methods match the API specification.
4. Print a summary:

```
Playwright tests generated for /path/to/project
- Test files created: N
- Page objects created: N (if POM)
- Config initialized: yes/no
- Scenarios covered: <list>
```

## Best Practices Summary

1. **HTTP Methods**: POST for create, GET for read, PUT/PATCH for update, DELETE for delete
2. **No Default Values**: Always test with non-default inputs to catch edge cases
3. **Manual Actions**: UI interactions over mocks, mocks as fallback only
4. **Role-based Selectors**: Use `getByRole`, `getByLabel`, `getByText` before CSS selectors
5. **Clean State**: Each test independent, no shared state between runs
6. **Clear Names**: `test('should show error when email is invalid', ...)` not `test('form validation', ...)`
7. **Trace on Retry**: Enable trace collection for debugging failed tests
8. **Parallel Execution**: Tests should run in parallel, avoid shared resources