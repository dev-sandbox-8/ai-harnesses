#!/usr/bin/env python3
"""
scan_secrets.py — lightweight secret/exposed-credential scanner.

Walks a repository, skips noise directories and binary blobs, and flags
candidate exposed secrets using a curated set of provider regexes plus a
keyword + Shannon-entropy heuristic.

This is a *precision-first* scanner: it favors surfacing likely-real secrets
over maximizing recall. It is meant to run read-only inside an unattended
container where Claude runs in auto mode, so it never writes or mutates
anything — it only reports.

Usage:
    python3 scan_secrets.py <repo-path> [--json]
"""
import os
import re
import sys
import json
import math

# Directories we never descend into.
SKIP_DIRS = {
    ".git", "node_modules", "dist", "build", ".next", ".nuxt",
    "venv", ".venv", "env", "__pycache__", ".tox", ".cache",
    "vendor", "target", ".terraform", "coverage", ".idea", ".vscode",
    "bower_components", "Pods", ".gradle",
}

# File suffixes we treat as binary / non-scannable.
SKIP_EXT = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp", ".svg",
    ".mp4", ".mov", ".avi", ".mkv", ".mp3", ".wav", ".flac",
    ".pdf", ".zip", ".tar", ".gz", ".tgz", ".rar", ".7z", ".xz",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".exe", ".dll", ".so", ".dylib", ".bin", ".dat", ".class",
    ".pyc", ".o", ".a", ".jar", ".wasm", ".lockb",
}

MAX_FILE_BYTES = 1_000_000  # skip files larger than 1 MB

