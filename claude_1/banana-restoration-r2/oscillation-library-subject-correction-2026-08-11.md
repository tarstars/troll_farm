# Oscillation situation library — subject correction, and a parent-lineage comparison

- Author: `claude_1`, 2026-08-11. Branch `agent/claude_1-banana-restoration-r2`
  at `1ac52281`; `origin/main` at `5d679d22`; `origin/agent/chatgpt_1` at
  `0b493294`.
- **This document corrects a published defect of my own.** My committed
  `oscillation-library/` was harvested from the wrong program. It is not
  deleted, not rewritten and not re-scoped: it is now *labelled*, and the
  correct-subject library is published beside it.
- Deliverables:
  `claude_1/banana-restoration-r2/oscillation-library-98628e98/` (the new tree:
  `library/` with 34 frozen situations + `index.json`, `panel-config.json`,
  `build_subject_library.py`, `README.md`), plus the retargeted loader
  `oscillation_library.py`, the extended suite `test_oscillation_library.py`
  (88 tests), the labelling of `oscillation-library/index.json`, and this
  report.
- **This is not M3b.** No best action, preferred action, ranking,
  recommendation, verdict, fix or remedy is recorded anywhere in either tree.
  §7.

Every quantitative claim below is tagged **MEASURED**, **INFERRED** or
**UNRESOLVED**, with the exact command and the SHA-256 of every input.

---

## 0. The defect, stated plainly

`oscillation-library/` was published as the deliverable of manifest item
**M3a**, whose named subject is

```
readable__no_orchard = cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs
sha256 98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29
```

**MEASURED.** Of its 33 frozen situations, 32 carry
`provenance.bot_source_sha256 = a8eb3b2b…` — the *parent*,
`candidate-agent6553250-preseed-orchard-coverage-slim.min.rs` — and one (the
`REAL_CORPUS` record) carries `f26e3781…`, a third program. **Zero come from
the subject.**

```
python3 - <<'EOF'
import json,collections,glob
print(collections.Counter(json.load(open(p))["provenance"]["bot_source_sha256"][:8]
      for p in glob.glob("claude_1/banana-restoration-r2/oscillation-library/OSC-*.json")))
EOF
# -> Counter({'a8eb3b2b': 32, 'f26e3781': 1})
```

Two published consequences follow and are respected here rather than argued
away:

1. My "47 episodes / 33 situations" was never comparable with `chatgpt_1`'s
   34/32. Different programs, not a method disagreement.
2. My headline — *all 20 terminal ≥62-turn D-1 episodes have an idle blocker;
   none with a working blocker reaches 62* — was a claim about the **parent**.

What was accepted was the **method**. It is reused here unmodified (§3).

---

## 1. The subject, pinned

**MEASURED.** The subject is not present in this branch's working tree; it is
read from `origin/main`.

```
git show origin/main:cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs \
  | sha256sum
# -> 98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29
git show origin/main:cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs | wc -l
# -> 1475
```

It is materialised at an absolute scratch path solely so the panel can compile
it; the pinned identity is the digest and the git ref, both recorded in
`panel-config.json` and in every frozen situation's
`provenance.bot_source_git_ref` / `provenance.bot_source_sha256`.

| input | SHA-256 |
|---|---|
| subject `submitted-agent6593838-readable-no-orchard.rs` | `98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29` |
| `oscillation-library-98628e98/panel-config.json` | `eca5cb32e8fc5daa61dd69d0753f9a3962eff5cbce10cf12e8410ba36c903fe5` |
| `claude_1/pipeline/fuzz_panel.py` | `d8900abf31dd030d07096e9a063365aa0e1f58b85a1613d02b07d3935c523a6a` |
| `claude_1/banana-restoration-r2/trace_detectors.py` (unmodified) | `59dce10dc87797bc6b1b8da0f628f4ddd82b561d93946fa91453d2ea40805209` |
| `build_oscillation_library.py` (the accepted method, unmodified) | `4b9fce4ca49a6ce05b4f3f8cb8f7b81d78b7da3c863a4e1ad32fdd2f16aff9df` |
| `oscillation-library-98628e98/build_subject_library.py` (new driver) | `9f9807a8648e4a83b7f56e188e0a9b98a1bd94d57480903f9e9964c1b624a084` |
| panel output `games.jsonl.gz` | `e84fb9f3a3d89e885ed01b95fbc81eced76d347ba46312d5774a95aa2740dc39` |
| **subject `library_sha256`** | **`1370384da9cad46e4f60617b2c9edd076de6ffd9f26d30d0066528de414f9174`** |
| parent-lineage `library_sha256` (unchanged) | `5858d35122973f017374ed2136aa2855e8e2ace68114b1e8e6f52759e0136c61` |

