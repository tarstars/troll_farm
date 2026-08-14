# Task 20260814-iteration-3-work-plan — iteration 3 opening queues

**STATUS 2026-08-14 late / 2026-08-15: A-1..A-5 ALL DELIVERED by claude_1; A-2 accounting
independently VERIFIED by codex_1 (65/54/11 on `f5acb142`); A-3 N5 re-review CONCUR (N5 CLOSED);
A-4 dridriun re-review CONCUR (postmortem CLOSED); A-5 H3a preflight PASS (A-6 licensed but
DEFERRED). SUPERSEDED AS QUEUE by the owner programme of 2026-08-15 —
`docs/PROGRAMME-banana-farm-2026-08-15.md` and policy message `20260814T213500Z…-banana-oscillation-programme-policy.md`.
Open residue here: C-1 discharge question to codex_1; C-2 F1 PARKED by owner ruling `f5acb142`.**

Coordinator: `local_claude_1`. Created 2026-08-14 after the P0 arc closed (guards G1–G6
done pending final re-verification; σ = 1.501 delivered and closed). This record is the
citable source for the per-agent queues assigned in the two policy messages of the same
stamp. It creates no new science; every item below already has its own task record or
backlog entry, cited inline.

## Standing constraints on everything below

- **No Arena action is authorized by this plan.** Arena authority is `local_claude_1`
  alone; any submission is a separate decision under `docs/STATE.md` §3.
- **σ discipline:** measured score variability is 1.501, so any ≥+1.0 value claim needs
  5 arena runs per arm. Plan experiments accordingly; do not claim value from single reads.
- **Owner-facing wording:** plain language first, codes explained at first use
  (`coordination/multi-agent-protocol.md`).
- **Guards standing rule:** a new test is not finished until it has been observed
  failing — break the subject, watch it fail, restore, say what you broke.
- Doer / reviewer / integrator stay distinct on every item.

## codex_1 queue (in order)

### C-1. G6 final re-verification — closes task `20260810-guards-that-cannot-fail`

Your 2026-08-14 review verdict `REVISION_REQUIRED` named exactly one defect: trunk still
counted mutant D4-M6 in the denominator (51/63) although its exclusion was approved. That
was an integration gap, now repaired: claude_1's application commit `5b931cbb` is merged
to trunk at `650fd73b`, where the manifest carries `excluded_from_totals: true` with the
equivalence proof as reason, and the regenerated ledger reads **62 run / 51 caught /
82.3 %**. Re-run your independent reproduction against trunk `650fd73b` (or later). On a
clean pass, publish acceptance; the guards task then closes end-to-end. Estimated small —
the audit harness you already built applies unchanged.

### C-2. F1 readiness audit — confirmed, task per `docs/BACKLOG.md` §P1 F1

Reassigned to you 2026-08-12; this confirms it as your next item after C-1. Scope
unchanged: use only legal public state history, whole-map-root folds, turn 40 as primary,
fixed linear/centroid models, and command/label deletion plus static/permutation/seat
controls. N4 is closed and H3a is integrated; the exact A2-0b artifact hash was
reverified before release. Deliverable: a readiness report. Boundary: a classifier alone
never authorizes adaptation.

### C-3. CBF second review — task `20260807-d89a-leak-repairability-scoping`

Second, independent review of claude_1's 2026-08-07 `NOT_REPAIRABLE` verdict on the D89a
banana-leak (D92 isolation: 5.4× denial dose, opponent score +0.188 upward,
`gold_adaptive` family delta 208.78). Deliverable: concur or dissent, with evidence.
This feeds the owner decision on whether the CBF conditional-banana-farm design
(`docs/superpowers/specs/2026-08-07-conditional-banana-farm-design.md`, complete, not
implemented) ever enters implementation. Reviewing the verdict does not authorize any
implementation work.

## claude_1 queue (in order)

### A-1. c5 instrument ruling — in flight, scope confirmed

As assigned in `20260812T073000Z…-c5-instrument-ruling-assignment-policy.md` and taken up
in your 2026-08-14 ack: rule whether the c5 instrument can observe the behaviour policed
by detector D-9 rows (b) `train_late`, (c) `train_missing`, (d) `train_stats_differ`,
and close row (a)'s applicability axis in the same pass. Output: a citable ruling record
with supported / unsupported-with-reason per row. D-6 (a1) stays out of scope, as ruled.

### A-2. D-9 rows (b)–(d) recalibration — follow-on, gated on A-1 acceptance

