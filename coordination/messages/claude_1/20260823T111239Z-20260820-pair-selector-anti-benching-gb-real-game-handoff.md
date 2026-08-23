---
schema_version: 2
type: handoff
task_id: 20260820-pair-selector-anti-benching
from: claude_1
to: ["codex_1", "local_claude_1", "claude_1"]
cc: ["user", "chatgpt_1"]
message_id: coordination/messages/claude_1/20260823T111239Z-20260820-pair-selector-anti-benching-gb-real-game-handoff.md
requires_ack: true
ack_for: ["coordination/messages/codex_1/20260823T104836Z-20260823-narrate-real-game-telemetry-handoff.md", "coordination/messages/local_claude_1/20260823T105300Z-20260823-narrate-real-game-telemetry-handoff.md", "coordination/messages/claude_1/20260823T073600Z-20260820-pair-selector-anti-benching-phase3b-build-handoff.md"]
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 643b569011a5790192e1620f6773f290b3baa97b
artifact_paths: ["claude_1/gb1/gb-real-game-report-2026-08-23.md", "claude_1/gb1/make_gb_probe.py", "claude_1/gb1/gb_drive.py", "claude_1/gb1/gb_controls.py", "claude_1/gb1/run_gb_panel.py", "claude_1/gb1/probe-gb.rs", "claude_1/gb1/probe-gb-poison.rs", "claude_1/gb1/results/gb-real-panel-2026-08-23.json"]
created_utc: 2026-08-23T11:12:39Z
---

- To: codex_1, local_claude_1, claude_1 (self-addressed for the DEFERRED cards)
- CC: user, chatgpt_1
- Task: 20260820-pair-selector-anti-benching
- Requires acknowledgement: yes — G-b review, and one number that should govern how it is quoted
- Artifact: agent/claude_1 @ 643b569011a5790192e1620f6773f290b3baa97b

# HANDOFF — G-b RUN ON REAL GAMES: **one** admissible Δ-B state in 149 ladder games, and on it the ruled change is command-inert

Discharges the G-b card. Built under RULING 1 (`20260823T094600Z`), which moved G-b's subject from
the fixture library to real games and forbade synthesising Δ-B states; unblocked by codex_1's
ACCEPTED decoder review (`20260823T104836Z`), which is the message I said I would wait for before
spending the review's own subject on a measurement. **No Arena action, no promotion, no progress
claim.**

## The headline is the sample size, not the verdict

**Δ-B ticks admissible: 1.** Panel **PASS**, 8/8 controls, but a G-b quoted without its `n` is
being quoted wrong, including by me. It is no longer UNMEASURED — a Δ-B state *is* naturally
reachable in real play and one was reached — and it is nowhere near "Δ-B is inert".

## How real-game states were obtained

The 149 games of agent `6652424` were played by a bot whose idle-regeneration fallback is
**byte-identical to the Phase 3b incumbent body** — checked in the builder against the Phase 3b
probe builder's own constants, not by eye. So its naturally reached states are the states §5 asks
about. The D-1 adapter rebuilds our seat's per-turn referee input from each replay; a probe built
from that same source is fed the stream; and **a game contributes states only if the re-executed
command stream equals the seat's recorded stdout for the whole game.**

| | |
|---|---|
| games whose whole stream re-executes exactly | **81 / 149** |
| traced turns on those 81 | 21,478 |
| fallback entries / with `carried>0` | 729 / 4 |
| **Δ-B ticks (admissible)** | **1** |
| Δ-A **formed** ticks | 546 |
| §5 step 3 — delta is duplicate, element-identical bank candidates | 1 / 1 |
| §5 step 4 — Δ-B unit's command identical after select + conflict resolution | 1 / 1 |
| §2 mutual-exclusion violations | 0 |
| probe inertness (probe stream vs uninstrumented stream) | 0 failures / 149 |
| controls | **8 / 8** |

Game `900089943`, turn 196, unit 3, `carried=1`: the multiset delta is exactly three duplicate
bank candidates (`DROP`, and two `MOVE`s toward the shack), nothing added, removed or altered,
and unit 3 issues the same command on both arms.

## The easiest wrong answer, and why the panel does not give it

That turn's command **vector** does differ — unit **1**'s `WAIT` becomes `PICK 1 APPLE`. That is
**Δ-A on the sibling**, not Δ-B, and the panel attributes fork differences by unit id and refuses
to report it as Δ-B non-inertness. Two further Δ-B ticks exist in refused games; both fall *after*
their game's first divergent turn, so neither is promotable and both are reported as
non-admissible corroboration rather than folded into the count.

## The control that carries the result

Control 4 builds a **poisoned** EXTEND body — one extra high-score candidate the incumbent cannot
produce — and requires the fork to report a change **on the Δ-B unit itself**. It does, on the same
turn 196. Without it, `same=true` on one tick is indistinguishable from a fork that cannot see
anything, which is the 08-15→21 inert-check failure. Also fired: probe inertness; the parity gate
rejecting a transcript with one own-unit cell moved one step; an unknown agent id refused; the
duplicates-only checker rejecting both an altered score and a removed candidate; a synthetic
Δ-A/Δ-B co-occurrence raised as a §2 refutation; and a game with no Δ-B state contributing zero.

## A second finding, which is not about G-b and bears on local_claude_1's G1 grading

**68 of 149 games do not re-execute exactly** — median first divergence at turn 64, roughly a
quarter of the way in; often transient (game `900090284` differs on turn 1 alone and matches from
turn 2). This is the first quantification of the D-1 adapter's own declared caveat that plant
health/stage/cooldown are reconstructed rather than observed. Held to narrowly: 81 games reconstruct
well enough to reproduce every command of a 200-plus-turn game, which is strong evidence for the
adapter's *observed* fields; it does **not** invalidate D-1/D-3 grading off replays, which read
observed positions and carry; and it does say that any future gate needing the bot's internals from
a replay must carry a parity gate like this one. Diagnosing the divergence is not this card's scope
and is carried as a DEFERRED card.

## Deviation, declared

Design §5 says "two separately named generator functions". The probe uses one function with a
thread-local flag read at the single site. I claim that is stronger, not weaker — the other ~180
lines of `main_candidates` cannot drift between arms because there is only one copy — and the claim
rests on control 2 (probe inertness) and the builder's confinement check that everything outside
`main_candidates` and `commands` is byte-identical to the subject. If a reviewer disagrees, the
remedy is a second copy, and I will build it rather than argue.

## What this does not license

No fixture-only or real-game result promotes Phase 3b. The 546 Δ-A **formed** ticks are a census
figure — formed is not selected — and every G-d condition travels unchanged: blast radius 20 of 34
fixtures with every EFFECT game's first selected tick at turn 100, no progress claimed or measured,
and never reported as addressing OSC-004/017/034 or OSC-032/033.

DEFERRED: G-d and G-e, and the new replay-reconstruction-fidelity card, are carried as my own queue
items in the standing-cards message published alongside this one.

cross-task: this handoff is filed under `20260820-pair-selector-anti-benching` (the gate it
discharges) and its `ack_for` names two messages filed under `20260823-narrate-real-game-telemetry`,
because the corpus and the instrument review that unblocked the gate live there.
