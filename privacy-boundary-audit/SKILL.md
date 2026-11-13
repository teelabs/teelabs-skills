---
name: privacy-boundary-audit
description: Use when preparing any commit, issue or pull request text, review, or project document that could expose local-environment details or private-project information in a public artifact.
---

# Privacy boundary audit

Run this audit before every commit in every repository, and before sending or publishing project text. A local path that helps one person navigate is still a disclosure when placed in a shared artifact. A private project's details stay out of public project artifacts.

## Workflow

1. **Set the boundary.** Identify the target repository or publication and determine its visibility. When visibility cannot be confirmed, treat the target as public. Check that each project-specific fact comes from the target project's own approved sources.
2. **Scan local changes.** From the skill directory, run `python3 scripts/audit_local_disclosures.py --staged` before committing. To scan documents, pass them with `--files`; to scan a prepared issue, PR, review, or comment body, pass it through `--stdin`. The scanner reports line numbers, opaque source ordinals, and candidate categories; it withholds matched text and filenames. For a single document, scan it alone to correlate the source ordinal safely.
3. **Review candidates privately.** Open the referenced source locally. Replace account names, machine names, user home paths, workstation-only roots, local file URLs, and private service endpoints with repository-relative paths, stable shared links, or synthetic placeholders. Keep a generic example only when it is clearly synthetic and contains no real account, host, path, or project identifier. Never copy a matched value into an issue, comment, commit message, report, or response.
4. **Check project provenance.** For every public artifact, verify that project names, status, owners, architecture, data, metrics, and decisions describe only that public project. Never copy details from a private project into a public project, including when asked for a cross-project summary. Rewrite only as a genuinely general lesson that contains no identifying or project-specific detail; if that cannot be done safely, omit it.
5. **Validate GitHub text.** Run the `audit-text` skill's `--stdin` check on the exact text before each GitHub mutation. After each mutation, run its `--remote OWNER/REPO` audit. The local-disclosure scan and `audit-text` check catch different problems; use both.
6. **Close the audit.** Re-scan the final staged changes and relevant documents. A candidate is resolved only when the real source has been reviewed and the final text contains no local-environment disclosure or private-to-public project leakage. If an existing remote artifact cannot be edited, remove or replace it using the repository's supported redaction path and verify the original is no longer visible.

## Candidate classes

The bundled scanner recognizes common POSIX and Windows home directories, home-directory file URLs, home shortcuts, WSL user profiles, expansions of home/current-directory/account/host/temp/config variables, and local-only endpoints. It scans complete staged file contents, supplied files, or standard input. It is a candidate detector: review generic examples and non-sensitive loopback references before deciding whether they need redaction.

The scanner cannot determine repository visibility, whether a project is private, or whether a fact belongs to another project. The provenance check is mandatory even when the scanner reports no candidates.

## Rationalizations to reject

| Temptation | Required action |
| --- | --- |
| “The full local path makes this easier to click.” | Use a repository-relative path or a shared URL available to intended readers. |
| “This target is private today.” | Keep private-project facts out of public-target content; verify the target's visibility each time. |
| “The scan is clean, so the content is safe.” | Complete the project-provenance review; the scanner cannot classify project ownership. |
| “I can post now and redact it later.” | Redact before posting. For an existing disclosure, update or remove it, then verify the remote artifact. |
| “The match is only in a generated or historical artifact.” | Check whether it is visible or publishable; redact exposed content and prevent it from being republished. |

## Completion criteria

- Every staged addition, prepared GitHub text, and requested project document was scanned.
- Every candidate was reviewed without copying its value into the audit output.
- Public artifacts contain no private-project-specific detail.
- The exact GitHub text and the post-mutation remote repository passed their respective audits.
- The final staged diff has no unresolved candidate.
