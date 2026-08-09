# Referee / TRAIN repair — revision r4

- Task: `20260809-referee-train-repair`
- Responding to: `chatgpt_1/referee-train-repair-r3-review-2026-08-09.md`
  (artifact commit `07a37c0b02ac04ccf718d9251eedc3f0721dd8d1`, handoff
  `coordination/messages/chatgpt_1/20260809T073500Z-20260809-referee-train-repair-r3-review-handoff.md`)
- Prior disposition: **`DISPATCH_LAYER_ACCEPTED — PANEL_REVISION_REQUIRED`**, panel `GATE_UNREADY`
- Authority: `rust/src/game/engine.rs` — **untouched**, sha256 `7c240abfcfdf678993960fe73440735a19f934596c9651bdf915e2902f78fb05`
- Instrument: `fuzz-panel/5-two-player-phase-merged-referee`
- Corpus: `c5-two-player-phase-merged-2026-08-11` (bumped from `c4`; c4 retired from calibration)
- Referee sha256: `d8900abf31dd030d07096e9a063365aa0e1f58b85a1613d02b07d3935c523a6a`

This report answers the review's **exact findings** (B1–B6 and the two contract
corrections), not the earlier B1–B11 list. Nothing accepted in r3 was regressed: strict
parse-before-mutate, the full own-command phase order, first non-TRAIN command per unit,
multiple-TRAIN handling, engine-authoritative TRAIN, the Rust-authority differential
design, row retention on unsupported verbs, version fail-closed and the machine-readable
`m040` packet are all still pinned and still green.

---

## 0. Two numbers, never conflated

The review's blocker B5 exists because r3 published one config and quoted two numbers
from it. This report therefore states both, always labelled, and the panel itself now
refuses to let them be confused (§5).

| run | question it answers | config | c4 (before) | c5 (after) |
|---|---|---|---|---|
| **FLOOR** | how many games does the panel block when the candidate **is** the parent? | `fuzz-panel-floor-config.json` | **119** | **118** |
| **CANDIDATE** | how many games does the panel block for banana `eac2eb36` vs parent `a8eb3b2b`? | `fuzz-panel-config.json` | **123** | **121** |

Both "before" figures are **fresh reruns of the committed r3 blob** (`4cd3853d`) in a
detached worktree, not quotations; both packets are committed under
`claude_1/pipeline/evidence-r4/before-c4/`. Both "after" figures are committed under
`claude_1/pipeline/evidence-r4/`. All four runs were verified deterministic (a second run
produces byte-identical JSON apart from wall time). **Nothing was tuned toward any
number**; §7 shows the corpus churn behind these deltas is 37–44%, not 1%.

---

## 1. Disposition per finding

| finding | status | mutation probe | result |
|---|---|---|---|
| **B1** independent execution review absent | **NOT CLOSED — external** (owned by `local_claude_1`) | n/a | reproduction packet in §8 |
| **B2** opponents mutate the world through a second simulator | **CLOSED** | `M11`, `M12` | CAUGHT, CAUGHT |
| **B3** parent protocol failure fails open | **CLOSED** | `M13` | CAUGHT |
| **B4** durable packet loses exact raw output | **CLOSED** | `M14`, `M15` | CAUGHT, CAUGHT |
| **B5** floor is not a committed reproducible packet | **CLOSED** | `M16` | CAUGHT |
| **B6** corpus version cannot be adopted | **CLOSED** (c4 → c5, full rerun) | `M8` | CAUGHT |
| **C-O1** PICK cannot fund TRAIN; DROP cannot either | **CLOSED** (rule implemented, contract correction adopted) | `M2`, `M4` | CAUGHT, CAUGHT |
| **C-C4/C5** invariance is conditional | **CLOSED** (both directions pinned) | `M3` | CAUGHT |

**16 of 16 mutations caught, 0 survived** (`claude_1/pipeline/evidence-r4/mutations-2026-08-11.txt`).
No blocker below is closed by code that no test pins.

