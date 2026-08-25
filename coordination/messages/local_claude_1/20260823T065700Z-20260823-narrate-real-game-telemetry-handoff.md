---
schema_version: 2
type: handoff
task_id: 20260823-narrate-real-game-telemetry
from: local_claude_1
to: ["claude_1", "codex_1"]
cc: ["user", "chatgpt_1"]
message_id: coordination/messages/local_claude_1/20260823T065700Z-20260823-narrate-real-game-telemetry-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: f2ebc9bb07bafe16e883d8fe875ec276ea5a3a1c
artifact_paths: ["local_claude_1/narrate/probe-msg-length-2026-08-23.rs", "local_claude_1/narrate/msg-length-probe-2026-08-23.json"]
created_utc: 2026-08-23T06:57:00Z
---

- To: claude_1, codex_1
- CC: user, chatgpt_1
- Task: 20260823-narrate-real-game-telemetry
- Requires acknowledgement: yes — this frees the grammar, which I told claude_1 to build tight

# HANDOFF — NARRATE step 1 ANSWERED off the ladder: 2,000 characters of `MSG` per turn survive byte-exact, every turn, for zero Arena cost

Step 1 is done and it did not need the owner's go, because it did not need the ladder.

## The measurement

One `TestSession/play` game — game id **900074185**, our code versus `escdemon` (6479768),
completed normally, 250 turns each, scores 100–104. **One game of the 12-game burst cap used; I
stopped there because the result is unambiguous.**

The probe is the champion (`candidate-door1-pure-deletion.rs`, `547fa706…`) with the once-only
banner replaced by **one `MSG` on every turn whose payload grows 8 characters per turn** — a
repeating `0-9` ruler between a declared length and an `-END` terminator, so both truncation and
its exact cut point would be readable. Probe source sha256 `e0206f9d127ae1cc…`, compiled clean
locally before it was sent.

| question | answer |
|---|---|
| largest payload that survived | **2,000 characters** (2,028-char full `stdout` line, turn 250) |
| truncated turns | **0 of 250** |
| turns whose ruler was not byte-exact | **0 of 250** — checked character by character, not by terminator |
| rejected turns, dropped commands, timeouts | none; the game ran to its end and both bots scored |
| is a per-turn `MSG` legal at all | **yes** — 250 of 250 turns carried one and play continued |

**No limit was found.** The honest statement is not "the limit is 2,000" but "2,000 is safe and we
never reached a boundary". The ramp simply ran out of turns.

## What this changes for the build

**claude_1: the tight character budget I imposed is lifted.** Two units' targets is on the order of
40 characters. You have roughly fifty times that. Design the grammar for a decoder to read
comfortably — self-describing field names, an explicit turn number, and `Target::None` distinct
from a unit that is absent — rather than squeezing it.

There is real headroom to carry more than the target if codex_1 rules it useful (the chosen
candidate's score, or the runner-up), which would let real games answer *why* a unit chose what it
chose and not only *what*. **I am not chartering that** — it widens the instrument, and a wider
instrument is a bigger parity risk. Raise it as a construction question if you think it is worth it.

**The two-`MSG`-tokens-in-one-turn question is moot** and I am withdrawing it from the charter. One
`MSG` per turn is proven to work and holds far more than we need, so the banner folds into the same
line and nothing needs a second token.

## The limits of this result, stated because they are real

1. **This is a TestSession game, not an Arena game.** The Arena `MSG` round trip is verified
   byte-preserved into the corpus only for the 41-character banner (game `899964767`). Same
   referee and same replay format, so I expect it to hold — but 2,000 characters through the
   *Arena* path is inferred, not measured. It is measured on the AAAAA block's first game, which
   is early enough to matter and cheap enough to check.
2. **One game, one opponent, one map.** Length behaviour is not a per-map property, so I did not
   spend more of the burst on it.
3. This says nothing about whether emitting `MSG` changes play. That is gate G-P and it is still
   claude_1's, unchanged.

Artifacts pinned at `agent/local_claude_1@f2ebc9bb`: `local_claude_1/narrate/probe-msg-length-2026-08-23.rs`
(the exact source sent) and `local_claude_1/narrate/msg-length-probe-2026-08-23.json` (every turn's
declared length, arrived length, terminator and byte-exactness). Reproduce with
`cgauto/field_panel.play` against `escdemon`; the session cookie lives on `project_host` only.
