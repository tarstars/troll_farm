# PEEK step 0b — the decline census answers the question, and it REVERSES my step-0 delivery

Task `20260822-peek-planner-target-map`, the coordinator's card of 2026-08-22T19:29:45Z
(extend the probe to log declines; probe only; no candidate edit). Built, run, and it settles
the question the fire table could not reach.

## Headline

**A widened trigger has a firing opportunity inside BOTH episodes, on every oscillating tick,
and the seam declines all of them for exactly one reason: the partner is not `WAIT` and a
detour existed.**

| episode (pinned pack) | window | in-window collisions the seam SAW | fires | decline reason |
|---|---|---|---|---|
| OSC-005, unit 2, cells (10,2)/(9,2) | **turns 7–18** | **5 at the partner block** (t8, 10, 12, 14, 16) + 2 early-exit rows at t18 | 0 | **all 5**: partner not `WAIT` **and** a detour existed |
| OSC-027, unit 2, cells (5,2)/(4,2) | **turns 3–24** | **10 at the partner block** (t4, 6, 8, … 22) | 0 | **all 10**: same |

Every other gate passes on every one of those rows: `legal=true`, `free=true`, `allowed=true`,
`index_ok=true`, `landing_forbidden=false`, occupant is neither a mover nor already swapped. The
shape is a **genuine pass-through** — `target_is_landing=false` (OSC-005 mover at (9,2) heading
for (2,2) through (8,2); OSC-027 mover at (4,2) heading for (1,2) through (3,2)) — and the BFS
distance strictly decreases across the landing (7→6 and 3→2). The blocker's command on every one
of those ticks is `CHOP`.

**So the busy-blocker half of R-1 is reachable after all**, and the integrator's standing doubt —
"even rev 1 never fired inside OSC-005's episode, so the widening may buy the 13 and none of
R-1's other half" — is **REFUTED on the mechanism**, not merely unconfirmed. Rev 1 indeed never
fires there; it declines fifteen times, at the one clause a widening would change.

## I must correct my own step-0 delivery, in full

My step-0 handoff (`…/20260822T193137Z-…-step0-handoff.md`, artifact
`claude_1/peek/step0-osc005-osc027-2026-08-22.md` at `agent/claude_1@c093e8e5`) concluded that
**"the partner-state relaxation is ruled OUT as the missing ingredient in both windows."** That
conclusion is **WRONG**, and so is the evidence I built it on.

**The cause: I read the wrong fixture pack.** All of this tooling loads
`claude_1/banana-restoration-r2/oscillation-library-**98628e98**/library/` — the digest-pinned
pack keyed to the subject bot `submitted-agent6593838-readable-no-orchard.rs`
(`fixture_harness.py:76`). I read `claude_1/banana-restoration-r2/oscillation-library/`, a
different pack from a different bot (`candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`)
on different maps. Same fixture ids, different games:

| | pinned pack (authoritative) | the pack I read |
|---|---|---|
| OSC-005 | m070 seat 1, unit 2, turns **7–18**, cells (10,2)/(9,2), blocker `CHOP` | m065 seat 1, turns 9–20, cells (8,1)/(9,1), blocker `WAIT` |
| OSC-027 | m066 seat 0, unit 2, turns **3–24**, cells (5,2)/(4,2) | m004 seat 0, turns 24–31, cells (8,2)/(9,2) |

