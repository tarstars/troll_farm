# Curriculum PPO Level 1 preflight result — 2026-07-19

## Verdict

**The infrastructure gates pass, but PPO from scratch is closed before the prospective bank.**

The Rust vector environment, spatial network, CPU execution path, teacher, and controls are all
sound enough for another curriculum iteration.  Two independent debug-bank runs fail to learn the
complete nontrivial build loop by 250,000 transitions.  The faithful-schedule run learns local
HARVEST and DROP decisions but not reliable global destination selection.  It reaches only 12.7%
success versus 10.9% random legal and 99.8% teacher, with 3/876 nontrivial successes.

The frozen official training stream beginning at 1,000,000 and held-out evaluation bank beginning
at 2,000,000 were **not opened by a learned policy**.  This is a readiness rejection, not a held-out
L1A result.  The exact resident and Arena entry remain unchanged.

## Infrastructure and controls

The implementation consists of:

- `rust/src/rl_level1.rs`: batched full-geometry environment and C ABI;
- `cgauto/rl_level1_env.py`: persistent NumPy/ctypes vector wrapper;
- `cgauto/train_level1_ppo.py`: 34,926-parameter masked spatial actor-critic and PPO;
- `cgauto/analyze_level1_policy.py`: deterministic action/opportunity audit; and
- focused Rust/Python tests.

Integrity evidence:

- 3/3 focused Rust tests pass;
- 5/5 focused Python environment/model/audit tests pass;
- repeated batches are byte-identical under identical seeds/actions;
- the teacher action is legal on every checked state; and
- slow/fast one-step resynchronization over 30 seeds and 8,938 steps has zero inventory and zero
  plant-count differences.

The slow/fast check also reports 8,138 position differences (91.05%).  This is expected but large:
both local engines use different deterministic substitutes for the official referee's randomized
movement ties.  The environment remains a curriculum/mechanism substrate, not arena-transfer
evidence.

Frozen held-bank controls, run before any learned evaluation:

| Policy | Success | Median successful turn | Height-bucket floor | Throughput |
|---|---:|---:|---:|---:|
| deterministic teacher | 998/1,000 = 99.8% | 40 | 99.60% | 42,109 transitions/s |
| random legal, RNG 7301 | 109/1,000 = 10.9% | 1 | 10.04% | 66,718 transitions/s |

Random success is almost entirely the zero-deficit case: the action sampler merely vacates an
already funded shack and automatic training succeeds.  The controls therefore separate complete
resource acquisition from an easy initial-state artifact.

The 14-thread setting sustains roughly 4,000--7,100 rollout transitions/s and 760--1,060 effective
transitions/s including four PPO epochs.  End-to-end debug runs use about 69.5% aggregate host CPU,
which passes the protocol's `>5,000 transitions/s` alternative during normal sampling.  Twenty
logical threads are rejected as an execution setting: on this hybrid i7 they trigger frequency
collapse and reduce sustained inference by more than an order of magnitude.

## Debug run A — 250k-local schedule

Configuration: model seed 29, training seeds from 0, debug evaluation seeds 5,000--5,999, 250,000
total transitions, so linear learning-rate decay reaches zero at the checkpoint.

- success: 124/1,000 = 12.4%;
- nontrivial success: 0/876;
- median successful turn: 1;
- minimum height bucket: 10.8%;
- recent mean shaped return improves from roughly -27 to -5.49;
- runtime: 310.16 seconds wall, 806 effective transitions/s overall; and
- peak RSS: 1.24 GiB.

The action audit identifies a hard local transition failure:

- 160,854 MOVE, 601 DROP, 745 PICK APPLE, and **zero HARVEST**;
- HARVEST was legal on 73,230 audited decisions and never selected;
- 130,651 moves target the current cell (canonical WAIT); and
- all successes have initial LEMON deficit zero.

This run learned partial potential reduction but not the work verb needed to turn proximity into
currency.

## Debug run B — faithful 1M schedule through Stage A

Configuration: model seed 31, the same debug partitions, a nominal 1,000,000-transition schedule,
and the frozen Stage A stop at 250,000.  Learning rate therefore remains `1.875e-4` at evaluation,
exactly as it would in the prospective run.

- success: 127/1,000 = 12.7%;
- nontrivial success: 3/876 = 0.342%;
- median successful turn: 1;
- minimum height bucket: 11.24%;
- recent mean shaped return improves to -11.32;
- runtime: 317.26 seconds wall, 788 effective transitions/s overall; and
- peak RSS: 1.28 GiB.

This run learns direct work but still fails the full loop:

- HARVEST is selected on 403/470 legal opportunities (85.74%);
- DROP is selected on 10,983/14,401 legal opportunities (76.27%);
- the policy nevertheless issues 106,558 current-cell waits;
- only 4,015 moves target a LEMON tree, while it also emits 11,876 CHOP and 11,269 PICK BANANA
  actions irrelevant to the requested LEMON build; and
