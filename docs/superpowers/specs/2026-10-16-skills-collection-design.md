# Skills Collection Monorepo Design

## Goal

Turn this repository into a public, vendor-neutral collection of independently installable and independently updateable AI-agent skills. The canonical repository is `teelabs/teelabs-skills`.

## Users and supported workflows

The collection serves people who want to discover or install one or more skills for Codex, Claude Code, Cursor, OpenCode, and other Agent Skills-compatible tools. The canonical repository is `teelabs/teelabs-skills`.

Supported workflows are:

```sh
npx skills add teelabs/teelabs-skills --list
npx skills add teelabs/teelabs-skills --skill dev-squad
npx skills update dev-squad
```

```sh
sm source add https://github.com/teelabs/teelabs-skills.git --install
sm install teelabs/teelabs-skills version-changelog --force
```

Each skill directory is a source unit. A consumer can update `dev-squad` without updating `version-changelog`, subject to the installer’s source and lockfile behavior.

## Repository layout

```text
<skill-name>/
  SKILL.md
  references/       # optional, only when progressive disclosure is useful
  examples/         # optional, only when examples materially clarify use
docs/
  superpowers/specs/
scripts/
  validate-skills.mjs
skills.json
AGENTS.md
CHANGELOG.md
CONTRIBUTING.md
LICENSE
README.md
SECURITY.md
```

Existing skills remain at their current paths. A skill’s name in frontmatter must match its directory slug, and all references inside a skill must resolve to existing paths relative to the Markdown file containing the link.

## Skill contract

Every public skill must have a `SKILL.md` with YAML frontmatter containing:

- `name`: a unique lowercase hyphenated slug matching the directory name;
- `description`: a concise model-facing trigger description that says when the skill applies.

The body should make the agent’s process explicit, use progressive disclosure for optional material, and define observable completion criteria. Agent-specific files may be included when needed, but the core `SKILL.md` must remain portable.

## Collection metadata

`skills.json` is a small, human-readable index of public skills with this schema:

```json
{
  "schemaVersion": 1,
  "repository": "https://github.com/teelabs/teelabs-skills",
  "skills": [
    { "name": "dev-squad", "path": "dev-squad", "summary": "..." }
  ]
}
```

`schemaVersion` is the integer `1`; `repository` is the canonical HTTPS repository URL; `skills` is a sorted array of objects with non-empty string `name`, `path`, and `summary` fields. `path` is a top-level directory name. It is supplementary metadata: installers discover skills from `SKILL.md`, so the index must not become a second source of truth for frontmatter.

## Validation

`node scripts/validate-skills.mjs` must validate:

1. every immediate child directory containing a `SKILL.md` is discovered; root-level and nested `SKILL.md` files are rejected unless the discovery rules are explicitly expanded later;
2. frontmatter is present and parseable;
3. `name` and `description` are present and non-empty;
4. frontmatter `name` matches the containing directory;
5. skill names are unique;
6. local Markdown links in each skill resolve relative to the Markdown file containing the link;
7. `skills.json` contains exactly the discovered public skills.

The validator may use a small dependency-free YAML frontmatter parser, but it must support the existing collection syntax: scalar values, folded (`>-`) and literal (`|`) block scalars, and simple arrays. It must reject missing delimiters and malformed required fields rather than silently accepting them.

The same command runs in GitHub Actions on pushes and pull requests. CI should use a current supported Node LTS without requiring a package install for the validator.

## Governance and security

`AGENTS.md` is the authoritative contributor/agent operating contract. It must state that skills are executable instruction supplied to AI systems, so changes require focused review, tests where applicable, no secrets or destructive defaults, and explicit handling of external side effects.

`SECURITY.md` must explain how to report prompt-injection, unsafe-command, credential, or supply-chain issues. GitHub issue templates should not encourage users to paste secrets.

## Release and updates

The collection itself is distributed from Git. There is no root npm package and no root version that couples all skills. `CHANGELOG.md` tracks collection-level changes under `[Unreleased]` and identifies affected skill slugs. Skill authors should keep changes scoped to the affected skill whenever possible.

The README must show both the plural `npx skills` CLI and `sm` commands, including selective install and update examples. `sm source add ... --install` is documented as source registration plus all-skill import; selective installation uses `sm install teelabs/teelabs-skills <skill> --force`. It must state that users should review skill instructions before enabling them because a skill is trusted agent input.

## Acceptance criteria

- `teelabs/teelabs-skills` exists on GitHub and its default branch is `main`.
- A fresh clone contains the two existing skills plus the collection governance and validation files.
- The validator exits zero on the committed tree.
- GitHub Actions runs the validator.
- `npx skills add teelabs/teelabs-skills --list` discovers both existing skills.
- Selective install examples name one skill at a time, and update examples demonstrate independent updates.
- `sm source add` can recognize the repository as a source, and `sm install teelabs/teelabs-skills version-changelog --force` can install a selected skill.
- An isolated verification proves that updating one skill leaves the other skill and its companion files unchanged for both supported CLIs.
