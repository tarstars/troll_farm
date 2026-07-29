# chatgpt_1: champion fruit-valuation analysis

Date: 2026-07-29
Agent: `chatgpt_1`
Status: analysis complete; implementation unclaimed

## Correction

The earlier `chatgpt_1` audit inspected stale `main` (`v0.6.1`). The active competitive codebase is branch `session-2026-07-01`, which contains the Rust bot, frozen submissions, arena history, and coordination documents.

The repository-authoritative current champion/default is **`v1.59.0-ringfix3`**:

- `rust/src/botmain.rs` declares `VERSION = "1.59.0-ringfix3"`.
- `cgauto/api_submit.py` defaults to `cgauto/submissions/v1.59.0-ringfix3.min.rs`.
- `data/candidates/v1.61.0-chopharvest/brief.md` explicitly names `v1.59.0-ringfix3` as its champion base, so `v1.61` is a candidate rather than the default champion.

## User observation

The champion implements plant-chop-drop well, but may miss opponent-effective fruit collection in the opening and middle game. The suspected cause is fruit being underweighted.

This observation is supported, with one refinement: the main problem is not a single scalar fruit coefficient. The planner uses large lexicographic priority bands, so lower-band fruit work cannot beat higher-band PCD/funding/chop work regardless of travel efficiency or immediate fruit count.

## Current priority structure

Approximate relevant bands in `v1.59.0-ringfix3`:

| Action | Band |
|---|---:|
| Plant carried banana | 88 |
| Full load -> bank | 80 |
| Build incomplete PCD ring: PICK / park-to-PICK | 78 / 77 |
| Standing selected harvest | 75 |
| Chopper fell | 72 / 70 |
| Chopper/ladder funding | 58-65 |
| Banana or water-apple seed forage | 52 |
| Starter chop help | 42 / 40 |
| Generic ripe-fruit collection | **38** |
| Emergency chop | 31 / 30 |

`BAND = 100_000`, while ETA corrections are small. Therefore generic fruit at band 38 is effectively an idle fallback, not an economic competitor.

During incomplete ring construction the source comment explicitly states that build-ring PICK suppresses distant foraging. Thus a nearby multi-fruit tree, or one the opponent will collect first, can still lose to a ring errand.

## Additional implementation gaps

### 1. Broad high-value fruit mode is inactive

The planner has an all-ripe-fruit band 62 in `Phase::Hoard`, but the live champion fixes `GE_META = Tempo`. Tempo never enters Hoard, so that band is inactive in normal champion play.

### 2. Standing harvest is selective

Band-75 standing harvest is enabled mainly for:

- current training deficits;
- banana or water-adjacent apple under specific gates;
- Hoard phase.

Other ripe fruit underfoot relies on the generic band-38 path and may lose to remote higher-band tasks.

### 3. Fruit races against opponent harvesters are not valued

The existing `race()` helper models only an enemy **chopper already standing on the tree** and asks whether the tree will be felled before our arrival.

It does not estimate:

- nearest enemy harvester ETA;
- fruit remaining when each side arrives;
- harvest-power/capacity interaction;
- opponent score denied by collecting first;
- opponent training resources denied by collecting plum/lemon/apple first.

The generic fruit candidate uses the chop-race helper only to avoid chasing a tree that will disappear. This is not an opponent-effective fruit race model.

## Evidence against a blanket fruit-band increase

Several earlier arena experiments show that globally promoting fruit can damage the tight PCD machine:

- `v1.24.0-fruitbank`: starter chased fruit instead of chop-helping; approximately -1.0 arena score.
- `v1.37.0-nanaflow`: tree-first banana plus placement bundle; approximately -3.2 to -3.3.
- `v1.44.0-harvest-before-fell`: approximately -2.6.

Therefore the proposed change should not simply raise all fruit above chopping or ring work.

## Recommended isolated hypothesis: competitive fruit

Add a new **competitive-fruit** candidate, separate from generic idle-fruit.

Conceptual value:

```text
competitive_value =
    our_bankable_fruit
  + opponent_fruit_denied
  + training_shadow_value
  - interrupted_PCD_value
```

Normalize by occupied turns:

```text
travel + harvest + return-to-bank
```

A minimal first experiment can stay within the existing band planner:

1. Keep ordinary uncontested fruit at band 38.
2. Add a conditional competitive-fruit band around 79, so it may beat ring PICK 78 but not full banking 80 or planting 88.
3. Offer it only when all of the following hold:
   - fruit is ripe now;
   - we arrive strictly before the nearest enemy harvest-capable troll;
   - expected collectible fruit is at least 2, or the fruit closes an immediate training deficit;
   - the load can be banked before endgame;
   - the tree is not doomed to an enemy chop before arrival.
4. Include opponent-denial value, especially for plum/lemon/apple that fund opponent training.
5. Preserve existing PCD priority for uncontested one-fruit errands.

This directly tests the user's hypothesis while avoiding the known fruitbank/nanaflow failure mode.

## Measurements

Do not judge by wood alone. Record at turns 75, 150, 225, and 300:

- our fruit banked by type;
- opponent fruit banked by type;
- fruit denial swing;
- wood for both sides;
- ring completion turn and ring occupancy;
- count of competitive-fruit tasks that displaced ring/PICK/chop-help work;
- total score margin;
- arena delta against the frozen champion.

Use paired field opponents that previously out-fruited the bot; Boss-only gates are insufficient for this hypothesis.

## Coordination

No implementation files are claimed by `chatgpt_1` in this note. Another agent may claim the competitive-fruit experiment, but should announce the claimed version/files before editing. The frozen champion artifact must remain untouched.