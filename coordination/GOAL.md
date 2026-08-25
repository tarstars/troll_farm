# GOAL — no active autonomous mission

You are `local_claude_1`: project coordinator, integrator, and the **sole** Arena controller
(owner, 2026-08-24). `local_codex_1` is a contributor with no integration or Arena authority.

## Current state

The previous mission — *drive Candidate 2 (the swap, no lock, proved) to its gates, with the
per-troll stall gate and the quarantine move beside it* — is **complete, 2026-08-25T23:15Z**
(archived at `coordination/goals/20260825-candidate-2-swap-mission.md`):

- **P4b** (`20260825-p4-per-troll-stall-gate`) — DONE: a per-troll stall gate behind `--p4b`,
  the poison arm caught, the champion's parked-troll baseline measured (27 episodes on 16 of 240
  panel games).
- **Quarantine list on `main`** (`20260825-quarantine-on-main`) — DONE: roster v2, a role
  transfer is now one roster edit; every roster id sweeps 12 / 0 / 0 / 0.
- **Candidate 2** (`20260825-dance-cure-candidate-2-swap`) — G-1 complete and reproduced by
  codex_1 (dances 27 → 13 on the panel, sixteen controls pass), **not qualified**: the
  pre-committed stops fired — the pair-swapping loop (a planner re-assignment, 5 points on one
  game) and `m061` (a champion planner bug worth 75 points that the exchange exposes). Both are
  the owner's rulings, on `local_claude_1/cure2/owner-question-2026-08-25.md` (v3).

The ladder holds the Candidate 1 instrument (agent `6659743`); nothing requires restoring
anything (owner, 2026-08-23). No Arena action was taken today.

## Direction

There is no active autonomous goal. Sweep the inbox on each wake, discharge what is owed, and
await the owner's rulings (the loop: A planner "keep your goal" / B narrow the rule / C read anyway
/ D stop; Candidate 0, the champion fallback fix). Two follow-up charters wait for the next idle
wake or the owner's word: `20260826-p4b-narrator-param` and `20260826-deferred-card-lint`
(codex_1 builds, claude_1 reviews, both small, no Arena).

Do not charter Candidate 0, Candidate 3, route-around, or a read; do not run panels, start score
tests, submit bots, merge peer branches, or restart autonomous operation from this file. Each
requires its own current charter or standing authority. All rules in `docs/STATE.md` and
`coordination/multi-agent-protocol.md` remain binding, plus the standing operational rules of
2026-08-25: fresh-archive extracts are scratch removed by `trap`; a dying session's last act is a
`blocker`; after publishing a card, re-run the sweep and confirm it is live — a clean lint is not
evidence; a peer silent past its lease after ack-required mail is checked on the VM (wake log,
session log, `df`) before it is assumed to be thinking.
