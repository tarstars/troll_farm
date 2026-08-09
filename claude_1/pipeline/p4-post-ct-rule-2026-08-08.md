# P4 post-`C_T` referee-state rule (Phase 1 item 3) — 2026-08-08

Author `claude_1`. Execution review `local_claude_1`, adversarial review
`chatgpt_1`. Scope: `claude_1/pipeline/fuzz_panel.py` (P4 / `eval_p4`) and its
self-tests only. `trace_detectors.py` is **unmodified** — the D-7 half of the
same question is *referred*, not implemented (§7).

**Headline:** the post-`C_T` state explains **0 of the residual 30** P4 windows
(MEASURED, §4). All 30 are genuine stalls of the reference implementation over
a world that offered a legal resource action on **every** turn of the window.
The rule was still implemented, because the final turn today carries **no
liveness obligation at all** in either direction; the fix is a boundary
correctness fix that leaves the floor at 118/240 unchanged.

---

## 1. Environment and provenance

| item | value |
|---|---|
| host python | 3.12.3 (`python3 -m unittest`; **no pytest on this host**) |
| rustc | 1.97.1 (8bab26f4f 2026-07-14), `$HOME/.cargo/bin` |
| repo | `/home/tarstars/prj/troll_farm-claude_1`, branch `agent/claude_1-banana-restoration-r2` |
| commits | `49c3204b` RED, `974042d3` GREEN, this report |

Input SHA-256 (post-GREEN):

| file | sha256 |
|---|---|
| `claude_1/pipeline/fuzz_panel.py` | `c21428ffeeaf8e02968a6e8be25a5b8e032c704b93a785ccd340b80eb0b754a4` |
| `claude_1/pipeline/test_fuzz_panel.py` | `27d1d6230de180968951bbda9e74b58fe35d66b64f20ff039d9449e5ed00e371` |
| `claude_1/pipeline/fuzz-panel-config.json` | `f5394e7a8b974062b07f42bc535e113dca2e9d67b64c9b196c1a4b63660b99fe` (**unmodified — no new flag was needed**) |
| `cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs` (parent = floor bot) | `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55` |
| `claude_1/banana-restoration-r2/trace_detectors.py` | `59dce10dc87797bc6b1b8da0f628f4ddd82b561d93946fa91453d2ea40805209` (**unmodified, both before and after**) |

Scratchpad (analysis inputs/outputs), under
`/tmp/claude-1000/-home-tarstars-prj-troll-farm/3b336b91-cd2f-4655-9aaf-31fd6d3d156f/scratchpad/p4ct/`:

| file | sha256 | role |
|---|---|---|
| `floor-before.json` | `390772985ea25af1e11302a8bb323d7031de3a8eeaffc52775dd846557aea73e` | floor config (BEFORE) |
| `floor-after.json` | `a4fc49f508a081637cb0efe96b8087abe0df7b6fafff17790f018afcd00e815f` | floor config (AFTER) |
| `games-before/games.jsonl.gz` | `505afd036fc15a18598217503b64b395c7a1ca268a8f34ae8088d85c9eb229fa` | 240 archived games, BEFORE |
| `games-after/games.jsonl.gz` | `35d4676f04ceda9123d78966c708be52b268fda77ca50196ac651b06628a1c96` | 240 archived games, AFTER |
| `floor-before-games.json` | `580b84f8e9ea286d892eda6f7e41a644c0f61b85be9b67747ea9da7cffe9301f` | slim per-game verdicts, BEFORE |
| `floor-after-games.json` | `020138952182911a450b17953ce1ea2f35b37faade0653dc7fb50b81a9920f94` | slim per-game verdicts, AFTER |

Two of those four output files are **not** byte-reproducible for reasons
unrelated to the panel: `games.jsonl.gz` carries gzip's mtime header, and the
slim JSON embeds `stats.wall_time_seconds`. The *content* is deterministic —
sha256 of the canonical `games` payload (`json.dumps(..., sort_keys=True)`,
verified identical across two consecutive AFTER runs):

