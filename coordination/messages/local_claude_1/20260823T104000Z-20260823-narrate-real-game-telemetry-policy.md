---
schema_version: 2
type: policy
task_id: 20260823-narrate-real-game-telemetry
from: local_claude_1
to: ["local_claude_1"]
cc: ["claude_1", "codex_1", "user"]
message_id: coordination/messages/local_claude_1/20260823T104000Z-20260823-narrate-real-game-telemetry-policy.md
requires_ack: true
ack_for: []
supersedes: ["coordination/messages/local_claude_1/20260823T065200Z-20260823-narrate-real-game-telemetry-update.md"]
created_utc: 2026-08-23T10:40:00Z
---

- To: myself (the queue items)
- CC: claude_1, codex_1, user
- Task: 20260823-narrate-real-game-telemetry
- Requires acknowledgement: yes (self-addressed queue anchor; a bystander ack must not discharge it)

# CARDS — one CLOSED, one advanced, two carried

Replaces `20260823T065200Z`, named in `supersedes`. These are mine. No peer receipt discharges them.

## Closed this wake

The off-ladder `MSG` length probe is **CLOSED, delivered**, not carried: 2,000-character payloads
survive byte-exact, 0 of 250 turns truncated, no limit reached
(`20260823T065700Z`, artifact `agent/local_claude_1@f2ebc9bb`). Its one gap — that the probe carried
no spaces and no `;`, while the frozen grammar is space-separated — was closed by a second
off-ladder game on the exact submitted instrument, and then by the Arena identity check below.

## The cards

DEFERRED: 20260823-narrate-real-game-telemetry — the AAAAA Arena block, reads 2 to 5. **Advanced,
not blocked.** Read 1 is live: submission `41182039`, agent `6652424`, submitted 09:44Z, immature at
23.8 after 50 minutes. **codex_1's platform condition is DISCHARGED** — 20 real games, 5,257 turns,
0 decode errors, 0 telemetry on the opponent's seat, both seats
(`20260823T103000Z`, artifact `agent/local_claude_1@ebd5ebb1`). The stop condition it carried did
not trigger, so the block proceeds. Submissions go through `cgauto/api_submit_once.py` with hash
verification, one cycle in flight, never `night_runner.py`.
UNBLOCK-SIGNAL: read 1 matures (~11:45Z) and its score is taken from an agent-validated block; then
submit read 2. Repeat to read 5.

DEFERRED: 20260823-narrate-real-game-telemetry — restore the champion when the block ends. The
instrument is a measuring instrument and can never be champion: it changes the command stream.
Restore `cgauto/submissions/candidate-door1-pure-deletion.rs`, sha
`547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0`. Do **not** follow
`docs/PROMOTION-RUNBOOK.md`, whose abort path restores a bot retired weeks ago.
UNBLOCK-SIGNAL: read 5 taken, or the block abandoned for any reason. This card outlives the block —
if the block stops early, the restore still happens.

DEFERRED: 20260821-swap-r1-cure — the residual-13 disposition and the cure-arm basket criterion.
Unchanged and still mine; claude_1's own chain waits on exactly this ruling. Parked behind NARRATE
by the re-ranked backlog, and the case for ruling it on real games rather than on the 34 fixtures is
now stronger, not weaker: the instrument that would grade it is the one on the ladder.
UNBLOCK-SIGNAL: a NARRATE corpus graded for dancing, blocking and idleness, or a written owner
ruling to decide it on fixture evidence anyway.

## Not mine

The NARRATE decoder is claude_1's, chartered at `20260823T103000Z` with 149 real replays supplied at
`local_claude_1/narrate/games/` because its host holds no platform credential. Its review is
codex_1's. Neither is discharged by anything in this message.
