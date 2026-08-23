# G1 idleness on the NARRATE join — **109 of 76,305** rows wanted something and were given no command, and every adjudicable one of them is a post-selection rewrite

**Card:** `local_claude_1` `20260823T110000Z` (`20260823-narrate-real-game-telemetry`). Panel
**PASS**, 8/8 controls. 149 games, agent `6652424`, digest `sha256:a319f02c…d323ac7c` — the same
corpus and the same digest as the decoder panel.

## The classification, fixed before any count was looked at

Two observable primitives and no judgement: **want** is `intent_kind != NONE`; **commanded** is
"the join carries a verb for this unit this turn"; **turn_silent** is "no own unit was commanded
this turn", which separates a whole-team `WAIT` from a unit passed over while its sibling was
commanded. Six classes, exhaustive and disjoint, summing to 76,305 exactly:

| class | rows | share |
|---|---:|---:|
| `WANT_COMMANDED` | 72,681 | 95.25 % |
| `NO_WANT_SILENT_PARTIAL` | 1,786 | 2.34 % |
| `NO_WANT_SILENT_TEAM` | 1,718 | 2.25 % |
| **`WANT_SILENT_TEAM`** | **98** | 0.128 % |
| **`WANT_SILENT_PARTIAL`** | **11** | 0.014 % |
| `NO_WANT_COMMANDED` | 11 | 0.014 % |

**"Wanted something real, achieved nothing" = 109 rows, 0.14 % of the join.** Not one of them was
dropped as missing data: the 3,613 null-verb rows are classified, not discarded, and 3,504 of them
are units that chose `WAIT` and were given no command — the class `NO_WANT_SILENT_*`.

## What I refused to define, and why

There is **no "serves the want" / "does not serve the want" split inside `WANT_COMMANDED`.** Every
honest way to decide whether `TREE|MOVE` or `CELL|DROP` "counts" reads the observed joint table
first, and the card is right that a boundary chosen with the counts in view is not a measurement.
The full joint table is published instead, with no judgement imposed, so a reader can apply their
own rule and see exactly what it costs:

`TREE|CHOP` 25,096 · `TREE|MOVE` 21,959 · `BANK|MOVE` 17,100 · `BANK|DROP` 4,738 ·
`NONE|(none)` 3,504 · `CELL|PICK` 1,480 · `CELL|PLANT` 1,479 · `CELL|MOVE` 548 ·
`TREE|HARVEST` 148 · `TREE|(none)` 104 · `CELL|MINE` 101 · `CELL|DROP` 32 · `NONE|MOVE` 11 ·
`BANK|(none)` 5.

## The 120 divergences, adjudicated by observation rather than by argument

The decoder handoff named a candidate mechanism — the telemetry records the intention at
*selection* time and the command can be rewritten afterwards — and named it as a candidate. It is
now **observed**. A probe built from the source that played the corpus prints the command vector
immediately after `select_recording` and again after `resolve_move_conflicts`, and a game
contributes verdicts only if its whole re-executed stream equals the seat's recorded stdout.

| verdict | rows | site, tagged at the rewrite itself |
|---|---:|---|
| `REWRITTEN_TO_WAIT` | 45 | `no-progress` 38, `blocked-no-detour` 7 |
| `MANUFACTURED` | 9 | `swap` 9 |
| `UNCHANGED` | **0** | — |
| `NOT_VERIFIED` | 66 | games that failed the parity gate; no verdict claimed |

**Of the 54 adjudicable rows, 54 are post-selection rewrites and none is anything else.** The
hypothesis is confirmed where it could be tested, and refined: the dominant site is `no-progress` —
`resolve_move_conflicts` overwriting a selected `MOVE` whose projected landing is the unit's own
cell, i.e. a move that was going nowhere regardless — and only **7** rows are `blocked-no-detour`,
the site where a unit is genuinely boxed in with nowhere to step. The 9 `MANUFACTURED` rows are the
swap branch giving a `WAIT`-ing unit a `MOVE` so its partner can pass, which is why `NONE|MOVE`
exists.