| run | `games` payload sha256 |
|---|---|
| BEFORE | `f25038304ec655c15873e31942db2fbca4ea767dbc93e6ec23e11202b3c12132` |
| AFTER (run 1 = run 2) | `f833c075270f4776544e222bf4c7972d96bb59b7ca42a2187a697a2b2f7e1fab` |
| `analyze.py` | `2bcda18e1e29572ef53c425e27a827c471b843e94fd77377bfdef6dc56f8d8fb` | post-`C_T` replay of the P4 games |
| `classify2.py` | `904826661dd4b3c3480c71b8e493d4a5c338b936db6f74bef70088c8fa1bfdb5` | actionability classification |
| `postct_scan.py` | `ef9facadacedaedb680226329c4697e3064126c98ddaae5e11d0d5aa8b33c700` | post-`C_T` scan of all 240 games |
| `mutate.py` | `7eb8c047cce5562e1f71eb537feded01e0f56b21ab6dcfc416a69d0082418273` | mutation ledger driver |

The floor configs are byte-identical to the committed
`fuzz-panel-config.json` except for `task`, both `source`/`crate` set to the
absolute parent path (parent judged against itself) and a fresh `games_dir`.
The analysis scripts replay each archived command stream into a fresh
`FuzzReferee`; the replay was asserted **byte-identical** to the recorded
transcript for all 29 P4 games (`replay_ok: 29/29`, MEASURED), so the
post-`C_T` states below are the referee's, not a re-implementation's.

Exact commands (all run with `PATH=$HOME/.cargo/bin:$PATH` from the repo root
/ the scratchpad):

```
python3 claude_1/pipeline/fuzz_panel.py --config <scratch>/floor-before.json \
        --report <scratch>/floor-before.md --json <scratch>/floor-before-games.json
python3 claude_1/pipeline/fuzz_panel.py --config <scratch>/floor-after.json  \
        --report <scratch>/floor-after.md  --json <scratch>/floor-after-games.json
python3 analyze.py    floor-before.json games-before/games.jsonl.gz > classify-before.json
python3 classify2.py  floor-before.json games-before/games.jsonl.gz > classify2.json
python3 postct_scan.py floor-before.json games-before/games.jsonl.gz
python3 mutate.py .
cd claude_1/pipeline && python3 -m unittest test_fuzz_panel
cd claude_1/pipeline && python3 -m unittest test_pre_review
```

(The `--report` output is MARKDOWN regardless of the file suffix.)

---

## 2. Reconciling "30" and "32" — the games-vs-episodes ambiguity, again

State the unit every time. On the **floor** run (parent judged against
itself, 120 maps × 2 seats = 240 candidate games, 200 turns,
`liveness_window` 60), MEASURED from `floor-before-games.json`:

| definition | count |
|---|---|
| games with ≥ 1 blocking P4 violation | **29** |
| P4 violation **episodes** (stall windows) | **30** (one game, `m071-s1`, has two) |
| games blocking on **P4 alone** (no D-*, no P2) | **4** |
| games with a raw (pre-calibration) stall window ≥ 60 turns | 200 |
| games with ≥ 1 blocking **D-1** violation | **32** |

**My figure is 29 games / 30 windows**, identical to the number already in
`gate-repair-p4-report-2026-08-06.md` ("30 windows in 29 games"). The
coordinator's **32 is the D-1 games column**, not P4: it is the first cell of
the floor row in that same report's detector table (`| FLOOR | 32 / 35 | ...`
= D-1 32 games / 35 episodes) and it is the "19/32 D-1 games also fail P4"
sentence in `feasibility-raw-zero-2026-08-07.md:338`. There is no
P4 measurement anywhere that yields 32. **This report uses "29 games / 30
episodes" throughout, and every table below names its unit.**

---

## 3. What "post-`C_T`" means, precisely

`rt.run_binary_custom` writes state `S_t`, reads command line `C_t`, applies
it, then grows. The transcript therefore contains `S_1..S_T` — each the world
**before** that turn's commands resolve — and `C_1..C_T`. `progress_turns`
can only read transitions `S_t -> S_{t+1}`, i.e. turns `1..T-1`; `stall_windows`
correspondingly ranges over `1..T-1`. **The final turn is therefore invisible
in both directions:** a `C_T` that banks or plants is never counted as
progress, and a `C_T` that does nothing is never counted as a stalled turn.

