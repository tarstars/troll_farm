# Historical validation of the pre_review gate — 2026-08-05

Acceptance criterion: the mechanized pre-review tool must retroactively **BLOCK** the state
the integrator rejected and **CLEAR** the state that fixed it. Ground truth: the three
IMPLEMENTATION_INVALID reviews on `origin/agent/local_codex_1`
(`coordination/messages/local_codex_1/20260804T213001Z-…`, `20260805T083001Z-…`,
`20260805T143001Z-20260802-banana-restoration-r2-ack.md`), encoded as
`claude_1/pipeline/failure-ledger.json`.

Environment: rustc 1.97.1 (`~/.cargo/bin`), Python 3.12 stdlib, no network, deterministic.
All three runs are reproducible with one command from `claude_1/pipeline/`:

```
python3 run_historical_validation.py        # exit 0 iff a=BLOCK, b=BLOCK, c=CLEAR
```

which reconstructs the round-3 state from git, generates the two historical configs, and
invokes `pre_review.py` three times. Verbatim per-run reports are committed under
`claude_1/pipeline/validation/` (`a-report.md/.json`, `b-report.md/.json`,
`c-report.md/.json`). Summary output of the run recorded here:

```
pre_review: BLOCK (1 finding(s); report: …/validation/a-report.md)
pre_review: BLOCK (11 finding(s); report: …/validation/b-report.md)
pre_review: CLEAR (0 finding(s); report: …/validation/c-report.md)
historical validation (a): PASS (BLOCK as required)
historical validation (b): PASS (BLOCK as required)
historical validation (c): PASS (CLEAR as expected)
```

## (a) Round-3 rejected state, t5 declared candidate-driven — **BLOCK** (required)

Reconstruction (performed by the script; equivalent manual commands):

```
git show 8b000bad:claude_1/banana-restoration-r2/candidate-banana-r2.min.rs   # 2f58edef… bytes (sha256 verified)
git show 8b000bad:claude_1/banana-restoration-r2/traces/t5_flip_convert-transcript.txt
git show 8b000bad:claude_1/banana-restoration-r2/traces/t5_flip_convert-commands.txt
python3 pre_review.py --config <config-a.json> --report a-report.md --only trace-provenance
```

`config-a.json` declares the then-committed t5 trace exactly as the round-3 handoff treated
it: candidate-driven, critical, source = the 2f58edef bytes. Result: **exit 1, BLOCK**,
one SCRIPTED_TRACE finding — the committed commands do not survive regeneration:
**17 of 20 command lines diverge**. Mismatch evidence (regenerated = what the real
2f58edef binary emits on the committed transcript; committed = the scripted stream):

| turn | committed (scripted) | regenerated (real candidate) |
|---|---|---|
| 4 | `MOVE 0 2 1;WAIT` | `WAIT;WAIT` |
| 11 | `MOVE 0 2 2;WAIT` (return to mother) | `WAIT;WAIT` |
| 12–16 | `CHOP 0;WAIT` ×5 (the "conversion") | `WAIT;WAIT` ×5 |

This is byte-level confirmation of r3 finding 1: "Running the real candidate on the same
scenario gives PICK, MOVE, PLANT, then resident WAIT through turn 20: no flip response or
conversion." A scripted trace structurally cannot pass this check.

## (b) Round-3-era instruments vs the single-model check — **BLOCK** (required)

Reconstruction: `git show 8b000bad:…/trace_detectors.py`, `…/regression_tests.py`,
`…/banana_blocks/block-i1.rs` into a temp dir; oracle config = CONVERSION_RACE_ORACLE
(module `conversion_race_oracle.py`, quantity patterns for the conversion-deadline
arithmetic: `max\(\s*(?:t\s*\+\s*)?eta_opp`, `eta_opp\w*\s*\.\s*max\s*\(`,
`exact_chops\w*\s*<\s*eta_opp`, `ceil\w*\(\s*(?:current_)?health\b[^)]*chop`);
`python3 pre_review.py --config <config-b.json> … --only single-model`.

Result: **exit 1, BLOCK**, 11 MODEL_DIVERGENCE findings. The decisive hits — divergent
deadline arithmetic present at 8b000bad and **absent from the current files**:

