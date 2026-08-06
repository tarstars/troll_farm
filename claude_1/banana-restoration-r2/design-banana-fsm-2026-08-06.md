# Design — banana wrapper state machine + interference contracts (r2)

Date: 2026-08-06. Status: DESIGN (retrospective consolidation; no code changes).
Task: `20260802-banana-restoration-r2`.

Sources (all claims about past defects cite these):

- SPEC = `claude_1/banana-restoration-r2/invariant-spec-2026-08-04.md` (incl. revision
  blocks 2026-08-04, 2026-08-05 CONVERSION_RACE_ORACLE, 2026-08-06 abandonment-release).
- SEAM = `claude_1/banana-restoration-r2/integration-seam-2026-08-04.md`.
- ACK1 = `origin/agent/local_codex_1:coordination/messages/local_codex_1/20260804T213001Z-20260802-banana-restoration-r2-ack.md`.
- ACK2 = `...20260805T083001Z-20260802-banana-restoration-r2-ack.md`.
- ACK3 = `...20260805T143001Z-20260802-banana-restoration-r2-ack.md`.
- R5 = `claude_1/banana-restoration-r2/diagnosis-r5-2026-08-05.md`.
- R6 = `claude_1/banana-restoration-r2/diagnosis-r6-2026-08-06.md`.
- I1 = `claude_1/banana-restoration-r2/banana_blocks/block-i1.rs` (as-built SNAPSHOT read
  2026-08-06; line numbers are that snapshot's; the file may have moved under concurrent work).
- ORACLE = `claude_1/banana-restoration-r2/conversion_race_oracle.py`
  (`conversion_race_oracle`, the one named oracle; SPEC Revision 2026-08-05).

Design stance: the composed system failed five times not because any single rule was
missing but because the wrapper's *implicit* states (camping, lost-hold, convert latch,
release) and its five coupling channels were never specified as a closed machine. This
document closes both: (A) a total FSM, (B) one contract per channel, (C) proof that every
observed defect lands on a named element, (D) the verification pyramid, (E) the as-built delta.

---

## A. State machine (complete, closed)

### A.0 Conventions

1. One FSM instance per game; the FSM owns exactly one unit slot (the resident = starter,
   SPEC B3/C1) and one cell slot (the latched mother, SPEC I-13/I-29).
2. `task` ranges over `BananaTask = {Boot, Plant, Chop, Harvest, Bank, Idle}` (I1:63-71).
3. "Emitted intervention set" = which of the six channels of section B the state may touch
   this turn. Channels: CH1 `banana_idle_unit`, CH2 `banana_protected_cell`,
   CH3 resident `replace_action` post-edit, CH4 non-resident veto post-edit,
   CH5 C8 re-resolution, CH6 arbitration read.
4. Liveness horizons cite SPEC I-19/I-20/I-21 (commitment persistence, monotone progress,
   forced commitment).
5. Names: `S-DORM`, `S-WORK`, `S-CONV` etc. map onto as-built names where they exist
   (`BananaPhase::{Dormant,Active,Abandoned}`, `banana_lost`, `banana_lost_banking`,
   `banana_idle_streak`, `banana_target == (Chop, mother)`); the mapping is in A.1 and E.

### A.1 State enumeration (10 persisted states; S-WORK parameterized by 5 tasks)

Note (F2): the former S6 "HarvestNow" is NOT a persisted state — it is the Mealy `HARVEST`
output of EV4 attached to the persisted state the resident already occupies (S3/S4/S5). The
row below is retained only to document that output mode; it is never a transition target and
never decoded from persisted fields (see the Mealy declaration in A.2 and A.4).

| id | name | as-built encoding (I1 snapshot) |
|---|---|---|
| S0 | Unarbitrated | `banana_enabled == None` (turn-1 pre-decision, I1:1004-1006) |
| S1 | Disabled | `banana_enabled == Some(false)` (apple game, permanent) |
| S2 | Dormant | enabled, `phase == Dormant` |
| S3 | ActiveWork(task ∈ {Boot,Plant,Chop,Harvest,Bank}) | `phase == Active`, `banana_target == Some((task,cell))`, `task != Idle`, not the Chop-mother latch. `ActiveWork(Boot/Plant)` is the Founding/CarryingSeed analog; `ActiveWork(Chop/Bank)` is the WoodCycle. Distinct commitments, one state family (ratified in E, GAP-3) |
| S4 | ActiveIdle | `phase == Active`, chosen candidate Idle, `banana_idle_streak ∈ {1,2}`; includes the F-B1 idle-yield aside move |
| S5 | ActiveReleased | `phase == Active`, `banana_idle_streak >= 3` (F-D2 starvation release; reservation dropped, resident inner-controlled) |
| ~~S6~~ | HarvestNow (OUTPUT MODE, not a state — F2) | the EV4 Mealy output `HARVEST` emitted from S3/S4/S5 (I1:649-664): flip latched this turn, ripe fruit harvestable immediately (resident on mother, capacity free). Persisted state is UNCHANGED; the flip is re-observed next turn. Never a transition target, never decoded from persisted fields |
| S7 | Converting | contest-response branch 2 latch: `banana_target == Some((Chop, mother))` (I1:626-638; set nowhere else — ring Chop candidates are orthogonal-only) |
| S8 | LostBanking | `banana_lost && banana_lost_banking` (I-10a branch 3 with leftover cargo; I1:737-751, 1033-1044) |
| S9 | LostReleased | `banana_lost && !banana_lost_banking` (resident permanently inner-controlled; persistent claim while lost plant lives — SPEC Rev 2026-08-06) |
| S10 | AbandonedBenign | `phase == Abandoned && !banana_lost` (deadline / completion / resident death; structural identity thereafter) |

### A.2 Per-state specification

Format per state: **entry** / **evaluation order** (what is checked first each turn) /
**interventions** (channels this state may touch) / **exits** (guarded transitions, T-ids)
/ **liveness** (obligation + horizon).

**Causal per-turn phase order (R1a / review §R1 / F1).** A turn is a single atomic
evaluation, but its internal causality is an explicit FIVE-PHASE order so that no event is
consumed before the phase that can produce it. The prior draft selected the transition in
step 1 *before* commands existed, yet EV10 is command-produced the same turn (review R1.1) —
a causal impossibility. The phases below fix that: **transition selection is PHASE-5, after
command-derived events are observed in PHASE-4.** The whole turn is still a pure function of
(`S_t`, persisted FSM fields); "phase" names causal precedence, not extra state.

- **PHASE-1 — read state + observe pre-action events.** Read `S_t` (view + latched FSM
  fields). Observe every event whose source is pre-action `S_t` or inferred `S_{t-1}->S_t`
  (A.6 table): EV1-EV9, EV12-EV20. These are frozen now. EV20's dynamic bank-route
  reachability (F7) is a PHASE-1 predicate on `S_t` (occupancy included), not a landed fact.
- **PHASE-2 — arbitration / eligibility (pre-delegation).** S0 arbitration (CH6, once);
  phase update (activation / death / completion, pure view read); and the resident's
  **pre-delegation decision**: (a) blocked/bounce bookkeeping (F-B3); (b) Converting latch
  check; (c) **ownership + asset-threat evaluation** (EV4-EV7 via ASSET_SURVIVAL_ORACLE,
  A.7) on EVERY active turn, all activities, before candidate work; (d) contest branches;
  (e) candidate set + commitment rule (SPEC §e); (f) carrier-yield arbitration (R4/F5,
  §B.1) then idle-yield / starvation release. This phase fixes the resident's INTENDED verb
  and the channel-write intent (CH1/CH2), but selects no transition yet.
- **PHASE-3 — inner delegation produces candidate commands.** CH1/CH2 are written as a pure
  function of the PHASE-2 intent; the inner policy is delegated once and returns candidate
  commands for every slot. No hidden second evaluation occurs (F9).
- **PHASE-4 — observe command-derived events.** Observe the events that only exist once
  commands do: **EV10** (the resident/inner verb this turn acquires wood that fills
  capacity — knowable from the candidate command + current cargo, and confirmed against the
  post-command projection). Any future command-produced event is observed here. No such
  event is read in an earlier phase.
- **PHASE-5 — select transition + apply channel post-edits.** With ALL events known
  (pre-action ∪ inferred ∪ command-produced), select the single highest-priority live
  transition by the A.6 total order — this fixes `S_{t+1}`. Then apply post-edits in order:
  CH3 (resident replace_action) → CH4 (non-resident vetoes) → CH5 re-resolution iff CH3
  rewrote a command. Finally emit the **channel-touch + channel-record telemetry** (F9,
  §D.1): one record per edited/vetoed slot AND one per pre-delegation channel effect
  (CH1 idle-insertion, CH2 candidate-removal) captured inside PHASE-2/3.

**Observability rule (F1, normative):** an event may be consumed only in or after the phase
that can produce it. EV10 (command-produced) is therefore never an input to a transition
selector that runs before commands exist; it is observed in PHASE-4 and consumed in PHASE-5.

**Mealy declaration (R1 / F2). HarvestNow is an OUTPUT, not a state.** This is explicitly a
Mealy machine. The former "S6 HarvestNow", the S3 blocked-hold WAIT, and the S4 idle-yield
aside are **transient output modes**, not persisted states. The review (R1.2) showed S6
could not be both a non-persisted output AND a transition target with a decodable row: if it
is not persisted, next turn's decoder cannot select an "S6 row", so its edges are
unreachable. **Resolution (F2): S6 is removed as a persisted state and as a transition
target.** EV4 (flip ∧ ripe-on-cell) is a Mealy OUTPUT — `HARVEST` — emitted from a CH1=Some
state (S3/S4, or S5 after the ripe fruit re-employs the resident to S3, T5b); the persisted
next state is that CH1=Some state, unchanged (the flip/threat is re-observed next turn and,
if it persists, routes to S7/S8/S9 via EV5/EV6). There is no S6 row and no T6a. The persisted state family is therefore the
**ten** states S0-S5, S7-S10 (A.1); the persisted fields are exactly those in A.5.1; the
runtime decoder maps (persisted fields + `S_t`) to one of those ten states each turn and A-0
(§B.7) asserts the decode is single-valued. A transient output mode carries no obligation
into `S_{t+1}` beyond its persisted fields.

**S0 Unarbitrated.**
Entry: construction. Evaluation: run the read-only orchard-eligibility replica
(I1:143-178) on the turn-1 view, before any delegation (SPEC I-28).
Interventions: CH6 only. Exits: T0a eligible → S1; T0b ineligible → S2. Unconditional and
same-turn: S0 never survives a turn. Liveness: none (sub-turn state).

**S1 Disabled.**
Entry: T0a. Evaluation: none — structural identity; commands returned untouched.
Interventions: none; CH1/CH2 pinned `None`. Exits: none (absorbing). Liveness: none
(byte-equality with parent is the obligation, SPEC check 4 / I-27).

**S2 Dormant.**
Entry: T0b. Evaluation: deadline first, then activation predicate: `|own| >= 2` (I-16),
starter on ring, seed source exists (I1:938-977). Interventions: none; CH1/CH2 `None`.
Exits: T2a `turn > 100` → S10 (I-1); T2b activation predicate true → S3/S4 (first
resident decision picks the state; entering task from a fresh candidate recompute).
Liveness: none for the wrapper; funding-phase byte-equality with parent (I-17/I-18, D-9).

