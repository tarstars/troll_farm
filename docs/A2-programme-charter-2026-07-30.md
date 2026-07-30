# A2 — Architecture-2 programme charter

Authorized by the owner 2026-07-30 ("yes, build it"). Author: `claude_1` (integrator).
Integrator recommendation of record was to **hold** pending N1/N3; the owner elected to
build. N3's renewable-base question is therefore **folded into Phase 0** rather than used
as a pre-gate — building starts immediately, and the one question that could make the
design target physically impossible gets answered in the first phase instead of never.

## Mission

Build a **new bot**, from scratch, around the coupled economy the field's strong agents run
— while the resident keeps the ladder slot at zero risk. The resident is not modified,
not retired, and not touched by this programme.

Target, stated as **behavioural invariants** rather than imitation of any named bot:

| invariant | measured field reference | resident today |
|---|---|---|
| harvest-capable labour | only 9.5% of top-5 trained workers have `harvest_power 0` | **100%** are incapable |
| own-crop reap rate | 15–29% (top cohort) | **0.9%** |
| concurrent live crops | ~5–6 held | ~2, and 98.97% self-chopped before fruiting |
| servicing ratio (crops ÷ capable workers) | 2.5–3.0 | ≈0 |
| bills funded from earned currency | 66%, of which 76% fruit | ~0 earned; hard-capped at 2 workers |
| suppression | retained alongside production | already competitive — **keep it** |

Explicitly **not** a target: copying a named bot's parameters. Prose postmortems are intent,
not implementation (H5), and B4.4's tempo figures are under verification by N2 — do not
hard-code "plant at turn 21–29" or any other cohort number until N2 clears it.

## Hard constraints (from mechanics, not preference)

50 ms/turn and ≤100 kB single-file source at submission; carry capacity is frequently 1;
**no cross-player blocking exists** (`docs/mechanics.md:42-45` — do not design around it);
and the tree population on a map is **finite**, which is exactly why Phase 0 must settle
whether a renewable base is even possible (H1: worker 4 affordable in 0/220 games because
credited resources are a one-time windfall).

## Phases and gates

Milestone gates 1–5 are adopted verbatim from `chatgpt_1`'s review (§H2) and are
preregistered. Each phase ends with a ledger entry and an explicit per-gate verdict.

**Phase 0 — feasibility and harness (two parallel workstreams).**
- **0a. Renewable-base feasibility (= N3).** From the corpus: does a genuinely
  self-sustaining resource loop exist on these maps, or does the top cohort merely consume a
  larger windfall faster? Deliver the per-map ceiling on sustainable crop throughput and the
  turn by which a fruit-funded third worker is reachable. **K1 (kill): if no renewable base
  exists, the design target is impossible — stop the programme and report.**
- **0b. Referee and evaluation parity.** A new bot needs the same measurement rig the
  resident's experiments use: paired panels against the 8-family opponent set, both seats,
  byte-identical thread repeats, the six waste detectors, and the promotion tooling. Prove
  parity by reproducing a known resident result before trusting any A2 number.

**Phase 0b status, 2026-07-30: QUALIFIED (review acknowledgement pending).** The locked
referee path reproduces the known legacy result exactly, is byte-identical across one and
20 threads, zero-gates critical/unclassified errors, and covers all 2,048+2,048
trajectories with all six detectors. Continued referee RNG changes 1,781/2,048
trajectories, so Phase 1 must use only this path and fresh preregistered ranges.

**Phase 1 — economy skeleton.** Plant, harvest, bank, and fund a third worker in one
closed-loop scheduler. **Semantic clarification from the owner, 2026-07-30:** early
planting establishes and partially renews an orchard; late planting converts accumulated
fruit into wood. These are complementary phases, not contradictory planting-time claims.
Phase 0a found the population-level base **sub-critical** (median R≈0.75), so the design
may exploit partial renewal but must not assume indefinite self-replacement; it must also
convert the finite endowment before the game ends. Measured targets to aim at:
**worker 3 by turn 34–106** (top-5 earliest/median), **worker 4 by turn 55–137**, with
self-planted crops carrying **37–50%** of the bill currency and the endowment's share
*falling* from ~40% to ~27% as the game runs.
**Gate: fruit-funded worker 3 in ≥40% of fresh-map games by turn ~110** (= amended K1),
plus non-zero own-crop reap.

**Phase 1 also inherits a hard requirement from D174a:** the top cohort's mined iron rises
from **5.99** by worker 3 to **16.05** by worker 4 — iron acquisition *scales with roster*.
The resident's mining is gated off entirely at `own_units < 2`, which would be **fatal** in
A2. A2 must mine throughout, and opportunistically (D174a proved dedicated mining detours
are harmful: −10.76).

