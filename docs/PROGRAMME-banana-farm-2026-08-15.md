# PROGRAMME — banana farm, reached through an oscillation deep-dive

- Owner-decided 2026-08-15 (conversation with `local_claude_1`); this file is the single
  holistic record the owner asked for: *"we have a lot of pieces, but they don't form a
  holistic picture."*
- Plain-language rule applies: every code name is explained at first use.
- Status of each stage is kept HERE. Task records hold the detail; this file holds the shape.

## What we are doing, in one paragraph

We want to run the banana-farm experiment. Before building it, we make the ground solid:
take the clean readable bot as the base, deeply understand its oscillations (trolls walking
back and forth doing nothing), and either fix them or have the owner rule them harmless.
Then we review the farm design once more, build it, and measure it on the ladder. Depth over
speed — the owner has ruled: **no cheap ways**; recent stalls came from shallow
investigation, not lack of activity.

## The base bot

`cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs`, SHA-256
`98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29` — the current ladder
resident ("readable no-orchard"): human-readable formatting, orchard code removed, six
mature ladder runs, median ≈ 23.6. All work in this programme bases on this file. The old
275 KB compact "sacred" file stays frozen and is NOT the base; the CBF design spec of
2026-08-07 must be re-based onto the readable file (its line numbers and grafting plan
refer to the old one).

## The two bot specifications (owner decision 2026-08-15)

Both share the same pipeline: **gather resources → train the second troll → select lemon or
plum → deny (chop) the selected species near the enemy → banana farm → abort to aggressive
all-out chopping if the enemy collects more from our farm than we do.**

- **Spec A — unconditional.** Farming follows denial as the normal course of the game.
  Closest to D89a, the 2026-07-21 farm that averaged +79 margin but lost catastrophically
  in its worst games.
- **Spec B — conditional ("if third troll").** Farming starts only if the enemy fields a
  third troll — i.e. only in games where we are already out-scaled. This is the written
  CBF spec of 2026-08-07 (`docs/superpowers/specs/2026-08-07-conditional-banana-farm-design.md`),
  built to cut off D89a's catastrophic tail.

Which is better is a measured question (stage 6), not a design argument. Both must respect
the standing owner rule: **no banana action before our second troll is trained** (threshold
zero, no exemption).

## The stages, in order, with gates

| # | Stage | Owner gate | Task record |
|---|---|---|---|
| 1 | Oscillation deep-dive: Decision Packet tool, moves viewer, per-situation adjudication of ideal behaviour | Owner rules per situation; final ruling "fixed" OR "unavoidable and harmless" is the owner's alone | `coordination/tasks/20260815-oscillation-deep-dive.md` |
| 2 | Owner goal-hierarchy doctrine (one page: what trolls should value, in priority order) | Owner corrects and freezes the draft | inside stage-1 task |
| 3 | Oscillation outcome: implement the fix, or record the owner's "harmless" ruling | Owner | inside stage-1 task |
| 4 | Write both farm specifications A and B against the readable base | Owner reviews both before implementation | `coordination/tasks/20260815-banana-farm-two-specs.md` |
| 5 | Implement (staged: inert state machine + byte-identity proof, then farm, then abort; both specs share code) | — (standing rule: a test is not finished until observed failing) | opened when stage 4 passes |
| 6 | Measure on the ladder: interleaved A/B campaign, ~8 mature runs per night, owner go-ahead per night | Owner authorizes each night | opened when stage 5 passes |

## Measurement arithmetic, agreed in advance (σ ruling of 2026-08-13)

Ladder noise σ = 1.501 per mature run. One night = 8 runs = 4 per arm interleaved
A/B/A/B → uncertainty on the difference ≈ 1.06 points → **one night cleanly resolves
differences of ~2 points or more**. If arms land closer than that, one further night
(8 per arm total → SE ≈ 0.75) usually settles it. Runs are serialized through the single
arena controller (`local_claude_1`); nightly cycling is automated; a mature run takes ~2 h.
Behavioural gates deliver a *correctly built* bot, never a *good* one — value comes only
from stage 6.

## Roles (owner decision 2026-08-15)

- **claude_1** — writes the code (Decision Packet, viewer, bot stages); it built the
  frozen oscillation situation library and holds the Decision Packet contract.
- **codex_1** — tough logical reviews at every gate.
- **local_claude_1** — integrator, record-keeper, sole arena controller.
- **owner** — goal doctrine, per-situation ideal-behaviour rulings, the
  harmless/fix ruling, spec review, nightly measurement go-aheads.

## Standing facts this programme must not contradict

- `docs/CONSTRAINTS.md` "oscillation is CLOSED permanently" is a closure about **score
  value** (+0.045 for a perfect fix). This programme reopens the work on the owner's
  2026-08-09 grounds — control, technical debt, test coverage, understanding — restated
  and re-authorized 2026-08-15. No agent may refuse stage 1 by citing that closure.
- The unresolved mystery stays on the books: games with oscillation run ~13.6 points below
  par after map control, while the fix is worth +0.045 — so those games likely hide a
  different, undiagnosed defect. Stage 1's per-situation analysis is expected to expose it.
- Banana R2 history (six implementation-invalid rounds) binds stage 5: implementation
  validity gates and observed-failing tests come before any value panel.