- success above zero deficit occurs on only three maps.

The first failure was not merely unlucky initialization or premature learning-rate decay.  Reward
shaping can teach local work transitions, but global target/phase selection from scratch is the
remaining bottleneck.

## Multi-level analysis

### Action level

The 13-plane legality mask works and direct verbs are learnable.  However, `MOVE current` is both
the universal wait and a spatial action at the selected troll.  It becomes an attractive local
mode once the policy has harvested the easiest movement reward.  More entropy or a larger budget
would extend a representation that already missed the frozen capability boundary.

### Representation level

The observation contains selected-unit and plant maps but no explicit per-cell navigation-distance
field.  A four-block convolution has limited receptive range on a 22-cell-wide board.  The teacher
uses all-pairs path distance, while the policy must infer that relationship indirectly through
terrain convolutions.  Destination selection is therefore needlessly hard and partly
non-representable at the pilot's depth.

### Curriculum level

The first task still asks a random policy to discover a long multi-trip sequence.  Potential
shaping makes partial movement profitable, but complete success requires repeated rare phase
transitions.  The public winner's broad description does not establish that its Level 1 started
from entirely random weights without demonstrations, richer distance channels, or easier internal
sublevels.

### Whole-project level

This result strengthens, rather than weakens, the architecture pivot.  The current resident's
field residual is complete score flow, and isolated heuristics have repeatedly failed.  The new
stack now provides a fast full-geometry learning substrate and deployable action representation.
What failed is one initialization/curriculum, not the need for a whole-policy controller.

### Transfer level

Nothing here qualifies a live candidate.  Map generation and economy are useful locally, but the
91% slow/fast position drift and previously measured opponent stochasticity require later field
gates.  No Arena write is warranted.

## Ranked next hypotheses

1. **Teacher-supervised bootstrap, then PPO.**  Imitate the 99.8%-successful deterministic teacher
   on training-only trajectories so MOVE/HARVEST/DROP phases are represented before terminal
   optimization.  This directly attacks both observed failures and is inexpensive.
2. **Explicit selected-to-cell BFS distance plane.**  Replace redundant observation channels with
   per-cell distance to the selected troll and home.  This makes the teacher's destination rule
   representable without deep message passing.
3. **Online teacher auxiliary loss during PPO.**  Retain a small cross-entropy term on visited
   states so PPO cannot collapse back to current-cell waiting while it explores better routes.
4. **Progressive deficit curriculum.**  Begin with one missing LEMON on ripe/near-source maps,
   then expand deficits and source maturity before the frozen random-map task.
5. **Factorized verb and destination heads.**  Choose MOVE versus direct work globally, then a cell
   conditional on MOVE; this prevents a single spatial WAIT logit from absorbing every phase.
6. **DAgger-style teacher recovery.**  Query the teacher only on states reached by the learned
   policy, closing covariate shift after behavior cloning.
7. **Productive-action pruning sublevel.**  When a requested resource can be harvested or useful
   cargo dropped, temporarily mask unrelated economic actions; later remove the pruning.
8. **Phase/needed-resource auxiliary heads.**  Predict SEEK/HARVEST/RETURN/TRAIN and the currently
   binding currency to force the trunk to encode the relevant global state.
9. **Recurrent compact memory.**  Add previous phase/action state only if feed-forward bootstrapping
   still oscillates; the current direct-action audit does not yet justify it.
10. **Top-replay imitation after simulator Level 1.**  Distill strong field trajectories only once
    the fixed-worker loop is learned, because replay imitation now would mix plan selection,
    opponent response, and movement failure at once.

The next authorized implementation combines directions 1 and 2.  Direction 3 is reserved as a
single follow-up if PPO erases a successful supervised policy.  The official Level 1 train/eval
banks remain sealed until a behavior-cloned model clears the debug functional gate.

## Artifact checksums

- teacher control: `8b4053bd74dd7e2248b671802e371c82e19bff1ec447cc8725d2ba289aa3a1c1`
- random control: `3bdd77f2d1b60410aa3c919baf312e0f6164d9fd5af0b7e1641dc5922fbfec2f`
- run A summary: `157a9ef1b702644112a79a64ede42817bc214ac7a45bae1ca7c5810f16491c2d`
- run A action audit: `062eefca77ba6de33642e4bf45f2c9fb0c508272d22e6f89aad654a60da2a95f`
- run B summary: `0f2919a77296c167f282b8b6240fd90072983ee80386eb24425fe10f61634118`
- run B action audit: `cc4e2447bb3475b5167d69ae7ef9f097c2e6f3999f3dff4e908a1cc0e56deaff`

