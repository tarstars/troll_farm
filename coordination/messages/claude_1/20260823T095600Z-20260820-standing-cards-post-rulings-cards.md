---
schema_version: 2
type: update
task_id: 20260820-pair-selector-anti-benching
from: claude_1
to: ["claude_1"]
cc: ["local_claude_1", "codex_1", "user"]
message_id: coordination/messages/claude_1/20260823T095600Z-20260820-standing-cards-post-rulings-cards.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260823T073800Z-20260823-standing-cards-phase3b-built-cards.md"]
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 76eeefd73f221c87ff959062e6d6853c092a69de
artifact_paths: ["claude_1/STATUS.md", "claude_1/picker3/results/phase3b-gac-2026-08-23.json"]
created_utc: 2026-08-23T09:56:00Z
---

- To: myself (the queue items)
- CC: local_claude_1, codex_1, user
- Task: 20260820-pair-selector-anti-benching
- Requires acknowledgement: yes (self-addressed; the cards below are the queue items)

# standing cards — after RULING 1 and RULING 2: G-b is no longer blocked on a ruling, it is waiting on real games

Replaces `20260823T073800Z`, named in `ack_for`. Two cards change and no card is discharged.

**Delivered this wake, off the board.** RULING 1 recorded in the gate record itself
(`agent/claude_1@76eeefd7`) with the gates **re-run** — G-a + G-c PASS 34/34 both subjects, Δ-B
0/0, only the status text differs from `09ed550f` — and the RULING 1/RULING 2 ack published at
`20260823T095400Z`.

DEFERRED: 20260820-pair-selector-anti-benching, **G-b** — Δ-B inertness by same-state fork.
Status is now **UNMEASURED on the fixture library** (ruled `20260823T094600Z`), which is not a pass
and not a failure. **No longer blocked on a ruling** — the ruling arrived, and it forecloses the
synthesis branch my own report had left open: Δ-B states are not to be synthesised to fill this.
UNBLOCK-SIGNAL: a real-game corpus from NARRATE carrying intentions, in which Δ-B states are either
naturally reached (run G-b there) or absent (the mechanism does not occur, which is itself the
answer). Fixture-library states cannot supply it and are not to be manufactured.

DEFERRED: 20260820-pair-selector-anti-benching, **G-d** — panel with named costs, every changed
game named. Ordered after G-b, unchanged. Conditions travelling with it and not renegotiable by me:
no fixture-only result promotes this; the blast radius is 20 of 34 fixtures with every EFFECT
game's first selected tick at turn 100 (the replant block's own `view.turn>=100` guard); progress
is neither claimed nor measured; and it is never reported as addressing OSC-004/017/034 or
OSC-032/033, including the two of those whose command streams it changes.
UNBLOCK-SIGNAL: G-b measured on real games, or ruled unmeasurable there.

DEFERRED: 20260820-pair-selector-anti-benching, **G-e** — the two-clause bar of
`20260822-alpha-progress-regrade`: healed **with progress**, never merely detector-silent, graded by
the re-grade instrument at `79dfdd63`. Ordered after G-d. Unchanged.
UNBLOCK-SIGNAL: G-d delivered.

DEFERRED: 20260821-corpus-prevalence (b) — the prevalence measurement, deliverables 2–4. The
re-titling branch of this card's unblock-signal is **struck**: RULING 2 declines the re-title in
writing, and the card keeps its own question — **our** lineage's prevalence, resident of record
`6561795`, who appears in none of the 290 in-repo replays. The adapter is out of this wait (D-1
delivered, G-1 ACCEPTED), so the remaining block is **host reach alone**.
UNBLOCK-SIGNAL: `data/processed/games.jsonl` readable from my host with sha256
`a882e52787fa474cba4cdbe6b08a20d5e3925fe8d743bc201da8f816eb1e4e14`, OR a written owner/coordinator
instruction placing the execution on `project_host`, OR a NARRATE corpus of our own games with our
own agent ids.
STANDING LABEL: `d1_flagged_pairs = 37` / `d1_episodes_total = 77` is **adapter coverage** over 136
pseudonymous players and is never to be quoted as prevalence, by me or by anyone citing my files.

DEFERRED: 20260821-swap-r1-cure — the G-2-verdict → G-3 → G-4 chain. Unchanged. The NARRATE
instrument built from swap R-1's source is a measuring instrument, not a candidate; codex_1's G-P
review says in terms that it grades swap R-1 as nothing, and read 1 (`41182039`) does not change
that.
UNBLOCK-SIGNAL: a written `local_claude_1`/owner ruling on the residual 13 and on the cure-arm
basket criterion.

## Not mine, and not to be discharged by me

The AAAAA read-1 block, the Arena identity check on the first replay, and the champion restore are
`local_claude_1`'s. I have started no Arena run and taken no Arena action. My platform condition on
G-P stands undischarged: a clean 153/153 TestSession run of the submitted instrument is real
evidence about the grammar and is not evidence about the Arena.

cross-task: this message carries cards for four tasks and is filed under
`20260820-pair-selector-anti-benching`; `ack_for` names its predecessor, filed under
`20260823-narrate-real-game-telemetry`. My standing cards travel as ONE self-addressed message
spanning every open task, so a replacement must cross the task boundary or the predecessor's cards
sit discharged by nothing.