---

## 2. B2 — the opponent is now one phase-merged engine transition

### What was wrong

`FuzzReferee.apply()` ran the candidate's eight phases and then called
`OPP_POLICIES[self.profile](self)`. Those policies moved units, decremented `fruits`,
subtracted tree `health`, banked `carry` and deleted plants **directly**, after every
phase, with their own simplified rules. `engine.rs::step` (755-806) cannot produce that
transition at all.

### What r4 does

`engine.rs:755-806` takes **two** command streams:

```rust
pub fn step(game: &mut GameState, cmds0: &[String], cmds1: &[String]) {
    let a = parse_cmds(cmds0);
    let b = parse_cmds(cmds1);
    let mut all_moves = a.moves.clone();
    all_moves.extend(b.moves.iter());          // 760-762
    apply_moves(game, &all_moves);
    ...
    for talents in &a.train { apply_train(game, 0, *talents); }   // 786-789
    for talents in &b.train { apply_train(game, 1, *talents); }   // 790-791
```

The panel now mirrors exactly this:

- `OPP_POLICIES[profile]` returns a **command line for player 1**
  (`opponent_command_line`). A policy decides; it has no privileged access to the world.
- that line goes through the **same** `parse_commands` trust boundary as the candidate's
  (its `used` set is per player, as in the engine, which parses each stream separately);
- `_execute(parsed, opp)` merges the buckets phase by phase — `dict.update` for moves
  (the engine's `HashMap::extend`, so on a duplicate unit the opponent's intent wins) and
  `a`-then-`b` concatenation for the list buckets — and runs `_train_one(..., 0)` for the
  candidate's TRAIN entries and `_train_one(..., 1)` for the opponent's, over one shared
  `next_id`;
- `can_train` / `train` / `_train_one` are parametrised by player: roster count,
  inventory, shack and spawn identity are all read for that player
  (`engine.rs:526-567`);
- `step_toward` still exists (the inherited referee calls it) but **nothing in the panel
  calls it any more** — there is no second navigation path;
- `_act_harvest` and `_act_chop` are deleted.

### The behaviour change this forces, stated plainly

A unit can no longer step onto a plant **and** act on it in the same turn, because
`engine.rs:717-720` keeps only the first non-TRAIN command per unit. Arrival and action
are now two turns for the opponent, exactly as they are for every real bot. This is the
repair, not a side effect, and it is the main reason the corpus churns (§7).

### Evidence

- `TestDifferentialTwoPlayer`: 10 two-player cases (cross-player MOVE contention onto one
  cell; both players TRAIN in one turn; an opponent unit standing on its own shack
  blocking only *that* player's TRAIN; both streams commanding the same unit; both
  chopping one tree; both harvesting one plant; PICK and DROP in one turn; same-cell
  cross-player PLANT merging and mixed-type PLANT cancelling; both mining) compared
  **field for field** against `engine::step(&mut g, &c0, &c1)` compiled from `engine.rs`
  and `state.rs`'s own bytes, and against the independent `sim/engine.py` mirror. Both
  oracles agree with the panel on all ten.
- `test_a_generated_opponent_line_is_engine_conformant`: the line the panel's **own
  policy** emits, executed as player 1's stream through the authority, reproduces the
  panel's post-state.
- `test_the_two_player_oracle_is_not_vacuous`: a deliberately wrong post-state is
  rejected.
- Structural: `test_no_direct_opponent_simulator_remains` fails if
  `OPP_POLICIES[self.profile](self)`, `_act_harvest` or `_act_chop` reappear.
- Corpus: the opponent issues commands in **148 of 240** candidate games (11 329 command
  lines; 9 535 MOVE, 1 600 HARVEST, 1 163 CHOP, 750 DROP), and candidate and opponent
  MOVE to the same target cell in **70 of 240** games (§9).

