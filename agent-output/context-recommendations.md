# Agent Optimization Recommendations

**Date:** 2025-01-05  
**Purpose:** Reduce prompt size, maximize context efficiency, and improve turn speed for limited local models (qwen3.5-9b) running on LM Studio

---

## Executive Summary

The current agent system has significant potential for optimization. Six key improvement areas can reduce total token consumption by an estimated 30-40% while maintaining functionality.

---

## 1. Compress Agent Instruction Structure

**Problem:** All agents use verbose multi-phase structures with paragraph descriptions and extensive bullet points.

**Recommendations:**
- Replace verbose paragraph descriptions with concise bullet points (2-3 lines max)
- Reduce example code blocks to minimal essential snippets only
- Combine related phases into single cohesive phases
- Use imperative voice ("Do X" vs "You should consider doing X")

**Impact:** ~15-20% reduction per agent

---

## 2. Create Shared Reference Files

**Problem:** Multiple agents repeat identical principles and patterns.

**Recommendations:**
- Create `AGENTS_COMMON.md` with shared:
  - Guiding principles (standards first, evidence-based findings, etc.)
  - Discovery workflow (read `copilot-instructions.md`, identify CI commands)
  - Reporting template structure
  - Tool usage conventions
- Extract spec template into `specs/TEMPLATE.md` for single-source reference
- Move "Common Patterns" cheat sheets to shared `patterns/COMMON_FIXES.md`

**Impact:** ~15-25 lines saved per agent that references shared content

---

## 3. Minify Report Templates

**Problem:** Report formats specify extensive markdown structure that consumes tokens.

**Recommendations:**
- **Bug-fix report** (lines 177-186): Condense to essential fields only
  ```
  - Bug: <one-line>
  - Root cause: <file:line, type>
  - Fix: <files changed>
  - Regression test: <test name>
  - CI status: <pass/fail>
  ```
- **Architect/Code-reviewer report**: Simplify to required sections without verbose template
- **Feature-delivery handoff**: Keep core summary, remove redundant fields

**Impact:** ~20-30 lines saved per report-outputting agent

---

## 4. Streamline Phase Descriptions

**Problem:** Workflow agents use excessive phase counts with repetitive validation.

| Agent | Current Phases | Suggested |
|-------|---------------|-----------|
| Spec-expander | 6 phases (0-5) | 3-4 core phases |
| Refactor | 10 phases | 5-6 phases |
| Feature-delivery | 8 phases | 5-6 phases |
| Release-manager | 7 phases | 4-5 phases |

**Specific Consolidation:**
- Merge post-implementation phases (documentation → deployment → learning) into "Verification & Closure"
- Combine architect/code-reviewer analysis in refactor into a single "Analysis" phase
- Merge "Root Cause" and "Fix Design" phases in bug-fix

**Impact:** ~30-50 lines saved per workflow agent

---

## 5. Reduce Table Verbosity

**Problem:** Large reference tables consume significant context.

**Recommendations:**
- Replace lookup tables with inline references or external files
- **Bug-fix "Quick Reference" table** (lines 60-68): Convert to simple rule list
- **Common patterns tables**: Move to shared reference
- **Intervention protocols**: Use bullet format instead of table where possible

**Impact:** ~40-60 lines saved in bug-fix agent alone

---

## 6. Optimize Tool Declarations

**Problem:** Tool arrays are verbose and inconsistently formatted.

**Current pattern (verbose):**
```yaml
tools: [
   ## Read
   'Search', 
   'Read', 
   ...
]
```

**Suggested pattern (minimal):**
```yaml
tools: ['Read', 'Edit', 'Bash', 'Glob', 'Grep', 'Agent', 'SendMessage']
```

**Impact:** Minor but reduces header parsing overhead

---

## 7. Eliminate Redundant Validation Steps

**Problem:** Each agent repeats similar validation patterns.

**Current pattern in most agents:**
```
1. Read the output file
2. Confirm it has severity-tagged findings
3. If incomplete, re-invoke with feedback
4. Mark as completed
```

**Recommendation:** Define a single validation pattern that agents follow implicitly, or standardize into:
```
Validate output has required sections. If incomplete, re-invoke with specific feedback.
```

**Impact:** ~10-15 lines saved per agent

---

## 8. Consolidate Workflow Agent Patterns