**S3 ActiveWork(task).**
Entry: T2b; from S4/S5 on productive-candidate reappearance (EV15); the EV4 HARVEST output
is an in-state S3/S4 turn (F2, no S6); task switches internal to S3 go through the commitment rule (SPEC §e: clause-1
invalidation, H=3 hold, eps=1 upgrade).
Evaluation order: global order; within 4e, wood cargo short-circuits to Bank-only
candidates (I-21, I1:442-445); surplus banana suppresses Plant candidates (I-9,
I1:461, 499); **founding guard for a diagonal Plant is `founding_safety_oracle` (A.7, F4)
`feasible_found` on the POST-PLANT `t+1` anchor** — exact executable-HARVEST safety (our
first harvest STRICTLY before the opponent's, ties = last-fruit duplication = unsafe; and
the sapling surviving choppers to our harvest), NOT arrival-order, no proxy ETA inequalities
(R2 replaces the old `eta_opp_h > first_fruit_delay ∧ eta_opp_x > 2*CD + ceil(health(2)/chop)`
of F-C1, which was a second approximate deadline); orthogonal wood slots keep instant
margins; Bank candidates skip occupied doors
while a free one exists (F-B2, I1:378-390); I-5 late cutoff blocks all planting (EV18 is
a guard, not a transition — planting candidates vanish, other tasks continue).
Interventions: CH1 = Some(resident); CH2 = Some(latched mother) iff a founded mother
lives; CH3 (one rewrite, resident only); CH4 (mother vetoes + seed exclusivity);
CH5 (priority = {resident}, forbidden set EMPTY — R5 ruling).
Exits: T3a EV4 → emit `HARVEST` output, persisted state UNCHANGED (F2: no S6);
T3b EV5 → S7; T3c EV6 → S8 (cargo>0) / S9 (cargo=0); T3d EV7
(asset-under-attack, design-new — see E GAP-1) → oracle-generalized convert-vs-abandon:
S7 if a conversion completes before the asset's value is destroyed, else S8/S9; T3e EV9
resident died → S10; T3f EV17 feature complete/impossible → S10; T3g task
invalidation/upgrade → S3(task') or S4 (only Idle candidate remains); T3h EV13 blocked 2
turns with same target still dominant and cargo-free → blocked-hold WAIT one turn
(sub-state of S3, I1:807-826), then re-probe; **T3i EV20 (F7) in S3(Bank): the committed
bank route is dynamically unusable (no conflict-resolved landing sequence to any door for a
bounded no-progress horizon, own-unit occupancy included) → hand the carrier back to the
inner economy (CH1=None), cargo kept, ownership to inner — the same production exit as
S8/T8d, so S3(Bank) can never loop on an occupied route (the DEF-09/DEF-12 class)**.
Liveness: (Bank) `door_dist` strictly decreases every unblocked turn, ≤1 consecutive
non-decrease, DROP within `door_dist(t_commit) + 2` turns (I-19/I-20; D-4 horizon).
(Chop/Harvest/Plant/Boot) BFS distance to target strictly decreases per unblocked turn;
verb lands within `eta + H + 2` turns or the target invalidates (I-26). Forced case: full
cargo ⇒ Bank commitment this turn (I-21).

**S4 ActiveIdle.**
Entry: from S3/T2b when the candidate maximum is Idle. Evaluation: global; plus F-B1
idle-yield — if camping the mother with a loaded teammate within Chebyshev 2, step aside
to the minimal free ortho neighbor that keeps every loaded teammate's bank reachable
(I1:847-907). Interventions: CH1 = Some(resident); CH2 as S3; CH3 (WAIT or aside MOVE);
CH4; CH5 iff CH3 rewrote. Exits: T4a EV14 3rd consecutive Idle → S5; T4b EV15 productive
candidate → S3; T4c EV4 → emit `HARVEST` output, state unchanged (F2, as S3/T3a);
T4d EV5 → S7; T4e EV6 → S8/S9; T4f EV17 → S10 (contest and phase exits identical to S3 —
the flip check precedes candidate work, so camping cannot hide a flip; DEF-06). Liveness:
dwell ≤ 3 turns holding the reservation (then S5); while camping, the N1 obligation of §B
(never the persistent obstacle of a loaded teammate) is the state's second obligation.

**S5 ActiveReleased.**
Entry: T4a. Evaluation: contest/phase checks still run (mother may flip while released);
candidate generator probed each turn for EV15; the release persists while the best
candidate is Idle or Bank-of-inner-cargo (I1:917-926 — banking inner-acquired cargo is
not lifecycle-productive; re-capture caused D-2 churn). Interventions: CH1 = None
(reservation released); CH2 as S3; CH4 (mother + seed vetoes still apply — the released
resident is protected-against like a peer); no CH3/CH5. Exits: T5a EV15 → S3; T5b EV4 → RE-EMPLOY
to S3 and emit `HARVEST` (F2: a ripe on-cell fruit is a productive candidate, so the
released resident is re-acquired — CH1=Some — for the harvest turn; persisted next state S3,
not a phantom S6); T5c EV5 → S7; T5d EV6 → S8/S9; T5e EV9 → S10; T5f EV17 → S10. Liveness: none for the wrapper; inner
economy owns the worker (P4 parity with parent is the gate).

**HarvestNow (EV4 output mode — NOT a state, F2).**
Trigger: EV4 — ownership flip (I-7, committed-harvester ETA, ties conceded) while a ripe
fruit is harvestable immediately (on-cell, capacity free). Effect: the Mealy output for the
resident this turn is `HARVEST` (CH3 = `HARVEST`; CH1 = Some; CH2 = Some(latched); CH5 if
CH3 rewrote), and the **persisted state is unchanged** (the resident stays in S3/S4/S5). No
transition into a distinct state occurs and no persisted discriminator is written, so there
is nothing to decode next turn. Next turn the flip/threat is re-observed from the top: if it
persists → EV5/EV6 → S7/S8/S9; if cleared (opponent left) the resident resumes S3/S4;
fruit-gone-with-flip-persisting → EV5/EV6. Liveness: exactly one HARVEST lands this turn;
the EV4 output cannot recur without a fresh ripe on-cell fruit, so it does not loop.

**S7 Converting.**
Entry: EV5 — flip latched and ASSET_SURVIVAL_ORACLE (A.7) `feasible_convert` (strict:
`completion_turn < asset_lost_turn`, absolute, anchored at the decision turn); or EV7 →
oracle-feasible attack response. Decision latched against re-OPTIMIZATION: a mere opponent
arrival on an already-won race does not reopen it (I1:614-638; I-10a "decided once").
Evaluation: latch check (4b) first, then the R6 infeasibility re-check (EV19). Interventions:
CH1 = Some; CH2 = Some(latched mother); CH3 = `MOVE`-to-mother / `CHOP`; CH4; CH5. Exits:
T7a EV8 mother destroyed (our final chop or opponent) → phase update: ring/stock live →
S3/S4, else → S10 via EV17; T7b EV9 → S10; **T7c EV19 conversion became IMPOSSIBLE (mother
unreachable / cell occupied by a working peer / a new deadline `asset_lost_turn <=
completion_turn` caused by a PATH loss, re-run each turn from `S_t`) → safe abandon: S8 if
`total_carried > 0` else S9** (R6: every commitment has an infeasibility exit; this is
distinct from re-optimization — a still-reachable, still-winnable race is never abandoned).
Liveness: while EV19 does not hold, the final chop lands on or before `completion_turn`
(A-12) and distance-to-mother strictly decreases while traveling; EV19 firing is bounded
(one BFS/oracle probe per turn) and terminates the state, so S7 cannot loop.

**S8 LostBanking.**
Entry: EV6 (oracle-infeasible flip) with `total_carried > 0` at the loss turn; the one
sanctioned deferral: an already-committed banking DROP executes at the flip turn itself,
response begins wood-free at t+1 (SPEC I-10a; I1:645-647). Evaluation: bank-only
(`banana_lost_action`, I1:409-431 — nearest-door (distance, cell) minimum).
Interventions: CH1 = Some (held ONLY for the leftover cargo); CH2 = Some(latched lost
cell) while the lost plant lives; CH3 = MOVE-to-door/DROP; CH4 (incl. count-based
`reserved_banana` PICK veto per F6/R5 — B.4); CH5. Exits: T8a cargo = 0 (DROP landed or cargo lost) →
S9 immediately, same turn (I1:1038-1043); T8b EV9 → S9 (worker gone; claim persists);
T8c EV16 lost plant died → claim lapses, state remains until T8a; **T8d EV20 no door
BFS-reachable while cargo > 0 → I-19 terminator: the worker is handed back to the inner
economy (CH1 = None) carrying its cargo, ownership explicitly transfers to the inner policy
(the wrapper discards neither the cargo nor the worker), and the lost-cell claim persists
under EV16; state becomes S9** (R6: no silent cargo discard, no loop). Liveness:
I-19/I-20/I-21 verbatim on the leftover cargo — strict door progress, DROP within
`door_dist(loss) + 2`; if that horizon is unreachable, T8d fires (bounded), so S8 cannot
loop.

**S9 LostReleased.**
Entry: T8a; or EV6 with nothing carried (released at the flip turn itself, SPEC Rev
2026-08-06). Evaluation: claim maintenance only. Interventions: CH2 = Some(latched lost
cell) while that plant lives, then None (EV16); CH4 (mother vetoes and the count-based
`reserved_banana` PICK veto while the claim is live — both FINITE, lapsing at EV16, F6/R5); CH1 =
None; no CH3/CH5. S9 is inner-controlled passthrough EXCEPT the finite CH2/CH4 claim; it is
therefore NOT byte-equal to the parent while the claim lives (R5: do not call it structural
identity where a channel still writes). Exits: none (absorbing; `banana_lost` latched blocks
re-activation). Liveness: none for the wrapper; the finite non-interference obligations of
§B are the state's whole contract.

**S10 AbandonedBenign.**
Entry: T2a deadline; EV9 resident death; EV17 completion/impossibility. Evaluation:
none. Interventions: none; CH1/CH2 None; structural identity (I1:1067-1071). Exits: none
(absorbing). Liveness: none; byte-equality with inner output.

### A.3 Event classes

| ev | definition (deterministic predicate on `S_t` + FSM state) |
|---|---|
| EV1 | arbitration decision (orchard-eligible / not), turn 1 only (SPEC I-28) |
| EV2 | activation predicate: `\|own\| >= 2` ∧ starter-on-ring ∧ seed source (I-16 + checkpoint) |
| EV3 | activation deadline `turn > 100` (I-1) |
| EV4 | ownership flip (`eta_res >= eta_opp_h`, ties conceded, I-7) ∧ ripe fruit harvestable immediately |
| EV5 | ownership flip ∧ ¬EV4 ∧ ORACLE feasible |
| EV6 | ownership flip ∧ ¬EV4 ∧ ORACLE infeasible |
| EV7 | asset-under-attack, **ownership-INDEPENDENT (F2)**: our live latched mother is chop-threatened before we would next act on it — `opp_destroy_turn < T_service` (ASSET_SURVIVAL_ORACLE, A.7), where `T_service` is our next-service turn on the mother (A.7, defined exactly from oracle outputs, F2/R2.4). Fires whether or not an ownership flip co-occurs; the `S_{t-1}->S_t` health-drop is telemetry-only corroboration, not a separate trigger (design-new; R6 family d2, revised R2/F2) |
| EV8 | mother destroyed (own final chop, opponent chop, any cause) |
| EV9 | resident died (`view.unit(id)` = None) |
| EV10 | wood acquired with full capacity → forced Bank commitment (I-21) |
| EV11 | cargo banked / cargo lost (commitment terminator, I-19) |
| EV12 | target invalidated: destroyed / completed / planted-over / occupied by working peer / unreachable (SPEC §e clause 1) |
| EV13 | blocked 2 consecutive turns, bounce-inclusive: BFS distance to held target did not drop below the best achieved (F-B3) |
| EV14 | 3rd consecutive Idle choice (F-D2) |
| EV15 | lifecycle-productive candidate (ring Chop/Harvest/Plant/Boot) exists after a release |
| EV16 | lost/latched plant died (claim lapse) |
| EV17 | feature complete/impossible: nothing carried ∧ no live ring banana ∧ no usable banked seed |
| EV18 | I-5 late cutoff reached for a cell (guard: Plant candidates vanish) |
| EV19 | committed conversion infeasible (S7): re-run of ASSET_SURVIVAL_ORACLE from `S_t` shows the latched conversion can no longer complete before `asset_lost_turn` due to a PATH/target loss (unreachable mother, cell occupied by a working peer) — NOT a mere opponent arrival on an already-won race (R5/R6 review §R6) |
| EV20 | committed bank route unusable (S3(Bank) **and** S8 — F7): no legal, **dynamically conflict-resolved** landing sequence to any door exists for a bounded no-progress horizon while cargo > 0. Extends the old static-BFS test: a door BFS-reachable but with every usable landing occupied/reserved by own workers (the coordination-injury class) triggers EV20. Pre-action predicate on `S_t` incl. own-unit occupancy (I-19 terminator generalized; review §R6/F7) |

Environment conditions (not events — they parameterize guards and channel obligations):
ownership-flip sub-classification ripe/unripe × feasible/infeasible is EV4/EV5/EV6;
"second worker not yet trained" is the dwell condition of S2 (¬EV2);
"orchard-eligible map" is EV1; choke/articulation geometry and single-door contention are
geometry parameters of the N1/N3 obligations and the C8/I-22 serialization guard
(resident first, then ascending id — SPEC rev 2026-08-04 item 8), exercised by the D.2
grid, not distinct transitions.

### A.4 Transition table (state × event)

Codes: `T-x` = transition defined in A.2; `∅` = no-op self-loop by definition (state's
per-turn function ignores the event; justification in A.5); `U` = unreachable in that
state (argument in A.5). Passthrough to the inner policy is NEVER implicit: it is exactly
the states whose CH1 = None (S1, S2, S5, S9, S10 and the non-resident units always), each
reached by a named transition. **F2: there is no S6 row.** T3a/T4c/T5b (the EV4 columns of
S3/S4/S5) are Mealy `HARVEST` OUTPUT self-edges — they emit HARVEST and leave the persisted
state unchanged; they never target a distinct state.

| state \ ev | EV1 | EV2 | EV3 | EV4 | EV5 | EV6 | EV7 | EV8 | EV9 | EV10 | EV11 | EV12 | EV13 | EV14 | EV15 | EV16 | EV17 | EV18 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S0 | T0a/T0b | U1 | U1 | U1 | U1 | U1 | U1 | U1 | U1 | U1 | U1 | U1 | U1 | U1 | U1 | U1 | U1 | U1 |
| S1 | U2 | ∅3 | ∅3 | ∅3 | ∅3 | ∅3 | ∅3 | ∅3 | ∅3 | ∅3 | ∅3 | ∅3 | ∅3 | ∅3 | ∅3 | ∅3 | ∅3 | ∅3 |
| S2 | U2 | T2b | T2a | U4 | U4 | U4 | U4 | U4 | ∅5 | ∅5 | ∅5 | U4 | U4 | U4 | U4 | U4 | U4 | ∅5 |
| S3 | U2 | ∅6 | ∅7 | T3a | T3b | T3c | T3d | T3g | T3e | T3g→Bank | T3g | T3g | T3h | U8 | ∅6 | U9 | T3f | guard |
| S4 | U2 | ∅6 | ∅7 | T4c | T4d | T4e | T3d | T3g | T4e' (=T3e) | T4b→Bank | ∅10 | T3g | ∅10 | T4a | T4b | U9 | T4f | guard |
| S5 | U2 | ∅6 | ∅7 | T5b | T5c | T5d | T3d | ∅11 | T5e | ∅12 | ∅12 | ∅11 | ∅12 | ∅13 | T5a | U9 | T5f | guard |
| S7 | U2 | ∅6 | ∅7 | ∅17 | ∅17 | ∅17 | ∅17 | T7a | T7b | U18 | ∅18 | T7a | ∅19 | U8 | ∅6 | U9 | via T7a | ∅7 |
| S8 | U2 | ∅6 | ∅7 | ∅20 | ∅20 | ∅20 | ∅20 | T8c | T8b | U21 | T8a | ∅22 | liveness | U8 | ∅23 | T8c | via T8a | ∅7 |
| S9 | U2 | ∅6 | ∅7 | ∅20 | ∅20 | ∅20 | ∅20 | T16' | ∅24 | ∅12 | ∅12 | ∅12 | ∅12 | ∅12 | ∅23 | EV16→claim None | ∅24 | ∅7 |
| S10 | U2 | ∅25 | ∅25 | ∅25 | ∅25 | ∅25 | ∅25 | ∅25 | ∅25 | ∅25 | ∅25 | ∅25 | ∅25 | ∅25 | ∅25 | ∅25 | ∅25 | ∅25 |

**A.4a — impossible-commitment columns EV19, EV20 (R6; scope extended by F7).** These
events are live in every state that holds the corresponding commitment. **F7 extends EV20
from S8-only to EVERY bank commitment state (S3(Bank) as well as S8)** and from static BFS
to DYNAMIC conflict-resolved reachability (occupied/reserved landings count as blocked):

| state | EV19 (conversion impossible) | EV20 (bank route unusable — dynamic) |
|---|---|---|
| S3(Bank) | U (no conversion latch) | T3i → blocked-hold then, if the bounded no-progress horizon elapses with no usable conflict-resolved door route, hand the carrier back to inner (CH1=None), cargo kept |
| S3(non-Bank) | U | U (no bank commitment) |
| S7 | T7c → S8(cargo>0)/S9 | U (no bank commitment in S7) |
| S8 | U (no conversion latch in S8) | T8d → S9 (worker to inner, cargo kept) |
| all other states | U | U |

EV20 now fires whenever **no legal, conflict-resolved bank landing sequence to any door
exists for a bounded no-progress horizon** — a door statically BFS-reachable but with every
usable landing occupied/reserved by own workers (the DEF-09/DEF-12 injury class) triggers
the exit instead of looping. With EV19/EV20 every commitment state (S3(Bank), S7, S8) has a
production exit for success, invalidation, death, AND infeasibility — the §R6/F7 obligation.
Debug-build panics on "impossible commitment with no transition" are therefore unreachable.

### A.5 Completeness argument

1. **Rows are exhaustive**: A.1's 10 PERSISTED states (F2: HarvestNow is an EV4 output, not
   a persisted state, so it is not a row) partition the wrapper's reachable configuration
   space — `banana_enabled ∈ {None, false, true}` × `phase` ×
   `{banana_lost, banana_lost_banking, idle_streak >= 3, target == (Chop, mother)}` — and
   every combination not named is excluded by construction (e.g. `banana_lost` with phase
   ≠ Abandoned is unreachable: the loss transition sets both, I1:737-738; the
   contract-harness assertion A-1 checks the exclusion at runtime).
