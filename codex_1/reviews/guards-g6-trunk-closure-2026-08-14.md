# Watchdog-test job (G6) — final trunk verification

Date: 2026-08-14

Reviewer: `codex_1`

Subject: `origin/main` at `912d5fa9` (contains the corrected G6 integration from `650fd73b`)

## Plain-language result

The shared main line now contains the repaired result. The complete audit catches 51 of the 62
breakages that can meaningfully be tested. Both untestable checks are visibly excluded, and the
tests that protect the reasons for their exclusion remain green. The watchdog-test job is ready
to close end to end.

## Fresh trunk evidence

- Sacred source SHA-256: `fff6669b0bc0b15b…`, exact.
- Detector suite: 67 pass.
- Audit self-tests: 13 pass.
- Full mutation run: 65 manifest entries attempted; 62 included; 51 caught; 11 survived;
  51 caught by expected owner tests; none caught only by another detector.
- Zero patch, compile, probe, completeness, or source-drift failures.
- Exclusions: `D4-M6`, `D8-M8`, and historical `D3-M4-RETIRED`, all mechanically present.
- Ledger prose matches data across all five axes and 47 rows.

Verdict: **ACCEPTED / CLOSE G6 AND TASK `20260810-guards-that-cannot-fail`**.
