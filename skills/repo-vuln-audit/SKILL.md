---
name: repo-vuln-audit
description: >
  Scan a repository for exposed secrets (API keys, tokens, private keys,
  hardcoded credentials) and overly-permissive GitHub policies (workflow
  permissions, pull_request_target RCE vectors, branch protection, repo
  visibility, CODEOWNERS). Use this skill whenever the user wants to audit a
  repo for security holes, check for leaked keys, harden CI/CD, review GitHub
  Actions permissions, assess whether a repository is safe to run Claude in
  auto mode against, or generally "check this repo for vulnerabilities /
  secrets / risky GitHub config". Read-only by design — it never writes or
  mutates files, so it is safe to run unattended.
invocation: manual
---

# Repo Vulnerability Audit

A read-only security audit of a repository focused on two high-leverage
surfaces: **exposed secrets** and **overly-permissive GitHub policy**.

## Why this skill exists

The user runs Claude in **auto mode inside a minimal-permission container** and
wants confidence that the repository it operates on won't leak credentials or
act as a pivot into their GitHub org. Two things cause almost all real damage
in that scenario:

1. **A leaked secret** (API key, token, private key) committed to the repo.
2. **An overly-permissive GitHub policy** that turns a typo, a dependency, or a
   malicious PR into code execution or a secret exfil.

Everything this skill does is **read-only**. It scans, reports, and recommends.
It never edits code, never rotates keys, never changes repo settings. That makes
it safe to invoke unattended — and it's exactly what you want running before
Claude is let loose in auto mode.

## When to use

- "Check this repo for exposed API keys / secrets"
- "Is it safe to run Claude in auto mode on this repo?"
- "Audit my GitHub Actions permissions / CI security"
- "Review this repo's branch protection / GitHub policy"
- "Scan for leaked credentials before I commit / before I containerize"

## Inputs

- `<repo-path>` — local path to the git repository (positional).
- Optionally, an authenticated `gh` CLI for live GitHub policy reads. If `gh`
  is absent or unauthenticated, the skill still does the file-based scan and
  the in-repo workflow/CODEOWNERS checks, and notes that remote policy checks
  were skipped.

---

## Workflow

### Step 1 — Orient

1. Resolve `<repo-path>` to an absolute path. Confirm it's a directory.
2. Note whether it's a git repo (`git -C <path> rev-parse`).
3. Check `gh` availability: `gh auth status` (suppress errors). Record whether
   remote policy reads are possible.

### Step 2 — Secret scan (always)

Run the bundled deterministic scanner. It walks the tree, skips `node_modules`
/ `.git` / build dirs / binaries, and flags provider-pattern credentials plus
keyword+entropy candidate secrets:

```bash
python3 <skill>/scripts/scan_secrets.py <repo-path>
# add --json for machine-readable output
```

`<skill>` is this skill's directory. If you don't know it, locate this file and
use its parent. Treat any hit as a finding; `critical`/`high` severities are the
priority.

> Why a script instead of grep: the regexes encode provider token formats and an
> entropy heuristic that would be tedious and error-prone to reproduce by hand,
> and a script keeps the scan deterministic and reproducible across runs.

### Step 3 — In-repo GitHub policy (file-based, always)

Inspect these in the repo itself (no `gh` needed):

1. **`.github/workflows/*.yml`** and **`.github/actions/**`** — look for:
   - missing top-level `permissions:` block
   - `permissions: write-all` or `contents: write`
   - `pull_request_target` that checks out or runs PR-supplied code
   - `secrets: inherit` on reusable workflows triggered by untrusted events
   - `GITHUB_TOKEN` pushing/deploying without a stated need
2. **`CODEOWNERS`** (`.github/CODEOWNERS`, root, or `docs/`) — does it exist?
   Is it enforced by branch protection?

Detailed patterns and remediation for each are in
`<skill>/references/github-policy.md` — read it before grading workflow files.

### Step 4 — Remote GitHub policy (only if `gh` authenticated)

If `gh auth status` succeeded, read live policy via the commands in
`references/github-policy.md` §B–§E:
- branch protection on `main`/`master`/`release/*`
- repo visibility + outside collaborators with `admin`/`write`
- org-level Actions permissions (optional)

If `gh` is unavailable, emit a `low`-severity informational note that remote
policy checks were skipped, and rely on the file-based checks.

### Step 5 — Synthesize

1. Rank all findings by severity (critical → low).
2. Cross-reference: a **public repo** (from Step 4) that also has a **live
   secret** (from Step 2) is the worst-case combination — promote it to
   `critical` and call it out first.
3. Write the report (template below) to
   `agent-output/repo-vuln-audit-report.md` (create `agent-output/` if absent).
   Also print a compact summary to the user.

---

## Report template

```markdown
# Repo Vulnerability Audit

**Repository:** <absolute path>
**Date:** <ISO-8601>
**Scope:** secrets + GitHub policy (read-only)
**Overall risk:** Critical / High / Medium / Low / Clean

## Summary
| Surface | Risk | Findings |
|---|---|---|
| Exposed secrets | … | N |
| Workflow permissions | … | N |
| Branch protection | … | N |
| Repo visibility / collaborators | … | N |
| CODEOWNERS enforcement | … | N |

## Critical first
<the one or two things that, if ignored, blow up the container>

## Detailed findings
### Exposed secrets
<file:line — match — why it matters — fix>

### GitHub policy
[SEVERITY] <surface>: <what's wrong>
  where: <file | gh resource>
  why it matters: <one line>
  fix: <one-line remediation>

## Recommendations (prioritized)
1. [P0] …
2. [P1] …
```

## Severity guidance

- **critical** — public repo + live secret; `write-all` on a deploy workflow;
  `pull_request_target` executing PR code.
- **high** — any leaked key/token in a private repo; no branch protection on
  `main`; `permissions: write-all` generally.
- **medium** — missing `permissions:` block; stale-review dismissal off;
  `allow_force_pushes` enabled; missing CODEOWNERS enforcement.
- **low** — informational (e.g., remote policy read skipped); low-entropy
  keyword match worth a glance.

## Hard rules

- **Never write, edit, or delete** any repo file or GitHub setting. Report only.
- **Never print a full secret value** in the user-facing summary beyond the
  first ~8 chars + last 2; the scanner already truncates matches.
- If the scan is clean, say so plainly — don't invent findings to look thorough.