# Curated provider regexes. Each maps to a human label.
PROVIDER_PATTERNS = [
    (r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----", "Private key block"),
    (r"\b(AKIA|ASIA)[0-9A-Z]{16}\b", "AWS access key ID"),
    (r"\bgh[pousr]_[A-Za-z0-9]{36,}\b", "GitHub personal access / OAuth token"),
    (r"\bgithub_pat_[A-Za-z0-9_]{50,}\b", "GitHub fine-grained PAT"),
    (r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b", "Slack token"),
    (r"\bAIza[0-9A-Za-z\-_]{35}\b", "Google API key"),
    (r"\bsk_live_[0-9a-zA-Z]{24,}\b", "Stripe live secret key"),
    (r"\bsk_test_[0-9a-zA-Z]{24,}\b", "Stripe test secret key"),
    (r"\brk_live_[0-9a-zA-Z]{24,}\b", "Stripe restricted key"),
    (r"\bsk-[A-Za-z0-9]{20,}\b", "OpenAI API key"),
    (r"\bSG\.[A-Za-z0-9_\-]{22}\.[A-Za-z0-9_\-]{43}\b", "SendGrid API key"),
    (r"\bSK[0-9a-fA-F]{32}\b", "Twilio API key"),
    (r"\beyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b", "JSON Web Token (JWT)"),
    (r"//registry\.npmjs\.org/:_authToken=\S+", "npm registry auth token"),
    (r"\bglpat-[0-9A-Za-z_\-]{20,}\b", "GitLab personal access token"),
    (r"\bhook=https://hooks\.slack\.com/services/T[A-Za-z0-9/]+\b", "Slack incoming webhook URL"),
]

# Keyword assignments that, when given a high-entropy or long value, are
# almost always a leaked secret.
SECRET_KEYWORDS = [
    "api_key", "apikey", "api-key", "secret", "secret_key", "secretkey",
    "access_token", "accesstoken", "access-token", "auth_token", "authtoken",
    "client_secret", "client-secret", "private_key", "password", "passwd",
    "pwd", "token", "bearer", "credentials", "credential", "passphrase",
]
KW_RE = re.compile(
    r"""(?im)^\s*["']?([A-Za-z0-9_\-\.]*?(?:%s)[A-Za-z0-9_\-\.]*?)["']?\s*[:=]\s*["']?([^\s"']{8,})"""
    % "|".join(re.escape(k) for k in SECRET_KEYWORDS)
)

ENTROPY_THRESHOLD = 3.5  # bits per character; printable ASCII max is ~4.7

# Values that look like secrets by keyword but are actually placeholders, code
# identifiers, file handles, or library-internal variables. Keeping this list
# out of the per-line hot loop makes the intent obvious and easy to extend.
FALSE_POSITIVE_VALUES = {
    # literal placeholders
    "null", "none", "true", "false", "undefined", "example", "changeme",
    "your_api_key_here", "your_api_key", "paste_tunnel_token_here",
    "random-secret", "personal-access-token", "<random-secret>",
    "<personal-access-token>", "<your-token>", "sk-your-key-here",
    # code identifiers / variables (not assigned literals)
    "calculate_stats(tokens)", "a_summary.get(", "b_summary.get(",
    "connectslackcredentials(", "connectgithubcredentials(",
    "connectlinearcredentials(", "connect_response.json()[",
    "process.env.vercel_token", "process.env.turso_auth_token!",
    "thinking_budget", "s.subagenttokens", "sessionstats?.tokens",
    "scorecards.reduce((sum,", "_auth_prefertoken", "survivors.filter(f",
    "generatetoken", "explicittoken", "generated-fallback",
}

# Prefixes that indicate a value is a code reference, not a literal secret.
CODE_PREFIXES = ("$", "${", "process.env", "env.", "chat-", "scorecards", "sessionstats")


def is_false_positive_value(value: str) -> bool:
    # Strip surrounding quotes and common trailing punctuation (commas,
    # semicolons, parens) so "thinking_budget," matches "thinking_budget".
    v = value.strip("\"'").rstrip(",;)")
    low = v.lower()
    if low in FALSE_POSITIVE_VALUES:
        return True
    # unquoted env-var / template references
    if v.startswith(CODE_PREFIXES):
        return True
    # method-call / property-access patterns: "x = foo.bar(" or "foo.bar["
    if "(" in v or "[" in v:
        return True
    # template-literal or backtick fragments
    if v.startswith("`") or v.endswith("`"):
        return True
    # code identifier with member access, e.g. "s.subagentTokens"
    if re.search(r"^[A-Za-z_]\w*\.\w+$", v):
        return True
    return False


def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    freq = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in freq.values())


def is_text_file(path: str) -> bool:
    ext = os.path.splitext(path)[1].lower()
    if ext in SKIP_EXT:
        return False
    try:
        with open(path, "rb") as f:
            chunk = f.read(4096)
        chunk.decode("utf-8")
        return True
    except (UnicodeDecodeError, OSError):
        return False


def scan_file(path: str, rel: str, findings: list):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError:
        return

    for lineno, line in enumerate(lines, start=1):
        line_stripped = line.rstrip("\n")

        # 1) Provider-specific patterns.
        provider_hit = False
        for pattern, label in PROVIDER_PATTERNS:
            for m in re.finditer(pattern, line_stripped):
                provider_hit = True
                findings.append({
                    "type": "provider-credential",
                    "label": label,
                    "file": rel,
                    "line": lineno,
                    "match": m.group(0)[:80],
                    "severity": "critical",
                })

        # 2) Keyword assignment + entropy heuristic. Skip on lines already
        #    covered by a provider pattern to avoid double-reporting the same
        #    secret (e.g. "API_KEY = ghp_..." already flagged by the GitHub
        #    token regex).
        if provider_hit:
            continue
        for m in KW_RE.finditer(line_stripped):
            key, value = m.group(1), m.group(2)
            # Ignore obvious non-secrets / placeholders / code, not literals.
            if is_false_positive_value(value):
                continue
            entropy = shannon_entropy(value)
            long_enough = len(value) >= 16
            if entropy >= ENTROPY_THRESHOLD or long_enough:
                findings.append({
                    "type": "keyword-secret",
                    "label": f"Possible secret in '{key}'",
                    "file": rel,
                    "line": lineno,
                    "match": f"{key} = {value[:80]}",
                    "severity": "high" if entropy >= ENTROPY_THRESHOLD else "medium",
                    "entropy": round(entropy, 2),
                })


def scan_repo(root: str):
    findings = []
    root = os.path.abspath(root)
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune skipped directories in place.
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root)
            try:
                if os.path.getsize(full) > MAX_FILE_BYTES:
                    continue
            except OSError:
                continue
            if not is_text_file(full):
                continue
            scan_file(full, rel, findings)
    # De-duplicate identical hits.
    seen = set()
    deduped = []
    for f in findings:
        key = (f["file"], f["line"], f["match"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(f)
    return deduped


def main():
    if len(sys.argv) < 2:
        print("usage: scan_secrets.py <repo-path> [--json]", file=sys.stderr)
        sys.exit(2)
    repo = sys.argv[1]
    as_json = "--json" in sys.argv
    if not os.path.isdir(repo):
        print(f"error: not a directory: {repo}", file=sys.stderr)
        sys.exit(2)

    findings = scan_repo(repo)
    # Sort: critical first, then by file/line.
    order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings.sort(key=lambda f: (order.get(f["severity"], 9), f["file"], f["line"]))

    if as_json:
        print(json.dumps({"count": len(findings), "findings": findings}, indent=2))
    else:
        if not findings:
            print("No exposed secrets detected.")
        else:
            print(f"Found {len(findings)} candidate secret(s):\n")
            for f in findings:
                print(f"[{f['severity'].upper()}] {f['label']}")
                print(f"  file: {f['file']}:{f['line']}")
                print(f"  match: {f['match']}")
                if "entropy" in f:
                    print(f"  entropy: {f['entropy']} bits/char")
                print()
    # Exit 0 = clean, 1 = findings present (lets callers gate on it).
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
