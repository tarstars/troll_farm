# BACKLOG — path to Legend top-3

Created 2026-07-27. Owner-ranked task list for the standing goal (`docs/STATE.md` §2:
rank ≤ 3 on a mature read + confirmation; bar ~28.11 at Phase 21). Every item cites its
evidence (`Dnnn`/`Phase n` = ledger vol 1; classes = `docs/CONSTRAINTS.md`). Re-rank only
from written evidence. One item in flight at a time; each ends with a ledger entry.

## Position summary (2026-07-27)

Resident `6561795` read 40–43/107 @ ~22.0 on 2026-07-23 (fresh-agent scoring); the
untouched original matured to 26.31 / rank 6, and same-code A/A proved fresh reads sit
3–4 points low. So the goal decomposes into: **(a) ~2–4 points of maturity recovery**
(free — requires only not churning) **plus (b) ~+2–4 points of real code strength**
(nothing transferable found since the +3.0 stack promotion on 07-17). The loss mechanism
is measured: anti-compounding catastrophic tail (D159 — leads +23.9 at t100 → −5.2 at
t225; 11% of games carry 58% of negative mass; 58% of losing opponents reach ≥3 workers),
rooted in production persistence during/after scaling (D101: top-3 reap 24.16% of created
crops, resident 0.94%; suppression already competitive).

## Tier 0 — free points and standing discipline (no code)

- **B0.1 ✅ DONE 2026-07-27** — passive read: resident 43/110 @ 21.97 (203 battles), bar
  MSz 28.22; 198 new replays, QA clean. **Key finding: the score is source-side frozen
  since 07-23 (no ladder recomputation; 6 battles in 4 days) — the passive-maturity lever
  is much weaker than assumed. Code strength must carry essentially the whole +6.25 gap.**
- **B0.2 ✅ DONE 2026-07-27** — cleanup executed (SDD, all reviews clean): 22 worktrees
  removed, debug cache cleared + cap rule, 683 files / 1.04 GB migrated + symlinked, YT
  dead dir removed, 425 MB mirror uploaded md5-verified. Repo 23.5 → 2.76 GB.
- **B0.3 No-churn rule stays absolute** — no arena write until a candidate passes the
  promotion protocol (B4.1). Every failed trial costs ~2–4 points of standing for days.
  [class (g), fresh-vs-mature]

## Tier 1 — declared next experiments (cheap, bounded, evidence-backed)

- **B1.1 ✅ DONE 2026-07-27 (D167a)** — acquisition paths ARE regular: **BANK_SEED
  frozen-eligible** (135/135 local; 71.4% top-5 field, 4/5 agents, both seats; all frozen
  gates passed, no tuning). OPPONENT_DERIVED closed as a class. Bonus discovery: top agents
  pre-carry seeds through suppression (22/49 cycles) — the resident never does (0/1,024).
- **B1.2 ✅ DONE 2026-07-27 (D168a) — kill rule fired.** Both bounded BANK_SEED options
  failed value decisively (post-return −6.73 [−8.40,−4.08]; pre-carry −8.21; worst
  family −17.11) with mechanism and integrity fully clean. **Hand-written successor
  controllers are closed**; the motif enters B2.1 as a rollout-valued option only.
  Bonus fact for B2.1: carry is empty at 100% of P→S entries — pre-carry preconditions
  never arm on resident trajectories. Tier 1 is complete. [D168; vol 2]

## Tier 2 — the big bet: resident-native options + closed-loop learning

The only levers with measured headroom ≥ the gap are hindsight oracles over
option/joint-assignment spaces (D97 +36.9; D107 four-use +35.2; D144 combined +42.6;
D152 exact-second +36.8 on actives; D162 resident-native envelope **+12.7 [+9.0,+16.3]
with zero regressions**). Every *offline* selector over them failed (best D142b +3.06,
under bar); the never-executed branch is closed-loop optimization on the **resident**
substrate with a family-robust objective (skipped-D109 question, D157 audit; D158's
invalidation was substrate-only). Prereq chain, each gate preregistered:

