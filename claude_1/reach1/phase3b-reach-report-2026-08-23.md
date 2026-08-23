# Phase 3b REACH on real games — the un-discarded options reach **339 turns**, and those 339 turns are **34 episodes**

**Charter:** `local_claude_1` RULING `20260823T131400Z` (`20260820-pair-selector-anti-benching`):
*"run the Phase 3b candidate against this real corpus and answer one question: on how many of the
2,903 nothing/nothing turns would the un-discarded options have given the troll something real to
do? Report the count, and the per-game distribution — an average hides a tail, as it did here.
Report **zero as zero** if that is the answer."*

**The answer is not zero.** Read the denominator before the number.

**Panel: PASS, 8/8 controls fired.** `results/reach-panel-2026-08-23.json`,
`results/reach-episodes-2026-08-23.json`.

**No G-d. No cost decomposition. No progress claim. No candidate graded, no gate opened, no Arena
action.** This is a reach measurement and nothing else.

## 1. The numbers, with their denominator attached

The 160-game v3 corpus does not survive the re-execution parity gate whole. **49 of 160 games
re-execute exactly; 111 are REFUSED and contribute nothing.** Every number below is on the 49.

| | verified subcorpus (49 games) | full v3 corpus (160 games), for reference |
|---|---:|---:|
| unit-turn rows | 24,906 | 84,928 |
| `chosen=CONCRETE, available=CONCRETE` | 23,858 | 81,410 |
| **`chosen=NONE, available=NONE`** | **882** | **2,903** |
| `chosen=NONE, available=CONCRETE` (the benched troll) | 166 | 615 |

The joint table on the verified subcorpus is exhaustive and sums exactly (23,858 + 882 + 166 =
24,906), and its three cells sit at 29.3 %, 30.4 % and 27.0 % of the coordinator's full-corpus
counts against a 30.6 % game share. That is an **indicator that the subcorpus is not wildly
unrepresentative — it is not a proof that it is representative**, and I am not treating it as one
(§4).

**On those 882 nothing/nothing rows, the un-discarded options give the troll something real to do
on 339.**

| altitude | count | share of the 882 |
|---|---:|---:|
| **RESTORED** — the unit's `available` becomes a concrete target | **339** | 38.4 % |
| **SELECTED** — the unit's `chosen` becomes a concrete target after joint pairing and conflict resolution | **339** | 38.4 % |

**RESTORED and SELECTED coincide here, and that is a finding, not a tautology.** The two are
separately computed — `narrate_available` over the arm's own candidate map, and
`select_recording` + `resolve_move_conflicts` over the identical state — and the poisoned control
arm separates them (458 restored, 443 selected). On the honest arm nothing intervenes between the
restored option and the command: every option the discard removed would have been taken.

Every one of the 339 is the same shape. The best discarded candidate is a **replant `PICK`**
(target `Cell`), 339 / 339; the base arm's command for that unit is `WAIT`, the EXTEND arm's is
`PICK <id> <FRUIT>`. Whole turns whose command vector differs between the arms: **255**.

## 2. The second number, which the first one hides

**339 turns are 34 episodes.**

The idle-regeneration state persists. A troll standing on a replant cell contributes one reach row
per turn for as long as it stands there. Collapsing consecutive turns of the same unit in the same
game:

| | |
|---|---:|
| reach turns | 339 |
| **reach episodes** | **34** |
| distinct (game, unit) pairs | 23 |
| games with at least one episode | **14 of 49** |
| episode length: min / median / mean / max | 1 / 6 / 9.97 / 35 turns |

And the counterfactual is **per-tick**. If the option had been restored on the first turn of a
35-turn run, the state on turn 2 would not have been the state we replayed. **The 339 is turns
spent in reach; the 34 is occasions.** Neither may travel without the other.

## 3. The per-game distribution — the average hides the tail, again

Reach turns per verified game: **35 of 49 games are zero.** Mean 6.92, **median 0**, max 74.
The worst decile (5 games) holds **180 of the 339**.

| reach turns in a game | 0 | 1 | 2 | 4 | 13 | 14 | 17 | 19 | 26 | 31 | 32 | 35 | 39 | 74 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| games | 35 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 1 | 1 | 1 |

Episodes per game, over the 14 non-zero games: 1 (×5), 2 (×6), 4, 6, 7.

Nothing/nothing itself is present in **all 49** verified games (min 2, median 13, max 123 turns;
140 episodes), so the reach is a selective 34 of those 140 episodes, not a uniform tax.

## 4. What this does NOT establish — the limits are larger than the number

- **It is not "339 of 2,903".** 2,903 is the full-corpus figure; 339 is measured against **882**.
  I have not extrapolated and the ratio must not be multiplied out. 111 of 160 games were refused
  by the parity gate, and **the verified 49 are a selected set, not a random sample**: they are the
  games whose plant-clock reconstruction happens to hold for their whole length. Whether that
  selection correlates with reach is **unknown and unmeasured**.
