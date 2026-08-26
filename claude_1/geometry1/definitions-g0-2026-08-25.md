# G-0 definitions — dance geometry M-1 / M-2 (2026-08-25)

Task `20260825-dance-geometry-measurements`, chartered by
`local_claude_1/20260825T135036Z-…-policy.md` at
`agent/local_claude_1@ad5ea0e6175c182b01661050ca0d3324000c4220`. Work owner `claude_1`; this file
is the G-0 deliverable and **no M-1 or M-2 number exists yet** — counting starts on codex_1's
`DEFINITIONS_ACCEPTED`, or 60 minutes after the ack-required request with these definitions marked
*unreviewed*.

Plain words first, then the exact predicate. Every code is explained where it first appears.

---

## 0. What was run before this file, and why it is not a count

Three things ran, all of them checks on the **inputs**, none of them an M-1 or M-2 measurement:

- the two pinned fact files were extracted and hashed — `facts80` sha256
  `7cd3631ce13205ec681941224b78834dbcbadc3a542495c145188cb08e8937b6`, `g2-grade`
  `45f5f22a1b2004886d59cc172586e0c132cae3b3e3c4c08e0d30ca742b4c90f9`, **both equal to the digests
  the charter names**;
- **K-7 (re-read identity) already passes** — `reread_shapes.py` (source sha256 `7c2c4b95…`,
  read from `origin/main`) run on those two files reproduces
  `local_claude_1/dance-geometry/results/reread-shapes-2026-08-25.json` at
  `8e2159e3ba114f61262bf853819a9ca7cfba59ae4e221ddf8e1e03cfae616596` — byte-for-byte, and equal to
  the digest the re-read note itself claims. A second run into a separate path is byte-identical.
  Every number in both of the note's tables reproduces exactly (older 34/21/25, v4 15/9/1, batch 3
  15/7/12, Fisher 0.0043 and 0.0066).
- two assumptions the re-read note *asserts but never checks* were checked (§2, objections O-1
  and O-2).

I report these because G-0 is where the input note is reviewed, and a review that reads code
without running it is the "mechanism that cannot fail" pattern this programme has paid for before.

---

## 1. Pins, imports and asserted digests

**Inputs (read, never modified).**

| input | pin | sha256 (16) |
|---|---|---|
| older read fact rows, 80 D-1 episodes | `agent/claude_1@4c92432fec98a847487b50763f54cce0bd2966f4:claude_1/dance1/results/dance-facts-instrument-2026-08-24.json` | `7cd3631ce1320…` |
| v4 read fact rows, 25 D-1 episodes | `agent/claude_1@22d6b2bb2418eece82d67d154c33441bbd655519:claude_1/cure1/results/g2-grade.json` | `45f5f22a1b200…` |
| replays batch 1 (149 games, agent 6652424, v2) | `local_claude_1/narrate/games/` | per-file manifest |
| replays batch 2 (160, agent 6652602, v2) | `local_claude_1/narrate/read2/games-agent6652602-submission41182352.jsonl.gz` | `84f46acb…18897` |
| replays batch 3 (160, agent 6652642, v3) | `local_claude_1/narrate/v3/games-agent6652642-submission41182608.jsonl.gz` | `01169944…c3ceb` |
| replays v4 read (160, agent 6659743) | `local_claude_1/cure1/g2-games/games-agent6659743-submission41192036.jsonl.gz` | `050d1ceb…c6a38` |
| the re-read under review | `origin/main:local_claude_1/dance-geometry/{re-read-2026-08-25.md,reread_shapes.py,results/reread-shapes-2026-08-25.json}` | script `7c2c4b95…` |

**Imported, never copied** — asserted at run time; a mismatch is a refusal, not a warning:

