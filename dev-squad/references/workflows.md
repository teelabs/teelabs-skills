# Workflows

Choose the smallest workflow that can establish confidence. Upgrade when
discovery reveals hidden complexity.

## Feature

Use when adding user-visible behavior or a new capability.

Discovery: product/spec, architecture, contracts, data/security impact, tests,
and UX/accessibility. Plan: acceptance criteria first, then implementation,
contract, migration, docs, and verification tasks. Review: happy path,
failure paths, backwards compatibility, authorization, observability, and
documentation.

## Bug fix

Use when existing behavior is incorrect, failing, unsafe, or regressed.

Use `superpowers:systematic-debugging` before proposing a fix. Establish a
reproducer, expected behavior, root cause, regression test, minimal fix, and
proof that adjacent behavior remains intact. Do not accept a test change that
merely hides the failure.

## Refactor

Use when behavior should remain stable while structure improves.

Define invariants before editing. Require characterization/regression coverage,
small mechanical steps, unchanged public behavior, and a diff review focused
on accidental semantic changes.

## Investigation

Use when the user wants an answer, diagnosis, feasibility result, or risk
assessment rather than an immediate code change. Keep agents read-only unless
the user separately approves a prototype. Report evidence, confidence,
unknowns, options, and a recommendation.

## Cross-cutting or high-risk work

Add explicit security/privacy, contract, migration, rollback, and operational
reviewers. Use isolated worktrees and a written plan. Require a user decision
before changing a public boundary or persistent data model.

## Reusable profile pattern

Projects may add a local profile containing only their conventions:

```text
profile:
  source_of_truth: [paths]
  acceptance_sources: [paths]
  required_checks: [commands]
  risk_reviewers: [roles]
  delivery_gates: [human approvals]
```

The profile narrows the squad's investigation; it does not weaken the core
evidence, review, safety, or approval rules.