Host: `rustc 1.97.1 (8bab26f4f 2026-07-14)`, `Python 3.12.3`, stdlib only, no
pytest.

---

## 2. The floor run — the subject judged against itself

`panel-config.json` is a copy of `claude_1/pipeline/fuzz-panel-floor-config.json`
with **both** `candidate.source` and `parent.source` repointed to the absolute
path of the `98628e98` file, distinct crates
(`m3a_subject_98628e98_seat_a` / `_seat_b`), a fresh `games_dir`, and
`run_identity: floor` retained. Seeds, maps, turns, class mix, opponent mix,
liveness window and every other calibration field are untouched.

**MEASURED.** Command, exactly as run:

```
PATH=~/.cargo/bin:$PATH python3 claude_1/pipeline/fuzz_panel.py \
  --config claude_1/banana-restoration-r2/oscillation-library-98628e98/panel-config.json \
  --report <scratch>/floor-report.md --json <scratch>/floor-packet.json
# -> fuzz_panel: BLOCK [floor run] (240 games, 119 blocking, 0 flagged,
#                0 gate-unready, 14.7 s)
```

The floor identity is **machine-checked, not asserted**: `load_config` →
`_check_run_identity` (`fuzz_panel.py:2098`) requires a `floor` config's
candidate bytes to equal its parent bytes. The emitted packet records
`run_identity: "floor"`, `candidate_sha256 == parent_sha256 == 98628e98…`,
`instrument_version fuzz-panel/5-two-player-phase-merged-referee`,
`corpus_version c5-two-player-phase-merged-2026-08-11`, and every one of the
240 rows carries `run_identity: floor`.

**MEASURED.** Detector totals over the 240-game subject floor, in *episodes*:

| D-1 | D-2 | D-3 | D-4 | D-5 | D-6 | D-7 | D-8 | D-9 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **38** | 0 | 0 | 6 | 1 | 15 | 0 | 0 | 196 |

D-1: **38 episodes across 35 game rows**. P4: **27 games fail P4**, of which
**8 have no D-1 at all**. Only D-1 and P4 are oscillation/liveness instruments
and only those were harvested.

---

## 3. The method is unchanged; three provenance corrections are not method

`build_subject_library.py` is a thin driver. It **imports and calls
`build_oscillation_library` unmodified** — the harvest, the classifier
(`m3a-observational/1`), the idleness criterion (wait fraction ≥ 0.95 **and** 0
cell changes over the window), the dedupe key, the freezing discipline and the
integrity hashing are all the accepted code, byte-for-byte. It changes three
things, all of them provenance:

1. **The subject.** Both panel sources are `98628e98`. The driver refuses to
   build if any harvested situation carries a different `bot_source_sha256`, or
   if the config is not a `floor` run of the subject.
2. **The provenance note.** `harvest()` writes a fixed sentence, *"the arena
   parent judged against itself"*. True of the parent tree, **false here**; it
   is replaced per situation with one naming the subject and its git ref, and
   `bot_source` is recorded as the `origin/main` git ref rather than the scratch
   absolute path the compiler was handed.
3. **The real-corpus record is excluded.** `harvest()` appends the Elost
   same-tree deadlock as a `PARTIAL` `REAL_CORPUS` situation. Its own committed
   result file names its bot as
   `candidate-agent6585739-owner-tent-banker-commitment-slim.min.rs`
   (`f26e3781…`) — a **third** program. A library declaring `98628e98` as its
   subject may not contain it. It is dropped from this tree, not deleted from
   the repo; it remains in the parent tree, now correctly labelled. The
   exclusion is printed by the build and recorded in `index.excluded`.

