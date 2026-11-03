---
name: audit-text
description: Use when validating GitHub issue, pull request, comment, or review text before sending it, or when a repository needs a language-independent check for literal escaped line breaks.
---

# Audit Text

Use this skill to catch GitHub text that contains literal `\\n`, `\\r`, or
`\\r\\n` sequences where actual line breaks are required. The skill is
repository-agnostic: it does not depend on the target project's language,
package manager, build system, or root manifest.

## Use it in these scenarios

- Before creating or updating an issue, pull request, review, or comment.
- In CI or a local hook that validates generated GitHub bodies.
- When an API payload was assembled from JSON, shell, YAML, or a template and
  escaped newlines may have been serialized literally.
- When reviewing agent-generated GitHub text for formatting regressions.
- When auditing an existing repository's issues and pull requests after a
  migration or automation change.

Do not use it as a source-code linter, secret scanner, Markdown style checker,
or authorization check. It is read-only and does not create, edit, or delete
GitHub data.

## Commands

The bundled executable uses only Python 3's standard library. Remote mode also
requires an authenticated `gh` CLI.

```sh
python3 /path/to/audit-text/scripts/audit-text.py --stdin < body.txt
python3 /path/to/audit-text/scripts/audit-text.py --remote OWNER/REPO
python3 /path/to/audit-text/scripts/audit-text.py --remote
```

`--remote` accepts an explicit `OWNER/REPO`; without it, the command resolves
the repository from the current checkout through `gh repo view`. It audits up
to the first 100 issues, pull requests, comments, and reviews returned by the
GitHub GraphQL API.

Exit status is part of the contract:

- `0`: no literal escaped returns found;
- `1`: text was audited and findings were found;
- `2`: invalid arguments, missing `gh`, authentication, repository, or API
  failure.

## Handling findings

Report the exact source and line numbers. Replace serialized escape sequences
with real line breaks before the GitHub mutation. Validate the final text
again, then perform the separate authorization and mutation steps required by
the task. Never treat a passing text audit as evidence that a GitHub mutation
succeeded.

## Focused validation

Run the bundled test without relying on the host project's package manager:

```sh
bash audit-text/scripts/audit-text-test.sh
```
