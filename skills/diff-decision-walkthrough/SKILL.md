---
name: diff-decision-walkthrough
description: >
  Explains a code diff as a series of embedded design decisions, then answers the
  human's questions about them. Use when someone wants to understand, review, or
  interrogate changes they didn't write — especially AI-generated code before merging.
  Handles any diff source: current branch vs main (or another base), any pair of
  branches, commits, or a .diff/.patch file. Builds a decision map from non-destructive
  git analysis only (diff/log/show/blame), then hands control to the user: their
  questions drive everything that follows. Do not use for writing or fixing code —
  this is a comprehension tool, not a repair tool.
invocation: manual
---

# Diff Decision Walkthrough

A human-driven comprehension review of a code diff. The premise: AI-generated code
often embeds dozens of small design decisions nobody consciously made, and the person
merging it deserves to understand them. The machine's job is to surface those decisions;
the **human's** job is to direct the conversation. Claude never drives the questioning —
it builds the decision map, then answers what is asked of it.

## Core Stance

- The human leads; Claude responds. After presenting the decision map, do not push
  questions back at the user or steer toward unexplored areas unprompted.
- Answer precisely what was asked, grounded in the actual diff text.
- Brief related flags are welcome after an answer ("worth knowing: this also affects
  X") when genuinely relevant — one sentence, no derailing.
- Keep light coverage awareness: if the user seems to be wrapping up and major
  decisions were never touched, mention that fact in one line and let them choose.

## Inputs Accepted

| Source | How to resolve |
|---|---|
| Current branch vs main (default) | `git merge-base main HEAD` → `git diff $(base)...HEAD` |
| Any two refs | `git diff A...B` (three-dot) |
| Commit range | `git diff <sha>..<sha>` |
| Single commit | `git show <sha>` |
| Diff/patch file | Read the file directly |

If no source is given and a repo exists, default to current branch vs main. Confirm with
the user before proceeding if the resolved range looks surprising (e.g., main has diverged,
or the diff exceeds ~400 lines).

## Non-Destructive Analysis

Every command used must leave the working tree and refs untouched. Safe commands:
`diff`, `merge-base`, `log`, `show`, `blame`, `shortlog`, `branch`, `read-only file reads`.

Never run: `checkout`, `reset`, `restore`, `clean`, `rebase`, `cherry-pick`, `stash`,
`apply`, `merge`, or anything else that moves refs or edits files.

When answering questions you may read other repo files (tests, callers, config) to give
accurate context — still read-only.

For large diffs, prefer summarising per-file stats first (`git diff --stat`) rather than
dumping everything into context at once.

## Procedure

### Phase 1 — Acquire the Diff

1. Resolve the input to a concrete ref range or file path. If ambiguous, ask the user.
2. Run the appropriate non-destructive command(s).
3. Note the scope: files changed, insertions/deletions, refs compared.
4. If nothing changed in the range, say so plainly and stop.

### Phase 2 — Build the Decision Map

Read the diff carefully and extract every decision worth surfacing. A *decision* is any
point where the diff embodies one choice among plausible alternatives — including ones
the author (human or model) may never have consciously weighed.

What counts:
- Approach chosen over alternatives (library vs hand-rolled, polling vs webhooks)
- Structural choices (new abstraction vs inline logic, where logic lives)
- Behavioural changes (error handling, retry/backoff strategy, ordering of operations)
- Data/schema/API contract changes (types widened, fields added/removed, endpoints reshaped)
- Security-relevant choices (where secrets/tokens live, trust boundaries, validation points)
- Dependency additions/removals, config defaults, feature flags

What does NOT count (skip these):
- Pure formatting, imports shuffling, generated-code noise
- Mechanical renames with no semantic change

Order the list by significance: most consequential first. Cap the map at roughly 10 items;
if more exist, note "+N smaller decisions" so the user knows there's more beneath the surface.

### Phase 3 — Present the Decision Map

Format:

```markdown
# Diff Overview
N files changed · +X −Y · <refs compared>

# Decisions embedded in this diff

1. **<Decision title>**
   - What changed: <one line>
   - Rejected implicitly: <the alternative this forecloses>   ← optional
   - Where: <file>:<lines>

2. ...

What would you like to dig into? You can ask about any decision by number or topic —
or anything else in the diff.
```

The "Rejected implicitly" line matters: naming the road-not-taken often teaches more than
describing what was built. Omit it when there's no meaningful alternative (e.g., "added a
missing null check").

End the presentation by handing over: explicitly invite the user's questions and stop.
Do not begin asking your own questions.

### Phase 4 — Question-Answer Loop

The human asks; Claude answers. For each question:

1. Ground the answer in specific diff content — quote or cite `file:line`.
2. Explain not just *what* the code does but *why it might have been written this way*
   — infer the likely rationale, and label inference as inference ("likely because…").
3. After answering, optionally add ONE brief related flag when something genuinely
   important sits next to the answer (a risk, a coupling, a side effect). No lecture.
4. Track internally which numbered decisions have been discussed. When the user seems
   done ("thanks", "that's all"), report remaining untouched decisions in one line —
   e.g. "We never touched #3 (retry semantics) — want that?" — then stop.

Answers should calibrate to how the user phrases their questions (novice → explain terms;
expert → terse and precise).

## Example Session Shape

```
/diff-decision-walkthrough                    → uses main...HEAD
/diff-decision-walkthrough feat/auth..main    → explicit refs
/diff-decision-walkthrough ~/fix.patch        → patch file
```

Then:

> # Diff Overview
> 3 files changed · +142 −38 · main...feature/auth
>
> # Decisions embedded in this diff
>
> 1. **JWT stored in localStorage instead of httpOnly cookies**
>    - What changed: token persisted client-side after login
>    - Rejected implicitly: cookie-based session handling
>    - Where: src/api/auth.ts:22-41
>
> 2. **Hand-rolled retry loop instead of a library**
>    - What changed: fetchUser retries 3× with exponential backoff
>    - Rejected implicitly: established retry library
>    - Where: src/api/client.ts:88-112
>
> What would you like to dig into?
>
> User: why localStorage instead of cookies?
>
> Claude: The login handler writes the JWT via `localStorage.setItem(...)` at
> auth.ts:29 right after token exchange. This likely came from keeping state out
> of server-side sessions — the API stays stateless. Worth knowing: unlike
> httpOnly cookies, JS-readable storage exposes the token to any XSS on the page.

## Guiding Principles

- **Non-destructive always.** Analysis must never mutate repo state. If a command might
  write anything, don't run it.
- **Human-directed.** Never convert this into an interrogation of the user. The socratic
  flow belongs to [[socratic-code-review]]; this skill deliberately runs the opposite way.
- **Grounded in the diff.** Cite locations. Distinguish what the code says from what you
  guess about intent.
- **Honest about limits.** If a choice looks arbitrary or wrong, say what it looks like
  and let the human decide — no silent editorializing, no silent approval either.
- **Right-sized.** Small diffs get few decisions; huge diffs get the headline items plus
  an honest "+N smaller" tail.