Nothing in classification, window, world state, command line, detector counts or
dedupe input is touched by the driver.

**MEASURED.** Command, exactly as run:

```
cd claude_1/banana-restoration-r2/oscillation-library-98628e98
python3 build_subject_library.py --games <scratch>/games/games.jsonl.gz
# -> EXCLUDED (not the subject): REAL_CORPUS from bot f26e3781e972006c
# -> harvested 46 subject episodes -> 34 frozen situations
#    (library_sha256 1370384da9cad46e4f60617b2c9edd076de6ffd9f26d30d0066528de414f9174)
```

---

## 4. What is in the correct-subject library — MEASURED

| | |
|---|---|
| frozen situations (files, excluding `index.json`) | **34** |
| episodes represented (sum of multiplicities) | **46** = 38 D-1 + 8 P4-only |
| `library_sha256` | `1370384da9cad46e4f60617b2c9edd076de6ffd9f26d30d0066528de414f9174` |
| completeness | **34/34 FULL** — no `PARTIAL`, no invented state |

| mechanism | situations | episodes |
|---|---:|---:|
| **M1** — corridor block | 11 | 11 |
| **M2** — stationary occupation invisible to planning | 14 | 19 |
| **M3** — scorer cycle | 1 | 1 |
| **UNCLASSIFIED** | 8 | 15 |
| **total** | **34** | **46** |

| blocker | situations | episodes |
|---|---:|---:|
| **IDLE** | 17 | 22 |
| **WORKING** | 8 | 8 |
| **NONE** (M3, unstable peer, or a stall) | 9 | 16 |

| kind | situations | episodes |
|---|---:|---:|
| `D1_EPISODE` | 30 | 38 |
| `P4_STALL` | 4 | 8 |

D-1 episode length over the 38 episodes: **min 7, median 74, max 195**; 20 are
≥ 62. Multiplicity distribution: 27 ×1, 3 ×2, 3 ×3, 1 ×4.

### 4.1 The freeze is real — MEASURED

```
OSC_LIB_REPLAY=1 PATH=~/.cargo/bin:$PATH python3 -m unittest test_oscillation_library
# -> Ran 88 tests, OK (skipped=1)
#    replay: library -- 34/34 FULL situations reproduce their frozen
#            command window byte-for-byte (0 skipped: older corpus)
```

Every situation was replayed from **its own literal data** — the frozen
`static_map_rows`, `initial_world_state.plants` / `.units` / `.inventories.own`
and `provenance.opponent_profile` fed straight into `fuzz_panel.make_referee`,
**no call back into the map generator** — the subject was run closed-loop, and
the resulting command lines were compared with the frozen window. **34 of 34
reproduce byte-for-byte; 0 mismatches.**

Default run is stdlib-only and takes ~0.6 s:
`python3 -m unittest test_oscillation_library` → **88 tests, OK (skipped=2)**.

### 4.2 A finding produced by that same gate

**MEASURED, and it is a real limit, not a nuisance.** The parent tree's replay
test, which passed 32/32 when that tree was published, now **cannot run**: the
tree was frozen under corpus `c3-train-engine-authority-2026-08-09` and
`make_referee` is always the *current* panel, `c5`. Rather than let it fail or
quietly pass, the test now compares `provenance.corpus_version` with
`fuzz_panel.CORPUS_VERSION` and skips with the reason stated:

```
skipped "every FULL situation in oscillation-library was frozen under a corpus
 other than the running panel's c5-two-player-phase-merged-2026-08-11
 (32 skipped); replay is not meaningful across a corpus bump"
```

The parent tree's byte-exact replay claim is therefore **historical**, true of
c3 and not re-verifiable today. The subject tree is c5 and verifies now.

### 4.3 Fail-closed integrity — DEMONSTRATED on the new tree

The whole mutation suite is re-run against the subject tree by overriding one
class attribute, so it gets the *same* guarantees, not a weaker restatement:
`TestSubjectIntegrityFailsClosed` really mutates a scratch copy eleven ways —
moving a unit, flipping a mechanism, appending a space to a command line, a
self-consistent forgery that re-signs the file, one that also rewrites the index
entry, deleting a file, adding an unindexed file, bumping the declared count,
zeroing the library hash, dropping `bot_source_sha256`, nulling a FULL world
state — and shows `load_library` raising `IntegrityError` and returning nothing
each time, with `test_the_unmutated_copy_loads` as the control so none can pass
vacuously.

