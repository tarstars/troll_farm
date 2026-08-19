# Watchdog-test job (G6) — revision acceptance

Date: 2026-08-14

Reviewer: `codex_1`

Subject: `agent/claude_1` at `5b931cbb`

## Owner summary

The missing bookkeeping update is fixed. The two checks that cannot affect any result are now
visibly excluded from the score, while their reasoning remains protected by tests. The complete
audit now reproducibly catches 51 of the 62 breakages that can meaningfully be tested. G6 is
accepted for integration.

## Independent verification

- Both `D4-M6` and `D8-M8` have manifest-level `excluded_from_totals=true` entries with the
  construction proof, 0-of-416 differential, and coordinator ruling cited.
- Both ledger rows are `EQUIVALENT_GUARD_UNTESTABLE`, not `NO_FIXTURE`.
- Detector suite: 67 pass.
- Audit self-tests: 13 pass.
- Fresh whole-manifest mutation run: 65 entries attempted, 62 included, 51 caught, 11 survived,
  51 caught by expected owner tests, zero caught only by another detector.
- Zero patch, compile, probe, completeness, or pinned-source-drift failures.
- Prose/data check passes across all five axes and states both 51/64 and 51/62 with the denominator
  rulings as the sole reason for the change.
- Sacred source remains byte-exact at SHA-256 `fff6669b0bc0b15b…`.

Verdict: **ACCEPTED / READY_FOR_INTEGRATION**. No detector predicate changed and no Arena action
was taken.
