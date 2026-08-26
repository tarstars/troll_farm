# What "FIXED on the champion" meant before today, and what it means now

Card `20260821-episode-identity-regrade`, deliverable 4. For the owner, through local_claude_1.
Measurement and tooling only: **no bot changed, no case re-ruled.**

## The one-sentence version

Eight of the 34 oscillation fixtures were recorded as FIXED on the champion; with episode identity
enforced, **none of the eight survives, because the champion never plays the game those windows
were recorded in.** The tally does not go from 8 to 7 or 3 — it goes to **zero graded cures**, and
the honest replacement number is that the champion reproduces **11 of the 34** recorded episodes
and is NOT_FIXED on all 11.

## What the grader used to do

The harness rebuilt each fixture's map from provenance and refused a rebuild whose map differed —
and that was the whole of its identity check. It then played the champion on that map and asked,
over the **recorded window's turn bounds**, whether the detector was silent and whether the unit
made progress. On a fixture where the champion plays a different game, those turn bounds point at
whatever the champion happened to be doing at turns 12–20 of *its* game. If the champion's troll
was busy elsewhere, the detector was silent and the unit made progress, and the row said FIXED.

That is what those eight rows were. Not a lie, not a bug in the fix; a question asked of the wrong
game.

## What it does now

Two frozen facts must both hold before a single recorded turn bound is read:

1. the command line the library froze for every turn of the window equals the replay's, and
2. the board at the window's first turn equals the frozen `world_state_at_entry`.

Neither alone is enough. On OSC-032 every recorded line is `WAIT`, so a completely different game
passes (1) — the controls record that the champion passes the command half on OSC-032 with 0
mismatches and is caught only by the board. A fixture that fails either is graded
**`NOT_REPRODUCIBLE_ON_BASE`**: never FIXED, never NOT_FIXED, because both words are claims about
a window this run does not contain. A fixture whose entry state cannot even be decoded fails the
same way, closed.

## The numbers

| | before the gate | with identity enforced |
|---|---|---|
| FIXED | 8 | **0** |
| NOT_FIXED | 26 | 11 |
| NOT_REPRODUCIBLE_ON_BASE | — | **23** |

The 23 break down as 18 caught by **both** halves, 3 by the window commands alone and **2 by the
entry board alone** — and those last two are **OSC-032 and OSC-033**, the pair that motivated the
card. A command-only gate would have waved through exactly the cases this was built for. All eight former
FIXEDs are among them, and seven of the eight differ on *every* frozen command line in the window
(OSC-034 on 4 of 94). The champion reproduces exactly OSC-001, 002, 005, 012, 013, 017, 021, 024,
026, 027, 030 — the same 11 local_claude_1 named, arrived at independently here through the
harness rather than through the re-grade script.

Each row also carries the real-end annotation from the accepted `20260821-p4-stalls-real-end-regrade`
artifact (the frozen `has_stalled` end turn and the conservative grace-only bound), read rather
than recomputed. It is an annotation; it changes no verdict here.

## What this costs, and what it does not

- **It does not say the champion is worse.** It says eight of its recorded cures were never
  measured. The right reading is "unmeasured", not "regressed".
- **It does not re-rule anything.** The 18 BUG, the six BUG and the OSC-032/033 disposition are
  the owner's.
- **It does bite on live work.** Cure α's G-2 expects "005/027/012/001 → FIXED"; all four
  reproduce on the champion, so that gate can still be read — with the standing caveat that α
  never fires on 027 at all. The anti-benching Phase 3a targets 004/013/017/034: **013 and 017
  reproduce; 004 and 034 do not** and must be reported NOT_REPRODUCIBLE rather than diagnosed.
- **It leaves one structural question open, which is the owner's:** 23 of the 34 fixtures can no
  longer be measured on the champion at all. Re-freezing the oscillation library on the champion
  would restore them; it would also retire the recorded evidence base these cases were ruled on.
  I am not proposing it here — local_claude_1 raised it and it is the owner's call.

## Reproduce

```
python3 claude_1/t1/fixture_harness.py --self-test          # 17 cases, gate controls included
python3 claude_1/regrade2/identity_gate_controls.py         # 11/11, G-1 byte-equivalence + G-2
python3 claude_1/regrade2/regrade34.py                      # both arms, the side-by-side table
```
