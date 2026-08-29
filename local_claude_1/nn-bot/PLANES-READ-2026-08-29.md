# Reading the signed plane table — what it settled, what it left to the source

Written 2026-08-29 by `claude_1` for card `20260829-nn-bot-way-b-dataset`, on the day
`OBS-PLANES.md` was signed and the Phase 1 environment landed
(`codex_1` handoff `20260829T184046Z`, artifact `dc420b449bb0d442f0c9b3c4facedac70e0de740`).

The card asks the dataset to carry a **second, independent** implementation of the 104 planes and a
drift test that requires the two to be byte-equal on 1,000 states. The second implementation is
`local_claude_1/nn-bot/build_planes.py`. This note says exactly how independent it is, because a
drift test written by reading the other implementation proves less than one written blind, and the
difference should be on the record rather than in my head.

## The result first

```text
python3 local_claude_1/nn-bot/build_planes.py --self-test
    self-test: PASS (0 failures)

python3 local_claude_1/nn-bot/build_planes.py --drift \
    --library <release>/libtroll_farm.so --states 1000
    drift test, generation v144-legacy: 1000/1000 states byte-identical
    (324 of them with a staged earlier troll)
    environment observation digest sha256
    745398c34c4fe1e0b79336c5fcf1a8288e3a1450fb1feeb6a066167b21e59f7e
```

The 1,000 states are drawn from the exact reconstruction of the ten-game slice
(`local_claude_1/nn-bot/replays-slice-10/`), shuffled with seed 20260829; each is viewed from a
random seat, at the plan phase or at a random own troll's mini-step, with a random plan index and a
random prior-trained latch. The comparison is on raw `u8` bytes, as the table requires.

**The generation.** The delivered environment reports `TF_FULL_PLAN_SIZE = 144` and the signed
table is written to that vocabulary, so the drift test ran in `v144-legacy`. The dataset itself is
built to `v400-2026-08-29` (amendment 8 of the parent card). The builder holds both and the drift
test **refuses** to compare across them: a v400 plan index is not representable in a 144-plan ABI,
so a green run across generations would be meaningless. When the environment is rebuilt to 400 the
same command re-runs in `v400-2026-08-29` with no edit.

## The six places the table did not decide, and how I decided them

Everything not listed here was written from `OBS-PLANES.md` alone. These six I resolved by reading
`rust/src/rl_full.rs` at the pinned commit, so on these six the drift test is a **consistency
check**, not an independent confirmation.

1. **A shack cell is none of grass, water, rock or iron.** The table makes the map row
   authoritative for planes 1–6 and says a tree does not replace grass, but it does not say what
   the two shack cells are. The source gives them plane 0 and planes 5/6 only.
2. **A dead tree is absent from planes 12–15.** Plane 7 is "any living tree"; the table does not
   repeat the condition for size, health, fruit and cooldown. The source skips `health <= 0`
   entirely, so a felled tree's cell is zero in all of 7–15.
3. **A door cell reads zero in planes 38–39, not one.** The table fixes the shack cell at zero and
   is silent about the doors themselves. They are the BFS sources, so they are zero too, and the
   first cell past a door is one.
4. **A BFS source is seeded at distance zero whether or not it is walkable.** The table does not
   say it. It matters wherever a troll stands on its own shack, which is not a walkable cell.
5. **Planes 57–58 and 72–87 count the trolls as they were, not as they are staged.** Planes
   16–37, 93–96 and 100–103 draw an earlier own troll at its staged end cell; the counts, maxima
   and sums are taken from the unstaged list. Staging moves a troll's cell and nothing else, so the
   two readings agree on every state — but they are different rules and only one is implemented.
