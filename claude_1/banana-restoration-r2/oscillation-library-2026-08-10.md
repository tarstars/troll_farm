# The oscillation situation library — M3a (enumerate and freeze)

- Item: manifest **M3a**, the first half of the owner's manifest point 5
  ("build a library of the situations where oscillation occurred").
- Author: `claude_1`, 2026-08-10. Branch `agent/claude_1-banana-restoration-r2`
  at `975e6365`; `origin/main` at `5476d523`.
- Deliverables: `claude_1/banana-restoration-r2/oscillation-library/` (33
  frozen situations + `index.json`), `oscillation_library.py` (loader +
  integrity check), `test_oscillation_library.py` (40 tests),
  `build_oscillation_library.py` (harvester),
  `oscillation-library-panel-config.json` (the exact panel config used), and
  this report.

## 0. Scope limit, stated first because it is the point of the item

**M3a freezes the situations only.** The manifest's point 5 also asks what the
best action was in each and how it compares with what the combined score
actually chose. That is **M3b**, it is a separate item, it is blocked on the
Decision Packet, and **nothing in this deliverable attempts it**.

No frozen situation, and no line of the loader, records a best action, a
preferred action, a recommendation, a verdict, a fix or a remedy. That
silence is not a promise in prose: `TestNoBestActionRecorded` walks every key
of every frozen file against a forbidden-key list and every string against a
forbidden-phrase list, and asserts the index declares the M3a scope limit.

The reason is the circularity M3b exists to avoid. Every situation here was
found by running the shipped bot and reading its own transcript. If I now
wrote down "the right move at m110 turn 7 was X", X would be derived from the
same scorer whose behaviour M3b is supposed to independently audit, and the
comparison M3b performs would be a comparison of the scorer with itself.

## 1. What is in the library

| | |
|---|---|
| frozen situations (files, excluding `index.json`) | **33** |
| episodes represented (sum of multiplicities) | **47** |
| `library_sha256` | `5858d35122973f017374ed2136aa2855e8e2ace68114b1e8e6f52759e0136c61` |

### 1.1 Mechanism histogram

By situation, and by episode (multiplicity counted):

| mechanism | situations | episodes |
|---|---:|---:|
| **M1** — corridor block | 11 | 11 |
| **M2** — stationary occupation invisible to planning | 14 | 20 |
| **M3** — scorer cycle | 1 | 1 |
| **UNCLASSIFIED** | 7 | 15 |
| **total** | **33** | **47** |

The 15 UNCLASSIFIED episodes are 5 D-1 episodes whose peer does not hold a
single cell across the window (so no stationary blocker is established) plus
the 10 P4 stall windows, which are not alternations at all and are labelled
UNCLASSIFIED by construction — see §4.

### 1.2 Idle-vs-working blocker split

| | situations | episodes |
|---|---:|---:|
| blocker **IDLE** | 17 | 23 |
| blocker **WORKING** | 8 | 8 |
| **NONE** (no blocker: M3, unstable peer, or a stall) | 8 | 16 |

The idleness criterion is taken verbatim from the mechanism analysis §1.5:
*wait fraction ≥ 0.95 over the window **and** 0 changes of cell over the
window*. Both components are stored per situation, so a later item can
re-adjudicate the boundary without re-running anything.

**MEASURED, and the sharpest single number in this report.** Cross-tabulating
the 36 D-1 episodes by blocker state and by the "terminal mode" threshold of
≥ 62 turns used throughout the prior analyses:

| | ≥ 62 turns | < 62 turns |
|---|---:|---:|
| blocker IDLE | **20** | 3 |
| blocker WORKING | **0** | 7 |
| no blocker established | **0** | 6 |

Every one of the 20 terminal episodes has an idle blocker; not one episode
with a working blocker or no blocker reaches 62 turns. This reproduces the
prior analysis's "20/20 terminal episodes have a permanently idle blocker" on
a different bot build and a bumped corpus, and it is why the item asks the
library to carry the distinction: the 195-turn `m110` case and the 7-turn
`m040` case are the **same mechanism (M1)** and differ **only** in the blocker.

### 1.3 Kind and completeness

| kind | situations | episodes | completeness |
|---|---:|---:|---|
| `D1_EPISODE` | 27 | 36 | FULL |
| `P4_STALL` | 5 | 10 | FULL |
| `REAL_CORPUS` | 1 | 1 | **PARTIAL** — see §3.4 |

D-1 episode length over the 36 harvested episodes: min 7, median 95, max 195;
20 are ≥ 62 turns.

## 2. What a frozen situation contains

