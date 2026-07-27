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

- **B1.1 D167: successor-job acquisition-path recovery** *(1 session, local, consumed maps)*
  Recover the seed-acquisition paths behind the 135 natural local PLANT returns and the
  field PLANT returns from the immutable D164 snapshot; freeze observable semantic job
  classes (KEEP / acquire-and-PLANT / own-crop HARVEST) only if broad and distinct from
  D87/D89. **Kill rule:** heterogeneous paths → close hand-written controllers for good
  and go to B2. [D166 decision; class (a)/(e) guards]
- **B1.2 Trajectory-conditioned successor-job value, resident-backed short rollouts**
  *(1–2 sessions; only if B1.1 freezes classes)* Offline, bounded-horizon (16–32 turn)
  rollout value over exact resident KEEP at P→S transition states — value computed at
  decision time, sidestepping the D153 fitted-value fold-transfer failure. **Kill rule:**
  held-block value < +2 or family floor < −3 → record and stop; do not tune. [D166;
  classes (b)/(f)]

## Tier 2 — the big bet: resident-native options + closed-loop learning

The only levers with measured headroom ≥ the gap are hindsight oracles over
option/joint-assignment spaces (D97 +36.9; D107 four-use +35.2; D144 combined +42.6;
D152 exact-second +36.8 on actives; D162 resident-native envelope **+12.7 [+9.0,+16.3]
with zero regressions**). Every *offline* selector over them failed (best D142b +3.06,
under bar); the never-executed branch is closed-loop optimization on the **resident**
substrate with a family-robust objective (skipped-D109 question, D157 audit; D158's
invalidation was substrate-only). Prereq chain, each gate preregistered:

- **B2.1 Resident-native option interface + headroom audit** *(2–3 sessions)*
  Define the option vocabulary at the resident's natural job boundaries (successor jobs
  from B1.1 + D162-style bounded reserve/route/protect + joint two-worker assignments per
  D97 semantics, rebuilt resident-anchored per the D158/D161 substrate rule). Include the
  B3.1 trigger — observed opponent scaling past 2 workers, 42–125 turns of lead time in
  84% of catastrophes — as an activation-conditioning feature of the interface. Measure
  the crop-safe hindsight envelope on paired local maps, both seats, eight families.
  **Gate:** envelope ≥ +10 mean with no negative family and clean tails (D162 achieved
  +12.7 on a narrower vocabulary). **Kill:** < +5 → the class is dead; fall back to
  Tier 3 + maturity.
- **B2.2 Family-robust closed-loop training on that interface** *(3–5 sessions + YT)*
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