The post-`C_T` referee state — the world after `C_T` resolves — is already in
the panel's hands: `run_pair` holds `ref_c`, and the game loop has applied
`C_T` (plus the referee's own end-of-turn opponent step and growth) before the
loop exits. `grow()` touches only plants and the opponent policy touches only
opponent inventory/units (`make_banana_traces.py:187-198`,
`fuzz_panel.py:603-643`), so **the own inventory and own-unit cargo in that
state differ from `S_T` if and only if `C_T`'s own commands changed them**
(MEASURED by construction; verified by the byte-identical replay).

---

## 4. The residual 30 — classification (MEASURED)

Every one of the 29 games / 30 windows was replayed and classified.

### 4.1 Against the four hypotheses in the brief

| class | episodes | share |
|---|---|---|
| **(1) genuinely stalled with work remaining** | **30 / 30** | 100 % |
| (2) terminal-state boundary at `T` (post-`C_T`) | **0 / 30** | 0 % |
| (3) resource reachable but not actually actionable | **0 / 30** | 0 % |
| (4) something else | 0 / 30 | 0 % |

**(2) post-`C_T` = 0/30, four independent ways** (all MEASURED,
`classify-before.json`, `postct_scan.py`):

* in **0 / 29** games does `C_T` change the own inventory or any own unit's
  cargo (`progress_at_T_apply: 0`); the final commands are
  `WAIT;MOVE` ×11, `WAIT;WAIT` ×7, `MOVE` ×5, `WAIT` ×5, `CHOP` ×1 (the lone
  `CHOP` does not fell the tree, so no cargo moves);
* in **0 / 29** games does `work_remaining` differ between the pre-`C_T` and
  post-`C_T` state at turn `T` (`wr changes at T: 0`);
* **0 / 29** windows were trimmed by the terminal calibration at all
  (`live_end == window_end` in every case); 25/29 games have work remaining at
  `S_T`, 4/29 became terminal earlier but still carried ≥ 60 live turns;
* the shortest window is **62 live turns** — no window sits within one turn of
  the 60-turn boundary, so a ±1-turn correction at `T` could not have flipped
  any of them.

**(3) non-actionable = 0/30.** For every turn of every window I evaluated
whether the own player could *execute* a resource action: harvest (reachable
plant with `fruits > 0`, a unit with `harvest_power > 0` and free capacity),
chop (reachable plant, `chop_power > 0`, free capacity) or bank (cargo held
and a walkable path to a tent door). A legal **chop** was available on **every
turn of all 30 windows**; a legal **harvest** was available on every turn of
9 of them and on at least one turn of all 30. Longest run of consecutive
actionable turns ≥ 60 in **30/30**.

### 4.2 Sub-split of the 30 genuine stalls

| axis | split |
|---|---|
| shape | 24 trailing to the sim horizon, 6 mid-game (window closes before `T`) |
| strongest available action | 9 "**chop + harvest** available on every turn", 21 "chop available on every turn, harvest intermittently" |
| live window length | min 62, median 168, max 199 turns |
| map class | choke_corridor 14, forest_sparse 5, single_door_tent 3, orchard_eligible 3, open_field 3, multi_door 1, water_diagonal 1 |
| opponent | harvester 17, idle 13 |
| co-blocking | 25 episodes in games that also fail P1, 1 also P2, 4 episodes in games that block on **P4 alone** |
| behaviour in-window | `WAIT`/`WAIT;WAIT` 12, `WAIT;MOVE` 11, `MOVE` 5, other 2 |

Full per-episode table:

| game | class | opponent | window | live turns | always available | dominant commands | other props |
|---|---|---|---|---|---|---|---|
| m003-s0 | single_door_tent | harvester | 22-199 | 178 | chop | `WAIT;MOVE` | P1 |
| m014-s1 | orchard_eligible | idle | 5-199 | 195 | chop+harvest | `WAIT;MOVE` | P1 |
| m021-s1 | choke_corridor | idle | 61-199 | 139 | chop | `WAIT;WAIT` | P1 |
| m039-s1 | choke_corridor | harvester | 44-199 | 156 | chop | `MOVE` | P1 |
| m046-s0 | choke_corridor | harvester | 11-199 | 189 | chop | `WAIT;MOVE` | P1 |
| m050-s1 | choke_corridor | harvester | 12-170 | 159 | chop | `WAIT;MOVE` | P1 |
| m053-s0 | choke_corridor | harvester | 91-199 | 109 | chop | `WAIT` | P1 |
| m059-s0 | choke_corridor | harvester | 11-199 | 189 | chop | `WAIT;WAIT` | — |
| m059-s1 | choke_corridor | harvester | 11-199 | 189 | chop | `WAIT;MOVE` | P1 |
| m060-s0 | forest_sparse | harvester | 37-199 | 163 | chop | `WAIT;MOVE` | P1 |
| m071-s0 | open_field | idle | 32-199 | 168 | chop | `WAIT;MOVE` | P1 |
| m071-s1 | open_field | idle | 26-99 | 74 | chop | `WAIT;MOVE` | P1 |
| m071-s1 | open_field | idle | 106-199 | 94 | chop+harvest | `WAIT;MOVE` | P1 |
| m073-s0 | choke_corridor | harvester | 5-66 | 62 | chop | `MOVE` | P1 |
| m073-s1 | choke_corridor | harvester | 13-108 | 96 | chop | `WAIT;WAIT` | — |
| m079-s0 | forest_sparse | harvester | 33-199 | 167 | chop | `WAIT;MOVE` | P1 |
| m079-s1 | forest_sparse | harvester | 31-199 | 169 | chop | `WAIT;MOVE` | P1 |
| m084-s1 | single_door_tent | idle | 26-199 | 174 | chop | `MOVE` | P1 |
| m087-s0 | multi_door | idle | 58-199 | 142 | chop+harvest | `WAIT` | P1 |
| m090-s0 | choke_corridor | harvester | 12-190 | 179 | chop | `WAIT;MOVE` | P1,P2 |
| m091-s0 | forest_sparse | idle | 91-199 | 109 | chop+harvest | `WAIT` | P1 |
| m091-s1 | forest_sparse | idle | 94-199 | 106 | chop+harvest | `WAIT` | P1 |
| m094-s1 | single_door_tent | idle | 1-199 | 199 | chop+harvest | `WAIT;MOVE` | P1 |
| m099-s1 | choke_corridor | harvester | 8-199 | 192 | chop | `MOVE` | P1 |
| m100-s0 | choke_corridor | harvester | 6-99 | 94 | chop | `WAIT;WAIT` | — |
| m101-s0 | water_diagonal | idle | 100-199 | 100 | chop+harvest | `WAIT` | P1 |
| m104-s1 | orchard_eligible | idle | 26-199 | 174 | chop+harvest | `WAIT;MOVE` | P1 |
| m106-s0 | choke_corridor | harvester | 11-199 | 189 | chop | `WAIT;WAIT` | — |
| m110-s1 | choke_corridor | harvester | 1-199 | 199 | chop | `MOVE` | P1 |
| m114-s1 | orchard_eligible | idle | 1-199 | 199 | chop+harvest | `WAIT;MOVE` | P1 |

(windows are the BEFORE numbers; after the rule the 24 trailing windows end at
200 instead of 199 — §6.)

### 4.3 Where post-`C_T` *does* bite on the floor

Scanning **all 240** floor games (`postct_scan.py`, MEASURED):

* **2 / 240** games make own progress at turn `T` that the pre-rule panel
  could not see: `m019-s0` (`PICK 0 BANANA;WAIT` — a banana leaves the bank
  and enters a unit's cargo) and `m104-s0` (`HARVEST 0;PICK 2 APPLE` — an
  apple harvested into cargo and one withdrawn). Neither game has a stall
  window, so neither verdict moves.
* **0 / 240** games gain a block from the new rule (no trailing run sits at
  exactly 59 live turns followed by an idle `C_T`).
* **0 / 240** games lose a block (no already-formed window ends with a
  productive `C_T`).

So on this floor the rule is **verdict-neutral** and purely a
boundary-correctness fix. INFERRED: its practical effect will appear on
candidates whose games end mid-task (the `7ad9d784`-class candidates that
already show 79 P4 games), where a 59-live-turn tail plus an idle final turn
is a plausible shape.

---

## 5. The rule as implemented

**Predicate (ABSOLUTE — a function of the candidate's own recorded world
state; no parent reference, no inherited exemption, no command-pattern
heuristic):**

> turn `T` is a **stalled turn** ⟺ `work_remaining(S_T)` **and** resolving
> `C_T` changes neither the own inventory nor any own unit's cargo.
>
> — the **obligation** is set by the *pre*-state (only a world that still
> offers a resource action can demand one; unchanged from the 2026-08-06
> terminal calibration), the **outcome** is read off the *post*-state.

Turns `1..T-1` are unchanged. Stall windows are still maximal runs of
progress-free turns, still trimmed to their live prefix, and still block iff
≥ `liveness_window` live turns remain — the only change is that turn `T` is
now inside the accounting domain instead of being exempt by construction.

Code (all in `claude_1/pipeline/fuzz_panel.py`):

* `post_ct_state(ref)` — the panel's own referee, once the loop has applied
  `C_T`, re-parsed through the transcript parser so it is the same
  `td.GameState` type every other predicate consumes. No detector or referee
  module was modified; `regression_tests.run_binary_custom` is untouched.
* `post_ct_progress(tr, post)` — `progress_turns`' own predicate applied to
  the `S_T -> post` transition. Opponent inventory/cargo motion and plant
  growth are world motion, not own progress, and are ignored exactly as they
  are for turns `1..T-1`.
* `stall_windows(prog, T, window, last_known=None)` — `last_known` is the last
  turn whose *outcome* is known. It **defaults to `T-1`**, so every pre-existing
  caller is byte-identical; the post-`C_T` caller passes `T`.
* `eval_p4(tr_c, tr_p, window, post_state=None)` — sets `last_known = T` and
  adds `T` to the progress set when `post_ct_progress` holds.
  `post_state=None` preserves the pre-rule behaviour for callers that cannot
  supply a referee (the outcome of `C_T` is then genuinely unknown, so the
  final turn carries no obligation). `run_pair` **always** supplies it, and a
  test pins that (mutation M7).
* `tr_p` is still never consulted; `test_no_parent_reference_in_eval_p4_body`
  still passes (no `parent`/`inherit`/`aligned`/`tr_p` token in the body).

**Deliberately NOT done:** the rule does not let a productive `C_T`
retroactively excuse an already-formed window — a 160-turn stall that ends
with a bank is still a 160-turn stall (`test_completing_work_at_C_T_does_not_
excuse_a_longer_stall`). Any such "the last action completed the task, so
forgive the stall" reading would be exactly the over-exemption the brief warns
against, and §4 shows it would buy nothing anyway (0/30).

**No config flag was added** — the rule is unconditional and needs no
calibration constant, so `fuzz-panel-config.json` is unmodified.

---

## 6. Floor before → after (MEASURED)

Parent judged against itself; 120 maps × 2 seats = 240 candidate games; 200
turns; `liveness_window` 60; seeds
`[982451653, 15485863, 32452843, 49979687, 67867967, 86028121]`.

| metric (unit) | BEFORE | AFTER |
|---|---|---|
| games | 240 | 240 |
| **blocking games** | **118** | **118** |
| flagged (report-tier) games | 0 | 0 |
| wall time | 16.2 s | 11.6 s |

Per property, **games with ≥ 1 blocking violation**:

| property | BEFORE | AFTER |
|---|---|---|
| P1 (detectors) | 114 | 114 |
| P2 (R-5 alternation) | 4 | 4 |
| P3 (orchard inertness) | 0 | 0 |
| **P4 (liveness)** | **29** (30 episodes) | **29** (30 episodes) |
| P4-only games | 4 | 4 |

Per detector, **games / (games with ≥1 episode)**:

| detector | BEFORE | AFTER |
|---|---|---|
| D-1 | 32 | 32 |
| D-4 | 6 | 6 |
| D-5 | 1 | 1 |
| D-6 | 9 | 9 |
| D-7 | 0 | 0 |
| D-9 | 74 | 74 |

Per-game diff of the two `--json` outputs: **0 games changed verdict**;
**24 games changed their P4 violation payload** — the trailing windows now end
at turn **200** instead of 199 (e.g. `m003-s0`: `(22, 199, live_end 199)` →
`(22, 200, live_end 200)`), i.e. the final turn is finally accounted for.
Downstream consumers that string-match P4 `why` text or window ends should
expect that one-turn shift.

---

## 7. What this implies for D-7 — REFERRED to `local_claude_1`, not implemented

`trace_detectors.py` is out of my boundary and is byte-identical before and
after this change (sha256 `59dce10d…`). The same post-`C_T` gap exists in D-7
and is **larger** there, because D-7's obligation is about outcomes (banked or
planted), not about a rolling window. Concretely, at
`trace_detectors.py:979-981` the per-unit loop does `if t + 1 > T: break`, so
the banana ledger never sees `C_T`:

