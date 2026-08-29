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