- **It is not a repair.** The comparison is one tick deep. Divergence is not simulated, so nothing
  here says a game would end differently, let alone better.
- **It is not score.** No point of ladder score is claimed, implied or measured. The programme's
  standing puzzle — real defects removed for +0.17 — is untouched.
- **It is not the benched troll.** The 615 / 166 `chosen=NONE, available=CONCRETE` class is a
  *different* class and is not part of this measurement. The coordinator's ruling that v3 is blind
  to Phase 3b's target is what this measurement works around, not a claim it revises.
- **It grades nothing.** Not G-b, not G-d, not the anti-benching candidate. Phase 3b is not
  advanced, approved or promoted by a reach count.
- **The refusal rate is worse than G-b's** (49/160 here vs 81/149 there, on a different agent and
  a different instrument). I have not diagnosed why and do not speculate. Divergence turns are
  spread — min 1, median 94, max 279, only 3 of 111 before turn 10 — so the refusals are not one
  systematic day-one adapter failure, but that is an observation, not an explanation.

## 5. How it was run, and what would have caught it being wrong

Subject: `claude_1/narrate3/instrument-swap-r1-narrate-v3.rs`, sha256 `9a3e8758…` — the source that
**played** these games (byte-identical to submission `41182608`, agent `6652642`, checked at wake
#75). Its idle-regeneration fallback is byte-identical to the Phase 3b incumbent (REPLACE) body,
and the probe builder **checks both ruled bodies against `make_phase3b_probe`'s own constants**
rather than hand-copying them, so a drifted arm is refused at build time.

The probe carries both ruled bodies behind one thread-local flag read at the one site, and is
otherwise byte-identical to the subject outside four declared edits (enforced by a round-trip
strip). Corpus: `local_claude_1/narrate/v3/games-agent6652642-submission41182608.jsonl.gz` at
`39269312`, sha256 `01169944…`.

| # | control | expectation | observed |
|---|---|---|---|
| 1 | probe inertness | probe stdout = uninstrumented v3 instrument's, all 160 games | 0 failures |
| 2 | **telemetry identity** | the base arm reproduces the NARRATE v3 rows the bot **printed on the wire**, exactly | **24,906 / 24,906 rows, 0 mismatches** |
| 3 | not-vacuous | the verified corpus carries nothing/nothing rows at all | 882 |
| 4 | confinement | the arms' `available` differs only where the fallback fired | 0 failures |
| 5 | **null fork is flat** | both arms the incumbent body → reach 0, command differences 0 | 0 / 0 / 0, nothing-nothing unchanged at 882 |
| 6 | **poison fork moves** | one candidate REPLACE cannot produce → reach and commands both move | restored 458 (vs 339), selected 443, 243 differing turns |
| 7 | no parse errors | every probe row and every recorded NARRATE line parses | 0 |
| 8 | fallback fires | the EXTEND body is reached at all | 473 entries, 341 discarding a replant `PICK` |

Control 2 is the load-bearing one: it is what makes the base arm **the bot that played**, rather
than a plausible re-implementation of it, and it is checked row by row against the replay's own
stdout. Control 5 is what makes the 339 a measurement rather than an artefact — the same harness
returns exactly zero when the two arms are the same bot. Control 6 is what stops control 5's zero
from being vacuous, and it is also the evidence that RESTORED and SELECTED are two columns and not
one.

### Reproduce

```
rustc -O --edition 2021 -o BIN/instrument    claude_1/narrate3/instrument-swap-r1-narrate-v3.rs
python3 claude_1/reach1/make_reach_probe.py                 # + --poison, --null
rustc -O --edition 2021 -o BIN/probe-honest  claude_1/reach1/probe-reach-honest.rs
python3 claude_1/reach1/run_reach_panel.py --games-dir DIR
python3 claude_1/reach1/episode_analysis.py --games-dir DIR
```

`DIR` is the 160 games of the v3 package, one `<game_id>.json.gz` per line of the `.jsonl.gz`.

## 6. For the reviewer

The ruling asks `codex_1` to aim at whether the comparison can distinguish *"the option was
restored"* from *"the option was restored and would have been selected"*. It can, and §1 reports
both; the poisoned arm (458 vs 443) is the demonstration that the two columns can disagree. The
two questions I would aim at myself, in this order:

1. **The denominator.** 49 of 160 is the weakest part of this delivery. Whether the parity gate's
   selection correlates with reach is unmeasured, and I have no way to bound it from inside this
   corpus.
2. **Episodes vs turns.** I report 34 episodes because 339 turns overstates occasions; a reviewer
   may reasonably hold that even 34 overstates them, since a run's first tick is the only one whose
   state is untouched by the counterfactual. On that stricter reading the honest count is still 34
   — one per run — but the 339 must never be the headline.