1. **False positive (leniency needed).** A unit holding bananas at `S_T` whose
   `C_T` is `DROP` at a door (banking them) or `PLANT BANANA` still shows the
   bananas in `S_T`; the end-of-game sweep at `:1011-1016` then emits
   `unbanked_at_end` for fruit that *was* banked. The existing exemption only
   covers `prov == "harvest"` acquired in the final 6 turns, so a banana
   harvested at `T-8` and banked at `T` is reported lost. MEASURED on this
   floor: **0 occurrences** (no banana carry decrement at `T` in any of the
   240 games), so this is latent here; INFERRED to matter for candidates whose
   games end mid-delivery (`7ad9d784` shows D-7 35 games / 67 episodes).
2. **False negative (strictness needed).** `lost_bananas` (`:996-1007`) needs
   the `t -> t+1` carry delta, so a unit that drops bananas illegally on the
   final turn is undetectable today. Post-`C_T` would catch it. MEASURED:
   0 on this floor.
3. **The trap — a naive post-`C_T` extension makes D-7 *worse* on this floor.**
   `m019-s0`'s final command is `PICK 0 BANANA;WAIT`: the unit withdraws a
   banana from the bank at turn `T`. Extending D-7's loop to `T` registers a
   FIFO entry with `prov == "bank_pick"` and acquisition turn `T+1`, which the
   `unbanked_at_end` sweep then reports, because the "final 6 turns" excuse is
   restricted to `prov == "harvest"`. **D-7 would go 0 → 1 episodes on the
   floor for a bot that did nothing wrong** (there is no turn left in which to
   bank). MEASURED: exactly 1 game on this floor (`m019-s0`, unit 0, delta
   `+1` banana, verb `PICK`).

