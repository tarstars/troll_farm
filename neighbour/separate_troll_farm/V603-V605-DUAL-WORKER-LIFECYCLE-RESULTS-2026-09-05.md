# V603--V605 explicit dual-capability second-worker lifecycle: productive too late, closed -- 2026-09-05

## Verdict

V603--V605 repaired the missing composition from V470 and V601: the second worker had harvest
power, owned typed plots, planted them, harvested their first mature fruit, felled mature wood,
banked it, and refilled the lane. The largest arm, V605, added 11.58 ring plants and 19.71 ring
harvests per game. It nevertheless scored -36.75/-27.25/+5.96 against exact V468 at turns
100/200/final. V603 and V604 also lost both checkpoints and finished behind V468. No arm entered
the frozen 192-game panel, fresh maps, duels, packaging audit, or platform publication.

The failure is architectural rather than an inactive branch. By turn 100 V605 had exchanged
36.34 chop commands for seed, plant, harvest, and banking work. Although the outer controller
replaced only the trained worker's command slot, the new crops also attracted the inherited V468
starter: it issued 15.05 fewer chops by turn 100. Final chops nearly recovered only because games
ran 28.5 turns longer; opponents gained 84.3 score and 14.2 wood while V605 gained only 6.0 score
and 0.2 wood. A concurrent orchard cannot pay the early axe opportunity cost under this shared
planner.

## Implementation and repair

`build_v603_dual_worker_lifecycle.py` derives all three arms from V595, whose lineage derives from
V468. It reuses V470's exhaustive training enumeration with maximum harvest power one and the
one-apple reserve. The successful second train changes from `TRAIN 3 2 0 2` to
`TRAIN 3 2 1 2`, still at median turn 6. The added controller:

- changes only the trained harvest/chop worker's selected action slot;
- records only that worker's successful typed plant attempts;
- chooses own-half cells within four steps of the home bank, preferring water;
- avoids the starter's selected target and projected landing;
- takes surplus bank fruit or fruit from ripe non-owned trees;
- protects tracked trees to size four, harvests the first generation, then mature-fells and banks;
- replants carried fruit before seeking another seed; and
- falls back to the best non-protected wood cycle.

V603, V604, and V605 differ only in live plot cap two, four, or six. Each compact program is
99,223 UTF-16 units, 777 below the platform limit.

The first 24-game smoke exposed a concrete implementation defect: `plot_cell` rejected every
occupied cell, including the worker's own cell. After reaching a selected planting cell, the
speed-three worker selected another cell and oscillated forever. The resulting smoke-one losses
of -68.2/-115.6/-119.2 were diagnostic only. A regression test now requires other-unit occupancy
to be excluded while allowing `worker.id`, all candidates and runners were rebuilt, and the
smoke-two panels below are the verdict evidence. The repaired worker plants normally; representative
V605 events are `PICK 2 BANANA` at turn 8, `PLANT 2 BANANA` at turn 10, and successive mature
`HARVEST`/replant cycles from turn 34.

## Repaired behavior smoke

Each rebuilt arm ran map seed 9,941,000 in both seats against all 12 frozen opponent families:
24 paired games per arm. Deltas are candidate minus exact V468, whose mean score was
94.67/160.67/215.46 and whose mean wood was 53.21.

| arm | live plots | turn 100 | turn 200 | final | candidate W/T/L | wood delta | opponent score delta | decision |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| V603 | 2 | -24.00 | -23.13 | -8.21 | 12/0/12 | -2.75 | +73.71 | reject |
| V604 | 4 | -39.63 | -35.34 | -8.63 | 11/0/13 | -3.08 | +81.38 | reject |
| V605 | 6 | -36.75 | -27.25 | +5.96 | 13/0/11 | +0.21 | +84.33 | reject |

V468 went 19/1/4. All arms retained two workers and trained at turn 6. First command divergence
was therefore turn 6, with mean changed command turns of 261.00, 261.75, and 261.42. There were
no critical or unclassified issues. Respectively 5, 8, and 11 rows reported only noncritical
blocked moves; the checkpoint and economic failures persist across zero-issue rows and are much
larger than that secondary traffic cost.

Capacity scales the intended mechanism but not score:

| candidate minus V468 | V603 cap 2 | V604 cap 4 | V605 cap 6 |
|---|---:|---:|---:|
| ring plants | +4.67 | +10.38 | +11.58 |
| ring harvests | +10.33 | +15.54 | +19.71 |
| final wood | -2.75 | -3.08 | +0.21 |
| final own score | -8.21 | -8.63 | +5.96 |
| final opponent score | +73.71 | +81.38 | +84.33 |
| game turns | +27.33 | +28.50 | +28.50 |

## Mechanism

V605's per-role command stream locates the checkpoint loss. Counts below are commands per game
through turn 100.