**Mutations.** `M11` (drop `moves.update(opp.moves)` — i.e. ignore the opponent stream)
→ **CAUGHT** by 6 tests. `M12` (spawn every trained unit as player 0 at shack 0) →
**CAUGHT** by 4 tests, first by the two-player differential.

---

## 3. B3 — parent protocol failure now fails closed

`aggregate_verdict` read only the candidate's `execution_status`, and the parent's
ledger was never copied onto the row — only a bare status string that nothing consumed.

r4:

- `_record_execution(row, ref, seat=...)` runs for **both** seats and writes the complete
  ledger under a `parent_` prefix: `parent_execution_status`,
  `parent_command_errors`, `parent_command_error_counts`,
  `parent_command_error_total`, `parent_error_lines`, `parent_train_events`,
  `parent_spawns`, `parent_opponent_commands_sha256`;
- `row_execution_failed(row)` is the single predicate: **either** seat failing makes the
  row instrument-invalid, and `aggregate_verdict` returns `GATE_UNREADY`;
- `summarize` publishes `parent_instrument_invalid_games` and `gate_unready_games`
  alongside the candidate-side counts, and the report's instrument-invalid table names
  which seat failed.

Tests: `test_aggregate_is_unready_when_only_the_parent_failed`,
`test_aggregate_is_unready_for_a_malformed_parent_command`, and two **end-to-end** planted
runs in both seats — an unsupported-verb parent and a malformed-command parent — that
assert exit 2, `verdict == GATE_UNREADY`, both rows retained in the denominator, and the
parent's error ledger present and internally consistent
(`parent_command_error_total == sum(parent_command_error_counts.values())`).

**Mutation `M13`** (restore the candidate-only predicate) → **CAUGHT** by 7 tests.

---

## 4. B4 — the durable packet keeps the exact raw output

`parse_commands` stripped every fragment before recording `raw`; the retained list was
capped at 50; the full stream lived only in `artifacts`, which `run_panel` drops from the
JSON packet.

r4:

- `split_fragments()` splits on `;` **keeping each fragment's exact `[start, end)`
  character span**, including empty fragments (their placement is evidence);
- every error carries `raw` (the verbatim slice, whitespace included), `span`,
  `normalized` (the whitespace-collapsed form the parser tokenized), `line_sha256` and
  `line_length`, so `line[span[0]:span[1]] == raw` byte for byte;
- the referee retains `error_lines`: the **verbatim stdout line** of every offending turn
  with its sha256 and length;
- the retained error stream is **uncapped** (`MAX_RETAINED_ERRORS` is gone;
  `REPORT_ERROR_ROWS` now bounds only the human-readable markdown table), and
  `command_error_total` is published so truncation would be detectable.

Tests include an end-to-end planted bot whose line is `"  MOVE 0 1 1 ;; FLY 0 ; TRAIN 1 1 1 ;"`
— leading blanks, an empty fragment, an unsupported verb and a malformed TRAIN — and
`test_the_durable_row_can_reconstruct_every_offending_command` reconstructs **every**
offending fragment from the JSON packet alone (line + span), checking the line hash.
`test_the_error_stream_is_not_capped` plants 150 bad fragments and asserts all 150 are
retained.

**Mutations.** `M14` (re-introduce the `strip()`) → **CAUGHT** by 5 tests. `M15`
(re-cap the stream at 50) → **CAUGHT** by 2 tests.

---

## 5. B5 — the floor is a committed packet, and a floor claim from a candidate config is now impossible

Two things were required: commit a distinct parent-versus-parent packet, and make the
mislabelling mechanically impossible rather than discouraged.

**The mechanism.** Every config must declare `run_identity` in the **raw** JSON:

- `floor` — the parent judged against **itself**; `load_config` requires
  `candidate.source` and `parent.source` to hash to the **same bytes**;
- `candidate` — requires them to **differ**.