New in this tree, `TestSubjectIdentity` makes the *identity* defect a test
failure rather than a reading error: every situation must carry
`bot_source_sha256 == 98628e98…`; neither `a8eb3b2b…` nor `f26e3781…` may appear
anywhere in any file; the index must declare the subject and `run_identity:
floor`; the panel config must be a floor run of the subject against itself with
identical sources and distinct crates; and no `REAL_CORPUS` record may be
present.

---

## 5. The idle-blocker claim, re-tested on the correct subject

### 5.1 The answer: **it holds. MEASURED.**

Cross-tabulating the **38 subject D-1 episodes** by blocker state and the ≥ 62
turn threshold:

| | ≥ 62 turns | < 62 turns |
|---|---:|---:|
| blocker **IDLE** | **20** | 2 |
| blocker **WORKING** | **0** | 8 |
| no blocker established | **0** | 8 |

**Every one of the 20 terminal episodes has an idle blocker; not one episode
with a working blocker or no blocker reaches 62 turns.** The parent-lineage
number was 20 / 3 / 0 / 7 / 0 / 6. The load-bearing cells — 20, 0, 0 — are
identical.

`blocker_state` is part of the dedupe key, so every member of a group was
independently measured to the same state; the episode-level tabulation is
therefore sound, not an imputation from the representative. Asserted as a test
(`TestSubjectIdleBlockerCrossTab`), so a re-harvest that changes the answer
fails loudly instead of silently contradicting this report.

### 5.2 Exactly which field carries the evidence

`chatgpt_1` reports the base panel it was given carries **no blocking-peer
identity or position history**, and that is correct — §6.3. This extraction
*can* settle the claim because it freezes the peer's behaviour, not just the
oscillator's. The evidence is, in order of derivation:

**Primary (raw, per-turn):**

- `window.commands[].line` — the **verbatim command line for every turn of the
  window**, for *all* units, both the oscillator and the blocker.
- `world_state_at_entry.units[]` and `initial_world_state.units[]` — every unit
  of **both** players in the 14-field wire shape, so positions are literal.

**Derived (stored, and re-derivable from the primary):**

- `classification.blocker.wait_fraction_in_window` — component 1 of the
  criterion;
- `classification.blocker.distinct_cells_in_window` — component 2;
- `classification.blocker.non_wait_verbs_in_window` — what it was doing instead;
- `classification.blocker.idle_by_analysis_criterion` — the conjunction;
- `classification.blocker_state` — `IDLE` / `WORKING` / `NONE`;
- `classification.all_own_peers_at_entry` — the same measurements for **every**
  own peer, so the classification can be re-adjudicated without a re-run.

**MEASURED — the derived fields are not taken on trust.**
`test_the_blocker_wait_fraction_is_rederivable_from_the_frozen_window`
recomputes each blocker's wait fraction from the situation's own verbatim
command lines and requires agreement: **0 mismatches over all 30 D-1 situations
that have a blocker.**

All 20 terminal episodes resolve to blockers with
`distinct_cells_in_window == 1` and `wait_fraction_in_window` between **0.98 and
1.00** (18 at exactly 1.00 with `non_wait_verbs_in_window == []`; two at 0.99 /
0.98 with a single `CHOP`).

### 5.3 What is still INFERRED

Unchanged from the accepted method, and recorded in each affected situation's
`unresolved` list: the **M1/M2 discriminator** is inferred, because the goal the
bot actually held is not observable in a transcript; and the **M3 attribution**
to a specific pricing branch is taken from the mechanism analysis, not measured
here. Settled by an instrumented build or the Decision Packet — out of boundary
for M3a, which may not modify any bot.

---

## 6. Three-way reconciliation with `chatgpt_1`

### 6.1 Do I reproduce 34 / 32 and the ledger SHA? **Yes, exactly. MEASURED.**

Running `chatgpt_1`'s own extractor on `chatgpt_1`'s own base panel:

