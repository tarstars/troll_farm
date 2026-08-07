# Feasibility scoping — raw `D-1 == 0` and `D-4 == 0` on parent `a8eb3b2b`

- Author: `claude_1` (subagent), 2026-08-07
- Status: **SCOPING REPORT.** No bot source, detector, gate, candidate or parent was
  modified. Read-and-run only.
- Question (owner ruling 2026-08-07, binding, not under review): the acceptance gate
  requires raw `D-1 == 0` and `D-4 == 0` on the candidate's delivered bytes, with no
  inherited-parent and no aligned-prefix exemption. The owner has accepted that the parent
  lineage must therefore be repaired. **Is reaching raw `D-1 = 0` and `D-4 = 0` on this
  parent achievable, at what cost, at what risk?**

**Headline verdict: `FEASIBLE_WITH_CONDITIONS` for D-4; `UNRESOLVED` for D-1 as a whole —
`FEASIBLE_WITH_CONDITIONS` for its dominant cluster (34/35 episodes) and `UNRESOLVED` for
the residual cluster (1/35), which alone keeps raw D-1 above zero. Reaching raw zero on
*both* detectors is not demonstrated to be achievable, and the two prior frozen-protocol
attempts at the dominant cluster both closed at their mechanism gate. Full verdict table in
§8; recommendation in §9.**

---

## 0. Evidence discipline

Every claim below is tagged:

- **[M] MEASURED** — I ran it in this session, from committed tools, on the frozen parent
  bytes; the command and inputs are in §1.
- **[P] PRIOR-MEASURED** — a number quoted from committed evidence in this repository that
  I did **not** re-run. Source path given every time.
- **[I] INFERRED** — a conclusion I derived from measurements plus source semantics. Stated
  as inference, never as measurement.
- **[A] ASSUMED** — an assumption I could not test.
- **UNRESOLVED** — I could not determine it; the evidence that would settle it is named.

Repository state: branch `agent/claude_1-banana-restoration-r2`, HEAD `73fec609`.
Toolchain: `rustc 1.97.1 (8bab26f4f 2026-07-14)` at `$HOME/.cargo/bin`, python3.12 stdlib.

### Input hashes (sha256, all recomputed this session) **[M]**

| file | sha256 |
|---|---|
| `cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs` (the parent) | `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55` |
| `claude_1/pipeline/fuzz_panel.py` | `cc7db6f2f048a1739e587cff9e26e5783d08f69672e233b227a6294f03b6571d` |
| `claude_1/banana-restoration-r2/trace_detectors.py` | `59dce10dc87797bc6b1b8da0f628f4ddd82b561d93946fa91453d2ea40805209` |
| `claude_1/pipeline/fuzz-panel-config.json` (template) | `f5394e7a8b974062b07f42bc535e113dca2e9d67b64c9b196c1a4b63660b99fe` |
| `rust/src/bin/yamo_orchard_live.rs` (readable relative, see §4) | `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f` |
| floor config I generated (§1) | `47e35c7ebd719f9152206f85f2f8fa98e6b888dffd59d3dd5f22093df9fe22b6` |
| floor games archive, **decompressed** `games.jsonl` | `aaec8ca8a22d6a0fb91429a64d1391d5f95bd144bee340262836b5e80d159889` |

Note on `yamo_orchard_live.rs`: its sha256 prefix `fff6669b` is the same byte-exact frozen
dev copy that the D171a and D176a experiment records name as their control snapshot
(`data/analysis/live-agent-6553250/d171a-oscillation-breaker-result-2026-07-28.md`,
`…/d176a-…-result-2026-07-29.md`). The line references in §4 are therefore against the same
artifact those experiments used.

---

## 1. Floor reproduction — exact command **[M]**

The floor config is the committed panel config with **both** `candidate.source` and
`parent.source` pointed at the absolute path of the parent, distinct crate names, and a
fresh `games_dir`. Byte-reproducible generator:

```bash
FEAS=/tmp/claude-1000/-home-tarstars-prj-troll-farm/3b336b91-cd2f-4655-9aaf-31fd6d3d156f/scratchpad/feas
mkdir -p "$FEAS"
cd /home/tarstars/prj/troll_farm-claude_1
python3 - <<'EOF'
import json, pathlib, os
S = pathlib.Path(os.environ["FEAS"])
cfg = json.loads(pathlib.Path("claude_1/pipeline/fuzz-panel-config.json").read_text())
P = "/home/tarstars/prj/troll_farm-claude_1/cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs"
SHA = "a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55"
cfg["task"] = "FEASIBILITY floor: parent a8eb3b2b as its own candidate (raw D-1/D-4 scoping)"
cfg["candidate"] = {"source": P, "sha256": SHA, "crate": "feas_floor_candidate"}
cfg["parent"]    = {"source": P, "sha256": SHA, "crate": "feas_floor_parent"}
cfg["games_dir"] = str(S / "games-floor")
cfg["bin_cache_dir"] = str(S / "bin")
(S / "floor-config.json").write_text(json.dumps(cfg, indent=2) + "\n")
EOF

export PATH="$HOME/.cargo/bin:$PATH"
python3 claude_1/pipeline/fuzz_panel.py \
    --config "$FEAS/floor-config.json" \
    --report "$FEAS/floor-report.md" \
    --json   "$FEAS/floor-summary.json"
```

