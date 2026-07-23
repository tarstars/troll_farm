# D164a current-field macro-transition audit — result

Date: 2026-07-23  
Verdict: **freeze a bounded, per-worker producer → suppressor → producer return as the next
resident-anchored causal hypothesis.**

## Fresh platform snapshot

The authorized read-only collector completed snapshot `20260723T074715Z-d164a` with 393 unique
finished games, 21 battle lists, 415 public requests, and zero failures. All bulk bodies and parsed
products are on the external-backed `data/external/arena-corpus` root. No game, TestSession,
submission, resident, or reserved local map was changed.

The leaderboard still identifies exact resident agent `6561795` as `tass`, now rank **43** with
score **21.97**. D159 observed rank 40 / 22.26 earlier the same day, so this is a materially newer
ladder read, not a policy change.

Parsing reconstructs all 393 games: 203 contain the resident, 190 contain a selected top-20 source,
and the open products provide 192 resident games plus exactly ten actor appearances for each of
20 current top agents. There are zero replay, identity, score-shape, turn, state-diff, duplicate-ID,
or duplicate-trajectory failures. Eleven confirmation games remain sealed and were not
enumerated. One replay contains an exact same-cell, same-kind simultaneous PLANT by both players;
the analyzer classifies that generation as `joint`, matching the known referee merge rather than
pretending either player owns it.

## Multi-level result

### Field behavior

Nine motifs pass the frozen breadth and resident-gap gate. Eight are already represented or
causally closed by project history. The sole new coordination primitive is a **bidirectional
per-worker role handoff**: the same worker performs own production, temporarily suppresses an
opponent-created crop, and later returns to own production.

| Motif | Top 1–5 | Top-agent support | Ranks 6–20 | Resident | History decision |
|---|---:|---:|---:|---:|---|
| Producer → suppressor → producer | **72.0%** | **5/5** | **27.3%** | **10.9%** | **open as stateful return** |
| Reap → bank cycle | 98.0% | 5/5 | 72.7% | 9.9% | closed by D89/D163 |
| Own-crop reaping | 98.0% | 5/5 | 76.7% | 9.9% | closed standalone |
| Opponent-crop reaping | 58.0% | 5/5 | 24.0% | 1.6% | exact residual rejected |
| Same-worker renewal | 96.0% | 5/5 | 74.7% | 2.6% | fixed cycle/pulse closed |
| Coordinated later TRAIN | 86.0% | 5/5 | 40.7% | 0.0% | fixed reserve/bridge closed |
| Strict producer/suppressor split | 78.0% | 5/5 | 64.7% | 9.4% | static split closed |
| Production/suppression overlap | 70.0% | 5/5 | 59.3% | 8.9% | wholesale scheduler closed |
| Foundation production + later suppression | 62.0% | 5/5 | 27.3% | 0.0% | complete scaler closed |

The one-way producer-to-suppressor handoff fails: 28.0% top-five prevalence, support from only two
top agents, and only a 6.6-point prevalence gap over the resident. Pre-scale renewal plus joint
funding also fails reference breadth at 15.3% in ranks 6–20. Neither can rescue or replace the
selected motif.

### Timing and state

The 36 top-five handoff games span all five agents and both seats. The first suppression switch has
median turn **179** and the return has median turn **217.5**. Once suppression begins, return is
usually short: median **15.5 turns**. Eleven switches occur at workforce two, ten at workforce
three, fourteen at workforce four, and one at workforce five. The primitive is therefore neither
a first-move recipe nor a synonym for adding worker three.

Ranks 6–20 independently show 41 handoff games across eleven agents and both seats, with median
switch/return turns 159/207 and median suppression duration 23. The resident exhibits 21 cycles,
all at workforce two, but much later production entry and only 10.9% prevalence.

At turns 75–150, top-five handoff games already carry less opponent live-crop health and roughly
0.6–1.0 fewer opponent crops than non-handoff top-five games. They also bank more fruit by turns
75–125. These are descriptive state associations, not causal value estimates. Likewise, handoff
games average +98.08 margin in the top five while the resident's rare handoff games average
-17.29; policy strength and opponent mixture confound that contrast.

### Project-history adjudication

The fresh field data do **not** reopen permanent farming, fixed production pulses, opponent-crop
harvest-on-contact, serialized TRAIN funding, static role separation, or wholesale D40 transfer.
Those mechanisms are visible in leaders but already have negative causal tests.

The new distinction is explicit return ownership. D92 could divert a worker to suppression but
did not bound the excursion around a remembered producer job. D24/D26 returned an entire cold
policy at a fixed turn, not one worker to its prior productive state. D162/D163 cannot represent
role history or a P→S→P episode at all.

## Next causal experiment

Use exact warmed resident as control and fallback on already-consumed maps. Arm only after one
resident worker has a referee-confirmed own-production history and then enters opponent-crop
suppression. Let it complete one bounded suppression excursion, explicitly return it to its
remembered live own-production target, and abort to exact resident if the target disappears or the
episode exceeds the field-derived 16-turn return horizon.

Require:

- exact resident actions before activation and after return/abort;
- both seats, broad opponent support, and enough activated tasks;
- no TRAIN, crop-ownership, command, transaction, or horizon violations;
- positive paired mean margin and own-score protection;
- nonnegative family breadth, catastrophe count, and negative-margin mass; and
- a negative decision if activation is too sparse or if explicit return merely repeats D87's
  unharvested-crop failure.

This is a local mechanism experiment, not a candidate or Arena protocol.

## Reproducibility

- snapshot manifest: `2e5ed6b0e8cb486de57d2deddaf36a46074b6ddc58057e4042c017007afb0520`;
- processed manifest: `eef9d329192cc2655ab4c2d0398999feb4e1f7b36cb88b03b4e693103230570c`;
- analyzer: `617908d5f1bc12d37b7113e2578a87062fc48c30aa37f07884067e8752353fb6`;
- occurrence rows: `453d91741198e03f00519feca8fba4349b6adaa78ba621e3c33c864aab16fc21`;
- aggregate result: `6ed98a7c7547b3b1c27b2b96bf975b07109880198f9b38fb5725bb626af42e27`;
- focused and snapshot regression tests: 22/22 pass.

The one-process and 20-process occurrence rows are byte-identical. Wall time falls from 21.59
seconds at 98% CPU to 2.88 seconds at 1,489% CPU, a 7.5× speedup.
