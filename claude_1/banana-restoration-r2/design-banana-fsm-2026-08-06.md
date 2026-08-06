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

### A.1 State enumeration (11 states; S-WORK parameterized by 5 tasks)

| id | name | as-built encoding (I1 snapshot) |
|---|---|---|
| S0 | Unarbitrated | `banana_enabled == None` (turn-1 pre-decision, I1:1004-1006) |
| S1 | Disabled | `banana_enabled == Some(false)` (apple game, permanent) |
| S2 | Dormant | enabled, `phase == Dormant` |
| S3 | ActiveWork(task ∈ {Boot,Plant,Chop,Harvest,Bank}) | `phase == Active`, `banana_target == Some((task,cell))`, `task != Idle`, not the Chop-mother latch. `ActiveWork(Boot/Plant)` is the Founding/CarryingSeed analog; `ActiveWork(Chop/Bank)` is the WoodCycle. Distinct commitments, one state family (ratified in E, GAP-3) |
| S4 | ActiveIdle | `phase == Active`, chosen candidate Idle, `banana_idle_streak ∈ {1,2}`; includes the F-B1 idle-yield aside move |
| S5 | ActiveReleased | `phase == Active`, `banana_idle_streak >= 3` (F-D2 starvation release; reservation dropped, resident inner-controlled) |
| S6 | HarvestNow | contest-response branch 1 (I1:649-664): flip latched this turn, ripe fruit harvestable immediately (resident on mother, capacity free). Transient: one turn per firing |
| S7 | Converting | contest-response branch 2 latch: `banana_target == Some((Chop, mother))` (I1:626-638; set nowhere else — ring Chop candidates are orthogonal-only) |
| S8 | LostBanking | `banana_lost && banana_lost_banking` (I-10a branch 3 with leftover cargo; I1:737-751, 1033-1044) |
| S9 | LostReleased | `banana_lost && !banana_lost_banking` (resident permanently inner-controlled; persistent claim while lost plant lives — SPEC Rev 2026-08-06) |
| S10 | AbandonedBenign | `phase == Abandoned && !banana_lost` (deadline / completion / resident death; structural identity thereafter) |

### A.2 Per-state specification

Format per state: **entry** / **evaluation order** (what is checked first each turn) /
**interventions** (channels this state may touch) / **exits** (guarded transitions, T-ids)
/ **liveness** (obligation + horizon).

Global evaluation order (every enabled turn; this order is normative — DEF-06 arose from
flip evaluation being reachable only from some activities, ACK3 item 1):

1. Arbitration (once, S0 only) — CH6.
2. Phase update (activation / death / completion) — pure view read.
3. Resident decision, in order: (a) blocked/bounce bookkeeping (F-B3); (b) Converting
   latch check; (c) **ownership + asset-threat evaluation** (EV4-EV7) — evaluated on
   EVERY active turn, all activities included, before any candidate work; (d) contest
   branches; (e) candidate set + commitment rule (SPEC §e); (f) idle-yield / starvation
   release.
