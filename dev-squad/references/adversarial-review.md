# Adversarial review

Use this loop whenever the change affects security, privacy, money, tenants,
data integrity, public contracts, infrastructure, or a critical user journey.

## Review sequence

1. Restate the intended invariant in one sentence.
2. List trust boundaries, inputs, state transitions, side effects, and failure
   paths.
3. Generate attacks and misuse cases from the actual feature, not a generic
   checklist.
4. Attempt each case against code, tests, or a controlled local probe.
5. Record result as `RESISTED`, `EXPLOITABLE`, `UNPROVEN`, or `BLOCKED`.
6. Tie every result to evidence and severity.
7. Require a fix, a proved non-applicability argument, or explicit user
   approval to defer.

## Minimum questions

- Can an unauthorized actor cross an identity, tenant, role, or ownership
  boundary?
- Can stale, replayed, forged, duplicated, or reordered input succeed?
- Are errors, timing, logs, metrics, and responses leaking sensitive state?
- Are resource use, retries, concurrency, and unbounded storage controlled?
- Does restart, multiple instances, partial failure, or migration change the
  security or correctness result?
- Do contracts, generated types, consumers, docs, and tests agree?
- Does the test prove the invariant, or only exercise the implementation's
  current shape?

## Severity

- `CRITICAL`: exploitable security/privacy/data-loss issue or release-blocking
  correctness failure.
- `IMPORTANT`: meaningful security, contract, reliability, or regression risk.
- `MINOR`: localized defect with a safe workaround and no boundary impact.
- `OBSERVATION`: improvement or follow-up with no current release impact.

Never convert `EXPLOITABLE`, missing evidence, or an environment blocker into
`PASS`. A reviewer may be wrong, but the disagreement must be resolved with
new evidence or explicitly presented to the user.
