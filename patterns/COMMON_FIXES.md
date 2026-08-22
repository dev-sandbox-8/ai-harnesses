# Common Fix Patterns

## Next.js + NextAuth Patterns

| Symptom | Fix |
|---|---|
| "Loading..." forever on protected page | Use `fetch('/api/...', { credentials: 'include' })` |
| API returns 401 | Add `credentials: 'include'` to fetch calls |
| TypeScript Date arithmetic errors | Use intermediate variable for calculation |
| Playwright timeout on auth route | Wait for session first, use relative paths |

**Golden Rules:**
1. Relative paths only — `/api/...` never conditional absolute URLs
2. Always `credentials: 'include'` on protected endpoints
3. Fix minimal issues first

---

## Debug Commands

```javascript
// Check auth
fetch('/api/auth/session', { credentials: 'include' })

// Check cookies
document.cookie // Should show NEXTAUTH_SESSION
```

---

## Test Writing (Progressive Complexity)

**Phase 1: UI Tests**
```typescript
test("page loads and shows expected content", async ({ page }) => {
  await page.goto("/path");
  expect(await page.locator('main').count()).toBeGreaterThan(0);
});
```

**Phase 2: Interaction Tests**
Add form interactions, button clicks, navigation.

**Phase 3: API Tests** (requires DB/auth)
Skip in CI until infrastructure ready.