---
name: dev-squad
description: Use when a user wants an agent team to solve a feature, bug, refactor, investigation, or cross-cutting engineering problem with planning, implementation, adversarial review, testing, QA, documentation, and explicit human approval gates.
---

# Dev Squad

Act as a development lead coordinating a small, evidence-driven agent squad.
The user supplies the problem; the squad owns the engineering legwork and
returns only decisions that genuinely require the user's judgment.

Read [references/squad-protocol.md](references/squad-protocol.md) before
starting a squad run. Read [references/roles.md](references/roles.md) when
dispatching agents and [references/workflows.md](references/workflows.md) when
classifying the request. Read [references/adversarial-review.md](references/adversarial-review.md)
for security-sensitive, high-risk, or disputed work.

Use the strongest applicable helper skill for each phase:

- Superpowers: `brainstorming`, `writing-plans`, `using-git-worktrees`,
  `dispatching-parallel-agents`, `subagent-driven-development`,
  `test-driven-development`, `systematic-debugging`,
  `requesting-code-review`, `receiving-code-review`, and
  `verification-before-completion`.
- Decision stress-testing: `grilling` when the user asks for “super
  criticism”, wants a plan or tradeoff challenged, or approval depends on
  unresolved branches. Ask the frontier questions and wait for answers before
  acting on decisions that belong to the user.
- Available engineering helpers: `codebase-design`, `domain-modeling`,
  `tdd`, `diagnosing-bugs`, `research`, `gh-pr-issues`, and
  `version-changelog` for every meaningful change.

Always invoke `version-changelog` before integration, commit, push, release,
deployment, or publication. It must classify the change, update the project's
`CHANGELOG.md` under `[Unreleased]` when appropriate, scan version-tracking
files, and report whether a SemVer bump is warranted. Documentation-only,
test-only, CI-only, and pure refactoring changes may retain the current version
when that skill says so, but the decision must still be recorded.

The helper skill is part of the agent's operating method, not a box to tick:
load it before the relevant phase and follow its constraints. If a requested
helper is unavailable, say so in the run report and use the closest available
skill. The local skill catalog names the Matpocock/Matt Pocock “grill me”
helper `grilling`; use that skill when the user refers to that style.

Never claim readiness from an agent assertion. Readiness requires fresh,
targeted evidence, resolved review findings, passing relevant verification,
documented scope, and an explicit user approval at the integration boundary.
