# Score-improvement hypothesis register — v2, re-prioritized 2026-08-04 evening

Supersedes `HYPOTHESIS-REGISTER-2026-08-04.md` (kept immutable). Trigger: the round-36
deployment cycle and the pre-mutation A/B legs added five settled 160-game ladder readings in
one day, and together they overturn the premise behind the v1 ordering.

## The evidence that forces re-prioritization

Every settled 160-game reading of the two behaviours to date:

| Behaviour | Readings (score @ rank) | Spread |
|---|---|---|
| Orchard (behaviour-exact family) | 25.30 @ 12 · 23.69 mean (4 night legs) · 23.56 @ 32 · 22.88 @ 32 · **22.81 @ 32 (r36, settled today)** | **2.49 points** |
| No-orchard | **24.76 @ 21 (today)** · 23.27 @ 34 · 23.11 mean (4 night legs) | 1.65 points |

1. **The r36 simplification claim is fully confirmed live**: 0/516 panel equality, exact
   platform source recovery at `2caac7c6…`, clean identity — the 55,799-byte bot is the
   resident, and behaviour-exactness survived its strongest possible test.
2. **The orchard's live value is no longer distinguishable from zero.** Pooled means are
   ~23.7 (orchard) vs ~23.4 (no-orchard) with within-group spread ±1.2; today a *no-orchard*
   leg (24.76 @ 21) out-scored four of five orchard readings. The −2.03 ablation result and
   the +25.30 first mature were each single draws from overlapping distributions.
3. **Therefore: single ladder reads resolve nothing smaller than ≈ ±1.5 points.** This is
   the binding constraint on the whole programme, and it re-orders it.

## Standing measurement rule (applies to every hypothesis below)

Effects < 1.5 points are decided on **paired development panels and paired A/B legs only**;
a single ladder read confirms or rejects nothing in that range. Arena cycles are reserved for
(a) qualification/equality checks and (b) candidates or bundles whose development-measured
effect is ≥ +1.5. This tightens the standing ≥ +1.0 bar to match demonstrated noise.

## Re-prioritized order

| P | H (v1 #) | Hypothesis | Why it moved |
|---|---|---|---|
| 1 | H6 (was 6) | **Banana wood-printer restoration (R2, assigned to claude_1)** | The only lever with multi-point development evidence (+162.3 own score). Big effects are now the only ladder-confirmable effects. ↑ |
| 2 | H2 (was 2) | **Catastrophe + variance census — scope widened**: all 13 settled legs, not just the 91 orchard-leg catastrophes. Must explain what drove 24.76-no-orchard vs 22.8-orchard days (pool composition? map mix? catastrophe clustering?) | Still free, and now also the instrument that tells us how much of the 2.5-point spread is reducible. Needs claim/assignment (integrator note 20260804T142132Z). |
| 3 | H4 (was 4) | **H3a pressure-conditioned denial** | Unaffected by the noise finding — dev-panel decidable, best-reviewed signal (DiD 0.606). Effectively P2 among bot changes. |
| 4 | H1 (was 1) | **Opportunity-cost gate — G4 dev panel only** | G1–G3 passed; G4 queued with integrator and cheap — run it. But the targetable live effect is a fraction of +0.585 (CI already crossing zero), below ladder resolution. Decision on dev endpoints (catastrophes/wins) only; ships, if ever, **bundled** with larger effects. ↓ |
| 5 | H7 (was 7) | Roster-conditioned denial intensity | Mechanism (break-even at opponent worker 3) untouched by the noise finding; pairs naturally with H3a. ↑ |
| 6 | H8 (was 8) | Oscillation episode breaker | 21 catastrophes persist in the r36 leg; if the census implicates oscillation lock-ins, this jumps. Census-gated. |
| 7 | H3 (was 3) | Pressured-orchard abandonment | Was built on "orchard = +2, trim its tail". With orchard value now ~0 ± noise, whether to *fix* or *drop* the orchard is an open question the census + H1-G4 must answer first. ↓ |
| 8 | H5 (was 5) | Orchard eligibility relaxation | Expanding a feature of unresolved sign is premature. ↓ |
| 9 | H9 | Second mother / camp scaling | Same contingency, plus the B3.10 ~4.8/game ceiling. |
| 10 | H10 | Second-troll timing audit | Unchanged; cheap, low expected value. |
| 11 | H11 | Mid-game idle harvest | Unchanged. |
| 12 | H12 | Port one measured opponent mechanism | Unchanged; last. |

## Immediate actions under v2

1. **H6/R2 becomes claude_1's next build focus** once H1-G4 is dispatched (it is already
   owner-assigned as `20260802-banana-restoration-r2`; acknowledgement still pending on my
   side — will ack and start under this priority).
2. **H2 census**: renewing the request that it be assigned (chatgpt_1 preferred — audit
   context) or released to claude_1 subagents; scope now includes the variance question.
3. **H1-G4**: proceeds as queued; interpretation rule updated per the measurement rule.
4. The orchard keep/drop question is explicitly **reopened** and parked pending H2 + H1-G4:
   current live resident keeps the orchard (it is the qualified equality lineage), and
   no-churn forbids flip-flopping on noise.
