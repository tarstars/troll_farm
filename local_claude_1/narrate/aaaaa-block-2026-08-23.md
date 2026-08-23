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
| 2 | `41182352` | (pending) | 11:08 | — | in flight | — |

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
