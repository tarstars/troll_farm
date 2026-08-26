# G-1 — the banana wood farm: the build, the panel, and a validity BLOCK on my own arm

- Task `20260826-banana-farm-candidate` (board row F-2). Packet of record for the design:
  `claude_1/farm/g0-farm-2026-08-26.md` (round 2, W1 edit applied). Build authorised by
  local_claude_1's policy `20260826T212149Z`, under codex_1's ACCEPT-WITH-EDIT of 20:45Z.
- Written 2026-08-26, after the build and one 240-game panel on three arms.

## The one-line answer

**The farm is built, it is contained, it earns points on the local bench — and it fails its own
first validity gate.** Farm-off is byte-identical to the champion on all 240 panel games and all
34 fixtures. Farm-on gains **+3,100 own-score points over 240 games** (89 games changed). And it
takes the panel's blocking-game count from **52 to 96**: **50 new blocked games, 6 cured**. Gate
V1 is pre-committed as go/no-go, and a single failure is a BLOCK on my own arm. **The ladder slot
is not used.** The value number is reported because the packet says to report it; under a failed
V1 it is not a result, it is a description of games that also broke.

## What was built

| artifact | what it is |
|---|---|
| `claude_1/farm/make_farm_source.py` | the generator: nine anchored replacements on `claude_1/cure3/cure3-keep-v6.rs` (the v6 emitter, sha `01b61444…`, itself generated from the champion `ad1ae4ef…`). Refuses if the parent drifts |
| `claude_1/farm/farm-v8.rs` | the one source, 4012 lines |
| `claude_1/farm/build_arms_farm.py` | the three arms from ONE flag line; each arm diffed against the source and refused unless exactly one line differs; each compiled before its hash is recorded |
| `claude_1/farm/arm-{instrument,candidate,farmoff}.rs` | `FARM`×`NARRATE` = (T,T), (T,F), (F,T). `KEEP_RULE_ENABLED` is **false** on all three (packet §7 row W3) |
| `claude_1/farm/containment_farm.py` | the 34-fixture containment read, repointed to `narrate8` |
| `claude_1/farm/farm-*-config.json` | the panel configs; corpus, seeds, mixes, turns and liveness window copied unchanged from `claude_1/cure3b/cure3b-ruleoff-config.json`, so the matched floor stays valid |
| `claude_1/farm/results/` | the fixture read, the two smoke reads, the three panel reports |

The state machine, the aim rule, the five ordered denial reasons, K = 2, the five-part latch
(`w=60, F=6, N=12, R=2.0, M=15`) and the nine-token v8 group are the packet's, unchanged. **No
latch constant was re-tuned**, on the panel corpus or anywhere else; §4 pre-committed to that and
it is kept.

## The gates, as pre-committed in §9

| gate | result | evidence |
|---|---|---|
| C1 containment | **PASS** | farm-off vs the champion: **240/240** command streams byte-identical (MSG stripped) and **34/34** fixtures byte-identical with identical referee state; `fs=0`, `fp=0` on every turn |
| V1 no new blocked game | **FAIL** | farm-off **52** blocking games, farm-on **96**. 50 new, 6 cured |
| V2 no-progress (P4/P4b differential) | **not run** — V1 already blocks the slot; running the p4b gate would spend codex_1's tool on an arm that cannot ship | the panel's own P4 fired on 5 of the new games |
| V3 W1 | **partial** — the panel's own wood-carrier invariant (I-19/I-20/I-21) fires on at least one new game (m007 seat 1), where a full carrier shuttled two cells for 9 turns without dropping | see "what W1 cannot do" below |
| L1/L2/L4 + grammar | **PASS** | `narrate8.check_telemetry` over all 240 instrument games: **0 errors**. The latch never fired, so L4 is vacuous |
| L3 no early fire | **vacuously PASS** | the latch fired in **0 of 240** games |
| instrument/candidate parity | **PASS** | the two farm-on arms are byte-identical in play on 240/240 games |

## The three numbers that matter

**1. The latch never fires.** 0 of 240 games. The packet pre-registered this exact outcome as a
*suspicion, not a pass*: "0% across 240 games is not a pass, it is a suspicion that the latch is
unreachable and L3/L4 must then be shown to be live on a constructed fixture rather than merely
unviolated." That constructed fixture has not been built, so **the latch is untested code on this
evidence**. The reason is visible in the wire: the enemy-hit counter `fe` is ~0 across the corpus
while our own ring work `fw` runs to the tens. The in-game attribution of §4.5(3) — one hit per
(turn, ring cell) where the cell's plant lost health *and an enemy troll stands on it* — may
simply never be satisfied by these opponent profiles, or may be too strict. Either way the ratio
`fe > 2·fw` cannot be reached, and a latch that cannot be reached is not a one-way latch, it is
dead code.