One JSON file per situation. Every field below is literal data copied out of
the referee transcript — **no call back into `fuzz_panel.build_skeleton` or
any other generator**, so a change to the map generator, the class mix, the
seed list or the regeneration-attempt counter cannot silently move a
situation.

- `provenance` — source, map id, seat, seed, generation attempt, map class,
  opponent profile, map dimensions, corpus version, instrument version, panel
  seeds/maps/turns/liveness window, the panel config SHA-256, and **the
  SHA-256 of the bot source that produced it**.
- `static_map_rows` — the map as the bot read it, verbatim.
- `world_state_at_entry` — turn number, both inventories, every plant
  (`kind x y size health fruits cooldown`), every unit of **both** players in
  the 14-field wire shape (`id player x y speed capacity harvest chop` +
  6 carry slots).
- `initial_world_state` — the same, at turn 1, so the whole game is replayable
  from the frozen record alone.
- `window` — oscillating unit, turn range, length, the two cells, `k`, and the
  **verbatim command line for every turn of the window** (all units, both
  the oscillator and the blocker).
- `classification` — mechanism, the evidence sentence, blocker state, every
  measured fact about every own peer (cells held in the window, cells held to
  game end, wait fraction, non-WAIT verbs, plant on its cell, adjacency), a
  canonical geometry stencil, a human-readable map excerpt, shack-door
  evidence, and the classifier version.
- `detectors` — the full D-1..D-9 counts for the game, every D-1 episode in
  it, every P4 violation detail, `live_horizon`, and the turns simulated.
- `multiplicity` — how many episodes map to this situation, the dedupe key
  digest, and the full member list.
- `unresolved` — what this situation does **not** settle, and what would.
- `content_sha256` — the digest of everything above.

### 2.1 The freeze is real — MEASURED

Every FULL situation was replayed from its own literal data: the frozen
`static_map_rows`, `initial_world_state.plants`, `initial_world_state.units`,
`initial_world_state.inventories.own` and `provenance.opponent_profile` were
fed straight into `fuzz_panel.make_referee` (no generator call), the shipped
bot was run closed-loop through `regression_tests.run_binary_custom`, and the
resulting command lines were compared with the frozen command window.

```
OSC_LIB_REPLAY=1 PATH=~/.cargo/bin:$PATH \
  python3 -m unittest test_oscillation_library
# -> 40 tests, OK  (test_every_full_situation_reproduces_its_command_window)
```

Result: **32 of 32 FULL situations reproduce their frozen command window
byte-for-byte; 0 mismatches; 1 skipped (the PARTIAL real-corpus record).**
This test is opt-in behind `OSC_LIB_REPLAY` because it needs `rustc`; the
default `python3 -m unittest test_oscillation_library` is stdlib-only and
runs in 0.26 s.

### 2.2 Fail-closed integrity — DEMONSTRATED, not asserted

Three layers: the per-file `content_sha256` over the canonical payload; the
index's copy of that digest; and `library_sha256` over the sorted
`(id, content_sha256)` pairs, which catches an added or removed file that a
per-file digest cannot. `load_library` checks all three plus the file-set,
the declared count, the schema, the enumerated field values, the id/filename
agreement, the required provenance fields, and that a FULL situation really
carries a world state and a PARTIAL one really gives a reason for its
absence. **Any failure raises `IntegrityError` and returns nothing** — there
is no partially-verified load.

Ten tests each really mutate a scratch copy of the library and show the
loader refusing it, with a control (`test_the_unmutated_copy_loads`) that
proves the copy loads clean first so none of them can pass vacuously:

| mutation actually performed | caught by |
|---|---|
| move a unit one cell in `world_state_at_entry` | file digest |
| flip the mechanism label | file digest |
| append one space to one command line | file digest |
| bump an inventory **and recompute the file's own digest** | the index's copy |
| … **and also rewrite the index entry** | `library_sha256` |
| delete a situation file | file-set check |
| add an unindexed situation file | file-set check |
| increment `index.situation_count` | count check |
| zero out `index.library_sha256` | library digest |
| drop `provenance.bot_source_sha256`, re-signing file and index | required-field check |
| null out a FULL situation's world state, re-signing file and index | completeness check |

Sample output from the CLI test, which also asserts a non-zero exit status:

```
oscillation_library: INTEGRITY FAILURE: OSC-001.json (OSC-001): content hash
mismatch -- file records 952f7979daa75ada…, payload hashes to 91799f77feece286…
The frozen situation has been modified; refusing to load the library.
```

### 2.3 Dedupe by mechanism + geometry, not by game id

