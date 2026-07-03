---
applyTo: "**/*.test.*,**/*.spec.*"
---

# Test file conventions

Apply these rules whenever editing or creating test files.

## Structure

- One test file per source file, co-located or in a `__tests__/` sibling folder.
- File naming: `<module>.test.<ext>` or `<module>.spec.<ext>` — match the project convention.
- Group related assertions using `describe` blocks named after the unit under test.
- Use `it` or `test` with a description in plain English: "returns null when input is empty".

## What to test

- **Happy path:** the expected output for typical, valid input.
- **Edge cases:** empty string, zero, null/undefined, empty array, boundary values.
- **Error cases:** invalid input, network failure, missing dependency — verify the correct error or fallback behaviour.

## Assertions

- Assert on **behaviour and structure**, not on UI copy, pixel values, or design tokens.
- One logical assertion per test; group multi-step sequences in a single `it` with clear comments.
- Prefer `toEqual` over `toBe` for objects to avoid reference-equality failures.

## Mocking and isolation

- Mock all external services (HTTP, databases, file system, timers).
- Reset all mocks between tests (`beforeEach`/`afterEach`).
- Do not test implementation details (private methods, internal state) — test the public contract only.

## Coverage targets

- Aim for 80 % line coverage on business-logic modules.
- Do not chase 100 % — untested error branches that require environment failures are acceptable if documented with a comment.

## Anti-patterns to avoid

- Tests that pass without assertions (`expect` with no matcher).
- Tests that depend on execution order.
- Snapshot tests for large data structures — prefer explicit field assertions.
- Committing `console.log` calls in test files.
