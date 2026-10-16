# Squad protocol

## Operating contract

The lead agent owns context, delegation, synthesis, gates, and communication.
Worker agents own bounded investigations or changes. The user owns product
intent, material tradeoffs, approval to proceed after planning, and approval
to integrate or publish.

The squad may inspect, edit, test, and document within the requested scope. It
must preserve unrelated user work, use isolated worktrees for independent
implementation, and avoid push, merge, deployment, publication, destructive
cleanup, production data changes, or external messages unless the user
explicitly authorizes that exact action.

## Run lifecycle

### 1. Frame

Translate the request into a short problem brief:

- desired outcome and non-goals;
- affected repository, worktree, product surface, and constraints;
- acceptance signals and likely risks;
- whether this is a feature, bug, refactor, investigation, or release task.

Inspect repository instructions, relevant specifications, current changes, and
recent history. Do not start implementation while the problem boundary is
ambiguous. Ask one focused question only when an assumption could materially
change the work.

### 2. Discover in parallel

Dispatch independent read-only agents where useful:

- explorer: architecture, data flow, and affected paths;
- requirements analyst: product/specification and acceptance criteria;
- test analyst: existing coverage, missing cases, and verification commands;
- risk reviewer: security, privacy, reliability, compatibility, and rollback.

Each report must distinguish observed facts, inferences, and unknowns. Every
important claim cites a file/line, test, command, or reproducible observation.

### 3. Plan and gate

The lead reconciles discovery into a plan with disjoint tasks. Every task has
an owner, write scope, dependencies, acceptance checks, and verification
commands. Use `superpowers:writing-plans` for multi-step work.

Pause for user approval when the plan changes product behavior, public
contracts, data shape, security boundaries, or meaningful scope. “Proceed” at
this gate authorizes implementation only; it does not authorize merge,
publication, deployment, or destructive operations.

### 4. Implement test-first

Dispatch implementers in isolated worktrees. Use
`superpowers:using-git-worktrees`, `superpowers:subagent-driven-development`,
and `superpowers:test-driven-development` when applicable. Each implementer:

1. writes or updates a failing test or executable acceptance check;
2. makes the smallest coherent change;
3. runs focused verification;
4. updates required contracts, specs, docs, and changelog decisions;
5. reports changed paths, evidence, limitations, and remaining risks.

The lead does not accept “tests pass” without knowing which tests ran and
whether they exercise the requested behavior.

### 5. Review every task

Before integration, send each task to an independent reviewer who did not write
it. Ask for both specification compliance and code-quality/maintenance review.
For bugs, use `superpowers:systematic-debugging` before accepting a fix. For
design or interface changes, use `codebase-design` and `domain-modeling` when
their concepts apply.

Classify findings as critical, important, minor, or observation. Critical and
important findings block acceptance until fixed or disproven with evidence.
The implementer must respond to findings; the lead must not silently waive
them. Re-review changed areas after fixes.

### 6. Run the final squad critique

Dispatch independent final reviewers as the risk warrants:

- red-team/security and privacy;
- contract/API/consumer compatibility;
- specification and acceptance criteria;
- test validity and regression coverage;
- QA/user-visible behavior;
- documentation and operations/release readiness.

Use [adversarial-review.md](adversarial-review.md) for the criticism loop.
Reviewers must challenge false confidence, stale evidence, hidden scope,
test-only fixes, contradictory docs, and untested failure paths.

### 7. Verify and report

Run the repository's relevant full checks against the final integrated state.
Capture exact commands, target revision, exit status, and meaningful output.
Separate `PASS`, `FAIL`, `BLOCKED`, and `NOT_APPLICABLE`; a blocked check is
not a pass.

Before presenting the result for integration, invoke `version-changelog`.
Record its change classification, changelog decision, version-file scan, and
any version transition in the final report. Repeat it before commit, push,
release, deployment, or publication if the change set has evolved.

The final report contains:

- delivered change and changed paths;
- acceptance criteria and evidence;
- review findings and dispositions;
- checks run and their results;
- known limitations and deferred work;
- recommendation: `READY_FOR_USER_APPROVAL`, `CHANGES_REQUESTED`, or
  `BLOCKED`.

The lead pauses at `READY_FOR_USER_APPROVAL`. The user's approval is required
before integration into a shared branch, release, deployment, publication, or
other external mutation.

## User interaction model

Keep routine coordination internal. Interrupt the user only for:

- a product or security tradeoff with no safe default;
- a plan that materially changes the requested scope;
- an environment/credential/permission blocker;
- a required approval gate;
- a final decision between ready, changes requested, or blocked.

When the user requests changes, convert the request into new acceptance checks,
dispatch the smallest affected review loop, and return with updated evidence.
