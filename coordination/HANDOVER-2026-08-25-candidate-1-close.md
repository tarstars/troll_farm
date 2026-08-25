# HANDOVER 2026-08-25 — Candidate 1 closed at G-2; the dance programme's state at flush

Read `coordination/HANDOVER-2026-08-24b-flush-delta.md` for the role/transport posture (still
true); this file is the science and the queue since then. Written at ~12:50Z on 2026-08-25 by
`local_claude_1`, trunk `a01f31af` + this commit, `origin/main` == `agent/local_claude_1`.

## Resume here

- Agent `local_claude_1` — coordinator, integrator, **sole** Arena controller (owner, 08-24).
  Worktree `/home/tarstars/prj/troll_farm-local_claude_1`; the main checkout at
  `/home/tarstars/prj/troll_farm` is on the stale `session-2026-07-01` branch (and holds the
  untracked 23k-game corpus under `data/raw/games/`). **Every shell command must `cd` into the
  worktree** — the harness resets the cwd to the main checkout between calls.
- Ritual: `python3 scripts/inbox_sweep.py --me local_claude_1 --fetch`; read every new message
  from the peer's remote ref (`git show origin/agent/<id>:<path>`); `--mark` as its own step;
  commit the seen-state. At flush: exit 0, 0 delivery errors, 12 quarantined, 0 owed.
- `coordination/GOAL.md` = **no active mission**. `docs/STATE.md` §4 is current (150/150 lines).
- **Owner's queue (nothing else needs them):** `local_claude_1/cure1/owner-verdict-sheet-2026-08-25.md`
  — (1) park/revise/retire Candidate 1 (recommendation: park); (2) **Candidate 2**: swap the
  never-moving teammate once, or route around it; (3) charter the per-troll stall gate or leave it
  recorded. Also standing: the quarantine role-fragility decision (blocking nothing).

## What happened 2026-08-24 evening → 2026-08-25 noon

1. **Dance synthesis delivered** to the owner; **evidence dossier** `docs/EVIDENCE-DANCE-2026-08-24.md`
   (everything measured since July, with sources).
2. **Attribution on real games** (`20260824-real-game-dance-attribution`, DELIVERED): 462 episodes
   classified; 4 in 10 have a teammate parked on a plant *working* it beside the dance; the fixture
   library's idle-blocker shape is 0 of 80 in real instrument games; no troll danced wanting
   nothing. Lineage: champion 16.8 % of 2-troll games = very-old 17.4 % (same-ladder +0.00);
   swap R-1 is not the origin. Brief: `local_claude_1/dance-attribution-owner-brief-2026-08-24.md`.
3. **Mechanism read from the champion's code** (`local_claude_1/dance-mechanism-map-2026-08-25.md`):
   unit-blind BFS pathing + occupancy-aware resolver whose detour set excludes the troll's own cell
   → forced backward step → a→b→a. `compatible` forbids targeting a working troll's cell (why the
   dancer's target is always elsewhere). No cross-turn memory in the bot.
4. **Two cure proposals**, independent: mine `local_claude_1/dance-cure-proposal-2026-08-24.md`
   (A: hold then one swap; B: score smoothing, road pricing; C: joint planning) and chatgpt_1's
   **r2** `chatgpt_1/dance-cure/proposal-r2-correction-2026-08-25.md` (pair-level next-step
   compatibility; diagnose before build). chatgpt_1's first version cited invented figures; r2
   withdrew them by name and is verified. Its r2 *message* file is mis-named (`-correction-r2.md`
   fails `MSG_RE`) — republication requested (`20260825T073000Z`), harmless.
5. **Candidate 1 built and measured in one day** (`20260825-dance-cure-candidate-1-hold`, owner
   "do it"): G-0 (codex_1, 8 definitions; claude_1's reservation-order hazard → my two-phase
   fixed-point construction ruling), G-1 as built REVISION_REQUIRED (orchard break; idle 2.28 %;
   **P4 gate found blind**), revised arm (hold only on transient blocks) ACCEPTED, **G-2 read of
   160 real games: FAIL on both acceptance clauses, no kill rule fired** — the hold fired 253× in
   102 games and in **0 of 25 recorded dances**; the real dances are permanent-block dances. codex_1
   reproduced the grade byte-for-byte. Candidate 1 PARKED pending the owner; G-3 not started;
   **the second pre-authorized Arena action is unspent**. Records: task card,
   `local_claude_1/cure1/` (read ledger, 160-game package `050d1ceb…`, verdict sheet),
   `claude_1/cure1/` (`agent/claude_1@22d6b2bb`), `codex_1/reviews/dance-cure-candidate-1-*`.

## Arena state

Ladder resident: the Candidate 1 instrument (agent `6659743`, submission `41192036`, source
`cgauto/submissions/candidate-hold-v1-instrument.rs` `cc4b3087…`) — a measuring instrument that
can never be champion; no restore obligation (owner, 08-23). Champion of record still door 1
`547fa706…`, off ladder. `NIGHT-HALT` on the VM, `night-runner.service` down; the agent launcher
is active (claude_1/codex_1 wake on ack-required mail). Off-ladder TestSession burst used today: 1
of 12.

## Standing facts worth not rediscovering

- Rulings must be published `requires_ack: true` toward the ruled party — a bare `ack` receipt
  wakes nobody (claude_1 slept 40 min on one). Message filenames must match `MSG_RE`
  (`<stamp>-<task>-<kind>.md`, kind letters only) or they are not messages to any sweep.
- Stamps are `date -u`, never ahead; do not `sleep` until a stamp inside a 5-minute command.
  Never pad a short hash into a 40-hex `artifact_commit` — `git rev-parse` it.
- The panel's P4 stall gate is game-level and blind to one parked troll; the per-troll
  idle-with-work share (`H`+`W`, line 1.5 %, champion 0.73 %) is the safety net of record.
  "P3 clean" on an orchard-eligible seat view means the whole game.
- The champion's own forced-`WAIT` mover leaves its cell unreserved (latent contention, pre-existing,
  excluded from Candidate 1) — recorded, unchartered.
- Peer branches carry ~150+ unmerged commits each (their 08-23/25 tooling); integration into
  `main` is owed and must be done with the quarantine hazard in mind (never merge wholesale; pin).
- chatgpt_1 lives in the owner's interactive session, not on the VM launcher.

## Owed by me

Nothing to the peers. To the owner: the verdict sheet is written; the next charter (Candidate 2,
P4 gate, or Candidate 3 score smoothing) waits on their ruling.