| role and verb | V468 | V605 | delta |
|---|---:|---:|---:|
| starter `CHOP` | 45.38 | 30.33 | -15.05 |
| worker `CHOP` | 31.00 | 9.71 | -21.29 |
| starter `HARVEST` | 2.00 | 5.04 | +3.04 |
| worker `HARVEST` | 0.00 | 5.04 | +5.04 |
| starter `PLANT` | 0.25 | 1.50 | +1.25 |
| worker `PLANT` | 0.04 | 12.88 | +12.84 |
| worker `PICK` | 0.08 | 8.71 | +8.63 |

The explicit worker lane does produce: in a representative row it plants six bananas by turn
30, harvests at turns 34 and 40, replants the fruit, and later repeats the lifecycle with lemons.
That throughput is precisely the problem under the shared planner. The worker stops harvesting
natural value and chopping while it creates the lane. Then V468 sees those live crops in the
global state and redirects the supposedly preserved starter into their harvest, plant, and bank
work. Preserving the starter's outer command slot is not the same as preserving its behavior when
the state visible to its planner has changed.

At the end V605 emits 179.79 chops per game against V468's 182.79, but takes 301.0 turns against
272.5. The 28.5 extra turns explain the apparent recovery: final chop count is similar while chop
rate and early deposits are much worse. Extra crops and duration benefit the opposing policies
more than this bot; the cap sweep's opponent gain rises monotonically from +73.71 to +84.33 while
own score never gains 6. This rules out raising the cap or running the expensive full panel.

The next experiment must isolate ownership at the planner boundary, not merely at the final
action slot. It will keep V468 exact through turn 100, hide worker-owned plots from the starter's
target planner, and activate the mature cap-six lane only after the checkpoint. This differs from
V588's post-turn-100 overlay because the repaired lane has typed ownership, first-generation
harvest, and mature felling; the new test is whether starter isolation can retain the proven axe
income while the lane pays back.

## Verification and integrity

- focused builder tests: 12 passed, including standalone readable compilation, cap normalization,
  self-occupancy regression, starter-slot preservation, typed reconciliation, and compact limit;
- complete repository suite: 238 passed in 49.80 seconds;
- canonical rebuilt runners, discarded smoke-one diagnostics, repaired smoke-two panels, gates,
  and diagnostics:
  `/data/separate_troll_farm-working/archive/2026-09-05-v603-v605-dual-worker/`;
- V603/V604/V605 runner SHA-256:
  `e0f152de79aed7a24968a77e4ba5ce9668132704495c536759d489f26470ec5a` /
  `8249ebbe0bf1920db0e2dada3cf9037e153c512a9174b2ee281868b73cc981c2` /
  `b4c7b81c636804f154bf108e6f736aa8b22902439ff29016c8c8bf191ab5c6cc`;
- repaired panel SHA-256:
  `712365148366b095e8611caa47f03670d6e4fc0c19a2afc6c28e896121a11483` /
  `c4c5cac01ae868378d94e884f4a2e5e676e3e7f8c5c0d6bff1353fd4520a587d` /
  `c27732c95a9d5201c841b47be5579a610a0074bbd8810ac0bebf5931ca581d04`;
- repaired gate SHA-256:
  `b7d9c39471285c43985d26a2da661a82b025c56c4a57e08e815826075c99de26` /
  `435563b8581cc4235c82ef2faaed6227726166d1fa0d020e2674e969573cc646` /
  `6543f01864da5fccd2f0b6fc4201a5349b1d89cd7175ed5caf20a675c8781044`;
- repaired diagnostics SHA-256:
  `305b6ad37afa054b5b3737202c4d500cc30eb7d72d70d25acfb97e7bf52497f5` /
  `594ab82e47ede70462efda3e0181a56aa461d6484aa79f17f7ae1986358b8da6` /
  `6b0161b2b3a5c7c9b2578fb7aad3d883373d41484c0209d1d3e6938b156e1287`;
- module SHA-256:
  `8aae387eefc2d10266b35f01362b2081188e677d208dd40308e1f09b5354b09d` /
  `c8eca5b59ea833bda5a5cba8f0f8d0f448d23d871729b7898f264de8f7d6ab22` /
  `0c22884a22e69ceca5d832a52f38eb35f0a17deaec899ad72244fdfa4b3279c9`;
- compact SHA-256:
  `4bed0658ae7b25533fe9d8467e814fae6bf6ffd27a2c6a295b111e89459e6c56` /
  `6e1bb7693a907bea5ce854c466361acac8295029109809aadacffe1dc16f1056` /
  `204af85216b4954bf932d9d2c66dbd1166ac53394629c5fcbba4b7df21cd82a0`;
- builder/test SHA-256:
  `f5183b4df367d17a0fc2338fdc65967a87eeabcc9cc49e93c059855e1a42faba` /
  `cefd89e43a89f5da9a20d53bbdb9bb279f63599fcd2e9049eab8e833f3bd197c`;
- production remained unchanged: `bot.rs`
  `b8d2c4e298d7d748612b64b1a91c3d88826c467846f9544d0df1b86279588372`,
  `submission.rs`
  `922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`;
- read-only neighbor remained at `370fa63cae12eda129ff5553c33a7086dfcb87c2`, retaining its pre-existing
  modified `data/processed/stats.json` and untracked
  `data/panels/top5-ab-20260902T115338Z.json`.
