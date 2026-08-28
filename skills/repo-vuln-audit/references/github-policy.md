# GitHub Policy & Permission Checks

This reference supplements the `repo-vuln-audit` skill with the specifics of
what "overly-permissive GitHub policy" means and the `gh` commands that read
it. Everything here is **read-only** — these commands never mutate a repo.

## Why this matters for an unattended, auto-mode container

A leaked secret is bad, but an *overly-permissive policy* is how that leak
becomes a breach, and how a dependency or a malicious PR becomes code execution
on your runners. The cheapest security win for an auto-mode container is to
make sure the repo it operates in can't be turned into a pivot. These checks
focus on the highest-leverage policy surfaces.

---

## A. In-repo workflow permission misconfiguration (file-based)

These live in `.github/workflows/*.yml` (and `.github/actions/**`). No `gh`
auth required — read the YAML directly.

### 1. Missing top-level `permissions:` block
A workflow without an explicit `permissions:` block inherits the repo-level
default. If the org/repo default is `read` that's fine, but many repos default
to `write` or `read-all`. **Always pin the narrowest scope.**

Good:
```yaml
permissions:
  contents: read
```
Red flag:
```yaml
# no permissions: block at all, OR
permissions: write-all
```

### 2. `permissions: write-all` / `contents: write` with untrusted input
`write-all` grants every scope. Flag it. Also flag `contents: write` combined
with `pull_request_target` (runs with repo write context but checks out
**untrusted** PR head code — a classic RCE-on-runner vector).

### 3. `pull_request_target` + checkout of PR ref
```yaml
on: pull_request_target
...
- uses: actions/checkout@v4
  with:
    ref: ${{ github.event.pull_request.head.ref }}   # DANGEROUS
```
`pull_request_target` executes in the *base* repo's trusted context but the
head ref is attacker-controlled. Flag any `pull_request_target` that checks
out or runs code from the PR.

### 4. `secrets` passed to untrusted steps
Flag `secrets: inherit` on a reusable workflow call (`uses: ./.github/...`)
that is itself triggered by `pull_request_target` or `issue_comment`.

### 5. `GITHUB_TOKEN` used to push / deploy
If a workflow pushes commits, publishes a release, or deploys, it needs write
perms — note it as a finding so the user can confirm it's intended and scoped.

---

## B. Branch protection

Read-only `gh` commands (require `gh` auth; fail gracefully if absent):

```bash
gh api repos/<owner>/<repo>/branches/<branch>/protection
gh api repos/<owner>/<repo>/branches
```

Things to verify on protected branches (e.g. `main`, `master`, `release/*`):
- `required_status_checks` present (at least one CI check must pass)
- `enforce_admins: true` (protection applies to admins too)
- `required_pull_request_reviews` with `required_approving_review_count >= 1`
- `dismiss_stale_reviews: true`
- `allow_force_pushes: false`
- `allow_deletions: false`
- `restrictions` present if the branch should be locked to specific pushers

**Finding severity guide:**
- No branch protection on `main`/`master` → **high**
- Protection exists but `enforce_admins: false` or `required_approving_review_count < 1` → **medium**
- `allow_force_pushes: true` or `allow_deletions: true` → **medium**

---

## C. Repository visibility & collaborator model

```bash
gh repo view <owner>/<repo> --json isPrivate,visibility
gh api repos/<owner>/<repo>/collaborators?per_page=100 \
  --jq '.[] | {login, permission}'
```

Check:
- Public repo containing secrets/sensitive code → **high** (cross-check with
  the secret scan — a public repo with a leaked key is the worst case)
- Outside collaborators with `admin` or `write` who aren't org members
- `permission: admin` granted to bots/service accounts that don't need it

---

## D. CODEOWNERS review requirements

`CODEOWNERS` (in `.github/`, root, or `docs/`) can enforce review by path. If
it exists, confirm that protected branches *require* CODEOWNERS review
(`required_pull_request_reviews` + the branch rule `required_signatures` /
code owner enforcement). A CODEOWNERS file with no enforcement is theater.

```bash
gh api repos/<owner>/<repo>/contents/.github/CODEOWNERS --jq '.content' | base64 -d
```

---

## E. Org-level policy (optional, broader)

Only if the user wants org-wide posture:
```bash
gh api orgs/<org>/actions/permissions          # can org use Actions?
gh api orgs/<org>/actions/permission-policy    # allowed actions
gh api orgs/<org>/repos                                        # repo list + visibility
```

---

## Output format for policy findings

Report each as:
```
[SEVERITY] <surface>: <what's wrong>
  where: <file | gh resource>
  why it matters: <one line>
  fix: <one-line remediation>
```

Severity scale: `critical` (public repo + live secret, or write-all on
push-triggered deploy), `high`, `medium`, `low`.