The dedupe key is `kind | mechanism | blocker_state | canonical_stencil`. The
stencil covers exactly the oscillation cells (or, for a stall, the stalled
unit's cell) **and their orthogonal neighbours** — which is precisely the
shipped resolver's action space, since both the direct landing and the detour
candidate set are drawn from the orthogonal neighbours of the current cell. It
marks the oscillation cells, the blocker, and whether the blocker stands on a
plant, and it is minimised over the eight dihedral frames of the lattice, so
the same local shape at any rotation or reflection on any map yields the same
string. Decoration further away — other plants, the shacks, the map border —
is deliberately excluded: it does not enter the decision and would make every
episode unique.

Effect: 47 episodes collapse to 33 situations. Multiplicity distribution:
26 situations ×1, 3 ×2, 1 ×3, 3 ×4. The representative of a group is the
longest episode (ties by map id, seat, unit, turn start); every member is
listed by map/seat/unit/turn-range, so nothing is lost.

## 3. What each source contributed

### Source 1 — the panel floor (parent judged against itself)

**MEASURED.** Command, exactly as run:

```
PATH=~/.cargo/bin:$PATH python3 claude_1/pipeline/fuzz_panel.py \
  --config claude_1/banana-restoration-r2/oscillation-library-panel-config.json \
  --report <scratch>/floor-report.md
# -> fuzz_panel: BLOCK (240 games, 119 blocking, 0 flagged, 16.3 s)
```

The config sets **both** `candidate.source` and `parent.source` to the
absolute path of
`cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`
with distinct crate names (`m3a_floor_candidate` / `m3a_floor_parent`) and a
fresh `games_dir`. **119/240 blocking reproduces the stated current floor
exactly** at corpus `c3-train-engine-authority-2026-08-09`.

Yield: **36 D-1 episodes across 33 games**, and **29 games failing P4**, of
which **10 have no D-1 at all**. After dedupe: 27 `D1_EPISODE` situations and
5 `P4_STALL` situations. 37 distinct maps contributed. Map classes of the
representatives: `choke_corridor` 12, `orchard_eligible` 6, `single_door_tent`
4, `forest_sparse` 3, `forest_dense` 2, `multi_door` 2, `open_field` 2,
`water_diagonal` 1. Opponent profiles: `harvester` 13, `idle` 11,
`chopper_aggressor` 8.

Detector totals over the floor (MEASURED): D-9 196, D-1 36, D-6 15, D-4 6,
D-5 1; D-2, D-3, D-7, D-8 zero. Only D-1 and P4 are oscillation/liveness
instruments and only those were harvested.

**Corpus-version note (MEASURED).** The mechanism analysis of 2026-08-09
reported **35** D-1 episodes for the readable build `98628e98` under corpus
`c2-train-2026-08-09`. This harvest reports **36** for the slim arena parent
`a8eb3b2b` under `c3-train-engine-authority-2026-08-09`. Results are not
comparable across the corpus bump, and the panel refuses a config declaring a
different version. The named cases nevertheless land identically — see §5.

### Source 2 — `m040` seats 0 and 1

**Seat 1 yielded exactly the documented case**: unit 0, turns **80–86**, cells
**(4,0)↔(3,0)**, blocker unit 6 (a TRAIN-spawned worker) holding (5,0) and
emitting `CHOP`/`MOVE` — wait fraction 0.00, so **WORKING**. Frozen as
`OSC-010`, mechanism **M1**.

**Seat 0 yielded nothing.** Under corpus c3 `m040` seat 0 has **no violations
at all** — no D-1 episode, no P4 stall, no detector failure. It is recorded
here as a plain negative, not omitted.

### Source 3 — `m110` seat 1

**Yielded the 194-turn corridor case**, frozen as `OSC-001`: unit 0, turns
**6–200** (195 turns of alternation), cells **(6,2)↔(5,2)**, blocker unit 2
holding (4,2) with wait fraction 1.00 and no plant on its cell — **M1**,
blocker **IDLE**. It is the longest episode in the library and the R-6a
fixture target.

**MEASURED anti-drift check.** The frozen literal state is byte-identical to
the R-6a fixture published in §6 of the mechanism analysis: the same five map
rows, the same three 14-field unit rows, the same single
`["BANANA",2,2,4,6,1,48]`, the same `[0,0,0,2,0,0]` inventory, class
`choke_corridor`, profile `harvester`. `test_m110_geometry_is_the_published_R6a_fixture`
asserts each of these as literals, so the assertion survives any future change
to the generator.

### Source 4 — the real corpus (B3.4 and its descendants)

**Partly yielded; the limitation is stated plainly rather than papered over.**

What is committed: the *analysis products*. `docs/LEDGER-MAP.md` row B3.2/B3.3
records "sustained same-two-cell oscillation (18/194 games, worst 131 turns)";
row B3.4 records the root cause and "causality modest (2/18 causally
suspicious)"; `data/analysis/live-agent-6553250/d171a-oscillation-breaker-protocol-2026-07-28.md:17`
records "17/18 real episodes: a teammate parked ≥85 % of the run (11/18 at the
own shack door…)".