```
git show origin/agent/chatgpt_1:local_claude_1/verification/readable-no-orchard-oscillation-2026-08-08.json \
  > base-panel.json          # sha256 b42fb8a7ae2c26af7e52dd18128a04bf221a794fbffe52e63d57b47122332e69
git show origin/agent/chatgpt_1:chatgpt_1/m3a_extract_from_panel.py \
  > extract.py               # sha256 f4b493de50d681fe0c65c432e584de0cfc34eaa6c8617d6a4dded9f47fc290e0
python3 extract.py --input base-panel.json --check --output repro.json
```

| measure | `chatgpt_1` published | my reproduction |
|---|---:|---:|
| panel games | 240 | **240** |
| D-1 episodes | 34 | **34** |
| game-row situations | 32 | **32** |
| episodes ≥ 62 states | 20 | **20** |
| situations with such an episode | 19 | **19** |
| `episode_ledger_sha256` | `8e05b8ae…fffc5d` | **`8e05b8aeb9fa90449819558f2c638a358f9c8667c35ea28d2fc2788b02fffc5d`** |

`--check` exits 0. Their arithmetic is exactly reproducible.

**One divergence, minor and worth recording. MEASURED.** The committed ledger
`chatgpt_1/m3a-d1-situation-library-2026-08-10.json`
(`fd25806039521c895c89351761f2125f6c92bfadde236612ba0e4daba7e52963`) is *not*
byte-identical to what the committed script now emits. `diff` of the two, both
canonicalised, is **exactly one line**: the committed blob's `summary` lacks the
`episode_ledger_sha256` field the script now writes. Everything else — all 32
situations, all 34 episodes — is identical. The blob and the script are one
revision apart; the digest itself reproduces. No count is affected.

### 6.2 Do my *own* counts equal 34 / 32? **No — 38 / 35. That is the finding.**

**MEASURED.** Applying `chatgpt_1`'s counting rule verbatim (their script, my
panel packet) to the subject floor I ran:

| measure | `chatgpt_1` base panel | my c5 subject floor |
|---|---:|---:|
| D-1 episodes | 34 | **38** |
| game-row situations `(map_id, seat, attempt)` | 32 | **35** |
| episodes ≥ 62 states | 20 | **20** |
| situations with such an episode | 19 | **19** |
| `episode_ledger_sha256` | `8e05b8ae…` | `f739b66b4b87102419c01aa8bbc85f0dcf82c17f0bc0df96238e22132d69162c` |

Same bot, same seeds, same 240-game recipe, same detector — **different
referee**. Row-level divergence, MEASURED:

- rows only in the base panel: `m005 s1`, `m088 s1`;
- rows only under c5: `m025 s1`, `m028 s1`, `m040 s1`, `m058 s1`, `m068 s1`;
- 8 rows present in both with a **longer** c5 window on the same unit and the
  same two cells (e.g. `m085 s0 u0 (1,4)↔(2,4)`: 17–23 → 17–25;
  `m079 s1 u2`: 33–197 → 33–200; `m092 s0 u0`: one episode 2–36 becomes two,
  2–54 and 77–83).

The direction is consistent: the c5 two-player phase-merged referee merges both
seats into one `engine.rs::step` transition, so contention persists longer and
alternations run longer. This is a **corpus-version difference, not a method
disagreement, and not an error by either agent.**

### 6.3 The sharpest number in the reconciliation

**MEASURED.** Compare the D-1 *game-row* sets three ways:

| population | D-1 game rows |
|---|---:|
| parent `a8eb3b2b` @ c3 (my old library) | 33 |
| subject `98628e98` @ c5 (this library) | 35 |
| subject `98628e98` @ base panel 2026-08-08 (`chatgpt_1`) | 32 |

- parent @ c3 vs subject @ base: symmetric difference = **exactly one row,
  `m040 s1`**;
- subject @ c5 vs subject @ base: 7 rows;
- subject @ c5 vs parent @ c3: 6 rows.

