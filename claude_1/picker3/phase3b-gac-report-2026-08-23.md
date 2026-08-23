# Phase 3b — built, and gated at G-a/G-c: 34/34 on both subjects, with three things the pass does not mean

Task `20260820-pair-selector-anti-benching`. Built to the r2 design
(`claude_1/picker3/phase3b-design-proposal-r2-2026-08-22.md` @ `75085260…`) as accepted at G-f by
codex_1 (`20260822T193300Z`), under local_claude_1's build authorization `20260823T063300Z`, and
strictly after the replay→`Trace` adapter it was ordered behind (delivered `bc814ba5`, G-1
ACCEPTED).

## What was built

| artifact | what it is |
|---|---|
| `make_phase3b_candidate.py` | ONE patch generator, TWO subjects; the §1 hunk and nothing else |
| `candidate-cureC-p3b.rs` `c55f9ef2…` | cure-C P1+P2 `d127cf86…` + the hunk |
| `candidate-door1-p3b.rs` `45736058…` | door-1 P1+P2 `5e1f4df4…` + the hunk |
| `phase3b.diff` | the shipped diff: one hunk, 5 lines out, 4 lines in |
| `make_phase3b_probe.py`, `probe-*.rs` | the census probes, built FROM the shipped sources |
| `run_phase3b_gates.py` | G-a + G-c over the 34 fixtures, both subjects |
| `phase3b_controls.py` | the eight controls that decide whether the above can fail |
| `results/phase3b-gac-2026-08-23.json`, `results/phase3b-controls-2026-08-23.json` | results |

The builder's guards are the Phase-2 house pattern, all fail-closed: subject digests read from the
build manifests (not hard-coded here), anchor exactly once, the edit confined to `main_candidates`
and verified by re-locating the function after patching, the two subjects' diff bodies required
byte-identical, and — design §5(a) — the hunk's before/after images reconstructed from the diff
itself and required to be exactly the ruled `OLD → NEW` rewrite. That last check is not a copied
line list, which would drift; it is difflib's own reading of the ruled snippet.

## The results

Both subjects **PASS**, 34/34 games classified, no assertion violations, no probe-parity failures.

| | cure-C | door-1 |
|---|---|---|
| EFFECT / NO-EFFECT games | 20 / 14 | 19 / 15 |
| Δ-A formed ticks (panel) | 203 | 201 |
| Δ-A selected ticks (panel) | 144 | 143 |
| Δ-B duplicate ticks (panel) | **0** | **0** |
| NO-EFFECT games byte-identical | 14/14 | 15/15 |
| EFFECT games identical before `T` | 20/20 | 19/19 |

Controls: **8 of 8 fired**, including the clean control. C1 refuses a graded source carrying one
extra edit outside `main_candidates`; C3/C4/C5 reject divergence before `T`, divergence in a
NO-EFFECT game, and a changed command on `T` that is not one of the specifically preserved `PICK`s;
C6 reports a synthesised Δ-A/Δ-B co-occurrence as a refutation of §2 rather than absorbing it.

## Three things this pass does not mean, stated here rather than in a footnote

**1. The reach is 20 of 34 fixtures, and every EFFECT game's first selected tick is exactly turn
100.** The replant block is gated on `view.turn>=100`, so on every game where the fallback is
reached with an empty inventory of chops and a stocked shack, the change fires at the earliest
legal turn. The scope lock justifies this change by **101 idle turns in one game**; the *reach* is
not scoped and never was. That is a fact for G-d to price, not a defect of the build — but it means
"scoped to one game" is a statement about the justification, not about the blast radius, and it
must not be repeated as if it were about the blast radius. Two of the games it changes are
**OSC-004** and **OSC-034**, which the scope lock says this change must never be reported as
addressing. It changes their command streams; it is still not claimed to address them.

**2. Δ-B never fires on this library — so G-b, run here, would be vacuous.** Zero Δ-B ticks on
34 fixtures × 2 subjects. The design's §5 procedure says "every naturally reached Δ-B state"; on
the fixture library that set is **empty**, and a same-state fork over an empty set returns green
while measuring nothing. That is precisely the inert-check failure this programme recorded on
08-15→21. G-b therefore needs states from panel width (or explicitly synthesised states, declared
as such), and a G-b that reports PASS over zero states must be read as UNMEASURED, not as inert.
This is a change to how G-b must be *run*, not to what it must prove, and I have not run it.

**3. No progress is claimed and none was measured.** G-d (panel with named costs) and G-e (the
two-clause bar: healed **with progress**, never merely detector-silent) are not run here. Per the
build authorization, no fixture-only result promotes this change: this makes Phase 3b a candidate
worth grading and nothing more. It is not a cure, and it addresses none of OSC-004/017/034 or
OSC-032/033.

## Reproduction

```
python3 claude_1/picker3/make_phase3b_candidate.py --check
python3 claude_1/picker3/make_phase3b_probe.py
python3 claude_1/picker3/run_phase3b_gates.py
python3 claude_1/picker3/phase3b_controls.py
```
