# Review of the owner's score-transparency manifest — `claude_1`

- Subject: `docs/MANIFEST-score-transparency-2026-08-09.md` (`origin/main`, sha256
  `9db8e25f33aeb858db935f2b7f1424bb5c97679d0b94152c7223a6df80b233b3`)
- Governing policy: `coordination/messages/local_claude_1/20260809T160000Z-20260809-score-transparency-manifest-policy.md`
  (`origin/agent/local_claude_1`, sha256
  `469f3d1e1a59372fabc75ad5cffebfac93a9acf1b8c95382dda567d4c92c887f`)
- Author: `claude_1`, 2026-08-09.
- **Scope: review only.** No bot, candidate, parent, `.min.rs`, detector, gate, `rust/**` or
  `cgauto/**` artefact was modified. No Arena, CI or submission action. The only executions were
  `git show`, `grep`, `awk`, `sed`, `sha256sum` — all read-only.

## Independence

I did **not** read `chatgpt_1`'s review (`coordination/messages/chatgpt_1/20260809T183000Z-…`)
or anything on `origin/agent/chatgpt_1` — **skipped per instruction**. Both subagents I used were
given the same hard exclusion and both confirmed it. I did read the manifest, the policy, and my
own prior committed work, which are inputs rather than answers.

---

## 0. Provenance

Repository `/home/tarstars/prj/troll_farm-claude_1`, branch `agent/claude_1-banana-restoration-r2`
at `14b75fa4`; `origin/main` at `cf3ab04b`.

| input | sha256 |
|---|---|
| `rust/src/bin/yamo_orchard_live.rs` (dev authority, byte-sacred) | `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f` |
| `rust/src/game/engine.rs` (rules authority) | `7c240abfcfdf678993960fe73440735a19f934596c9651bdf915e2902f78fb05` |
| `cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs` (from `origin/main`) | `98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29` |
| `docs/MANIFEST-score-transparency-2026-08-09.md` (from `origin/main`) | `9db8e25f33aeb858db935f2b7f1424bb5c97679d0b94152c7223a6df80b233b3` |

Reproduce the candidate:

```
git show origin/main:cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs | sha256sum
# 98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29
```

**Citation convention.** `R:n` = line `n` of the shipped candidate `98628e98`.
`Y:n` = line `n` of `rust/src/bin/yamo_orchard_live.rs` (`fff6669b`). Where a construct exists in
both I give both, because the two files disagree and that disagreement is itself a finding (§1).

---

## 1. Before anything else: the manifest audits the wrong file

**MEASURED.** The manifest's band table and its two worked properties (a) and (b) are drawn from
`rust/src/bin/yamo_orchard_live.rs`. The bot under review, `readable__no_orchard` (`98628e98`),
is a **different artefact** with a different band table.

- The candidate's `main()` constructs `YamoBot::tuned_carry_regeneration_transit_idle_harvest()`
  (`R:1467`, preset at `R:786-795`). `yamo_orchard_live.rs`'s `main()` constructs
  `SecureOrchardBot::new()` (`Y:6016`), a wrapper that does not exist in the candidate at all
  (`grep -c SecureOrchard` on the candidate returns **0**).
- The candidate's `YamoBot` struct has **15 fields** (`R:335`); `yamo_orchard_live.rs`'s has
  ~57 (`Y:672-729`).
- Eight functions the manifest's evidence depends on are **absent from the shipped candidate**.
  `grep -c` on `98628e98` returns 0 for each of: `farmer_candidates`, `ring_chop_candidates`,
  `main_loop_candidates`, `ring_cells`, `is_ring_diagonal`, `apply_opponent_crop_priority`,
  `scarce_pick_candidates`, `scarce_farmer_candidates`, `external_orchard_candidate`.

This is not a pedantic point. It changes the verdict on both of the manifest's specific claims,
and it is *the manifest's own thesis happening to the manifest*: an intention ("audit the bot's
scoring") was recorded as a number (a line-referenced band table) that turns out to describe a
neighbouring program. I say this without any suggestion of carelessness — it is exactly the
failure mode the manifest names.

### 1.1 The manifest's property (a) is arithmetically wrong — **DISAGREE**

> "a chop is `1000 * wood / turns`, and `wood` is capped by carry capacity (≤3) while `turns` is
> floored at 1 — so the base alone reaches **3000**, and with the denial bonus **3900**."

`turns` is **not** floored at 1. `R:611` (`Y:1093`):

```rust
let turns = (travel_turns + chop_turns + return_turns + 1).max(1);
```

`chop_outcome` (`R:556-581`, `Y:1016-1049`) iterates `for turns in 1..=100` and returns on the
first iteration in which `health <= 0`, so `chop_turns >= 1`. With `travel_turns >= 0` and
`return_turns >= 0`, the expression is `>= 0 + 1 + 0 + 1 = 2`. **`turns >= 2` always, and the
`.max(1)` is dead code.**

Therefore the true bounds are:

| quantity | manifest | **measured** |
|---|---|---|
| chop base max | 3000 | **1500** (`1000·3/2`) |
| chop + denial max | 3900 | **2400** (`+900/(1+0)`, requires a tree standing on the enemy shack) |
| chop + denial, realistic (`opponent_distance >= 1`) | — | **≤ 1950** |

The manifest's conclusion from (a) — that a chop could out-rank a differently-intended action —
still stands, but not for the reason given and not at that magnitude. §3 gives the crossings that
are actually real.

### 1.2 The manifest's property (b) is false for the shipped bot — **DISAGREE**

> "`fruit_candidates(..., base_score)` and `iron_candidates(..., base_score)` take the band as a
> **parameter** … The same function therefore emits scores into different bands depending on who
> called it."

In `98628e98` each has **exactly one call site**, both inside `early_candidates`, both with
literal constants:

- `R:448` — `Self::iron_candidates(view, unit, 6_100.0)`
- `R:455` — `Self::fruit_candidates(view, unit, kind, 6_000.0)`

There is no second caller. The band-as-parameter is **latent** opacity, not actual opacity: today
the intention and the number sit four lines apart in the same function.

The claim *is* true of `yamo_orchard_live.rs`, where `MoisanBot::farmer_candidates` calls
`fruit_candidates` with base `3_400.0`/`3_000.0` (`Y:1213-1220`) as well as `early_candidates`
with `6_000.0` (`Y:895`). But `farmer_candidates` is not in the shipped lineage.

**Consequence for the owner:** the strongest single example offered for point 2 does not survive
contact with the shipped artefact. Point 2 is nevertheless correct — §3 supplies better examples,
including one that is 37× larger.

### 1.3 The manifest's band table is also incomplete for the shipped bot

The table lists 6 bands. Exhaustive enumeration of the shipped candidate (`grep -n
"score:\|score =\|score +=\|score -="` over all 1475 lines) finds **21 distinct scoring
expressions at 17 sites**. Eight bands are missing from the manifest's table entirely, including
the largest one below `20_000` (`9_000`, `R:1262`) and both halves of the conversion pricing
(`R:1292`, `R:1295`, `R:1324`, `R:1327`) — which is where the confirmed defect lives.