| round-3 file:line | divergent code | current state |
|---|---|---|
| `trace_detectors.py:1119` | `race_won = exact_chops < eta_opp_now` (D-8-old arrival-only deadline) | D-8 now calls `cro.conversion_race_oracle(…)["feasible"]` (current `trace_detectors.py:1121-1132`) |
| `block-i1.rs:550` | `Some(resident_eta + chop_turns < eta_opp.max(ripen))` with `ripen = predicted.cooldown` proxy | current `block-i1.rs:599` uses the oracle semantics (`ticks_until_fruit`, `-1` completion) and cites CONVERSION_RACE_ORACLE at the mirror site |
| `regression_tests.py:394` | `static_deadline = max(eta_opp_t0, ripen_proxy)` | current `regression_tests.py` imports `conversion_race_oracle` (line 60) and only reports voided deadlines diagnostically |

Plus the structural findings: neither old `trace_detectors.py` nor old
`regression_tests.py` imports the oracle (it did not exist at 8b000bad), and the old
`block-i1.rs` mirror carries no CONVERSION_RACE_ORACLE marker. This mechanizes r3 finding
2 ("three divergent deadline definitions … One named oracle must drive spec, code, R-3,
and D-8") and r2 finding 1 (`ceil(health/chop_power)` hand-rolled arithmetic, also hit).

## (c) Full pre_review on the current branch state — **CLEAR** (expected)

```
python3 pre_review.py --config banana-r2-task-config.json \
        --report validation/c-report.md --json validation/c-report.json
# -> pre_review: CLEAR (0 finding(s)), exit 0, ~30 s
```

All four checks CLEAR (full detail in `validation/c-report.md`):

- **trace-provenance**: t1 (300 lines), t2 (60), t3 (20), t4 (20) regenerate
  byte-identically from the current `candidate-banana-r2.min.rs` (9f5ef833…); t5/t6 are
  declared scripted controls, non-critical, listed.
- **single-model**: importers `trace_detectors.py` / `regression_tests.py` verified;
  mirrors `block-i1.rs` (marker required and present) / `research-banana-r2.rs`
  (declared) accepted; every pattern hit explained; no divergent computation.
- **red-reason**: all four pairs RED for the documented reason on the exact rejected
  bytes rebuilt from git — R-1 on `a787d478` (f29efd0e…, I-9 surplus-plant at turn 58),
  R-3b on `0ece10ec` (280ed777…) and `8b000bad` (2f58edef…, refuses the oracle-feasible
  edge, `completion 6 < opponent harvest 7`), R-4 on `8b000bad` (no convert response in
  the I-10a window, `completion 18 < opponent harvest 27`). Exit nonzero AND all
  signature regexes matched in every case.
- **claims-coverage**: every evidence path exists; critical invariants I-9 (2 entries),
  I-10a (3), I-7 (2), D-8 (1) each carry non-scripted evidence; scripted controls are
  attached only to the non-critical `*-negative-control` claims; all 10 required
  deliverables present; all 6 mechanized ledger classes fed by the config, no waivers;
  INSTRUMENT_GAP checklist answer on file.

### Honest findings from (c) — non-blocking, reported, not tuned away

1. **`research-banana-r2.rs` mirrors the oracle arithmetic without citing it.** Line 2574
   (`resident_eta + chop_turns - 1 < eta_opp.max(ripe)`) is the oracle deadline, but the
   file never contains the string CONVERSION_RACE_ORACLE. It is accepted only because the
   config *declares* it as a mirror (rationale: arithmetic identity with the compact
   candidate is established by the research-vs-compact replay-equality gate and the seam
   asserts of `build_banana_candidate.py`); the tool prints an explicit NOTE in the
   report. Recommendation for the next handoff: add the oracle-name comment at the mirror
   site in `research-banana-r2.rs`, as `block-i1.rs` already does, and tighten the config
   to `marker_regex` for both mirrors.
2. **The scripted round-3 t5/t6 traces remain committed** under `traces/`. They are
   correctly declared `{scripted: true, critical: false}` and no claims entry for a
   critical invariant cites them, so they are allowed-but-listed per the policy; the
   candidate-driven flip evidence is R-4. They are retained for provenance of the D-8
   amendment; a future cleanup could rename them `control-*` to make the provenance
   obvious in the filename.

## Unit tests

```
python3 -m unittest test_pre_review -v   # 24 tests, OK (~0.6 s + rustc for the toy bot)
```

Synthetic coverage: fabricated scripted trace caught by regeneration; scripted-critical
blocked; planted `max(eta_opp, …)` divergence caught; importer-that-does-not-import
caught; unmarked mirror caught; comment-only mention non-blocking; red pair passing on
old bytes caught; wrong failure signature caught; scripted-control on a critical
invariant caught; missing evidence path caught; unguarded critical invariant caught;
missing deliverable caught; unfed mechanized ledger class caught and waivable; CLI exit
codes 0/1/2.
