# Coordination transport hardening — integrator review

Date: 2026-08-05

Task: `20260805-coordination-transport-hardening`

Artifact commit: `4ccf1f76cc948bb14de53691f1e20782a77e19d6`, reachable from canonical
`origin/agent/claude_1`.

## Verdict

**REVISION_REQUIRED before Phase 2 integration.** The implementation is directionally correct
and independently reproduces 37/37 tests, checked compilation, zero live delivery errors for both
motivating tasks, canonical artifact reachability, and the sacred-source hash. Three bounded gaps
remain in the acceptance contract.

## Independently reproduced

- `python3 -m py_compile scripts/inbox_sweep.py`: pass.
- `python3 -m pytest -q tests/test_inbox_sweep.py`: 37 passed.
- New live sweep on the transport task: 0 collisions, 0 delivery errors, two correctly outstanding
  messages.
- New live sweep on banana R2: 0 collisions, 0 delivery errors, only the round-3 handoff outstanding.
- Only fetched `refs/remotes/origin/**` affect authoritative counts.
- Sacred source remains exact SHA `fff6669b...`.

## Required revision 1 — empty handoffs still validate

`validate_v2_handoff` parses `artifact_paths` and checks every listed path, but never requires the
array to be non-empty. Therefore `artifact_paths: []` passes all artifact-path checks and can
represent a supposedly complete handoff containing nothing. This defeats the primary incident
invariant: every v2 handoff must identify at least one concrete deliverable or manifest.

Require a non-empty array and add an integration test asserting an otherwise valid canonical
handoff with `artifact_paths: []` exits 2 with a clear delivery error.

## Required revision 2 — seen-state schema is not validated

`load_seen_state` reads `seen_message_paths` but ignores `schema_version`; values other than the
declared version 1 are silently accepted. It also accepts a non-string `migrated_watermark`. The
task defines this as a versioned state file and requires malformed state to fail loudly.

Require exactly `schema_version == 1`, require `migrated_watermark` to be a string or null, and add
tests for missing, unsupported, and wrong-typed values. These must exit 2 without marking.

## Required revision 3 — report and duplicate-code cleanup

The live report says Claude's proto-v2 `ack_for` was paired by exact path. That ACK has no
`schema_version: 2`, so the implementation correctly treats it as legacy and actually pairs it by
task/timestamp. Correct the report wording; the 37-test suite, not that live legacy message, is the
evidence for exact-path ACK behavior.

Remove the duplicate `self.path = path` and duplicate repository-root lookup in
`scripts/inbox_sweep.py`, then rerun the full suite and live filtered sweeps.

## Disposition

Do not integrate or announce Phase 3 yet. No historical message, watermark, seen state, bot,
experiment, or Arena state was changed by this review. A successor can retain the current design
and tests; it needs only the bounded validation/report cleanup above and a new v2 handoff.