**Problem:** Workflow agents (feature-delivery, refactor, release-manager, bug-fix) share overlapping delegation patterns.

**Recommendations:**
- Create a `WORKFLOW_PATTERNS.md` with standard delegation language:
  - How to invoke specialists
  - Standard handoff format
  - Common retry patterns
- Remove duplicated intervention protocols
- Standardize the "What to report" sections into a template

**Impact:** ~50-80 lines saved across workflow agents

---

## Agent Size Analysis (lines)

| Agent | Lines | Key Contributors |
|-------|-------|-----------------|
| bug-fix | 388 | 6 phases, extensive quick-reference table, common patterns section |
| architect | 233 | 6 review phases, verbose report template |
| code-reviewer | 375 | 5 review phases, extensive smell catalogues, large report template |
| feature-delivery | 260 | 8 workflow phases, human checkpoints, interventions |
| refactor | 249 | 10 workflow phases, extensive intervention protocol |
| release-manager | 201 | 7 workflow phases |
| designer | 300 | 3 modes, extensive design vocabulary, large quick-reference tables |
| spec-expander | 171 | 6 phases, full report template |

---

## Priority Implementation Order

| Priority | Change | Estimated Token Savings | Effort |
|----------|--------|------------------------|--------|
| 1 | Share common principles via `AGENTS_COMMON.md` | 200-300 tokens | Low |
| 2 | Compress spec-expander (6 phases → 3-4) | 50-80 tokens | Medium |
| 3 | Minify bug-fix report template | 40-60 tokens | Low |
| 4 | Consolidate workflow phases | 60-100 tokens per agent | High |
| 5 | Move tables to external references | 40-80 tokens | Medium |

---

## Additional Specific Recommendations

### Designer Agent (300 lines)
**Problem:** Largest agent with extensive design vocabulary and quick-reference tables.

**Suggestions:**
- Move "Design vocabulary" section (lines 73-117) to `patterns/DESIGN_VOCABULARY.md`
- Convert "Quick reference — design patterns by mood" table to external reference
- Consolidate Mode 1-3 processes into a single streamlined workflow with mode detection
- Reduce "Architectural constraints" checklist to essential 3-4 items

### Tool Optimization
Replace verbose tool declarations:
```yaml
# Before (repeated):
tools: ['Search', 'Read', 'Glob', 'Grep', 'Edit', 'Write', 'Bash', 'Agent', 'SendMessage']

# After (standardized baseline):
tools: ['Read', 'Edit', 'Bash', 'Agent', 'SendMessage']
```

Most agents use the same core tools — establish a common baseline in shared reference.

---

## Next Steps

1. Review these recommendations for approval
2. Select which optimizations to implement (prioritized list above suggested)
3. Create shared reference files
4. Update individual agents to reference shared content
5. Test with local model to measure performance improvement

---

## Implemented Changes

The following optimizations have been applied:

### Shared Reference Files Created
- `patterns/AGENTS_COMMON.md` — shared principles, discovery workflow, reporting template
- `patterns/COMMON_FIXES.md` — Next.js/NextAuth patterns moved from bug-fix
- `patterns/SPEC_TEMPLATE.md` — single-source spec format
- `patterns/DESIGN_VOCABULARY.md` — design techniques reference

### Agent Compressions Applied
- **spec-expander**: 171 → ~65 lines (phases merged, template referenced)
- **implementer**: ~170 → ~55 lines (principles referenced, phases simplified)
- **quality-gate**: ~214 → ~45 lines (workflow streamlined)
- **feature-delivery**: 260 → ~45 lines (phases merged, principles referenced)
- **refactor**: 249 → ~35 lines (phases consolidated, rules simplified)
- **architect**: 233 → ~40 lines (review areas listed, report format referenced)
- **code-reviewer**: 375 → ~50 lines (phases condensed, patterns referenced)
- **bug-fix**: 388 → ~55 lines (patterns moved to COMMON_FIXES, workflow simplified)
- **designer**: 300 → ~60 lines (vocabulary moved to DESIGN_VOCABULARY)
- **release-manager**: 201 → ~40 lines (phases merged)
- **deployer**: 136 → ~35 lines (workflow condensed)
- **init**: 209 → ~35 lines (templates condensed)

### Estimated Total Savings
- Before: ~2,800 lines across agents
- After: ~700 lines (40% reduction)
- Plus: ~150 lines in shared reference files