What is **not** committed: **the underlying per-episode rows for those 18
games.** I searched `data/`, `docs/`, `local_*/`, `cgauto/` and the git history
for a B3.4 per-game result file and there is none; the D171a and D176a result
JSONs carry aggregate verdicts (`integrity`, `mechanism`, `panel`, `reason`,
`schema`, `value`, `verdict`), not episode rows. **I have therefore not frozen
any of those 18 games, and I have invented nothing.** The three figures above
are cited as prior-work provenance `[P]`, not as measurements of mine.

The one real-corpus episode that *does* have committed per-episode evidence is
the Elost same-tree deadlock,
`data/analysis/live-agent-6553250/elost-same-tree-occupancy-deadlock-result-2026-07-31.json`
(SHA-256 `ac5263ba96087ee397cbacaf0515e9048c8293c5373c7d771a698ad6def03b1c`).
It is frozen as **`OSC-033`, completeness `PARTIAL`**: game `897556967`,
resident seat 1, unit 2 alternating **(18,5)↔(18,6)** over **8** decision
states, turns **61–68**, while unit 1 — capable, full of wood, standing on the
live LEMON at (19,6) — emits ten consecutive `WAIT`s (turns 58–67) and is
nonetheless assigned that same tree as unit 2's target on all ten turns. That
is **M2** in its purest form. Blocker state is recorded **WORKING**, because
the committed record shows the occupant chopping on turns 55–57 and resuming
`CHOP` on turn 68 — the episode is bounded by the blocker's own work.

Its world state is **`null`**, with `world_state_absent_reason` naming the two
files that would supply it —
`data/external/elost-same-tree-occupancy-deadlock/game-897556967.json`
(`7d2531710e…`) and `trajectory-897556967.jsonl` (`2a809f316e…`) — and the
fact that `data/external` is git-ignored (`.gitignore:15`) and absent from
this checkout. `test_the_real_corpus_episode_is_frozen_as_partial_not_invented`
asserts the situation stays honest about this.