---

## 2. Point-by-point verdicts

### Point 1 — "the bot's logic is defined by assigning weights to actions" — **AGREE_WITH_QUALIFICATION**

It is accurate as far as it goes, and it understates the problem in a way that matters.

**MEASURED.** The weights are only half the decision procedure. Three other mechanisms determine
behaviour and carry no weight at all:

1. **Candidate-set construction.** Whole intentions are made unavailable by early `return`s
   before any weight is compared: `R:1170-1173`, `R:1185-1188`, `R:1271-1276`, `R:1277-1280`,
   `R:1282-1286`. An action that is never emitted cannot be outranked — it is *invisible*, which
   is strictly worse for debuggability than being outranked.
2. **The compatibility relation.** `compatible` (`R:643-654`, `Y:1329-1341`) is a hard constraint,
   not a weight, and it is the only thing coupling the two units' decisions.
3. **`resolve_move_conflicts`** (`R:726-778`, `Y:1440-1529`) rewrites the selected commands after
   scoring, with its own unweighted lexicographic tie-break. My prior committed analysis
   (`claude_1/banana-restoration-r2/oscillation-attack-claude_1-2026-08-09.md` §1.2) shows this
   stage alone producing a 194-turn no-op with the *scorer entirely blameless* — the goal cell was
   constant on all 200 turns.

**What specifically should change:** a bridge that maps only `score -> intention` will explain
34 of 35 oscillation episodes not at all, because 34 of them are decided after scoring ends. The
bridge must cover **admission** (which candidates exist), **weight**, and **arbitration**
(`compatible` + `resolve_move_conflicts`). If it covers only weight it will be a document that is
true and useless, which is the failure mode the manifest itself warns about (D-6).

### Point 2 — "the assignment is not transparent" — **AGREE**

Endorsed, and I can strengthen it with evidence the manifest does not have.

**MEASURED.** In §1 above, two independent readers (the owner and `local_claude_1`) produced a
band table, a worked bound and a structural claim about the code — and the bound is wrong by 2×
(§1.1), the structural claim describes a function not present in the shipped bot (§1.2), and the
table omits 8 of 14 bands (§1.3). I make no criticism: I needed four hours and exhaustive
enumeration to establish this, and my own prior document
(`oscillation-attack-claude_1-2026-08-09.md` §7.7) contains a self-correction of the same class.

That is now **three** documented incidents, not two:
`compatible`'s `Target::None` branch; the retired anti-stall watchdog; and the manifest's own
evidence. Three is a pattern, and the pattern's cause is exactly as the owner states.

**What specifically should change:** the useful conclusion is not "write a document" — the
manifest *is* a document and it drifted within a day of being written. It is that **claims about
the scorer should not be expressible except as executable assertions.** See §6.

### Point 3 — "build a bridge between the trolls' algorithms and the weighting approach" — **AGREE_WITH_QUALIFICATION**

Agreed that the artefact is needed; I disagree with the implied form, and I have to report that
**most of it already exists**. `docs/superpowers/specs/2026-07-10-intent-missions-design.md`
(status: *"DESIGN — awaiting user review … No implementation until approved"*) is this manifest,
written a month earlier for the legacy bot, with a complete intention→band table at `:47-57` and
an explicit priority ordering at `:58-61`. `rust/src/botmain/planner.rs:77-160` is the typed form
of that bridge, working, in the legacy bot. §5.1 has the full account.

The qualification is the maintainability objection the manifest itself raises, and which I think
is decisive against a prose or table form: a table of 21 expressions across two diverging files,
hand-maintained, will be wrong within a week — §1 is the proof, because the manifest's own table
already was.

### Point 4 — "build tooling to analyse, test and debug" — **AGREE**

