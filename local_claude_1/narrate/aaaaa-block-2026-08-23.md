# AAAAA block — instrumented swap R-1, five reads of one arm

Owner-directed 2026-08-23. Purpose: real-game intention logs **and** swap R-1's first ladder
position. No pairing — there is nothing to compare against; the deliverable is the logs plus a
position.

- Arm (all five reads): `local_claude_1/narrate/instrument-swap-r1-narrate-v2-SUBMITTED-2026-08-23.rs`
- SHA-256 `aaebc503cc2660e920d45858767c6932575324085c93ef9345906f683b5a9271`
- Submitted through `cgauto/api_submit_once.py` with `--expected-sha256`, one cycle in flight,
  never `night_runner.py`.
- Restore target when the block ends: `cgauto/submissions/candidate-door1-pure-deletion.rs`,
  SHA `547fa706…`. An instrumented bot can never be champion.

| read | submission | agent | submitted UTC | games | mature score | rank |
|---|---|---|---|---|---|---|
| 1 | `41182039` | `6652424` | 09:44 | 161 | **23.88** | 30 / 176 |
| 2 | `41182352` | `6652602` | 11:08 | 160 | **23.84** | 29 / 176 |
| 3–5 | — | — | — | — | **CANCELLED** | — |

## Read 1 notes

- Maturity judged by two things together: the game burst finished (161 games, then trickling at
  ~1 per 10 min) and the score was flat across four checks over 26 minutes — 23.8, 23.8, 23.8, 23.88.
- **Telemetry identity check PASSED before the score was taken**: 20 real games, 5,257 turns, 0
  decode errors, 0 leakage to the opponent's seat, both seats
  (`local_claude_1/narrate/arena-identity-check-2026-08-23.json`). codex_1's platform condition on
  G-P is discharged by it.
- 149 of these games are archived at `local_claude_1/narrate/games/` and are the corpus the NARRATE
  decoder was built and accepted against.

## What read 1 does NOT say

The champion (door 1, `547fa706…`) read **22.6** earlier the same day, one unpaired read. The
instrument reads **23.88**. **That +1.28 is not a result.** Both are single unpaired reads taken at
different times of day against a moving field, and the measured difference SD at one run per arm is
**2.123** (σ = 1.501, `docs/STATE.md` §3) — so a gap of this size is ordinary noise. It is not
evidence that swap R-1 is better than the champion, and it must not be quoted as such. Deciding that
would need a paired block, which this is not.

The arm is also **not swap R-1**: it is swap R-1 plus per-turn telemetry. G-P proved the planner is
byte-identical with the message stripped, which makes it a fair instrument, not a graded candidate.

## The block was STOPPED at read 2, deliberately (2026-08-23T12:10Z)

Ruling: `coordination/messages/local_claude_1/20260823T121000Z-20260823-narrate-real-game-telemetry-policy.md`.

Reads 3–5 would have spent ~6 more hours of ladder time collecting **v2** games. v2 is structurally
blind to the class the whole programme is about — a troll whose work the picker discarded records
"wanted nothing" — and a gated v3 that can see it was waiting in the queue. Under the owner's
standing preference (*quick iterations with new games and new analytics*, 2026-08-23) that trade is
the wrong way round.

**Cost, accepted and named:** swap R-1's position rests on 2 reads, not 5 — standard error ≈1.06
instead of ≈0.67. The arm is a measuring instrument that can never be champion, so its score was
never going to decide anything alone.

**Kept:** read 1 matured at 23.88 over 161 games; read 2 sat at 23.84 over 160. Both arms' games were
collected before eviction — 149 + 160 = **309 games, 81,884 of our turns** — and the behavioural
result replicated across the two independent batches (dancing 11 % both times; contention and
repeated pick-and-drop 0 both times).

**No champion restore follows.** Owner, 2026-08-23: who sits on the ladder does not need managing.
The slot passes to NARRATE v3 once codex_1's independent G-P review clears.

## Slot handed to NARRATE v3, 2026-08-23T12:19Z

Read 2 matured at **23.84** over 160 games (flat across 12:07 and 12:17 checks) and its games were
collected and verified complete — a top-up run returned the identical package digest
`84f46acb…`, so nothing was lost to the rolling window.

**swap R-1's ladder position, from two reads of an instrumented arm: 23.88 and 23.84.** Consistent,
and neither is a comparison against anything. It is not a grading of swap R-1 as a cure.

v3 submitted immediately after, with no champion restore in between (owner ruling 2026-08-23):

| instrument | submission | source | sha256 | submitted |
|---|---|---|---|---|
| NARRATE v3 | `41182608` | `local_claude_1/narrate/instrument-swap-r1-narrate-v3-SUBMITTED-2026-08-23.rs` | `9a3e8758…` | 12:19Z |

Off-ladder check before submitting (`TestSession/play` game `900106553`, 3 of the 12-game burst cap
used today): 200 turns, **0 decode failures**, `t=` contiguous, longest line 110 characters against
2,000 safe, and **89 of 399 unit-rows already carried a discarded want** — the new field is live in
real play, not a copy of the chosen target. Shapes observed: `TREE`, `CELL`, `BANK`, `NONE`.
`SHACK` and `ABSENT` unattested in play, exactly as claude_1's caveats said.

Still owed on v3 and NOT discharged by any of the above: **the live Arena identity check** — codex_1's
travelling platform condition. Real replays, telemetry byte-intact, absent from the opponent's seat.
