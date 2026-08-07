# H1 opportunity-cost orchard activation gate protocol — DRAFT FOR INTEGRATOR REVIEW 2026-08-04

Status: **FROZEN PENDING INTEGRATOR ACK — Phase A landed, margins frozen, G1–G3 executed and
passed (results below). No G4 panel run before the integrator ack.**

Task: `20260804-h1-orchard-opportunity-cost-gate` (claim:
`coordination/messages/claude_1/20260804T134600Z-20260804-h1-orchard-opportunity-cost-gate-claim.md`).
Register: `claude_1/hypothesis-register/HYPOTHESIS-REGISTER-2026-08-04.md`, hypothesis 1.

## 1. Objective and hypothesis

Replace the secure orchard's static activation rule with a prospective opportunity-cost gate:
before the orchard wrapper overrides the starter, compare projected remaining orchard value
against the displaced inner starter task's value, and activate only when the orchard exceeds
it by a frozen margin M.

**H1 (falsifiable):** at some frozen margin M, the gated orchard retains the orchard's win
contribution (+38 wins per 640 games in the 8-leg night A/B) while shedding a material share
of its catastrophe contribution (+22 catastrophes per 640 games), for a net live gain above
the current +0.585 mean Arena-score point estimate (CI [−0.645, +1.815]).

Evidence base:

1. `chatgpt_1` audit `20260804-orchard-activation-species-audit`
   (`chatgpt_1/orchard-activation-species-audit-final-2026-08-04.json`): activations where an
   enemy could arrive before first bank ran **−52.2 mean margin** in the kept stratum vs
   **−10.2** in the would-be-blocked stratum; static idle-only and first-bank gates are
   rejected; the audit names the prospective opportunity-cost gate as the next plausible
   improvement and warns the needed values (inner task predicted cycle ETA, expected banked
   score, projected orchard harvests) **are not in replay output**, so the decisive test is
   closed-loop on fresh common seeds.
2. Live ablation 2026-08-03 plus `claude_1/orchard-code-cost/orchard-code-cost-report.md`:
   removing the orchard cost −2.03 rating live; the orchard camps in a small minority of
   games (~7 %), concentrated in 300-turn top-tier games. The orchard is worth keeping; only
   its worst activations are the target.

H1 is **rejected** if no margin arm achieves the G4 primary direction (section 5, gate G4).

## 2. Exact parent

- Source: `claude_1/e7a-incremental-simplification/candidate-r36-delete-orphaned-carry-total.rs`.
- Bytes: 55,799.
- SHA-256: `2caac7c6e71e8dcc613a2275fe8129cdf9aec2c1230e50f7dfdec79908528381`.
- Provenance: behaviour-exact with live E7a; round-22 checkpoint
  DEVELOPMENT_EXACT_EQUALITY_PASS 0/516 at the round-22 checkpoint; rounds 23–36 carry per-round replay gates and the r36-specific 516-task panel is requested and pending (20260804T090000Z).
- Auxiliary reference (bridge far side):
  `claude_1/orchard-code-cost/activation-disabled-reference.rs`, 62,581 bytes, SHA-256
  `8fc1b7f3499a407e5df546bbc688843c56c0f6e7d9382b18ba359592b586693d` — the parent lineage
  with the orchard activation test replaced by "never", command-identical to baseline on
  24/25 packet games (sole difference: the one game where the orchard actually activated).

All candidates are built from the r36 parent by a deterministic builder that verifies the
parent hash and every anchor's exact replacement count before writing output.

## 3. Instrumentation and arms

One code change, one tunable: at the activation decision site, compute
`projected_orchard_value − displaced_starter_value` and activate only if the difference
`> GATE_MARGIN`. Value definitions (inner candidate score for the starter task; orchard
cycle ETA and projected banked harvests from `can_activate`'s `OrchardCycle` estimates;
enemy ETA) are fixed by the Phase-A gate-design report and frozen with the margins.

| Arm | GATE_MARGIN | Expected behaviour |
|---|---|---|
| C0 (bridge) | `i32::MIN` | Gate always passes ⇒ command-identical to the r36 parent on all replay gates. Validates that instrumentation alone changes nothing. |
| A-inf (bridge) | `i32::MAX` | Gate never passes ⇒ command-identical to the activation-disabled reference on all replay gates. Closes the bridge from the other side. |
| M0 | 0 | Activate only when orchard ≥ displaced. Strictest arm. |
| M−128 | −128 | Lenient arm compensating the displaced side's deliberate repetition overestimate. |
| M−256 | −256 | Most lenient arm; brackets the design report's worked-example delta (−134). |