`--report` output is **Markdown** despite prior `.json` naming, as the task record notes.

Result **[M]**:

```
fuzz_panel: BLOCK (240 games, 118 blocking, 0 flagged, 16.8 s)
```

**BLOCK 118/240 — reproduces the stated floor exactly.** Re-run a second time with a
different `games_dir`: identical 118/240, and the decompressed `games.jsonl` byte-identical
(`aaec8ca8…` both runs), and `floor-report.md` identical modulo the wall-time line. The
floor is deterministic.

### Per-detector floor, both units **[M]**

| detector | blocking games | episodes |
|---|---|---|
| D-1 A→B→A movement | **32** | **35** |
| D-4 abandoned carried wood | **6** | **6** |
| D-5 unbounded planting | 1 | 1 |
| D-6 opponent-favoured fruit | 9 | 15 |
| D-9 second-worker TRAIN displacement | 74 | 196 |
| D-2 / D-3 / D-7 / D-8 | 0 | 0 |
| P2 asset survival | 4 | — |
| P4 liveness (calibrated) | 29 | — |

D-1 = 32 games / 35 episodes and D-4 = 6 games / 6 episodes, exactly as the task states,
and matching `claude_1/pipeline/design-gate-redesign-2026-08-07.md` §1.

### Scoping fact the owner needs first **[M]**

| | games blocking |
|---|---|
| floor, as measured | **118 / 240** |
| games blocked **only** by D-1 and/or D-4 | 12 |
| floor **if D-1 and D-4 were both driven to zero** and nothing else changed | **106 / 240** |

**Repairing D-1 and D-4 to raw zero moves the gate from 118 blocking games to 106.** It
does not produce a green gate; D-9 alone blocks 74 games (63 of them as the sole cause).
This does not contradict the ruling — the ruling is about D-1 and D-4 specifically — but any
plan costed as "repair the parent so the gate passes" is costing the wrong thing.

Overlaps **[M]**: D-1 ∩ P4 = 19 games (59% of D-1 games also fail liveness);
D-4 ∩ P4 = 2; D-1 ∩ D-4 = 1.

---

## 2. D-1 root cause — clustering the 32 games / 35 episodes

All 35 episodes were extracted with full context (map/seat/class/opponent/seed, unit, cells,
turn window, per-turn own+opponent positions, cargo, inventory, plants, emitted commands).
Scratchpad: `$FEAS/extract.py`, `$FEAS/episodes.json`.

### 2.1 Every episode has the same command-level signature **[M]**

In **35/35** episodes the oscillating unit emits, on every turn of the window, a `MOVE`
whose destination is the *other* of the two cells. There is not one episode in which the
unit stands still, waits, or is displaced while holding a fixed emitted destination. The
emitted destination is the post-resolution **landing** cell, not the policy's goal — the
parent rewrites every `MOVE` to its one-step landing in
`resolve_move_conflicts_with_priority_and_forbidden` — so the command stream alone does not
say whether the *goal* alternates.

### 2.2 The occupancy signature **[M]**

| feature | count |
|---|---|
| episodes with a **stationary own peer** adjacent to the oscillation pair | **34 / 35** |
| episodes with **no other own unit alive at all** (solo) | **1 / 35** |
| of the 34: the parked peer stands **on a plant** | 30 / 34 |
| of the 34: the parked peer emits **WAIT** for the whole window | 28 / 34 (4 emit `CHOP`, 2 undetermined) |
| D-1 rate in games with **1** own unit | 1 / 98 = **1.0 %** |
| D-1 rate in games with **2** own units | 31 / 142 = **21.8 %** |

The mechanism is essentially unavailable to a one-unit game.

### 2.3 Causal confirmation: replaying the parent's own resolver **[M]**

I reimplemented, read-only in Python, the two parent functions that decide a landing cell —
`game::nav::next_cell` and `MoisanBot::resolve_move_conflicts_with_priority_and_forbidden` —
and asked, for each episode: *does a single constant goal `G`, together with the observed
reserved/occupied sets, reproduce the entire observed landing sequence?*
(Scratchpad `$FEAS/resolver_fit.py`.)

- **28/35 episodes: reproduced exactly, every turn, by one constant goal.**
- **6/35 more: reproduced by one constant goal on every turn except the single final turn**
  — the turn on which the oscillation breaks, i.e. the turn the goal actually did change
  (verified individually: the sole mismatch is the last observed turn in all six).
- **1/35 (`m085` seat 0): no constant goal fits.** This is the solo episode.

So **34/35 episodes are fully explained by a fixed goal plus the parent's own detour
tie-break.** Further, in **24/28** of the exactly-fitting episodes the fitted goal set
*contains the parked peer's own cell*, and in several (`m046`, `m079`×2, `m094`, `m099`,
`m073`, `m078`, `m014`) the fitted goal set is **exactly** `{peer cell}`.

**[I]** The mechanism, stated once: *two own units select the same tree. One arrives, stands
on it and stops (waiting for fruit, or chopping). The second unit keeps that same cell as its
goal. `next_cell` returns that cell as its landing; the resolver finds it `reserved` because
the peer is not moving; the detour branch picks the best free orthogonal neighbour by
`(BFS-distance-to-goal, cell)`, which is a retreat; next turn, from the retreat cell, the
landing is the original cell again and is not reserved, so it steps back. The tie-break has
no cross-turn memory, so it regenerates the identical choice forever.*

