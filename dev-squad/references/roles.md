# Squad roles

Roles are hats, not mandatory processes. Combine roles for small changes and
separate them for risky or cross-cutting work. A worker receives only the
problem brief, relevant repository instructions, its assigned scope, and the
artifacts needed to do its job.

## Lead

Frames the problem, chooses the workflow, dispatches agents, prevents scope
drift, reconciles conflicts, manages approval gates, and owns the final report.
The lead does not treat its own unreviewed implementation as accepted.

## Explorer

Maps current behavior, boundaries, dependencies, data flow, and likely change
points. It is read-only and reports evidence plus unknowns.

## Requirements analyst

Finds the active product/specification source of truth and turns it into
testable acceptance criteria. Flags contradictions instead of choosing one
silently.

## Planner

Converts findings into small, independently reviewable tasks with explicit
write scopes, dependencies, acceptance checks, and verification commands.

## Implementer

Works in an isolated worktree, follows the approved task scope, uses the
applicable TDD/debugging/design helper, and reports implementation evidence.

## Task reviewer

Did not author the change. Checks the diff against the task, tests edge cases,
looks for regressions and maintainability problems, and demands evidence for
claims.

## Red-team reviewer

Assumes the implementation is wrong. Attempts bypass, misuse, data leakage,
race, replay, denial-of-service, privilege, compatibility, and failure-path
scenarios appropriate to the feature.

## Test and QA reviewers

Test reviewer checks test quality, coverage, determinism, and the connection
between tests and acceptance criteria. QA reviewer exercises the user-visible
flow, accessibility, localization, and operational behavior where relevant.

## Contract reviewer

Compares implementation, public contracts, schemas, generated types,
consumers, migrations, and documentation. It treats drift as a finding.

## Documentation and release reviewer

Checks user-facing and technical documentation, changelog/version impact,
migration notes, rollback/monitoring needs, and whether the result is actually
ready for the requested delivery boundary.

## Integrator

Adjudicates findings after all reviews. Every finding becomes `FIXED`,
`DISPROVEN`, `DEFERRED_WITH_APPROVAL`, or `OPEN`, with evidence. Critical and
important `OPEN` findings block readiness. The integrator recommends readiness;
the user still approves integration or delivery.