**2. Denial is a formality on this corpus.** Turns by state: TRAIN 19,252 · DENY 509 · FARM
28,239 · WOOD 0. Denial ended by reason `a` (no aim tree alive on the enemy's half) in **141**
games, by `b` in 2, by the turn-120 deadline `t` in 1, and never by `c` or `d`. On most panel maps
there is no enemy tree of a training species to deny at the moment the second troll appears, so
DENY is entered and left on the same turn. The denial arm of the contract is, on this evidence,
untested rather than tested-and-passed.

**3. The farm plants and harvests a great deal, and gains points.** 1,076 accepted farm plants and
1,093 accepted mother harvests over 240 games; 89 games changed; **+3,100 own-score points**, best
game +118, worst −90. The packet pre-registered a **loss** of 5–20 points a game and said: "If the
panel shows a *large* gain I will look for a containment bug before celebrating." I looked. C1 is
240/240 and the two farm-on arms are byte-identical in play, so the gain is not a containment
artefact of this harness. It is still a **local bench** number, and the contract §4 records that
the local bench overstated the 2026-08-02 farm by about 10 ladder points. It is not a verdict and
it does not buy the slot.

## Which rule broke, and on which games — the card's "dead means" answer

The 50 new blocked games, by the detector that fired (a game may fire more than one):

| detector | new games | what it means |
|---|---|---|
| D-6 `opp_harvested_ours` | 35 | **the opponent eats our farm.** We plant fruit on the ring and a harvester opponent walks in and takes it. This is the risk the owner named on 2026-08-02 — "do not create fruit the opponent can harvest before us" — and the mother-siting rule (farthest walkable diagonal from the enemy hut) does not prevent it |
| D-1 two-cell alternation | 21 | A→B→A shuttles, some of them **wood carriers**, which is W1's own subject |
| D-5 `outside_ring` | 19 | a plant landing off the ring |
| D-7 `unbanked_at_end` | 14 | a fruit taken from the shack and never returned |
| D-2 pick/drop cycling | 10 | |
| P4 / D-4 no-progress | 5 / 5 | |
| P2 | 4 | |

**D-6 is the finding.** It is not a coding slip; it is the farm's central economic risk showing up
as a referee-visible property. A ring farm next to a harvesting opponent is a feeding station, and
the design's protection against that — the latch — is the very thing that never fires, because the
latch counts **chops** and the theft here is **harvests**. Those two facts are one fact: *the
instrument was pointed at the wrong verb*. That is a design defect, not a build defect, and it is
the honest headline of this panel.

## Six build resolutions, all made after the design was accepted

The packet fixed the rule; the build had to fix things the packet did not name. Each of these is a
choice I made, each is commented at its site in the source, and each is a fair target for review.

- **BR-2** `fp` counts only PLANTs the **farm itself offered**. The first smoke read showed `fp=2`
  on a game whose state never left TRAIN: the champion's own regeneration plants land on ring
  cells, and a cell-attributed counter reported them as farm plants — that is, reported the
  owner's standing rule broken when it was not.
- **BR-3** while **no mother stands**, mothers are filled before plots. §2.2 leaves the order open;
  a scarce first seed spent on a plot is felled for 4 wood and the farm is over.
- **BR-4** a farm candidate's divisor is the **troll's occupancy**, not the wall clock. Charging
  the 24-turn growth to the troll scored every plant at ~125 against ordinary chops at ~200 and
  left the farm inert (1 accepted plant across 34 fixtures). The champion's own `chop_candidates`
  divides by occupancy; this matches it.
- **BR-6** the **mother guard**: while the farm runs, every candidate *aimed at* a living banana on
  a mother cell is removed unless the farm offered it. Removing only the `CHOP` was not enough —
  the approach MOVE carries the same target, and the troll shuttled onto the mother and back.
- **BR-7** W1's door set in **two stages**: all doors first (so the distance function does not move
  under the carrier's feet), and only if that admits nothing, the doors our other troll is not
  standing on (so a carrier is not stranded by its own partner). Each stage cures what the other
  caused; both failures are named in the source comment.
- **BR-8** the **seed guard**: a troll that took a banana on a farm offer is filtered to the farm's
  own offers until the banana leaves its carry, because the farm has no other authority over what
  the champion does with a carried fruit.

## What W1 cannot do, stated plainly

W1 filters a wood carrier's **candidate list**. It cannot bind the **emitted command**: the
champion's `resolve_move_conflicts` runs after selection and may rewrite a MOVE into a lateral or
regressive detour. On m007 seat 1 a full carrier alternated two cells for nine turns with its cargo
unchanged, and every candidate it was offered had passed the filter. Repairing that means touching
the resolver's hold logic, which the card's "Do not touch" list forbids. So V3 as written — a
statement about the **accepted** stream — cannot be made true by a filter over candidates alone.
This is a limit of the accepted design, and it should be read before any bounded repair is
chartered.

## One instrument finding, for the coordinator

The instrument arm reports **96** blocking games and the candidate arm **92**, while the two are
**byte-identical in play on 240/240 games**. Four games (`m014/0`, `m045/0`, `m054/0`, `m104/0`)
block only when the `MSG` line is present. Some panel detector is reading the payload as
gameplay. Nothing in this packet depends on those four games — the V1 failure is 50 games wide —
but a detector that sees a diagnostic line is a defect in the instrument and it should be fixed
before the next candidate is judged by it.

## Reproduce

```
python3 claude_1/farm/make_farm_source.py
python3 claude_1/farm/build_arms_farm.py
python3 claude_1/farm/containment_farm.py                      # 34/34, 0 telemetry errors
for arm in farmoff instrument candidate; do
  python3 claude_1/pipeline/fuzz_panel.py \
      --config claude_1/farm/farm-$arm-config.json \
      --report claude_1/farm/results/panel-$arm.md \
      --json   claude_1/farm/results/panel-$arm.json
done
```

## What I am asking for

Nothing is submitted. Slot 3 stays booked and unused. The card's dead condition is met — the
validity gates failed on the panel — so this goes to the owner as: **the farm works, earns on the
bench, and is not safe to put on the platform in this form**, with two specific things a bounded
repair would have to answer first: *(1)* the latch counts chops while the theft is harvests, and
*(2)* W1 cannot bind the emitted stream without the resolver, which is not mine to touch.
