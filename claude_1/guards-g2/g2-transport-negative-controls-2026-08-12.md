# G2 — negative controls for the transport suite

- Author: `claude_1`, on the VM · Date (real UTC): 2026-08-12
- Task: `20260810-guards-that-cannot-fail`, sub-item **G2** (owner `claude_1`)
- Subject: `scripts/inbox_sweep.py` (1,309 lines) and `scripts/lint_outbox.py` (296), at
  **`origin/main` = `d468db37`**, measured in a detached worktree
- Reviewer must not be the integrator (task constraint). `local_claude_1` wrote both the tooling
  and its tests, so it cannot be the reviewer of this sub-item.

## Result

**The transport suite is load-bearing. 13 targeted mutants, 13 caught, zero survivors**, across
both subjects, and each one is caught by a test whose name matches the thing that was broken.

| Subject | Tests | Mutants | Caught | Survivors |
|---|---:|---:|---:|---:|
| `inbox_sweep.py` | 72 | 7 | **7** | 0 |
| `lint_outbox.py` | 24 | 6 | **6** | 0 |

Control: all 96 tests green before mutating. Drive exit 0 for both.

| Mutant | What it breaks | First test to fail |
|---|---|---|
| S1 | authority becomes `refs/heads/` — unpushed counts as delivered | `test_worktree_ack_does_not_acknowledge_remote_message` |
| S2 | roster read from a branch, not trunk | `test_tool_drift_warns_on_mismatch_and_is_quiet_when_in_sync` |
| S3 | v2 `requires_ack` field ignored | `test_requires_ack_boolean_legacy_and_kind_rules` |
| S4 | legacy `Requires acknowledgement: yes` ignored | `test_requires_ack_boolean_legacy_and_kind_rules` |
| S5 | exit 0 with outstanding acknowledgements | `test_worktree_ack_does_not_acknowledge_remote_message` |
| S6 | exit-2 transport-broken signal dropped | `test_immutable_path_collision_across_remote_refs_exits_2` |
| S7 | non-integer `schema_version` treated as legacy | `test_schema_version_of_legacy_and_v2` |
| L1 | lint exits 0 with errors — the publish gate | `test_unknown_kind_fails_with_suggestion` |
| L2 | non-canonical publish branch not flagged (F9b) | `test_lint_warns_when_head_is_not_my_canonical_branch` |
| L3 | immutable-path collision ignored (TQ-6) | `test_lint_reports_an_immutable_path_collision` |
| L4 | published message editable in place | `test_editing_an_already_published_message_is_flagged` |
| L5 | deletion of a published message undetected (TQ-4) | `test_staged_mode_reports_deletion_of_a_committed_message` |
| L6 | any filename accepted in the outbox namespace | `test_malformed_message_filename_fails` |

Evidence: `claude_1/guards-g2/results/g2-inbox-sweep-results.json` and
`…/g2-lint-outbox-results.json`; runner `claude_1/guards-g2/run_g2_mutations.py`.

## Sampling rule, as the sub-item requires

**Targeted, not exhaustive.** Every functional area of each subject carries at least one mutant,
and within an area the edit chosen is the one whose failure would be **silent** — a wrong count,
a skipped check, a swallowed error — over one that would crash loudly and be noticed anyway.

Areas covered: for `inbox_sweep.py`, authority selection, roster/quarantine authority, ack
discharge (both the v2 field and the legacy line, mutated separately), exit status (both the
unacknowledged signal and the transport-broken signal), and schema validation. For
`lint_outbox.py`, exit status, the publish-branch check, all three immutability guards, and
namespace validation.

Each mutant targets a defect the project has actually suffered where one exists: L2 is finding
**F9b** (three real quarantine entries came from publishing to a task branch), L3 is **TQ-6**,
L5 is **TQ-4**, S2 is the defect the comment above `ROSTER_REF` describes in trunk's own source.

## What this does and does not establish

**Does:** in every area sampled, at least one test fails when the subject is broken, and the
failing test is topically the right one. The concern that motivated G2 — tests written by the
author of the tooling might pass regardless — **is not borne out here.** That is a real negative
result and I would rather report it than manufacture a finding.

**Does not:**

- **This is 13 mutants against 96 tests.** A targeted pass cannot show the suite is sound, only
  that it is not vacuous in the places probed. Unprobed: seen-state/watermark handling, the
  dual-format legacy parser's details, per-field validators beyond `schema_version`, and the
  `--mark` path.
- **"First test to fail" is not "the only test that catches it."** The drive runs pytest with
  `-x`, so it stops at the first failure; S1 and S5 report the same test for that reason, not
  because it is the only guard. Removing `-x` would enumerate every catching test at
  proportionally more runtime.
- **A caught mutant says a test fails, not that the test asserts the right thing** for the right
  reason. I read the named tests to confirm each is topically about the mutated behaviour; that
  is a human check, not a mechanical one.

## Correction, 2026-08-12 (raised by `codex_1` in review)

Both result JSONs originally declared `task_id: 20260811-s3-collector-v2` — the shared
`mutation_runner.py` hard-coded the task it was first written for, so **G2's own evidence
claimed to belong to the collector task.** A machine-readable provenance error, and exactly the
sort a reader cannot catch by eye. The field is now a parameter, this driver passes
`20260810-guards-that-cannot-fail`, and both files are regenerated. Measurements are unchanged:
7/7 and 6/6, zero survivors.

## Method notes

Measured against **trunk, not my branch** — the tooling everyone runs is trunk's, and the
publish gate is trunk's exit status. Subjects are restored from an in-memory copy after each
mutant and the drive refuses to report a result if restoration did not happen.

One extension to `claude_1/collector-v2/mutation_runner.py` was needed and is additive: it now
accepts multiple test paths and an explicit working directory, and it **retains the pytest tail
for caught mutants as well as survivors**. That last one matters here — G2's question is *which*
tests are load-bearing, and the previous version discarded exactly that evidence, keeping the
output only when a mutant survived.

## Not done

The sub-item permits changing tests and harnesses. **I changed none** — there was nothing to
repair, since no mutant survived. If a wider pass later finds gaps, the repairs belong in a
follow-up with its own controls.
