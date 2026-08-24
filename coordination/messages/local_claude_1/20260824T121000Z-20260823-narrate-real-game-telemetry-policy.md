---
schema_version: 2
type: policy
task_id: 20260823-narrate-real-game-telemetry
from: local_claude_1
to: ["local_claude_1"]
cc: ["user", "claude_1", "codex_1", "local_codex_1"]
message_id: coordination/messages/local_claude_1/20260824T121000Z-20260823-narrate-real-game-telemetry-policy.md
requires_ack: false
ack_for: ["coordination/messages/local_claude_1/20260823T065200Z-20260823-narrate-real-game-telemetry-update.md", "coordination/messages/local_claude_1/20260823T104000Z-20260823-narrate-real-game-telemetry-policy.md"]
supersedes: ["coordination/messages/local_claude_1/20260823T104000Z-20260823-narrate-real-game-telemetry-policy.md"]
created_utc: 2026-08-24T12:10:00Z
---

- To: myself (the queue items)
- CC: user, claude_1, codex_1, local_codex_1
- Task: 20260823-narrate-real-game-telemetry
- Requires acknowledgement: no — this message closes the queue anchor rather than opening one

# CARDS — all three carried cards are CLOSED; I carry nothing

Replaces `20260823T104000Z` and discharges it and `20260823T065200Z`, both named above. These cards
were self-addressed so no peer receipt could discharge them; I am discharging them myself, on the
record, having verified each disposition in the repository rather than accepting the handover's
summary of it.

## The three cards

**CLOSED — the AAAAA Arena block, reads 2 to 5.** Not completed: **cancelled by written ruling** at
`20260823T121000Z` — *"Reads 3, 4 and 5 are cancelled."* Reads 1 and 2 matured (`41182039`/`6652424`
= 23.88 rank 30; `41182352`/`6652602` = 23.84 rank 29), read 2's 160 games were collected and digest-
verified before the seat was reused, and NARRATE v3 (`41182608`/`6652642`) then took the ladder as a
successor instrument, not as read 3.

*I carry the cost forward explicitly, because the handover table does not show it:* swap R-1's ladder
position rests on **two** reads, standard error ≈ **1.06**, not the ≈ 0.67 the five-read design was
bought for. Anyone citing that position must cite the wider interval. The deliverable as chartered
does not exist and will not.

**CLOSED — restore the champion when the block ends.** Discharged by owner ruling, 2026-08-23:
*"remove 4. It doesn't really matters, who is on ladder"*, recorded at `20260823T114000Z`. Nothing
has to happen when a block ends.

*Two things survive the discharge and are not to be over-read:* door 1
(`cgauto/submissions/candidate-door1-pure-deletion.rs`, `547fa706…`, hash re-verified exact today)
remains the **documented** fallback target — knowing what to fall back to is not an obligation to
fall back; and `docs/PROMOTION-RUNBOOK.md` still must not be followed, its abort path naming a bot
retired weeks ago.

*One provenance caveat I record against my own work:* this owner ruling exists in the repository only
as my own transcription of a spoken utterance, in a message I authored. It is self-consistent across
four documents but single-sourced through me. If the owner ever reads it back as wrong, my
transcription is the thing that was wrong, and the restore obligation returns.

**CLOSED — 20260821-swap-r1-cure, the residual-13 disposition and the cure-arm basket criterion.**
Its unblock signal was delivered — 469 real games in three batches, blocking 0 %, dancing 11 %,
idleness 615/84,928 troll-turns = 0.72 % — and I issued the ruling at `20260823T131600Z`: the chain
is **RETIRED**, the residual 13 are fixture artefacts with no real-game counterpart, and the basket
criterion has no chain left to decide. `coordination/tasks/20260821-swap-r1-cure.md` carries the
RETIRED status. `claude_1`'s dependent card is discharged and it receipted that itself at
`20260823T133219Z` on `origin/agent/claude_1`.

*Reopen trigger, unchanged and automatic:* one contention episode in any graded real corpus reopens
the task. Grading now runs on every batch we collect, so this needs no watcher.

## Queue state

The NARRATE task's decision purpose is complete and I hold **no live card and no lane**. I am not
opening one. The project awaits the owner's next priority.

## One open defect I am parking here rather than losing

The quarantine's twelve adjudications are bound to whoever *currently* holds the coordinator role,
so every transfer voids them and a merge reintroduces the break without a conflict. It has broken on
two consecutive transfers in two days and I repaired it by hand again today. It is coordinator-owned,
therefore mine, and it goes to the owner as an open defect with a proposed fix — not repaired on my
own authority over the one file I am also the sole author of. Detail:
`20260824T120400Z-20260805-coordination-transport-hardening-ack.md`.
