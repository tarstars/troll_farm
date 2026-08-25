# 20260824-dance-cure-proposal — propose a cure for the dances that survive in real games

- Status: **OPEN — CHARTERED 2026-08-24T19:40Z by owner instruction** (owner, coordinator session
  2026-08-24 ~19:30Z: *"send a message to chatgpt_1 with description what we discovered and task
  to propose a cure for these problems. You work on the same problem, then we will compare
  approaches"* — the coordinator's transcription).
- Record owner: local_claude_1 · Work owner: **chatgpt_1** (proposal) · Parallel, independent:
  **local_claude_1** (its own proposal, held unpublished until chatgpt_1's is delivered) ·
  Judge: **the owner** compares the two · Reviewer: none at this stage (design, not code)
- Area: the dance question — cure design. Successor to `20260824-real-game-dance-attribution`
  (DELIVERED) and the evidence dossier `docs/EVIDENCE-DANCE-2026-08-24.md`.
- Base: champion `547fa706…` = `cgauto/submissions/candidate-door1-pure-deletion.rs` (read-only;
  the resident and dev copy are byte-sacred). Evidence pins: `agent/local_claude_1@9050144a`
  (dossier commit follows), `agent/claude_1@4c92432f` (fact tables, report, brief).
- Branch: agent/chatgpt_1 (work), agent/local_claude_1 (record)
- Progress lease: 15 minutes without concrete evidence inside a session.
- Created UTC: 2026-08-24T19:40:00Z · Last updated UTC: 2026-08-24T19:40:00Z

## THE QUESTION (owner's, plain words)

We now know what the dancing troll is doing in real games (`docs/EVIDENCE-DANCE-2026-08-24.md`
§7–8). **Propose a cure.** Not code — a design the owner can compare against the coordinator's
independent proposal and, if chosen, charter for building and measuring afterwards.

## The problems, as measured (the cure must speak to each by name)

- **P1 — the working blocker (42 % of instrument episodes, 38 % of the champion's):** a teammate
  stands on one cell orthogonally adjacent to the two dance cells, *working* it — chopping,
  harvesting, picking, dropping, planting — with wait fraction ≈ 0; in 24 of 34 it stands on a live
  plant; in 10 of 34 it never leaves that cell again all game. The dancer bounces beside it.
- **P2 — no blocker, fixed target (22 of 80):** a teammate is alive but not adjacent/stationary; the
  dancer's stated target is the same cell every turn of the window and it still bounces.
- **P3 — no blocker, changing target (21 of 80):** same, but the stated target changes inside the
  window (two or more distinct real targets; not a tidy every-other-turn flip, which never occurs).
- **P4 — context, not a target:** we dance in ≈ 17 % of two-troll games versus 10–13 % for opponents
  in the same games, while blocking each other 0 % (opponents 14–23 %); the July pre-cure bot
  had the opposite profile (0 % dance, 43 % blocking). A troll given nothing while it had real work:
  0.72 % of troll-turns. No dancer ever wanted nothing.

Facts to design against, all measured: the library's *idle*-blocker shape does not occur in real
instrument games (0 of 80); half the episodes are the minimum 7-turn window and their "blockers"
later move freely, while long-window blockers often never move again (10 of 23); dances mostly end
by the dancer making progress (52 of 80) or the teammate finally moving (16); a cell-swap by the
two trolls occurs in 11 of 80 episodes.

## What the record already taught about cures (do not repeat)

- A fix that removes one pattern by force manufactures another: D171a (+117 % short runs), swap
  rev 1 (98 re-swaps in one game), anti-benching P1/P2 (detectors silenced, progress not restored),
  r2 (blocking games 35 → 115). **Every proposal states what it could manufacture and how that is
  detected.**
- An acceptance rule without a **progress term** is satisfied by silencing detectors. The measure
  of a cure is the troll doing useful work, not the alarm going quiet.
- Two locally correct rules can compose into a wall
  (`docs/DISCOVERY-two-correct-doors-make-a-wall-2026-08-17.md`); name the rule your change
  composes with.
- Displacing a working troll refuses to help: 2,010 of 2,245 benched trolls wanted to stay and
  work where they stood; 0 wanted a different square.
- Two generations of fixture-driven cures moved the ladder +0.17 ≈ 0.00. The ladder is the final
  judge, and it is deaf to small things.

## Deliverable — one document, `chatgpt_1/dance-cure/proposal-2026-08-2x.md`

For each of P1, P2, P3 (P4 as context):

1. **Mechanism you assume**, with the champion's code lines that produce the pattern (read the
   source; cite `file:line`; mark [READ] vs [INFERRED]).
2. **The rule change**, in plain words and in pseudo-code — what the troll does differently, where
   in the per-turn pipeline (candidate generation, joint pairing, movement/conflict resolution,
   idle fallback), and what state it needs across turns, if any.
3. **What it could manufacture** (the opposite defect, a new wall) and the detector that would
   catch it.
4. **Predicted effect on the evidence tables** — which rows of `EVIDENCE` §8 shrink, which stay,
   and by roughly how much; what it does *not* fix.
5. **How to measure it** with the accepted instruments (replay adapter + D-1 + the `mech`
   classification; the lineage grading; same-ladder alternating A/B with a progress term), and
   the kill rule.

Rank the changes if there are several; recommend one to build first. No code, no candidate, no
bot change, no Arena action, no verdict on other agents' work.

## Exclusive write set

- chatgpt_1: `chatgpt_1/dance-cure/**`, `coordination/status/chatgpt_1.md`,
  `coordination/messages/chatgpt_1/**`.
- local_claude_1: this record, `local_claude_1/dance-cure-proposal-2026-08-24.md` (held until
  chatgpt_1's handoff lands), status, STATE §4.

## Do not touch

- `rust/src/bin/yamo_orchard_live.rs` (`fff6669b…`), `cgauto/submissions/*`, `data/raw/games/`,
  any other agent's namespace, the Arena (controller local_claude_1).

## Acceptance

- A `handoff` from chatgpt_1 to local_claude_1 naming the full commit and the document path,
  `requires_ack: true`. The coordinator then publishes its own proposal (already written, held) and
  puts both in the owner's queue. The owner compares; whatever is chosen gets its own build charter
  with codex_1 review and the progress-term acceptance rule.

## Arena authority

Read-only platform access: not needed. Platform mutation: forbidden.

Deferrals: none.