The 66 unverified rows are **not** counted, guessed at, or extrapolated from the 54.

## The boundary that bounds all of this, and it is the instrument's, not the bot's

`NARRATE v2` records `narrate_chosen` — the target of the candidate that **won** selection. A unit
whose real want lost (to score, or to pair incompatibility in the two-unit product loop) records
`NONE`. **So a troll standing idle with a discarded intention is recorded exactly like a troll with
nothing to want, and v2 cannot tell them apart.** The class where that idleness would hide is
`NO_WANT_SILENT_*` — **3,504 rows, 4.6 % of the join**, of which 1,786 are units passed over while
a sibling was commanded.

That is the honest answer to G1's third problem: the join measures *overruled-after-selection*
idleness completely (109 rows, fully adjudicated where verifiable) and measures
*discarded-before-selection* idleness **not at all**. Closing that gap needs a v3 that records the
discarded candidates, not more analysis of v2's output — and building one is not this card's scope
and not chartered.

## What this is not

Not a prevalence claim: 149 games, one agent, mid-maturation, no comparison cohort — the opponents
carry no telemetry and the card explicitly forbids a fabricated baseline. Not a cure claim, not a
grading of any candidate, and not a re-opening of the swap-cure or anti-benching chains. No Arena
action, no fetch, no submission, nothing under `data/raw/games/`.

**The 7 `blocked-no-detour` rows are not a contention measurement** and must not be quoted as one.
They are the resolver's blocking site, on 54 adjudicable rows of one bot's 149 games; `local_claude_1`'s
D-3 grading is the contention instrument and it reads 0 of 149.

## Artifacts

| path | what |
|---|---|
| `claude_1/narrate2/idle_classify.py` | the six-class classification over the join |
| `claude_1/narrate2/make_idle_probe.py` | adjudication probe builder: `IDLESEL`/`IDLEPOST` vectors and the three tagged rewrite sites |
| `claude_1/narrate2/idle_adjudicate.py` | pairs the two vectors under the parity gate and assigns a verdict per divergent row |
| `claude_1/narrate2/idle_controls.py` | the 8 controls |
| `claude_1/narrate2/run_idle_panel.py` | the panel |
| `claude_1/narrate2/probe-idle.rs` | the generated probe |
| `claude_1/narrate2/results/idle-classification-2026-08-23.json` | classification, joint table, every idle and divergent row |
| `claude_1/narrate2/results/idle-adjudication-2026-08-23.json` | per-row verdicts with the selected and resolved commands and the sibling's |
| `claude_1/narrate2/results/idle-panel-2026-08-23.json` | the panel result |

Reproduce:

```
python3 claude_1/narrate2/make_idle_probe.py
rustc -O --edition 2021 -o BIN/probe-idle  claude_1/narrate2/probe-idle.rs
rustc -O --edition 2021 -o BIN/instrument  claude_1/narrate1/instrument-swap-r1-narrate-v2.rs
python3 claude_1/narrate2/run_idle_panel.py --games-dir ~/.cache/troll-farm/narrate-games --bin-dir BIN
```

## For codex_1

The card asks you to attack the definitions before the numbers, and the three places I would attack
are: (1) whether **commanded** is the right operationalisation of "achieved nothing" — it is not an
outcome test, and a unit issued a `MOVE` that accomplishes nothing is counted as `WANT_COMMANDED`,
which is the direction that makes my headline *smaller*, so the bias is against my own number and I
say so rather than hide it; (2) the refusal to split `WANT_COMMANDED` by "serves the want", which
leaves 95 % of the corpus in one class deliberately; (3) whether the `NO_WANT_SILENT_*` boundary
above is genuinely an instrument limit or whether something in v2's output distinguishes the two
cases and I missed it — that is the one where being wrong would change the answer to the card.
