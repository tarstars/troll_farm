# Phase 2 day-7 independent reproduction — REPRODUCED

Task: `20260829-nn-bot-way-b-dataset`  
Charter: `coordination/messages/local_claude_1/20260830T021141Z-20260829-nn-bot-way-b-dataset-handoff.md`  
Source reviewed: `origin/main@12d07ba4943fc56dae45d70808634c5d4a4649c3`  
Run UTC: 2026-08-30 02:16–02:29  
Runner: `codex_1` on the VM; no Arena or platform action

## Verdict

**REPRODUCED.** The 10,059-row codec/mask test, the two bench runs, and the trainer smoke all
match claude_1's reported deterministic results. The 24-game and 48-game bench reports have zero
stable-row differences from the committed originals after deleting only `policy_seconds`. The two
trainer epoch records have zero differences after deleting only the three timing fields
`train_seconds`, `held_out_seconds`, and `rows_per_second`.

Preflight: `/dev/vda1` had 2.0 GB free (90% used); no package was installed. The byte-sacred
resident remained SHA-256 `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.
The release library rebuilt from the integrated source with `/home/tarstars/.cargo/bin/cargo`.

## Commands

```text
/home/tarstars/.cargo/bin/cargo build --manifest-path rust/Cargo.toml --release --lib
/home/tarstars/venvs/nn-bot/bin/python local_claude_1/nn-bot/build_dataset.py --codec-test local_claude_1/nn-bot/results/pilot
/home/tarstars/venvs/nn-bot/bin/python local_claude_1/nn-bot/bench.py --self-test
/home/tarstars/venvs/nn-bot/bin/python local_claude_1/nn-bot/bench.py --policy random-legal --no-replays --out codex_1/results/nn-bot-way-b-dataset/bench-random-legal.json
/home/tarstars/venvs/nn-bot/bin/python local_claude_1/nn-bot/bench.py --policy random-mask --both-seats --no-replays --out codex_1/results/nn-bot-way-b-dataset/bench-random-mask-both-seats.json
/home/tarstars/venvs/nn-bot/bin/python local_claude_1/nn-bot/train_clone.py --self-test --shard local_claude_1/nn-bot/results/pilot --name pilot
/home/tarstars/venvs/nn-bot/bin/python local_claude_1/nn-bot/train_clone.py --shard local_claude_1/nn-bot/results/pilot --name pilot --epochs 2 --batch 64 --limit 4000 --workers 2 --out codex_1/results/nn-bot-way-b-dataset/clone-smoke
```

## 1. Builder codec/mask test

PASS in 201.74 s, zero failures:

- 2,954 plan rows and 7,105 command rows (10,059 total)
- MOVE 3,494; CHOP 1,418; DROP 891; HARVEST 746; PLANT_BANANA 206;
  PLANT_LEMON 83; PICK_BANANA 82; PLANT_PLUM 71; MINE 48; PICK_LEMON 29;
  PICK_PLUM 23; PLANT_APPLE 9; PICK_APPLE 5
- 1,992 plan rows labelled index 0, the four-zero "train nothing" plan
- shard vocabulary and library vocabulary both `v400-2026-08-29`

Every label round-tripped through the compiled codec and was legal under the environment mask.

## 2. Bench

The adapter self-test passed 6/6: seat rendering for both seats, seat-rotated codec round-trip,
TRAIN dry-run emission, referee terminal rule, and a whole runtime-mask turn accepted by the
referee.

The day-1 `random-legal` control reproduced in 14.33 s: 24 games, policy wins 0, mean scores
13.6 versus 152.8, illegal commands 0, timeouts 0, referee errors 0, 21 `grace_expired` and 3
`turn_limit`. Stable per-game rows differ from the original on 0/24 games.

The `random-mask --both-seats` run reproduced in 167.86 s: 48 games, policy wins 0 (0/24 from
each seat), mean scores 21.3 versus 153.1, illegal commands 0, timeouts 0, referee errors 0,
41 `grace_expired` and 7 `turn_limit`. Stable per-game rows differ from the original on 0/48
games.

Every entry below has illegal commands 0, referee errors 0, and timeouts 0. Each cell is
`terminal turn / reason`.

| map hash | policy seat 0 | policy seat 1 |
|---|---:|---:|
| `7b515d6db8085355` | 300 / turn_limit | 300 / turn_limit |
| `64b1d4b14f026f9f` | 221 / grace_expired | 241 / grace_expired |
| `c84154d29ea19fbc` | 273 / grace_expired | 102 / grace_expired |
| `b086e0e6163a45ac` | 276 / grace_expired | 257 / grace_expired |
| `89e906123ff36a86` | 300 / turn_limit | 296 / grace_expired |
| `a6062948c27575a8` | 243 / grace_expired | 240 / grace_expired |
| `50bcce5e7ae4a14c` | 190 / grace_expired | 216 / grace_expired |
| `daadbfd7e8423f86` | 248 / grace_expired | 240 / grace_expired |
| `b6a5501980dd849a` | 217 / grace_expired | 227 / grace_expired |
| `19111bc9b90011bb` | 204 / grace_expired | 212 / grace_expired |
| `b91f102962423ddd` | 227 / grace_expired | 219 / grace_expired |
| `6d81a00871f22f23` | 283 / grace_expired | 275 / grace_expired |
| `c14dea6aa5d28951` | 283 / grace_expired | 267 / grace_expired |
| `78e4df84516e04d1` | 111 / grace_expired | 113 / grace_expired |
| `33261cf926f7a3eb` | 227 / grace_expired | 231 / grace_expired |
| `2433a442a41ce6cb` | 300 / turn_limit | 300 / turn_limit |
| `7a082aa227d4192a` | 221 / grace_expired | 182 / grace_expired |
| `62694c8c0a48cf44` | 222 / grace_expired | 225 / grace_expired |
| `21d2746745cd7896` | 116 / grace_expired | 116 / grace_expired |
| `2d8f315778eba2a8` | 300 / turn_limit | 300 / turn_limit |
| `879f73412b531333` | 141 / grace_expired | 118 / grace_expired |
| `80385f5fdcac43f7` | 274 / grace_expired | 263 / grace_expired |
| `d9c8059a3038862e` | 296 / grace_expired | 277 / grace_expired |
| `b64b9915e3f228af` | 263 / grace_expired | 261 / grace_expired |

## 3. Clone trainer

The trainer self-test passed 6/6, including plan-size source, vocabulary identity, staged-prefix
order, one-head-only updates, masked-label rejection, and foreign-vocabulary checkpoint refusal.

The smoke used 4,000 training rows (1,233 plan + 2,767 command; 9 games) and 1,000 held-out rows
(230 plan + 770 command; 1 game). Its deterministic numbers match the report to printed precision:

| epoch | plan loss | command loss | plan acc | command acc | held plan | held command |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2.9722 | 3.2499 | 0.6829 | 0.4055 | 0.5435 | 0.4429 |
| 2 | 2.1589 | 2.2378 | 0.6910 | 0.4460 | 0.5435 | 0.4260 |

Last-epoch training accuracy also matches: MOVE 5.2% (1,381 rows), CHOP 77.8% (555), DROP
99.1% (332), HARVEST 94.1% (272), and PLANT_BANANA 100.0% (94). The run took 148.84 s;
throughput differed from the original and is not part of the deterministic gate.

## Runtime-adapter review sentence

`nn_runtime.py` builds no plane or mask in Python: `PlaneBuilder.observe` obtains both directly
from `tf_full_obs_from_state`; spatial commands use `tf_full_decode_action` and
`tf_full_encode_command`, while the only locally formatted TRAIN dry-run is constructed from the
talents returned by the signed `tf_full_decode_plan` codec. Thus there is one signed codec/runtime
implementation, with Python limited to state-document assembly, dry-run orchestration, terminal
rule adaptation, and seat rendering.

## Preserved artifacts

- `bench-random-legal.json` — SHA-256 `4a12fe293f0892ab9474b4bb1d09b0bd6b5f15a880531ca23a3b7bbcbe4ad02b`
- `bench-random-mask-both-seats.json` — SHA-256 `9d09a736a8b955ef9da6d7078a40195a4e90f91d6c78d1e2f2537d30d511670c`
- `clone-smoke/clone-pilot.json` — SHA-256 `94e7a7dd2ba88cb4e5e4114c36b3d46d656daac5f5bce2c033b2bfb4ef59cf0a`
- `clone-smoke/clone-pilot.pt` — SHA-256 `b29be6cd00f2d59ff8ff0e44562a91c2a130c04b677740df98abed4634fe42ae`

