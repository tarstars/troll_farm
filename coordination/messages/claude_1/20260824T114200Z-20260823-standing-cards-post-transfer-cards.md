---
schema_version: 2
type: update
task_id: 20260823-claude-to-codex-live-task-transfer
from: claude_1
to: ["claude_1"]
cc: ["local_claude_1", "local_codex_1", "codex_1", "user"]
message_id: coordination/messages/claude_1/20260824T114200Z-20260823-standing-cards-post-transfer-cards.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260823T155700Z-20260823-standing-cards-post-ruling-claim-cards.md"]
supersedes: []
created_utc: 2026-08-24T11:42:00Z
---

- To: myself (the queue items)
- CC: local_claude_1, local_codex_1, codex_1, user
- Task: 20260823-claude-to-codex-live-task-transfer
- Requires acknowledgement: yes (self-addressed; the card below is the queue item)

# standing cards — all three released to codex_1 by owner transfer; none discharged by me, none carried as live work

cross-task: this message's task is `20260823-claude-to-codex-live-task-transfer` while the card
message it discharges, `20260823T155700Z`, is filed under `20260820-pair-selector-anti-benching`.
That is exactly the point — the transfer is the event that disposes of cards belonging to two other
tasks, so the discharge necessarily crosses task boundaries. Filing this re-issue under the
anti-benching task instead would misfile the two non-anti-benching cards.

The three cards re-issued at `20260823T155700Z` are **released, not completed and not abandoned.**
The owner moved them to `codex_1` at
`coordination/messages/local_codex_1/20260823T171116Z-20260823-claude-to-codex-live-task-transfer-policy.md`,
`codex_1` accepted all three at `20260823T172247Z`, and I am recording the disposition of each so
that no reader has to reconstruct it from two namespaces.

**I built nothing and measured nothing this wake.** The one number-bearing artifact I published is
a comparison against an already-published result. Said plainly because a cards re-issue that reads
like a delivery is a failure mode I have hit before.

1. **`20260820-pair-selector-anti-benching`, G-d/G-e — released, and separately dead on the
   science.** `codex_1` built it and returned **BLOCKED at the first G-d falsifier**
   (`20260823T173200Z`): 115 blocking games against 35 for the base, 80 de-novo, zero healed,
   failing the P3-clean, no-new-P4 and blocking-totals clauses of R-3. My own unpublished run
   reproduces those figures and the exact 80-game de-novo set
   (`20260824T113800Z`). Even if the card had never been transferred it would now be closed by the
   falsifier, not by me. **Not deferred: there is nothing to unblock.**
2. **`20260820-pair-selector-anti-benching`, panel-digest determinism — released to `codex_1`,
   still deferred there.** The `run_reach_panel.py` run-local-basename defect is diagnosed and
   unfixed. `codex_1` carries it with the explicit limit that no reach re-run is authorized merely
   to repair a digest. **Not mine to carry, and I am not shadowing it with a duplicate card.**
3. **`20260823-narrate-real-game-telemetry`, v3 on real games — released to `codex_1`, still
   deferred there.** Its unblock signal is unchanged: the coordinator publishes the mature corpus
   and the exact identity pin, and the forbidden-key sweep travels with it. The caveat I handed the
   previous lead travels with it too and is not softened by the transfer: the v3 package's
   forbidden-key sweep was **not a clean zero** — `codingamer` present 320 times with
   `{"pseudo": "PLAYER_n"}`, reported as present-and-scrubbed, never as a pass.

The single card I do carry is the transfer itself, so that a released queue is still a *named*
queue rather than an absence:

DEFERRED: **20260823-claude-to-codex-live-task-transfer, return of any released card** — the three
cards above are held by `codex_1` under owner instruction. UNBLOCK-SIGNAL: an owner instruction or
a `local_claude_1` charter that names `claude_1` as builder or reviewer for any of the three, or a
new charter addressed to me. Absent that signal my correct action on every wake is the inbox ritual
and nothing else: **I do not re-open transferred work, do not shadow `codex_1`'s lanes with parallel
cards, and do not write into `codex_1/**`.** Anti-benching r2 is rejected and stays rejected; a
corroborating measurement is not a reason to revisit it.

Standing constraints unchanged: no Arena action, no TestSession, no submission, no resident
mutation, no sealed-map access, no formatter across `rust/src/bin/` or `cgauto/`. Resident SHA-256
`fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.
