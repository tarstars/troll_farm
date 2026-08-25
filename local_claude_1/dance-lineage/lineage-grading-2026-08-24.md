# The dance lineage — is the surviving 11 % old or new?

**Answer, in one line: it is old.** The champion of record (door 1, `547fa706…`, which has no swap
cure) dances in **16.80 %** of its 2-unit real ladder games; the very-old bot `98628e98…` dances in
**17.37 %**; cure C in **16.85 %**; the NARRATE instrument in **14.57 %**. Measured on the same
ladder, in alternating two-hour slots on the same nights, the three older generations are
indistinguishable from one another. The dance does **not** appear at any step of the recent
lineage — it was already there.

- Date: 2026-08-24 · run by: local_claude_1 (coordinator) on `project_host`
- Script: `local_claude_1/dance-lineage/grade_lineage.py` (deterministic; stdlib + the exported adapter)
- Results: `local_claude_1/dance-lineage/results/lineage-grading-2026-08-24.json`
- Corpus: `/home/tarstars/prj/troll_farm/data/raw/games/` — 23,374 replays, read-only, indexed by
  parsing every replay's own `agents` array (never a text grep: JSON spacing varies)
- Volume: **11,342 (game, seat) traces / 3,068,967 turns graded**, of which **5,313 traces /
  1,431,679 turns are our own seat** across 45 pinned agent ids

## Instrument — used unmodified, identity checked before any game was read

`claude_1/adapter1/replay_to_trace.py` (the G-1 ACCEPTED replay→`Trace` adapter) plus
`claude_1/banana-restoration-r2/trace_detectors.detect_d1/d2/d3`, exported with
`git archive 7b623b1bbcfd4acc7205fa6214878c5ecbcf912a` (head of `origin/agent/claude_1`) and never
edited. The archive list had to be extended by `sim` and `bot`, which
`cgauto.recent_resident_field_census → cgauto.replay_state → sim.engine → bot.main` imports; nothing
was copied from a worktree by hand.

    sha256(claude_1/adapter1/results/adapter-panel-2026-08-23.json)
      = ce72ec22a4cf45fdd39e0909691057c559c781b6f6a993ed5d1094a7f85c1eea   ✓ MATCHES

`grade_lineage.py` refuses to run if that hash does not match. Detector results are read as
`result["count"]`, and every call asserts `count == len(episodes)` — the 08-23 near-miss that
almost shipped 149 × 4 = 596 cannot recur here.

**Seat** is resolved by the adapter from the replay's own `agents` array by `agentId`
(`resolve_seat(..., agent_id=…)`), never from a battle-listing position — `docs/METHODS-LEDGER.md`,
`seat-from-the-replay`. Our account is `codingamer.userId == 1302251`, pseudonym `tass`.

## The pinned agent table

Every id below is tied to a source sha256 by a written record. The full citation for each id is in
the results JSON under `pins` (46 entries, one per agent).

