# Swap R-1 — the per-fire event table, and why the ruling's first predicate is INVERTED

Task `20260821-swap-r1-cure`. Written to codex_1's remedy ruling
`codex_1/reviews/swap-r1-g1-remedy-ruling-2026-08-21.md`, which BLOCKS every candidate edit and
authorises exactly this diagnostic: extend the probe, publish a per-fire event table over
OSC-001/005/006/011/012/027, and propose the smallest stateless predicate that separates the two
repeated-pair fixtures from the working ones.

**Headline: I am not proposing pass-through viability. The table shows it is not merely
insufficient — on this corpus it is backwards.** It keeps all 27 OSC-006 dance fires and rejects
both clean working fires (OSC-005, OSC-012). A different, simpler predicate removes 98 of the 111
re-swaps at a cost I can state exactly; the remaining 13 are **not separable from the intended
behaviour by any fact the seam can see**, which is the widening case the ruling anticipated.

## What was built, and what was NOT

Probe only. `make_swap_candidate.py` gained one `eprintln!` appended to `FIRE_ROW`, which the
builder inserts into the **probe** and never into the delivery candidate.

- `cgauto/submissions/candidate-swap-r1.rs` — sha256 `bbbb75d3d3cfa9b5…`, **unchanged** from the
  G-1 package (`build-manifest-2026-08-21.json` is the check; both control files are unchanged
  too). The only rebuilt output that differs is `probe-swap-r1.rs`.
- New: `claude_1/swap1/g1_event_table.py` → `g1-event-table-2026-08-21.json` (36 fires).
- Probe parity is re-proven before any row is read: the probe's command stream must equal the
  plain candidate's, per fixture, or the run aborts. It passed on all six, and the full 34-fixture
  sweep was re-run against the new probe (`g1-sweep-probe-reverify-2026-08-21.json`): four gates
  PASS, ruling 4 still FAILS at 111, and the JSON is identical to the pinned
  `g1-sweep-2026-08-21.json` field for field once the new per-fire `seam` block is removed. The
  G-1 package's numbers therefore still stand exactly as delivered.

## The event table, in one screen

`vac` = the mover's next step from the landing leaves the partner's old cell.
`tgt=land` = the partner's cell IS the mover's final target. `rev` = the reverse-swap turn.

| fixture | turn | mover | cell → landing | target | vac | tgt=land | partner | partner cmd | path | rev |
|---|---|---|---|---|---|---|---|---|---|---|
| OSC-001 | 7 | 0 | (5,2)→(4,2) | (2,2) | yes | no | 2 | WAIT | YIELD | none |
| OSC-005 | 52 | 0 | (2,2)→(1,2) | (1,2) | **no** | **yes** | 2 | WAIT | YIELD | none |
| OSC-012 | 9 | 0 | (10,2)→(11,2) | (11,2) | **no** | **yes** | 2 | WAIT | YIELD | none |
| OSC-011 | 27–31 | 0/2 alt. | (8,4)↔(9,4) | (9,4) | no | yes | 2/0 | WAIT | YIELD | +1 each |
| OSC-011 | 33 | 0 | (9,4)→(8,4) | (8,2) | yes | no | 2 | WAIT | YIELD | none |
| OSC-006 | 2–28 | 0/2 alt. | (1,3)→(2,3) | (2,2) | **yes** | **no** | 2/0 | **CHOP** | NODETOUR | +1 each |
| OSC-027 | — | — | — | — | — | — | — | — | — | never fires |

## Finding 1 — pass-through viability is inverted here

`P1` (target beyond the cell **and** the next step vacates it) keeps **27/27** OSC-006 fires and
**0/1** in each of OSC-005 and OSC-012. Both intended fires are arrive-and-stay: the mover's final
target *is* the idle partner's cell, so it can never "pass through". Every OSC-006 dance fire, by
contrast, is a textbook pass-through — mover at (1,3), target (2,2), stepping onto (2,3) and
leaving it next tick — and P1 waves all 27 through. P2 and P3 (the weaker halves) behave the same
or do nothing: P3 keeps every recorded fire, because every fire already reduces the mover's BFS
distance, including all 27 in the dance.

The reason is visible in the table: **displacement, not progress, is what distinguishes the dance.**
Both OSC-006 trolls want (2,2); the swap only exchanges which of them stands adjacent to it.

## Finding 2 — 98 of the 111 re-swaps are the working-partner path, and that path fires nowhere else

Corpus-wide, over all 34 fixtures and all 52 fires, **every** no-detour (working-partner) fire is
one of OSC-006's 27. The yield path accounts for the other 25 fires across 15 fixtures.

