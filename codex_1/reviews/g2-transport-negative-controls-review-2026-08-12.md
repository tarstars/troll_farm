# G2 transport negative-controls review — 2026-08-12

- Reviewer: `codex_1` (independent of the integrator/tool author)
- Pinned artifact: `d5b63685868424b4e41913ac0d0cbb7681025bf7`
- Subject base: `origin/main` at `d468db37`
- Verdict: **SUBSTANCE ACCEPTED — EVIDENCE METADATA REVISION REQUIRED**

## Independent reproduction

I reconstructed an actual detached Git worktree at `d468db37` (necessary because one test audits
the repository's authoritative remote messages), installed the handed-off driver and runner, and
executed the full control plus both drives:

- control: 96 passed;
- inbox sweep: 7 defined, 7 applied, 7 caught, zero survivors, exit 0;
- lint outbox: 6 defined, 6 applied, 6 caught, zero survivors, exit 0;
- after the drive, both subject SHA-256 values exactly matched their `d468db37` blobs and `git
  diff` was empty for both subjects.

The reported first-failing tests match the independently generated result tails. Each is topically
connected to the deliberate break. The targeted sampling rule is honest and appropriately bounded:
it covers the named high-value functional areas but does not claim exhaustiveness, and it explicitly
lists seen-state, detailed legacy parsing, most field validators, and `--mark` as unprobed.

The runner extension is mechanically sound for this use: it accepts multiple test paths and an
explicit repo working directory, retains caught-mutant failure tails, rejects non-unique anchors,
restores in `finally`, and verifies restoration before reporting.

## Required correction

Both committed G2 JSON result files falsely declare:

```json
"task_id": "20260811-s3-collector-v2"
```

The cause is `mutation_runner.py`, where `run_drive` hard-codes its original collector task id.
These are G2 artifacts for `20260810-guards-that-cannot-fail`; a machine-readable provenance field
must not identify a different task. Parameterize `task_id` (with a compatibility default if needed),
pass the G2 id explicitly, regenerate both JSON files, and republish. No mutation or test expansion
is requested. The technical G2 conclusion is accepted; only evidence provenance blocks final
acceptance.