**Margins FROZEN 2026-08-04** from the Phase-A gate-design report
(`claude_1/h1-orchard-gate/gate-design-report.md`, SHA-256 `7c56baa18445946395e396f37b7294da3259c8748b7086879f66dbc7a4cde7eb`):
arms 0 / −128 / −256. Rationale: the displaced-side formula deliberately overestimates
(assumes the best chop cycle repeats forever), so useful margins are negative; no positive
arm is fielded. The values derive from the report's mechanics arithmetic (orchard ≤ 150
points; worked-example delta −134), not from the 1,280 audited games. No margin may be
revised after any G4 outcome is opened.

## 4. Endpoints (declared before any run)

- **Primary:** (a) catastrophic-loss count; (b) negative-margin mass (sum of negative
  per-game margins).
- **Secondary:** win count, mean game margin, mean development score.
- **Comparison arm:** C0 (= current orchard behaviour), paired per-seed.

## 5. Staged gates, in order

Each arm passes gates in order; a failure at any gate has the stated meaning and stops that
arm (section 6).

1. **G1 — static.** Builder anchors: parent SHA-256 matches section 2 and every replacement
   anchor occurs exactly the manifest count. Candidate rebuilds byte-identically from the
   builder. Standalone optimized compilation passes. Empty input exits cleanly.
   *Failure means:* construction defect; fix the builder, not the protocol.
2. **G2 — bridge equality.** C0 must be command-identical to the r36 parent on all replay
   gates: all ten frozen semantic fixtures, and all 7,234 command lines of the 25-game
   immutable public offline-parity packet, zero unknown updates, zero stderr. A-inf must be
   command-identical to the activation-disabled reference on the same gates.
   *Failure means:* the instrumentation is not behaviour-neutral (C0) or the gate does not
   actually control activation (A-inf); the value plumbing is wrong and no margin arm result
   would be interpretable.
3. **G3 — activation-rate sanity.** On the 25-game packet, report per-arm activation counts
   for M0/M+/M−. Pass criterion: no margin arm activates **more** than C0.
   *Failure means:* the value comparison is inverted or degenerate; back to Phase A.
4. **G4 — closed-loop paired development panel** on fresh common seeds, run by
   `local_codex_1` (integrator environment authority). All arms (C0, M0, M+, M− if present)
   on the identical seed set, paired per-seed against C0. Primary pass direction for a
   margin arm: **catastrophic losses strictly down vs C0 AND wins not materially down**
   (win count within noise of C0 on the paired panel); negative-margin mass down is the
   confirming primary. Secondary endpoints are reported, not gated.
   *Failure means:* that margin does not separate bad activations from good ones.
5. **G5 — disposition.** Any surviving arm is scored against the standing **≥ +1.0 rating
   bar** (`docs/APPROACH-REGISTER-2026-07-30.md`) before any Arena consideration. Clearing
   G4 alone earns a register update and possible follow-up panel, not an Arena cycle.

## 6. Stop rules

1. Any G1–G3 failure stops that arm; it may re-enter only as a new candidate restarting at G1.
2. If **all** margin arms fail G4's primary direction, **H1 is falsified**; record the result
   in the hypothesis register and move to H3 (pressured orchard abandonment), which attacks
   the same +22-catastrophe mass post-activation instead of pre-activation.
3. **No Arena mutation under this protocol at all.** G5 produces a disposition
   recommendation only; any Arena cycle is a separate owner-sequenced action through the
   controller.

## 7. Explicit non-goals

1. No species change: BANANA as mother rejected by the audit (roughly half throughput,
   sharply reduced survival margin); the bounded BANANA wood printer is H6, a separate
   architecture.
2. No eligibility relaxation (distance ≥ 11 → 9/10, Dormant window): that is H5.
3. No idle-only gate: rejected — 51/54 real activations would be suppressed; it is
   effectively orchard deletion, which already lost −2.03 live.
4. No static distance/first-bank threshold: rejected — the blocked stratum outperformed the
   kept stratum; arrival is not destruction.

## 8. Division of labour

- **Phase A (claude_1):** activation-site value analysis on the readable r36 source; gate
  design with exact anchors; margin derivation. Subagents read and draft; claude_1 verifies
  and freezes.
- **Phase B (claude_1):** this protocol, frozen after integrator review and before any
  candidate panel run; builders and G1–G3 execution.
- **Phase C (local_codex_1):** the G4 closed-loop paired panel on fresh common seeds and the
  G5 disposition, per integrator environment authority.

## 9. Safety boundary

Keep `rust/src/bin/yamo_orchard_live.rs` byte-exact at SHA-256 prefix `fff6669b`
(`fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`). Do not run formatters
on any locked source. No sealed ranges are opened; no intermediate step consumes an
untouched range. Write set: `claude_1/h1-orchard-gate/`, the task-id message namespace, and
the claude_1 status file — nothing else. No Arena, TestSession, or platform action.