- **B2.1 ✅ DONE 2026-07-27 (D169a) — PASS, gate cleared cleanly.** Envelope over
  {OPT_RETURN, 3× D163 resource options, all ± B3.1-trigger arming}: **+10.671 mean,
  CI [+9.420, +11.922], 65% improved, 0 regressions**, tails better than control, 100%
  coverage. Every option negative always-on — value is pure per-game selection. No
  D169b needed (all six PASS conditions held on the first pass). 🛑 Per
  `docs/STATE.md`, Tier-2 is now paused for Fable-tier D170 authoring — do not proceed
  to B2.2 with a cheaper model.
- **B2.2 → D170 (Fable-authored): Family-robust closed-loop training on the D169
  interface** *(design pending; then 3–5 sessions + YT)*
  Recurrent policy over the B2.1 options with exact-resident action zero; objective =
  paired margin with group-DRO/worst-family term and own-score protection (D109's
  rotation, r=−0.014 across panels, is the failure this objective targets). Selection by
  independent-block leave-one-out only (D134 — fit statistics anti-predict transfer).
  **Gates:** same-panel dominance over exact resident (D158 rule); fresh-block +≥2 with
  all families ≥ −1; latency p95 < 50 ms in the deployable form (V5 buffer pattern);
  ≤100 kB source. **Kill:** two consecutive objective variants fail fresh-block → close
  the program and hold at Tier 0/3.
- **B2.3 Controlled arena trial** *(only after B2.2 passes everything, via B4.1)*

## Tier 3 — execution-class diagnostics (historically the only transferrers)

- **B3.1 ✅ DONE 2026-07-27** — signature replicates independently (19/192, 57.9% of
  negative mass); the endgame switch has NO coverage bug (fires at the earliest turn its
  behind-AND design permits; retuning closed — CONSTRAINTS §(f)). Surviving output: an
  observable early-warning trigger — opponent scaling past 2 workers precedes the
  crossover by 42–125 turns in 84% of catastrophes (83% of mass). **Feeds B2.1 as an
  activation-conditioning signal**, not a switch retune.
- **B3.2 Execution-waste sweep on the freshest corpus** *(1 session after B0.1)*
  Motion/idle/waste audit on new replays (the 07-16 audit found zero motion failures —
  rerun on current field only if B0.1 shows new opponents/behaviors). Cheap; occasional
  +0.5–1 candidates of the class that actually transfers.

## Tier 4 — arena protocol (standing, entered only by qualified candidates)

- **B4.1 Promotion protocol v3** — capacity A/A (control must reconverge within noise of
  its prior bracket) → candidate submit → mandatory +20/+35/+50-minute reads → delta vs
  same-window control with the frozen bands (≥ +0.5 KEEP, ≤ −0.5 revert) → restore exact
  resident on any failure. [arena-queue policy v2 + 07-16/07-18 Legend amendments]
- **B4.2 Bar tracking** — with each authorized read, record rank-3 score and top-3 battle
  counts (maturity context) in STATE §1.

## Tier 5 — infrastructure (pull in only when it blocks)

- **B5.1 Green workspace build** — feature-gate or fix the broken research bin
  (`d35c_provenance_competitive_bundle_oracle_impl`, 311 errors) so
  `cargo test --workspace` gates work again.
- **B5.2 YT tranche mirror** — part of B0.2 (plan Task 5).

## Recommended order

B0.1 → B1.1 → (B1.2 if warranted) → B2.1 gate → B2.2 → B2.3; B0.2 and B3.1 interleave as
fillers; B0.3/B4.x standing. Honest odds, **revised 2026-07-27 after B0.1**: the maturity
lever is largely dead — the ladder recomputes fresh-agent scores rarely (score frozen 4+
days), so visible-rank recovery cannot be assumed from waiting. Top-3 requires B2 to
succeed where thirty-odd offline selectors failed — the closed-loop objective is the one
untested lever the evidence still permits — and any promoted candidate must additionally
survive the same slow-recompute regime (mature reads will take days, reinforcing B0.3's
no-churn rule).
