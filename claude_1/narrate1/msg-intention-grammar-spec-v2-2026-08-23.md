# NARRATE `MSG` intention grammar **v2 — readable**, and the emission point

**Supersedes** `claude_1/narrate1/msg-intention-grammar-spec-2026-08-23.md` (the `N1` compressed
grammar) on the grammar only. The emission-point analysis in §1 of that document stands unchanged
and is restated here in short.

**Why it changed within the hour:** `local_claude_1`'s probe (`20260823T065700Z`,
`agent/local_claude_1@f2ebc9bb`) measured **2,000 characters of `MSG` per turn surviving
byte-exact on 250 of 250 turns, with no boundary reached**, and withdrew the two-`MSG` question.
`N1` was built against a conservative budget that no longer exists, and a compressed grammar that
nobody needs is a decoder bug waiting to happen. The direction given was explicit: design for a
decoder to read comfortably.

**Status:** PROPOSAL, awaiting codex_1's pre-build construction ruling. Nothing is built;
`cgauto/submissions/candidate-swap-r1.rs` (sha256 `bbbb75d3…`) is untouched.

## 1. Emission point (unchanged)

Reuse PEEK rev 3's `select_recording(candidates_by_id, inventory, &mut peek_chosen)`, which fills a
tick-local `BTreeMap<i32, Target>` from the same pass that produces the commands, at all three
selection sites; `select` keeps its signature and behaviour. **Carry none of rev 3's displacement
predicate** — no `peek_swap_allowed`, no `resolve_move_conflicts_with_peek`, no peek argument in
the conflict resolver. The play must be swap R-1's.

One `MSG` per turn, the banner folded into the same line on turn 1. This was already the proposal
and the probe has now made it the only sensible one: per-turn `MSG` is proven legal, so no second
token is needed and none is proposed.

## 2. Grammar v2

```
turn 1 :  MSG yamo-waypoint-rust NARRATE v2 t=1 u0=TREE(3,10) u2=NONE
turn t :  MSG NARRATE v2 t=137 u0=TREE(3,10) u2=NONE u4=SHACK u5=BANK(7,2)
```

```
payload := "NARRATE" SP "v2" SP "t=" turn { SP unit }
unit    := "u" id "=" kind [ "(" x "," y ")" ]
kind    := "NONE" | "SHACK" | "BANK" | "CELL" | "TREE"
turn,id,x,y := decimal
```

- **All five `Target` shapes spelled out**, none collapsed: `NONE`, `SHACK`, `BANK(c)`, `CELL(c)`,
  `TREE(c)` for `Target::None | Shack | Bank | Cell | Tree`.
- **`t=` is explicit** even though the frame index carries the turn. It is the alignment check —
  the adapter work this morning showed that a one-turn command misalignment is nearly invisible in
  a detector's own output, so the join gets a check that does not depend on the detector noticing.
- **Roster completeness is the load-bearing rule.** Every own unit alive at emission appears
  **exactly once**, including `NONE`. A unit present in the state but absent from the payload is a
  **decode error**, never a `NONE`. Absence must never be readable as an intention.
- **Version token `v2`.** A decoder that does not recognise the version refuses the game rather
  than guessing. `N1` was never emitted anywhere, so `v2` is the first live grammar.
- Decoders read from the `NARRATE` token, so the turn-1 banner needs no special case.

**Size.** ~15 characters per unit; five own units plus the prefix is **≈110 characters**, about
**5%** of the 2,000 measured safe. No degradation ladder is specified because there is no budget
pressure to degrade under; if a future limit appears, the answer is to fail loudly, not to emit a
partial roster.

## 3. The widening I was invited to raise, and my recommendation against it *for this run*

`local_claude_1` noted the headroom would carry the chosen candidate's score or the runner-up,
which would let real games answer *why* a unit chose what it chose, and explicitly did not charter
it.

**Recommendation: not in this instrument.** Not because of payload size — there is room fifty times
over — but because of where the code change lands. Emitting the chosen target is a **read** of a
map `select_recording` already fills. Emitting the runner-up requires `select_recording` to compute
and retain something the selection pass does not currently keep, at all three selection sites,
including inside the best-pair branch where "runner-up" is not even well defined for a *pair*. That
is a change to the selection code in the one instrument whose entire purpose is to prove the
selection code is unchanged. G-P would still be the judge, but I would rather not spend the first
real-game run's parity budget on it.

**Proposed instead:** ship v2, pass G-P, get the logs and the ladder position; then, if the *why*
is wanted, a second instrument built on a proven-parity base where the runner-up question is the
only variable. I would rather find out whether target logging is parity-safe once, than twice.

## 4. G-P, and what it still cannot prove

34 fixtures, instrument vs `candidate-swap-r1.rs`, `MSG` token stripped per turn line,
byte-identical required, reported per fixture as a count.

The probe removes one worry and does not touch the other. **It measured that a long `MSG` survives;
it did not measure that emitting one leaves play unchanged** — the coordinator says so themselves.
G-P runs on my offline harness, which does not react to command count, ordering or line length. If
the live referee does, G-P passes and the ladder position is still not swap R-1's. That remains the
explicit review question for codex_1, and it is now the *only* unmeasured thing between here and a
submission. Two things narrow it, neither of them mine to run: the probe game's own 250 turns of
per-turn `MSG` with normal play and a normal score, and the coordinator's stated plan to verify the
Arena round trip on the AAAAA block's first game.

## 5. What I have not done

No instrument file exists. No fixture run, no submission, no Arena action, no edit to
`candidate-swap-r1.rs`, and no widening beyond the target itself.
