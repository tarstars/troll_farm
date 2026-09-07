# Persistent-horizon screen: deployment failure on the first candidate request

Status: the frozen screen of `LOOKAHEAD-FIELD-PROTOCOL-2026-09-05.md` is **stopped**, not passed
and not failed on gameplay. Two of its twelve requests were issued; ten were never attempted. The
twelve confirmation requests were never opened. No publication followed, and no canonical source
file (`bot.rs`/`submission.rs`) was touched at any point.

## Standing platform result (unchanged by this screen)

V439 remains the live published artifact: submission 41245746 / agent 6704418, mature rank 28 in
Legend, 95W/0D/65L over 160 games, mean own score 207.4125 versus opponent 200.0625. The
`EVALUATION.md` goal of an observed top-seven mature rank is **not met**. Nothing below changes
that reading.

## What the two requests produced (evidence)

Provenance for both runs is archived under `/data/separate_troll_farm-working/planning/2026-09-05`;
the frozen screen manifest is `persistent-horizon-field/screen/manifest.json`.

| | Baseline (V439) | Candidate (persistent horizon) |
|---|---|---|
| Game id | 901553263 | 901553280 |
| Seed | 260905990701 | 260905990701 (same) |
| Seat | 0 | 0 |
| Opponent | putibuzu, agent 6479779 | agent 6479779 |
| Scores (own/opp) | 132 / 189 | -2 / 22 |
| Official ranks (own/opp) | 1 / 0 | 1 / 0 |
| Turns | 232 | 3 total frames, frame 0 agent -1 |
| Wood | 33 / 45 | — |
| Requests / losses / failures | 1 / 1 loss / 0 | 1 / 1 official loss / 1 compilation failure |
| Played games | 1 | 0 |

Game identifiers are **not** seeds; the pairing above is established by the echoed seed
260905990701, seat 0 and opponent identity 6479779, not by the adjacent game numbers.

The candidate request hit a compilation timeout **before any gameplay**: the platform diagnostic
ends `Compilation took too long and has been interrupted...`. Its official rank-1 loss and its
-2/22 score are therefore artifacts of that failure, not a competitive observation. Per the
protocol and `EVALUATION.md`, the failed run stays in the denominator: the screen's candidate
record is 1 request, 0 played games, 1 deployment failure. That is already a zero-failure-gate
violation, so the screen cannot advance regardless of the ten unattempted requests.

The collector exited 75 and performed no retry, as required. The candidate raw response and replay
were saved even though no candidate row was written to the screen manifest — the manifest is
incomplete relative to the archived artifacts, and the artifacts are the authority for this report.

## Local evidence, restated for scope

The candidate is SHA `9f01587b4f71b8e5bbbe15e86a69aac274fe1ac476725951e6bf67db304b1c5d`, 92,430
UTF-16 units. On the eight consumed development maps it scored 176/5/11 versus V439's 173/5/14
(+3 match points), mean own 239.505208 vs 238.458333, mean opponent 110.161458 vs 110.5625, margin
129.34375 vs 127.895833. Existing packaged/readable audit: 43,263 turns identical; 320 startup
checks, 0 errors, worst 3.772 ms; 496 tests. All of this is **local development data only**. It was
sufficient to open the screen and remains insufficient for any strength claim.

## Compiler-diagnostic experiment (complete, and what it does not show)

Local build of the exact candidate source with `rustc --edition=2021 -O`, no `-Awarnings`:
return 0, 9.196543591 s, 4,499,093 stderr bytes, 108 warnings.

The original source preceded by
`#![allow(non_camel_case_types, non_snake_case, non_upper_case_globals, dead_code, unused_imports,
unused_variables, unused_mut)]`, a newline, and one extra trailing newline: return 0,
8.772011635 s, 0 stderr bytes, 0 warnings.
Quiet-variant SHA `bb78d5946995b5f141b825db3e54ef7911d1761c28b5e2f3a8b16d58cf2b622a`.

Evidence: the candidate emits a very large volume of local diagnostics, and a packaging-only prefix
removes all of it; the diagnostic also added a trailing newline. The production export repair
preserves the original suffix exactly and therefore has a different hash.

Inference, explicitly not established: that diagnostics caused the remote timeout. The platform's
compiler flags and time limit are **not verified**. These local flags must not be described as the
exact platform default, and no known timing margin may be claimed from the 9.196 s / 8.772 s pair.
At this diagnostic stage, no repaired source had been checked remotely; the subsequent result
is recorded below and does not erase the original failure.

## Next primary step (local, no gameplay change)

Apply the same lint prefix, preserving the frozen source suffix byte-for-byte, then re-run the
full local gate set before any further platform contact:

1. Export the actual artifacts and run the tests **without** `-Awarnings`, so residual diagnostics
   are visible rather than suppressed by the harness.
2. Guard the suffix: assert that the bytes after the prefix are equal to the frozen original source
   and that the frozen original hash `9f01587b…c5d` still reproduces from them.
3. Re-run the exact execution audit (packaged/readable command-stream identity) and the interactive
   startup checks.

No gameplay edits are part of this step. A prefix-only change is a packaging repair, not a new
policy, and the repaired artifact is still the same controller.

## Only after those gates pass

A new, explicitly frozen **one-request** deployment smoke test using the repaired hash, on the
already-consumed seed 260905990701. Its purpose is diagnostic — does the artifact compile and play
on the platform — and it must be labelled as such. It is **not** fresh competitive evidence: the
seed is consumed, the opponent is known, and n=1.

Controls that apply:

- Preserve the original failure record; do not resume, retry or reissue the old POST.
- The original screen is closed. Its ten unattempted seeds were never consumed, so reusing them is
  not forbidden, but any reuse must be disclosed as coming from a closed screen. A fresh plan with
  new seeds is simpler and is the recommended route.
- Reusing opponent identity 6479779 is legitimate. Nothing here requires a different opponent, and
  no such requirement should be invented.
- Any later competitive plan needs freshly frozen, unopened seeds and the unchanged advance gates
  of `LOOKAHEAD-FIELD-PROTOCOL-2026-09-05.md`: at least one additional match point, no lost
  baseline win against the target identities, no majority of worse-margin blocks, zero deployment
  or protocol failures, with seed echo, seat, opponent identity and initial-input hash verified per
  pair and official ranks used for outcomes.

## Bottom line

Zero competitive evidence was gathered about the persistent-horizon planner. One baseline game was
played and lost (132/189); the candidate never ran. The failure is a deployment/packaging failure
with an undetermined underlying cause, and the standing platform position is still V439 at
rank 28.

## Completed packaging repair and second deployment failure

The actual repaired compact source is SHA
`3eb6a70e55cb82292e87e836887018f849c7d8a44eee8b9a8fa1822ce915687b`, 92,553 UTF-16 units.
It adds only the lint attribute and preserves every frozen original byte after the prefix;
unlike the preliminary diagnostic it adds no trailing newline. Readable SHA:
`b0c689780b961c50a24501e999a9f8fe2b717307b710551eb68d4978395b8775`.

Primary verification of the Claude-assisted repair:

- Full suite: 498 passed in 203.41 seconds. Actual compact/readable export tests no longer use
  command-line warning suppression.
- Sequential `rustc --edition=2021 -O` builds: readable 9.042 s, compact 10.815 s, both successful,
  zero stderr. Local toolchain: rustc 1.97.1, LLVM 22.1.6; platform toolchain remains unverified.
- Old compact versus repaired compact: 160 games / 43,263 turns, zero command differences.
- Repaired readable versus repaired compact: same 160 streams, zero command differences.
- 320 open-stdin startup launches: all correct, mean 1.385 ms, maximum 1.943 ms, zero over 50 ms.

After all gates passed, the separately frozen one-request diagnostic ran from 10:35:42 to
10:36:15 UTC. Game **901554831**, same consumed seed **260905990701**, seat 0, opponent
putibuzu / agent 6479779: official ranks 1/0, scores -2/22, **compilation timeout before gameplay**.
Frame zero contains only `Compilation took too long and has been interrupted...`, without
the earlier warning flood. The collector exited 75 without retry. This diagnostic is closed.

Denominators: this new source has **one requested game, one official loss, one deployment
failure, zero played games**. Across the original screen and the separately labelled repair
diagnostic, two candidate requests both failed compilation; neither produced gameplay evidence.
The baseline request remains one normal 132/189 loss. Original screen requests not attempted
remain ten; its twelve confirmation requests remain unopened.

This establishes that warning suppression **is not sufficient** to make this candidate deploy.
It does not identify the remaining bottleneck or establish that warning emission had no cost.
No additional platform games or publication are scheduled. The next bounded offline experiment
will measure compiler cost of targeted no-inline attributes, retaining failures and exact source
provenance; any faster build still needs command-equivalence and runtime checks before use.

Evidence: `packaging-repair-validation.{json,log}`, `packaging-repair-*-aa.json`,
`packaging-repair-startup.json`, and `packaging-repair-smoke/{plan.json,run/manifest.json}` in the
planning evidence root. The smoke's raw response and replay are saved despite an empty
completed-row list. Live V439 was read again immediately before the diagnostic: rank 28/177,
rating 23.43, agent 6704418; canonical files and neighboring project remain unchanged.
