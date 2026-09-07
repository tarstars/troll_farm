# NOT CERTIFIED — packaging equality holds on all 160 streams; STOPPED on a preserved startup discrepancy

**Verdict.** Exact readable vs exact **shipped pruned** compact is command-identical on
all 160 archived streams, within timing and error limits. The protocol/startup leg
failed: `check_lookahead_startup.py` aborted on its own baseline assertion, so the
320-start check and the compile-timing leg were **not run**. Reproducer preserved, no
repair attempted under the frozen hash. Not a strength result; no platform action.

**Files.** No repository file changed (`git status` unchanged; `bot.rs` 44e3daca…,
`submission.rs` 7f61a6cd… untouched). Frozen inputs verified before use: readable
`claude_candidate_chopup_a.rs` **7a5722e4…** (281,543 UTF-16); compact
`claude_candidate_chopup_a.min.rs` **d40ed644…**, **91,043 UTF-16 ≤ 100,000**; parent
`claude_candidate_policy_flat.rs` 95ee691e…. New evidence scripts (working storage only):
`exact_stream_cert.py` e489f0cc…, `reproducer.py` bbfdb247….

**Tests.** Absolute rustc **1.90.0 (1159e78c4)**, `--edition=2021 -O`, no `-Awarnings`:
readable rc=0 **0 diagnostic bytes** (90650544…); shipped pruned compact rc=0 **0
diagnostic bytes** (96c191df…) — the pruned artifact itself, not a regenerated minify.
Full-stream interactive run (turn-by-turn stdin/stdout, host otherwise idle):
**160/160 streams, 160 unique game ids, both seats, 43,263 turns per arm, 0 differing
turns**; every process rc=0, empty stderr, exact turn count, no early exit. Timing:
readable mean 1.979 ms / p95 11.55 / max **33.94 ms**; compact 1.975 / 11.55 / **33.73 ms**;
**0 turns >50 ms**. Startup: aborted at case 1 —
`first command mismatch readable game=901547751 seat=0`. Characterisation only: in 16
first-turn cases readable==compact 16/16, but chopup differs from the V439 baseline in
2/16 (901547751 seat 0 `MOVE 0 6 2` vs `MOVE 0 5 3`; seat 1 `MOVE 1 11 6` vs `MOVE 1 12 5`),
deterministic over 3 repeats. The frozen **parent** binaries emit the baseline command on
that input, so the chopup rule **activates** on this official map — the "zero activation"
reading was panel-specific.

**Evidence.** `claude-runs/20260907T021124Z-4097278-1/`: `exact-stream-160.json` (+ log),
`startup-discrepancy.json`, `reproducer-901547751-seat{0,1}.txt`, `hashes.txt`,
`binaries.sha256`, `PROGRESS.md`; binaries in `chopup-cert-2026-09-07/bin/`.

**Limitations.** Equality is replayed observed state, not adaptive play; no strength or
publication claim, no local gate passed. Startup latency and the ≤1.10x V439 compile
ratio remain unmeasured for this candidate. Divergence scope beyond turn 1 unquantified.

**Next action.** Primary decides whether the turn-1 activation on 901547751 is intended;
if yes, re-ticket certification against the **parent** rather than the V439 baseline.