Recommendation for the owner of `trace_detectors.py` (NOT implemented here):
if D-7 adopts the post-`C_T` state, the end-of-game excuse must be widened
from "harvested in the final 6 turns" to "acquired with no remaining turn in
which the obligation could be discharged" — i.e. anything acquired at `T`
(any provenance) plus the existing harvest window. The same
obligation/outcome split I used for P4 transfers directly: **the pre-state
sets the obligation, the post-state records the outcome.** The evidence file
is `games-before/games.jsonl.gz` (sha above), game `m019-s0`.

---

## 8. TDD and the mutation ledger

**RED** (commit `49c3204b`, tests only): 11 tests, recorded failure —
7 × `TypeError: eval_p4() takes 3 positional arguments but 4 were given`,
`AttributeError: module 'fuzz_panel' has no attribute 'post_ct_progress'`,
`… 'post_ct_state'`,
`TypeError: stall_windows() takes 3 positional arguments but 4 were given`,
`AssertionError: 1 != 2 : one P4 evaluation per game`
→ `Ran 11 tests — FAILED (failures=1, errors=10)`.

**Both-sided coverage** (the escape-hatch guard): `test_final_turn_that_banks_
is_progress_and_passes` and `test_final_turn_cargo_change_is_progress_and_
passes` require a game whose work IS completed by `C_T` to pass;
`test_idle_final_turn_completes_the_stall_window`,
`test_opponent_only_change_at_C_T_is_not_own_progress` and
`test_completing_work_at_C_T_does_not_excuse_a_longer_stall` require a game
that genuinely stalls to the horizon with work remaining to keep blocking.
All five share one base fixture in which turns 5-9 are exactly five
observable stalled turns — one short of the window — so the verdict turns
**entirely** on how turn `T` is counted, and neither direction can pass by
accident.

