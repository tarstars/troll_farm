# PROGRESS — chopup startup certification with explicit reference (actual UTC)

- 02:21:22Z start; read AGENTS/WORKFLOW/WORKSTATE, ticket, prior cert run
  20260907T021124Z-4097278-1 (its 160-stream report reused, not rerun).
- 02:23:00Z `check_lookahead_startup.py`: added `--expected-binary` (default =
  benchmark_lookahead.BASELINE, i.e. legacy V439); expected startup line now comes
  from a batch `run()` of that reference; report schema v2 gains
  `commands_equal_reference` + `reference{path,sha256,is_v439_baseline}`; mismatch
  message names the reference and both command arrays. Open-stdin/liveness, full-line,
  500 ms timeout and latency logic untouched. `main(argv=None)` returns the report.
- 02:23:33–02:25:56Z focused test (run dir, fake bots + 1 real replay, 40 starts):
  (1) reference intentionally different from V439 PASSES, starts=40,
  commands_equal_reference=true, is_v439_baseline=false;
  (2) a different short/compact output still RAISES and writes no report;
  (3) with the flag omitted the same arms fail against the V439 baseline — legacy
  default preserved. Exit 0, "ALL 3 FOCUSED CHECKS PASSED".
- 02:26:10–02:26:11Z serial 320-start check, host idle (load 0.35), reference =
  exact READABLE chopup binary 90650544…: starts=320, commands_equal_reference=true,
  mean 1.105 ms, max 1.570 ms, over_50ms=0, exit 0. Both arms (readable and shipped
  compact 96c191df…) compared against that reference.
- 02:27:13–02:27:52Z matched alternating three ctrl/cand compile pairs, nothing else
  running: ctrl = submission.rs (V439 7f61a6cd…), cand = claude_candidate_chopup_a.min.rs
  (d40ed644…), absolute rustc, `--edition=2021 -O`, no `-Awarnings`.
  ctrl 6.412/6.314/6.277 s (diag 27,869 B each), cand 6.581/6.640/6.995 s
  (diag **0 B** each). Median ratio 6.6397/6.3145 = **1.0515 ≤ 1.10**, rc=0 throughout.
- DEVIATION: the only rustc on this host is **1.97.1 (8bab26f4f 2026-07-14)**
  (`~/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustc`,
  d3a664c9…); no 1.90 toolchain exists any more, so the pairs are 1.97.1, matched
  within the run. Earlier runs recorded 1.90.0 — the toolchain moved.
- 02:28:02Z no rustc/checker/bench process left; only repo change is
  `check_lookahead_startup.py`. Frozen chopup sources unmodified (7a5722e4…/d40ed644…),
  bot.rs/submission.rs untouched. No platform call, no panel, no commit.
