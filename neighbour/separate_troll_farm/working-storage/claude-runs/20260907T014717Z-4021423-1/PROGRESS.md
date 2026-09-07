# PROGRESS — run 20260907T014717Z-4021423-1 (frozen chopup: field + broader sample)

All times UTC. Deadline 02:32:17.

- 01:47-01:50 read CLAUDE.md, AGENTS.md, WORKFLOW.md, WORKSTATE.md, EVALUATION.md,
  the ticket, and the prior chopup RESULT/PLAN. `sha256sum` confirms the three
  frozen sources unchanged (candidate readable 7a5722e4, compact d40ed644,
  parent policy-flat 95ee691e).
- 01:49 seed check: recursive grep for `426092` over the repo and over
  `/data/separate_troll_farm-working/` hits only prospective planning text
  (WORKSTATE.md, tasks/frozen-chopup-generalization.md, this run's prompt/input)
  and one incidental latency substring `20426092` in the 012354Z panel.tsv. No
  panel row, plan or manifest ever recorded a game on 426092000..023. UNSPENT.
- 01:50 PID 4032452 `cargo build --release --bin candidate_compare_panel`,
  run-local `CARGO_TARGET_DIR`, control module = parent verbatim, candidate
  module = chopup. Finished 1m12s, exit 0. Binary sha256 c30f0e25.
- 01:51 PID 4033135 built the two exact standalone field binaries with the
  absolute Rust 1.90.0 toolchain, `-O`, no warnings-as-errors: parent 5fe4cbb1,
  candidate 640e8b74. Exited.
- 01:52:06 PID 4039342 ONE panel launched in the background: 426092000..023,
  24 maps x 2 seats x 12 opponents = 576 pairs, 4 threads, `ALLOW_ANY_MAP_SEED=1`.
  PLAN.md was frozen at 01:52, before this launch and before any row existed.
- 01:52-01:53 stage 1 field replay (`field_activation.py`, run-local, uses the
  existing `audit_candidate_command_streams` decoder/renderer; no framework or
  source change). 12 archived screen games, both arms on identical recorded
  states. Parent reproduces the recorded official stream exactly on all 6
  policy-flat games (0 mismatches); the 6 v439 games mismatch 0/7/1/2 as expected
  for a different policy. Candidate diverges from parent in 2/12 games (1 of the
  6 distinct maps): tonigineer seat 1, turn 8, parent `TRAIN 2 2 0 2` + `MOVE`,
  candidate `MINE 1` — a real deferred first hire, not a no-op.
- 01:53-01:54 stage 1b rejection diagnostic. `instrument.py` copies the FROZEN
  candidate into the run directory and adds stderr-only tags at each
  `chop_upgrade` rejection; the repository candidate is untouched. Compiled to
  `candidate_instr`, replayed the same 12 games: stdout identical to the
  uninstrumented candidate in 12/12 (`COMMAND_NEUTRAL_ALL=True`).
  Rejections, per distinct map: 4/6 `cap_or_infinite_eta` (parent already at the
  chop cap 3, etas 2/4/12/12); 1/6 `eta_window` (viewlagoon seat 0, chop 1->2,
  base_eta 0, up_eta 36 > allowed 15, deadline_eta 34); 1/6 ACCEPT (tonigineer,
  chop 2->3, base_eta 6, up_eta 16, felling 90->62, extra_delay 10).
- 01:52:06-02:06:36 ONE panel, PID 4039342, exit 0, 869.527 s for 576/576 pairs.
  Stage 1/1b ran concurrently on the same 4 cores; that costs wall clock only and
  cannot change referee outcomes. No latency measurement was taken at any point.
- 02:07 summary (`summarize_panel.py`, copied verbatim from run 012354Z) and
  `activation.py` (new, run-local): baseline 519/14/43 pts 526.0, candidate
  518/15/43 pts 525.5, delta **-0.5**; issues 2 vs 2, critical 0 vs 0.
  Activation 48/576 pairs (maps 426092004 and 426092010, both seats, all 12
  opponents); every spec change is chop +1 only (movement/carry/harvest 0).
- 02:07 the 2 candidate issues are `move_blocked:1` on 426092016 seat 1 vs
  gold_adaptive and compact_gold — a map with NO command divergence, identical
  in both arms, inherited from the parent. Still counted: the frozen rule says
  zero candidate issues, so it is reported as not met, not explained away.
- 02:07 GATE FAILS on both clauses (delta not strictly positive; candidate issues
  not zero) -> PARK. No certification run, per the frozen plan.
- 02:07 process table clean: no cargo/rustc/panel/python job left, nothing
  detached, no automatic rerun. Hashes re-verified in `hashes.txt`; the three
  frozen sources, `bot.rs` and `submission.rs` are byte-identical to 01:48Z.
