# D-9 calibration — `banana_before_train` does not measure TRAIN displacement

- Date: 2026-08-08
- Phase 1 item 1, `docs/HARDENING-PLAN-CONSOLIDATED-2026-08-07.md`
- Task: `20260807-detector-semantics-repair` (taken from `local_codex_1` 2026-08-07)
- Analyst: `local_claude_1`. **Read-only.** No detector edited, no gate changed, no games run,
  no candidate, no host surface, no Arena action.
- Input: `local_claude_1/verification/local_claude_1-floor-selftest-result-2026-08-07.json`,
  SHA-256 `322895ee57ae…` (240-game parent-vs-parent floor self-test, parent `a8eb3b2b`)
- Reproduce: `python3 cgauto/analyze_d9_calibration.py [--json]`
- Tests: `tests/test_analyze_d9_calibration.py` (8)

## Verdict: `MISCALIBRATED_RETIRE_OR_REPAIR`

D-9's `banana_before_train` clause fires **196 times across 74 games in a run where TRAIN
displacement is zero by construction.** Every one of its paired clauses — the ones that
actually observe displacement — correctly fired zero times in the same run.

## Why the run settles the question

The floor self-test judges the parent **against itself** (verified: `candidate == parent` in
all 240 games). A bot cannot displace its own TRAIN relative to itself: it trains on the same
turn, with the same stats tuple, as the reference. Every D-9 episode in this run is therefore
a false positive by construction — not by argument.

The paired clauses were genuinely enabled, so their silence is a real measurement rather than
an artifact of a disabled code path: `fuzz_panel.eval_p1` forwards `parent_cmds` into
`td.run_all`, which passes it to `detect_d9` (`trace_detectors.py:1231-1237`).

| clause | kind | episodes |
|---|---|---:|
| `banana_before_train` | unpaired proxy | **196** |
| `train_late` | paired, observes displacement | 0 |
| `train_missing` | paired, observes displacement | 0 |
| `train_stats_differ` | paired, observes displacement | 0 |

## What the proxy is actually detecting

The 196 episodes split **98 `PICK` / 98 `PLANT`** — exactly paired. That is the resident's own
shack-ring orchard (`rust/src/bin/yamo_orchard_live.rs:1193`): pick a banana from the shack,
plant it in the ring near our own base. Designed, deliberate behaviour that has shipped in
every submission this project has made.

The clause reads spec A10 literally: any `PLANT`/`PICK … BANANA` before the candidate's own
TRAIN while it holds one unit. It never consults the parent. Its premise is that banana work
before TRAIN must have delayed TRAIN — and that premise is false, because the parent does
exactly this banana work and trains at precisely the turn it would have anyway.

## Consequence for the gate

**D-9 is the single largest source of the broken floor. Retiring it alone takes the floor from
118 blocking games to 46 — a 61% reduction.**

| detector | episodes | games | note |
|---|---:|---:|---|
| D-9 | 196 | 74 | miscalibrated, above |
| D-1 | 35 | 32 | real; D1-A 34/35 has an untried memoryless guard |
| D-6 | 15 | 9 | |
| D-4 | 6 | 6 | real; single-door bank serialisation, localised |
| D-5 | 1 | 1 | |
| D-2 | 0 | 0 | **UNPROVEN — never fired** |
| D-3 | 0 | 0 | **UNPROVEN — never fired** |
| D-7 | 0 | 0 | **UNPROVEN — never fired** |
| D-8 | 0 | 0 | **UNPROVEN — never fired** |

This closes Phase 1 item 1 and supplies item 3's evidence: four detectors have never fired
across 240 games. They are `UNPROVEN`, not passing — nothing in this run shows they can fire
at all. Note that **D-7 belongs on that list too**; the consolidated plan named only
D-2/D-3/D-8.

## Recommended repair, for review — not applied

Retire the `banana_before_train` clause and let D-9 keep only its paired clauses, which
measure the thing D-9 is named for and are demonstrably correct on this panel (zero false
positives where zero is the truth).

The alternative — keeping the proxy but exempting behaviour the parent reproduces — is
**rejected**: it is exactly the round-6 ROOT-A parent-differential gate that the owner removed
on 2026-08-06 under the raw/absolute ruling. The repair must make the detector correct, not
reintroduce an exemption.

Retiring it does not weaken displacement coverage, because the paired clauses already cover
`train_late`, `train_missing` and `train_stats_differ` directly. It removes a proxy for
displacement while keeping displacement itself.

## Boundaries

I am the integrator and I run the host gates, so I am authoring an instrument I also use.
**No detector change I author may appear in a verdict until `claude_1` and `chatgpt_1` have
each independently reviewed it**, and the floor figures quoted here must be reproducible by a
second party on a different machine. This document proposes; it does not adopt.

This analysis reads one committed artifact. It does not establish that the remaining 46
blocking games are genuine parent defects — that is Phase 2's question, and D-1 in particular
remains unresolved.