**GREEN** (commit `974042d3`): `test_fuzz_panel` **40/40 OK**,
`test_pre_review` **24/24 OK** (both pre-existing suites, unmodified apart
from the added P4 tests).

**Mutation ledger** — `mutate.py` copies the module into a scratch package
(with `banana-restoration-r2` symlinked so imports resolve; the repo is never
mutated), applies one mutation, and runs the whole `test_fuzz_panel` suite.

| # | mutation | verdict | failing tests |
|---|---|---|---|
| M0 | unmutated control | **survives (OK)** — as it must | — |
| M1 | `post_ct_progress` **always True** | **CAUGHT** (3) | idle_final_turn_completes_the_stall_window, opponent_only_change_at_C_T, post_ct_progress_predicate |
| M2 | `post_ct_progress` **always False** | **CAUGHT** (4) | completing_work_at_C_T_does_not_excuse_a_longer_stall, final_turn_cargo_change, final_turn_that_banks, post_ct_progress_predicate |
| M3 | `stall_windows` final-run boundary off by one (`n+1-start` → `n-start`) | **CAUGHT** (3) | idle_final_turn…, opponent_only_change…, stall_windows_last_known_turn |
| M4 | rule removed (`last_known = T` → `T-1`) | **CAUGHT** (2) | idle_final_turn…, opponent_only_change… |
| M5 | final turn **always** stalled (outcome ignored) | **CAUGHT** (3) | completing_work…, final_turn_cargo_change, final_turn_that_banks |
| M6 | `post_ct_progress` reads the **opponent** inventory | **CAUGHT** (4) | completing_work…, final_turn_that_banks, opponent_only_change…, post_ct_progress_predicate |
| M7 | call site passes `None` instead of the post state | **CAUGHT** (1) | panel_supplies_the_post_ct_referee_state_to_p4 |
| M8 | `stall_windows` ignores `last_known` | **CAUGHT** (3) | idle_final_turn…, opponent_only_change…, stall_windows_last_known_turn |

