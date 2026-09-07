# PROGRESS — exact-source certification, frozen chopup A (actual UTC)

- 02:11:24Z start. Read AGENTS.md/WORKFLOW.md/WORKSTATE.md, prior cert run
  20260906T173455Z-2544959-1 (policy-flat) and chopup run 20260907T012354Z-3956144-1.
- 02:12:10Z frozen hashes verified in repo, unmodified:
  `claude_candidate_chopup_a.rs` 7a5722e4… (281,543 UTF-16),
  `claude_candidate_chopup_a.min.rs` d40ed644… (**91,043 UTF-16 <= 100,000**),
  parent `claude_candidate_policy_flat.rs` 95ee691e… present unchanged,
  `submission.rs` 7f61a6cd… (V439) unchanged. Host idle: load 0.16, 4 cores.
- 02:13:06Z exact deployable binaries built with absolute rustc 1.90.0
  (1159e78c4 2025-09-14), `--edition=2021 -O`, no `-Awarnings`:
  readable rc=0, **0 diagnostic bytes**, sha 90650544…;
  SHIPPED PRUNED compact `.min.rs` rc=0, **0 diagnostic bytes**, sha 96c191df….
  The compact arm is the shipped pruned artifact; no generic minified arm is used.
- 02:13:46Z smoke of new `exact_stream_cert.py` on 2 streams: 453 turns/arm,
  0 differing turns, max 20.1 ms, 0 over 50 ms.
- 02:14:0xZ launched full 160-stream interactive exact-vs-exact run
  (turn-by-turn stdin/stdout, real process I/O, both arms serial, nothing else
  running). Log `exact-stream-160.log`, report `exact-stream-160.json`.
- 02:17:02Z 160-stream exact-vs-exact run finished, PID 4106933 exit 0, stderr empty.
  160/160 archived streams, 160 unique game ids, both seats present, 43,263 turns per
  arm, **0 differing turns**, every process rc=0 with no extra stdout/stderr and exactly
  the expected turn count. Timing over real process I/O: readable mean 1.979 ms,
  p95 11.55 ms, max 33.94 ms; compact mean 1.975 ms, p95 11.55 ms, max 33.73 ms;
  **0 turns over 50 ms** in either arm.
- 02:17:14Z `check_lookahead_startup.py` (existing 320-start checker) ABORTED on its
  own baseline assertion: `first command mismatch readable game=901547751 seat=0`.
  Startup timing therefore never measured. No repair attempted, checker not modified.
- 02:17:54Z reproducer preserved (`reproducer.py`, `startup-discrepancy.json`, both
  protocol files). All 16 first-turn cases (8 games x 2 seats): readable == compact in
  16/16; chopup differs from the V439 baseline binary in 2/16 — game 901547751 seat 0
  (`MOVE 0 6 2` vs `MOVE 0 5 3`) and seat 1 (`MOVE 1 11 6` vs `MOVE 1 12 5`).
  Deterministic over 3 repeats.
- 02:18:13Z divergence attributed by direct measurement, not inference: the frozen
  PARENT policy-flat binaries (b9e9268a…/fbefd7c6…, from the 20260906T173455Z cert)
  emit the baseline `MOVE 0 5 3` on the same input. The chopup rule ACTIVATES on this
  official map, contradicting the panel-only "zero activation" reading.
- 02:18:35Z STOPPED per ticket discrepancy rule. Serial compile timing vs V439 NOT RUN.
  No repository file changed; no live jobs left; no platform call.
