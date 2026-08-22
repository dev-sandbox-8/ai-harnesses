---
name: security-check
description: >
  Analyzes untrusted repositories for security risks before installation. Checks for
  OWASP Top 10 vulnerabilities, malware patterns, keylogging, excessive privileges,
  obfuscated code, unexpected network activity, dependency risks, and malicious
  installation scripts.
invocation: manual
---

# Security Check Skill

Analyze a repository for security risks before installing or using it in your projects.

## Usage

```
/security-check <repository-path>
```

- `repository-path` — path to the local repository directory to analyze

## Pre-flight Checks

1. Identify the project type: Node.js, Python, Go, Rust, Ruby, Docker, or other
2. Locate manifest files (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Gemfile`, `Dockerfile`)
3. Check if it's a git repository and review commit history for suspicious patterns
4. Create `agent-output/security-check-report.md` if it doesn't exist

## Security Audit Workflow

### Phase 1 — Repository Metadata Analysis

1. Read `package.json` (or `pyproject.toml`, `Cargo.toml`, `go.mod` based on language)
2. Check for:
   - Suspicious package name patterns (typosquatting: `lodasch`, `npma`, etc.)
   - Unusually high version numbers or rapid version churn
   - Missing or incomplete metadata (author, license, repository fields)
   - Deprecated or archived status warnings

### Phase 2 — Installation Script Audit

Check for dangerous installation hooks:
- `package.json` `preinstall`, `install`, `postinstall` scripts
- `package.json` `prepare`, `prepublish`, `prepack` scripts
- Shell scripts (`.sh`) in root or scripts directory
- Docker entrypoints and initialization commands
- Makefile suspicious targets

Red flags:
- Network downloads in install scripts
- `curl http` or `wget` to non-package-host URLs
- `eval` or `exec` with remote content
- Base64-encoded payloads
- File system writes outside `node_modules`

### Phase 3 — OWASP Top 10 Code Analysis

#### Injection Vulnerabilities
- SQL injection patterns: string concatenation in queries, missing parameterized queries
- Command injection: unsanitized input to `exec`, `spawn`, `child_process`, `system()`
- Code injection: `eval`, `Function` constructor, dynamic imports with user input

#### Broken Authentication & Session Management
- Hard-coded credentials, API keys, secrets
- Weak password requirements
- Session tokens in URLs or logs
- Missing authentication on sensitive endpoints

#### Sensitive Data Exposure
- Logging of sensitive data (passwords, tokens, PII)
- Unencrypted data storage or transmission
- Secrets in code or config files

#### XML External Entities (XXE)
- XML parsing without entity restrictions
- External entity declarations in parsers

#### Broken Access Control
- Authorization checks bypassed or missing
- Path traversal vulnerabilities (`../`, `path.resolve` without sanitization)

#### Security Misconfiguration
- Default credentials, demo configs in production
- Overly permissive CORS, CSP, or security headers
- Debug mode enabled in production

#### Cross-Site Scripting (XSS)
- Unescaped HTML output, `innerHTML` assignments
- Missing output encoding
- Dangerous template patterns

#### Insecure Deserialization
- Deserialization of untrusted data without validation
- Pickle, YAML load, or similar unsafe deserialization

#### Using Components with Known Vulnerabilities
- Outdated dependencies (check against known CVE databases)
- Dependencies with no recent updates
- Dependencies from untrusted sources

#### Insufficient Logging & Monitoring
- Missing security event logging
- Log injection vulnerabilities

### Phase 4 — Malware Pattern Detection

Search for:
- Keylogging: `keypress`, `keydown`, `record`, `capture`, keyboard event handlers
- Clipboard access: `clipboard`, `copy`, `paste` APIs in non-UI contexts
- Process monitoring: `ps`, `process`, `kill`, `tasklist` for monitoring
- Network exfiltration: `fetch`, `XMLHttpRequest`, `axios` to suspicious domains
- File system reconnaissance: enumerating sensitive paths (`/etc/`, `~/.ssh/`, `id_rsa`)
- Anti-analysis: debugger detection, VM detection, sandbox evasion
- Obfuscation: heavy string encoding, meaningless variable names, excessive minification

### Phase 5 — Excessive Permissions & Privileges

For npm packages:
- Check `package.json` `dependencies` that seem excessive for the package's purpose
- Native module compilation requiring system privileges
- Post-install scripts with system-level operations

For Docker/Other:
- Root user in containers
- Unnecessary capabilities (`CAP_SYS_ADMIN`, `CAP_NET_RAW`)
- Host volume mounts beyond what's needed

### Phase 6 — Dependency Risk Assessment

1. Extract all dependencies from manifest files
2. Check for:
   - Abandoned packages (no updates in > 1 year, unmaintained repo)
   - Packages with high severity CVEs
   - Deep or complex dependency trees with security history
   - Dependencies from authors with suspicious patterns
   - Binary/native dependencies requiring compilation

### Phase 7 — Network Activity Analysis

Search for:
- Hard-coded IP addresses or domains
- DNS lookup APIs
- Unexpected external service integrations
- Telemetry or analytics in utility libraries
- WebSocket connections to external servers

### Phase 8 — Obfuscation Detection

Check for:
- Excessive use of `eval`, `new Function`
- Base64-encoded strings or payloads
- Hex/octal encoding of strings
- Minified code in non-distributable files
- Meaningless variable names (`a`, `b`, `c`, `_0x1234`)

### Phase 9 — Git History Analysis

Check for:
- Suspicious commits (e.g., "fix typo" with massive changes)
- History rewrites or force pushes
- Author name/email changes
- Commits from unknown authors shortly before release
- Removal of security-related comments

### Phase 10 — Supply Chain Verification

1. Verify package integrity:
   - Compare checksums against published values
   - Check for signed commits/releases
   - Verify repository URL matches package registry
2. Check for typosquatting attempts:
   - Similar names to popular packages
   - Recently created accounts
   - Unusual download patterns

## Search Patterns Reference

### Dangerous Functions to Flag
```
eval\(|new Function\(|child_process\.|exec\(|spawn\(|system\(|passthru\(|shell_exec\(|
curl\s+http|wget\s+http|fetch\(|XMLHttpRequest\(|axios\.|\.ajax\(|
localStorage\.setItem\(|sessionStorage\.setItem\(|
document\.write\(|innerHTML\s*=|outerHTML\s*=
```

### Suspicious Variable/Function Names
```
_[a-z0-9]{4,}
[a-z]{1,3}\.[a-z]{1,3}\.[a-z]{1,3}
base64_decode|atob\(|btoa\(
```

### Sensitive Paths to Check
```
/etc/passwd|/etc/shadow|\.ssh/id_rsa|\.pgp/|~/\\.bash|\.env|credentials|secrets?\.
```

## Output

Create `agent-output/security-check-report.md` with:

```markdown
# Security Check Report

**Repository:** <path>
**Date:** <ISO-8601 date>
**Overall Risk:** Low/Medium/High/Critical

---

## Summary

| Category | Risk Level | Issues Found |
|---|---|---|
| Installation Scripts | Low/Medium/High/Critical | N |
| OWASP Top 10 | Low/Medium/High/Critical | N |
| Malware Patterns | Low/Medium/High/Critical | N |
| Permissions | Low/Medium/High/Critical | N |
| Dependencies | Low/Medium/High/Critical | N |
| Network Activity | Low/Medium/High/Critical | N |

---

## Recommendations

1. [Priority 1] <Specific action to mitigate highest risk>
2. [Priority 2] <Action for next highest risk>
...

---

## Detailed Findings

### Installation Scripts
<Details of any install script risks>

### OWASP Top 10 Issues
<Details of any OWASP violations>

### Malware Patterns
<Details of any malware indicators>

### Permissions & Privileges
<Details of any privilege escalation risks>

### Dependency Risks
<Details of any risky dependencies>

### Network Indicators
<Details of any suspicious network activity>

### Obfuscation
<Details of any obfuscation patterns>
```

## Exit Codes

- 0 — No critical risks found, safe to install
- 1 — Warnings found, review recommended
- 2 — Critical risks found, do not install