**8 caught / 0 survived.** In particular the always-true and always-false
mutations are each caught by tests on the *opposite* side, which is the defect
class (D-9, D-6, I-30 tie-break) this programme has hit three times.

---

## 9. UNRESOLVED

1. **`UNRESOLVED` — is "a choppable tree is reachable" a liveness
   obligation?** In 21 of the 30 residual windows the only action available on
   *every* turn is `CHOP`; the bot sits or paces next to a tree it declines to
   fell. Chopping destroys a fruit source, and the shipped
   `preseed-orchard-coverage` parent deliberately cultivates rather than
   chops — so P4 as written encodes a design opinion the reference
   implementation contradicts, the same shape as D-9's unpaired clause. The
   opinion-free subset is the **9 windows where a `HARVEST` was legal on every
   turn** (ripe fruit in reach, free capacity, `harvest_power > 0`): declining
   *those* for ≥ 60 turns is unambiguously a liveness bug. **Evidence that
   would settle it:** an owner ruling on whether P4's `work_remaining` should
   count destructive actions; if it should not, the residual is 9 windows /
   9 games, and the floor's P4-only term drops accordingly. I did **not**
   change this — it is a semantics ruling, not a boundary fix. (INFERRED
   reading; the 21/9 split is MEASURED.)
2. **`UNRESOLVED` — P3 dormancy vs P4 liveness.** 3 of the residual windows
   are `orchard_eligible` maps, where P3 *requires* the candidate's command
   stream to byte-equal the parent's (designed inertness) while P4 demands
   progress. On the floor P3 is trivially satisfied (parent vs itself), so
   only P4 fires; a real candidate must satisfy both, and on those maps the
   two properties can be jointly unsatisfiable. **Evidence that would settle
   it:** whether any orchard-eligible geometry admits a command stream that is
   both byte-identical to the parent's and progress-making — decidable by
   replaying the parent stream and checking `progress_turns` on those 3 maps
   (not done here; out of scope for this item).
3. **`UNRESOLVED` — effect of the rule off the floor.** Verdict-neutral on
   this floor (§4.3). Its discriminating power on the `7ad9d784`-class
   candidates (79 P4 games) is unmeasured. **Evidence that would settle it:**
   the same before/after diff run against those candidate sources; it is a
   `--config` swap, but candidate runs were out of scope for this item.
