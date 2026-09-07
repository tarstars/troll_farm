# Startup/compile legs PASS against the explicit exact-readable reference

**Verdict.** With the intended oracle, the frozen chopup candidate passes the startup
and compile legs: 320/320 starts equal the reference, 0 over 50 ms, 0 errors; candidate
compile median 1.0515x V439 with 0 diagnostic bytes. Fixture oracle corrected only;
bot behaviour and frozen sources unchanged. Not a strength or publication claim.
`commands_equal_reference` is true; `commands_equal_old_baseline` is **false** and not
claimed (chopup intentionally differs from V439 on 2/16 first turns).

**Changed files.** `check_lookahead_startup.py` 45dd4426… — adds `--expected-binary`
(default `benchmark_lookahead.BASELINE`, legacy V439), expected line from a batch run of
that reference, report schema v2 with `commands_equal_reference` and
`reference{path,sha256,is_v439_baseline}`, richer mismatch message, `main(argv)` returns
the report. Open-stdin/liveness, full-line, 500 ms timeout, latency logic unchanged; no
weakening to "any output". Only repo change (`git status`). Frozen inputs re-verified
unmodified: readable 7a5722e4…, compact d40ed644… (91,043 UTF-16), submission.rs
7f61a6cd…, bot.rs 44e3daca….

**Tests.** Focused test (run dir, `test_expected_binary_option.py`, real replay + fake
bots, 40 starts): reference intentionally different from V439 PASSES; a different
compact/short output still RAISES and writes no report; with the flag omitted the same
arms FAIL against V439 (legacy default preserved). Exit 0.
Serial 320-start check, host idle, reference = exact READABLE chopup binary
`/data/separate_troll_farm-working/chopup-cert-2026-09-07/bin/readable` 90650544…:
starts=320, commands_equal_reference=true, mean 1.105 ms, max 1.570 ms, over_50ms=0,
exit 0; short arm = shipped compact 96c191df….
Three matched alternating compile pairs, nothing else running: ctrl 6.412/6.314/6.277 s
(diag 27,869 B), cand 6.581/6.640/6.995 s (diag **0 B**), rc=0; median ratio **1.0515**.
160-stream equality report reused from run 20260907T021124Z-4097278-1, not rerun.

**Evidence.** `claude-runs/20260907T022118Z-4130195-1/`: `startup-320.json`,
`startup-320.log`, `test_expected_binary_option.py`, `focused-pass.json`, `timings.txt`,
`rustc-version.txt`, `sources.sha256`, `PROGRESS.md`; compile dir
`chopup-cert-compile-022118/`.

**Limitations.** DEVIATION: no rustc 1.90 exists on this host any more; pairs used the
only installed absolute rustc **1.97.1 (8bab26f4f)** d3a664c9…, matched within the run.
Startup equality covers turn 1 of 16 game-seat cases; the reference is the candidate's
own readable build, so it proves readable==compact packaging, not correctness of the new
policy. No field/strength evidence; local gates unchanged.

**Next action.** Primary reviews the reference choice, then runs the two unranked
known-map diagnostic games already prepared.
