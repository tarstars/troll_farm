# 20260825-dance-cure-candidate-1-hold — Candidate 1: a blocked troll holds instead of stepping backwards (+ v4 telemetry)

- Status: **OPEN — CHARTERED 2026-08-25T07:55Z by owner instruction** (owner, coordinator
  session: *"do it"* to the plan "Candidate 1 first, with the v4 telemetry field built into the
  candidate" — the coordinator's transcription).
- Record owner: local_claude_1 · Work owner: **claude_1** (build: candidate, instrument variant,
  v4 decoder, gates) · Reviewer: **codex_1** (G-0 design pre-build, G-1 execution) · Arena
  controller and integrator: local_claude_1 (submits the instrument read and the score block).
- Area: the dance cure, first build. Inputs: `docs/EVIDENCE-DANCE-2026-08-24.md`,
  `local_claude_1/dance-cure-proposal-2026-08-24.md` (approach A without the swap),
  `local_claude_1/dance-mechanism-map-2026-08-25.md`, chatgpt_1's r2
  `agent/chatgpt_1@a90ff533:chatgpt_1/dance-cure/proposal-r2-correction-2026-08-25.md` (its
  pair-level step check is **step 4** of the plan, not this candidate).
- Base: champion `cgauto/submissions/candidate-door1-pure-deletion.rs`, SHA-256
  `547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0` (1,474 lines). Telemetry
  source to transplant: `agent/claude_1:claude_1/narrate3/instrument-swap-r1-narrate-v3.rs`
  (`9a3e8758…`) — **the `MSG` hunk only; the swap rule is retired and must not be carried.**
- Branch: agent/claude_1 (work), agent/codex_1 (review), agent/local_claude_1 (record, Arena).
- Progress lease: 15 minutes without concrete evidence inside a session.
- Created UTC: 2026-08-25T07:55:00Z · Last updated UTC: 2026-08-25T07:55:00Z

## THE QUESTION (owner's, plain words)

When one of our trolls finds its next step taken by its teammate, today it walks **backwards**
(the resolver may not let it stand still and picks the best free neighbour, which in a corridor is
the cell it just left), then forwards, then backwards — a dance. **Does letting it stand still for
up to two turns, instead of stepping backwards, remove the short dances in real games without
parking trolls or costing score?** And can we *see* the rule fire, turn by turn, in real games?

## The change — read from the code, minimal

`resolve_move_conflicts_with_priority_and_forbidden` (`:720-772` of the base). Today, when a
mover's landing is reserved/forbidden (`:749-750`), the detour (`:755-762`) is the free orthogonal
neighbour with the smallest BFS distance to the target, and `unit.cell` is not a candidate.

```
per unit, across turns:  blocked_turns: BTreeMap<unit_id, u8>   (new field on YamoBot)

when the landing is blocked:
  d_cur  = toward_goal[unit.cell]          (bfs distance from the unit's own cell, same map as :755)
  detour = best free orthogonal neighbour as today
  if detour exists and toward_goal[detour] <= d_cur:        -> take it (lateral/improving; unchanged)
  else if blocked_turns[id] < W (W = 2):                    -> emit WAIT, blocked_turns[id] += 1   [HOLD]
  else:                                                     -> take the regressive detour as today
                                                               (or WAIT if none), blocked_turns[id] = 0
when the landing is free, or the unit emits a non-MOVE command: blocked_turns[id] = 0
```

Nothing else changes: no swap, no re-targeting, no change to candidate scores or `compatible`.
The bound `W` is what keeps a hold from becoming a parked troll: after two holds the old
behaviour returns for one turn, so the worst case is a slower dance, never a stall.

## Telemetry v4 — the rule must be visible in real games

Extend the NARRATE payload (v3 grammar → v4, same `MSG` line, versioned with refusal in **both**
directions like v2/v3) with, per own unit per turn: `r=` the resolver branch taken —
`P` primary landing · `L` lateral/improving detour · `H` hold (new rule) · `R` regressive detour
(hold expired or rule off) · `W` forced WAIT (no neighbour) · `N` no MOVE this turn — and
`b=<blocked_turns>`. Longest v3 payload was 111 characters against 2,000 safe; v4 adds ≤ 12 per
unit. Decoder `claude_1/narrate4/` with the gp3-style controls: every code attested by a fork that
can produce it, poison forks for the two new ones, v3↔v4 mutual refusal proven.

Two builds from one source and a compile-time flag:
- **instrument arm** = base + hold rule + v4 telemetry (for the real-game read; can never be champion);
- **candidate arm** = base + hold rule, no `MSG` (for the score block and, if kept, the ladder).
- **rule-off arm** = base + v4 telemetry, hold disabled (parity reference).

## Gates (fail-first, in order)

- **G-0 design review (codex_1, one wake, before any code):** the predicate above, `W = 2`, the
  reset rule, the v4 grammar and refusal, the parity plan. `DESIGN_ACCEPTED` / `REVISION_REQUIRED`,
  published `requires_ack: true` toward claude_1.
- **G-1 build + parity + panel (claude_1 builds, codex_1 re-runs from a fresh archive):**
  1. rule-off arm with `MSG` stripped is **byte-identical in play** to the base on the 34 frozen
     situations and the 240-game named-cost panel (the α parity gate, reused);
  2. rule-on arm on the 240-panel: blocking games **not above** the base's 35 (r2 went 35 → 115 —
     that is the shape to fear); P3 orchard-inertness clean; long-stall (P4) games not above base;
     every changed game named with its first divergence;
  3. the 11 fixtures the champion reproduces: no `FIXED` lost; any gained reported with
     `progress_restored`, never detector silence;
  4. controls: a fixture where the hold fires and the dance ends with progress (positive); a
     poison arm that holds on **every** blocked step forever (must be caught by the P4 gate); the
     v4 decode controls.
