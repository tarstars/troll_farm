# Phase 3 — why the anchor is idle on the detector-quiet-but-stalled turns

Task `20260820-pair-selector-anti-benching`. Discharges the deferral card published at
`coordination/messages/claude_1/20260820T202851Z-...-progress.md`: *measure, on the P1+P2
candidate, why the anchor unit's candidate list is empty on the detector-quiet-but-stalled turns.*

**Measurement only.** Nothing here proposes a change, and nothing here licenses extending P1 or
P2. The card's bar was a measurement before any further selector work; this supplies it.

## Headline

**The card's premise was wrong and the measurement corrects it. The list is never empty.**

On every idle turn of all four ruled fixtures, on both bases, the anchor's candidate list is
exactly **one** entry — the `WAIT` that `main_candidates` seeds it with. And it gets there by a
single route on **100% of those turns**: the `idle_regeneration && chops.is_empty()` fallback.

That fallback returns a **fresh** `vec![MoisanBot::wait()]` instead of extending the `out` it has
already built. On OSC-013 that discard is **not** harmless: on **101 of the 170** idle turns
`out` held **two real `PICK` candidates** and they were thrown away.

So the 170 turns are two different things, not one:

| turns | what the generator had | what it returned |
|---|---|---|
| 31–99 (69 turns) | nothing — `out` held only its own `WAIT` | the seeded `WAIT` |
| 100–200 (101 turns) | **two `PICK` candidates, score 7500 / 7499** | the seeded `WAIT` |

Both spans are contiguous and the split is exactly at turn 100, which is the `view.turn>=100`
guard on the safe-regeneration replant block that pushes those `PICK`s. Identical on both bases.

## What was measured, and by what instrument

Two steps, two probes, both `eprintln!`-only and both parity-gated against the uninstrumented
candidate's command stream.

**Step 1 — `idle_shape.py` → `idle-shape-2026-08-20.json`.** Re-reads the Phase-2 selector
probe's own `PS2CAND` rows. No new instrument. Buckets every window turn by the anchor's list
contents.

| fixture | employed | list is exactly the seeded `WAIT` | list empty | list has non-`WAIT` work |
|---|---|---|---|---|
| OSC-004 | 11 | 3 | 0 | 0 |
| OSC-013 | 17 | **170** | 0 | 0 |
| OSC-017 | 7 | 187 | 0 | 0 |
| OSC-034 | 4 | 90 | 0 | 0 |

Identical on `cureC-p1p2` and `door1-p1p2`. Every idle list has length exactly 1. The reader
carries a cross-check that must be 0 — a turn the selector benched while non-`WAIT` work was in
the list — and it is 0 everywhere, so this reader and `gate_bench.py` agree on which turns are
idle.

**Step 2 — `make_route_probe.py` + `route_census.py` → `route-census-2026-08-20.json`.** A new
tap one function further up, on the GENERATOR rather than the selector: five anchors, each
required to match exactly once or the build is refused. It names the return path of
`main_candidates` / `endgame_candidates` per unit per turn, plus what the generator saw.

    idle_routes  = {'main:IDLE_REGEN_FALLBACK': 3 / 170 / 187 / 90}     (100%, all four, both bases)
    predicates   = carried=0  free_cap=2  safe_regen=true  idle_regen=true
    sub-generators = chops=0  idle_harvest=0  bank=0
    discarded    = OSC-013 only: 2 x PICK target=Cell((2,1)) score=7500.0 / 7499.0, on 101 turns

The employed turns take `main:CHOPS` and `main:FULL_BANK`, so the route tap is live on more than
one path and is not a constant.

## Gates — each one fails the run rather than degrading it

1. **Parity** — both probes' command streams byte-identical to the uninstrumented candidate
   (`coverage.check_parity`), per fixture, per arm. This is what licenses reading the diagnostic
   rows as facts about the real binary.
2. **Coverage** — exactly one `PS3FINAL` row for the anchor on every turn of every window; no
   gaps, no duplicates. A hole would make every rate above wrong.
3. **Cross-probe agreement** — `PS3FINAL n`, read at `by_id.insert` in `commands()`, must equal
   the number of `PS2CAND` rows the *selector* probe logged for the same unit and turn. Two
   independent taps on one list; disagreement reports no route at all.
4. **One route per unit per turn** — a unit takes one return path; two rows would mean the tap is
   double-counting.
5. **Exact-once anchoring** — an anchor matching twice refuses the build instead of guessing.

All passed. `PS3FINAL n == PS2CAND count` on every turn of every fixture on both bases is the one
that matters most here: it is why "the generator's list" and "the list the selector saw" are the
same object and not two measurements glued together.

## What this does and does not establish

**Established.** The residual stall on these turns is **not a selector defect**. The selector is
handed a one-element list and returns the only element in it. P1 and P2 are doing what they were
built to do and are correctly untouched by this. On 69 of OSC-013's 170 idle turns, and on all of
OSC-004 / OSC-017 / OSC-034's idle turns, the generator genuinely produced nothing: no chop, no
idle-harvest, nothing carried to bank. On 101 turns it produced two `PICK`s and a lossy fallback
dropped them.

**NOT established, and not claimed.** That keeping those two `PICK`s would restore progress. That
would require them to be selected, to be legal, and to move the unit out of the cycle — none of
which is measured here, and the last one is the grader's bar, not the generator's. Nor is it
established that the discard is a defect at all: `idle_regeneration` may be deliberately
exclusive of the replant block. **Whether that fallback should extend `out` instead of replacing
it is a design question for the owner, and I am not answering it by building something.** The
programme's withdrawn `GENERATOR_GAP` claims of 2026-08-17 came from exactly this step — treating
a measured absence of work as a demonstrated cause — and this report stops before that line.

Also not claimed: anything about the other 235 non-deadlock turns, or about any fixture outside
the four ruled ones.

## Replay

    python3 claude_1/picker2/idle_shape.py        # step 1: what the list holds
    python3 claude_1/picker2/make_route_probe.py  # build the generator probes
    python3 claude_1/picker2/route_census.py      # step 2: which route, and what it saw

The Phase-2 battery (`run_gates.py`) is deliberately **unmodified** — codex_1 reproduced that
package as it stands, and Phase 3 does not perturb a reproduced artifact.

## Artifacts

- `claude_1/picker2/idle_shape.py`, `idle-shape-2026-08-20.json`
- `claude_1/picker2/make_route_probe.py`, `route-probe-manifest-2026-08-20.json`,
  `routeprobe-cureC-p1p2.rs`, `routeprobe-door1-p1p2.rs`
- `claude_1/picker2/route_census.py`, `route-census-2026-08-20.json`
