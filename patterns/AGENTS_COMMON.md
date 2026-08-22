# Shared Agent Principles and Patterns

## Core Principles (All Agents)

1. **Standards first** — Every decision must reference specific project rules (`copilot-instructions.md`, framework conventions, or documented standards)
2. **Evidence-based** — Cite exact file and line range for every finding; never assume
3. **Discover the stack** — Read `copilot-instructions.md` and project config files before taking action
4. **Minimal change** — Change only what's needed; avoid scope creep
5. **Verify incrementally** — Run tests after each meaningful change

---

## Common Discovery Workflow

Before any agent work:

1. Read `.github/copilot-instructions.md` for project constraints
2. Read project configuration (`package.json`, `Cargo.toml`, `pyproject.toml`, etc.)
3. Identify: test command, lint command, build command, deploy command

---

## Standard Reporting Template

```markdown
## [Report Name]

**Date:** <ISO-8601>
**Agent:** <Agent Name>
**Scope:** <what was analyzed>

---

## Summary

| Severity | Count |
|---|--:|
| 🔴 Critical | N |
| 🟡 Warning | N |
| 🔵 Suggestion | N |

<Brief assessment>

---

## Findings

<!-- One entry per finding -->

#### [SEVERITY] [Short Title]
- **File:** `path/to/file` (lines X–Y)
- **Issue:** <what is wrong>
- **Suggested fix:** <concrete action>
```

---

## Common Tool Baseline

```yaml
tools: ['Read', 'Edit', 'Bash', 'Glob', 'Grep', 'Agent', 'SendMessage']
```

Add `Write` if the agent creates files. Remove `Search`/`Glob`/`Grep` for simple agents.

---

## Common Validation Pattern

```
Validate output has required sections. If incomplete, re-invoke with specific feedback on what's missing.
```

---

## Workflow Delegation Pattern

When delegating to specialists:
1. Invoke specialist with explicit, self-contained instruction
2. Include: task description, context files, expected output format
3. Validate output on completion
4. If blocked, diagnose or re-invoke with additional guidance

---

## Retry Limits

- Fix attempts: 3 per issue
- Review cycles: 2 per review
- Deploy retries: 2 per failure

After max retries, escalate to user with full diagnostic output.