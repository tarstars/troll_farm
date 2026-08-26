# Gate G-P — the NARRATE instrument plays swap R-1's game: **34/34 byte-identical, 0 telemetry errors**

**Task:** `20260823-narrate-real-game-telemetry`. **Ruling built to:** codex_1 construction **r3**,
`20260823T070405Z` (`agent/codex_1@ef12a455`). **Author:** claude_1, 2026-08-23.

| artifact | sha256 |
|---|---|
| `claude_1/narrate1/instrument-swap-r1-narrate-v2.rs` | `aaebc503cc2660e920d45858767c6932575324085c93ef9345906f683b5a9271` |
| `claude_1/narrate1/run_gp_parity.py` | the gate |
| `claude_1/narrate1/gp_controls.py` | the controls that prove the gate can fail |
| `claude_1/narrate1/results/gp-parity-2026-08-23.json` | `c1ff34b030e460cca8b2156d6b08eb96eddb5307a4cb29b6e871b7cc634a3a05` |
| `claude_1/narrate1/results/gp-controls-2026-08-23.json` | `4521843c801207a78fb1073a3660d72c478129e29645a1b8a407ed7bbf643db2` |

**Base, unedited:** `cgauto/submissions/candidate-swap-r1.rs`, sha256
`bbbb75d3d3cfa9b5de05fdc68785fd2b2fb2de18d04344e021233ada26dc7fc3` — verified unchanged after the
build; the instrument is a separate file.

## 1. Result

```
34 fixtures, both arms re-run through the same fuzz_panel referee from the same frozen provenance
byte-identical after removing the complete MSG token : 34 / 34
telemetry errors (grammar, roster, ordering, alignment): 0
verdict: PASS
```

**The comparison is not trivially true.** The base emits **1** `MSG` token per game; the instrument
emits **200**, one on each of the 200 replayed turns. 199 extra tokens per fixture are removed and
what remains is identical byte for byte.

Real emitted lines (OSC-006):

```
t=1   MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v2 t=1 u0=TREE(2,2) u2=TREE(2,3);WAIT;MOVE 2 2 3
t=2   MSG NARRATE v2 t=2 u0=TREE(2,2) u2=TREE(2,3);MOVE 0 2 3;MOVE 2 1 3
t=137 MSG NARRATE v2 t=137 u0=NONE u2=NONE;WAIT;WAIT
```

≈60 characters against the 2,000 the coordinator measured safe.

## 2. What was built, and what was deliberately not

Three edits to a copy of the base, nothing else:

1. `select` becomes a thin wrapper over **`select_recording`**, lifted from PEEK rev 3, which
   records the chosen `Target` per unit at all three selection sites (single-unit, best-pair,
   remainder). `select`'s signature and behaviour are unchanged.
2. `commands()` calls `select_recording` with a tick-local `BTreeMap<i32, Target>`, borrowed
   inside the one call and never stored.
3. The banner push becomes a captured `Option<&str>`, and one `MSG` is **inserted at index 0**
   after the gameplay tokens are built.

**Carried from PEEK rev 3: only `select_recording`.** No `peek_swap_allowed`, no
`resolve_move_conflicts_with_peek`, no `peek_target_cell`, no peek argument threaded into the
conflict resolver. The instrument's play is swap R-1's.

**Order and the `WAIT` fallback.** Gameplay tokens keep their relative order (`TRAIN`, then the
selected commands). The `if out.is_empty()` fallback runs on the **gameplay** tokens, before the
telemetry is inserted, so the instrument can never suppress the base's `WAIT` by making the vector
look non-empty. That is the one place where an "obvious" ordering would have silently changed play.

## 3. Grammar, as ruled

`MSG [<announcement> ]NARRATE v2 t=<turn> u<id>=<target> ...`, targets `NONE`, `SHACK`,
`BANK(x,y)`, `CELL(x,y)`, `TREE(x,y)`; ids ascending; **every live own unit exactly once**,
`NONE` explicit; banner only on turn 1; one message per turn, first in the list.

The gate does not take that on trust. Per turn, per fixture, it decodes the emitted payload back
and checks: exactly one `MSG` token, and it is first; the version is `v2`; `t=` equals the actual
turn; ids ascending and unique; and **the roster equals the live own units in that turn's state**,
taken from the trace rather than from the payload. 6,800 turn-lines were decoded this way.

## 4. The controls — every check shown to fail before it was believed

`python3 claude_1/narrate1/gp_controls.py` → exit 0, 11 of 11 fired:

| control | fires |
|---|---|
| unmutated telemetry is accepted (or every row below proves nothing) | clean |
| `t=` shifted by one | turn misalignment |
| a unit dropped from the roster | roster ≠ live own units |
| ids emitted out of order | not ascending |
| a second `MSG` token appended | 2 MSG tokens |
| `MSG` moved out of first position | not first |
| `SHACK` → `HOME` | off-grammar target |
| banner on a later turn | banner present=True, expected False |
| a unit emitted twice | appears twice |
| `strip_msg` removes the complete token and only it | gameplay tokens survive intact |
| a gameplay token merely *containing* "MSG" (`MSGX 1`) | **not** stripped |

The last two matter most: a stripper that removed too much would manufacture parity, and one that
matched a prefix would eat a gameplay token. The first row matters as much — a control suite where
the clean case also "fires" is measuring nothing.

## 5. What G-P does not prove, stated before anyone reads the 34/34

**Platform non-interference is NOT established by this gate and is not mine to establish.** This
harness does not react to the command stream's count, ordering or line length. The instrument emits
a `MSG` token on every turn where the base emits one on turn 1 only. If the live referee reacts to
that — a cap, a truncation, a timeout on a longer line — **G-P passes and the ladder position is
still not swap R-1's**.

Two things narrow it, neither of them run by me: the coordinator's probe game carried a per-turn
`MSG` for 250 of 250 turns with normal play and a normal score, and their stated plan makes the
first Arena read an identity check on telemetry transport, with mismatch stopping further reads.

Also unchanged: nothing here grades swap R-1 as a cure, the instrument can never be the champion
because it changes the command stream, and no Arena action is mine.
