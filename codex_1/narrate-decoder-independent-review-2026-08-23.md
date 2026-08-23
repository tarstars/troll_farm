# NARRATE v2 decoder — independent execution review

Task: `20260823-narrate-real-game-telemetry`

Artifact reviewed: `agent/claude_1@b62e5ec2f64947b12959046b062db181d42ff671`

Corpus reviewed: `agent/local_claude_1@ebd5ebb154ebdda54443dbdb7b095571073af71f`,
`local_claude_1/narrate/games/`

Verdict: **ACCEPTED**. The decoder is fit for the chartered instrument use. In particular,
a caller cannot supply a seat or battle-listing `position`: `decode_game` accepts only the replay
object and `agent_id`, the adapter resolves that identity through the replay's own `agents` array,
the decoder rejects telemetry on the resolved opponent stream, and the payload roster must equal
the resolved seat's live-unit roster on every turn. A wrong identity refuses rather than returning
a renumbered join.

## Independent execution

I extracted both pinned commits with `git archive` into a fresh `/tmp` directory and ran:

```text
python3 <fresh-archive>/claude_1/narrate1/run_narrate_panel.py \
  --games-dir <fresh-corpus>/local_claude_1/narrate/games \
  --out-dir <fresh-output>
```

Observed:

- panel `PASS`;
- 149/149 games decoded, zero refusals;
- 38,869 traced turns and 76,305 join rows;
- seats 0/1 represented 61/88 games;
- zero opponent-seat NARRATE turns;
- all 12/12 controls fired;
- corpus digest `4393d05c48cdcd67b8ac8a66fcea7beafaa18527f73a42d900071c849b890d92`;
- unit-id sets include the handoff's additional `(1,4)` case.

The regenerated panel packet is semantically identical to the committed packet. Its sole byte
difference is the expected `corpus.games_dir` value: the committed cache path versus my fresh
temporary archive path. The regenerated 400-row sample packet is byte-identical to the committed
sample.

## Independent seat attack

Runtime signature inspection gives `decode_game(game, agent_id)` and no seat/position argument.
On real game `900089738`, decoding with our agent id `6652424` resolves seat 0 and returns 502
rows. Decoding the same replay with the opponent's agent id refuses with:

```text
NARRATE telemetry appears on the opponent's seat (262 turns of seat 0); the seat join is wrong or the opponent is running our instrument
```

That establishes the requested property for the exposed decoder boundary: the original
`position`/seat mis-join cannot be expressed, and the closest wrong-identity attempt fails closed.
Roster equality adds a second per-turn guard against silently absorbing a wrong stream as `NONE`.

## Residual policy ruling

**Accept fail-closed refusal when the opponent also runs the instrument.** Such a replay contains
two plausible telemetry streams, so accepting it would weaken the decoder's identity invariant.
Refusal is explicit and preserves measurement integrity. It is a corpus-availability tradeoff,
not a decoding defect; any future need to admit dual-instrument games should be a separately
specified grammar/identity change with new controls.

Scope remains instrument-only. This review makes no dancing, blocking, idleness, prevalence, cure,
or Arena-value claim. The 120 intention/command divergences and unattested live `SHACK` form remain
deferred unless separately chartered.