4. Channel writes CH1/CH2 as a pure function of the resulting state (§B).
5. Delegate to inner policy.
6. Post-edits: CH3 (resident) then CH4 (non-resident vetoes).
7. CH5 re-resolution iff CH3 rewrote a command.

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
Entry: T2b; from S4/S5 on productive-candidate reappearance (EV15); from S6 after
harvest; task switches internal to S3 go through the commitment rule (SPEC §e: clause-1
invalidation, H=3 hold, eps=1 upgrade).
Evaluation order: global order; within 3e, wood cargo short-circuits to Bank-only
candidates (I-21, I1:442-445); surplus banana suppresses Plant candidates (I-9,
I1:461, 499); founding guard for a diagonal Plant uses horizon margins
(`eta_opp_h > first_fruit_delay`, `eta_opp_x > 2*CD + ceil(health(2)/chop)`, F-C1,
I1:342-358); orthogonal slots keep instant margins; Bank candidates skip occupied doors
while a free one exists (F-B2, I1:378-390); I-5 late cutoff blocks all planting (EV18 is
a guard, not a transition — planting candidates vanish, other tasks continue).
Interventions: CH1 = Some(resident); CH2 = Some(latched mother) iff a founded mother
lives; CH3 (one rewrite, resident only); CH4 (mother vetoes + seed exclusivity);
CH5 (priority = {resident}, forbidden set EMPTY — R5 ruling).
Exits: T3a EV4 → S6; T3b EV5 → S7; T3c EV6 → S8 (cargo>0) / S9 (cargo=0); T3d EV7
(asset-under-attack, design-new — see E GAP-1) → oracle-generalized convert-vs-abandon:
S7 if a conversion completes before the asset's value is destroyed, else S8/S9; T3e EV9
resident died → S10; T3f EV17 feature complete/impossible → S10; T3g task
invalidation/upgrade → S3(task') or S4 (only Idle candidate remains); T3h EV13 blocked 2
turns with same target still dominant and cargo-free → blocked-hold WAIT one turn
(sub-state of S3, I1:807-826), then re-probe.
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
candidate → S3; T4c-f = T3a-c/T3e/T3f (contest and phase exits identical to S3 — the
flip check precedes candidate work, so camping cannot hide a flip; DEF-06). Liveness:
dwell ≤ 3 turns holding the reservation (then S5); while camping, the N1 obligation of §B
(never the persistent obstacle of a loaded teammate) is the state's second obligation.

**S5 ActiveReleased.**
Entry: T4a. Evaluation: contest/phase checks still run (mother may flip while released);
candidate generator probed each turn for EV15; the release persists while the best
candidate is Idle or Bank-of-inner-cargo (I1:917-926 — banking inner-acquired cargo is
not lifecycle-productive; re-capture caused D-2 churn). Interventions: CH1 = None
(reservation released); CH2 as S3; CH4 (mother + seed vetoes still apply — the released
resident is protected-against like a peer); no CH3/CH5. Exits: T5a EV15 → S3; T5b-d =
T3a-c (contest); T5e EV9 → S10; T5f EV17 → S10. Liveness: none for the wrapper; inner
economy owns the worker (P4 parity with parent is the gate).

**S6 HarvestNow.**
Entry: EV4 — ownership flip (I-7, committed-harvester ETA, ties conceded) while a ripe
fruit is harvestable immediately (on-cell, capacity free). Evaluation: none beyond
emitting HARVEST. Interventions: CH1 = Some; CH2 = Some(latched); CH3 = `HARVEST`;
CH4; CH5. Exits: T6a next turn re-evaluates from the top: flip persists → EV5/EV6 →
S7/S8/S9; flip cleared (opponent left) → S3/S4; fruit gone + flip persists → EV5/EV6.
Single-turn state by construction. Liveness: exactly one HARVEST lands this turn.

**S7 Converting.**
Entry: EV5 — flip latched and ORACLE `feasible` (strict:
`completion_turn < opponent_harvest_turn`, both absolute, anchored at the decision turn;
ORACLE:160-223). Decision latched: no re-arbitration mid-sequence (opponent arrival
mid-chop does not reopen the won race; I1:614-638). Evaluation: latch check (3b) first.
Interventions: CH1 = Some; CH2 = Some(latched mother); CH3 = `MOVE`-to-mother / `CHOP`;
CH4; CH5. Exits: T7a EV8 mother destroyed (our final chop or opponent) → phase update:
ring/stock live → S3/S4, else → S10 via EV17; T7b EV9 → S10. No other exit — the latch
is broken only by the mother's death. Liveness: the final chop lands on or before the
ORACLE's predicted `completion_turn` (runtime-assertable, A-12); distance-to-mother
strictly decreases while traveling.

**S8 LostBanking.**
Entry: EV6 (oracle-infeasible flip) with `total_carried > 0` at the loss turn; the one
sanctioned deferral: an already-committed banking DROP executes at the flip turn itself,
response begins wood-free at t+1 (SPEC I-10a; I1:645-647). Evaluation: bank-only
(`banana_lost_action`, I1:409-431 — nearest-door (distance, cell) minimum).
Interventions: CH1 = Some (held ONLY for the leftover cargo); CH2 = Some(latched lost
cell) while the lost plant lives; CH3 = MOVE-to-door/DROP; CH4 (incl. banana-PICK
exclusivity); CH5. Exits: T8a cargo = 0 (DROP landed or cargo lost) → S9 immediately,
same turn (I1:1038-1043); T8b EV9 → S9 (worker gone; claim persists); T8c EV16 lost
plant died → claim lapses, state remains until T8a. Liveness: I-19/I-20/I-21 verbatim on
the leftover cargo — strict door progress, DROP within `door_dist(loss) + 2`.

**S9 LostReleased.**
Entry: T8a; or EV6 with nothing carried (released at the flip turn itself, SPEC Rev
2026-08-06). Evaluation: claim maintenance only. Interventions: CH2 = Some(latched lost
cell) while that plant lives, then None (EV16); CH4 (mother vetoes while claim live +
banana-PICK exclusivity for the rest of the game); CH1 = None; no CH3/CH5. Exits: none
(absorbing; `banana_lost` latched blocks re-activation). Liveness: none for the wrapper;
non-interference obligations of §B are the state's whole contract.

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
| EV7 | asset-under-attack: opponent chopper at `eta_opp_x <= 1` of the live mother, or mother health decreased without an own chop (design-new; R6 family d2) |
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
reached by a named transition.

| state \ ev | EV1 | EV2 | EV3 | EV4 | EV5 | EV6 | EV7 | EV8 | EV9 | EV10 | EV11 | EV12 | EV13 | EV14 | EV15 | EV16 | EV17 | EV18 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S0 | T0a/T0b | U1 | U1 | U1 | U1 | U1 | U1 | U1 | U1 | U1 | U1 | U1 | U1 | U1 | U1 | U1 | U1 | U1 |
| S1 | U2 | ∅3 | ∅3 | ∅3 | ∅3 | ∅3 | ∅3 | ∅3 | ∅3 | ∅3 | ∅3 | ∅3 | ∅3 | ∅3 | ∅3 | ∅3 | ∅3 | ∅3 |
| S2 | U2 | T2b | T2a | U4 | U4 | U4 | U4 | U4 | ∅5 | ∅5 | ∅5 | U4 | U4 | U4 | U4 | U4 | U4 | ∅5 |
| S3 | U2 | ∅6 | ∅7 | T3a | T3b | T3c | T3d | T3g | T3e | T3g→Bank | T3g | T3g | T3h | U8 | ∅6 | U9 | T3f | guard |
| S4 | U2 | ∅6 | ∅7 | T4c | T4d | T4e | T3d | T3g | T4e' (=T3e) | T4b→Bank | ∅10 | T3g | ∅10 | T4a | T4b | U9 | T4f | guard |
| S5 | U2 | ∅6 | ∅7 | T5b | T5c | T5d | T3d | ∅11 | T5e | ∅12 | ∅12 | ∅11 | ∅12 | ∅13 | T5a | U9 | T5f | guard |
| S6 | U2 | ∅6 | ∅7 | T6a | T6a | T6a | ∅14 | T6a | T3e | U15 | U15 | T6a | U15 | U15 | ∅6 | U9 | U16 | ∅7 |
| S7 | U2 | ∅6 | ∅7 | ∅17 | ∅17 | ∅17 | ∅17 | T7a | T7b | U18 | ∅18 | T7a | ∅19 | U8 | ∅6 | U9 | via T7a | ∅7 |
| S8 | U2 | ∅6 | ∅7 | ∅20 | ∅20 | ∅20 | ∅20 | T8c | T8b | U21 | T8a | ∅22 | liveness | U8 | ∅23 | T8c | via T8a | ∅7 |
| S9 | U2 | ∅6 | ∅7 | ∅20 | ∅20 | ∅20 | ∅20 | T16' | ∅24 | ∅12 | ∅12 | ∅12 | ∅12 | ∅12 | ∅23 | EV16→claim None | ∅24 | ∅7 |
| S10 | U2 | ∅25 | ∅25 | ∅25 | ∅25 | ∅25 | ∅25 | ∅25 | ∅25 | ∅25 | ∅25 | ∅25 | ∅25 | ∅25 | ∅25 | ∅25 | ∅25 | ∅25 |

### A.5 Completeness argument

1. **Rows are exhaustive**: A.1's 11 states partition the wrapper's reachable
   configuration space — `banana_enabled ∈ {None, false, true}` × `phase` ×
   `{banana_lost, banana_lost_banking, idle_streak >= 3, target == (Chop, mother)}` — and
   every combination not named is excluded by construction (e.g. `banana_lost` with phase
   ≠ Abandoned is unreachable: the loss transition sets both, I1:737-738; the
   contract-harness assertion A-1 checks the exclusion at runtime).
2. **Columns are exhaustive over the rejection history**: EV1-EV18 cover every event any
   diagnosis or ACK exposed — ownership flip in all four ripe×feasible quadrants
   (EV4/5/6; ACK2 item 2, ACK3 item 2), mother destroyed (EV8), worker died (EV9,
   SEAM R5), opponent adjacent as both harvester-camp (inside EV4-6 via I-7) and
   chopper-attack (EV7; R6 d2), second worker not trained (¬EV2 dwell; ACK gate D-9),
   orchard-eligible map (EV1), choke/articulation and single-door geometry (environment
   parameters of N1/N3 + C8 serialization; R5, R6 b1/b2), starvation (EV14; R6 d),
   bounce-blocked (EV13; R6 b2).
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
   inner-owned concern. ∅13 streak already ≥ 3; release persists. ∅14 EV7 with a ripe
   on-cell fruit: harvest-now dominates (order 3c evaluates EV4 first). U15 S6 lasts one
   turn and emits HARVEST (no MOVE/cargo events attributable to it). U16 harvesting a
   live mother contradicts EV17's "no live ring banana". ∅17 latch: the convert decision
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

---

## B. Interference contracts (six channels)

Master invariant **CI-0 (state-purity)**: on every turn, each channel's value/action is a
pure function of (FSM state, latched data, `S_t`) as tabulated below — never of incidental
history. This kills the stale-reservation class by construction: a channel cannot hold a
value its current state does not license.

### B.1 CH1 — reservation `banana_idle_unit` (SEAM I2/I3/I4)

1. WRITER states and legal values: `Some(resident_id)` in S3, S4, S6, S7, S8;
   `None` in S0, S1, S2, S5, S9, S10. Written every enabled turn before delegation
   (SEAM R1); no other writer exists (`external_idle_unit` is the orchard's, never
   shared — SEAM R1).
2. Inner touchpoints: YamoBot inserts `WAIT` for the reserved id (SEAM I4), removing the
   unit from inner planning; its cell becomes a *stationary obstacle* in every
   conflict-resolution pass.
3. NON-INTERFERENCE obligations:
   - **N1 (carrier-progress)**: the reservation must never make the reserved unit a
     persistent stationary obstacle on a loaded teammate's committed bank route — no
     reservation may remove the last progress-making candidate of a full carrier for
     ≥ 2 consecutive turns (generalizes R5 §H3 and R6 ROOT B: articulation cells and
     occupied-door detours are two geometries of the same violation). Discharged by:
     idle-yield (S4), starvation release (S5), loss release (S9), and the S3 rule that a
     working resident is moving toward completion.
   - **N5 (funding)**: CH1 is None until EV2 — no reservation can displace TRAIN
     (I-17/I-18; D-9).
4. Runtime-assertable contract:
   - A-1: `banana_lost ⇒ phase == Abandoned`; `idle_streak >= 3 ⇒ CH1 == None`;
     `CH1 == Some(w) ⇒ state ∈ {S3,S4,S6,S7,S8} ∧ w == starter_id`.
   - A-4 (N1 check): for every own unit `u` with `free_capacity(u)==0 ∧ carry[WOOD]>0`:
     `door_dist(u,t) < min door_dist(u,t') over the last 2 turns`, OR a DROP/cargo-loss
     occurred, OR `u` was displaced ≤ 1 turn (I-20 tolerance). Violation ⇒ panic with
     the reserved unit's cell and the carrier's route.
   - A-5: `state ∈ {S5,S9} ⇒` the resident's emitted command equals the inner's
     un-edited command for that slot.

### B.2 CH2 — cell claim `banana_protected_cell` (SEAM I2/I3/I6)

1. WRITER states and legal values: `Some(latched_mother)` in S3/S4/S5/S6/S7 while the
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
     resident in S6/S7 — i.e. claim ⇒ no own CHOP/HARVEST candidate survives on the
     claimed cell for any inner-controlled unit (the filter worked); a CH4 veto firing
     (B.4) is evidence this assertion's upstream failed and is itself logged.
   - A-8: dormant/disabled turns: `CH1 == None ∧ CH2 == None ∧ output == inner output`
     byte-equal (check 4).

### B.3 CH3 — resident command post-edit via `replace_action` (SEAM A, I1:1083-1087)

1. WRITER states: S3, S4, S6, S7, S8 — exactly the CH1=Some states; at most ONE rewrite
   per turn, targeting only the resident's slot. Legal values per state: S3(task) — the
   verb of the committed task (`MOVE/CHOP/HARVEST/PLANT/PICK/DROP/WAIT` per task); S4 —
   `WAIT` or the idle-yield `MOVE`; S6 — `HARVEST`; S7 — `MOVE`-to-mother or `CHOP`;
   S8 — `MOVE`-to-door or `DROP`.
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

1. WRITER states: any state with CH2 = Some (mother veto), plus every S3-S9 state for the
   banana-PICK exclusivity veto. Legal action: substitute `WAIT` — never any other verb —
   and only for: (a) `CHOP`/`HARVEST` by a unit standing ON the claimed cell;
   (b) `PICK … BANANA` at the bank (I-2/I-15 exclusivity, held while active and for the
   rest of the game after loss — SPEC Rev 2026-08-06).
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

1. WRITER states: runs iff CH3 rewrote a command this turn (S3, S4, S6, S7, S8). Legal
   parameterization: priority set = `{resident}` exactly; forbidden set = **empty,
   always** (the r5 mother-forbidden set is void — R5 §H3, ratified R5 fix).
2. Inner touchpoints: `resolve_move_conflicts_with_priority` re-parses already
   landing-rewritten moves; every stationary own unit's cell is `reserved`; detour
   tie-break is `(dist, cell)`-lexicographic (R6 b mechanism step 3).
3. NON-INTERFERENCE: N1 is the binding obligation — the re-resolution may displace a
   carrier at most 1 consecutive turn (I-20 tolerance); the single-door serialization is
   deterministic (resident first, then ascending id — I-22 rev item 8); CH5 must never
   run on released/dormant turns (the inner's own resolution stands).
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

- A-12 (oracle-completion): in S7, `current_turn <= committed completion_turn`; the
  mother's final chop lands at `<= completion_turn` (catches any drift between the
  candidate's inline race arithmetic and ORACLE — the DEF-07 class).
- A-14 (D-8 scope): any own chop-class command targeting a live own diagonal banana ⇒
  state == S7 (entered via EV5). Discretionary owned-mother chop panics (ACK2 item 2).
- A-15 (one-seed): resident carries ≥ 2 bananas ⇒ emitted verb ∈ {MOVE-to-door, DROP}
  and no Plant candidate was offered (I-9; ACK1 item 1).
- A-16 (bootstrap): total feature-attributable bank `PICK … BANANA` count ≤ 1 per game
  (I-2).
- A-17 (plant geometry): every own `PLANT BANANA` cell ∈ Ring, count caps per I-12/I-13,
  founding guard of S3 held at plant time (D-5/D-6 decision side).

---

## C. Retrospective validation (acceptance test of this design)

Defect registry: every terminal defect from the five rounds (ACK1-3, R5, R6), each mapped
to the design element that makes it impossible or assertion-caught. Any unmapped defect
would mean the design is incomplete; there are none.

| # | defect (citation) | design element that kills/catches it |
|---|---|---|
| DEF-01 | No one-seed reservation: 2 harvested bananas both replanted before banking (ACK1 item 1) | S3 surplus guard (Plant candidates suppressed while `carry[BANANA] > 1`) + assertion A-15 |
| DEF-02 | I-10a unimplemented: unripe contested mother fell through to normal investment; no convert/abandon (ACK1 item 2) | EV4/EV5/EV6 are total over the flip quadrants and evaluated in every active state (table rows S3-S5 have no `∅` in those columns); no-implicit-passthrough rule A.5.4 |
| DEF-03 | No compilable readable research source; checks 2/3 unrunnable (ACK1 item 3) | D.4 host-gate precondition 1 (readable+compact pair is a build artifact gate, not good will) |
| DEF-04 | Static `ceil(health/chop)` ignored growth during the chop sequence (ACK2 item 1) | EV5 guard is ORACLE by name (growth-aware `exact_chop_turns`, ORACLE:124-141); assertion A-12 catches any regression at the first divergent conversion |
| DEF-05 | D-8 exemption scope unclear; vacuous pre-existing-mother trace (ACK2 item 2) | A-14: own diagonal chop ⇔ S7, entered only via EV5 after a real flip; D.2 grid must reach S7 from a candidate-driven own-plant (grid class G-f) |
| DEF-06 | Flip response unreachable: real candidate camps on mother, scripted t5 masked it (ACK3 item 1) | Evaluation-order rule (3c before candidates, all states) + S4 dwell bound (EV14 ≤ 3) + D.2 requirement that EV4-6 fire from S4 in-grid |
| DEF-07 | Three inconsistent conversion deadlines / mixed time origins (ACK3 item 2) | Single-oracle rule: EV5/EV6/A-12/A-14 all name ORACLE; the design forbids any second deadline expression (B.7 A-12 asserts agreement per conversion) |
| DEF-08 | R-3 boundary not candidate-reachable (ACK3 item 3) | D.2: ORACLE boundary geometries r3a/r3b are mandatory grid points reachable closed-loop (grid class G-f) |
| DEF-09 | Mother in CH5 forbidden set ⇒ transit-impossible ⇒ 225-turn carrier livelock (R5 §H3; host round-4 review) | CH5 contract: forbidden set EMPTY always (B.5.1) + N2 transit-neutrality (B.2.3) + A-4 |
| DEF-10 | R5 v2: forbidden-landing + door-occupancy *jointly* suffice; fix removed only one conjunct (R5 geometry log; recurred as R6 ROOT B) | N1 is stated over the conjunction (any channel-induced stationarity on the carrier's last progress route, B.1.3); A-4 is geometry-agnostic |
| DEF-11 | Detector attribution gap: 74 D-9 + inherited D-4/D-6 flagged on byte-identical parent behavior (R6 ROOT A) | D.1/D.3: attribution rule "banana-attributable = diverges from the parent's aligned slot" is part of the harness definition, not detector discretion |
| DEF-12 | Stationary Idle resident camping mother = reserved obstacle ⇒ carrier parity livelock (R6 ROOT B, b1) | S4 idle-yield rule + N1 + A-4; S4 dwell bound EV14 |
| DEF-13 | `banana_bank` targeted occupied doors; bounce-blind blocked counter ⇒ resident k=96 bounce (R6 b2) | S3(Bank) occupied-door guard (F-B2) + EV13 bounce-inclusive definition (F-B3) + liveness obligation of S3(Bank) |
| DEF-14 | Instant plant margins certified only the planting turn; opponent farmed the mother every regrowth (R6 ROOT C(i)) | S3(Plant) founding guard: diagonal mother requires `eta_opp_h > first_fruit_delay` ∧ `eta_opp_x > conversion horizon` (F-C1); A-17 |
| DEF-15 | Inverted claim release: post-loss cell claim dropped, worker kept; inner reinvested in lost asset (R6 ROOT C(ii); candidate D-8/D-1 tails) | CH2 legal-value table: claim persists in S8/S9 while the lost plant lives (latched); CH1 = None in S9; A-6/A-1 |
| DEF-16 | Lost-hold froze the resident to game end; P4 stalls (R6 ROOT D, d1) | S8 exit T8a is immediate on cargo = 0, S9 is CH1=None; S8 liveness = I-19/20/21 with horizon; A-1 |
| DEF-17 | Chopper-blind flip: harvester-only ETA ⇒ resident spectated while choppers killed the mother (R6 d2) | EV7 asset-under-attack event (design-new, transition T3d in S3/S4/S5) + S4 dwell bound as liveness backstop; grid class G-d makes it reachable |

Coverage: 17/17 defects mapped. Three (DEF-03, DEF-08, DEF-11) are
verification-infrastructure defects and map to section D by design — the maturity pyramid
is part of the deliverable precisely because those rounds were lost to test gaps, not
wrapper gaps.

---

## D. Verification plan (maturity pyramid, bottom-up)

### D.1 Contract harness (foundation)

1. A probe build (family probe pattern — SEAM R8's activation probe) compiled with a
   `banana_contracts` cfg: after step 7 of every turn, evaluate assertions A-1 … A-17
   against (FSM state, channel values, `S_t`, emitted commands, paired parent stream
   where available). Violation ⇒ `eprintln!` full witness (turn, state, channel values,
   both command streams) then `panic!`.
2. Attribution rule baked in (DEF-11): a command is banana-attributable iff it differs
   from the stable parent's aligned slot on the identical input stream; A-8's
   byte-equality check supplies the pairing.
3. Contracts are compiled OUT of the delivery build (cfg-gated; delivery stderr must stay
   empty — SEAM R2/R8). The probe build's bytes are never the submission bytes.

### D.2 Exhaustive small-scope enumeration (primary functional evidence)

Bounded grid, enumerated completely, all A.4 transitions + all A-contracts checked on
every configuration, closed-loop candidate-driven (DEF-06/DEF-08: scripted traces are
inadmissible as primary evidence).

Parameter lattice (proposal):

1. Map templates (6): T1 open ring (8 ring cells, 4 doors); T2 corridor with the
   diagonal mother as articulation cell (R5 `R5_MAP` class); T3 single reachable door
   (I-22 serialization); T4 two doors, one occupiable by a parked unit (R6 b2 class);
   T5 orchard-eligible map (water-adjacent door, `enemy_distance >= 11` — must yield S1);
   T6 solo-worker map (¬EV2 for the whole game). Dimensions ≤ 14×5 as in the trace
   fixtures.
2. Water at the mother candidate: {none, adjacent} (2) — CD 6 vs 4 (SPEC §0).
3. Opponent profile: {harvester, chopper, mixed, idle} (4) — chopper reaches EV7,
   harvester reaches EV4-6, idle reaches pure-lifecycle paths.
4. Opponent start ETA to the mother candidate: {1, 3, 6, 12} (4) — spans instant-loss,
   pre-first-fruit, the ORACLE r3a/r3b strict-tie band, and never-flips.
5. Opponent count: {1, 2} (2).
6. Second own worker: {absent, present-empty, present-full-wood, trained-at-turn-8} (4)
   — full-wood exercises N1/A-4 on every geometry.
7. Banked banana stock: {0, 1} (2) — bootstrap path on/off.
8. Turn cap: 80 (covers plant → first fruit → one conversion race at CD 6 with slack;
   activation deadline paths tested by template T6 + cap).

Size: 6 × 2 × 4 × 4 × 2 × 4 × 2 = **3072 configurations** (target band 2k-10k). Each
runs the real candidate binary closed-loop under the D.1 probe; oracle outputs
cross-checked against ORACLE (Python) per conversion decision.

Event-class reachability argument (each A.3 event class reachable in-grid):
EV1 ← T5 (eligible) vs T1-T4,T6 (ineligible). EV2/¬EV2 ← worker configs, T6.
EV3 ← T6 with cap? no — EV3 needs turn > 100: add a single dedicated long-run
sub-panel (T6 × 4 profiles, cap 120, 24 configs) to reach it; included in the count
above as replacement of dead combinations (T5 × water is fixed ⇒ 3072 nominal minus
degenerate cells ≈ 2.9k live). EV4 ← harvester ETA 1 with ripe fruit (water-adjacent,
cap 80 reaches first fruit at ~16-20). EV5/EV6 ← harvester ETA 3/6 at the r3a/r3b band
(grid class G-f: both boundary geometries appear verbatim as T1 instances).
EV7 ← chopper profiles (G-d). EV8 ← chopper kills + own conversions. EV9 ← mixed
profile with combat-capable opponent adjacent to the resident (template T2 places the
resident exposed). EV10/EV11 ← full-wood second worker + resident wood cycle.
EV12 ← peer occupancy in T4. EV13 ← T2/T4 blockade geometries. EV14/EV15 ← idle
opponent + no-stock configs (candidate generator starves during growth).
EV16 ← chopper kills the lost plant post-EV6. EV17 ← stock 0 + mother destroyed.
EV18 ← the cap-120 sub-panel with late activation. Single-door contention ← T3;
articulation ← T2 (both are N1/A-4 stress classes, per DEF-09/10/12/13).

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
| GAP-1 | No EV7: flip trigger counts harvesters only (`banana_opponent_eta(…, false)`, I1:644); chopper attack on the mother is invisible (R6 d2; F-D3 was deferred) | **(i) refactor needed** — add the EV7 predicate (chopper ETA ≤ 1 ∨ un-attributed mother health drop) feeding the same oracle-generalized convert/abandon branch. Without it, table cells S3-S5 × EV7 are open and D.2 class G-d fails by construction. Largest deviation |
| GAP-2 | Claim is recomputed per turn as `min` over live diagonal bananas (`banana_mother_cell`, I1:200-207, read again at I1:1056-1060) — post-loss it can migrate to a different (even opponent-planted) diagonal banana; pre-loss it is `f(view)`, not `f(state)` | **(i) refactor needed** — latch the founded/lost mother cell in wrapper state; CH2 = latched cell while its plant lives (CI-0, A-6). Small, mechanical |
| GAP-3 | S6/S7 are implicit (branch + `banana_target == (Chop, mother)` encoding), not named states | **(ii) ratify** — the encoding is deterministic and single-writer (ring Chop candidates are orthogonal-only, so the latch is unambiguous); A.1 provides the mapping; D.1 asserts the state decode |
| GAP-4 | I-16's "or training permanently infeasible" arm omitted (R6 family a: strictly stricter, never earlier) | **(ii) ratify** + spec revision note: solo-worker banana play was never validated; stricter activation is the safe default |
| GAP-5 | I-1 payback-feasibility term not checked at activation (only turn ≤ 100 + checkpoint) | **(ii) ratify** — I-5 plant cutoff blocks late planting and EV14/S5 bounds the cost of a work-less activation to ≤ 3 reserved turns |
| GAP-6 | Dormant deadline and benign completion both land in `phase == Abandoned` shared with the lost path | **(ii) ratify with mapping** — S10 vs S8/S9 are distinguished by `banana_lost`; A-1 asserts the pairing |
| GAP-7 | Post-release Bank-of-inner-cargo keeps the release and re-increments the streak (I1:917-926) | **(ii) ratify** — implements "release ends only at a lifecycle-productive candidate"; the design encodes it as EV15's definition |
| GAP-8 | `banana_lost_banking` not cleared on resident death (harmless: unit lookup gates the branch, I1:1020-1045) | **(ii) ratify** + A-1 covers it (S8 with dead worker decodes as S9 for all channels) |
| GAP-9 | HarvestNow requires standing on the mother (adjacent-with-ripe-fruit flip goes to the oracle branch) | **(ii) ratify** — matches SPEC I-10a "harvestable immediately"; the oracle correctly prices the adjacent case |
| GAP-10 | Evaluation order and channel legality existed only as comments scattered through I1 | **(ii) ratified by this document** — A.2's global order is the normative statement; D.1 makes it checkable |

Minimal path to design-conformance: (1) GAP-2 latch (small, isolated); (2) GAP-1 EV7
branch (medium — one new predicate + reuse of the existing branch bodies); (3) D.1
contract harness as a probe build; (4) D.2 grid runner reusing `make_banana_traces.py`
machinery. No other as-built change is required; everything else is ratified above.