2. **Columns are exhaustive over the rejection history**: EV1-EV20 cover every event any
   diagnosis or ACK exposed — ownership flip in all four ripe×feasible quadrants
   (EV4/5/6; ACK2 item 2, ACK3 item 2), mother destroyed (EV8), worker died (EV9,
   SEAM R5), opponent adjacent as both harvester-camp (inside EV4-6 via I-7) and
   chopper-attack (EV7 via ASSET_SURVIVAL_ORACLE; R6 d2), second worker not trained (¬EV2
   dwell; ACK gate D-9), orchard-eligible map (EV1), choke/articulation and single-door
   geometry (environment parameters of N1/N3 + C8 serialization; R5, R6 b1/b2), starvation
   (EV14; R6 d), bounce-blocked (EV13; R6 b2), and impossible commitments (EV19/EV20;
   review §R6). Co-occurrence is resolved by the A.6 total priority order.
3. **Every cell is filled**: each (state × event) pair is a `T-x` (defined in A.2), a `∅`
   (self-loop: the state's per-turn function is total and the event does not change the
   guard outcome — footnotes below), or a `U` (unreachable — footnotes below). A total
   per-turn function + a filled table = no implicit behavior.
4. **No implicit fallthrough**: the candidate list always contains WAIT (I-25;
   I1:440), so the resident decision is total in every CH1=Some state; passthrough
   states are exactly the CH1=None states, each entered by a named transition, and in
   them the wrapper's output is the identity (S1/S2/S10) or identity-except-CH2/CH4
   (S5/S9) — asserted per turn by A-2/A-3.
5. Footnotes: U1 sub-turn state (S0 resolves before any other evaluation). U2 arbitration
   fires once (guard `banana_enabled == None`). ∅3 S1 ignores everything (structural
   identity is its contract). U4 no mother/target/reservation exists in S2. ∅5 events on
   inner-owned units don't touch the dormant wrapper. ∅6 already active / already
   satisfied. ∅7 deadline and cutoff only guard planting/activation; active states
   continue (I-5 is a plant guard, not a kill switch). U8 states with a non-Idle forced
   action can't accumulate an Idle streak. U9 EV16 concerns the *lost* plant; pre-loss
   mother death is EV8. ∅10 Idle has no cargo commitment / no held route (idle-yield
   aside is not a commitment). ∅11 released resident has no wrapper target. ∅12
   inner-owned concern. ∅13 streak already ≥ 3; release persists. (∅14/U15/U16 are VOID
   under F2 — there is no S6 row; EV4's HARVEST is an output self-edge of S3/S4/S5, and when
   EV4 co-occurs with EV7 the A.6 priority order (EV4 rank 6 > EV7 rank 9) makes harvest-now
   dominate in-state, no separate cell needed.) ∅17 latch: the convert decision
   is not re-opened (SPEC I-10a "decided once"; ACK2 item 2). U18/∅18 conversion runs
   cargo-free until wood lands from the final chop; the wood from completion enters via
   T7a → S3(Bank). ∅19 the latch holds through blocks; the mother cannot be occupied by
   a peer (CH2/CH4) and the resident has priority (CH5), so a block is ≤1 turn transient.
   ∅20 already lost; flip predicates are latched (I-7 "latched once lost", SPEC D-8).
   U21 `banana_lost_action` never acquires cargo (bank verbs only). ∅22 the door target
   set can't invalidate (doors are static; occupied-door handling is a per-turn re-pick
   inside `banana_lost_action`). ∅23 `banana_lost` blocks re-activation permanently. ∅24
   S9 is absorbing; worker death changes nothing the wrapper still does. T16' in S9: EV8
   on the latched plant IS EV16. ∅25 S10 absorbing identity.

### A.6 Concurrent-event priority (total order) — R1 (review §R1)

EV1-EV20 are predicates that can be simultaneously true on one `S_t`. Filling A.4 does not
by itself define behavior when two columns are true. This section closes that.

**Observation source / phase (F1 — which phase each predicate is read in; an event is
consumed only in or after the phase that can produce it):**

| source / phase | events |
|---|---|
| PHASE-1 pre-action `S_t` (view + latched fields, before delegation) | EV1, EV2, EV3, EV4, EV5, EV6, EV7, EV12, EV13, EV14, EV15, EV17, EV18, EV19, **EV20 (F7: dynamic reachability on `S_t`, incl. own-unit occupancy)** |
| PHASE-1 inferred `S_{t-1}->S_t` (fact that landed since last turn) | EV8, EV9, EV11, EV16 |
| PHASE-4 command-produced at `t` (result of the command we/inner emit this turn) | **EV10** (consumed in PHASE-5, never earlier — review R1.1) |