**INFERRED, with strong measured corroboration.** The base panel declares no
`instrument_version` and no `corpus_version` at all — it predates the
fail-closed declaration requirement (review B7) and is dated 2026-08-08, before
the c1→c2 TRAIN repair of 2026-08-09. The one row that separates it from the
parent's c3 population is `m040`, which is *precisely* the row
`fuzz-panel-floor-config.json` declares `instrument_invalid` under
`c1-silent-train-2026-08-09` ("TRAIN emitted on 166 / 182 of 200 turns … and the
game still scored CLEAN"). MEASURED: in the base panel `m040` seats 0 and 1 are
both all-zero and `block=False`; under c5 seat 1 blocks with D-1 and P2. The
signature matches exactly.

Two consequences, and I state both because one is uncomfortable for me:

1. **`chatgpt_1`'s 34/32 is arithmetically exact but is derived from an
   instrument the current panel would refuse.** Their reasoning is sound; the
   artefact they were handed as sufficient is not calibration-eligible today.
   That is not a criticism of their work — it was the artefact the assignment
   named.
2. **The parent and the subject produce D-1 populations this instrument cannot
   distinguish.** Every row-level difference I can see between the parent's c3
   library and the subject's populations is attributable to a referee change,
   not to the program. The episode-level mechanism and blocker histograms are
   near-identical (M1 11 / M2 20 / M3 1 / UNCL 15 vs M1 11 / M2 19 / M3 1 /
   UNCL 15; IDLE 23 / WORKING 8 / NONE 16 vs IDLE 22 / WORKING 8 / NONE 16),
   and all four named cases land on the same mechanism and the same blocker
   state on the subject (§6.4).

**UNRESOLVED.** Whether the two programs are behaviourally distinguishable on
this corpus at all. I ran the subject at c5 only; I did **not** run the parent at
c5, so bot and corpus are not fully separated. Settled by one further floor run
of `a8eb3b2b` under c5 and a row-set diff against this library. I did not run it
because it is not needed for the subject correction and would add a second
240-game floor to the record for a question nobody has asked.

This does **not** rehabilitate the old tree. The identity claim it made was
false, its `REAL_CORPUS` record is from a third program, and its replay claim is
no longer verifiable. That the substantive findings *survive* the correction is
now a **measured** result rather than an assumption — which is the entire point
of having done the re-extraction.

### 6.4 The named cases, on the correct subject — MEASURED

`TestSubjectNamedCases` asserts each against the frozen data.

| case | frozen as | mechanism | blocker | window (c5) | parent-tree window (c3) |
|---|---|---|---|---|---|
| `m110` s1 u0 | `OSC-001` | **M1** | **IDLE** (u2 @ (4,2), wait 1.00, 1 cell, no plant) | 6–200, 195 turns | 6–200, 195 turns |
| `m040` s1 u0 | `OSC-010` | **M1** | **WORKING** (u6, `CHOP`) | 80–86, 7 turns | 80–86, 7 turns |
| `m014` s1 u2 | `OSC-017` | **M2** | **IDLE** (u0 on a live plant, wait 1.00) | 7–200, 194 turns | 7–200, 194 turns |
| `m085` s0 u0 | `OSC-026` | **M3** | **NONE** (one own unit) | 17–25, 9 turns | 17–23, 7 turns |

All four land on the same mechanism and the same blocker state as the mechanism
analysis `oscillation-attack-claude_1-2026-08-09.md` — which was itself written
about `98628e98`. The only change is `m085`'s window, two turns longer under c5.

---

## 7. Scope guard — no best action is recorded. MEASURED.

`TestNoBestActionRecorded` and `TestSubjectNoBestActionRecorded` walk **every
key** of **every** frozen file in **both** trees against a forbidden-key list
(`best_action`, `correct_action`, `optimal_action`, `right_action`,
`recommended_action`, `recommendation`, `should_have`, `verdict`,
`adjudication`, `expected_action`, `ideal_action`, `fix`, `remedy`) and **every
string** against a forbidden-phrase list (`best action`, `correct action`,
`optimal action`, `right action`, `recommended action`, `should have moved`,
`should have waited`, `the bot should`, `the unit should`, `ought to have`), and
assert each index declares the M3a scope limit. Both pass.

The reason is the circularity M3b exists to avoid: every situation here was
found by running the shipped bot and reading its own transcript, so any "the
right move was X" written now would be derived from the same scorer M3b is
supposed to audit independently. **No M3b adjudication is attempted anywhere in
this work.**

---

## 8. The parent tree is labelled

`oscillation-library/index.json` gains **two fields and nothing else**: a
`subject_note` and a `subject` block. No situation file was touched, no
structure changed, nothing deleted.

The note records, in full: that the tree is the parent lineage `a8eb3b2b…`; that
its one `REAL_CORPUS` record is from `f26e3781…`; that **zero** situations come
from the subject `98628e98…`; that it **must not be cited as M3a**; that its
47/33 is not comparable with `chatgpt_1`'s 34/32; that its ≥62-turn headline is a
claim about the parent; and where the correct-subject library and this
correction live. `subject.is_m3a_subject` is `false` and
`subject.m3a_subject_is` points at `98628e98…`.

**MEASURED — the label changed nothing else.** `library_sha256` is computed over
the `(id, content_sha256)` pairs, so an index-only edit cannot mask a touched
situation:

```
5858d35122973f017374ed2136aa2855e8e2ace68114b1e8e6f52759e0136c61   before
5858d35122973f017374ed2136aa2855e8e2ace68114b1e8e6f52759e0136c61   after
```

and the tree still loads 33 situations clean. `TestParentLineageIsLabelled`
asserts the note's content, the unchanged digest, the unchanged count, and that
`oscillation_library.DEFAULT_DIR` now resolves to the **subject** tree so an
unqualified load returns the M3a deliverable.

---

## 9. Verification, reproducible end to end

```
# 1. pin the subject
git show origin/main:cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs \
  | sha256sum   # 98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29

# 2. the floor run (both sources = the subject; run_identity floor is enforced)
PATH=~/.cargo/bin:$PATH python3 claude_1/pipeline/fuzz_panel.py \
  --config claude_1/banana-restoration-r2/oscillation-library-98628e98/panel-config.json \
  --report r.md --json p.json
#   BLOCK [floor run] (240 games, 119 blocking, 0 flagged, 0 gate-unready)

# 3. harvest
cd claude_1/banana-restoration-r2/oscillation-library-98628e98
python3 build_subject_library.py --games <games_dir>/games.jsonl.gz
#   46 subject episodes -> 34 frozen situations

# 4. integrity
cd .. && python3 oscillation_library.py --dir oscillation-library-98628e98/library
#   OK -- 34 situations, 46 episodes, library_sha256 1370384da9cad46e...

# 5. the suite (stdlib only, ~0.6 s)
python3 -m unittest test_oscillation_library            # 88 tests, OK (skipped=2)

# 6. byte-exact replay (needs rustc)
OSC_LIB_REPLAY=1 PATH=~/.cargo/bin:$PATH python3 -m unittest test_oscillation_library
#   88 tests, OK (skipped=1); 34/34 FULL situations reproduce byte-for-byte
```

---

## 10. Summary of what changed, and what did not

| | old tree `oscillation-library/` | new tree `oscillation-library-98628e98/library/` |
|---|---|---|
| bot | parent `a8eb3b2b` (+1 record from `f26e3781`) | **subject `98628e98`** |
| corpus / instrument | c3 / fuzz-panel/3 | **c5 / fuzz-panel/5** |
| run identity | floor (parent vs parent) | **floor (subject vs subject), machine-checked** |
| situations / episodes | 33 / 47 | **34 / 46** |
| kinds | 27 D1 + 5 P4 + 1 REAL_CORPUS | **30 D1 + 4 P4, no REAL_CORPUS** |
| completeness | 32 FULL, 1 PARTIAL | **34 FULL** |
| ≥62-turn cross-tab | IDLE 20 / WORKING 0 / NONE 0 | **IDLE 20 / WORKING 0 / NONE 0** |
| byte-exact replay | 32/32 at c3; **not re-verifiable at c5** | **34/34 at c5** |
| status | parent-lineage comparison artefact, labelled | **the M3a deliverable** |

Unchanged: the harvest, the classifier, the idleness criterion, the dedupe key,
the freezing discipline, the fail-closed hashing, and the M3a scope guard. The
method was accepted; only the data was wrong, and only the data has been
replaced.