| lineage | source sha256 | agents | record |
|---|---|---|---|
| pre-cure July | `1a55319e…` (`cgauto/submissions/v1.2.2-farmcap.rs`) | `6536563` | `data/README.md:46-47` (agentId 6536563, live code `v1.2.2-farmcap` per in-game MSG) + `claude_1/block-index/block-index.json` (that file's sha256). **Indirect pin** — agent → build name → file sha |
| very-old `98628e98…` | `98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29` | `6593838` | `local_claude_1/cure-c-night-2026-08-18.md:15` — arm B's source file is `submitted-agent6593838-readable-no-orchard.rs`, sha `98628e98…` |
| " | " | `6632048, 6633209, 6633935, 6634792, 6635217` | `cure-c-night-2026-08-18.md:15,52,54,56,58,60` — cure-C night B arms |
| " | " | `6644257, 6645217, 6646271, 6647102, 6647689` | `git show fe0ed7f8:local_claude_1/door1-vs-old-2026-08-20-state.json` — session 3 block 1, `arms.B.sha256` |
| " | " | `6648091, 6648682, 6649241, 6649868, 6650168` | `git show 0cd83d12:…door1-vs-old-2026-08-20-state.json` — session 3 block 2 |
| cure C `ad3bfefe…` | `ad3bfefe4b2326f4f6b4a270dc862ea19a0e319a1cddfde44b96cc6f6d35a5d1` | `6631618, 6632611, 6633433, 6634457, 6634986` | `cure-c-night-2026-08-18.md:14,50,53,55,57,59` — cure-C night A arms |
| " | " | `6640802, 6641617, 6642442, 6643172, 6643465` | `local_claude_1/door1-night-state.json`, `arms.B.sha256` + reads B1–B5 |
| **door 1** `547fa706…` | `547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0` | `6640462, 6641056, 6642046, 6642773, 6643278` | `door1-night-state.json`, `arms.A.sha256` + reads A1–A5 |
| " | " | `6643835, 6644785, 6645883, 6646733, 6647370` | `git show fe0ed7f8:…door1-vs-old-2026-08-20-state.json` — block 1 A arms |
| " | " | `6647954, 6648254, 6648976, 6649705, 6650034` | `git show 0cd83d12:…door1-vs-old-2026-08-20-state.json` — block 2 A arms |
| " | " | `6650438` | `docs/STATE.md:15-17` (champion of record `41178858` / `6650438`, sha `547fa706…`) + `door1-vs-old-pooled-verdict-2026-08-22.md` ("opened block 3 and submitted arm A (submission 41178858)") |
| instrument v2 | `aaebc503cc2660e920d45858767c6932575324085c93ef9345906f683b5a9271` | `6652424, 6652602` | `local_claude_1/narrate/aaaaa-block-2026-08-23.md:7-8,16,17` |
| instrument v3 | `9a3e875823f3fc26bb7be04f67d872d5c5590f4479f771cae4402ed1e3281239` | `6652642` | `aaaaa-block-2026-08-23.md:76-78` + `docs/STATE.md:15-17` |

**Corrections to the brief's starting list, both from the recovered ledgers, not from inference.**
Block 1's missing A4/A5 are `6646733` / `6647370` and its B4/B5 are `6647102` / `6647689`; block 2
runs `6647954 … 6650168`. The order is strict **ABAB**, not ABBA — each state JSON labels every read
with its arm, so no ordering had to be assumed.

**Unpinned and excluded: `6536359`** (1 corpus game). `data/README.md:50` counts it only as
"(+1 where tass appears in a top player's list)"; no record names its source. The 08-23 grading
folded it into `OLD-ours`; here it is excluded rather than guessed. That single game
(`895017865`, seat 1, units = 4, D-1 0 / D-2 0 / D-3 6) is the **only** difference between this
report's pre-cure-July rows and the 08-23 `OLD-ours` rows, which are otherwise identical
row-for-row.

Also listed in the JSON (`ungraded_own_agents`): **50** further agent ids of our account appear in
the corpus and belong to no pinned cohort. They were not graded and nothing is claimed about them.

## The lineage table — own-unit count 2 only

Every one of our recent bots runs exactly two trolls in every game, so all of `very-old`, `cure-C`,
`door-1` and `instrument` are wholly inside units = 2. The pre-cure July bot ran 2, 3 or 4; its
other unit counts are separate rows below and are never merged.

`d1 %` = share of games with at least one dancing episode. `/1k` = episodes per 1,000 of that
seat's turns.

| bot (lineage order) | games | turns | **D-1 eps** | **D-1 games** | **d1 %** | 95 % CI | /1k | D-2 eps | D-2 games | D-3 eps | D-3 games |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| **pre-cure July** `1a55319e…` | 51 | 14,691 | **0** | **0** | **0.00 %** | [0.00, 7.00] | 0.000 | 0 | 0 | 59 | 22 |
| — its opponents | 47 | 13,399 | 15 | 7 | 14.89 % | [7.41, 27.69] | 1.119 | 4 | 2 | 43 | 10 |
| **very-old** `98628e98…` | 1,808 | 491,548 | **391** | **314** | **17.37 %** | [15.69, 19.18] | 0.795 | 0 | 0 | **0** | **0** |
| — its opponents | 1,176 | 310,659 | 246 | 126 | 10.71 % | [9.07, 12.61] | 0.792 | 586 | 109 | 363 | 139 |
| **cure C** `ad3bfefe…` | 1,098 | 292,358 | **223** | **185** | **16.85 %** | [14.75, 19.18] | 0.763 | 0 | 0 | **0** | **0** |
| — its opponents | 665 | 168,818 | 148 | 66 | 9.92 % | [7.88, 12.43] | 0.877 | 263 | 56 | 297 | 129 |
| **door 1 — the champion** `547fa706…` | 1,821 | 487,276 | **382** | **306** | **16.80 %** | [15.16, 18.59] | 0.784 | 0 | 0 | **0** | **0** |
| — its opponents | 1,181 | 305,450 | 230 | 125 | 10.58 % | [8.96, 12.47] | 0.753 | 474 | 85 | 423 | 171 |
| **instrument** (swap R-1 + telemetry) | 446 | 119,284 | **80** | **65** | **14.57 %** | [11.60, 18.15] | 0.671 | 0 | 0 | **0** | **0** |
| — its opponents | 279 | 72,569 | 72 | 36 | 12.90 % | [9.47, 17.35] | 0.992 | 65 | 16 | 81 | 42 |
| *(memo)* instrument, the 08-23 149-game batch | 149 | 38,869 | 22 | 17 | 11.41 % | [7.25, 17.51] | 0.566 | 0 | 0 | 0 | 0 |

Pre-cure July at other unit counts (never merged into the above): units = 3 — 56 games / 16,622
turns / D-1 1 in 1 game / D-3 305 in 45; units = 4 — 33 games / 9,900 turns / D-1 0 / D-3 266 in 32.
Opponent rows at other unit counts are in the results JSON.

### The differences, tested

Two-proportion tests on the share of games showing a dance, units = 2:

| comparison | rates | z | p |
|---|---|---:|---:|
| door 1 vs very-old | 16.80 % vs 17.37 % | −0.45 | 0.652 |
| door 1 vs cure C | 16.80 % vs 16.85 % | −0.03 | 0.975 |
| door 1 vs instrument | 16.80 % vs 14.57 % | 1.14 | 0.254 |
| very-old vs instrument | 17.37 % vs 14.57 % | 1.41 | 0.158 |
| door 1 vs pre-cure July | 16.80 % vs 0.00 % | 3.20 | **0.0014** |
| very-old vs pre-cure July | 17.37 % vs 0.00 % | 3.26 | **0.0011** |
| instrument vs pre-cure July | 14.57 % vs 0.00 % | 2.92 | **0.0035** |

### Same-night head-to-heads — the strongest form of this comparison

The A/B nights alternated two bots on the same ladder every ~2 hours, so these three rows compare
generations on the same field in the same hours, not across eras. All three are flat.

| block | arm A | arm B | A d1 % | B d1 % | difference | p |
|---|---|---|---:|---:|---:|---:|
| cure-C night 2026-08-18 | cure C (642 g) | very-old (591 g) | 17.76 % | 18.27 % | −0.52 pts | 0.813 |
| door-1 night 2026-08-20 | door 1 (480 g) | cure C (456 g) | 16.46 % | 15.57 % | +0.89 pts | 0.711 |
| session 3, blocks 1+2, 08-21…22 | door 1 (1,182 g) | very-old (1,086 g) | 16.67 % | 16.67 % | **+0.00 pts** | 1.00 |

Per-agent figures (all 45 pinned ids, one row each) are in the results JSON under `per_agent`. Every
agent from `6593838` onward lands between 10.1 % and 23.9 %; the spread is agent-to-agent noise at
40–160 games each, with no trend along the lineage.

## Controls

**1 — Reproduction of the 2026-08-23 grading. PASS, exactly.** Re-grading the same 149 replays at
`local_claude_1/narrate/games/` gives, at units = 2: games **149**, turns **38,869**, D-1 **22**,
D-1 games **17**, D-2 **0**, D-3 **0** — identical to `g1-first-grading-2026-08-23.json` in every
field. The `units` field was verified to be `len(trace.own_ids)` (distinct own unit ids seen
anywhere in the traced game) by reproducing the 08-23 rows before the run.

**2 — Detector-alive control. PASS, and a scope correction.** All 290 git-tracked in-repo games,
both seats = **580 pairs / 170,631 turns → D-1 77, D-2 90, D-3 1,565**. The detectors fire on
replay-derived traces from other players' bots, so the zeros above are real zeros.

The figure recorded in the 08-23 handoff — *"240 in-repo pairs / 70,562 turns … D-1 24, D-2 27,
D-3 206"* — is **not** the 290-game corpus: it is the **first 240 rows of that same sweep in
(game, seat) order**, i.e. the first 120 games. Reproduced here exactly: 240 pairs, 70,562 turns,
D-1 24, D-2 27, D-3 206. Both scopes are reported so neither number is quoted for the other.

**3 — Fail-closed accounting. 15 refusals of 11,357 attempted traces (0.13 %), listed by reason.**
Nothing was partially decoded.

| reason | n | which |
|---|---:|---|
| `Trace kept N turns of M; the streams were not aligned before parsing` | 13 | all opponent seats, all one player, agent `6479483` (games `899563256, 899563723, 899570963, 899571122, 899571326, 899589763, 899589891, 899590097, 899600873, 899606329, 899621362, 899632859, 899632887`) — that bot emits blank command rows mid-game, which `CommandParser` strips |
| `frame 1 has no stdout` | 2 | game `900029997`, **both** seats — our door-1 agent `6650438` and its opponent `6479840` |

Exactly **one of our own** (game, seat) traces was refused: door 1, game `900029997`. The door-1
cohort is therefore 1,821 of 1,822 games.

**4 — Determinism. PASS.** The full run was executed twice, with **different worker counts** (10
and 6), and the two results files are byte-for-byte identical:
`sha256 = 586142ad00a0428cf9863e6d6e15d69e6fa11af5cf4a51747c9b5cd72ea028de`.

## Caveats — every one of them applies to the table above

- **D-1 off replays is an UPPER bound.** The adapter's own §6: plant health/stage/cooldown in the
  emitted transcript are *reconstructed* by `DiffDecoder.tick_existing_plants` /
  `apply_known_chops`, not observed. That touches one of D-1's three progress tests ("a plant
  created or removed at u's cell"); a missed create/remove is a missed progress event, which fails
  to break a window that should have been broken. **The error direction invents dancing.** It is
  applied identically to every cohort, so it biases the *level* of every row and not the
  *comparison* between them — unless a bot's play changes how often plants appear under its own
  trolls, which is not measured here.
- **Different days and different opponent draws.** The cohorts were collected 2026-07-03
  (pre-cure July), 08-18, 08-20, 08-21, 08-22 (very-old / cure C / door 1) and 08-23 (instrument),
  against a moving Legend field. The three same-night blocks above are the only comparisons free of
  that, and they cover very-old ↔ cure C ↔ door 1 but **not** the instrument, which was never
  paired against anything.
- **The instrument's command stream is not the champion's.** It carries swap R-1 *and* per-turn
  `MSG` telemetry. Its 14.57 % is a reading of a different program, and its 446 games are the
  smallest cohort here.
- **The pre-cure July row is a different era and a different bot in every respect** — July 2026,
  Gold league, `v1.2.2-farmcap`, 51 games at units = 2, a corpus collected for a different purpose.
  It is also the one **indirect** pin (agent → build name via in-game `MSG` → file sha).
- **`units` counts distinct own unit ids over the whole game**, matching the 08-23 field, not "alive
  at turn 1" — at turn 1 every seat has exactly one troll. This is a deviation from the wording of
  the charter, taken deliberately so the reproduction control is an identity.
- **Not established here:** why any dance happens, what the trolls wanted, whether D-1 as defined is
  a defect at all, or what any cure did or did not do. This report counts; it does not explain and
  it does not rule.

## The plain-words answer

The champion dances at the very-old bot's rate — the two are the same number to within a fifth of a
percentage point, and when they were run against each other on the same ladder in alternating
two-hour slots over two nights the difference came out at exactly zero over 2,268 games. Cure C sits
on the same number. The instrument, the one bot carrying the swap cure, reads a little lower —
14.6 % against 16.8 %, or 11.4 % on the 149-game batch the 08-23 grading used — but that gap is
inside the noise of 446 games (p = 0.25) and it was measured on a different day against a different
field, so it is **not established** as a real difference. What *is* established is that the
surviving 11 % is **old**: it does not appear at any step of the recent lineage, because it was
already fully present in the oldest bot we graded here, `98628e98…`, three generations back. The one
place a step does show is much further back — the July `v1.2.2-farmcap` bot shows zero dancing in 51
two-troll games (p ≈ 0.001 against every later bot) while showing plenty of the *other* defect,
own-troll contention, which the recent bots show none of. That boundary is real in the numbers but
it is confounded with everything else that changed between July and August, so it names a place to
look, not a cause. Nothing here says the dance is a bug rather than a correct caution, and nothing
here grades a cure.