`_check_run_identity` reads the two sources' actual digests (not the declared strings)
and refuses anything else, including an absent or unknown identity. The identity is then
carried into the report **title**, the `## Verdict:` line, the final `**VERDICT:**` line,
the JSON packet (`run_identity`, plus `candidate_sha256` / `parent_sha256`) and **every
row** (`row["run_identity"]` and `row["provenance"]["run_identity"]`). A number cannot be
relabelled after the fact, and a floor number cannot be produced by a candidate config at
all.

**The packets.** `fuzz-panel-floor-config.json` is committed beside
`fuzz-panel-config.json`; both declare the c5 identity; both were run and both outputs are
committed:

| file | identity | candidate sha | parent sha | verdict | blocking |
|---|---|---|---|---|---|
| `evidence-r4/floor-c5.json` / `.md` | `floor` | `a8eb3b2bb646…` | `a8eb3b2bb646…` | BLOCK | **118** |
| `evidence-r4/candidate-c5.json` / `.md` | `candidate` | `eac2eb36b5f2…` | `a8eb3b2bb646…` | BLOCK | **121** |

**Mutation `M16`** (skip the floor-versus-candidate source check) → **CAUGHT** by 3
tests.

---

## 6. B6 — instrument/corpus bump and full rerun

B2, B3 and B4 each change the instrument's trust envelope, so `c4` cannot enter
calibration. `INSTRUMENT_VERSION` → `fuzz-panel/5-two-player-phase-merged-referee`,
`CORPUS_VERSION` → `c5-two-player-phase-merged-2026-08-11`, and both committed configs
carry an `instrument_invalid_rows` entry retiring the whole `c4` corpus with
`eligible_for_calibration: false` and the reason
(`test_the_c4_corpus_is_retired_as_machine_readable_evidence`). All 240 rows were rerun
for **both** identities.

The `m040` six-part regression packet was **re-measured**, not re-tuned: seat 0's single
TRAIN moves from turn 35 (c4) to turn **33** (c5) because the `harvester` opponent on that
map now strips the shared plants more slowly (it can no longer move and harvest in one
turn), so the floor bot banks its bill two turns earlier. Every other clause — spawn id 6,
talents `(1,1,0,1)`, cell, carry, bill `[2,2,1,0,2,0]`, inventory after, the serialized
unit row, `emissions == [33]`, `command_errors == []`, status `ok` — is byte-identical,
and seat 1 is entirely unchanged at turn 19. Both the old and new values are recorded in
the test file beside the reason.

---

## 7. Floor and candidate: before → after, and the churn behind it

### Floor (parent `a8eb3b2b` judged against itself)

| measure (violation counts) | c4 (before) | c5 (after) | delta |
|---|---|---|---|
| D-1 | 33 | 34 | +1 |
| D-4 | 6 | 6 | 0 |
| D-5 | 1 | 1 | 0 |
| D-6 | 9 | 10 | +1 |
| D-9 | 74 | 74 | 0 |
| P2 | 5 | 5 | 0 |
| P4 | 29 | 28 | −1 |
| **blocking games** | **119** | **118** | **−1** |
| clean games | 121 | 122 | +1 |
| gate-unready games | 0 | 0 | 0 |
| games with a successful TRAIN | 2 | 2 | 0 |

Rows changed in at least one measured field: **89 of 240 (37%)**. Block flips: **7**
(`m005 s1`, `m022 s0`, `m068 s0`, `m088 s1` block→clean; `m025 s1`, `m028 s1`, `m042 s1`
clean→block).

### Candidate (banana `eac2eb36` vs parent `a8eb3b2b`)

| measure (violation counts) | c4 (before) | c5 (after) | delta |
|---|---|---|---|
| D-1 | 32 | 31 | −1 |
| D-4 | 9 | 9 | 0 |
| D-6 | 11 | 10 | −1 |
| D-7 | 1 | 1 | 0 |
| D-9 | 74 | 74 | 0 |
| P2 | 1 | 2 | +1 |
| P4 | 34 | 32 | −2 |
| **blocking games** | **123** | **121** | **−2** |
| clean games | 117 | 119 | +2 |
| gate-unready games | 0 | 0 | 0 |
| games with a successful TRAIN | 2 | 2 | 0 |

