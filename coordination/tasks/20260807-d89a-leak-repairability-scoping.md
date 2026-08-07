# 20260807-d89a-leak-repairability-scoping: is D89a's opponent-production leak repairable?

- Status: assigned — owner ruling 2026-08-07; may start after Phase 1 has an owner, analysis only
- Record owner / integrator: `local_claude_1`
- Work owner (analyst): `claude_1`
- Independent reviewer: `chatgpt_1`
- Area: banana programme route selection
- Base commit: `2ac569164e273be511e43fbfc5c0649b3756784d` (`main` == `session-2026-07-01`)
- Branch: `agent/claude_1` (canonical)
- Progress lease: 15 minutes without remotely inspectable concrete progress
- Created UTC: 2026-08-07T16:00:00Z
- Last updated UTC: 2026-08-07T16:00:00Z

## Why this exists

The owner has **not** chosen between routes. This task buys the evidence to choose.

Route A is the R2 wrapper line: eight implementation attempts, zero valid candidates, best result
22/240 blocking games, design-led but never a working orchard in measurement.

Route B is D89a `banana_seed_factory` (2026-07-21), which **works**: 256/256 activation across
both seats and all eight opponent families, all 1,344 bank BANANAs planted, sustained
harvest/replant in 252/256, mean paired margin **+79.441**, 95% CI **[+40.991, +117.892]**,
catastrophes 26 → 11, negative-margin mass 0.584×. It was rejected on **safety**: mean
opponent-score delta **+82.863** against a ≤ +1 gate, worst margin delta −235, worst
opponent-family mean −6.938 against ≥ −5, active p10 −72 against ≥ −20.

The decisive detail, and the reason this is worth one scoped analysis: the result artifact states
that **direct theft of our crops is not the dominant leak** — the larger term is the opponent's
*own* created crops. The mechanism changed the competitive schedule rather than simply feeding the
opponent. That is a different problem from the one Route A keeps failing at, and it may be
tractable.

## Outcome

Exactly one verdict on whether D89a's opponent-score leak is repairable **without destroying the
production gain that makes it interesting**:

| verdict | meaning |
|---|---|
| `REPAIRABLE` | a specific, named mechanism change plausibly brings opponent delta to ≤ +1 while retaining materially positive margin; state the change and what it costs |
| `NOT_REPAIRABLE` | the leak is structural to the mechanism; state the argument and what evidence would overturn it |
| `UNRESOLVED` | cannot be judged from committed evidence; state exactly what measurement is missing and what it would cost to obtain |

A `NOT_REPAIRABLE` verdict is a full success for this task — it closes a route with evidence
instead of leaving it as a permanent open question.

## Required content

1. **Decompose the +82.863.** How much is direct theft of our crops versus the opponent's own
   production, exactly, with the figures re-derived from the committed artifacts rather than
   quoted. Both reviews and the coordinator have so far relied on a qualitative reading.
2. **Mechanism of the schedule change.** *Why* does our private production raise opponent output?
   Identify the causal path in the D89a controller, not just the correlation.
3. **Candidate repairs**, each with the gate it targets and the production cost it would incur.
   Consider at minimum: bounding the orchard, timing/phase restriction, geometry restriction to
   contested-free zones, and conversion timing.
4. **Interaction with the standing rule.** Would any proposed repair introduce D-1/D-4 episodes?
   Raw zero is owner-standing and non-negotiable.
5. **Honest cost estimate** against Route A: Route A has consumed roughly a week for zero valid
   candidates. Say what Route B would plausibly cost, and say if it is worse.

## Sources

`data/analysis/live-agent-6553250/d89a-banana-seed-factory-{blueprint,protocol,result}-2026-07-21.md`,
`…-{discovery-result,freeze}-2026-07-21.json`, `cgauto/analyze_d89a_banana_seed_factory.py`,
`tests/test_analyze_d89a_banana_seed_factory.py` — all present on `main`. Re-running the committed
analyzer is encouraged; embed the exact command and every input SHA-256.

## Declared conflict of interest

`claude_1` owns Route A. A `NOT_REPAIRABLE` verdict on Route B protects its own line, so it must
argue this against its own interest and say so explicitly in the artifact. Mitigating context:
claude_1 surfaced D89a itself, against that same interest, which is why it holds this task.
`chatgpt_1` reviews independently — noting that its own disposition called this lineage "fully
superseded" and missed D89a, so it has a symmetric interest in the opposite direction. Both
interests are on the record; neither agent is recused.

## Prohibitions

Analysis only. No implementation, no candidate, no builder change, no detector or gate edit, no
host replay run, no value protocol, no TestSession, no submission, no Arena action. Read-only
against `data/`; no sealed ranges, official holdout, or the 11 sealed D164 games. No CI anywhere.
Phase 3 of the consolidated hardening plan does not start on either route until this verdict is
in and the owner rules.

## Deliverables

One handoff to `local_claude_1` on canonical `agent/claude_1`: the verdict, the exact
decomposition, the causal mechanism, the candidate repairs with costs, the standing-rule
interaction, and the honest Route A/B cost comparison.
