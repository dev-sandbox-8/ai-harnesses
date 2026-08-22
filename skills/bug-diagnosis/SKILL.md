---
name: bug-diagnosis
description: "Use when: investigating a bug, unexpected behavior, test failure, or error. Asks targeted clarifying questions one at a time using the ask-questions tool to build a precise mental model before proposing any fix. Avoids premature diagnosis. Use before touching code."
argument-hint: "Optional: paste an error message or describe the symptom to seed the first question."
---

# Bug Diagnosis

## Purpose

Systematically narrow down a bug to its root cause by asking one focused clarifying question at a time, then implement a targeted fix.

## When to Use

- A feature is broken or behaving unexpectedly
- A test is failing and the cause is unclear
- An error message is confusing or misleading
- You have a hunch but want to verify before changing code

## Procedure

### Phase 1 — Gather Context (one question at a time)

Ask questions in this order, but **skip any that were already answered** in the user's initial description. Only ask what you still need.

**Round 1 — Symptom**
Ask: What exact behavior are you seeing, and what did you expect instead? (Include any error messages or stack traces.)

**Round 2 — Reproducibility**
Ask: Can you reproduce this reliably? If so, what are the minimal steps to trigger it?

**Round 3 — Regression**
Ask: Was this working before? If yes, what changed most recently (code, config, dependency, environment)?

**Round 4 — Evidence**
Ask: Are there any logs, console output, or observable side-effects that give clues about where it's failing?

**Round 5 — Prior attempts**
Ask: What have you already tried, and what happened?

### Phase 2 — Diagnose

Once you have enough answers:
1. State your working hypothesis about the root cause in one sentence.
2. Identify the exact file(s) and line(s) most likely responsible.
3. If the hypothesis is uncertain, share your confidence level and what evidence would confirm it.
4. Ask one final confirmation question if needed — otherwise proceed.

### Phase 3 — Fix

Apply the minimal targeted fix:
1. Read the relevant code before changing anything.
2. Make the smallest possible change that addresses the root cause.
3. Do not refactor unrelated code.
4. Run relevant tests or linting after the fix.

### Phase 4 — Verify

1. Confirm the fix resolves the reported symptom.
2. Check for regression risk in adjacent code.
3. Report: what was broken, why, and what was changed.

## Rules

- **One question per turn.** Never ask multiple questions in the same message.
- **Use `vscode_askQuestions`** for all clarifying questions — do not embed them in prose.
- **Never propose a fix before completing Phase 1** unless the cause is definitively obvious from the initial description.
- **Prefer reading code over guessing.** Use file search and grep before forming a hypothesis.
- Keep fixes minimal. If a proper fix requires significant refactoring, flag it and implement the smallest safe change first.
