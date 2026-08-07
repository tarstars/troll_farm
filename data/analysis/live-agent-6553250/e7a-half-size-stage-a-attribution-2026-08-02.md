# E7a half-size Stage A — byte and live-behavior attribution

Status: **complete source attribution / architecture replacement required**.

## Exact boundary

- source: `candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs`
- SHA-256: `97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595`
- baseline: 62,820 bytes
- hard half-size ceiling: 31,410 bytes
- required net removal: 31,410 bytes

The attribution script uses unique semantic item markers and balanced Rust braces directly
on the exact compact artifact. Its spans are pairwise non-overlapping. It does not run a
formatter, rename identifiers, remove whitespace, or credit minification.

## Non-overlapping live blocks

| Logical block | Exact bytes | Baseline share | Live evidence |
|---|---:|---:|---|
| Secure APPLE orchard wrapper | 14,129 | 22.49% | Own planted crops were reaped in only 11/160 E7a games, although those 11 yielded 1,168 fruit; sparse but sometimes large |
| Door and regeneration coordination | 6,678 | 10.63% | Banking/regeneration is common, but the current machinery still permits 25/160 long period-2 games |
| Opening specification planner | 6,539 | 10.41% | Worker two trained in 160/160 games, median turn 9; behavior must remain, exhaustive generality need not |
| Endgame and idle harvest | 5,506 | 8.76% | 942 completed post-turn-250 conversion crops in 114/160 games; conversion must remain in simpler form |
| Joint assignment and movement | 4,942 | 7.87% | Required for two-worker safety, but general priority/forbidden machinery exists mainly for the orchard wrapper |
| Tree forecast and chop valuation | 4,702 | 7.48% | Core live production/denial; retain unless a smaller cycle model passes value gates |
| Fruit, iron and main candidate generation | 3,500 | 5.57% | Core opening and resource acquisition; preserve a smaller direct policy |

These named items account for 45,996 bytes. The remaining 16,824 bytes are parser, data
model, command orchestration, state fields, constructors and small helpers.

## Feasibility arithmetic

Removing the entire secure-orchard wrapper saves at most 14,129 bytes and leaves a
48,691-byte bot. Another **17,281 net bytes** must still disappear after that removal.
Therefore no single-block deletion can meet the objective.

The combined gross size of opening planning, door/regeneration coordination, joint
assignment/movement, and endgame/idle harvesting is 23,665 bytes. Replacing those four
live systems with approximately 6,000 bytes of focused two-worker logic, while removing
the orchard wrapper, is arithmetically sufficient:

```text
62,820 - 14,129 - 23,665 + 6,000 = 31,026 bytes
```

This is a replacement programme, not cleanup. N7's zero-byte dead-code conclusion remains
true.

## Current E7a live behavior (160 exact games)

- all 160 exact agent/submission rows decoded; zero fetch failures or unknown updates;
- worker two trained in 160/160 games, median turn 9;
- 43,369 MOVE, 28,228 CHOP, 6,572 DROP, 1,705 PICK, 1,704 PLANT, 1,307 HARVEST,
  160 TRAIN and 115 MINE commands;
- 1,704 attributed created crops; 11 reaped by the bot; 1,732 wood collected from its own
  created crops;
- 942 completed endgame conversion crops for 967 collected wood in 114 games;
- 2,105 contacts with opponent-created crops in 143 games;
- 25/160 games have a continuous period-2 MOVE run of at least six turns; worst 127.

## Removal ranking

1. **Remove the general secure-orchard wrapper.** It is the largest separable block and its
   priority/forbidden APIs cause downstream generality. Preserve no more than a minimal
   seed rule if value requires it.
2. **Replace door/regeneration coordination with explicit cargo commitments.** A wood
   carrier that chooses home must monotonically approach a fixed bank door until DROP.
3. **Replace opening enumeration with a small bill-preserving choice.** Retain worker-two
   reliability and E7a focus initialization; discard 27-spec ETA generality.
4. **Replace general joint assignment with a two-worker reservation rule.** The controller
   will never have more than two workers.
5. **Keep endgame conversion but remove idle-harvest and multi-mode generality.** Live use
   is too large to delete conversion wholesale.
6. **Retain chop-cycle economics initially.** Simplify only if the integrated candidate
   remains above 31,410 bytes.

## Next construction

Build `INTEGRATED_HALF` directly from the exact candidate with a fail-closed transform.
The builder must emit a logical deletion manifest and an identifier audit. The first
compile target is 30.5--31.4 kB, leaving no cosmetic-compression credit. Value/liveness
tests decide whether a minimal orchard seed rule is affordable.

Reproduction:

```bash
/home/tarstars/prj/troll_farm/.venv/bin/python \
  local_codex_1/e7a-half-size-logical-simplification/byte_attribution.py \
  cgauto/submissions/candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs \
  --output local_codex_1/e7a-half-size-logical-simplification/stage-a-byte-attribution.json
```