Only after the ruling is accepted, and only for rows ruled *supported*: replace the stale
`INSTRUMENT_UNSUPPORTED` labels with fixtures pinned under the guards standing rule (both
halves: observed catching, observed failing when the subject is broken). Rows ruled
*unsupported* keep an explicit label citing the ruling — no fixture is written for a
measurement the instrument cannot make.

### A-3. N5 narrow re-review — new assignment, read-only

The corrected N5 endgame-contest result awaits its narrow re-review
(`docs/BACKLOG.md` §P1 N5). Author was `local_codex_1` (dormant; corrected handoff
`coordination/messages/local_codex_1/20260731T131500Z-20260730-n5-endgame-opponent-plant-contest-corrected-handoff.md`),
so you are separation-clean. Narrow scope only: verify the correction preserves
`NO_MATERIAL_CONTEST_OPPORTUNITY` — the twelve semantic tests, and that literal
post-birth ETA leaves the primary value (deny-plus-capture ceiling 11.99 per all
resident games, CI [8.73, 15.76], below the frozen 20-margin gate) unchanged. No
re-derivation of the full protocol, no new measurement.

### A-4. B3.11 narrow re-review — new assignment, read-only

The corrected owner-postmortem of game `896352129` (vs Dridriun) awaits re-review
(`docs/BACKLOG.md` B3.11; corrected handoff
`coordination/messages/local_codex_1/20260731T134500Z-20260731-dridriun-fruit-control-postmortem-corrected-handoff.md`;
same author, so separation-clean). Narrow scope: verify the correction — the opponent
harvested zero resident-created apples, capture was reachable but not realized — and
that the conclusion stays measurement-only (a read-only corpus precheck, no capability
change, no target or threshold).

### A-5 H3a exact-17-game trigger preflight — second portion, added 2026-08-14

Resume of your owner-priority assignment, task
`coordination/tasks/20260802-h3a-conditioned-value-unblock.md`, parked through the P0
arc. Cheap first step only: the exact-17-game trigger preflight over the recovered
public-frame and 5,100-decision reconstruction packages — does the workforce-pressure
condition actually fire on the archived treatment games? This is a **stop gate**: on
fail, publish the finding and the H3a route pauses for an owner read; on pass, A-6
opens. Read-only, no candidate, no Arena. Estimated hours, not days.

### A-6 H3a conditioned-value build — gated on A-5 pass

Only on an A-5 pass: freeze/build C1, the equality bridge, the three-arm runner
(pressure-conditioned treatment / identical-always-on / unchanged control), then one
6,144-task development panel. In scope first, because Phase B/C is blocked until they
are fixed: the locked substrate's 213 numeric-fruit alias crashes, the continued-RNG
divergence, and the empty `MSG ;` incompatibility. Original estimate 3–5 working days
to the full path; re-estimate at A-6 start. Development panel only — any Arena step is
a separate decision under `docs/STATE.md` §3.

**Ordering note:** A-1/A-2 stay first as the live item; A-3/A-4 are small read-only
fillers; A-5 may start whenever A-1 is waiting on review or acceptance. D89a-LI (the
owner's new low-priority banana-leak analytic programme, backlog §P3) is **not**
assigned to anyone and starts only on a fresh owner charter.

## Status updates (2026-08-14, post-issue)

- codex_1 C-1 ✅ (guards task closed on trunk); C-3 ✅ delivered
  (`UNRESOLVED`, strongly leaning `NOT_REPAIRABLE`) — **owner ruled 2026-08-14:**
  closure label `FOR_FURTHER_INVESTIGATION`, gate weakened not removed, route recorded
  as programme D89a-LI at low priority. C-2 (F1) blocked on the unmounted
  `medium_data` volume; archive unblock path issued.
- claude_1 A-1 claimed and in flight; A-5/A-6 added as the second portion.

## Retained by local_claude_1 (not assigned out)

- Era annex for the Aug-9-committed / Aug-12-stamped message paths (objection window
  passed silently; mail-audit report §Recommendations).
- `docs/PROMOTION-RUNBOOK.md` stale-identity refresh before any promotion cycle uses it.
- Arena authority and the live resident (agent 6614096 / submission 41129543).

## Not in scope this iteration without new owner action

H3a Phase B/C (blocked on substrate defects), CBF implementation (pending C-3 and an
owner decision), H10a-r1 / H10b-r1 (peer-gated / charter not frozen), H11a (paused
behind H3a).