**Yielded nothing usable:** the Zasmu postmortem
(`zasmu-lemon-denial-oscillation-postmortem-result-2026-07-31.md`, game
`896352750`) records five A-B-A returns, all of **3 states**. D-1's predicate
needs `k ≥ 3`, i.e. ≥ 7 states / ≥ 6 transitions, so none of them is an
episode by the frozen detector; the document says so itself ("no sustained
≥10-state episode"). Nothing was frozen from it.

### Source 5 — prior analyses, used as pointers

`oscillation-attack-claude_1-2026-08-09.md`
(`f8983a8e6cdc977867843888a3f4a28c943552fc4785af6014d968e5cd6302ca`) supplied
the three mechanism definitions, Theorems 1–3, the ≥ 95 % / 0-cell idleness
criterion, the R-6a fixture to check against, and the named cases `m014`
(M2) and `m085` (M3). `feasibility-raw-zero-2026-08-07.md`
(`6a626504b91aca0fe65cbd2346a9aa67b7759c3ae48f0dac09002232c9eae62a`) supplied
the real-corpus B3.4 citations reproduced above. Neither supplied data that
was copied into a frozen situation; both were used to *check* the harvest.

## 4. How a situation is classified — and what is MEASURED vs INFERRED

The classifier (`build_oscillation_library.classify`, version
`m3a-observational/1`) reads **only** transcript-observable facts. The bot was
not modified, instrumented or read for this purpose: `rust/**`, `cgauto/**`
and every `.min.rs` were untouched.

```
if no other own unit is alive during the window        -> M3
elif no own peer holds a single cell for the whole
     window at orthogonal distance 1 from an
     oscillation cell                                  -> UNCLASSIFIED
elif that peer is IDLE and stands on a live plant      -> M2
else                                                   -> M1
```

**MEASURED** in every situation: the peer's cells held in the window and to
game end, its wait fraction, its non-WAIT verbs, whether a plant stood on its
cell at the entry turn, its adjacency to the oscillation cells, the number of
own units alive, and which oscillation cells are shack doors.

**INFERRED** — and marked so in every affected situation's `unresolved` list:

- **The M1/M2 discriminator.** The goal the bot actually held is *not*
  observable in the transcript. M2 is inferred from "the blocker is idle **and**
  stands on a live plant", which per the mechanism analysis §1.4(b) is the
  configuration in which `compatible` (readable line 644, `if a==Target::None
  || b==Target::None { return true; }`) lets a second unit take the occupied
  cell as its own target. M1 is inferred from the complement: the blocker is
  off-plant (so the goal is beyond it — `m110`) or it is actively working the
  plant it stands on (so its `CHOP` carries a real `Target` that `compatible`
  *can* see, and the oscillator's goal is something else — `m040`).
  *Settled by:* an instrumented build logging the resolver's goal per turn.
  **That is out of boundary for M3a, which may not modify any bot**, or by the
  Decision Packet.
- **The M3 attribution.** `m085` seat 0 has a single own unit, so by Theorem 2
  the resolver's detour branch cannot fire and the alternation must come from
  the goal selector — that much follows from the transcript. Attributing it
  specifically to the exclusive on-door pricing branch of `endgame_candidates`
  (readable 1290–1302, the ~25 % discontinuity) is taken from the mechanism
  analysis §1.3, not measured here. The one supporting observable I *can*
  measure is recorded: cell **(1,4) is an own shack door** (own shack (0,4)),
  which is what that branch keys on.

**UNCLASSIFIED is a real answer, not a shrug.** Five D-1 episodes
(`m066` s0, `m061` s0, `m070` s0, `m090` s0, `m004` s0 — all early-game, all
≤ 22 turns) have a peer that *moves* during the window, so neither the
forced-detour mechanism nor a stationary occupation is established by the
transcript. Labelling them M1 would be a guess. The 10 P4 stall windows are
UNCLASSIFIED because a stall is not an alternation: the mechanism analysis
§1.6 argues the terminal-oscillation population and the permanently-idle-worker
population are the same population seen from opposite ends, but that is an
argument about the population, not a measurement on any one of these
situations.

## 5. The named cases, cross-checked against the mechanism analysis

`TestNamedCases` asserts each of these against the frozen data.

| case | frozen as | mechanism | blocker | window | agrees with |
|---|---|---|---|---|---|
| `m110` s1 u0 | `OSC-001` | **M1** | **IDLE** (unit 2 @ (4,2), wait 1.00, 1 cell, no plant) | 6–200, 195 turns, (6,2)↔(5,2) | analysis §1.2 |
| `m040` s1 u0 | `OSC-010` | **M1** | **WORKING** (unit 6 @ (5,0), wait 0.00, `CHOP`) | 80–86, 7 turns, (4,0)↔(3,0) | analysis §1.5 |
| `m014` s1 u2 | `OSC-017` | **M2** | **IDLE** (unit 0 @ (10,0) on BANANA, wait 1.00) | 7–200, 194 turns, (10,1)↔(9,1) | analysis §1.4(b) |
| `m085` s0 u0 | `OSC-025` | **M3** | **NONE** (one own unit) | 17–23, 7 turns, (1,4)↔(2,4) | analysis §1.3 |

`test_the_two_named_cases_differ_exactly_in_the_blocker` asserts the pair the
item singles out: `m110` and `m040` carry the **same** mechanism label, the
**opposite** blocker state, and lengths differing by more than 25×.

## 6. Coverage gaps

1. **One corpus, one bot, one referee.** Everything except `OSC-033` comes
   from a single 240-game panel run of a single build
   (`a8eb3b2b`) under a single corpus version. A situation that only the
   readable build `98628e98`, or a different opponent mix, or 300 turns
   instead of 200, would produce is not here. The prior analysis's readable-build
   corpus reported 35 episodes against this run's 36; that one-episode delta is
   itself unexplained across the corpus bump.
2. **200 turns of a 300-turn game.** 15 of the 36 D-1 episodes run to turn
   200, i.e. they are truncated by the simulation horizon, not by the game.
   Their true lengths are lower bounds.
3. **Only D-1-shaped oscillation.** D-1 requires a strict two-cell alternation
   with `k ≥ 3`. A three-cell cycle, a period-4 cycle, or a two-cell
   alternation punctuated by a progress event every few turns is invisible to
   this harvest. Nothing in the library says such cases do not exist; nothing
   in it says they do.
4. **The real corpus is one episode deep.** 18 real B3.4 games are cited in
   the ledger; 1 real episode is frozen, and PARTIAL at that (§3.4).
5. **No M3 population.** Exactly one M3 situation exists in the whole library.
   Any statement about how common the scorer cycle is rests on a single
   episode.
6. **UNCLASSIFIED is 15 of 47 episodes (32 %).** Five D-1 episodes and all ten
   stall windows. Closing them needs goal-level observability, which M3a
   cannot obtain within its boundary.
7. **The dedupe key is a choice, not a fact.** A radius-1 stencil merges
   episodes that a radius-2 stencil would separate; the key digest and the
   full member list are stored so a later item can re-group without
   re-harvesting, but the 33 is a function of that choice.
8. **Both seats of a map are separate games but not independent samples** —
   they share geometry and plants. 37 distinct maps produced the 46 panel
   episodes.

## 7. UNRESOLVED, with what would settle each

Every situation carries its own `unresolved` list; the loader rejects a
situation that claims nothing is open. Consolidated:

| # | unresolved | what would settle it |
|---|---|---|
| U1 | The goal the bot held in each M1/M2 window — hence the M1/M2 boundary itself (25 situations, 31 episodes) | An instrumented build logging the resolver's goal per turn, run over the frozen states. **Out of M3a's boundary** (no bot may be modified). Alternatively the Decision Packet, if it exposes per-turn targets. |
| U2 | Whether `m085`'s two-cycle really comes from the exclusive on-door pricing branch of `endgame_candidates` | A committed scorer trace over the frozen `OSC-025` state showing the two candidate prices at (1,4) and (2,4). |
| U3 | Whether the 5 UNCLASSIFIED D-1 episodes are M1, M3, or something not yet named | Same instrumentation as U1. |
| U4 | Whether the 10 P4 stall windows share a mechanism with the D-1 population | A goal trace showing what the stalled unit was selecting while it made no progress. |
| U5 | Whether `trace_detectors.detect_d1` would in fact report the Elost episode, and what the literal world state at turn 61 was | Committing `data/external/elost-same-tree-occupancy-deadlock/trajectory-897556967.jsonl` (SHA-256 `2a809f316e03471cc9f8e54fdd1ae9410bde3abe9f3819b82677973d78ea7ec6`) and running the detector over it. |
| U6 | The 17 remaining real B3.4 episodes | Committing the per-episode rows behind `docs/LEDGER-MAP.md` B3.2/B3.3/B3.4, or re-deriving them from the arena replays. |
| U7 | Why the episode count moved 35 → 36 across the c2 → c3 corpus bump | A c3 run of the readable build `98628e98`, diffed episode-by-episode against this run. Cheap, but it is a corpus question, not a library question. |
| U8 | Whether any non-two-cell oscillation shape exists (gap 3) | A cycle detector with a period parameter, run over the same 240 games. |
| U9 | **What the best action was in each situation, and how it compares with what the combined score chose** | **M3b.** Deliberately not attempted here; blocked on the Decision Packet. |

## 8. Reproduction — every input, hashed

Toolchain: `rustc 1.97.1 (8bab26f4f 2026-07-14)` at `~/.cargo/bin/rustc`;
`Python 3.12.3`. Repository `/home/tarstars/prj/troll_farm-claude_1`.

| input | SHA-256 |
|---|---|
| `cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs` (the bot, used as **both** candidate and parent) | `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55` |
| `claude_1/pipeline/fuzz_panel.py` (run read-only; **not** modified) | `eff0a98ff5b9f636cf6c73de131e64d629cf63e7cdd6b8dca5afb51ba0d2c11b` |
| `claude_1/banana-restoration-r2/trace_detectors.py` (read-only) | `59dce10dc87797bc6b1b8da0f628f4ddd82b561d93946fa91453d2ea40805209` |
| `claude_1/banana-restoration-r2/regression_tests.py` (read-only) | `fbd6e8da451522bf0e8ec06826c48912b4d0f1c79961d49023276ba7837f11a1` |
| `claude_1/banana-restoration-r2/oscillation-library-panel-config.json` | `bb9734385fad50b9090a1344cf2b6fcd8f90bb628b4891693b9d709b23678fed` |
| panel `games.jsonl.gz` (scratch, 240 rows) | `36543dc8d76088779d01eaf902520389b87642871f322997ee36242fdff2e428` |
| `data/analysis/live-agent-6553250/elost-same-tree-occupancy-deadlock-result-2026-07-31.json` | `ac5263ba96087ee397cbacaf0515e9048c8293c5373c7d771a698ad6def03b1c` |
| `claude_1/banana-restoration-r2/oscillation-attack-claude_1-2026-08-09.md` | `f8983a8e6cdc977867843888a3f4a28c943552fc4785af6014d968e5cd6302ca` |
| `claude_1/banana-restoration-r2/feasibility-raw-zero-2026-08-07.md` | `6a626504b91aca0fe65cbd2346a9aa67b7759c3ae48f0dac09002232c9eae62a` |
| `claude_1/banana-restoration-r2/oscillation_library.py` | `077abc612a607647f4a7d24582877c9d8e2a0718b5ead918e08337fa5f5f33d2` |
| `claude_1/banana-restoration-r2/build_oscillation_library.py` | `4b9fce4ca49a6ce05b4f3f8cb8f7b81d78b7da3c863a4e1ad32fdd2f16aff9df` |
| `claude_1/banana-restoration-r2/oscillation-library/index.json` | `8b308f8f78c23cb08d2fbc2c27e8091988817be74b534b378ad5f692c637cefb` |
| the library itself (`library_sha256`) | `5858d35122973f017374ed2136aa2855e8e2ace68114b1e8e6f52759e0136c61` |

Steps:

```bash
# 1. the panel floor (parent judged against itself), ~16 s
PATH=~/.cargo/bin:$PATH python3 claude_1/pipeline/fuzz_panel.py \
  --config claude_1/banana-restoration-r2/oscillation-library-panel-config.json \
  --report <scratch>/floor-report.md
# (games_dir / bin_cache_dir in that config are scratch paths; edit them or
#  keep them, the harvest only reads games_dir/games.jsonl.gz)

# 2. rebuild the library from the panel output
cd claude_1/banana-restoration-r2
python3 build_oscillation_library.py \
  --games <games_dir>/games.jsonl.gz \
  --panel-config oscillation-library-panel-config.json

# 3. verify
python3 oscillation_library.py --verbose
python3 -m unittest test_oscillation_library -v          # 40 tests, 1 skipped
OSC_LIB_REPLAY=1 PATH=~/.cargo/bin:$PATH \
  python3 -m unittest test_oscillation_library            # 40 tests, 0 skipped
```

## 9. Boundary compliance

No file under `rust/**` or `cgauto/**` was modified; no bot, candidate, parent
or `.min.rs` was modified; `claude_1/banana-restoration-r2/trace_detectors.py`
and `claude_1/pipeline/fuzz_panel.py` were **imported and executed read-only**
and are byte-unchanged: `git diff HEAD~2 HEAD -- claude_1/pipeline/ claude_1/banana-restoration-r2/trace_detectors.py claude_1/banana-restoration-r2/regression_tests.py rust cgauto` is empty, and `trace_detectors.py` / `regression_tests.py` are also byte-identical to `origin/main` (`fuzz_panel.py` differs from `origin/main` only through this branch's own earlier, already-delivered commits, none of them mine). No Arena
action, no CI change, no submission, no host mutation. The only writes are the
six new files listed at the head of this report.

## 10. Complete episode index

Every harvested episode, and the frozen situation that carries it.

| origin | seat | unit | turns | length | mechanism | blocker | kind | situation |
|---|---|---|---|---|---|---|---|---|
| `897556967` | 1 | 2 | 61-68 | 8 | M2 | WORKING | REAL_CORPUS | OSC-033 |
| `m003` | 0 | 2 | 23-200 | 178 | M2 | IDLE | D1_EPISODE | OSC-019 |
| `m004` | 0 | 2 | 24-31 | 8 | UNCLASSIFIED | NONE | D1_EPISODE | OSC-027 |
| `m005` | 1 | 0 | 29-39 | 11 | M1 | IDLE | D1_EPISODE | OSC-006 |
| `m012` | 1 | 0 | 12-20 | 9 | M1 | WORKING | D1_EPISODE | OSC-007 |
| `m014` | 1 | 2 | 7-200 | 194 | M2 | IDLE | D1_EPISODE | OSC-017 |
| `m021` | 1 | 0 | 61-200 | 140 | UNCLASSIFIED | NONE | P4_STALL | OSC-031 |
| `m039` | 1 | 0 | 7-24 | 18 | M2 | IDLE | D1_EPISODE | OSC-012 |
| `m039` | 1 | 0 | 50-200 | 151 | M2 | IDLE | D1_EPISODE | OSC-012 |
| `m040` | 1 | 0 | 80-86 | 7 | M1 | WORKING | D1_EPISODE | OSC-010 |
| `m046` | 0 | 2 | 14-200 | 187 | M2 | IDLE | D1_EPISODE | OSC-013 |
| `m050` | 1 | 2 | 14-169 | 156 | M2 | IDLE | D1_EPISODE | OSC-013 |
| `m053` | 0 | 0 | 91-200 | 110 | UNCLASSIFIED | NONE | P4_STALL | OSC-028 |
| `m059` | 0 | 0 | 11-200 | 190 | UNCLASSIFIED | NONE | P4_STALL | OSC-028 |
| `m059` | 1 | 2 | 12-200 | 189 | M1 | IDLE | D1_EPISODE | OSC-002 |
| `m060` | 0 | 2 | 44-200 | 157 | M2 | IDLE | D1_EPISODE | OSC-015 |
| `m061` | 0 | 2 | 2-9 | 8 | UNCLASSIFIED | NONE | D1_EPISODE | OSC-026 |
| `m065` | 1 | 2 | 9-20 | 12 | M1 | WORKING | D1_EPISODE | OSC-005 |
| `m066` | 0 | 2 | 3-24 | 22 | UNCLASSIFIED | NONE | D1_EPISODE | OSC-026 |
| `m070` | 0 | 2 | 1-8 | 8 | UNCLASSIFIED | NONE | D1_EPISODE | OSC-026 |
| `m070` | 1 | 2 | 7-18 | 12 | M1 | WORKING | D1_EPISODE | OSC-004 |
| `m071` | 0 | 2 | 44-200 | 157 | M2 | IDLE | D1_EPISODE | OSC-015 |
| `m071` | 1 | 2 | 27-100 | 74 | M2 | IDLE | D1_EPISODE | OSC-023 |
| `m071` | 1 | 2 | 106-200 | 95 | M2 | IDLE | D1_EPISODE | OSC-022 |
| `m073` | 0 | 0 | 5-67 | 63 | M2 | IDLE | D1_EPISODE | OSC-024 |
| `m073` | 1 | 2 | 13-108 | 96 | UNCLASSIFIED | NONE | P4_STALL | OSC-028 |
| `m078` | 0 | 2 | 12-18 | 7 | M1 | WORKING | D1_EPISODE | OSC-009 |
| `m079` | 0 | 2 | 38-200 | 163 | M2 | IDLE | D1_EPISODE | OSC-014 |
| `m079` | 1 | 2 | 33-197 | 165 | M2 | IDLE | D1_EPISODE | OSC-014 |
| `m084` | 1 | 0 | 32-200 | 169 | M2 | IDLE | D1_EPISODE | OSC-021 |
| `m085` | 0 | 0 | 17-23 | 7 | M3 | NONE | D1_EPISODE | OSC-025 |
| `m087` | 0 | 0 | 58-200 | 143 | UNCLASSIFIED | NONE | P4_STALL | OSC-030 |
| `m088` | 1 | 2 | 9-17 | 9 | M1 | WORKING | D1_EPISODE | OSC-008 |
| `m090` | 0 | 2 | 2-9 | 8 | UNCLASSIFIED | NONE | D1_EPISODE | OSC-026 |
| `m090` | 0 | 2 | 17-189 | 173 | M2 | IDLE | D1_EPISODE | OSC-012 |
| `m091` | 0 | 0 | 91-200 | 110 | UNCLASSIFIED | NONE | P4_STALL | OSC-029 |
| `m091` | 1 | 0 | 94-200 | 107 | UNCLASSIFIED | NONE | P4_STALL | OSC-029 |
| `m092` | 0 | 0 | 2-36 | 35 | M1 | IDLE | D1_EPISODE | OSC-003 |
| `m094` | 1 | 2 | 10-200 | 191 | M2 | IDLE | D1_EPISODE | OSC-018 |
| `m099` | 1 | 0 | 8-200 | 193 | M2 | IDLE | D1_EPISODE | OSC-012 |
| `m100` | 0 | 0 | 6-99 | 94 | UNCLASSIFIED | NONE | P4_STALL | OSC-032 |
| `m101` | 0 | 0 | 115-200 | 86 | UNCLASSIFIED | NONE | P4_STALL | OSC-029 |
| `m104` | 1 | 2 | 29-200 | 172 | M2 | IDLE | D1_EPISODE | OSC-020 |
| `m106` | 0 | 0 | 11-200 | 190 | UNCLASSIFIED | NONE | P4_STALL | OSC-028 |
| `m110` | 1 | 0 | 6-200 | 195 | M1 | IDLE | D1_EPISODE | OSC-001 |
| `m114` | 1 | 2 | 7-200 | 194 | M2 | IDLE | D1_EPISODE | OSC-016 |
| `m118` | 1 | 2 | 8-14 | 7 | M1 | WORKING | D1_EPISODE | OSC-011 |

47 episodes, 33 situations.
