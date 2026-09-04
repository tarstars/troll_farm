# Orchard reproduction — everything I decided before I ran anything

Card: `coordination/tasks/20260904-orchard-reproduction.md` (chartered 2026-09-04 17:2xZ, due 2026-09-06 17:00Z).
Written and committed **2026-09-04 17:2xZ, before a single game was played** — that is the whole point of the
document. The card asks for three choices to be stated in advance (its §3); they are §3, §4 and §5 below.

**The constraint that governs this task, restated so it is on my own record:** I have not opened, and will not open,
anything under `chatgpt_1/champion-prefix-orchard/` — no `oracle.py`, no `policies.json`, no `results/`, no
`RESULTS.md`, no `FINAL.md` — until my own numbers are written down and committed. As of this commit I have read
only file *names* there (`git ls-tree --name-only`, needed to verify a transport defect on 09-04), never a file body.
Everything below was derived from the parent charter, my own closed kinetics read, and the referee.

---

## 1. What I am measuring

The same thing chatgpt_1 measured, restated from the charter only:

```text
A (baseline):  unchanged champion ────────────────────────────────────────► turn 300
B (candidate): unchanged champion through its own second TRAIN
               → a near-orchard macro
               → the same unchanged champion, continuously advanced ──────► turn 300
```

Reported: **Δ paired final margin** and **Δ paired own score**, each with a 95 % interval and n; the policy my
search chose and how often it chose `NO_PLANT`; my action vocabulary; my exclusion rule and its count; my selector.
Then, and only then, I read chatgpt_1's files and write a direct comparison.

## 2. The machinery, and why it is not a model

**I am not writing a planting model. The referee is the model.**

Both arms are played through the July Python referee (`fuzz_panel.FuzzReferee`) on real ladder maps from
`data/processed/maps.jsonl`, with the seeded per-map fruit/iron draw and the scripted opponents (`harvester`,
`chopper_aggressor`) — the harness shape of `local_claude_1/the-floor/smoke.py`, which I have run before. The
**champion binary is the decider on every turn of both arms**; it is never replaced by a policy.

Arm B interposes one thing between the champion's emitted command line and the referee: a **macro layer** that may
rewrite the command of **one designated planter troll**, and nothing else. Every other troll's command passes
through byte-identical. The layer is a pure pass-through until the branch turn.

This matters for the card's third question. Growth release, self-occupancy of the planting cell, raid, felling,
carry and banking are **whatever the referee does**, because the referee is what runs. There is no separate planting
model of mine to contain a self-occupancy bug, and therefore no repair of chatgpt_1's to inherit or to reproduce.
If the two implementations disagree, this is the most likely place, and the disagreement would be informative in
exactly the direction the card cares about.

**What I check instead of a model:** that the referee itself matches the mechanics the parent card §4 states as
given — plant → first-fruit turn beside water and inland; health at maturity by species (banana 6, plum 12, lemon
12, apple 20); felling a size-4 tree yielding 16 points; the carry and the bank. I check these on a handful of
hand-computed planted-tree cases before I read any aggregate. **If the referee disagrees with §4, that is a finding
and I report it rather than papering over it.**

## 3. The branch point, and the identity I must prove first

Branch = the first turn **after** the champion's own second `TRAIN` resolves, per map-seat, found by reading the
baseline arm's own command stream. It is not a fixed turn number and I do not assume turn 9.

**Mechanics before value, as two gates that run before any Δ is computed:**

1. **Prefix identity.** Arm A's and arm B's command streams are compared turn by turn up to and including the second
   `TRAIN`; they must be byte-identical on every map-seat. This is guaranteed by construction (the layer is a
   pass-through before the branch) and is therefore a check that my construction is what I think it is.
2. **The second troll never changes** — same talent, same training turn, on every case.
3. A command line on all 300 turns, and no referee error of any kind, **on both arms independently.**

Third training is disabled in arm B: the macro layer never emits a `TRAIN`, and if the champion emits a third
`TRAIN` it passes through unchanged on both arms, so the arms cannot differ by a roster change.

## 4. Choice one — the action vocabulary, published in full

The macro layer's complete alphabet for the designated planter troll. Nothing else is reachable by the search:

| action | meaning |
|---|---|
| `NO_PLANT` | pass the champion's own command through unchanged. **Always legal, on every turn, for every policy.** |
| `PICK <fruit>` | take a fruit to hold as a planting seed, when the troll carries none |
| `MOVE <cell>` | one step toward the policy's next planting cell |
| `PLANT <cell>` | plant the policy's species at a free cell inside the policy's radius of the shack |
| `CHOP <own tree>` | fell one of the orchard's own trees once the policy's fell trigger is met |
| `DROP` | bank carried wood at the shack |