Strongly agree, and this is my recommended first deliverable. See §5.2. The specific tool the
manifest describes ("given a game state, show every candidate action with its score, its band and
its intention") would have made every finding in §3 a ten-minute job instead of a four-hour one,
and would have caught §1's file mismatch immediately.

### Point 5 — "oscillation situation library, independent best action, compare" — **AGREE_WITH_QUALIFICATION**

Agreed on the library and on the comparison; the "independently work out the best action" clause
contains a trap the manifest does not name, and the corpus is in worse shape than the manifest
says. See §4.

### Point 6 — "intention is encoded as big steps; check the hierarchy; check sums don't cross" — **AGREE_WITH_QUALIFICATION**

This is the technical core and §3 is the audit. Summary of the verdict:

- The "big steps encode intention" reading is **correct for scores ≥ 6_000** and **false below
  it**. The scoring system is two-tier, and the manifest's model describes only the upper tier.
- The hierarchy in the upper tier is *mostly* consistent, with three specific inversions.
- Sums of sub-scores crossing intention boundaries: **I found 10 crossings, 8 MEASURED.** The
  largest is a factor of 37–961 and is not an arithmetic crossing at all — it is a *temporal*
  one. See X1.

---

## 3. The point-6 audit

### 3.1 Complete score inventory of the shipped bot (MEASURED, exhaustive)

Every score-producing expression in `98628e98`, obtained by
`grep -n "score:\|score =\|score +=\|score -=" readable.rs` and reading each hit.

| id | line(s) | value | intention as the code expresses it |
|---|---|---|---|
| S1 | `R:962`, `R:987`, `R:1059` | `20_000.0` | **UNBLOCK** — clear the unique shack door; *replaces* the unit's whole candidate list |
| S2 | `R:1283` | `10_000.0` | **COMMIT-CHOP** — endgame CHOP-in-place; *overwrites* a computed chop score and `return`s |
| S3 | `R:1262` | `9_000.0` | **REGENERATE** — PLANT a carried fruit here |
| S4 | `R:383` | `8_000.0` | **BANK** — DROP at a shack door |
| S5 | `R:1265` | `8_000.0 − dist` | **REGENERATE** — MOVE to a plantable cell |
| S6 | `R:1180` | `7_500.0 − priority` | **SEED** — PICK a fruit to carry for planting |
| S7 | `R:1292` | `7_000.0 − priority` | **CONVERT** — PICK for conversion, **turn > 250** |
| S8 | `R:386` | `7_000.0 − travel` | **BANK** — MOVE to a shack door |
| S9 | `R:394` | `7_000.0` | **BANK** — MOVE to the shack (fallback, no walkable door) |
| S10 | `R:489` | `base + 900 = 7_000.0` | **EQUIP** — MINE |
| S11 | `R:467` | `base + 900 = 6_900.0` | **EQUIP** — HARVEST |
| S12 | `R:1422` | `6_500.0` | **CLEAR-FOR-TRAIN** — MOVE off the shack |
| S13 | `R:501` | `6_100.0 − d` (**raw cells**) | **EQUIP** — MOVE toward iron |
| S14 | `R:1324` | `6_000.0 − priority − travel` | **CONVERT** — MOVE to a door, **turn > 250** |
| S15 | `R:479` | `6_000.0 − (travel + wait)` (**turns**) | **EQUIP** — MOVE toward a fruit tree |
| S16 | `R:619`, `R:622` | `1000·wood/turns + 900/(1+oppdist)` ∈ (0, **2400**] | **HARVEST-WOOD** — CHOP / MOVE to a tree |
| S17 | `R:1295` | `750/(ct+3) − priority/100` ∈ (0, **187.5**] | **CONVERT** — PICK, **turn ≤ 250** |
| S18 | `R:1327` | `750/(travel+ct+3) − priority/100` ∈ (0, **187.5**] | **CONVERT** — MOVE to a door, **turn ≤ 250** |
| S19 | `R:1365` | `1/trip` ∈ (0, **0.5**] | **IDLE-HARVEST** |
| S20 | `R:640` | `0.0` | **NOTHING** — WAIT |
| S21 | `R:1163` | `− opponent_eta_penalty · risk` | **DEAD** — `opponent_eta_penalty = 0` in the shipped preset (`R:784`), and `yamo_chop_candidates` returns early at `R:1130` |

### 3.2 The intentions, and whether the hierarchy is correct

Nine live intentions: UNBLOCK, COMMIT-CHOP, REGENERATE, BANK, SEED, CONVERT, EQUIP,
CLEAR-FOR-TRAIN, HARVEST-WOOD, IDLE-HARVEST, NOTHING.

**The structure is two-tier, and this is the central finding of the audit.**

**Upper tier, [6_000, 20_000] — the owner's reading is correct here.** Bands are separated by
≥ 100 and within-band variation is a small linear penalty (`travel`, `priority`, `dist`) that on
the corpus maps (≤ 14×6 cells, `claude_1/banana-restoration-r2/fuzz/failures/m085-s0/candidate-transcript.txt:1-6`)
never exceeds ~30. The invariant "a sum of sub-scores cannot cross into the band above" holds
**by construction** in this tier, because there are no sums — every upper-tier score is one
constant minus one penalty. This is genuinely good design and the owner should be told so: the
top of the table does what he thinks it does.

**Lower tier, (0, 2400] — the owner's reading is false here, and not by a little.** HARVEST-WOOD
(S16), CONVERT-before-turn-250 (S17/S18), IDLE-HARVEST (S19) and NOTHING (S20) share **one
continuous unbanded interval with no separator whatsoever**. Three distinct intentions are
compared by raw magnitude on three mutually incommensurable scales:

- S16 is a rate in *wood per turn*, scaled by 1000 — range (0, 2400]
- S17/S18 is a rate in *reciprocal turns*, scaled by 750 — range (0, 187.5]
- S19 is a *reciprocal trip length*, scaled by 1 — range (0, 0.5]

The scale factors 1000 / 750 / 1 have no recorded justification and differ by up to 4 orders of
magnitude. **In this tier intention is not encoded as a big step; it is not encoded at all.** The
comparison is decided by the scale factor, not by the merit of the plan.

**Three inversions in the hierarchy itself (MEASURED):**

- **H1.** CLEAR-FOR-TRAIN is `6_500` in the candidate list (S12, `R:1422`) but `20_000` as a hard
  list-replacement in the door-clearing path (S1, `R:962`/`R:987`). **The same intention is
  implemented twice with a 3× score difference and two different mechanisms.** See X7.
- **H2.** CONVERT occupies band `≈100` before turn 250 (S17/S18) and band `7_000` after (S7/S14).
  **The same intention changes tier at a hardcoded constant.** See X1.
- **H3.** IDLE-HARVEST (≤ 0.5) is ranked below the worst possible chop. A chop worth
  `1000·1/100 = 10` points on a 100-turn round trip pre-empts a 2-turn harvest worth 0.5. See X10.

### 3.3 Every place a sum of sub-scores can cross an intention boundary

Ten sites. **8 MEASURED** (traced end-to-end from source), 2 MEASURED-mechanism /
SUSPECTED-reachability.

---

#### X1 — the turn-250 band teleport — **MEASURED** — *largest crossing in the program*

`R:1291-1295` and `R:1323-1327` (`Y:3288-3292`, `Y:3323-3328`).

```rust
let conversion_score = if view.turn > 250 {
    7_000.0 - priority as f64                                   // R:1292
} else {
    750.0 / (conversion_turns + 3) as f64 - priority as f64/100. // R:1295
};
```

The **same intention** — convert a banked fruit into a planted tree at a shack door — is priced
at **≤ 187.5** on turn 250 and at **7_000 − priority** on turn 251, with the state otherwise
identical. The jump is **×37 to ×961** (`7000/187.5 = 37.3`; `7000/7.28 = 961` at the bottom of
the pre-250 range, `ct = 100`).

Consequences, both MEASURED from the table in §3.1:

- **Before turn 250**, CONVERT loses to any chop with `1000·wood/turns > 187.5`, i.e. any plan
  completing within `5.33 · wood` turns — for `wood = 3`, **any chop finishing in ≤ 15 turns**.
- **After turn 250**, CONVERT beats *every possible chop* unconditionally (7_000 > 2400) and also
  outranks BANK-by-moving (S8, `7_000 − travel`), losing only to DROP-in-place (S4, 8_000).

So the ordering of two intentions reverses completely at a hardcoded literal with no recorded
justification. The pre-250 branch is reachable — `endgame_candidates` is entered at any turn via
`committed_regeneration` (`R:1396-1398`) and via `idle_regeneration && chops.is_empty()`
(`R:1190-1192`, and `idle_regeneration = true` in the shipped preset, `R:789`) — and is
**empirically confirmed** at turn 17 in the D1-B episode
(`claude_1/banana-restoration-r2/fuzz/failures/m085-s0/`, episode `turn_start=17`).

This is the answer to the owner's point 6 in its sharpest form, and it is *not* an arithmetic
crossing. No sum of sub-scores is involved. **The boundary is crossed in time.** A hierarchy
audit that only checks arithmetic bounds would not find it.

---

#### X2 — the on-door exclusivity (the D1-B episode) — **MEASURED**

`R:1290` versus `R:1303-1304` (`Y:3284` vs `Y:3299`).

```rust
if is_adjacent(unit.cell, view.shacks[0]) && ... {   // price ONLY unit.cell   R:1290-1302
} else {
    for cell in &shack_starts { ... }                // price EVERY door        R:1303-1334
}
```

Verified in my prior committed work (`oscillation-attack-claude_1-2026-08-09.md` §1.3, m085
seat 0): standing on door `(1,4)` the unit sees only `(1,4)`, conversion 12 turns → `750/15 =
50.0`. One step off, at `(2,4)`, it also sees door `(0,5)`, conversion 6 turns → `750/12 = 62.5`.
**The same plan is worth 25 % more one step away from the door than standing on it**, and with a
competing tree candidate scoring 57.1/58.8 between the two, the unit is in a strict two-cycle.
This is a Bellman inconsistency: `V(s) < V(s')` where `s'` is a successor of `s` reached by a
null-progress step.

I confirm the brief's characterisation and add a second consequence it does not state:
**because the on-door branch prices only `unit.cell`, a unit standing on a bad door can never
see a good door.** Door comparison happens only in the off-door branch. The quality of the chosen
door is therefore determined by where the unit happened to stop.

*Correction to the brief:* the cited range `endgame_candidates ~1290-1302` is correct for the
**shipped candidate** `98628e98`, not for `yamo_orchard_live.rs`, where the same construct is at
`Y:3284-3334` and `Y:1276-1321` is a different function that does **not** contain this defect
(its endgame harvest is uniformly `6_000 − (travel + home)`, `Y:1313`, with no standing/stepping
split). The brief's `compatible ~1330-1331` reference, by contrast, is a `yamo_orchard_live.rs`
line number (`Y:1329-1341`; the candidate's is `R:643-654`). The two citations in the brief are in
two different numbering systems.

---

#### X3 — REGENERATE prices standing and stepping on different scales — **MEASURED**

`R:1261-1265` (`Y:3246-3249`): PLANT-here `9_000.0`; MOVE-to-a-plantable-cell `8_000.0 − dist`.

Same class as X2 but **safe against oscillation**: the in-place option always wins, so it cannot
two-cycle. It has a different cost. The gap between the two branches is `1_000 + dist`, while the
discrimination *between candidate cells* is only `dist`. **The code can therefore never trade one
step of travel for a better planting site** — it plants on the first legal cell it is standing on,
never on a door, never near water. Whether that is intended is unrecorded.

Sub-finding, same lines: the eligibility test at `R:1247` uses
`ceil_div(dist[cell], movement_speed)` (**turns**) while the score at `R:1265` uses `dist[cell]`
(**raw cells**). Two distance conventions, 18 lines apart, in one function.

---

#### X4 — raw cells versus turns inside the EQUIP band — **MEASURED, inert at map scale**

`R:501` prices iron as `base_score − *d` (raw BFS cells); `R:479` prices fruit as
`base_score − (travel + wait)` (turns, i.e. `ceil_div(d, speed)`). The nominal ordering is
iron-over-fruit by 100 (`6_100` vs `6_000`, `R:448`/`R:455`), but iron's penalty decays ~`speed`×
faster.

I record this as a genuine inconsistency and **explicitly not a bug**: the crossover needs
`d > 200`-ish, and the corpus maps are ≤ 14×6 (`.../m085-s0/candidate-transcript.txt:1-6`). Not
every inconsistency is a defect, and a review that reports all of them as defects is as unhelpful
as one that reports none.

---

#### X5 — the pair-sum selector trades across intention boundaries — **MEASURED mechanism, SUSPECTED reachability**

`R:683` (`Y:1379`), reached from `R:1432`:

```rust
let score = a.score + b.score;      // maximise the SUM over compatible pairs
```

The two units' decisions are chosen jointly to maximise the sum, subject only to `compatible`.
Upper-tier band *gaps* are 100–1_000; the lower-tier HARVEST-WOOD band *width* is up to 2_400.
**An optimiser maximising a sum can therefore demote unit A across an upper-tier intention
boundary (cost ≤ 1_000) in order to gain unit B an intra-chop improvement (gain up to 2_400).**
That is precisely "enough small increments outvote a higher-tier intention" — a lower-tier
*preference* outvoting an upper-tier *intention change*.

Reachability is SUSPECTED, not measured: it requires `!compatible(a.target, b.target)`, i.e. both
units naming the identical cell. **Settling evidence:** one counter in `select`, incremented when
`best_pair != (argmax_a, argmax_b)`, run over the 240-game corpus. That is a two-line
instrumentation of a scratch copy and would settle it in an afternoon.

Sub-finding, **MEASURED**: `select`'s greedy `ids.len() >= 3` branch (`R:694-711`) is **dead
code**. `can_train` returns `false` when `n >= 2` (`R:401-403`) and `TRAIN` (`R:1388`) is the only
source of units, so the bot never has more than two. A whole arbitration strategy — with different
semantics from the pair branch, since it is greedy-by-id rather than jointly optimal — has never
executed. It is exactly the kind of thing a bridge document would faithfully describe and thereby
mislead everyone.

---

#### X6 — BANK can evaporate rather than be outranked — **MEASURED mechanism, SUSPECTED reachability**

`MoisanBot::bank_candidates` (`R:371-399`) guarantees a non-empty result via the fallback at
`R:392-397`. `YamoBot::bank_candidates` (`R:947-955`) then filters out any
`Target::Bank(cell)` with `cell != unit.cell` occupied by another own unit — **after** that
guarantee — and can return **empty**.

A full unit adjacent to its own shack then falls through `R:1174-1176` and `R:1185-1187` with
nothing added, and emits `WAIT`. The BANK intention does not lose a comparison; it **disappears
before the comparison happens**, which is invisible to any tool that only inspects scores.

Mitigated for the one-door case by `force_unique_door_clear` (`R:978`, `door_unblocking = true`
in the shipped preset). **Not** mitigated when there are ≥ 2 doors and all are occupied, because
`unique_shack_door` (`R:956-959`) returns `None`. **Settling evidence:** a corpus count of turns
in which `YamoBot::bank_candidates` returns empty.

---

#### X7 — CLEAR-FOR-TRAIN is a soft candidate that six intentions outrank — **MEASURED**

`R:1419-1425` pushes a `6_500.0` MOVE. It is a *candidate*, competing on score. From §3.1, six
scores outrank it and can appear in the same list: S2 `10_000` (COMMIT-CHOP), S4 `8_000` (DROP),
S6 `7_500` (SEED-PICK), S7 `7_000` (CONVERT-PICK post-250), S10 `7_000` (MINE), S11 `6_900`
(HARVEST). Partial mitigation at `R:1416-1418` strips `PICK` candidates when
`persistent_regeneration && train_now` (true in the shipped preset), removing S6 and S7 — but not
DROP, CHOP, MINE or HARVEST.

**And the failure is silent.** `engine.rs` (`7c240abf`), the rules authority:

```rust
// Check shack is unoccupied
let shack = game.shacks[p];
if game.units.iter().any(|u| u.pos() == shack) {
    return;                                  // engine.rs:543-547
}
```

The `TRAIN` emitted at `R:1387-1389` is **discarded with no signal**. So the bot can emit `TRAIN`,
decline to clear the shack because a DROP scores 1_500 more, and never learn that the training
did not happen. This is an intention-boundary crossing whose consequence is invisible to the bot,
to the transcripts, and to every detector.

(Note also that `engine.rs:544` checks `game.units`, i.e. **all** units — an opponent standing on
our shack blocks TRAIN too, and the bot at `R:1419` only inspects its own.)

---

#### X8 — the `10_000` override discards the values it overrides — **MEASURED**

`R:1282-1286` (`Y:3271-3279`):

```rust
if let Some(mut current) = chops.iter().find(|c| c.command == format!("CHOP {}", unit.id)).cloned() {
    current.score = 10_000.0;
    out.push(current);
    return out;                 // <- discards every other candidate
}
```

Once a unit stands on *any* choppable tree in the endgame, its entire decision becomes "keep
chopping", discarding all conversion candidates, all other chops, and the `WAIT`. The tree's own
computed value is overwritten and thrown away, so a 12-turn tree and a 2-turn tree are identical.

I flag this as **correct under the manifest's model and questionable under the game's**: it is a
big step encoding an intention, exactly as the owner describes — and it is an intention with no
exit condition. It deserves an explicit owner decision rather than a bug report.

---

#### X9 — `Target::None` disables the only cross-unit constraint — **MEASURED**

`R:640` (`Y:1325-1327`) and `R:643-646` (`Y:1329-1332`). `wait()` is the sole `Target::None`
producer, and `compatible` returns `true` unconditionally when either side is `None`.

The known consequence (an idle unit is invisible to pair-compatibility while remaining a physical
obstacle) is established in `oscillation-attack-claude_1-2026-08-09.md` §1.4(b), where `m014`
seat 1 unit 0 stands on the target banana emitting `WAIT` for 195 turns while unit 2 orbits it.
I confirm it and restate it as a **scoring** defect: `compatible` is the only mechanism that makes
X5's pair-sum a *constrained* rather than a free optimisation. When one unit is idle, that
constraint vanishes entirely — so X5's crossing is *most* available exactly when one unit has no
intention to protect.

---

#### X10 — IDLE-HARVEST is four orders of magnitude below its competitor — **MEASURED**

`R:1365` scores idle harvest `1.0/trip` ∈ (0, 0.5]; `R:619` scores chop up to 2400. Both are
`Target::Tree`. The guard at `R:1413` admits idle-harvest only when every candidate is
`Target::None`, so it is unreachable whenever *any* chop exists — including a chop worth 10 points
on a 100-turn round trip, which pre-empts a 2-turn harvest worth 0.5.

The scale factors (1000, 750, 1) are the entire content of this ordering. Nothing about the
game's economy is expressed by them.

---

### 3.4 Summary of §3

| | count |
|---|---|
| distinct scoring expressions in the shipped bot | **21**, at 17 sites |
| live intentions | **11** |
| intention-boundary crossings / inconsistencies found | **10** |
| of which **MEASURED** end-to-end | **8** (X1, X2, X3, X4, X7, X8, X9, X10) |
| MEASURED mechanism, SUSPECTED reachability | **2** (X5, X6) |
| hierarchy inversions | **3** (H1 = X7, H2 = X1, H3 = X10) |
| dead scoring code found | **3** (`.max(1)` at `R:611`; `select`'s ≥3-unit branch `R:694-711`; the eta penalty `R:1163`) |

**Answer to the owner's question "is the hierarchy correct?":** in the upper tier, yes, with three
inversions. In the lower tier there is no hierarchy to be correct — and the one intention that
lives in *both* tiers (CONVERT) moves between them on turn 250. That is where I would look first.

---

## 4. Point 5 — the oscillation situation library

### 4.1 What the corpus already gives us for free (MEASURED)

`local_claude_1/verification/readable-no-orchard-oscillation-2026-08-08.json` (on `origin/main`,
sha256 `b42fb8a7ae2c26af7e52dd18128a04bf221a794fbffe52e63d57b47122332e69`, recomputed here rather
than copied). Verified counts:

```
git show origin/main:local_claude_1/verification/readable-no-orchard-oscillation-2026-08-08.json \
  | jq '[.games[].violations[] | select(.detector=="D-1") | .episodes[]] | length'
# 34
```

- **34 episodes / 32 games / 240 games total.** The manifest's figure is exactly right.
- Episode schema is **5 fields**: `cells, k, turn_end, turn_start, unit`. Map, seat, seed, class,
  profile and attempt come from the enclosing game object.
- **Deterministic regeneration is free.** `claude_1/pipeline/fuzz_panel.py:398-450`
  (`build_skeleton`) derives every draw from `base = seeds[map_index % len(seeds)]` and
  `rng = random.Random(base*1_000_003 + map_index*8191 + attempt*7919)`. Since
  `(map_id, seed, attempt, class, profile, seat)` is on every record, **each episode's initial
  state can be regenerated exactly, today, with no new artefact.** This is the single most
  valuable thing the project already owns for point 5 and it is not mentioned in the manifest.
- **22 of the 32 D-1 games already have full transcripts** under
  `claude_1/banana-restoration-r2/fuzz/failures/<mapid>-s<seat>/` (130 dirs, 6 files each:
  `candidate-transcript.txt`, `candidate-commands.txt`, `parent-*`, `detectors.json`,
  `properties.json`). D1-B (`m085-s0`) is among them, and its `candidate-commands.txt:17-22` shows
  the alternation directly.

### 4.2 Two problems the manifest does not mention

**(a) MEASURED — the committed corpus is stale.** It was produced by the **pre-repair** referee,
in which `TRAIN` and `MINE` were silently discarded. Under the repaired referee the same candidate
on the same seeds gives **35 episodes / 33 games**, not 34/32
(`oscillation-attack-claude_1-2026-08-09.md` §0). The 35th is a genuine two-worker case (`m040`
seat 1, turns 80-86) that the pre-repair fiction was masking. **Building a frozen library on the
34-episode corpus would freeze a referee bug into the library.** The rerun result is scratch-only
and was deliberately not committed; re-running it is the first step of item C, not an optional
extra.

**(b) MEASURED — the saved transcripts are from a different candidate.**
`claude_1/pipeline/fuzz-panel-config.json` declares candidate `eac2eb36…` and parent `a8eb3b2b…`,
**not** `98628e98`. They are usable as geometry but not as a record of what `readable__no_orchard`
did.

### 4.3 The circularity trap, named

The manifest says "independently work out the best course of action". **The trap is that the only
existing machinery for evaluating a plan is the scorer under audit.** Any "oracle" built by
calling `chop_candidates`, `conversion_chop_turns` or `predict_tree` and taking an argmax is
**not independent** — it inherits every one of the ten crossings in §3, and it will certify X1 and
X2 as correct because it computes them the same way. That failure would be indistinguishable from
success and would be exactly this week's recurring defect (the manifest's own words: "several of
this week's failures were instruments that measured something other than what they claimed").

**The good news: the project already owns two genuinely independent oracles and is not using
either for this.**

1. **`rust/src/etudes/oracle.rs`** (309 lines) — MEASURED independent. Its entire import list
   (`oracle.rs:26-32`) is `std::collections::HashMap`, `crate::game::engine`,
   `crate::game::state::GameState`, `super::actions::joint_actions`, `super::situation::Situation`.
   `grep -rn "botmain\|resident_policy\|strategies::\|moisan" rust/src/etudes/` returns **zero
   matches**. It is a sound informed-minimax over the real engine, valuing positions by
   `scores[X] − scores[Y]` at a horizon, with `NODE_BUDGET = 100_000` (`oracle.rs:47`) and a
   `replay_proof` re-check (`oracle.rs:279`). Its envelope is ~1 troll per side, small maps,
   horizon 5–20 — which is *smaller* than a real episode but **larger than what most D-1 episodes
   need**, since 20/20 terminal episodes have a peer that never moves at all.
   Companion: `rust/src/etudes/situation.rs:30 from_text` — a text state format with a round-trip
   test (`rust/tests/etudes.rs:6`) and a CLI renderer (`rust/src/bin/etude.rs`).
2. **`claude_1/banana-restoration-r2/conversion_race_oracle.py`** — reimplements the game
   arithmetic in Python from the spec (`predict_tree` `:107`, `exact_chop_turns` `:124`,
   `first_fruit_delay` `:144`) and answers decision questions (`:160`, `:282`, `:385`) without
   calling the bot. Self-test at `:442`.

Neither is cited in the manifest. Both are the shape point 5 needs.

**And a standing policy conflicts with point 5, which the owner should be told explicitly.**
Decision **D161** (`docs/evidence/generated/decision-evidence-index.yaml`) requires that
*"Experiments must anchor on the exact resident, or first prove same-panel dominance over it."*
That policy is a large part of why every artefact in this repository named "oracle", "teacher" or
"counterfactual" — `bundle_job_oracle.rs:505`, `d35b`, `d67`, `d112`, `d172a`,
`resident_residual_mc_teacher` — is resident-anchored by construction (each MEASURED to import
`SecureOrchardBot` or `rl_macro`). **Point 5 as written asks for something D161 currently
forbids.** That is an owner decision, not an agent decision, and it should be made before item C
is scheduled rather than discovered halfway through it.

### 4.4 What the library should actually contain, and what "best action" can honestly mean

Per episode: `(map_id, seat, seed, attempt, class, profile)` — sufficient for exact regeneration —
plus the frozen `GameState` at `turn_start`, the shipped bot's full candidate list with scores at
each turn of the window, and the commands actually issued.

For "the best action", I recommend **not** attempting a global optimum. It is unobtainable: the
game is two-player, 300 turns, with an opponent policy we do not control. Attempting it will
produce either a search that silently reuses the scorer, or a months-long project.

Instead, three tractable and genuinely independent oracles, in ascending cost:

1. **A dominance oracle (cheapest, and sufficient for X1/X2).** It does not name the best action.
   It asserts *relational* properties that need no value function: (i) `V(s) >= V(s')` when `s'`
   is a successor of `s` reached by a null-progress step (this alone falsifies X2 and any future
   instance of its class); (ii) the same intention scores in the same band on turn `t` and `t+1`
   absent a state change (this falsifies X1). **These are checkable against the existing corpus
   today and need no oracle at all** — only the candidate lists, which is tooling item B.
2. **A single-unit reachability oracle** (a bounded exhaustive search over one unit's actions in a
   frozen world with the opponent held still), built on `conversion_race_oracle.py`'s arithmetic,
   not the bot's. Answers "was there a strictly better plan for this unit?" — which is all that
   34 of 35 episodes require, since in 20/20 terminal episodes the peer never moves at all
   (`oscillation-attack-claude_1-2026-08-09.md` §1.5).
3. **A human-adjudicated ground truth for the ~5 shapes**, recorded once. Three mechanisms
   (M1/M2/M3) plus the two-worker case cover all 35 episodes; adjudicating five representatives is
   a day's work, adjudicating 35 is a week's, and the 35 are not independent.

**Verdict on point 5:** the library is worth building; the "independent best action" clause is
worth **weakening** to a dominance oracle for the first pass. I would say plainly to the owner:
the strong reading of point 5 is the most expensive item in the manifest and the one most likely
to produce a confident wrong answer.

### 4.5 Is item C worth doing before the measurement apparatus is repaired?

**Partly, and the split matters.** Freezing situations does not depend on the panel — it depends
on `build_skeleton` determinism, which is independent of the gate. *Comparing* against a
correctness standard does depend on the referee being right, and §4.2(a) shows the current corpus
was built on a referee that dropped `TRAIN` and `MINE`. So: **freeze and regenerate now; defer the
comparison until after the corpus rerun.** Doing them in the other order bakes in a known-stale
instrument.

---

## 5. Points 3 and 4 — what a bridge and tooling should concretely be

### 5.1 The bridge

**First, the thing the owner most needs to know: this bridge has already been designed, approved
in shape, and never built.**

`docs/superpowers/specs/2026-07-10-intent-missions-design.md` (MEASURED) is the manifest, written
a month earlier, for the *other* bot. Its motivation section states the owner's present complaint
verbatim:

> "The current decision layer (`planner::assign_resolved`) is **soft/emergent**: every action is a
> weighted candidate (band × 100_000 + tiny within-band adjustments) and a per-turn joint argmax
> picks winners. Nobody *decides*; behavior emerges from weight comparisons, and every fix is
> another weight tweak."

`:47-57` is a complete intention→band table (`Bank` ← 95, 80; `TrainTroll` ← 65/64/62/60/58;
`FellForWood` ← 72/70, 42/40, 31/30; `BuildRing` ← 88, 78/77, 52/50/49; `HarvestFruit` ← 75, 62,
38; `Idle` ← 10) and `:58-61` is an explicit priority ordering — *"replaces band VALUES with
readable policy … no magic numbers"*. Status line 3: **"DESIGN — awaiting user review … No
implementation until approved."**

Moreover, a partial bridge already **exists in code** for the legacy lineage:
`rust/src/botmain/planner.rs` has `enum Kind` (`:77-87`) with a doc comment naming each band,
`const BAND: i64 = 100_000` (`:33`), `fn value_band` (`:137`) reverse-mapping a value to its band,
and `fn claim_info` (`:149-160`) switching on band numbers to a semantic claim class. **That is
the typed bridge, working, in the other bot.**

And an existing document already maps the *resident's* score flow with line citations:
`data/analysis/live-agent-6553250/l3-learned-evaluator-scope-audit-result-2026-07-31.md:22-52`
enumerates the magnitudes `0 / 6,000 / 6,100 / 7,000 / 8,000 / 10,000 / 20,000` against
generator, filter, selector and rewrite line ranges. **What it lacks is names** — it says "band
6,000" and never "band 6,000 = fund the second troll". That naming is the actual gap.

So the honest statement of point 3 is not "build a bridge". It is: **the bridge exists in design
for the intention layer, in code for the legacy bot, and in line-citations for the resident. What
has never existed is the resident's `enum Intention`.** Three-quarters of item A is already
written, in three files that were never joined. This is the clearest instance of the pattern the
brief warns about, and it is worth more to the owner than any new artefact I could propose.

With that said — the manifest leaves the form open ("a table, a typed wrapper, named constants, a
specification"). I argue for exactly one of these and against the others, on the manifest's own
maintainability criterion.

**Against a table or specification document.** §1 is the empirical case: the manifest's own band
table drifted from the shipped artefact *before the review began*. The project has the D-6
precedent (a predicate enforced after its design document retired it, with tests that encode the
retired predicate). A prose bridge would be a third instance.

**For a typed wrapper — but only if it is load-bearing.** Concretely: replace `score: f64` on
`Candidate` (`R:319`) with `(intention: Intention, rank: f64)`, where `Intention` is an enum with
a total order, and comparison is lexicographic — intention first, rank second. Then:

- the intention is at the construction site, in the same expression as the number (point 2 solved
  structurally, not documentarily);
- **X1, X7, X10 and H1–H3 become type errors or explicit, greppable `Intention` choices** rather
  than invisible arithmetic;
- "a sum of sub-scores cannot cross an intention boundary" stops being a property to audit and
  becomes a property the type system enforces, since `rank` is only ever compared *within* an
  intention;
- a bridge that drifts from the code becomes impossible, because it *is* the code.

**This is a substantial behavioural change and I am not proposing it be done now.** It would alter
selection wherever two intentions currently interleave numerically — which, per §3.2, is the whole
lower tier. It needs the tooling (5.2) and the fixtures first, so the delta can be measured. I
name it because it is the only form of bridge I believe survives contact with this repository, and
because the owner should know that the cheap forms have already failed here twice.

**The honest interim:** derive the table mechanically rather than writing it. A ~40-line script
that greps every `score:`/`score =` site and emits the §3.1 table, run in CI, with a test that
fails when a new scoring site appears without a mapping entry. That cannot drift silently. It is
the smallest artefact that satisfies the manifest's success test ("the owner can state a troll's
logic and an agent can confirm or refute it by pointing at the bridge").

### 5.2 The tooling

The manifest's minimum specification is right and I would not expand it: *given a game state, show
every candidate action with its score, its band and its intention; given a decision, explain why
this action beat the alternatives.*

**This tool already exists. It was built, it works, and it was closed for a reason that does not
apply to a debugging tool.** (MEASURED — this is the single most important finding in §5.)

`cgauto/n4_candidate_pair_value_audit.py` (239 lines) plus the base85+zlib payload in
`rust/src/bin/n4_candidate_pair_surface.rs`. `instrument_resident()` (`:37`) applies six
`replace_once` patches (`:46, :48, :50, :56, :66, :91`) to a **copy** of the byte-sacred resident,
each asserting exactly one anchor so it fails loudly on drift. The injected probe types are
precisely the manifest's item B:

```rust
pub struct N4CandidateProbe { unit_id, index, command, score, target_kind, target_cell,
                              route_distance, predicted_size, predicted_health,
                              predicted_cooldown, fell_turns, fell_size, opponent_crop_target }
pub struct N4PairProbe     { index, first_index, second_index, score, commands }
pub struct N4Probe         { turn, candidates, pairs, selected_pre, selected_final }
```

That is: every candidate with its score and target; **every compatible pair with its joint score**
(which is X5, directly observable); the raw argmax winner *and* the post-rewrite winner separately;
plus an `n4_force_pair(&mut self, commands)` counterfactual hook that lets any pair be forced and
replayed. It is a better tool than the manifest asks for.

**Why it was shelved, and why that reason does not bind here.** MEASURED,
`data/analysis/live-agent-6553250/n4-candidate-pair-value-phase-a-result.json`:
`"verdict": "RUNTIME_CLOSE"`, `"phase_b_authorized": false`, with
`single_thread_p95_ms = 210.4` against a 5 ms per-turn arena latency gate and
`projected_full_bytes ≈ 10.7 GB` across 2,048 games. **It was killed on latency and volume for a
2,048-game census.** An offline tool inspecting *one* state has no 5 ms budget and emits kilobytes.
The implementation lock
(`data/analysis/live-agent-6553250/n4-candidate-pair-value-phase-a-implementation-lock.json`)
records `sacred_resident_sha256: fff6669b…`, which **still matches today** — so the patches still
bind, unmodified.

Two further lines of work (L2, L3) are recorded as "CLOSED BY N4 RUNTIME" in
`docs/APPROACH-REGISTER-2026-07-30.md:80-81`. **Three workstreams died downstream of a latency
verdict on a census, not a capability verdict on the instrument.** Reviving N4 as an offline
single-state tool reopens all three at near-zero cost.

**What exists and should be reused (MEASURED):**

- `cgauto/n4_candidate_pair_value_audit.py` — the candidate/pair dumper and counterfactual hook.
  **Do not rebuild this.**
- `rust/src/etudes/situation.rs:30 from_text` + `rust/src/bin/etude.rs` — a text state format with
  a round-trip test and an ASCII board/entity renderer. The ready-made front end.

- `claude_1/pipeline/fuzz_panel.py` — `build_skeleton` (`:398-450`), `materialize`, `make_referee`.
  Deterministic state construction from `(seed, map_index, attempt)`. **This is the state loader;
  do not write another one.**
- `claude_1/banana-restoration-r2/regression_tests.py` — `run_binary_custom`, closed-loop binary
  driving.
- `claude_1/banana-restoration-r2/trace_detectors.py` — `build_trace`, `detect_d1`.
- `claude_1/banana-restoration-r2/make_banana_traces.py` — frozen literal fixtures.
- `claude_1/banana-restoration-r2/conversion_race_oracle.py` — the independent-oracle template
  (§4.3).
- `rust/src/game/engine.rs` (`7c240abf`) — the rules authority.

**What is genuinely missing:** the wiring, not the parts. Specifically:

1. **A single-state CLI front end.** N4's shipped runner is a 128-map × 8-family × 2-seat census
   emitting percent-encoded TSV — not `explain(state) -> table`. Needed:
   `explain <situation.txt>` → every candidate (unit, command, score, band, target, intention),
   every compatible pair with its joint score, the winner, its margin over the runner-up, and
   which post-selection rewrite changed it. Ingredients: `etude.rs`'s loader/renderer + N4's probe.
2. **Named bands for the resident** — the `enum Intention` of §5.1. §3.1 of this document is that
   table, derived; nobody has put it in the code.
3. **A shared `game::GameState -> yamo::game::GameState` adapter.** It is currently copy-pasted
   per binary (`control_view` in the N4 runner payload; `yamo_view` in
   `rust/src/bin/bundle_job_oracle.rs`). A live rediscovery vector.

**Note on why instrumentation, not a runtime flag:**
`grep -c "eprintln\|env::var" rust/src/bin/yamo_orchard_live.rs` returns **0** — the resident has
no debug hook in 6,024 lines. Patching a copy is the only route in, which is exactly what N4 does.
My prior work independently validated the technique on this lineage: adding two `eprintln!`s to a
scratch copy of `98628e98` produced **byte-identical** command streams against the unmodified
binary on eight control games (`oscillation-attack-claude_1-2026-08-09.md` §0, E2).

The gap between "we have no candidate visibility" and "we have it" is therefore a front end over
an existing, still-valid instrumenter. I estimate well under a day, and it is the item I would do
first (§7).

---

## 6. Risks, costs, and what I advise against

**Advise against — 1: writing the bridge as a document.** §1 and D-6 are two independent
demonstrations that this repository cannot keep prose synchronised with code. A wrong bridge is
worse than none because it will be cited. If a table is written, generate it.

**Advise against — 2: building the point-5 oracle out of the bot's own functions.** §4.3. This is
the highest-probability failure in the manifest: it would look like success, and it would certify
X1 and X2 as correct. If anyone proposes an oracle, the first question must be "which of
`chop_candidates`, `predict_tree`, `conversion_chop_turns` does it call?" and the acceptable
answer is "none".

**Advise against — 3: freezing the situation library on the committed 34-episode corpus.**
§4.2(a). Re-run first.

**Advise against — 4: acting on the manifest's band table.** §1.1–1.3. Three of its statements are
wrong or inapplicable to the shipped bot. Use §3.1.

**Advise against — 5: fixing X1 (the turn-250 teleport) without an owner decision.** It is the
largest crossing I found and it is *also* plausibly deliberate — "in the last 50 turns, convert
everything" is a legitimate endgame policy. The defect is that the policy is expressed as a magic
number inside a scoring formula with no recorded rationale, not necessarily that the policy is
wrong. This needs the owner, not an agent.

**Advise against — 6: building any new instrument before checking N4 and D161.** Two concrete
traps, both MEASURED in §4.3 and §5.2: item B has already been built and closed on a verdict that
does not apply (`RUNTIME_CLOSE`, a latency limit on a 2,048-game census); and item C's independence
requirement is currently forbidden by decision D161, which mandates resident anchoring. Each is a
week of work that would end in rediscovery or in a policy collision.

**Cost and risk of the four deliverables:**

| item | cost | main risk |
|---|---|---|
| B (tooling) | **< 1 day** — a front end over N4, which already exists and still binds | none material; instrumentation validated byte-identical on this lineage |
| D (hierarchy audit) | done — this document | that it is not acted on |
| A (bridge, generated form) | ~1 day, given §5.1's three existing sources | drift, mitigated by generating it |
| A (bridge, typed form) | large | behavioural change to a byte-sacred lineage; needs B first |
| C (situation library) | days; **weeks** under the strong reading of point 5 | circular oracle (§4.3); stale corpus (§4.2); **collision with decision D161** |

**One risk the manifest does not name.** Every finding in §3 is about `98628e98`, which is
`disposition: displaced_superseded` in `data/analysis/arena-submission-history.json` — it is not
the live bot. The live lineage (`e7a-r36-simplified`) has a *further-simplified* `YamoBot` with
9 fields against the candidate's 15. **A bridge and an audit built on `98628e98` may not transfer.**
Before item A is scheduled, someone should check which of X1–X10 survive in the live bot. I did not
do this — it was outside the brief — and I flag it as the highest-value cheap follow-up.

---

## 7. The question the policy most wants answered

> "Four substantial deliverables. Which single one, done first, would have prevented the most of
> this week's wasted effort?"

**B — the tooling. Specifically: revive N4 as an offline single-state `explain` tool.** Not the
bridge.

And note what that answer really says. Item B is not a build; it is a **~1-day front end over an
instrumenter that already exists and whose anchors still bind** (§5.2). The most expensive of the
four deliverables to *start* is the cheapest to *finish*, and nobody knew that, because the thing
was filed under a latency verdict from a different task.

The argument is evidential rather than a preference:

- The `compatible`/`Target::None` incident (two competent readers, opposite conclusions, twelve
  lines) was settled by *observing behaviour*, not by reading. A bridge document describing
  `compatible` would have been written by the same reader who misread it.
- D1-B was `UNRESOLVED — not localised` for a week and was closed the moment someone printed the
  candidate list. That is the entire causal story.
- The retired-watchdog error was settled by reading, and a bridge would not have covered it — the
  watchdog is not a scoring site.
- §1 of this review — the manifest's table describing the wrong file — would have been caught in
  minutes by a tool that prints the *actual* bot's *actual* candidates, and was otherwise caught
  only by four hours of enumeration.
- **Every other deliverable depends on it.** The bridge needs it to be verified against reality.
  The situation library needs it to record what the scorer chose. The hierarchy audit needs it to
  turn X5 and X6 from SUSPECTED into MEASURED — and N4's `N4PairProbe.score` field makes X5
  directly observable with no new code at all.
- **Three shelved workstreams reopen with it.** N4 itself, plus L2 and L3, both recorded as
  "CLOSED BY N4 RUNTIME" (`docs/APPROACH-REGISTER-2026-07-30.md:80-81`).

It is also the cheapest item in the manifest by an order of magnitude, and the only one that is
purely additive — no behaviour change, no gate interaction, and validated byte-identical on this
exact lineage.

**Second priority: the dominance oracle of §4.4(1)**, which needs only the candidate lists that B
produces and would have caught X1 and X2 automatically. Third: the generated bridge (§5.1). The
situation library under the strong reading of point 5 should be scheduled last, and scoped down.

---

## 8. Verdict table

| point | verdict | the concrete consequence |
|---|---|---|
| 1 — logic is weights | **AGREE_WITH_QUALIFICATION** | weights are ~1/3 of the decision; a weight-only bridge explains 1 of 35 oscillation episodes |
| 2 — not transparent | **AGREE** | third documented incident is the manifest itself (§1); the fix is executable assertions, not documents |
| 3 — bridge | **AGREE_WITH_QUALIFICATION** | ~3/4 already written across three unjoined files (§5.1); the real gap is the resident's `enum Intention`. Generate it or make it a type; do not write prose |
| 4 — tooling | **AGREE** | the tool already exists (N4) and was closed on a latency verdict that does not apply offline. Revive it. Do this first |
| 5 — situation library | **AGREE_WITH_QUALIFICATION** | corpus is stale (34 vs 35), transcripts are from another candidate, and the independence clause collides with decision D161; weaken "best action" to a dominance oracle |
| 6 — hierarchy / crossings | **AGREE_WITH_QUALIFICATION** | correct above 6_000, absent below it; 10 crossings, 8 MEASURED; largest is temporal, not arithmetic |
| manifest property (a) — chop reaches 3000/3900 | **DISAGREE** | `turns >= 2`; true maxima are 1500/2400 (`R:611`) |
| manifest property (b) — band set by caller | **DISAGREE** | one call site each in the shipped bot (`R:448`, `R:455`) |

### Open / unresolved

- **UNRESOLVED** — whether X5 and X6 actually fire in play. Settling evidence in each entry
  (§3.3); both are one-counter instrumentations of a scratch build.
- **UNRESOLVED** — whether X1–X10 survive into the live lineage (`e7a-r36-simplified`,
  `2caac7c6`). Settling evidence: the same enumeration of §3.1 run against
  `claude_1/readable-source/e7a-r36-readable.rs`. I did not do this; it was outside the brief.
- **UNRESOLVED** — whether the turn-250 constant in X1 is deliberate. No design record exists.
  Only the owner can settle it.
- **UNRESOLVED (owner decision, not evidence)** — whether decision D161's resident-anchoring
  requirement is waived for item C. Point 5's independence clause cannot be satisfied while it
  stands (§4.3).
- **UNRESOLVED (owner decision)** — whether
  `docs/superpowers/specs/2026-07-10-intent-missions-design.md` is revived, superseded, or
  formally retired. It has sat at "awaiting user review" for a month while the same problem was
  re-stated in a new manifest. Leaving it in that state is how the D-6 class of defect is created.