Rows changed in at least one measured field: **105 of 240 (44%)**. Block flips: **10**.

The counts above are **violation counts**, not per-game counts (a game can carry several
episodes of one detector); the per-game figures are in the committed reports. The
candidate's margin over the floor is `121 − 118 = 3` blocking games at c5, against
`123 − 119 = 4` at c4 — but the two corpora are not comparable and neither difference may
be quoted across the bump.

---

## 8. B1 — the independent execution review is still open, and this is the packet for it

B1 cannot be closed by me: the frozen acceptance order assigns it to `local_claude_1`,
executing in a second checkout. What r4 can do is make it a mechanical task. Exact
reproduction:

```
git checkout <this commit>
cd claude_1/pipeline
export PATH=$HOME/.cargo/bin:$PATH
python3 -m unittest test_fuzz_panel          # 163 tests
python3 -m unittest test_pre_review          #  24 tests
python3 mutation_drive.py                    # 16 mutations, expect 16 CAUGHT
python3 fuzz_panel.py --config fuzz-panel-floor-config.json \
    --report /tmp/floor.md --json /tmp/floor.json      # expect BLOCK, 118
python3 fuzz_panel.py --config fuzz-panel-config.json \
    --report /tmp/cand.md  --json /tmp/cand.json       # expect BLOCK, 121
python3 witness_scan.py --config fuzz-panel-config.json
```

Byte identities of the artifacts under review:

| artifact | sha256 (16) |
|---|---|
| `fuzz_panel.py` | `d8900abf31dd030d` |
| `test_fuzz_panel.py` | `c0680f86e719bba7` |
| `fuzz-panel-config.json` | `0b65e55cc62f740c` |
| `fuzz-panel-floor-config.json` | `a48c7653c54e2101` |
| `mutation_drive.py` | `17620cb213d989e0` |
| `witness_scan.py` | `c874d5955a30da60` |
| `rust/src/game/engine.rs` (authority, untouched) | `7c240abfcfdf6789` |

The differential oracle is **not skippable**: `rust_oracle_binary()` raises rather than
skip when `rustc` is absent. No differential case is excluded except the named
`SIM_LEG_DEFECTS`, whose exclusion is itself asserted to still fail against leg B for the
documented reason.

Committed run records: `evidence-r4/red-2026-08-11.txt` (the failing-first run: 163
tests, 17 failures, 39 errors, no pre-existing test regressed),
`evidence-r4/green-2026-08-11.txt`, `evidence-r4/mutations-2026-08-11.txt`,
`evidence-r4/witness-census-2026-08-11.txt`, and the four panel packets.

---

## 9. Witness census — what the corpus actually exercises at c5

Measured by `witness_scan.py` (an instrumented replay of all 240 games per identity; every
override delegates to `super()` and only observes). Candidate-run figures; the floor run
is in the same evidence file and agrees qualitatively.