**`WAIT` is deliberately absent.** A macro that idles is strictly worse than passing the champion's own command
through, and `NO_PLANT` already covers "do nothing special". This is also why my exclusion rule below can be
relative rather than absolute.

**A policy** is the tuple `(species, n_trees, radius, fell_trigger)` plus `NO_PLANT`:
species ∈ {banana, plum, lemon, apple}; `n_trees` ∈ {1, 2, 3}; `radius` ∈ {2, 4} steps from the shack;
`fell_trigger` ∈ {at maturity, at the first turn no wild tree stands within 4 steps}. That is
4 × 3 × 2 × 2 = 48 planting policies, plus `NO_PLANT` = **49**.

The grid comes from my own closed kinetics read, not from chatgpt_1's: 11.5 free cells within 2 steps and 27
within 4 (median, 400 map-seats), of which 2 and 5 are water-adjacent, and a starting fruit draw of 24 — so
`n_trees` above 3 is not reachable close to the tent and is not in the grid. Banana is in the grid first because
a chop-1 troll fells it in 6 turns against an apple's 20 for the same 4 wood.

## 5. Choice two — the exclusion rule, and it is deliberately not an absolute threshold

chatgpt_1 excluded **17 of 20** policies for introducing a new long-inactivity interval. Seventeen of twenty is a
large fraction sitting directly upstream of a null, so this is the choice most worth making differently.

**My rule: a policy is excluded on a map-seat only if its longest no-command streak exceeds the champion's own
longest no-command streak on that same map-seat.** Relative to the baseline, not to a fixed number.

The reason is in the parent card's own words: the harness's `stalled` field is a **longest no-command streak** —
not a crash, not a referee end condition, not a loss label. The champion itself has such streaks. A rule that
compares a candidate against an absolute threshold can therefore exclude a policy for behaviour the champion is
already exhibiting on the same map, and an exclusion rule that fires on the baseline is measuring the map, not the
policy.

**I will also compute an absolute-threshold variant** and report both counts side by side, plus **what the excluded
policies score** — because "how many does each rule drop, and were the dropped ones any good" is the question the
card is actually asking here.

## 6. Choice three — the selector, and the discriminator that is my own addition

**Selector, pre-registered: leave-one-map-out across the map-seats**, the same family chatgpt_1 registered. I am
not choosing a weaker selector to manufacture a difference; if two implementations agree under the same selector
family that is the stronger result.

A per-map choice is reported **only** as an explicitly labelled hindsight upper bound, never as a result. Its
hindsight oracle planted on 16 of 24 maps and it correctly refused to claim that; so will I.

**And one thing I am adding, recorded before the run because I wrote it down at wake #126 already:**

> A whole-game Δ of exactly 0.00 on every fold is consistent with two different findings — *the selector never
> planted* and *planting gained nothing* — and they are not the same fact.

So I will report, beside the selected result, **the fixed-policy Δ of every surviving policy against the champion
with no selection at all.** If the selector's Δ is 0.00 because it chose `NO_PLANT` everywhere, the fixed-policy
table says whether the policies it declined were worth anything. A null that arrives by a selector is a different
claim from a null that arrives by an absent mechanism, and this table is what separates them.

**Pre-registered prediction, also from wake #126, recorded before I see any number:** if the orchard is a near
reserve rather than a value engine, arm B's margin is flat through roughly the first hundred turns and opens only
after the near forest is consumed — no wild tree stands within four steps from turn 75 onward. A flat early margin
is the predicted shape, not a null. I will therefore report the margin as a curve over turns, not only at 300.

## 7. Dead means

If I cannot show the prefix is byte-identical through the second `TRAIN`, or cannot show the referee reproduces the
§4 mechanics on hand-computed planted-tree cases, **I stop and say so** rather than shipping an aggregate I do not
trust. Per the card, that is a real outcome and it is worth more than a number nobody can stand behind.

## 8. What this task must not do

No bot, no submission, **no platform by any route** (the owner's standing rule of 2026-09-04,
policy `20260904T140500Z`), no Arena, no ladder, no cluster. No third troll, no roster change, no altered second
troll. No tuning of anything against the development maps — this is a measurement, not a search for a win.

— claude_1, 2026-09-04
