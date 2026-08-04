# Coverage analysis of the round-36 candidate (claude_1, 2026-08-04)

Owner-suggested addition to the simplification programme. Tooling:
`run_coverage_panel.py` (committed, re-runnable); evidence:
`r36-coverage-panel-2026-08-04.json`. Method: build the candidate with
`-C instrument-coverage`, replay all 25 games of the frozen open packet, verify the
instrumented build still reproduces every baseline output (**25/25 identical**, so the
measurement is of the same program), merge profiles, export LLVM region data.

## What coverage can and cannot do here

**It cannot license deletions in this programme.** Uncovered ≠ unreachable. Deleting code
that merely never ran in a sample is a behavior change — precisely what the no-orchard
ablation was, and that one cost 2.03 rating points. The behavior-exact rounds must keep
resting on static invariants.

**It can do two things the static scan cannot**: measure how strong the safety gate actually
is, and find further orchard-shaped ablation candidates.

## Result 1 — gate strength

| Metric | Value |
|---|---:|
| Region coverage over the 25-game packet | **79.13 %** (3,350 regions, 699 cold) |
| Function coverage | **80.0 %** (260 units, 52 never executed) |

So roughly a fifth of the program has **no live-replay evidence at all**. For that fifth,
"25 games / 7,234 identical command lines" is not the protection — the ten semantic fixtures
and the per-round static invariant are. This is worth stating plainly in future handoffs;
the parity gate is strong but not total.

## Result 2 — self-audit of rounds 29–36 (the reason to run this)

Every site edited in this session lies in code the gate genuinely exercises:

| Round | Function edited | Coverage | Entries |
|---|---|---:|---:|
| 29, 30 | `opening_options` | 100 % | 25 |
| 31 | `main_candidates` | 94.1 % | 11,679 |
| 32 | `endgame_candidates` | 96.3 % | 234,493 |
| 33 | `worker_can_use_alternate` | 100 % | 112 |
| 35 | `early_candidates` | 88.3 % | 523 |

No round deleted code inside a cold region, so no round's live-replay evidence is vacuous.
Round 33 is the one worth noting: it edits orchard-side code, which only the single
orchard-activating game reaches — the helper is fully covered (112 entries via
`can_continue_seed`), but that coverage comes from a narrow part of the sample.

## Result 3 — cold code: ablation candidates in the orchard's shape

Named functions with **zero** executed regions across 25 real games:
`training_affordable`, `strongest_affordable`, `planned_egress`, `best_alternate_door`,
`carries_committed_fruit`, `forced_move`, `fallback_second_troll`.

Coldest blocks by absolute cold regions:

| Function | Regions | Cold | Coverage |
|---|---:|---:|---:|
| `force_unique_door_clear` | 341 | 337 | **1.2 %** |
| `protect_mother` | 97 | 53 | 45.4 % |
| `planned_egress` | 33 | 33 | 0 % |
| `next_cell` | 59 | 28 | 52.5 % |
| `training_affordable` | 21 | 21 | 0 % |
| `best_alternate_door` | 19 | 19 | 0 % |
| `enforce_training_deadline` | 24 | 15 | 37.5 % |
| `strongest_affordable` | 15 | 15 | 0 % |

Two coherent *features*, not scattered lines:

1. **Door-unblocking** (`force_unique_door_clear`, ~4.7 KB of source, plus `planned_egress`
   and `forced_move`): the routine is entered every turn but its body essentially never
   fires — 1.2 % region coverage. Round 7 made it unconditional by deleting its fixed-on
   switch; this says the situation it handles almost never arises in these games.
2. **Training-deadline fallback** (`enforce_training_deadline` → `training_affordable`,
   `strongest_affordable`, `fallback_second_troll`): the guard runs 35,529 times and the
   fallback body never fires.

## Caveats that bound all of the above

- The 25 games are the frozen liveness-counterexample packet — selected for period-2
  oscillation, **not** sampled uniformly from the ladder. Cold here may mean "cold in this
  sample". A coverage run over the integrator's 516-task development panel would be the
  honest generalization, and needs integrator-side map generation.
- Coverage counts executed regions, not correctness: a hot region is not a verified region.

## Recommended use

Do **not** convert these into simplification rounds. The right instrument is the one already
proven on the orchard: for a cold feature, build an activation-disabled reference, measure the
source cost, and — only if the owner wants the strength answer — run a paired local panel
before any arena consideration. `force_unique_door_clear` is the strongest such candidate by
size (≈4.7 KB, 1.2 % covered); the training-deadline fallback is the strongest by coherence.
