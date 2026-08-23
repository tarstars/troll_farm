# NARRATE — the bot says what it intends, and we read it back from real games

**NARRATE** is the handle. One line: *our bot prints each troll's target every turn using the
`MSG` output command; the platform records it; we read intentions out of real ladder games
instead of inferring them from 34 hand-picked fixtures.*

- Status: **OPEN — owner-raised 2026-08-23** ("I have concerns about the quality of our measuring
  baskets. I want to conduct such experiments in real games"). Capability audit **done**;
  step 1 is one Arena submission and needs the owner's go, because the ladder is deliberately
  stopped.
- Record owner: local_claude_1 · Build: **claude_1** · Review: **codex_1** · Arena: owner + controller.
- Created UTC: 2026-08-23T06:25:00Z

## Why this exists

Every behavioural claim this project has made about dancing, blocking and idleness rests on a
**34-fixture library** — hand-picked, recorded on a bot that has since been retired, and known to
be a biased sample (the benching set was chosen *because* a troll was benched). The owner's
concern is exactly right, and the 2026-08-23 intention measurement had to be published with the
caveat "biased by construction" attached.

Meanwhile the direct ladder measurement says the whole cure programme is worth
**+0.17, ≈0.00 symmetrised** — so the fixtures have been steering work that the ladder cannot see.

## Capability audit — verified 2026-08-23, by execution, not recall

| capability | state | evidence |
|---|---|---|
| submit to the platform | **have it** | 20 submissions across two blocks on 08-21/22, hash-verified, fail-closed |
| collect the telemetry | **have it, richly** | 21,496 games stored, **8,590 ours**; **both players' commands every turn**; 301 world states for a 300-turn game (positions, cargo, inventories, plants); full map |
| reconstruct the dance | **possible, not built** | every detector input is present in a replay; sized as shape translation, `local_claude_1/corpus-identity-2026-08-22.md` |
| reconstruct **intentions** | **impossible from a replay — but the bot can say them** | see below |
| reconstruct the stall detector | **not as accepted** | it reads state off a *live referee*; a replay keyframe is a reconstruction, not that input. A definition change, not a tooling job |

**The intention finding.** A replay records what the bot *did*, never what it meant — the target
lives inside our process and dies there. But `MSG <text>` is a legal output command, and it
survives end to end. Verified on a real Arena game we played on 2026-08-22 (`899964767`, our
agent `6648254`, seat 0): turn 1 reads

```
MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 5 6
```

That text went to the platform, returned in the replay, and is byte-preserved in
`data/processed/trajectories/899964767.jsonl`. **And we use the channel exactly once per game** —
a fixed banner on turn 1. It is idle for the other 299 turns.

There is **no `stderr`** in the frames; `stdout` is the only channel, and it is captured for
**both** players on every turn.

## The sequence

**Step 1 — the length probe. One submission, and it gates the design.** We do not know the
`MSG` length limit; our banner is 41 characters and two trolls' targets every turn is longer.
Emit a deliberately long, structured message and read back what survives. **Needs the owner's go
— the ladder is stopped.**

**Step 2 — parity.** An instrumented bot is a *different candidate*, not the champion: it changes
the command stream, so no byte-identical comparison against the champion can pass. `MSG` is
*believed* cosmetic; believed is not a gate. Prove play is unchanged — same seeds, same
decisions, message stripped.

**Step 3 — the replay→`Trace` adapter**, already sized. Its one trap is the alignment of 301
states to 300 command rows, which the existing code truncates **silently**.

**Step 4 — grade real games.** Dancing, blocked passes and now *intentions*, over thousands of
our own recorded games rather than 34 fixtures — which answers the corpus-prevalence card and the
intention question on the same instrument.

## What it would settle

- Whether the fixture library's picture of these defects holds on real play at all.
- The intention question on an unbiased sample: today's "in 100 % of cases the standing troll's
  want cannot be served by displacement" is measured on the retired bot's *benching* set and is
  explicitly not established for the champion.
- The owner's own prevalence question — how often each ruled defect actually occurs, by agent id.

## Costs and limits, stated up front

Message length unknown until step 1. An instrumented bot occupies the Arena slot we deliberately
stopped. The stall detector stays unavailable on replays regardless. And the instrumented arm can
never be the champion — it is a measuring instrument, run to learn, then retired.
