# Teelabs Skills

An open, vendor-neutral collection of independently installable skills for
Codex, Claude Code, Cursor, OpenCode, and other Agent Skills-compatible tools.

## Included skills

| Skill | Use it when |
| --- | --- |
| [`dev-squad`](dev-squad/SKILL.md) | You want an evidence-driven agent team for a feature, bug, refactor, investigation, or cross-cutting engineering task. |
| [`version-changelog`](version-changelog/SKILL.md) | You need consistent SemVer and Keep a Changelog updates across a project. |

Each top-level skill directory is an independent source unit. Companion files
under that directory are installed and updated with the skill.

## Install and update with `npx skills`

List the skills available from this collection:

```sh
npx skills add teelabs/skills --list
```

Install one skill at a time:

```sh
npx skills add teelabs/skills --skill dev-squad
npx skills add teelabs/skills --skill version-changelog
```

Update a single installed skill without selecting the others:

```sh
npx skills update dev-squad
```

Review the proposed instructions and the target paths before enabling a skill.
Skills are executable instruction supplied to an AI system and should be
treated as untrusted input until reviewed.

## Install and update with `sm`

Register this repository as a source and import all discovered skills:

```sh
sm source add https://github.com/teelabs/skills.git --install
```

Install or update one selected skill independently:

```sh
sm install teelabs/skills version-changelog --force
sm install teelabs/skills dev-squad --force
```

`sm source add ... --install` performs source registration plus all-skill
import. Use `sm install <source> <skill> --force` when selecting one skill.
Check the manager’s current help and review the source before changing a
global skill installation.

## Trust and security

Read a skill’s `SKILL.md` and companion files before installation. Do not run
commands, grant credentials, or approve external side effects solely because a
skill requests them. Report prompt injection, unsafe commands, credential
exposure, or supply-chain concerns through the process in [`SECURITY.md`](SECURITY.md).

## Contributing

See [`AGENTS.md`](AGENTS.md) for the operating contract and
[`CONTRIBUTING.md`](CONTRIBUTING.md) for contribution and review rules.

## License

This collection is released under the [MIT License](LICENSE).
