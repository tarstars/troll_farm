# HANDOVER 2026-08-25c — Candidate 2 measured, reproduced, and stopped at the owner's two questions; P4b and the quarantine move done

Read `coordination/HANDOVER-2026-08-25b-dance-geometry.md` and, for everything before noon,
`…-08-25-candidate-1-close.md`. This file is the delta 15:55Z → 23:15Z. Written by
`local_claude_1`.

## Resume here

- `coordination/GOAL.md` = **no active mission** (mission archived at
  `coordination/goals/20260825-candidate-2-swap-mission.md`). Ritual unchanged; the sweep now reads
  the quarantine from `origin/main` (roster v2).
- **Owner's queue:** (1) `local_claude_1/cure2/owner-question-2026-08-25.md` (v3) — the loop
  (A planner "keep your goal" / B narrow the rule / C read anyway / D stop) and Candidate 0 (the
  champion's replant-fallback bug); (2) the Candidate 1 verdict sheet (parked, code kept — done);
  nothing else needs them.
- **Follow-up charters, after the owner's ruling or on the next idle wake:**
  `20260826-p4b-narrator-param` (the `--p4b` gate reads v4 only; Candidate 2 narrates v5;
  `evaluate_rows` already takes a narrator — wire it at `p4b_gate.py:387` and
  `fuzz_panel.py:2443-2444`; codex_1 builds, claude_1 reviews) and `20260826-deferred-card-lint`
  (a `-deferred` message with no `^DEFERRED:` line is a lint error; codex_1 builds, claude_1
  reviews).

## What happened

1. Owner rulings ~15:55Z on the whole queue (R-1a in `docs/RULES-LEDGER.md`): Candidate 2 =
   swap with **no lock**, the swap back impossible by construction and proved; Candidate 1 parked,
   code kept; P4b chartered; quarantine list to `main`. Three charters at 16:34Z; owner `/goal`.
2. **P4b DONE** (`20260825-p4-per-troll-stall-gate`): unit-keyed differential gate, poison arm
   BLOCKed on a new key, champion baseline **27 parked-unit episodes on 16 of 240 games** (R-2's
   size on the panel); wired behind `--p4b` (default OFF, report tier).
3. **Quarantine-on-main DONE** (`20260825-quarantine-on-main`): authority files read from
   `origin/main`; roster v2 with `former_coordinators` (B′ + option 3 named limitation in §10.2);
   134/134; all five roster ids 12/0/0/0; launcher clone refreshed from 197 commits behind.
4. **Candidate 2** (`20260825-dance-cure-candidate-2-swap`): G-0 with proof accepted 16:56Z; built
   17:17Z (rule-off byte-identical to the champion on 274 games; panel dances 27 → 13); stopped at
   the pre-committed C-5 counter. Diagnoses: the loop = the pair selector re-assigns goals to the
   cells (−5 on 1/240 games); `m061` −75 = the champion's `idle_regeneration` fallback discarding
   replant PICKs after the freed troll fells the last tree. Sixteen controls + the P3 read, all
   accepted by codex_1 from fresh archives (C-10 66/66, C-11 54,800/54,800, C-13 1,096/1,096,
   C-7 counters live, C-8 9 cured / 4 silenced, C-16 scoping works, P3 0/240 with 228/12/0, C-12
   corpus 0.38 % vs 0.73 % by coordinator ruling). Cost in units: −24 own-score net (one map),
   +56 margin, +39 margin forgone on orchard maps, fixtures +35. **Not qualified**; both stops are
   the owner's; no Arena action taken; the G-2 arm not placed.
5. Operations: the launcher rings only on ack-required news (re-rung once); one wake died on a
   transient 403 at the proxy **after** doing its work and before pushing (re-verified from
   scratch by the next wake; probe `claude-proxy -p` answers `OK`); claude_1's six cards were
   shape-invalid (`# DEFERRED` headings) — a recurrence; rule: after publishing a card, re-run the
   sweep and confirm it appears under "unacknowledged, ack required"; a 110-second ruling
   collision on C-12 (codex_1 BLOCK / coordinator PASS on identical numbers) resolved by codex_1's
   concurrence — a verdict that is a reading of a sentence can flip with no measurement moving.

## Arena — unchanged

Resident: the Candidate 1 instrument (agent `6659743`); champion of record door 1 `547fa706…`,
off ladder; `NIGHT-HALT`. No action taken or authorized today.

## Owed by me

Nothing to the peers. To the owner: the v3 page. Peer branches carry ~170+ unmerged commits
each; integration owed, non-blocking, pin-only.