Everything downstream of that read is void: the "blocker emits `WAIT` on 10 of 12 window turns"
claim for OSC-005, the "one window offered a WAIT partner, the other a busy partner, and neither
produced a fire" argument, the determinate negative it supported, and the OSC-027 turn-24
false-positive site (that turn belongs to the other pack's game).

**The correction I published against the coordinator was itself the error.** I told
`local_claude_1` their "turns 7–18" was wrong and that the fixture said 9–20. **Their figure was
right and mine was wrong.** The 32-versus-34-turn arithmetic I offered was arithmetic over the
wrong game.

This is my recorded failure mode — *a figure changing meaning at a boundary* — and the boundary
this time was a directory name that differs from the pinned one only by a digest suffix. What
survives is what did not depend on that read: the fire table records fires only and cannot answer
the question (both of us reached that independently), and the census is the instrument that can.

## What survives from step 0, checked again against the pinned pack

- **Both episodes genuinely reproduce on this base.** `regrade34-identity-2026-08-21.json` lists
  OSC-005 and OSC-027 among the champion's 11, that champion is byte-identical to swap R-1's base
  (both sha256 `547fa706…`), and the identity gate it used reads the same pinned pack this census
  does. So "the seam saw these collisions" is a fact about this world.
- **The fire table is structurally incapable of answering the card's question** — it logs fires,
  never declines. That is why this census exists.

## What was built, and what was NOT

**Probe only.** Two `eprintln!` rows added by `make_swap_candidate.py::patch_probe`, which the
delivery candidate never goes through:

- `cgauto/submissions/candidate-swap-r1.rs` — sha256 `bbbb75d3d3cfa9b5…`, **unchanged** from the
  G-1 package; `control-base.rs` and `control-swap-r1.rs` unchanged; only `probe-swap-r1.rs`
  differs (`build-manifest-2026-08-21.json` is the check).
- **Probe parity re-proven per fixture before any row was read** — the probe's command stream must
  equal the plain candidate's or the run aborts. It passed on all six fixtures.
- No candidate edit, no predicate, no planner-target map, no mover-side pass-through test.

**Two census sites, because one cannot see everything.** `reserved` starts as the cells of own
units that are *not* moving, so a landing held by an own unit that is itself a mover is unreserved
and the seam takes its early `continue` — that collision never reaches the partner block. A census
placed only at the partner block would have missed that class silently; `SW1COLL0` sits before the
early exit and catches it (it is what OSC-005's t18 and OSC-001's two early rows are).

## Corpus context, all six event-table fixtures

| fixture | episode | collisions in-window | fires in-window | in-window decline reasons |
|---|---|---|---|---|
| OSC-001 | 6–200, unit 0 | 4 | 1 (t7) | 2 early-exit (both units moving) |
| OSC-005 | 7–18, unit 2 | 12 | **0** | **5 × partner-not-WAIT-and-detour**, 2 early-exit |
| OSC-006 | 12–20, unit 2 | 18 | 9 | none — every partner-block row fired |
| OSC-011 | 26–32, unit 0 | 10 | 5 | none — every partner-block row fired |
| OSC-012 | 8–200, unit 0 | 2 | 1 (t9) | none |
| OSC-027 | 3–24, unit 2 | 20 | **0** | **10 × partner-not-WAIT-and-detour** |

The two fixtures R-1 is about are the two with in-window declines, and they decline for one
reason. That is as clean a separation as this corpus has produced.

## What this does NOT establish, stated plainly

1. **It does not prove a widened trigger would fire.** It proves the seam reaches the decision and
   declines at a named clause. Whether a widened predicate fires there is codex_1's step 2, and
   nothing here is a predicate.
2. **It does not prove firing would restore progress.** Suppressing or adding a fire changes every
   later tick; only a G-1/G-2 rerun measures outcome. The two-clause bar still applies.
3. **PEEK's two halves pull in opposite directions on exactly these rows — step 2 must resolve it.**
   The blocker is `CHOP`ping the tree it stands on, so its planner target is plausibly *its own
   cell*. The refusal rule the task record sketches — *do not swap a partner off a cell that is
   that partner's own current target* — would then **refuse** the very displacement the owner's
   swap-and-return wants here. The mover-side pass-through test (which needs no exception) passes
   on all fifteen rows; the partner-side fact may veto them. I am not resolving that, and I flag
   that this paragraph is reasoning about intent, not measurement: **no target map is built and
   none of these rows carries a partner target.** It is the first thing PEEK's construction has to
   answer, and the census now makes it a concrete question over fifteen recorded rows instead of a
   hypothetical.

## Reproduce

```
python3 claude_1/swap1/make_swap_candidate.py      # candidate + controls byte-identical; probe rebuilt
python3 claude_1/peek/decline_census.py            # parity gate, then the census
```

Outputs: `claude_1/peek/decline-census-2026-08-22.json` (every row, every reason, all six
fixtures), this report.