| repaired rule | corpus witness? | evidence (candidate run, 240 games) |
|---|---|---|
| **B2 opponent as a command stream** | **YES — new at r4** | opponent commands on 11 329 turns in **148 games**: 9 535 MOVE, 1 600 HARVEST, 1 163 CHOP, 750 DROP |
| **B2 cross-player MOVE into one cell** | **YES — new at r4** | 141 turns in **70 games** where candidate and opponent MOVE to the same target |
| C4 full phase order | **YES** | 255 lines in **69 games** put a DROP/MINE before an earlier phase |
| TRAIN (r2/r3 repair) | **YES, thin** | 2 games, 1 spawn each (`m040` s0 t=33, s1 t=19) |
| PLANT / MOVE / `next_cell` | **YES, indirectly** | 105 of 240 rows changed a measured field across the bump |
| C5 first non-TRAIN per unit | **NO** | 0 lines repeat a unit id among non-TRAIN commands |
| C2 unsupported verb | **NO** | 0 occurrences |
| C3 malformed command | **NO** | 0 occurrences |
| O2 multiple TRAIN on one line | **NO** | 0 occurrences |
| `near_shack <= 1` (the shack cell itself) | **NO** | 0 PICK/DROP from a shack cell |
| multi-round HARVEST (`hp >= 2`) | **NO** | 0 — no roster in the corpus has `harvest >= 2` |
| CHOP snapshot (fresh tree not felled) | **NO** | 0 |
| speed-0 unit issuing MOVE | **NO** | 0 |
| candidate command naming an opponent unit | **NO** | 0 |
| **B3 parent execution failure** | **NO** | 0 of 480 seat-runs; pinned by planted end-to-end tests only |
| **B4 malformed raw evidence** | **NO** | 0; pinned by the planted `RAW_EVIDENCE_BOT` only |
| **B5 run identity** | **YES** | both committed configs run and both packets committed |

**r3 left 6 of 11 repaired rules unwitnessed; r4 leaves 10 of 17 unwitnessed** — but the
two rules the *review* said were producing false evidence (B2's opponent execution and
B5's identity) are now the most heavily witnessed things in the corpus. The unwitnessed
rules are pinned by unit tests, the two-oracle differential and the mutation drive, and
the floor **must not** be cited as evidence for any of them. The cause is a coverage
limit of the corpus (two real bots, one roster generator that never emits `harvest >= 2`,
no bot that emits malformed output), not a defect in the repairs.

---

## 10. `UNRESOLVED` against `engine.rs`

**Closed at r4:** `UNRESOLVED-r3-A` (the opponent is not engine-driven) — the opponent is
now a command stream merged into one `engine.rs::step` transition and is checked against
the authority's own bytes in both seats.

Still open, declared, none presented as conformance:

- **`UNRESOLVED-r3-B` — `next_id` seeding.** The transcript does not serialize
  `game.next_id`; it is seeded at `1 + max(existing unit ids)`. `engine.rs` guarantees only
  monotonicity (555/567) and has no unit-removal path. Unchanged, previously accepted (A3).
- **`UNRESOLVED-r3-C` — end of game.** The panel runs a fixed 200 turns and never applies
  `engine.rs::has_stalled` (819-868). This is now the largest remaining gap to `step`-level
  conformance.
- **`UNRESOLVED-r3-D` — MSG arity.** `engine.rs:696` treats `MSG` and `WAIT` identically, so
  the engine is silent on whether `MSG hello world` is well-formed. Choice: `MSG` accepts any
  body, `WAIT` must be bare. Stated so a reviewer can overrule it.
- **`UNRESOLVED-r3-E` — the strict trust boundary has no corpus witness.** Still 0 of 240
  (§9). C2/C3 are pinned by unit tests, planted bots and `M1`/`M7`/`M14`/`M15` only.
- **`UNRESOLVED-r4-F` — opponent TRAIN is never exercised by the corpus.** None of the three
  profiles emits TRAIN, so player-1 TRAIN (shared `next_id`, opponent bill, opponent shack
  occupancy) is pinned only by the two-player differential cases and `M12`. It is a real
  engine path with no corpus witness.
- **`UNRESOLVED-r4-G` — the opponent policies are still the panel's invention.** This is not
  an `engine.rs` divergence (the engine specifies no policies) but it bounds what the corpus
  can claim: the profiles are three deterministic scripts, not real bots, so opponent-sensitive
  properties sample three behaviours, not a distribution.
- **`B1`** — the independent execution review, owned by `local_claude_1` (§8).

No bot, candidate, detector predicate, host experiment, `TestSession`, submission, restore
or Arena state was modified. `rust/**`, `cgauto/**` and `claude_1/banana-restoration-r2/**`
were not touched.
