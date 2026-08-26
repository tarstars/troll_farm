# Fixture drift — diagnosis (2026-08-26, coordinator's local subagent, read-only)

Task `20260826-fixture-drift` (board 0-1). Outcome: **the 34 are retired as gates by owner ruling
15:45Z**; successor `20260826-fresh-fixture-dataset`. This file is the diagnosis of record.

## 1. What "reproducible on base" means

Not an engine-rot check. It asks: *does the candidate's re-run reproduce the episode the
**subject** bot recorded?* Two halves in `claude_1/t1/fixture_harness.py` (on `agent/claude_1`,
not `main`): `check_window_commands` (L154–177, every frozen turn's command vs the candidate's)
and `check_entry_state` (L180–214, plants/units/inventories at the window's first turn).
`episode_identity` (L217–240) fails closed; `grade` (L331–358) returns `NOT_REPRODUCIBLE_ON_BASE`
before reading any window. Library:
`claude_1/banana-restoration-r2/oscillation-library-98628e98/library/OSC-001…034.json`, recorded
from `cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs` (`98628e98`).

Both arms run today: subject bot → 34 graded, 0 not-reproducible (engine, maps, seeds, replay
intact); champion `547fa706` → 11 graded, 23 not-reproducible — the same split as the 08-21
artifact `claude_1/regrade2/regrade34-identity-2026-08-21.json`.

**Exact rule, no exceptions:** a fixture reproduces iff the champion's first divergence from the
subject's command stream falls strictly after the window's last turn. The 11 passers: 8 never
diverge (001, 002, 012, 013, 017, 021, 024, 026), 3 diverge late (005, 027, 030). All 23 failures
diverge at or before the window end.

## 2. The 23 — one cause

The candidate is a different bot from the one that recorded the fixture. No engine change, no
harness bug, no missing file, no map/seed mismatch (`spec_for` L106–124 verifies the rebuilt board
byte-for-byte and did not fire once). First divergence per fixture (turn): 003 t3, 004 t5, 006 t3,
007 t5, 008 t1, 009 t1, 010 t25, 014 t19, 015 t37, 016 t3, 018 t4, 019 t22, 020 t12, 022 t1,
023 t1, 028 t1, 029 t2, 032 t49 (board only), 033 t1 (board only); **near-misses** 011 t32,
025 t32, 031 t10, 034 t6 (1–4 commands of the window differ).

## 3. Recommendations as given (superseded by the owner's retirement ruling)

Group A (19): retire as gates — coverage carried by the 21 champion-lineage fixtures in
`oscillation-library-547fa706/library/` (`carry-over-2026-08-21.json`). Group B (011, 025, 031,
034): re-freeze on a champion run with `build_subject_library.py` (~2 h). Harness repair: none
needed; `claude_1/regrade3/panel_progress_adapter.py` `window_askable` (L195–216) is a *weaker*
question ("does the run contain the window") and must be adopted deliberately, never by drift.

## 4. Does the harness hide skips? No.

`fixture_harness.py` L503–504 prints `N FIXED / M graded (K NOT_REPRODUCIBLE_ON_BASE, not graded
either way)`; `regrade34.py` L156–158 prints the same and raises if all 34 pass.

**Correction to the premise:** the "34/34 fixtures byte-identical" containment verdicts
(`cure1/alpha_parity.py`, `cure3/containment.py`) call `load_situations` only and never
`episode_identity`/`grade` — they genuinely cover all 34. Only FIXED/NOT-FIXED grading is 11/34.

## 5. Effort / risk

Re-freeze Group B + control ~2 h; full champion-lineage 34 ~4–6 h; retire + docs ~1 h. Risk to
existing verdicts low: no live FIXED claim depends on the 23 (the 8 that once read FIXED were
withdrawn on 08-21, `fixed_with_identity_enforced: []`).