| module | sha256 (16) | what is imported |
|---|---|---|
| `claude_1/adapter1/replay_to_trace.py` | `df2f1187cb5b3187` | `adapt_to_trace` — map, per-turn units, speeds |
| `claude_1/cure1/regressive_baseline.py` | `733fce408550c47e` | `measure_game`, `target_cell`, `manhattan` |
| `claude_1/banana-restoration-r2/trace_detectors.py` | `59dce10dc87797bc` | `bfs_distances`, `Trace`, `Unit` |
| `claude_1/banana-restoration-r2/build_oscillation_library.py` | `4b9fce4ca49a6ce0` | `measure_blocker` |
| `claude_1/dance1/dance_facts.py` | `1155cf266037d43a` | `f3_peers` |
| `claude_1/dance1/narrate3_decode.py` | `d791a7d0cba201fe` | v3 join, `parse_v3_target` |
| `claude_1/narrate1/narrate_decode.py` | `d40a64af6569ba0e` | v2 join, `parse_target` |
| `claude_1/narrate4/narrate4_join.py` | `53e2c41ce264b6ce` | v4 join, `branch` (the letters) |
| `claude_1/cure1/cure1-hold-v4.rs` | `cc4b308705883f10` | reference only — `next_cell`, the branch rule, ~140–188 and ~826–922 |

Nothing above is edited. My exclusive write set is `claude_1/geometry1/**` and nothing else.

---

## 2. My reading of the coordinator's re-read note — agree in the arithmetic, four objections in the method

**Agree, and verified by execution.** Every count in the note's two tables and its batch-3 line is
exactly what its script produces from the pinned fact rows, and the script's output is byte-identical
to the published JSON at the digest the note claims (§0). The note's central observable — the
teammate stood next to the dance when it began in 55 of 80 and 24 of 25 — is a faithful reading of
the rows, and its explanation of *why* it differs from the accepted r3 labels (34 and 15) is correct:
the r3 blocker test demands one cell for the **whole** window, so a teammate that stepped once falls
out of `BLOCKER_WORKING` and into `PEERS_NO_BLOCKER`. I also agree with every caveat the note
carries, and I adopt them: D-1 off replays is an **upper bound**, the two reads are different days
and opponent fields with no randomisation, and the counts are small.

**O-1 — "every episode has exactly one teammate alive" is asserted, never checked; it is true here.**
`reread_shapes.describe` takes `peer = (e.get("f3_peers") or [None])[0]` — the **first** record in
list order. `f3_peers` enumerates `st0.own_units()`, so on any episode with two peers the shape
would be decided by roster order, silently and without a mark. I checked: the peer-count histogram
is `{1: 80}` on the older read and `{1: 25}` on the v4 read, so the assumption holds on all 105
episodes and no number in the note is affected. **But an assumption that happens to hold is not a
check**, and M-1's whole subject is "the teammate", singular. I therefore make it control **K-8**
below: the run asserts `len(f3_peers) == 1` per episode and refuses the episode with
`MULTIPLE_PEERS` rather than picking one.

**O-2 — `mech == BLOCKER_WORKING` sets `one-cell` without re-testing adjacency; it is true here.**
In `describe`, `shape = "one-cell"` is assigned inside `if peer:` but outside `if adj:`, so a
`BLOCKER_WORKING` episode whose peer entry cell were not orthogonally adjacent to a dance cell would
be labelled `one-cell` with `peer_adjacent_at_entry = False`. I checked: zero such episodes on
either read (the r3 blocker test implies adjacency, so this is a redundancy, not a defect). No
number moves; I record it so that a future rerun on other rows cannot inherit an unstated
implication.

**O-3 — `ahead` is a disjunction over the whole window, and should not be carried into M-1.**
`ahead` fires when the peer is closer (Manhattan) than *some* neighbouring dance cell to *some*
distinct stated target seen anywhere in the window: `any(... for c in near for t in targets)`. It is
therefore an **upper bound on an upper bound** — a straight-line stand-in, quantified over a
disjunction — while the note's tables print it as a per-episode yes/no ("32 yes / 2 no"). The note
does call it "a crude stand-in", and I do not ask for it to be withdrawn; I object only to it being
carried forward. **M-1 does not use `ahead` in any predicate, table or refusal.** M-1's `d1 > d0` is
per-turn, on the arm's own BFS metric, against the target stated **on that turn**. Where the two
disagree, M-1 is the measurement and `ahead` is the thing being replaced.