6. **The MOVE destination behind the staging rule.** The table says an earlier own troll is drawn at
   "the exact destination predicted by the engine after the movement-speed limit" and stops there.
   The referee's rule, as `sim/engine.py:next_cell` states it, is: of the cells within `speed`
   walking steps of the troll, take the one whose walking distance to the target is smallest, ties
   to the lexicographically smallest cell; an unreachable target is first replaced by the reachable
   cells nearest it in Manhattan distance.

   **This is the one that bit.** My first reading — "walk up to `speed` steps along a shortest path
   to the target" — is the natural reading of the table's sentence, and it disagreed with the
   environment on **123 of the 324 staged states, 38 %**, every disagreement being the staged troll
   drawn on the wrong cell (planes 16, 18–21, 22–27, 93, 94, 100, 101). The two rules coincide
   whenever the target is reachable within one step and diverge on ties and on unreachable targets.
   Written to the referee's rule, the same 1,000 states are byte-identical.

   The lesson for the table, offered to its signer: sentence 6 is the only place where a reader who
   follows `OBS-PLANES.md` faithfully builds a **different tensor** and no test in the programme
   would say so. It is worth one more sentence naming the rule.

## What the drift test does not yet cover

- **Twelve trolls.** The ten-game slice never trains past the trolls it has, so the deepest staged
  state carries few own trolls. The reserved-cell rule of the mask is not exercised here at all —
  the mask is a separate surface and this test compares observations only.
- **The v400 scales.** They are exercised by the self-test's saturation checks at the old and the
  new maxima for both seats, but not against a compiled environment, because none exists yet.
- **Seat rotation against the environment on a point-symmetric state.** Required check 1 of the
  table is proved inside the self-test on a hand-built board, not against the library.

## The v400 re-run against the amended environment (2026-08-29, evening)

`codex_1`'s amended Phase 1 delivery (correction `20260829T200655Z`, artifact
`07b440bd4ab035d5c70935bd549b7f7e8b8987f2`) rebuilds the environment to `TF_FULL_PLAN_SIZE = 400`,
so the drift test now runs in the generation the dataset is actually built to:

```text
python3 local_claude_1/nn-bot/build_planes.py --drift \
    --library /tmp/claude1-p1v400-repro/rust/target/release/libtroll_farm.so \
    --replays local_claude_1/nn-bot/replays-slice-10 --states 1000
    drift test, generation v400-2026-08-29: 1000/1000 states byte-identical
    (200 of them with a staged earlier troll, 0 skipped for having no legal staged prefix)
    environment observation digest sha256
    60dd395e815a3374890d78751833e1b05a256e987ec80ac212cddd32b5f21286
```

The planes themselves needed **no edit** — the v400 tables were already written and self-tested,
and every one of the 1,000 states matched on the first run against the compiled library. What did
need an edit is the **sampler**, and the reason is worth recording because it is a real change of
contract, not a bug in either implementation.

Amendment 2 makes `tf_full_obs_from_state` *validate* the context it is handed
(`validate_observation_context`, `rust/src/rl_full.rs:363`) and return `-2` for any context a real
game cannot reach. My sampler was written against the old permissive entry point and offered three
kinds of impossible context, so the first state of the run aborted with `returned -2`:

1. a plan index that the plan mask forbids (amendment 8's single rule: entry 0 is always legal,
   every other plan only while the roster has room — `legal_plan_mask`, `rl_full.rs:447`);
2. a `prior_target_trained` latch on a troll row, or on a plan row with a nonzero plan (the flag is
   plan-phase-only, and a trained target must have been cleared);
3. a staged prefix that was one arbitrary earlier troll with an arbitrary cell, where the
   environment now requires **exactly** the earlier-troll prefix in id order, strictly increasing,
   each staged action legal for its own troll.

The sampler now builds the prefix one troll at a time and takes the legal MOVE cells from the
environment's own per-cell mask. **That is a seventh consistency dependency**, and it is a weaker
one than the other six: it decides which contexts get compared, not what the planes contain. A
plane that both implementations got wrong would still pass; a context that only the environment
believes is legal would still be compared. The 200 staged states in the run above are staged from
that mask, and `0 skipped` says no sampled prefix was rejected.

Two coverage notes change. The v400 scales are no longer untested against a compiled environment —
they are exercised by the run above. The staged share fell from 324/1,000 to 200/1,000 because a
legal prefix is only available when the active troll is not the first of the roster.
