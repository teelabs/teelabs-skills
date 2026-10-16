# Skills Collection Implementation Plan

Spec: `docs/superpowers/specs/2026-10-16-skills-collection-design.md`

## Global constraints

- Preserve the existing `dev-squad` and `version-changelog` skill content unless validation identifies a concrete defect.
- Keep the repository dependency-free for validation; use Node 24 already selected in the environment.
- Skills remain independently installable and updateable by slug.
- Do not claim GitHub/install readiness until fresh commands verify it.

## Task 1: Collection governance and metadata

Owner: documentation/configuration agent. Write only: `README.md`, `AGENTS.md`, `CONTRIBUTING.md`, `SECURITY.md`, `LICENSE`, `CHANGELOG.md`, `.editorconfig`, `.gitignore`, `skills.json`, `.github/workflows/validate.yml`, `.github/ISSUE_TEMPLATE/*`, and `.github/pull_request_template.md`.

Document exact `npx skills` and `sm` commands, trust/security review, independent updates, contribution rules, and the current two skills. Ensure `skills.json` uses schema version 1 and sorted entries.

Expected verification: Markdown/config files exist, JSON parses, workflow invokes `node scripts/validate-skills.mjs`.

## Task 2: Dependency-free validator

Owner: validation agent. Write only `scripts/validate-skills.mjs` and any validator-specific fixture or test file under `scripts/fixtures/` if useful.

Discover immediate child directories containing `SKILL.md`; reject root-level and nested skill files. Parse frontmatter including scalar, folded/literal block, and simple array forms. Validate required fields, slug alignment, unique names, relative local Markdown links, and exact `skills.json` membership. Produce useful errors and exit nonzero on failure.

Expected verification: run the validator against the current tree and exercise at least one intentional failure fixture without changing the committed tree.

## Task 3: Compatibility audit

Owner: review agent. Read-only audit of both existing skills and the new governance/validator contract. Report broken links, invalid frontmatter, portability issues, or mismatches with `npx skills`/`sm`. Do not edit files.

Expected verification: report includes all discovered skill paths and installer-specific risks.

## Task 4: Integration and local verification

Main agent integrates delegated outputs, resolves findings, runs the validator, parses all JSON/YAML-like configuration, and tests discovery with `npx skills add . --list` plus selective local installation in a temporary directory. Verify `sm` source scanning and selected install without mutating the user’s global skill store.

## Task 5: GitHub publication

Main agent initializes git if needed, commits the complete initial tree, creates `teelabs/skills` with `gh repo create`, pushes `main`, and verifies repository metadata and remote content. Use `gh` for GitHub mutations. Then test public `npx skills add teelabs/skills --list`, one selected install, and one selected update; test `sm source add`/`sm install` using isolated temporary state where supported.

## Completion contract

- All task outputs reviewed; no unresolved critical or important findings.
- Validator exits 0 on the committed tree.
- GitHub Actions workflow is present and syntactically valid.
- GitHub repository and `main` branch are verified through `gh`.
- Public discovery and selective installation are verified with fresh output.
- Final report includes exact URLs, commands, and any limitation (especially if an installer’s update behavior cannot be safely exercised without global state).