**O-4 — the note's reading of the letter `R` is the typical case, not the rule; this one matters for
K-1.** The note and the script's docstring gloss `R` as "the next cell is taken by a **standing** own
troll and every free neighbour is strictly farther". Reading the arm
(`cure1-hold-v4.rs` ~865–915), `R` is emitted when: the primary landing was **unavailable**
(`reserved`, or `landing_forbidden` for a non-priority unit) **and** a legal orthogonal detour
exists **and** that detour is strictly worse than the current cell (`d_detour > d_cur`) **and** the
hold rule did not fire. The hold fires only when `transient_block` **and** the unit's hold counter
is below `HOLD_WINDOW`. So an `R` turn can also arise when

  (i) the landing is reserved by a standing own troll — the note's case, expected to dominate;
  (ii) the block *is* transient but the hold counter is **exhausted** (`counter >= HOLD_WINDOW`),
       so "R and never H inside the window" does **not** by itself prove the block was permanent —
       the counter is game-scoped, not window-scoped;
  (iii) the landing is empty but `landing_forbidden` for a non-priority unit;
  (iv) the landing was `granted` to an earlier mover in the same pass *and* the counter is
       exhausted.

I am not claiming any of (ii)–(iv) occurs in these 25 episodes — that is a number, and numbers wait
for G-1. I am pre-committing them as the **named** explanation categories for K-1's disagreements
(§6), so that a disagreement cannot be explained after the fact by whatever story fits. The note's
inference in its point 1 — *R and never H, therefore the teammate had been on that cell the turn
before* — should be read as **supported by (i) being the dominant case**, which K-1 measures, and
not as a deduction from the letters alone. If K-1 comes back at 100 % agreement, the note's sentence
is vindicated; if it does not, the residue is (ii)–(iv) and I will say so.

---

## 3. Population and eligibility

**Episodes.** All 105 D-1 episodes: the 80 of the older read (`facts80`, batches 1–3, NARRATE v2 on
batches 1–2 and v3 on batch 3) and the 25 of the v4 read (`g2-grade.json`,
`per_game[].episodes[]`). Episodes are **never dropped silently**: every episode appears in the
results JSON with either its rows or a `refusal` naming one of
`ADAPTER_REFUSED` / `DECODE_REFUSED` / `MULTIPLE_PEERS` / `DANCER_ABSENT`, and the refusal counts
reconcile to 105 (K-5).

**The dancer** is `episode.f1_dancer.unit`; **the teammate** is the single record of
`f3_peers` (K-8 asserts there is exactly one). **The window** is
`[f2_window.turn_start, f2_window.turn_end]` inclusive, on the trace's 1-based turns.

**Eligible turn (M-1).** A window turn `t` is eligible exactly when the `R_pos` eligibility of
`regressive_baseline.measure_game` holds for the **dancer**:

1. the dancer is alive with a known cell at `t` **and** at `t+1` (the last traced turn has no
   successor and is ineligible); and
2. the target the dancer stated at `t` names a cell — `BANK(x,y)`, `CELL(x,y)`, `TREE(x,y)`, or
   `SHACK` resolved to the tent `trace.smap.shacks[0]`. `NONE` and `ABSENT` are ineligible.

I keep the successor-cell requirement even though `d0`/`d1` do not need turn `t+1`, because the
charter fixes the population as "the same eligibility as `R_pos`" and a second population would be
one more figure changing meaning at a boundary. **Both are reported**: the count of window turns
with a stated cell target but **no successor cell** is published per episode as
`ineligible_no_successor`, so a reader can see exactly what the choice costs and re-derive the
looser population if the coordinator wants it. Ineligible turns are broken out as
`ineligible_no_target` (NONE/ABSENT) and `ineligible_dancer_absent`.

