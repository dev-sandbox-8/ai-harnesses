# Specification Template

Every spec file MUST contain these sections in order:

1. `# <Requirement heading>` + `> Source: plan/ROADMAP.md — Prepared requirements`
2. **Summary** — one paragraph, user-facing impact
3. **Current behaviour** — one subsection per sub-requirement; file + line ref + ≤5-line evidence
4. **Requirements** — numbered, testable, precise (include calculated values)
5. **Design-token changes** — table of token / old value / new value / rationale; or "None"
6. **Affected files** — table of file / change type / one-liner description
7. **Acceptance criteria** — Given/When/Then statements, one per observable outcome
8. **Testing instructions** — two subsections:
   - *Existing tests impacted*: table of test file / test name / pass·fail·update impact
   - *New tests to add*: for each test: layer, file path, plain-English description, regression guarded
9. **Implementation notes** — relevant `copilot-instructions.md` constraints, ordering deps, edge cases
10. **Out of scope** — explicit exclusions