The card's expectation for a displaced worker — back on its tree within 2 ticks — is not merely
untested here, it is **contradicted** where it was measured: OSC-006's 27 displaced CHOPs resume
after 29, 27, 27, 25, … 3 ticks. The displaced troll returns to the *cell* on the next tick (its
command is `MOVE … 2 3`) and is displaced again, so the work only restarts when the dance ends.

So `P5` — **fire only when the partner's command is WAIT** — drops all 27 OSC-006 fires, all 98 of
their re-swaps, and keeps every fire in OSC-001, OSC-005 and OSC-012. Its cost is exact and I am
not hiding it: it **deletes the entire displaces-real-work behaviour** from the accepted G-0
construction. On the recorded corpus that costs nothing measured, because the path has no other
occurrence; but it is a scope reduction of an accepted design, so it is codex_1's to rule on, not
mine to build. It is also not a cooldown and not a widening: `commands[u_index] == "WAIT"` is
already read at the seam today.

## Finding 3 — OSC-011's 13 re-swaps are NOT separable at the current seam

The remaining 13 re-swaps are OSC-011's alternating dance at turns 27–31. Grouping every fire by
the seam-visible fields the table records — vacates, target-is-landing, partner WAIT, partner verb,
path, detour existed, and both BFS distances — the OSC-011 dance fires land in **the same bucket**
as the OSC-005 and OSC-012 fires that must be kept:

```
vacates=False target_is_landing=True partner_was_wait=True partner_verb=WAIT
path=YIELD detour_existed=True bfs_from_mover_cell=1 bfs_from_landing=0
  OSC-005 t52  m=0 u=2   reverse=none   u next tick: WAIT
  OSC-011 t27  m=0 u=2   reverse=t28    u next tick: MOVE 2 9 4
  OSC-011 t28  m=2 u=0   reverse=t29    u next tick: MOVE 0 9 4
  OSC-011 t29  m=0 u=2   reverse=t30    u next tick: MOVE 2 9 4
  OSC-011 t30  m=2 u=0   reverse=t31    u next tick: MOVE 0 9 4
  OSC-011 t31  m=0 u=2   reverse=t33    u next tick: WAIT
  OSC-012 t9   m=0 u=2   reverse=none   u next tick: WAIT
```

(OSC-011's sixth fire, t33, is a clean non-repeating one and collides with OSC-001's.)

The claim's exact strength: **over every field this table records**, those fires are
indistinguishable, so no predicate over them can separate OSC-011 from OSC-005/012. It is not a
proof that no function of the whole `GameState` could — a predicate resting on board geometry or
on other units is not excluded — but none of the ruling's named candidates is such a function, and
I have not found one.

What *does* separate them is the fact the ruling already named as missing: **the partner's own
planner target.** In OSC-011 the displaced troll wants the contested cell (9,4) and moves straight
back for it; in OSC-005 and OSC-012 it stays `WAIT`. The right-hand column above is the evidence,
and it is worth exactly what it is: an **in-world consequence** of the swap, observed one tick
later, not a pre-swap fact and not proof the partner was stably idle. codex_1's warning holds —
`WAIT` is one tick's command, not stable idleness — and it cuts the way the ruling said: the seam
cannot tell a resting troll from one that is about to reclaim the cell.

## What I propose, and what I am not doing

1. **Do not build pass-through viability.** Finding 1 is the reason; it would keep the whole dance.
2. **Rule on `P5`** (yield path only), which is stateless, needs no new seam input, and removes
   98/111 re-swaps at the stated cost of deleting the working-partner path.
3. **The minimum seam-input widening, for the remaining 13**: the seam receives, for each own unit,
   the planner's intended target for that unit *even when its command this tick is `WAIT`* — one
   `BTreeMap<i32, Cell>` threaded from the planner, read-only. The predicate then is: *do not swap
   a partner off a cell that is that partner's own current target.* That is a **declared charter
   exception** and I have not built it; it needs the coordinator/owner before any candidate edit.
4. **No cooldown.** None was built and none is proposed.
5. **G-2 untouched.** No fixture grading was run or inferred. OSC-027 still never fires, so the
   clean working-partner return-to-work measure remains untested — and note that if `P5` is
   accepted, that measure becomes *vacuous* rather than untested, which codex_1 should weigh.

## Reproduce

```
python3 claude_1/swap1/make_swap_candidate.py     # candidate + controls byte-identical to the package
python3 claude_1/swap1/g1_event_table.py          # the table, the replay, the collision analysis
python3 claude_1/swap1/g1_sweep.py --json /tmp/reverify.json   # probe parity + inertness, all 34
```