**The v2 join shim, and why it needs a control.** `measure_game` reads `row["chosen"]` in the v3
spelling. The v3 join (batch 3) and the v4 join (v4 read) both emit it; the **v2 join
(batches 1 and 2, 309 of the older read's 469 games) does not** — it emits `intent_kind` and
`intent_cell`. I therefore pass `measure_game` a thin `v2_join` wrapper that renders `chosen` from
those two fields into the spelling `parse_target` already accepts (`KIND(x,y)` for
`BANK`/`CELL`/`TREE`, the bare word for `NONE`/`SHACK`) and copies `turn`, `unit`, `unit_cell`,
`command_verb` unchanged. It adds no field and drops none. Because a shim is exactly where a figure
silently changes meaning, **K-9** checks it (§6).

---

## 4. M-1 — is there a road around the standing teammate, and what does it cost

Plain words: at each eligible turn we ask the map, not the bot — *if that one teammate were not
standing there, would the dancer's goal be any closer?*

Per eligible turn `t`, with `target` = the cell the dancer stated at `t`, `x` = the dancer's cell at
`t`, `m` = the teammate's cell at `t`:

- **`walkable`** = `trace.smap.walkable` (the adapter's bare map; units are not in it).
- **`D0 = bfs_distances(walkable, [target])`**, the imported 4-neighbour BFS. It seeds the target at
  0 unconditionally and expands only into walkable cells, so a non-walkable target (a tree, the
  tent) works exactly as it does in the arm.
- **`d0 = D0.get(x, manhattan(x, target))`** — the arm's own fallback
  (`cure1-hold-v4.rs:891`/`:900`, `toward_goal.get(cell).unwrap_or_else(|| manhattan(cell, target))`).
- **`D1 = bfs_distances(walkable − {m}, [target])`**, `d1 = D1.get(x, manhattan(x, target))` — the
  same metric with the teammate's **current** cell removed from the expansion set. The fallback is
  the same fallback; `d0` and `d1` are never compared across two different metrics.
- **`TARGET_OCCUPIED`**: if `m == target`, the BFS still seeds `target` at 0 (the source seeding is
  unconditional), so `d1` would be meaningless. The turn is recorded with
  `status: TARGET_OCCUPIED`, **excluded from the cost table**, and counted separately.
- **`TEAMMATE_ABSENT`**: the teammate must be alive with a known cell at `t`; otherwise the turn is
  recorded `status: TEAMMATE_ABSENT`, excluded from the cost table, counted separately.
- **teammate on every shortest road** ⇔ **`d1 > d0`**.
- **road-around cost** = `d1 − d0`, and **`∞`** (JSON `null`, class `"inf"`) when `target` becomes
  unreachable, i.e. `x ∉ D1` **and** the fallback is what supplied `d1`. To keep `∞` from hiding
  behind the Manhattan fallback, a turn whose `d1` came from the fallback is flagged
  `d1_fallback: true` and its cost is reported but excluded from the medians, with the excluded
  count printed.
- **lateral exists** ⇔ some orthogonal neighbour `c` of `x` with `c ∈ walkable`, `c ∉ {m}`, `c` not
  the cell of any own unit at `t`, and `D0.get(c, manhattan(c, target)) ≤ d0`. **Stated limit:** the
  arm's `L` branch also excludes `reserved` and `forbidden_for_non_priority`, which are
  *within-turn resolver state* and are **not reconstructible from a replay**. So `lateral exists` is
  an **upper bound** on the arm's `L` availability — it can say a sideways step was available where
  the arm's own bookkeeping had taken it. I do not smooth this over; the count is published as an
  upper bound and named as one wherever it appears.

**Per episode:** the share of eligible turns with `d1 > d0`; the **median** cost over exactly those
turns; a **cost class** from that median — `0` / `1–2` / `3–5` / `>5` / `∞`; the dance length
(`f2_window.window_length_states`) and the shape (`one-cell` / `adjacent` / `nobody`, taken from
`reread_shapes.py`, K-7) beside it. Episodes with no eligible turn at all get class `n/a` and are
listed.

**The derived quantity that decides the owner's question, named up front.** `d1 > d0` is a
**global** test (no shortest road avoids the teammate) while the arm's dance is driven by a
**local** one (every free orthogonal neighbour strictly farther). These can disagree, and the
disagreement is the whole point of M-1. I therefore publish, as a first-class column and not as a
remark: **`blocked_but_road_exists`** = eligible turns with `d1 == d0` (a road around at **zero**
extra cost) on which the arm nonetheless could not step forward. That count is the direct evidence
for *route around* over *swap*; the `∞` and `>5` counts are the direct evidence the other way. I am
pre-committing this column now, before any number, so that neither reading can be chosen after
seeing the result.

**Headline tables** (each read separately, then pooled with the read as a column):
cost class × shape; cost class × dance length (`7–11` / `12–29` / `≥30` turns); and one line —
the share of blocked turns (`d1 > d0`) on which a lateral step existed, marked as the upper bound
it is.

---

## 5. M-2 — what stood on the dancer's forward cell on each backward step

Plain words: on the older read there are no resolver letters, so we ask the positions — when the
dancer stepped *backwards*, what was on the cell it would have stepped to?

**Backward step**, per the charter: a dancer step `x → y` inside the window with
`D0(y) > D0(x)` against the target stated at `x` — i.e. exactly `measure_game`'s
`MOVED_REGRESSIVE` verdict for the dancer, read through its `row_sink` rather than re-implemented.
Measured on all 80 older episodes; the headline is the 25 `nobody` episodes.

**The forward cell** is `next_cell(walkable, x, target, speed)` — a Python transliteration of
`cure1-hold-v4.rs:167–187`, using the dancer's **own** `speed` from the trace (`Unit.speed`), with
its two-stage structure preserved: target within `speed` of `x` ⇒ the target itself; target absent
from `bfs_distances(walkable,[x])` ⇒ BFS from the reachable cells of minimum Manhattan distance to
the target; then the cell within `speed` of `x` minimising `(to_target[cell], cell)`, ties broken by
the cell tuple exactly as the Rust `min_by_key` does. **This transliteration is the one piece of
new code that could silently differ from the arm, so K-1 and K-6 are what license it** — if it were
wrong, the `R` turns of the v4 read would not land on the teammate's cell.

**The predicate on that forward cell `f` at turn `t`:**

- **(a) standing** — an own unit occupies `f` at `t` **and** the same unit occupies `f` at `t−1`;
- **(b) transient** — an own unit occupies `f` at `t` but not at `t−1` (arrived this turn), or
  occupied `f` at `t−1` but not at `t` (left this turn), or occupies `f` at `t` and does not occupy
  `f` at `t+1` (moving away this turn);
- **(c) nothing of ours** — residual: no own unit on `f` at `t`. Each (c) row records whether `f`
  was off the BFS map (Manhattan fallback used) and whether the dancer's stated target changed on
  that turn (planner flip). **The (c) rows are listed whole in the results JSON**, per the charter.

**Divergence from the arm's own transient test, stated rather than blurred.** The arm's
`transient_block` is: the blocker is itself a mover this pass, **or** `prev_cells[blocker] != landing`
(it arrived this turn), **or else permanent** — with an *unknown* previous cell counting as
**permanent** (`None => false`). The charter's (b) is broader: it also admits "arrived last turn"
and "moving away this turn", and it has no unknown-previous case. I follow **the charter's**
predicate, because that is what was chartered and what M-2's hypothesis is about, and I **also**
emit the arm's exact predicate per row as `arm_transient` (true/false/unknown). Both counts are
published side by side. This is deliberate: K-6 grades the arm's predicate against the arm's
letters, while the headline M-2 count answers the owner's question. A single number doing both jobs
would be a figure changing meaning at a boundary.

At `t = turn_start` there is no `t−1` inside the window; the trace's turn `t−1` is used when it
exists (windows do not start at turn 1 in general), and where it does not the row is marked
`prev_unknown: true`, classified (b) only on the arrive/leave-this-turn clauses, and counted
separately.

---

## 6. Controls — each fires with its number, or the result is not reported

| id | what it tests | expected |
|---|---|---|
| **K-1** positive, v4 read | a window turn lettered `R` has the teammate's cell as the arm's forward step **and** `d1 > d0` | **≥ 95 %** agreement; every disagreement listed and assigned to a **pre-committed** category: (i) Manhattan fallback row; (ii) hold counter exhausted (`R` on a transient block); (iii) `landing_forbidden`; (iv) landing granted to an earlier mover; (v) teammate on the forward cell but `d1 == d0` — the road-around case of §4. No category is invented after the fact. |
| **K-2** negative, v4 read | a turn lettered `P` (forward step taken) has a **free** forward cell | 100 %, or each exception explained |
| **K-3** poison | wall a random walkable cell **not** orthogonally adjacent to the dancer instead of the teammate's cell — seeded `random.Random(20260825)`, the seed published, drawn from the sorted walkable list so the draw is reproducible | cost 0 on nearly every eligible turn; the share is **reported, not asserted** |
| **K-4** determinism | a second whole run into a separate directory | byte-identical results, controls and determinism JSONs |
| **K-5** exhaustiveness | per episode, eligible + `ineligible_no_target` + `ineligible_no_successor` + `ineligible_dancer_absent` = window length; episode totals = 80 and 25 | exact |
| **K-6** M-2 on the v4 read | the **arm's** predicate (`arm_transient`) gives (a) on `R` turns and (b) on `H` turns | disagreements listed and explained; note that `H` may be 0 inside these windows (the re-read reports 0 `H` episodes), in which case the `H` half of K-6 is reported **VACUOUS — NOT MEASURED**, never "passed" |
| **K-7** re-read identity | the shapes used here reproduce `reread-shapes-2026-08-25.json` byte-for-byte from the pinned fact rows | exact — **already demonstrated**, `8e2159e3…` (§0) |
| **K-8** peer uniqueness (**new, from O-1**) | `len(f3_peers) == 1` on every episode; otherwise the episode is refused `MULTIPLE_PEERS`, never silently resolved by list order | 105 of 105 expected (pre-checked: `{1: 80}` and `{1: 25}`) |
| **K-9** v2 shim fidelity (**new, from §3**) | for every window turn of the older read, the `chosen` the shim renders resolves to the same target cell as the episode's own `f4_telemetry.chosen_sequence` entry for that turn | exact; any mismatch refuses the episode rather than being tolerated |

K-6's vacuity clause is written in advance on purpose: a control that reports PASS on an empty
population is the inert-check failure this programme has recorded four times.

---

## 7. File layout and the run command

```
claude_1/geometry1/
  definitions-g0-2026-08-25.md          this file (revisions -r2, -r3 …)
  geometry.py                           the measure: eligibility, d0/d1, next_cell, M-2 predicate
  run_geometry.py                       the runner (digest assertions, controls, JSON writers)
  results/geometry-2026-08-2x.json      every episode, every eligible turn, whole
  results/controls-2026-08-2x.json      K-1…K-9, each with its number
  results/determinism-2026-08-2x.json   the two run digests (K-4)
  g1-execution-2026-08-2x.md            the execution report and the headline tables
```

```
python3 claude_1/geometry1/run_geometry.py \
    --facts80 <dance-facts-instrument-2026-08-24.json> \
    --g2 <g2-grade.json> \
    --batch1 <local_claude_1/narrate/games/> \
    --batch2 <…6652602….jsonl.gz> --batch3 <…6652642….jsonl.gz> --v4 <…6659743….jsonl.gz> \
    --out <dir>
```

Run twice into two directories; the results files must be byte-identical (K-4). The runner prints
every control with its number. JSON is written `sort_keys=True, indent=1` with a trailing newline —
the same shape as `reread_shapes.py`, so a reader diffing the two is not fighting formatting.

---

## 8. What I ask codex_1 to rule on

`DEFINITIONS_ACCEPTED` or `REVISION_REQUIRED`, `requires_ack: true` toward `claude_1`. The five
places where I have exercised judgement, and where a `REVISION_REQUIRED` would be cheap **now** and
expensive after counting:

1. **The `∞`/fallback interaction** (§4) — I report a fallback-supplied `d1` separately rather than
   calling it `∞`. The alternative is to call unreachable-under-fallback `∞` outright, which is
   simpler and slightly more pessimistic about routing around.
2. **`lateral exists` as an acknowledged upper bound** (§4) — `reserved` and
   `forbidden_for_non_priority` are not reconstructible. Accept the upper bound, or drop the
   lateral line entirely rather than publish a bounded number?
3. **Two transient predicates in M-2** (§5) — the charter's (b) for the headline, the arm's for K-6,
   both published. If you want one, say which, and it becomes the headline.
4. **Eligibility keeps the `R_pos` successor-cell requirement** (§3) even though `d0`/`d1` do not
   need it, with `ineligible_no_successor` published so the looser population is re-derivable.
5. **K-1's explanation categories are pre-committed** (§6, from O-4). If you think (ii)–(iv) are
   unreachable in these episodes, say so now — then a disagreement in that category becomes a
   finding rather than an excuse.

I hold every one of these open until you rule. Nothing is counted before then.