**Total priority order (rank 1 = highest; the PHASE-5 selector (F1) picks the highest-ranked
event — over ALL events including PHASE-4 command-produced EV10 — whose transition is live,
not `∅`/`U`, in the current state's A.4 row):**

| rank | event | class | why it dominates |
|---|---|---|---|
| 1 | EV9 resident died | roster terminality | a dead slot cannot act; nothing below is meaningful |
| 2 | EV8 tracked mother destroyed | asset terminality | commitment termination precedes any new commitment (I-10a "decided once") |
| 3 | EV16 lost plant died | asset terminality | closes the claim/veto before re-entry logic runs |
| 4 | EV17 feature complete/impossible | lifecycle terminality | absorbing → S10 |
| 5 | EV3 activation deadline | lifecycle terminality | past deadline never activates |
| 6 | EV4 flip ∧ ripe-on-cell | immediate value securing | grab realized value now (dominates speculative convert) |
| 7 | EV19 commitment infeasible (S7 path/deadline lost) | loss-response | abandon a provably-dead conversion before persisting it |
| 8 | EV20 bank route unreachable (S8) | loss-response | terminate an impossible bank without discarding cargo silently |
| 9 | EV7 asset-under-attack | loss-response | a loss event dominates opportunity; feeds the A.7 oracle jointly with any flip |
| 10 | EV6 flip, oracle-infeasible | loss securing | secure carried value / abandon (dominates convert) |
| 11 | EV5 flip, oracle-feasible | opportunity | convert only when nothing above fired |
| 12 | EV11 cargo banked/lost | commitment terminator | ends a bank commitment before EV10 opens a new one |
| 13 | EV10 full cargo → forced Bank | new commitment | after any terminator |
| 14 | EV12 target invalidated | replan | a blocked path to an invalid target is moot |
| 15 | EV13 blocked-2 threshold | replan | recompute after invalidation is handled |
| 16 | EV15 productive re-entry | release exit | re-employ before deciding to release |
| 17 | EV14 3rd idle → release | release | lowest active opportunity event |
| 18 | EV2 activation predicate | dormant→active | only when no terminal/deadline event fired |
| 19 | EV18 late-cutoff plant guard | guard (no transition) | vanishes Plant candidates only |
| 20 | EV1 arbitration (turn-1 only) | S0-exclusive | S0 resolves before any other event is reachable (U1 row) |

Justification: ranks 1-5 are loss/terminality facts (roster, asset, lifecycle); ranks
6-13 are value-securing and commitment events, with immediate securing (EV4) above threat
response (EV7-EV10) above speculative conversion (EV5) — exactly the review's "immediate
value securing dominates speculative conversion" and "commitment termination precedes a new
commitment". Ranks 14-20 are replan/opportunity/setup. Loss and liveness always dominate
opportunity.

PHASE-5 selects one **state transition**. Terminal asset/roster facts additionally drive
channel closure in the SAME atomic turn: EV8/EV16/EV9 null the latched CH2/CH1 regardless of
the selected transition (A-1/A-6 enforce it), so no channel outlives the fact that voids it.

**Worked collision resolutions (the review's listed cases + the S8 case):**

- **C1 EV9 + EV8 + EV17** (resident dies as our final chop kills the mother on a completing
  feature): rank 1 EV9 selected → S10 (T3e/T7b). Mother-destroyed and completion are moot
  once the slot is gone.
- **C2 flip (EV5/EV6) + EV7 attack** (EV7 is ownership-independent, F2, so it legitimately
  co-occurs with a flip): if EV4 also holds (ripe on-cell) rank 6 wins → emit `HARVEST`
  output, state unchanged (F2: no S6). Else rank 9 EV7 selected → T3d, resolved by
  ASSET_SURVIVAL_ORACLE (A.7) computed with BOTH threats: `asset_lost_turn =
  min(opp_harvest_turn, opp_destroy_turn)`. The earlier of harvest-out and chop-out sets the
  deadline; convert (S7) iff `completion_turn < asset_lost_turn` strictly, else S8/S9.
- **C3 EV8 + EV10** (our final chop both kills the mother and yields the wood that fills the
  carrier): rank 2 EV8 selected → T7a; the acquired wood is banked via the resulting
  S3(Bank). EV10's forced-bank is subsumed (footnote ∅18).
- **C4 EV11 + EV16** (the leftover DROP lands the same turn the lost plant dies): rank 3
  EV16 selected as the transition → T8c, claim lapses to `None` this turn; the DROP still
  executes (S8 CH3), cargo→0, and T8a fires next turn to S9. Claim closed immediately,
  cargo banked without loss.
- **C5 EV2 + EV3** (activation predicate true on the deadline turn): rank 5 EV3 selected →
  S10. Never activate past the deadline.
- **C6 EV12 + EV13** (held target invalidates on the turn the block counter trips): rank 14
  EV12 selected → T3g recompute; the blocked path to an already-invalid target is discarded.

Compound-event fixtures C1-C6 are mandatory manifest configurations (§D.2, L-FIX); none is
a prose-only cell.

### A.7 ASSET_SURVIVAL_ORACLE (named oracle) — R2 (review §R2)

The single growth-aware, absolute-time oracle that governs EV4-EV7. It **generalizes**
CONVERSION_RACE_ORACLE (which compares our conversion only against opponent HARVEST): it
additionally models opponent CHOP-out with exact travel/growth/action timing. With no
chop-capable opponent it reproduces CONVERSION_RACE_ORACLE byte-for-byte (asserted in
`conversion_race_oracle.py` self-test). It replaces EV7's old threshold `eta_opp_x <= 1 ∨
health-decrease`. Founding is decided by the separate anchored `founding_safety_oracle`
(F4, below). No second deadline expression is permitted anywhere (DEF-04/DEF-07/DEF-14/DEF-17).

Name/impl: `asset_survival_oracle` (+ `founding_safety_oracle`) in `conversion_race_oracle.py`.

Inputs (all from `S_t`, decision turn `t`): walkable set; mother cell `c`; mother plant
state (size, health, fruits, cooldown); near-water flag; resident (cell, speed, chop_power);
every opponent unit as (cell, speed, harvest_power, chop_power) — harvesters AND choppers,
same call.

Outputs (absolute turns anchored at `t`):

- `our_harvest_turn` — earliest turn we can execute a value-securing HARVEST on `c`
  (our arrival ∧ ripeness).
- `completion_turn` — turn our FINAL defensive/conversion chop lands (identical to
  CONVERSION_RACE_ORACLE).
- `opp_harvest_turn` — opponent's earliest executable HARVEST (arrival ∧ ripeness), over
  harvest-capable opponents (farm-out).
- `opp_destroy_turn` — opponent's earliest CHOP-out of the asset, growth-aware, **exact
  reachable single-chopper schedule (F3)**: at most ONE opponent unit can CHOP the tree per
  turn (the referee gates CHOP on standing ON the tree cell, and per-player movement-conflict
  resolution reserves a distinct landing per own unit, so two same-player choppers can never
  co-occupy the cell). Each turn from the earliest arrival, one chop lands applying the
  MAXIMUM chop_power among arrived choppers (best reachable single chopper / hand-off);
  powers are NEVER summed. A second chopper advances destruction only by arriving earlier or
  handing a higher single power — never by simultaneous co-located power. (Prior draft summed
  arrived powers — an unreachable over-count; review R2.1.)
- `asset_lost_turn = min(opp_harvest_turn, opp_destroy_turn)` — absolute turn the asset is
  FIRST destroyed-or-farmed-out.
- `feasible_convert = completion_turn < asset_lost_turn` (STRICT) — drives EV5/EV6/EV7.

`T_service` (F2/R2.4 — EV7's deadline, defined EXACTLY from oracle outputs, no undeclared
term): the absolute turn the resident's CURRENT commitment next acts on the mother cell —
`completion_turn` if already committed to a defensive CHOP on it, `our_harvest_turn` if
committed to HARVEST it, else `t + eta_res` (arrival if it re-targeted the mother now). All
four are oracle outputs; there is no free-floating "next service turn".

Semantics: EV4-EV6 are a mutually exclusive classification of a FLIP; EV7 is an
ownership-INDEPENDENT threat that may co-occur with any of them (F2). Evaluated in PHASE-2
every active turn:

- EV4 = flip ∧ ripe fruit harvestable on-cell this turn (`our_harvest_turn == t`) → `HARVEST`
  output (F2: no S6).
- EV5 = flip ∧ ¬EV4 ∧ `feasible_convert`.
- EV6 = flip ∧ ¬EV4 ∧ ¬`feasible_convert`.
- EV7 = (we own a live latched mother) ∧ `opp_destroy_turn < T_service` — the asset is
  chop-threatened before we would next act on it, **regardless of ownership flip**. Routes
  to the convert/abandon classification via `feasible_convert`. When EV7 co-occurs with a
  flip, the A.6 priority order resolves which fires (EV4 ripe-on-cell > EV7 > EV5).

**Strict tie (referee ruling):** `completion_turn == asset_lost_turn` is CONTESTED and
conceded to the opponent (feasible_convert False), consistent with I-7 /
CONVERSION_RACE_ORACLE.

**Strict-tie fixtures (the boundary cases the D.2 grid MUST contain; ST1-ST7 are ALL now
asserted in the oracle self-test — F8):**

- ST1 harvest tie: `completion_turn == opp_harvest_turn` (legacy r3a) → infeasible.
- ST2 harvest feasible-by-one: `completion_turn == opp_harvest_turn - 1` (r3b) → feasible.
- ST3 chop tie: a single chopper's kill turn `== completion_turn` → infeasible (conceded).
- ST4 chop feasible-by-one: chopper kill `== completion_turn + 1` → feasible.
- ST5 earlier-arriving chopper advance (F3-corrected): a lone far chopper leaves the race
  feasible; adding an EARLIER-arriving chopper moves the first-arrival turn earlier so
  destruction lands on the completion tie → infeasible. The advance is from earlier ARRIVAL,
  never summed power (the self-test also asserts two co-arriving choppers give the SAME
  destroy turn as one — the no-summation invariant).
- ST6 min(harvest,destroy): one unit that both harvests and chops; classification uses the
  earlier of the two (a late farm-out must not mask an early kill).
- ST7 growth-crossing: a low-size mother regrows between chops, so the growth-aware
  `opp_destroy_turn` (5 chops for size-2/health-4/cd-1/chop-1) is NOT the static
  `ceil(health/chop)` proxy (4) — the banned static proxy is provably wrong
  (DEF-04/DEF-17).

**FOUNDING SAFETY (F4/R2.2/R2.3) — `founding_safety_oracle`, the post-PLANT-anchored founding
guard.** The S3 founding guard is NOT `asset_survival_oracle` and is NOT arrival-order. The
prior `feasible_found = eta_res < eta_opp_h ∧ our_harvest_turn < opp_destroy_turn` was unsafe
(review R2.3): arriving first does not reserve the fruit cell, cross-player co-location is
legal, and a SIMULTANEOUS last-fruit HARVEST duplicates one banana to BOTH players. Founding
is now decided by exact executable-HARVEST safety on a frozen referee transition:

- **Post-PLANT time anchor (frozen, R2.2).** At decision turn `t` the resident is on the ring
  cell and emits `PLANT BANANA`. PLANT resolves during turn `t`'s action phase; the sapling
  is created on that cell and receives the creation-turn growth tick, so it FIRST exists in
  `S_{t+1}`. The oracle is anchored at `t+1`. Its `sapling` input is the referee's actual
  post-tick fresh-plant descriptor (size, health, fruits, cooldown) as it exists at `t+1` —
  no pre-tick or hypothetical proxy. The resident is ON the cell at `t+1`, so our harvest ETA
  is 0 and `our_harvest_turn` is pure ripeness.
- **Exact safety predicate.** `feasible_found = our_harvest_turn < opp_harvest_turn` (STRICT)
  `∧ our_harvest_turn < opp_destroy_turn` (STRICT), all in the `t+1` frame. Both harvest
  turns are exact EXECUTABLE HARVESTs (arrival AND ripeness on the same fruit cell) over the
  post-PLANT growth timeline; `opp_destroy_turn` uses the F3 single-chopper model. STRICT is
  load-bearing: an equal executable-harvest turn is the last-fruit-duplication case and is
  UNSAFE (conceded), not a win. The self-test witnesses all three outcomes: safe (opponent
  reaches the cell only after ripeness), unsafe-by-harvest-tie (opponent arrives before
  ripeness → shared ripeness turn → duplication), unsafe-by-chop-out.

A-17 (plant geometry) now checks `founding_safety_oracle.feasible_found` at plant time, on
the post-PLANT anchor, not the arrival-ETA proxy.

---

## B. Interference contracts (six channels)

Master invariant **CI-0 (state-purity)**: on every turn, each channel's value/action is a
pure function of (FSM state, latched data, `S_t`) as tabulated below — never of incidental
history. This kills the stale-reservation class by construction: a channel cannot hold a
value its current state does not license.

### B.1 CH1 — reservation `banana_idle_unit` (SEAM I2/I3/I4)

1. WRITER states and legal values: `Some(resident_id)` in S3, S4, S7, S8 (and for the one
   EV4 HARVEST-output turn, which is an S3/S4 turn — F2, no S6); `None` in S0, S1, S2, S5,
   S9, S10. Written every enabled turn before delegation
   (SEAM R1); no other writer exists (`external_idle_unit` is the orchard's, never
   shared — SEAM R1).
2. Inner touchpoints: YamoBot inserts `WAIT` for the reserved id (SEAM I4), removing the
   unit from inner planning; its cell becomes a *stationary obstacle* in every
   conflict-resolution pass.
3. NON-INTERFERENCE obligations:
   - **N1 (carrier-progress) — ENFORCED ARBITRATION RULE (R4, review §R4).** N1 is a
     production decision rule, not merely an assertion. Unconditional resident priority is
     REPLACED by the carrier-yield rule below; A-4 becomes the post-hoc check that the rule
     held. The rule is evaluated in PHASE-2 (F1), jointly over CH1+CH2+CH3+CH5 (not per channel):

     **Scope (F5/R4.1): every COMMITTED wood carrier, not just full ones.** The protected
     set is every own unit `u` with `carry[WOOD] > 0` that is committed to bank carried wood
     (the owner-contract commitment, per SPEC §e / I-19 — a capacity-2 unit carrying one
     wood on a bank commitment is protected exactly like a full carrier). `free_capacity==0`
     is NOT the predicate; bank-commitment ∧ positive wood cargo is.

     **Exact landing set (F5/R4.2): speed-aware, same semantics as CH5.** `P(u)` = the legal
     landing cells that strictly reduce `door_dist(u)`, computed with `u`'s ACTUAL movement
     speed and the referee's own movement + conflict resolution (`next_cell` over all cells
     reachable within speed, then the per-player reservation pass) — NOT ortho speed-1
     neighbours. `Blocked(u)` = cells of `P(u)` removed by any banana channel effect this
     turn: the reservation/idle cell (CH1, the resident's own cell), the claimed cell (CH2),
     the resident's post-edit landing (CH3), and cells reserved by CH5's priority resolution.
     CH2 is included ONLY as a destination/on-cell verb constraint and never as a MOVE-transit
     block (N2/N4/R4.4): a landing is in `Blocked(u)` via CH2 only if it is the claimed cell
     itself, never because a route merely crosses it.

     Decision (output = which yields): if `P(u) ≠ ∅ ∧ P(u) \ Blocked(u) == ∅` — a banana
     effect removes `u`'s LAST progress landing — then the banana effect YIELDS this turn AND
     the resident must PHYSICALLY VACATE the contested landing, not merely wait (F5/R4.3):
       1. Prefer an **ASIDE move**: the resident steps to a non-forbidden cell (not `u`'s
          progress landing, not the claimed cell) that preserves door reachability for `u`
          and every nearby carrier — i.e. after the aside, `P(u) \ Blocked(u) ≠ ∅`. The aside
          target is the `(dist, cell)`-minimal such cell (deterministic). This is the S4
          idle-yield aside generalized; CH5 does not reserve the vacated cell.
       2. WAIT is used ONLY when it already frees `u`'s landing (the resident was not standing
          on `u`'s sole progress landing). WAIT that leaves the resident on the articulation
          landing is NOT a yield and is never emitted as the yield action (R4.3).
       3. If no legal aside exists that keeps every nearby carrier's door reachable, the FSM
          enters the bounded blocked-hold path and, if the no-progress horizon elapses, the
          carrier takes the EV20 production exit (F7: hand-off to inner, cargo kept) — the
          route is released by a real state transition, never an assertion panic.
     Otherwise (`u` retains another progress landing) the resident keeps priority.

     **Conversion-deadline reconciliation (F5/R2.5).** A yield can cost the resident one
     travel turn. The priority contract is explicit: **the carrier owner-contract (N1)
     outranks a speculative conversion.** Therefore the conversion feasibility test
     (`asset_survival_oracle.feasible_convert`, EV5) must be evaluated with the
     ALREADY-KNOWN yield delay folded into `completion_turn`: if a pending carrier yield
     this turn will delay the resident, S7 entry uses the delayed completion turn, so a race
     that a yield turns into a tie is classified infeasible UP FRONT (EV6, secure/abandon)
     rather than entered and then missed. A conversion that cannot survive the mandatory
     yield is never latched; EV19 re-runs remain the safety net, but the original
     `completion_turn` is not claimed exact while a yield is owed (this closes R2.5).

     This makes N1 TRUE by construction (generalizes R5 §H3 and R6 ROOT B: articulation
     cells and occupied-door detours are two geometries of the one violation).
   - **N5 (funding)**: CH1 is None until EV2 — no reservation can displace TRAIN
     (I-17/I-18; D-9).
4. Runtime-assertable contract:
   - A-1: `banana_lost ⇒ phase == Abandoned`; `idle_streak >= 3 ⇒ CH1 == None`;
     `CH1 == Some(w) ⇒ state ∈ {S3,S4,S7,S8} ∧ w == starter_id` (F2: no S6).
   - A-4 (N1 check — verifies the R4/F5 rule held, does not implement it): for every own
     unit `u` COMMITTED to bank with `carry[WOOD]>0` (F5 scope, not `free_capacity==0`):
     `door_dist(u,t) < min door_dist(u,t') over the last 2 turns`, OR a DROP/cargo-loss
     occurred, OR `u` was displaced ≤ 1 turn
     (I-20 tolerance). Violation ⇒ panic. For exact attribution (review §R4/F9), the panic
     witness records `P(u)`, `Blocked(u)`, and the CHANNEL PROVENANCE of each blocked cell —
     which channel (CH1 idle cell / CH2 claimed cell / CH3 landing / CH5 reservation) removed
     it, read directly from the F9 channel records emitted this turn. No counterfactual re-run
     is used (F9: no hidden second evaluation): a stall whose `Blocked(u)` covers `u`'s last
     progress landing AND whose covering cell carries a banana-channel record is a blocking N1
     violation naming that channel; a stall on a diverged state with no banana-channel record
     covering `u`'s landing is an inherited inner-carrier stall, report-tier.
   - A-5: `state ∈ {S5,S9} ⇒` the resident's emitted command equals the inner's
     un-edited command for that slot.

### B.2 CH2 — cell claim `banana_protected_cell` (SEAM I2/I3/I6)

1. WRITER states and legal values: `Some(latched_mother)` in S3/S4/S5/S7 while the
   founded mother lives, and in S8/S9 while the *lost* plant lives (F-C2 persistence,
   SPEC Rev 2026-08-06); `None` everywhere else and after EV16. **Design rule
   (E GAP-2): the claimed cell is LATCHED at founding — the value is the latched cell,
   not a per-turn `min` recomputation** — so the claim can never migrate to a different
   (possibly opponent-planted) diagonal banana.
2. Inner touchpoints: the I6 retain filter removes every inner candidate whose target
   (`Tree/Bank/Cell`) equals the claimed cell — candidate filtering only, before
   selection (SEAM I6).
3. NON-INTERFERENCE obligations:
   - **N2 (transit-neutrality)**: the claim must never veto movement/transit — it binds
     destination selection and on-cell verbs only. A movement-level veto cannot
     distinguish transit from destination after landing-rewrite and livelocks carriers
     whose every door route crosses the cell (R5 §H3; ratified in I1:1119-1138).
   - **N3 (door-disjointness)**: the claimed cell is diagonal, doors are orthogonal —
     the claim can never remove a Bank candidate (R5 §H1). Geometric lemma, asserted.
   - N1 applies (a claim plus a camped unit jointly blockade — R5 v2 geometry: the fix
     must hold for the conjunction, not each conjunct).
4. Runtime-assertable contract:
   - A-6: `CH2 == Some(c) ⇒` (state licenses a claim) ∧ `c == latched_cell` ∧ a live
     banana stands on `c` ∧ `c ∈ diag(tent)` (hence `c ∉ doors`, N3).
   - A-7: `CH2 == Some(c) ⇒` no own unit's *selected* target equals `c` except the
     resident in the EV4-HARVEST output turn or S7 — i.e. claim ⇒ no own CHOP/HARVEST candidate survives on the
     claimed cell for any inner-controlled unit (the filter worked); a CH4 veto firing
     (B.4) is evidence this assertion's upstream failed and is itself logged.
   - A-8: dormant/disabled turns: `CH1 == None ∧ CH2 == None ∧ output == inner output`
     byte-equal (check 4).

### B.3 CH3 — resident command post-edit via `replace_action` (SEAM A, I1:1083-1087)

1. WRITER states: S3, S4, S7, S8 — exactly the CH1=Some states; at most ONE rewrite
   per turn, targeting only the resident's slot. Legal values per state: S3(task) — the
   verb of the committed task (`MOVE/CHOP/HARVEST/PLANT/PICK/DROP/WAIT` per task); S4 —
   `WAIT` or the idle-yield/carrier-yield ASIDE `MOVE`; the EV4 HARVEST output (F2, an S3/S4
   turn) — `HARVEST`; S7 — `MOVE`-to-mother or `CHOP`; S8 — `MOVE`-to-door or `DROP`.
2. Inner touchpoints: replaces the inner's planned command for the reserved slot; the
   `push` fallback of `replace_action` (SEAM R5) must be unreachable — guarded by the
   EV9 transition (dead resident ⇒ no rewrite).
3. NON-INTERFERENCE: CH3 touches no non-resident slot, ever (the factory's wholesale
   role rewrite is the negative example — SPEC §0, `banana_factory_trained_role_rewrites`).
4. Runtime-assertable contract:
   - A-9: per turn, `#(slots changed by CH3) <= 1` and the changed slot is the
     resident's; the written verb ∈ V(state) as listed in B.3.1.
   - A-10: `state ∈ {S8}` ⇒ written verb ∈ {MOVE-to-door, DROP} (I-19 verb restriction);
     `state == S7` ⇒ verb ∈ {MOVE-to-mother, CHOP} and target cell == latched mother.

### B.4 CH4 — non-resident veto post-edit (I1:1089-1118)

1. WRITER states: any state with CH2 = Some (mother veto), plus S3-S9 for the banana-PICK
   exclusivity veto. Legal action: substitute `WAIT` — never any other verb — and only for:
   (a) `CHOP`/`HARVEST` by a unit standing ON the claimed cell;
   (b) `PICK … BANANA` at the bank, **COUNT-SCOPED (F6/R5): the referee bank stores one
   fungible per-species BANANA count (`Stock[BANANA]`, not lots) — a PICK names only the
   species, never an individual fruit or its lineage, so a "latched-lineage PICK" is
   UNOBSERVABLE.** The veto is therefore respecified over observable counts, not provenance:
   the feature persists a `reserved_banana` count (the number of banked bananas it must
   retain — exactly 1 while a bootstrap seed is owed and the claim is live, else 0). CH4
   vetoes an own bank `PICK … BANANA` iff executing it would drop the OWN bank BANANA count
   below `reserved_banana` (`bank[BANANA] - 1 < reserved_banana`). It is FINITE:
   `reserved_banana` drops to 0 at EV16 (the latched plant dies) and the veto lapses.
   Because the test is a pure count threshold, any banana above the reserved count —
   opponent-planted or inner-economy — is freely pickable; nothing lineage-specific is
   claimed. The former "for the rest of the game, every bank `PICK … BANANA`" global veto is
   withdrawn. A truly global replant-suppression policy, if ever wanted, must be a separate
   persistent policy STATE with its own necessity/liveness/parity/value gates (not done here).
2. Inner touchpoints: post-selection command stream; second layer behind the I6 filter.
3. NON-INTERFERENCE:
   - **N4 (move-neutrality)**: CH4 never rewrites a `MOVE` (preserves N2); turning a
     stationary verb into WAIT cannot create a movement conflict, which is why CH5 need
     not re-run after CH4 (I1:1134-1138).
   - The vetoed unit keeps every other candidate next turn (the I6 filter should have
     already steered it; a firing veto is a filter escape).
4. Runtime-assertable contract:
   - A-11: every CH4 substitution this turn matches predicate (a) or (b) of B.4.1;
     count of (a)-firings over a game is expected 0 (each firing logged as a
     filter-escape warning, not a panic).

### B.5 CH5 — conflict re-resolution participation (I1:1139-1145)

1. WRITER states: runs iff CH3 rewrote a command this turn (S3, S4, S7, S8; F2: no S6). Legal
   parameterization: priority set = `{resident}` exactly; forbidden set = **empty,
   always** (the r5 mother-forbidden set is void — R5 §H3, ratified R5 fix).
2. Inner touchpoints: `resolve_move_conflicts_with_priority` re-parses already
   landing-rewritten moves; every stationary own unit's cell is `reserved`; detour
   tie-break is `(dist, cell)`-lexicographic (R6 b mechanism step 3).
3. NON-INTERFERENCE: N1 is the binding obligation, ENFORCED by the R4 carrier-yield rule
   (B.1.3): before CH5 reserves the resident's cell / applies resident priority, the rule
   checks whether that reservation removes a full carrier's last progress landing and, if
   so, drops resident priority for the turn so CH5 cannot manufacture the parity cycle. The
   re-resolution may otherwise displace a carrier at most 1 consecutive turn (I-20
   tolerance); single-door serialization is deterministic (resident first, then ascending
   id — I-22 rev item 8); CH5 never runs on released/dormant turns (the inner's own
   resolution stands).
4. Runtime-assertable contract:
   - A-12a: CH5 invoked ⇔ CH3 rewrote this turn; forbidden-set argument is empty.
   - A-4 (shared with CH1) is the post-hoc detector of any CH5-induced parity cycle.

### B.6 CH6 — arbitration read of orchard eligibility (I1:143-178)

1. WRITER states: none — read-only, by design (SPEC I-28: decision BEFORE first
   delegation, never by post-delegation field inspection). Executed once, in S0.
2. Inner touchpoints: none at runtime; the replica must remain gate-for-gate equivalent
   to `SecureOrchardBot::initialize`'s geometry test (drift here silently flips I-27/I-28).
3. NON-INTERFERENCE: zero dual-attributable commands over the whole game (I-27 evidence
   standard).
4. Runtime-assertable contract:
   - A-13: after the first delegated call, `inner.geometry.is_some() == (banana_enabled
     == Some(false))` — the replica agreed with the incumbent's own decision. Panic on
     mismatch (this is the only legal post-hoc *cross-check*; the decision itself never
     depends on it).

### B.7 Additional cross-channel assertions

- A-0 (Mealy decode, R1): the runtime decode of (persisted fields + `S_t`) to a state is
  single-valued each turn; transient output modes (the EV4 HarvestNow output, blocked-hold,
  idle-yield/carrier-yield aside) are produced within the turn, never decoded from persisted
  fields alone next turn.
- A-12 (oracle-completion): in S7, `current_turn <= committed completion_turn`; the
  mother's final chop lands at `<= completion_turn` (catches any drift between the
  candidate's inline race arithmetic and ASSET_SURVIVAL_ORACLE — the DEF-07 class). The
  committed `completion_turn` already folds in any mandatory carrier-yield delay owed at
  latch time (F5/R2.5), so the "exact completion turn" claim survives a yield; the committed
  deadline is `asset_lost_turn` from A.7; no other deadline expression exists.
- A-14 (D-8 scope): any own chop-class command targeting a live own diagonal banana ⇒
  state == S7 (entered via EV5 or EV7). Discretionary owned-mother chop panics (ACK2 item 2).
- A-15 (one-seed reservation — COUNT-based, F6): the one-seed reservation and surplus
  banking are invariants over the resident's fungible carry COUNT `carry[BANANA]` and its
  per-turn delta, NOT lineage. One-seed reservation: at most 1 banana is retained for
  bootstrap; surplus banking: whenever `carry[BANANA] > 1` the emitted verb ∈
  {MOVE-to-door, DROP} and no Plant candidate is offered, so the surplus (`carry[BANANA]-1`)
  is banked and the per-turn `carry[BANANA]` delta is ≤ 0 until it reaches 1 (I-9; ACK1 1).
- A-16 (bootstrap — COUNT-based, F6): the feature's own bank `PICK … BANANA` count is ≤ 1
  per game, and `reserved_banana ∈ {0,1}` with deposit/consume ordering — a bank DROP
  increments `bank[BANANA]` before any same-turn PICK is evaluated, and `reserved_banana` is
  reconciled on TRAIN (consume for the second worker), PICK (the one bootstrap draw), and
  DROP (surplus deposit). Liveness: `reserved_banana` reaches 0 by EV16 at the latest (I-2).
- A-17 (plant geometry): every own `PLANT BANANA` cell ∈ Ring, count caps per I-12/I-13,
  ASSET_SURVIVAL_ORACLE `feasible_found` held at plant time (R2; D-5/D-6 decision side).
- A-18 (impossible-commitment exit, R6/F7): no turn ends in S7 with the mother unreachable
  and cargo-free, nor in ANY bank commitment (S3(Bank) or S8) with cargo > 0 and no legal
  conflict-resolved landing sequence to any door for the bounded no-progress horizon
  (dynamic reachability, own-unit occupancy included — not static BFS). Such a turn must
  have taken T7c / T3i / T8d. Panic on a stuck commitment (the delivery-build loop is thus
  unreachable).

---

## C. Retrospective validation (acceptance test of this design)

Defect registry: every terminal defect from the five rounds (ACK1-3, R5, R6). Per the
review's ack, this table is now HONEST about the guarantee class, not an overclaim of 17/17
structural coverage. Each defect is classified **IBC** (impossible-by-construction: the
design's structure makes the behavior unrepresentable), **AC** (assertion/infra-caught: a
runtime contract or host gate catches it — verification, not structural prevention), or
**EW** (enumeration-witnessed: the manifest guarantees a config exercises the fix). The
PRIMARY class drives the tally; secondary guarantees are listed in the element column.

| # | defect (citation) | class | design element that kills/catches it |
|---|---|---|---|
| DEF-01 | 2 harvested bananas both replanted before banking (ACK1 1) | IBC | S3 surplus guard suppresses Plant candidates while `carry[BANANA]>1`; +AC A-15 |
| DEF-02 | I-10a unimplemented; no convert/abandon (ACK1 2) | IBC | EV4/5/6 total over the flip quadrants, evaluated every active turn (no `∅`); no-passthrough A.5.4 |
| DEF-03 | No compilable readable research source (ACK1 3) | AC | verification-infra: D.4 host-gate 1 (readable+compact build artifact). Design does not "prevent" it; the gate catches it |
| DEF-04 | Static `ceil(health/chop)` ignored growth (ACK2 1) | IBC | only ASSET_SURVIVAL_ORACLE (A.7, growth-aware) may express a deadline; a static one is forbidden; +AC A-12 |
| DEF-05 | D-8 exemption scope vacuous trace (ACK2 2) | AC | A-14 (own diagonal chop ⇔ S7 via a real EV5/EV7); +EW L-FIX reaches S7 from a candidate-driven plant |
| DEF-06 | Flip response unreachable; scripted t5 masked it (ACK3 1) | IBC | atomic PHASE-2 evaluates EV4-7 before candidates in ALL states (camping cannot hide a flip); +EW EV4-6 fire from S4 in-grid |
| DEF-07 | Three inconsistent conversion deadlines (ACK3 2) | IBC | single-oracle rule: ONE deadline expression (`asset_lost_turn`); F-C1's second proxy deadline is REMOVED by R2; +AC A-12 |
| DEF-08 | R-3 boundary not candidate-reachable (ACK3 3) | EW | honest: closed by an enumeration obligation — ST1/ST2 (and ST3-ST5) are mandatory L-FIX grid points, gate fails if absent |
| DEF-09 | Mother in CH5 forbidden set ⇒225-turn livelock (R5 §H3) | **AC** (F10) | CH5 forbidden set EMPTY always + N2 transit-neutrality + F5 carrier-yield rule; the R4/F5 rule is an ENFORCED runtime decision verified by A-4 + enumeration, not a structural impossibility (review R4 rejected IBC) |
| DEF-10 | forbidden-landing + door-occupancy jointly (R5; R6 ROOT B) | **AC** (F10) | F5 carrier-yield rule over the conjunction (last-progress-landing) + the ASIDE that physically releases + EV20/T3i exit; caught by A-4, not IBC (review R4) |
| DEF-11 | 74 D-9 + inherited D-4/D-6 flagged on byte-identical parent (R6 ROOT A) | AC | verification-infra: NOT structurally prevented — R3 correctly ATTRIBUTES it. Aligned-prefix + channel telemetry (D.1.2/D.1.4) makes inherited parent behavior report-tier |
| DEF-12 | Idle resident camping mother ⇒ parity livelock (R6 b1) | **AC** (F10) | F5 carrier-yield rule + S4 idle-yield ASIDE + EV20/T3i dynamic-route exit; verified by A-4 + L-CORE full-wood on T2/T3, not structurally impossible (review R4) |
| DEF-13 | `banana_bank` occupied doors + bounce-blind counter (R6 b2) | IBC | F-B2 occupied-door filter + EV13 bounce-inclusive; +AC S3(Bank) liveness/A-4 |
| DEF-14 | Instant plant margin farmed every regrowth (R6 ROOT C(i)) | **EW** (F10) | F4 founding guard is `founding_safety_oracle` on the post-PLANT anchor (exact executable-HARVEST safety, ties unsafe) — its correctness rides on the founding/ST fixtures being exercised (L-FIX founding + ST rows), not pure structure (review R2 rejected IBC); +AC A-17 |
| DEF-15 | Inverted claim release; inner reinvested in lost asset (R6 C(ii)) | IBC | CH2 latched persistence in S8/S9 while the lost plant lives + R5 bounded lineage veto; CH1=None in S9; +AC A-6/A-1 |
| DEF-16 | Lost-hold froze the resident to game end (R6 ROOT D, d1) | IBC | S8 T8a immediate on cargo=0, S9 CH1=None, +T8d infeasibility exit; +AC A-1/A-18; +EW EV16/re-entry fixtures |
| DEF-17 | Chopper-blind flip; resident spectated a chopper kill (R6 d2) | **EW** (F10) | choppers are IN the model: F3 single-chopper-per-turn `opp_destroy_turn` + EV7 oracle-driven ownership-independent; correctness rides on the chopper fixtures (L-CORE chopper + ST3/ST4/ST5), so enumeration-witnessed, not pure structure (review R2 rejected IBC) |

Corrected coverage tally (F10 — honest recomputation after F1-F9, reclassifying every defect
whose closure depended on a review-flagged over-claim): **8 impossible-by-construction**
(DEF-01/02/04/06/07/13/15/16), **6 assertion/infra-caught** (DEF-03, DEF-05, DEF-09, DEF-10,
DEF-11, DEF-12), **3 enumeration-witnessed** (DEF-08, DEF-14, DEF-17). Total 17.

Reclassifications vs the prior 13/3/1 (each per the re-review's §C findings):
- **DEF-09/10/12 IBC → AC.** The carrier-yield rule is an ENFORCED runtime decision (F5)
  checked by A-4 and witnessed by L-CORE full-wood rows, not a structural impossibility — the
  review (R4) rejected "impossible by construction" here. Its correctness is verified, not
  guaranteed by representation.
- **DEF-14/17 IBC → EW.** Founding safety (F4) and multi-chopper timing (F3) are now EXACT,
  but their guarantee rides on the founding/ST/chopper fixtures being exercised (review R2
  rejected IBC while these were inexact); they are enumeration-witnessed.
- **DEF-08 EW (now genuine).** The frozen manifest EXISTS as a materialized artifact (F8),
  so DEF-08's boundary is witnessed by real L-FIX rows, not a future promise.
- **DEF-06 stays IBC** — its "flip response reachable in every active state" claim no longer
  depends on the contradictory S6/EV7 model (F2 folded S6 to an output and made EV7
  ownership-independent), so the structural claim is now sound.
- DEF-11 stays AC (parent behavior is real; F9 channel-record attribution makes it
  report-tier), DEF-03/05 stay AC (build-artifact / assertion obligations).

---

## D. Verification plan (maturity pyramid, bottom-up)

### D.1 Contract harness (foundation)

1. A probe build (family probe pattern — SEAM R8's activation probe) compiled with a
   `banana_contracts` cfg: after step 9 of every turn, evaluate assertions A-0 … A-18
   against (FSM state, channel values, `S_t`, emitted commands, channel-touch telemetry,
   and the paired parent stream on the aligned prefix only — R3). Violation ⇒ `eprintln!`
   full witness (turn, state, channel values, both command streams) then `panic!`.
2. **Attribution rule (R3, review §R3) — aligned prefix ONLY, then channel telemetry.**
   Parent-command divergence certifies banana-attribution **only up to the first turn where
   the candidate and stable-parent command streams differ** (the aligned prefix). Both
   executions are closed-loop; once they diverge they are DIFFERENT games and per-turn
   command comparison is invalid (a later difference can be a downstream state consequence,
   and an equality can hide an active channel that happened to pick the same verb). So:
   - **On the aligned prefix** (including the pre-TRAIN funding phase and the TRAIN turn):
     the D-9 direct contract — (i) all six channels inert before EV2/second-worker
     existence, (ii) wrapper output == its own unedited inner output on that exact input,
     (iii) candidate == stable parent byte-for-byte incl. the stats tuple. The FIRST
     pre-TRAIN divergence is a D-9 FAILURE and ends the aligned-prefix proof.
   - **After the first divergence**: a command is banana-attributable iff the channel-touch
     telemetry (D.1.4) names it — CH1..CH5 explicitly recording which channel edited which
     worker's command that turn. Raw command-vs-parent comparison is no longer used. A
     teacher-forced shadow parent on the candidate's states may be logged diagnostically but
     is NOT a causal label.
   - Rewording (R3): "structural identity" in A-2/A-3/A-5/A-8 after a divergent history means
     "no wrapper edit to the CURRENT inner result" (the telemetry shows zero channel touches
     that turn) — NOT byte-equality to a separately evolved parent game. A-8's byte-equality
     is asserted only on the aligned prefix / dormant turns.
3. Contracts are compiled OUT of the delivery build (cfg-gated; delivery stderr must stay
   empty — SEAM R2/R8). The probe build's bytes are never the submission bytes.
4. **Channel-record telemetry (R3/F9) — side-effect-free, all six channels incl.
   pre-delegation ones.** After the first parent divergence, attribution is defined ONLY by
   per-channel records emitted INSIDE the single forward evaluation of the turn — never by a
   re-run, a shadow parent, or a hidden second advance of state/RNG. The prior schema logged
   only post-edited/vetoed slots (CH3/CH4/CH5); but CH1 removes the resident and injects a
   stationary obstacle, and CH2 filters candidates, BEFORE any command exists — they can
   change another worker's selected command with no post-edit (review R3). F9 gives every
   channel an explicit record captured at the exact point it acts:

   Record format (one per channel effect):
   `{turn, channel ∈ {CH1,CH2,CH3,CH4,CH5,CH6}, fsm_state, target_worker (unit_id),
     effect, pre_verb, post_verb, cell}` where
   - CH1: `effect="reserve_idle"` — emitted when CH1 inserts WAIT for the reserved unit and
     marks its cell a stationary obstacle; `target_worker` = the reserved id, `cell` = its
     cell. This makes the obstacle CH1 introduces an explicit, attributable fact for every
     other worker whose conflict resolution sees that cell.
   - CH2: `effect="candidate_removed"` — emitted at the I6 retain-filter, once per candidate
     the filter drops because its target == the claimed cell; recorded INSIDE the single
     filter pass the evaluation already runs (a candidate-SET delta, not a second planning
     pass), so no hidden RNG/state advance. `target_worker` = the affected unit, `pre_verb` =
     the removed verb, `cell` = the claimed cell.
   - CH3/CH4: `effect="replace"/"veto"` — the resident rewrite / non-resident WAIT
     substitution, `pre_verb`→`post_verb`.
   - CH5: `effect="reresolve"` — the resident-priority reservation that displaced a slot.

   **Attribution rule (F9):** after divergence, a worker's command that turn is
   banana-caused IFF some channel record this turn names that worker (`target_worker`) — the
   union of CH1-CH5 records is the sole, parent-independent attribution source. An empty
   record set is the machine-checkable witness of "no wrapper causation this turn" (the
   post-divergence identity claim), now sound because the pre-delegation channels (CH1/CH2)
   also emit records; an inner stall on a diverged state with an empty record set is an
   INHERITED inner stall (report-tier), while a stall whose worker is named by a CH1/CH2/CH5
   record is banana-caused (blocking). This feeds A-4's channel-naming (B.1) and is the
   definition the fuzz panel (D.3) uses so inherited parent behavior on a diverged state is
   report-tier, never blocking (DEF-11).

### D.2 FROZEN EXACT ENUMERATION MANIFEST (primary functional gate) — R5 (review §R7)

This is the FROZEN manifest whose later execution is the primary functional gate. It is
**bounded exhaustive over this frozen lattice**, NOT exhaustive over the game state space.
Every configuration runs the real candidate binary closed-loop under the D.1 probe (scripted
traces inadmissible as primary evidence — DEF-06/DEF-08); every A.4 transition and every
A-contract is checked on each; oracle decisions are cross-checked against ASSET_SURVIVAL_
ORACLE (Python) per turn. Each config has a stable ID `<sublattice>-<axis tuple>` and a
seed/map hash committed with the manifest.

**MATERIALIZED (F8/R7).** The manifest is no longer prose: `enumeration_manifest.py`
GENERATES it deterministically into `enumeration-manifest.json` — every row with a stable
`id`, an axes tuple, a per-(template,water) `map_hash`/`seed`, a `content_hash` over the
canonical row body, and a `witnesses` list of the event classes / transition edges / R1
collisions / strict-tie / historical-red tokens that row is constructed to exercise. The
script computes the coverage map (token → witnessing row ids) from the row set, asserts every
target in the universe is witnessed, prints the true `total_rows`, and emits a
`manifest_digest`; it is re-runnable to a byte-identical JSON. The row count and coverage
below are the script's ACTUAL output, not asserted prose.

Axes and value sets (frozen):
- `template` ∈ {T1 open ring/4 doors, T2 corridor articulation-mother (R5_MAP), T3 single
  reachable door (I-22), T4 two doors one parkable (R6 b2), T5 orchard-eligible (must yield
  S1), T6 solo-worker (¬EV2 whole game)}.
- `water` ∈ {dry, wet} (CD 6 vs 4).
- `profile` ∈ {harvester, chopper, mixed, idle}.
- `oppETA` ∈ {1, 3, 6, 12} (instant-loss, pre-first-fruit, r3a/r3b band, never-flips).
- `oppCount` ∈ {1, 2}.
- `worker` ∈ {absent, empty, full-wood, train@8}.
- `stock` ∈ {0, 1}.
- `cap` ∈ {80 default, 120 long-run}.

Exact configuration count (degenerate collapses stated explicitly, no fuzzy "≈"):

| sub-lattice | axes (fixed / varied) | arithmetic | configs |
|---|---|---|---|
| **L-CORE** playable maps | template{T1..T4}×water×profile×oppETA×oppCount×stock, worker∈{empty,full,train@8} | 4·2·4·4·2·3·2 | 1536 |
| **L-CORE dormant controls** | worker=absent collapses (¬EV2 ⇒ dormant identity, only template×water observable): 1 canonical control per (template,water) | 4·2 | 8 |
| **L-ELIG** T5 forced-S1 | T5×water×{worker absent,present} (proves eligibility overrides worker/opponent) | 1·2·2 | 4 |
| **L-SOLO** T6 ¬EV2 | T6×water(dry)×profile×oppETA{1,12}×oppCount{1}×stock | 1·1·4·2·1·2 | 16 |
| **L-LONG** cap-120 | T6×4 profiles cap120 (EV3 deadline) + T1×2 water×2 profile late-activate@92 (EV18) | 4 + 4 | 8 |
| **L-FIX** dedicated deterministic fixtures | ST1..ST7 (7) + C1..C6 (6) + EV9/EV15/EV16/EV19/EV20 (5) | 7+6+5 | 18 |
| **L-RED** historical red witnesses | round-3/4/5 rejected candidates f29efd0e/280ed777/2f58edef/9f5ef833 | 4 | 4 |
| **TOTAL** | | 1536+8+4+16+8+18+4 | **1594** |

**Count reconciliation (F8).** The prior prose claimed **1588** with a 16-row L-FIX (ST1..ST5
only) and NO rows for ST6/ST7 or the historical reds — exactly the gap the review flagged
(R7 items 1-2). The ACTUAL generated count is **1594**: +2 for ST6/ST7 as first-class L-FIX
rows (they were oracle-only before; ST7 was not even in the oracle self-test) and +4 for the
L-RED historical witnesses, which are now named manifest rows the gate fails without. The
generator prints this total and its `sublattice_counts`; there is no fuzzy "≈". `cap` = 80
for L-CORE/ELIG/SOLO, 120 for L-LONG/L-RED, per-fixture (≤120) for L-FIX. The old nominal
3072 (with an unenumerated "minus degenerate ≈2.9k") is withdrawn: L-CORE's worker=absent
block IS the exact degenerate set, collapsed to 8 named controls.

**Coverage proof obligation (COMPUTED by the script, F8 — the generator FAILS if any target
is unwitnessed).** Every event class (EV1-EV20), every transition edge (all 33 T-ids incl.
T3i/T7c/T8d and S9's T16'), every R1 collision (C1-C6), every strict-tie (ST1-ST7), and every
historical red is mapped to its witnessing row id(s) by `enumeration_manifest.py`'s coverage
pass; the table below is the human summary of that computed map:

| target | reached by (sub-lattice · axis combo) |
|---|---|
| EV1 / ¬EV1 | L-ELIG (T5 eligible → S1) vs L-CORE (T1..T4 ineligible) |
| EV2 / ¬EV2 | L-CORE worker∈{empty,train@8} vs L-CORE dormant controls + L-SOLO |
| EV3 | L-LONG T6 cap120 (turn>100 with ¬EV2) |
| EV4 | L-CORE profile=harvester, oppETA=1, wet (ripe on-cell flip) |
| EV5 / EV6 | L-FIX ST2 (feasible) / ST1 (infeasible); also L-CORE harvester oppETA∈{3,6} |
| EV7 | L-CORE profile=chopper + L-FIX ST3/ST4/ST5 |
| EV8 | L-CORE chopper kill + own conversion completion |
| EV9 | L-FIX EV9 fixture (combat opponent adjacent to resident on T2) |
| EV10 / EV11 | L-CORE worker=full-wood resident wood cycle |
| EV12 | L-CORE T4 peer occupancy |
| EV13 | L-CORE T2/T4 blockade geometries |
| EV14 / EV15 | L-CORE profile=idle, stock=0 (starve) → EV14; L-FIX EV15 fixture (productive re-entry) |
| EV16 | L-FIX EV16 fixture (chopper kills lost plant post-EV6) |
| EV17 | L-CORE stock=0 + mother destroyed |
| EV18 | L-LONG T1 late-activate@92 |
| EV19 | L-FIX EV19 fixture (mother made unreachable mid-conversion) |
| EV20 | L-FIX EV20 fixture (all doors made unreachable while carrying) |
| N1/A-4 stress | L-CORE worker=full-wood on T2 (articulation) and T3 (single-door) |
| C1..C6 (R1 collisions) | L-FIX C1..C6 fixtures (one deterministic config each) |
| ST1..ST7 strict-tie | L-FIX-ST1 … L-FIX-ST7 (ST6/ST7 now first-class rows AND oracle self-test) |
| historical reds | L-RED-f29efd0e / -280ed777 / -2f58edef / -9f5ef833 (gate fails if any regresses) |
| all A.4 edges incl. T3i/T7c/T8d/T16' | the computed union above; the coverage pass asserts every T-id has ≥1 witnessing row |

Dedicated deterministic fixtures (L-FIX) exist precisely so we do NOT assume a mixed/idle
opponent will happen to kill the resident (EV9) or that an idle profile will traverse
release→re-entry (EV15) or that a chopper will land on the lost plant (EV16) — each is
constructed, not hoped for. Historical red witnesses (the round-3/4/5 rejected candidates
f29efd0e/280ed777/2f58edef/9f5ef833, cross-referenced to `fuzz/failures/…` and the R5/R6
GREEN lists) are now first-class L-RED manifest rows (F8): the gate fails if any is absent or
regresses.

### D.3 Fuzz panel (defense-in-depth, demoted from primary)

Unchanged machinery (`fuzz/`, saved-failure re-runs), demoted to regression sweep behind
D.2; runs with the D.1 attribution rule so inherited parent behavior is report-tier,
never blocking (DEF-11). Saved R6 witnesses (`fuzz/failures/…`) are permanent regression
seeds; the R5/R6 GREEN-witness lists are the promotion gate.

### D.4 Host gates (unchanged)

1. Readable+compact pair: complete compilable research source, per-block compaction
   asserts, parent-restoration sha check (SEAM §C; DEF-03).
2. Behavioral research == compact equality on the mandated panels (check 3).
3. Dormant-equality broad panel + activation probe scoping (SEAM R8).
4. Exact-game gate `897829265` (both period-2 windows), banana-live replays, 516 panel,
   value/Arena gates (ACK3 stop list) — order: only after D.1-D.3 are green.

---

## E. Gap analysis vs as-built (I1 snapshot)

| gap | as-built (snapshot cite) | disposition |
|---|---|---|
| GAP-1 | No EV7 / chopper-blind flip; harvester-only ETA (`banana_opponent_eta(…, false)`, I1:644); AND F-C1 reintroduced a second approximate chopper deadline (R6 d2) | **(i) refactor needed — R2** — replace both EV7's threshold and the F-C1 founding proxy with ASSET_SURVIVAL_ORACLE (A.7): choppers enter the model via `opp_destroy_turn`, EV7 becomes oracle-driven, founding uses `feasible_found`. One oracle, no second deadline. Largest deviation |
| GAP-2 | Claim is recomputed per turn as `min` over live diagonal bananas (`banana_mother_cell`, I1:200-207, read again at I1:1056-1060) — post-loss it can migrate to a different (even opponent-planted) diagonal banana; pre-loss it is `f(view)`, not `f(state)` | **(i) refactor needed** — latch the founded/lost mother cell in wrapper state; CH2 = latched cell while its plant lives (CI-0, A-6). Small, mechanical |
| GAP-3 | S6/S7 are implicit (branch + `banana_target == (Chop, mother)` encoding), not named states | **(ii) ratify** — the encoding is deterministic and single-writer (ring Chop candidates are orthogonal-only, so the latch is unambiguous); A.1 provides the mapping; D.1 asserts the state decode |
| GAP-4 | I-16's "or training permanently infeasible" arm omitted (R6 family a: strictly stricter, never earlier) | **(ii) ratify** + spec revision note: solo-worker banana play was never validated; stricter activation is the safe default |
| GAP-5 | I-1 payback-feasibility term not checked at activation (only turn ≤ 100 + checkpoint) | **(ii) ratify** — I-5 plant cutoff blocks late planting and EV14/S5 bounds the cost of a work-less activation to ≤ 3 reserved turns |
| GAP-6 | Dormant deadline and benign completion both land in `phase == Abandoned` shared with the lost path | **(ii) ratify with mapping** — S10 vs S8/S9 are distinguished by `banana_lost`; A-1 asserts the pairing |
| GAP-7 | Post-release Bank-of-inner-cargo keeps the release and re-increments the streak (I1:917-926) | **(ii) ratify** — implements "release ends only at a lifecycle-productive candidate"; the design encodes it as EV15's definition |
| GAP-8 | `banana_lost_banking` not cleared on resident death (harmless: unit lookup gates the branch, I1:1020-1045) | **(ii) ratify** + A-1 covers it (S8 with dead worker decodes as S9 for all channels) |
| GAP-9 | HarvestNow requires standing on the mother (adjacent-with-ripe-fruit flip goes to the oracle branch) | **(ii) ratify** — matches SPEC I-10a "harvestable immediately"; the oracle correctly prices the adjacent case |
| GAP-10 | Evaluation order and channel legality existed only as comments scattered through I1 | **(ii) ratified by this document** — A.2's global order is the normative statement; D.1 makes it checkable |

Additional gaps opened by the 2026-08-06 review revision:

| gap | as-built (snapshot cite) | disposition |
|---|---|---|
| GAP-11 | No concurrent-event priority; A.4 cells assume one event fires (I1 branch order is incidental) | **(i) refactor needed — R1** — implement the A.6 total order as the step-1 selector; add A-0 decode assertion |
| GAP-12 | Attribution used raw candidate-vs-parent slot comparison past divergence (I1 detector assumptions) | **(i) refactor needed — R3** — aligned-prefix proof only, then channel-touch telemetry (D.1.4); emit the telemetry record from the probe build |
| GAP-13 | Post-loss veto is global (every bank `PICK … BANANA`, rest of game, I1:1089-1118) | **(i) refactor needed — R5** — scope the veto to the latched lineage and lapse it at EV16 (finite) |
| GAP-14 | S7/S8 lack impossible-commitment exits (only mother/resident death, I1:614-638/409-431) | **(i) refactor needed — R6** — add EV19/EV20 → T7c/T8d; A-18 asserts no stuck commitment |
| GAP-15 | N1 was assertion-only (A-4), not enforced; unconditional resident priority (I1:843-847) | **(i) refactor needed — R4** — carrier-yield rule in PHASE-2 (B.1.3); A-4 becomes the check |

Minimal path to design-conformance: (1) GAP-2 latch (small, isolated); (2) GAP-1/R2
ASSET_SURVIVAL_ORACLE (replaces EV7 threshold + F-C1 proxy with the extended
`asset_survival_oracle`); (3) GAP-11/R1 priority selector + GAP-15/R4 carrier-yield rule;
(4) GAP-13/R5 veto scope + GAP-14/R6 impossible-commitment exits; (5) D.1 contract harness +
GAP-12/R3 telemetry as a probe build; (6) D.2 frozen manifest runner (1594 configs, generated
by `enumeration_manifest.py`) reusing `make_banana_traces.py`. Everything else is ratified above.

---

## Revision 2026-08-06 (design review 20260806T073620Z)

Reviewer `local_codex_1` accepted the direction and skeleton and required five structural
corrections to make the design a total implementation contract. Each is resolved in place;
this section is the index, not a diff log.

- **R1 — atomic turn model + concurrent-event priority.** A.2 now defines the single atomic
  per-turn procedure (steps 0-9) with a per-event observation source. New **A.6** gives the
  TOTAL priority order over EV1-EV20 (rank 1 EV9 → rank 20 EV1), justified by loss/liveness
  dominating opportunity, with worked collision resolutions C1-C6 (the review's listed
  collisions). The Mealy declaration (A.2, A-0) fixes S6/blocked-hold/idle-yield as transient
  output modes, not persisted states.
- **R2 — one exact asset-survival oracle.** New **A.7** ASSET_SURVIVAL_ORACLE, implemented as
  `asset_survival_oracle` in `conversion_race_oracle.py` (extends the existing oracle; the
  harvest-only case reproduces CONVERSION_RACE_ORACLE exactly). It replaces EV7's threshold
  AND the F-C1 founding proxy — one growth-aware absolute-time deadline (`asset_lost_turn` =
  min of farm-out and multi-chopper chop-out), strict completion-before-opponent-action.
  Strict-tie fixtures ST1-ST7 defined; ST1-ST5 + founding + harvest-equivalence asserted in
  the oracle self-test (green).
- **R3 — attribution only on aligned prefix.** D.1.2 restricts parent-divergence attribution
  to the aligned prefix (first divergence ends it); beyond divergence, attribution uses the
  explicit channel-touch telemetry specified in D.1.4. A-2/A-3/A-5/A-8 reworded: identity =
  "no wrapper edit to the current inner result", not equality to a separately evolved parent.
- **R4 — enforce carrier-progress.** B.1.3 makes N1 a production DECISION rule (the
  carrier-yield rule, PHASE-2, over CH1+CH2+CH3+CH5 jointly): a banana effect that removes a
  full carrier's last progress landing YIELDS. A-4 is now the post-hoc check (with channel
  attribution), not the mechanism.
- **R5 — close the enumeration gate.** (a) B.4/S9 bound the post-loss veto to the latched
  lineage, finite, lapsing at EV16 (the global rest-of-game PICK veto is withdrawn). (b) New
  EV19/EV20 → T7c/T8d (A.4a) give S7/S8 production exits for impossible commitments (A-18).
  (c) D.2 is now the FROZEN EXACT ENUMERATION MANIFEST: axes + value sets, exact count
  **1588** (L-CORE 1544 + L-ELIG 4 + L-SOLO 16 + L-LONG 8 + L-FIX 16), the degenerate
  collapse enumerated (not "≈2.9k"), and a coverage proof obligation mapping every event
  class, transition edge, and R1 collision C1-C6 to a named config — the gate fails if any is
  unwitnessed. This manifest's later execution is the primary functional gate.

§C rewritten with an honest coverage class per defect: **13 impossible-by-construction, 3
assertion/infra-caught (DEF-03, DEF-05, DEF-11), 1 enumeration-witnessed (DEF-08)**. The
review's open items DEF-11 (now correctly attributed, not overclaimed as prevented), DEF-14
and DEF-17 (now closed by R2's single oracle) are resolved.

---

## Revision 2026-08-06b (chatgpt_1 re-review)

The independent re-review (`chatgpt_1`, disposition REVISION_REQUIRED) accepted the skeleton
and raised ten blocking findings F1-F10. Each is closed in place below (this section is the
index, not a diff log); the tally at the end is the honest recomputation F10 requires.

- **F1 — causal phase order.** A.2 now defines an explicit five-phase order: PHASE-1 read
  state + observe pre-action/inferred events → PHASE-2 arbitration/eligibility +
  pre-delegation resident decision (no transition yet) → PHASE-3 inner delegation produces
  candidate commands → PHASE-4 observe command-produced events (EV10 and any future ones) →
  PHASE-5 select transition + apply CH3/CH4/CH5 post-edits. EV10 is consumed in PHASE-5, never
  before commands exist (review R1.1); the A.6 observation-source table is re-labelled by
  phase and states a normative observability rule (no event consumed before the phase that can
  produce it). EV20 is a PHASE-1 pre-action predicate (review R1.4).
- **F2 — S6 contradiction + EV7 domain.** S6 is REMOVED as a persisted state and as a
  transition target: EV4 (flip ∧ ripe-on-cell) is a Mealy `HARVEST` OUTPUT of the CH1=Some
  state the resident already occupies (S3/S4; S5 re-employs to S3 first), with no S6 row, no
  T6a, and no phantom decode. The persisted family is 10 states. EV7 is given ONE domain —
  asset-under-attack INDEPENDENT of ownership flip — with `T_service` defined exactly from
  oracle outputs (no free-floating "next service turn", review R2.4); the health-drop is
  telemetry-only. A.4/A.6/C2 and all channel writer-state lists are regenerated consistently.
- **F3 — oracle over-counts choppers.** `_opp_destroy_turn` no longer sums simultaneous
  same-player chopper power: at most ONE chopper occupies the tree cell per turn (CHOP gates
  on standing on the cell; per-player movement-conflict resolution forbids same-player
  co-location — verified against the referee model). Each turn applies the MAX arrived power;
  advance comes only from earlier arrival/hand-off. Docstring corrected; ST5 rewritten (earlier
  arrival advances destroy 12→7) with an explicit no-summation invariant assertion; self-test
  green.
- **F4 — founding not exact.** New `founding_safety_oracle` replaces arrival-order with exact
  executable-HARVEST safety on a FROZEN post-PLANT anchor: PLANT resolves in turn `t`, sapling
  first exists at `t+1` (creation-turn tick applied), all turns anchored at `t+1`.
  `feasible_found = our_harvest_turn < opp_harvest_turn (STRICT) ∧ our_harvest_turn <
  opp_destroy_turn (STRICT)` — an equal executable-harvest turn is the last-fruit-duplication
  case and is UNSAFE (review R2.3). Self-test witnesses safe / harvest-tie-unsafe /
  chop-out-unsafe. §A.7 and the S3 guard + A-17 updated.
- **F5 — carrier-yield scope.** B.1.3 generalizes N1 from full carriers to EVERY committed
  wood carrier (`carry[WOOD]>0` ∧ bank-committed, not `free_capacity==0`), computes the
  progress-landing set speed-aware under CH5's exact movement/conflict semantics, and
  specifies an ASIDE move that PHYSICALLY vacates the contested landing (WAIT is used only when
  it already frees the cell; a bounded blocked-hold then EV20/T3i hand-off if no aside exists).
  Conversion feasibility folds the mandatory yield delay into `completion_turn` up front, with
  the priority contract stating N1 outranks a speculative conversion (review R2.5).
- **F6 — bank lot accounting.** The lineage-scoped PICK veto is unobservable (referee
  inventory is fungible per-species counts). Respecified over observable counts: a persisted
  `reserved_banana ∈ {0,1}` count, CH4 vetoes an own bank `PICK … BANANA` iff it would drop
  `bank[BANANA]` below the reserved count, lapsing at EV16. One-seed reservation and surplus
  banking are count/per-turn-delta invariants (A-15/A-16), with deposit/consume ordering and
  TRAIN/PICK/DROP reconciliation.
- **F7 — EV20 scope.** EV20 extended from S8-only/static-BFS to EVERY bank commitment (adds
  S3(Bank) via T3i) and to DYNAMIC conflict-resolved reachability (own-unit occupancy counts
  as blocked, bounded no-progress horizon). A.4a, the EV20 definition, A-18, and the S3 exits
  updated so an occupied route triggers a production hand-off instead of looping.
- **F8 — manifest materialized.** `enumeration_manifest.py` GENERATES `enumeration-manifest.json`
  deterministically: every §D.2 lattice row with a stable id, map/seed hash, content hash, and
  a declared witness set; it computes the coverage map (token → row ids), asserts completeness,
  and prints the true count. The ACTUAL total is **1594**, not 1588: +2 for ST6/ST7 as
  first-class rows (previously oracle-only; ST7 was not even asserted) and +4 for the L-RED
  historical red witnesses (f29efd0e/280ed777/2f58edef/9f5ef833). §D.2 prose reconciled to
  1594; coverage over EV1-20, all 33 T-ids, C1-C6, ST1-7, and the reds is computed, not
  asserted.
- **F9 — post-divergence attribution.** D.1.4 defines side-effect-free channel-record
  telemetry: after first divergence every channel (incl. the pre-delegation CH1 reserve-idle
  and CH2 candidate-removed, captured INSIDE the single filter/insertion pass — no double
  evaluation, no hidden RNG advance) emits `{turn, channel, target_worker, effect, pre_verb,
  post_verb, cell}`. Attribution = banana-caused iff a channel record names that worker's
  command that turn; the record union is the sole, parent-independent source. A-4 reads channel
  provenance from these records, not a counterfactual re-run.
- **F10 — §C tally.** Honestly recomputed after F1-F9: **8 impossible-by-construction, 6
  assertion/infra-caught, 3 enumeration-witnessed** (total 17). DEF-09/10/12 reclassify
  IBC→AC (the carrier-yield rule is an enforced, A-4-checked decision, not structural
  impossibility — review R4); DEF-14/17 reclassify IBC→EW (founding/chopper exactness rides on
  the fixtures being exercised — review R2); DEF-08 is now genuinely EW (the frozen manifest
  exists); DEF-06 stays IBC (its claim no longer depends on the contradictory S6/EV7 model).

Verification: `conversion_race_oracle.py` self-test green after the F3/F4 edits (incl. ST1-ST7,
the no-summation invariant, and the three founding-safety outcomes); `enumeration_manifest.py`
runs deterministically (re-run yields byte-identical JSON), reports 1594 rows and complete
coverage. Disposition remains design-only: no implementation, candidate build, host replay,
516 panel, value protocol, submission, restore, or Arena action is taken here.