- **G-2 real-game read (local_claude_1 submits; claude_1 grades; codex_1 checks):** one ~160-game
  instrument read; games collected before any resubmission; graded with the accepted adapter +
  D-1 + the r3 classification **and** the v4 branch counts. Acceptance: (a) holds fire and are
  followed by the dancer's progress (F7 `DANCER_PROGRESS` share not lower than the instrument's
  52 of 80); (b) regressive-detour turns per 1,000 turns down by at least half against the v3
  instrument read (`6652642`), and D-1 episodes per 1,000 turns down — attributed to the P1-short
  and P2 rows, not to silence; (c) kill rules: idle troll-turns (wanted real work, emitted WAIT)
  above 1.5 % (baseline 0.72 %); own-troll contention above 0; long-stall share of games above
  the champion's; any P1/P2 row migrating to a parked or stalled shape.
- **G-3 score floor (local_claude_1, owner rules):** one ABAB block, five pairs, candidate arm vs
  the champion, difference by arm. Kill below −1.0; otherwise the owner rules KEEP under the
  08-22 rule (behaviour axis passed, score a floor).

## Exclusive write set

- claude_1: `claude_1/cure1/**` (sources for the three arms, build script, parity/panel results,
  the G-1 report), `claude_1/narrate4/**` (v4 decoder + controls), its status and messages.
- codex_1: `codex_1/reviews/**`, its status and messages.
- local_claude_1: this record, `cgauto/submissions/candidate-hold-v1*.rs` (placed at submission
  time from claude_1's delivered bytes, hash-verified), the read/block ledgers under
  `local_claude_1/cure1/`, STATE §4, status.

## Do not touch

`rust/src/bin/yamo_orchard_live.rs` (`fff6669b…`), `data/raw/games/`, the 02:17 UTC cron, other
namespaces. No agent but local_claude_1 submits, fetches, or opens a TestSession.

## Arena authority

Two Arena actions are pre-authorized by the owner's "do it" for this task and no other: (1) one
instrument read at G-2; (2) one five-pair ABAB block at G-3. Both are surfaced to the owner before
they start (a notification, not a permission request). Anything else is a new decision.

## After this candidate

Queued, each its own charter after this read: **Candidate 3** (score smoothing at
`predict_tree`'s travel horizon, for the changing-target dances); **Candidate 2** (the long P1
tail: swap the working teammate or route around it — **the owner's ruling, still open**); then
the structural step (chatgpt_1's pair-level next-step compatibility), then joint planning.

Deferrals: none.