**[I], high confidence** This inference is not unique in the strict logical sense — a
two-goal model could also fit — but it is the parsimonious one, it is what the fitted goal
sets say, and it independently reproduces the conclusion the project already reached on the
**real** arena corpus (§6.2).

### 2.4 The residual episode is a genuinely different root cause **[M]**

`m085` seat 0, turns 17–22, single own unit, no peer, no possible reservation conflict — the
detour branch is unreachable. Fitting per-phase goals:

| unit standing at | feasible constant goals |
|---|---|
| `(1,4)` — the tent door, on which it has been planting-and-chopping | 50 cells, all east (the map's only remaining plant, a LEMON at `(9,1)`, is among them) |
| `(2,4)` — one step east | exactly `{(0,5), (1,4), (1,5)}` = the tent ring |
| intersection | **empty** |

The goal alternates between "go fetch the far lemon" and "come home and plant/bank", one
step apart, for six turns, then resolves into `PICK LEMON` → `PLANT LEMON`. This is a
two-cycle in the **goal selector**, not in the move resolver. n = 1.

### 2.5 D-1 cluster summary

| cluster | episodes | games | mechanism | evidence |
|---|---|---|---|---|
| **D1-A — same-tree contention × memoryless detour tie-break** | **34 / 35** | 31 / 32 | fixed goal on a cell a parked own peer occupies; resolver detour bounces forever | resolver replay reproduces every non-terminating turn; 34/34 have a parked adjacent peer; 30/34 peer stands on a plant |
| **D1-B — goal-selector two-cycle (no conflict)** | **1 / 35** | 1 / 32 | goal flips between a far target and the home ring on alternate cells | disjoint per-phase feasible goal sets, intersection empty |

**Two distinct D-1 root causes**, not twenty and not one. But D1-B is a real second cause,
and under a raw-zero rule a single episode is a block.

---

## 3. D-4 root cause — the 6 games / 6 episodes

All six are `kind: "no_progress"` (the "2 consecutive turns with no decrease of `door_dist`
and no DROP/cargo-loss" clause of `detect_d4`, `trace_detectors.py:757`). None is the
`non_bank_verb` clause.

### 3.1 Signature **[M]**

In all six the wood-carrying, bank-committed unit **stops emitting any command at all**
(the bot emits `WAIT`) for exactly 2–3 turns, then resumes walking to the door.

### 3.2 The two correlations are perfect **[M]**

| doors on the map | games | D-4 games | rate |
|---|---|---|---|
| **1** | 30 | **6** | **20.0 %** |
| 2 | 59 | 0 | 0 % |
| 3 | 19 | 0 | 0 % |
| 4 | 132 | 0 | 0 % |

**6/6 D-4 episodes occur on single-door maps; 0/210 on maps with two or more doors.**

And in **6/6**, the *other* own unit performs a bank `DROP` at that unique door inside or
immediately adjacent to the pause window (turns 15, 19, 24, 11, 21, 6 against windows
14–16, 15–17, 23–25, 9–11, 21–23, 5–7).

### 3.3 Mechanism

**[I], high confidence** The parent serialises banking when the tent has exactly one walkable
door: while one carrier is using the door, the second carrier is held in place. The gate is
`MoisanBot::unique_shack_door`, whose body I read verbatim in the minified parent bytes:

```rust
fn unique_shack_door(view:&GameState)->Option<Cell>{
    let doors:Vec<Cell> = ortho_neighbors(view.shacks[0]).into_iter()
        .filter(|cell| view.walkable.contains(cell)).collect();
    (doors.len()==1).then_some(doors[0])
}
```

`(doors.len()==1)` is exactly the empirical 1-door boundary — **[M]** for the predicate,
**[I]** for the attribution of the hold to `force_unique_door_clear`, which is the one
function gated on it and is enabled in this parent (`door_unblocking=true;`, one occurrence).

**D-4 has ONE root cause**, fully characterised, with a perfectly clean discriminator.

---

## 4. Source localisation

The parent is minified, single-line, 62,725 bytes. A readable relative exists and is a
strict superset: **every one of the parent's 94 `fn` names appears in
`rust/src/bin/yamo_orchard_live.rs` (94/94 shared, 0 parent-only)** **[M]**. The parent is
the slimmed member of that lineage. `claude_1/banana-restoration-r2/integration-seam-2026-08-04.md`
§A independently maps parent ↔ this family. Confidence in using the readable file for
line-level reading: **high**.

All named anchors are **unique substrings** of the parent bytes (occurrences = 1) **[M]**:

| cluster | readable location | minified anchor (occurrences / byte offset) | localisation confidence |
|---|---|---|---|
| **D1-A** | `MoisanBot::resolve_move_conflicts_with_priority_and_forbidden`, detour tie-break, `yamo_orchard_live.rs:1503–1519` — the `.min_by_key(|cell| (toward_goal…, *cell))` | `.min_by_key(\|cell\|{(toward_goal.get(cell).copied().unwrap_or_else(\|\|manhattan(*cell,target)),*cell,)})` — **1** occurrence @ 22281 | **HIGH** — resolver replay of exactly this code reproduces 34/35 episodes turn-by-turn |
| D1-A (upstream) | `game::nav::next_cell`, `:262–298` | `pub fn next_cell(` — **1** @ 4268 | HIGH (read; strictly monotone for a fixed goal, so it cannot itself oscillate) |
| D1-A (true origin) | whatever makes two units select the same tree — the candidate/target scorer | not localised | **LOW / UNRESOLVED** — see §10 |
| **D1-B** | goal selector; the gating predicate that flips between t=22 and t=23 | not localised | **NONE — UNRESOLVED** |
| **D-4** | `MoisanBot::force_unique_door_clear`, `:2109–2230`, gated on `MoisanBot::unique_shack_door` `:2085–2090` | `fn force_unique_door_clear(` — **1** @ 30941; `fn unique_shack_door(` — **1** @ 29892; `self.force_unique_door_clear(view,&mut by_id);` — **1** @ 47426; `door_unblocking=true;` — **1** @ 23282 | **MEDIUM-HIGH** — the 1-door gate is proven by measurement; that this specific function (rather than a sibling) emits the hold is inferred |

The project had already pinned D1-A independently. `docs/BACKLOG.md` B3.4 **[P]**:

> root cause pinned: memoryless detour tie-break, `yamo_orchard_live.rs:1505-19`; coverage
> gap in `force_unique_door_clear`

and `data/analysis/live-agent-6553250/d171a-oscillation-breaker-protocol-2026-07-28.md`
**[P]**:

> `resolve_move_conflicts_with_priority_and_forbidden` (`…:1440–1520`; detour tie-break
> `:1505–1519`): candidate generators recompute targets fresh each turn with zero memory;
> when the natural step is blocked by an own unit treated as reserved, the detour's
> `min_by_key((BFS_dist, Cell))` can tie between "retreat" and "go around", broken by
> incidental lexicographic Cell order — and regenerates the identical choice every turn.
> **17/18 real episodes: a teammate parked ≥85 % of the run.**

My independent 2026-08-07 measurement on this panel: **34/35 episodes have a parked
teammate.** That is a replication, on a different population, of a finding this project made
on the real arena corpus.

---

## 5. THE CRITICAL RISK — is each cluster a defect or functional behaviour?

The parent is arena-rated. The gate cannot see rating. A repair that removes oscillation and
lowers rating is a net loss. This section is the one that decides the recommendation.

### 5.1 What the bot is *actually* doing during D1-A — the decisive measurement **[M]**

For every D-1 window I asked: was there any **other** plant reachable by the oscillating
unit, i.e. did it have somewhere better to be?

| | episodes | oscillating turns |
|---|---|---|
| **no alternative reachable plant at any sampled turn** | **21 / 35** | **2,733 (80 %)** |
| an alternative reachable plant existed throughout | 12 / 35 | 650 (19 %) |
| alternative existed for part of the window | 2 / 35 | 14 (< 1 %) |
| **total** | 35 | **3,397** |

In 21 of 35 episodes — carrying 80 % of all oscillating turns — **the tree the peer is parked
on is the last reachable plant on the map.** The oscillating unit has literally nothing else
to do. Its pacing is idleness expressed as motion. D-1's predicate cannot distinguish
"deadlocked while productive work exists" from "idle in place with one cell of jitter", and
on this parent the second case dominates.

Countervailing measurement, and I do not want to bury it **[M]**: the harness's own
`work_remaining` predicate is `True` at the start **and** end of 35/35 windows, and 35/35
windows lie **entirely inside the live horizon**. So these are not the post-completion coast
that P4 repair #2 was built to excuse. Work does remain — it is just, in 21 cases, work that
only the *parked* unit is positioned to do. Consistently, 19/32 D-1 games also fail P4
liveness: the underlying idleness is a genuine and already-detected problem. It is simply not
D-1's problem, and D-1 is not the instrument that will fix it.

### 5.2 Prior real-corpus causality assessment **[P]**

`docs/LEDGER-MAP.md` row B3.4:

> Root-caused to a memoryless detour tie-break with zero cross-turn memory — ties regenerate
> indefinitely… **Causality modest (2/18 causally suspicious).**

Of eighteen sustained oscillations found in real arena games, only two were judged plausibly
to have cost anything. That is an independent, real-play estimate of the same defect/benign
split my §5.1 finds synthetically.

### 5.3 What happened the two times this project actually built the fix **[P]**

**D171a** (`…/d171a-oscillation-breaker-result-2026-07-28.md`), 2,048 paired tasks,
128 fresh seeds × 8 real opponent families × 2 seats. Verdict **CLOSED**:

- ≥10-turn runs fell only **127 → 69 (45.7 %)** against an ≥80 % floor;
- 5–9-turn runs **rose 183 → 398 (+117 %)**;
- **72 tasks with zero control oscillation acquired brand-new runs** (worst de-novo: 88 turns);
- 0/107 control-problem tasks fully resolved;
- value **neutral**: paired mean +0.053, CI [−0.043, +0.148], catastrophes 74/74 tied.

**D176a** (`…/d176a-oscillation-breaker-successor-result-2026-07-29.md`), same panel size.
Verdict **CLOSED-AT-MECHANISM**:

| sub-gate | control | candidate | gate | verdict |
|---|---|---|---|---|
| ≥10-turn task rate | 8.50 % (174) | 2.88 % (59) | ≤6.0 % | PASS |
| de-novo oscillation | — | 0.0 % (0) | ≤1.0 % | PASS |
| 5–9-turn runs | 213 | 825 (**+287 %**) | ≤+10 % | FAIL |
| worst-case run length | **247 turns** | **247 turns** | ≤20 | FAIL |

value: overall mean margin **+0.045**, CI **[−0.024, +0.114]**, catastrophes 73/73 tied,
worst family 0.000. The integrator's own adjudication: *"a working version of it is not worth
a promotion cycle."*

### 5.4 The arithmetic that matters most in this whole report

I read both predicates and they are the same predicate.

- D171a/D176a `RunTracker` (`rust/src/bin/d171a_oscillation_breaker_panel.rs:193–232`) **[M]**:
  a reversal is `positions[k]==positions[k-2] && positions[k]!=positions[k-1]`; `streak`
  counts consecutive reversals; for an alternating window of `L` positions, `streak = L−2`.
- `detect_d1` (`trace_detectors.py:555`) **[M]**: same alternation predicate, and it emits an
  episode when `(t-1) - s >= 6`, i.e. window length `L >= 7`, i.e. **`streak >= 5`**.

**D171a/D176a's `run_5_9` bucket starts exactly where D-1 starts.** Every run counted in
`run_5_9 ∪ run_ge10` is a D-1 episode (minus those containing a progress event).

Therefore **[I], and this is the single strongest piece of evidence in the report**: the best
oscillation breaker this project has ever built — D176a, which passed its de-novo gate
perfectly — would have taken D-1-eligible runs from roughly `213 + ≥174` to roughly
`825 + ≥59`, i.e. **more than doubled the D-1 episode count**, while leaving the worst-case
run at 247 turns, unchanged. It converts long oscillations into many short ones. Under a
threshold-at-zero rule, fragmentation is not a partial win; it is a regression.

### 5.5 Per-cluster judgement

| cluster | judgement | reasoning |
|---|---|---|
| **D1-A, the 21 no-alternative episodes (80 % of oscillating turns)** | **BENIGN ARTIFACT** | the contested tree is the only reachable plant; the unit has no better action; pacing ≡ waiting. The real problem in these games is idleness, already caught by P4 (19/32 overlap). |
| **D1-A, the 12 with an alternative** | **REAL DEFECT (probable)** | an alternative reachable plant existed and the unit stayed fixated on a contested cell. I cannot confirm the alternative was *worth* targeting (it may be an opponent crop, unripe, or already claimed) — hence "probable". Upper bound on recoverable time: 650 unit-turns across 240 games ≈ **2.7 turns/game**. |
| **D1-A, the 2 partial** | **UNKNOWN** | alternative present for part of the window only. |
| **D1-B** (1 episode) | **UNKNOWN** | 6-turn hesitation; goal genuinely flips; not localised; n = 1 gives no basis for a defect/benign call. |
| **D-4** (6 episodes) | **BENIGN ARTIFACT (probable)** | a deliberate, gated, single-door serialisation. Two units cannot bank through one door on the same turn, so holding one is coherent. The arguable inefficiency is *where* it holds — the waiter is often several cells from the door and could have closed distance — but the cost is 2–3 turns per banking cycle on 12.5 % of maps. Cannot rule out that it is load-bearing on 1-door maps. |

**Split across all 41 episodes: 27 benign artifact (21 D-1 + 6 D-4), 12 probable real defect,
2 unknown-partial (counted with the 12 in the headline as "not benign"), 1 unknown (D1-B).**

### 5.6 What I cannot quantify

The gate has no rating channel and neither do I. There is no arena rating measurement in this
session and none is possible from `fuzz_panel.py`, which measures margin on synthetic maps
against three scripted opponents. The only rating-relevant instrument in this repository is
the D171a/D176a paired panel (2,048 tasks × 8 real opponent families), and using it requires
building a candidate — which is out of scope here and, per D171a's record, requires a **new
owner authorisation** that "the D171a standing grant never triggered and does not carry
over" **[P]**.

---

## 6. Harness validity — are these episodes an artifact of the mini-referee?

### 6.1 Opponent correlation: NO signal **[M]**

| opponent | D-1 games / games | rate | restricted to 2-unit games |
|---|---|---|---|
| `idle` | 9 / 72 | 12.5 % | 9 / 34 = 26 % |
| `harvester` | 15 / 96 | 15.6 % | 15 / 62 = 24 % |
| `chopper_aggressor` | 8 / 72 | 11.1 % | 7 / 46 = 15 % |

**D-1 is not an `idle`-opponent artifact.** It appears at a similar rate against all three
profiles. The hypothesis the task flagged as "a strong signal" is refuted.

### 6.2 The mechanism is confirmed in *real* arena games **[P]**

`docs/LEDGER-MAP.md` row B3.2/B3.3, from a 4×-scale motion audit over the real corpus:

> One new lead found: **sustained same-two-cell oscillation (18/194 games, worst 131 turns)**
> → opened as B3.4.

Real-corpus rate **9.3 %** of games; my synthetic panel **13.3 %** (32/240), or 21.8 %
restricted to two-unit games. Real corpus: teammate parked in **17/18**; mine: **34/35**.
Worst real run 131 turns (`run_len` = window − 2); my worst window is 195 turns = `run_len` 193 (`m110` seat 1, turns 6–200).

**These D-1 episodes are not a harness artifact. The synthetic panel reproduces a defect the
project already measured in real play, at the same rate and with the same signature.** This
is the most important harness-validity result in the report, and it cuts *against* the
"repair the harness instead" option for D-1.

### 6.3 Map-class correlation: real, and consistent with the mechanism **[M]**

Restricted to the 142 two-unit games (the only games where D1-A is possible):

| class | D-1 games / games | rate |
|---|---|---|
| `orchard_eligible` | 5 / 16 | 31 % |
| `choke_corridor` | 14 / 46 | 30 % |
| `forest_sparse` | 3 / 10 | 30 % |
| `single_door_tent` | 4 / 16 | 25 % |
| `multi_door` | 1 / 6 | 17 % |
| `open_field` | 2 / 18 | 11 % |
| `forest_dense` | 1 / 10 | 10 % |
| `water_diagonal` | 1 / 20 | 5 % |

Constrained geometry (corridor, single door) and sparse plant supply (`forest_sparse`,
`orchard_eligible`) raise the rate 3–6× over `open_field` / `water_diagonal`. That is what the
mechanism predicts: fewer trees ⇒ more same-tree contention; narrower corridors ⇒ fewer free
detour cells. Several cells have small n (`multi_door` n=6) and I do not read them.

Full class × opponent contingency table is in `$FEAS/` (regenerable from `games.jsonl.gz`).

### 6.4 Where the harness *is* impoverished, and what it costs **[M]**

- maps are 10–14 wide × 4–8 tall; **98/240 games never train a second unit** — the harness
  reports D-1 on a population where 41 % of games structurally cannot exhibit D1-A;
- 20/240 games start with **zero** plants, 54 with one, 48 with two — the "last remaining
  tree" state of §5.1 is reached quickly and often;
- horizon is 200 turns against the real `TOTAL_TURNS = 300`.

**[I]** These do not create the D-1 mechanism (§6.2 settles that) but they do **inflate the
benign share of it**: a richer, longer map has more alternative targets, so more of the
oscillation would fall into the "alternative existed" bucket. The 21/35 benign share is
therefore likely an *over*-estimate of benignity relative to real play — one of the few
places where the synthetic panel is pessimistic about the bot in the direction of leniency.
UNRESOLVED: the exact real-play split. Evidence that would settle it: re-run the §5.1
alternative-target measurement over the real-corpus 18 B3.4 games.

### 6.5 A detector blind spot worth reporting **[M], [I]**

D-3 ("same-target contention") reports **0 episodes** on this panel, while D-1's dominant
cluster **is** same-target contention. D-3's proxy (per resolution A4) is "two own units
emitting `MOVE` to the identical destination cell on ≥2 consecutive turns" — but the parent
rewrites every `MOVE` to its one-step landing before it reaches the transcript, so two units
contending for one tree essentially never emit the same destination. **[I]** D-3 as
implemented cannot see the contention that causes 34/35 D-1 episodes on this lineage. This
reinforces §4.5 of the gate re-design proposal: D-3's zero is "untested", not "clean".

---

## 7. Cost and blast radius

### 7.1 Per-cluster change sketch and insertion sites **[M]** for site counts, **[I]** for design

| cluster | change needed | insertion sites in the minified bytes |
|---|---|---|
| **D1-A** | in the detour branch, do not take a detour that fails to strictly reduce distance-to-goal; emit `WAIT` instead. Memoryless — no arm/disarm state, therefore structurally immune to the stale-arm hole that killed D171a. | **1** — the `.min_by_key(…)` substring is unique (offset 22281). One guard on its result. |
| **D1-A (alternative)** | retarget: forbid selecting a tree an own unit already occupies. | not localised — the target scorer was not found; ≥1 site, unknown |
| **D1-B** | not determined | **0 known** — UNRESOLVED |
| **D-4** | make the held carrier close distance to the door while waiting rather than freeze, or shorten the hold to 1 turn | **1** — `fn force_unique_door_clear(` unique (offset 30941); the hold site inside it |

**[I]** Why the D1-A sketch is *not* what D171a/D176a tried, and why that matters: both prior
attempts added **per-unit cross-turn memory** and **hard-forbade** a remembered cell. D171a's
own post-mortem names the failure as a stale arm persisting after the echo self-terminated.
The sketch above adds no memory and forbids nothing; it only declines a move that provably
makes no progress. Position becomes constant, and D-1's predicate requires
`pos[t] != pos[t-1]`, so the episode cannot form. That is a genuinely untried point in the
design space, and it is the reason my D1-A verdict is not a flat `INFEASIBLE`.

**[I]** Its risk, stated plainly: the same guard also suppresses *legitimate* go-arounds,
where stepping temporarily away from the goal is the right move because a longer route
exists. On a map with a real alternative route the change converts "walk around the blocker"
into "wait for the blocker". Whether that is net-positive is exactly the question D171a and
D176a were built to answer and it cannot be answered from the fuzz panel.

### 7.2 Blast radius on everything built on the frozen parent **[M] / [P]**

Changing the parent bytes at all:

1. **Invalidates every gate baseline.** `fuzz_panel.compile_bot` hard-checks
   `parent.sha256` against the file and raises `PanelError` on mismatch (**[M]**, read at
   `fuzz_panel.py:964`). `claude_1/pipeline/fuzz-panel-config.json` pins
   `a8eb3b2b…`. Every committed floor number — the 118/240 here, the 118/116/146 in
   `claude_1/pipeline/verification/`, every per-detector floor in the gate re-design
   proposal — becomes a number about a bot that no longer exists.
2. **Invalidates the banana wrapper's insert-only construction.**
   `integration-seam-2026-08-04.md` **[P]** states the transform must be
   `parent + inserted strings at unique anchors`, with the inverse being deletion of those
   exact strings; every anchor and collision count in that document was "measured against
   this exact file" (62,725 bytes, `a8eb3b2b…`). A parent edit re-opens all five insertion
   anchors and the compactor-idempotence claim.
3. **Invalidates P3 orchard byte-inertness as currently framed.** P3 requires
   candidate commands == parent commands on orchard-eligible maps (**[M]**,
   `eval_p3`). A repaired parent changes the reference, so P3 must be re-baselined; and
   because D1-A fires on `orchard_eligible` maps at 31 % (§6.3), a D1-A repair **will**
   change orchard-map commands.
4. **Requires a fresh arena qualification.** The parent is a shipped, arena-rated bot. Any
   inner-policy change is a new bot. Per D171a's record **[P]**, promotion of any qualified
   oscillation successor "needs a NEW owner authorization".
5. **Consumes a validation budget.** The only rating-capable instrument is the 2,048-task
   paired panel; D171a and D176a each consumed a sealed 128-seed range
   (9,853,000–127 and 9,857,000–127, both recorded as consumed).

**[I]** Estimated cost of a *credible* D1-A repair: build + unit tests + a 2,048-task paired
panel + gate re-baselining + wrapper re-anchoring — comparable to D171a or D176a, each of
which was a full experiment cycle, and both of which closed.

---

## 8. Verdicts

| cluster | episodes | verdict | evidence that drove it |
|---|---|---|---|
| **D1-A** same-tree contention × memoryless detour tie-break | 34 / 35 | **FEASIBLE_WITH_CONDITIONS** | Reachable in principle: one unique insertion site, and the failure modes of both prior attempts (stale arm; run fragmentation) are structurally absent from a memoryless "no futile detour" guard. Conditions: (i) a 2,048-task paired-panel non-regression result, (ii) new owner authorisation, (iii) full gate + wrapper re-baselining. **Not** feasible by the route already tried — D176a, the best breaker built, would have *doubled* the D-1 episode count (§5.4). |
| **D1-B** goal-selector two-cycle | 1 / 35 | **UNRESOLVED** | Mechanism measured (disjoint per-phase goal sets, empty intersection) but not localised in source; n = 1. Needed to settle it: instrumented replay of `m085` seat 0 turns 17–23 with the goal-selector scores exposed — which requires building a debug variant of the bot, out of scope here. |
| **D-1 overall** | 35 | **UNRESOLVED** | A raw-zero rule is conjunctive over episodes. D1-A being feasible-with-conditions does not make D-1 = 0 feasible while D1-B is unlocalised. One unfixed episode is a block. |
| **D-4** single-door bank serialisation | 6 / 6 | **FEASIBLE_WITH_CONDITIONS** | One root cause, one discriminator (`doors.len()==1`, 6/6 vs 0/210), one gated function, one insertion site. Conditions: (i) evidence the hold is not load-bearing on 1-door maps, (ii) same re-baselining and authorisation costs. |

### Overall

**`UNRESOLVED`, leaning `INFEASIBLE` at acceptable cost.**

Not "infeasible" flatly: D-4 is a clean, small, well-understood target, and D1-A has an
untried and structurally sound repair direction. But raw zero on **both** detectors is not
demonstrated to be reachable, because (a) D1-B is unlocalised and one episode blocks, and
(b) the only measured attempts at D1-A's mechanism both failed their frozen mechanism gates,
with the better one increasing the very quantity the rule counts.

Single strongest piece of evidence: **§5.4 — D-1's threshold (`streak >= 5`) is byte-for-byte
the lower edge of D171a/D176a's `run_5_9` bucket, and D176a moved that bucket 213 → 825
(+287 %) while leaving the worst-case run at 247 turns unchanged. The best oscillation
breaker this project has built would have more than doubled the parent's raw D-1 count.**

---

## 9. Recommendation to the owner

Presented as options, with the evidence for each. The decision is the owner's.

**Option 1 — Repair D-4 only; do not repair D-1. RECOMMENDED as the highest-value
action if any repair is authorised.**
D-4 is 6 episodes, one root cause, one gate condition, one function, one insertion site, and
the affected population is 12.5 % of maps. It is the only part of this scope that is small,
fully understood, and not contradicted by prior experiment. It does **not** achieve the
ruling on its own.

**Option 2 — Repair the detector/harness for D-1's benign cluster, not the bot.**
This is supported by the evidence, and it is a narrower claim than "relax the rule".
`detect_d1` counts an idle unit that jitters between two cells identically to a unit
deadlocked while productive work exists. §5.1 measures that the first case is 21/35 episodes
and 80 % of oscillating turns on this parent. A predicate refinement — *no D-1 episode where
the unit has no reachable resource action other than one an own unit is occupying* — is
world-state grounded, parent-independent, uses no parent comparison, and introduces no
invisible masking. It is the same species of repair as P4 repair #2 (2026-08-06), which the
owner has already accepted, and which took P4 from 204 to 30 windows by exactly this kind of
terminal-state calibration. **[I]** Applying it would take D-1 from 32 blocking games to **13** — the number of games retaining at least one episode in which an alternative reachable plant existed (measured, §5.1 buckets).
Caveat, stated against my own recommendation: this is a change to `trace_detectors.py`, which
the gate re-design proposal §5 explicitly refers to integrator/owner scope and which I have
not made and must not make. It also does **not** reach zero — the 12 probable-defect episodes
and D1-B remain.

**Option 3 — Full D-1 repair on this parent. NOT recommended.**
Two frozen-protocol attempts, both closed; the better one would double the raw D-1 count;
value in both was statistically indistinguishable from zero (+0.053 and +0.045 mean margin,
both CIs straddling zero); and the change invalidates every gate baseline, the banana
wrapper's insert-only anchor set, and P3's byte-inertness reference. The measured upper bound
on recoverable productive time is 650 unit-turns over 240 games ≈ **2.7 turns/game**, and
that is an upper bound because it assumes every alternative target was worth taking.

**Option 4 — "this parent cannot reach raw zero; a different parent or a relaxed rule is
required."** This is where the evidence points if Options 1–2 are declined and Option 3 is
correctly priced. Two supporting facts. First, a candidate in this lineage has already been
measured at **D-1 = 0 games / 0 episodes** — chatgpt_1 tip `7ad9d784`
(`claude_1/pipeline/verification/fable-verify-7ad9d784-calibrated.md`, **[P]**) — so raw D-1
zero is not impossible in principle; but the same run measured **D-4 = 35 games / 46
episodes**, **D-7 = 35 / 67**, **P4 = 79**, and BLOCK **146/240**, i.e. clearly worse than the
parent's 118. Raw-zero on one detector was bought at a large price on the others. Second and
more fundamental: **driving D-1 and D-4 to zero moves the floor only from 118 to 106
blocking games** (§1). The ruling, satisfied perfectly, does not produce an acceptable gate.

**What I would not do:** treat D-1's episode count as a quality metric to be optimised. §5.4
shows the metric is fragmentation-sensitive — an intervention that genuinely reduces the
worst behaviour (long runs 174 → 59 tasks) *increases* the count. A threshold-at-zero rule on
this predicate rewards the wrong shape of fix.

---

## 10. UNRESOLVED items and the evidence that would settle each

1. **D1-B's source location.** Settled by: an instrumented debug build of the parent that
   logs the selected target per unit per turn, replayed on `m085` seat 0 turns 17–23.
   Requires building a bot variant — out of scope for a read-only scoping task.
2. **Whether the 12 "alternative existed" D1-A episodes are true defects.** The alternative
   plant may be an opponent crop, unripe, out of ETA, or claimed. Settled by: exposing the
   parent's own candidate scores for the alternative cells at those turns (same debug build).
3. **Whether the D-4 single-door hold is load-bearing.** Settled by: a paired panel restricted
   to 1-door geometries comparing hold vs no-hold margin.
4. **Real-play benign/defect split for D1-A.** My 21/35 is synthetic and §6.4 argues it
   over-states benignity. Settled by: applying the §5.1 alternative-target measurement to the
   18 real B3.4 games.
5. **Arena-rating effect of any repair.** Not measurable by `fuzz_panel.py` at all. Settled
   only by the 2,048-task paired panel (`rust/src/bin/d171a_oscillation_breaker_panel.rs`),
   with a fresh sealed seed range and new owner authorisation.
6. **Uniqueness of the constant-goal model in §2.3.** The model reproduces 34/35 episodes
   exactly, but a two-goal model could also fit. Settled by the same debug build as (1).

---

## Appendix — reproducing every number in this report

Scratchpad (session-local, not committed):
`/tmp/claude-1000/-home-tarstars-prj-troll-farm/3b336b91-cd2f-4655-9aaf-31fd6d3d156f/scratchpad/feas/`

| script | produces |
|---|---|
| `floor-config.json` | the run config (generator inlined in §1; sha `47e35c7e…`) |
| `extract.py` → `episodes.json` | all 41 D-1/D-4 episodes with ±3-turn context |
| `geom.py` → `geom.json` | oscillation-pair geometry, peer occupancy, exits |
| `cluster.py` → `d1_clusters.json` | §2.2 occupancy signature |
| `resolver_fit.py` → `resolver_fit.json` | §2.3 constant-goal resolver replay |

All are pure python3.12 stdlib and deterministic; all read only
`games-floor/games.jsonl.gz` (decompressed sha256 `aaec8ca8a22d6a0fb91429a64d1391d5f95bd144bee340262836b5e80d159889`)
and the committed `trace_detectors` / `fuzz_panel` modules. Regenerating the archive from
§1's command reproduces that hash byte-for-byte.

Nothing in `cgauto/`, `rust/`, `claude_1/pipeline/fuzz_panel.py`,
`claude_1/banana-restoration-r2/trace_detectors.py`, any candidate, or the parent was
modified by this work. `git status` on those paths is clean.