**Phase 2 — parity with the resident at equal roster.** **Gate: match the resident on the
same panel at 2v2 within noise, with tail safety no worse** (catastrophes ≤, negative mass
≤1.05×). A2 that cannot equal the resident at equal roster has no path.

**Phase 3 — scale survival.** **Gate: beat the resident's own record against 3- and
4-worker opponents** (its baseline: −37.1 margin at 2v3, 5.0% wins at 2v4+).

**Phase 4 — same-panel dominance.** **Gate: strictly dominate the resident on the shared
panel**, then deployability (int8/slim ≤100 kB, warm p95 ≤20 ms).

**Phase 5 — arena.** Runs under the **2026-07-30 standing authorization** (`docs/STATE.md`
§3): no separate per-candidate permission is needed, but the substance is unchanged — a
**QUALIFIED** verdict from Phase 4's frozen gates, expected gain above the arena noise band,
the full `docs/PROMOTION-RUNBOOK.md` with its capacity A/A phase, and owner notification
before and after. The no-churn *evidence* still governs the decision even though it no
longer governs the permission.

## Kill rules (preregistered — a programme without these is how months disappear)

- **K1 — AMENDED 2026-07-30 after Phase 0a, with the original recorded as an error.**
  *Original:* "Phase 0a finds no renewable base → stop." Phase 0a found **no reliable
  population-level self-replacement** — reproduction ratio median 0.75 even for the top
  five, only 1.2% of their games reaching full self-replacement, and tree populations
  collapsing from ~16 to 7 for every cohort. This does not deny the value of early orchard
  establishment or partial renewal, and it says nothing against separate late
  fruit-to-wood conversion.
  Read literally the original rule fires. It was **mis-specified by the integrator**: it
  assumed renewal was the necessary condition for reaching 3–4 workers, when the measured
  necessary condition is **conversion efficiency of a finite endowment**. The top five fund
  a third worker in **75.6%** of games and a fourth in **41.6%**, with their own plantings
  supplying **37.2%** and **49.7%** of that currency — the target is demonstrably reachable
  from a depleting base. *Amended rule:* **if Phase 1 cannot convert the endowment into a
  fruit-funded third worker in ≥ 40% of fresh-map games by turn ~110, stop** (references:
  top-5 75.6% by median turn 106; ranks 6–20 29.7% by median turn 85; resident 0/242, ever).
- **K2.** Phase 2 not reached within **6 working sessions** of Phase 1 starting → stop and
  reassess with the owner. Not a failure verdict; a budget circuit-breaker.
- **K3.** Phase 2 gate fails after two design iterations → stop. Equal-roster parity is the
  floor, not a stretch.
- **K4.** Phase 3 shows no improvement over the resident's scale-asymmetry record → the
  economy is not buying what it was built to buy → stop.
- **K5.** Any phase whose honest value estimate falls below **+1.0 rating** for the
  remaining work → stop (the standing bar; this week's evidence: −26.44, −10.76, −2.49,
  +0.045).

Kill = successful outcome. Record it and stop; do not tune around it.

## What is reused, and what is off-limits

**Reuse:** the referee-exact simulator, the 8-family panel, the 9,082-game corpus, the
waste-sweep detectors, `check_external_storage.py`, the slimming pipeline, and the
promotion runbook.

**Off-limits:** `rust/src/bin/yamo_orchard_live.rs` (byte-sacred, SHA `fff6669b`, and A2
must not import `troll_farm::resident_policy` except as a *control*); `cgauto/api_submit.py`
and `cgauto/submissions/*`; sealed ranges (9,844,200–215; the official-map holdout; the 11
sealed D164 games; 9,852,000–063; 9,857,000–127); `data/raw/games/` and the 05:17 cron. No
formatters over `rust/src/bin/` or `cgauto/`. New A2 seed ranges are declared per phase and
never reused for selection.

## Relationship to the re-scoped goal

The goal (2026-07-30) is a **mature score ≥ 25.40**, interim checkpoint 24.70. A2 is
**optional upside** against that target, not required by it — N1 may show maturity alone
covers much of the +3.64. A2 is authorized on its own merits, and if N1 delivers the target
without it, that is a good outcome for the project and does not retroactively justify
stopping A2 mid-flight; the K-rules govern that, not the score.

## Structure

Natural multi-agent programme: `local_codex_1` integrates and owns the gates following
the owner's 2026-07-30 handover; `claude_1` is offline. Workstreams use `agent/<id>`
branches with handoffs. Experiment ids `A2-0a`, `A2-0b`, `A2-1`, … each require their own
frozen protocol before execution.
