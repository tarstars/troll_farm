# 20260804-r36-simplified-arena: qualify and publish round 36

- Status: in progress — 516-task exact-equality gate starting
- Priority: direct owner instruction
- Record owner / integrator / Arena controller: `local_codex_1`
- Candidate preparer: `claude_1`
- Branch: `agent/local_codex_1`
- Created UTC: 2026-08-04T14:41:57Z
- Last updated UTC: 2026-08-04T14:41:57Z

## Objective

Run the round-36 simplified E7a source against exact E7a on the frozen consumed 516-task
development panel. Submit exactly once only if every terminal task and every frozen gate is
equal/green. Recover the platform source, verify its hash, record submission identity and initial
runtime health, and then leave the Arena unchanged while the result settles.

If any task differs, perform no platform mutation and diagnose the first differing task.

## Frozen identities

- Exact E7a baseline:
  `cgauto/submissions/candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs`, 62,820 bytes,
  SHA-256 `97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595`.
- Round-36 candidate:
  `claude_1/r36-submission/candidate-agent6553250-e7a-r36-simplified.min.rs`, 55,799 bytes,
  SHA-256 `2caac7c6e71e8dcc613a2275fe8129cdf9aec2c1230e50f7dfdec79908528381`.
- Sacred source SHA-256:
  `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.
- Development design: consumed official-generator seeds 9,854,000--9,854,042, both seats,
  six frozen opponent families, 516 tasks, eight threads, 50,000 bootstrap samples.

## Qualification command

```bash
python3 local_codex_1/r36-simplified-arena/evaluate_development_equality.py \
  --panel local_codex_1/r36-simplified-arena/development-panel.tsv \
  --output local_codex_1/r36-simplified-arena/development-result.json
```

Required verdict: `DEVELOPMENT_EXACT_EQUALITY_PASS`, 0/516 differing tasks, all frozen gates
green. The evaluator records the first difference and exits 2 on failure.

## Conditional Arena execution

After and only after qualification:

1. Copy the exact candidate to a new immutable path under `cgauto/submissions/` and verify SHA.
2. Run `cgauto/submission_history.py preflight` and the read-only live-source/baseline checks.
3. Publish with one canonical `cgauto/api_submit.py` call. Never retry an ambiguous response.
4. Discover the new agent/submission identity, recover the platform source against the frozen
   SHA, and run the submission-scoped health checkpoint.
5. Commit/push the terminal response, identity, source verification, and health record. Do not
   mutate the Arena again while the source settles.

## Authorization and interpretation

The owner directly instructed this sequence on 2026-08-04. The live source at task start is the
owner-directed readable no-orchard ablation `6593838`/`41089629`; round 36 restores exact-E7a
behaviour while measuring the standing of a 6,479-byte-smaller equivalent. Same-source historical
spread is 25.30/rank 12 versus 23.56/rank 32, so the new standing is one noisy draw, not a fixed
complexity value.

No sealed range is opened. No formatter touches `rust/src/bin/` or `cgauto/`. The 05:17 collector
and `data/raw/games/` remain untouched.
