---
schema_version: 2
type: handoff
task_id: 20260907-two-project-analysis-and-plan
from: local_claude_1
to: ["chatgpt_1"]
cc: ["user", "chatgpt_2", "claude_1", "codex_1"]
message_id: coordination/messages/local_claude_1/20260907T083819Z-20260907-two-project-analysis-and-plan-extension-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 67b2acc1e828cf25a7e6e76c2814dfcd3268a45c
artifact_paths: ["coordination/tasks/20260907-two-project-analysis-and-plan.md", "coordination/BOARD.md", "neighbour/separate_troll_farm/SNAPSHOT-README.md", "neighbour/separate_troll_farm/working-storage/COPY-RULE.txt"]
created_utc: 2026-09-07T08:38:19Z
---

- To: chatgpt_1
- CC: user, chatgpt_2, claude_1, codex_1
- Task: 20260907-two-project-analysis-and-plan (amended; board row A-1)
- Kind: handoff (the extended charter)
- Requires acknowledgement: yes

# AMENDED CHARTER — check again against the published repository, and extend

**The owner's words:** *"I published separate_troll_farm. Give chatgpt_1 task to check again and extend the analysis."*
The full amendment is on the card (§Amendment, at the pin above); this message is its summary. **Deadline unchanged:
2026-09-09 08:00Z.** Same rules, same heartbeat both ways.

## What is new

1. **The neighbour is public:** https://github.com/tarstars/separate_troll_farm — branch `main`, HEAD `badf27ef…`
   (2026-09-05 19:02Z), 111 commits, the whole committed tree: the ~1,000 candidate sources and builders, the tests,
   the tooling, the README ledger. **Precedence:** for anything committed, the published repository is the source of
   truth; our snapshot is a copy. The snapshot is the only copy of the ten 09-06/07 working-tree files the published
   HEAD lacks (listed on the card and in `SNAPSHOT-README.md`).
2. **The evidence you asked for is in the snapshot** under `neighbour/separate_troll_farm/working-storage/` — see the
   ack of a minute ago and `COPY-RULE.txt` for what was pruned.
3. **Your first packet is verified and integrated**, and its corrections are on the board.

## The extension — new files in `chatgpt_1/two-project-plan/`, append-only

- **E1 `RECHECK-<date>.md`** — every statement in the first packet that changes against the primary source and the
  new evidence, numbered; confirm the snapshot's committed documents match the published ones; say what you could
  not check.
- **E2 `PHASE0-AUDIT-<date>.md`** — your own Phase 0, now: the matrix of every existing controller (theirs: `next_bot`,
  the 09-07 dispatch variants, the complete-funding run, V543/V564, the home-growth kernel; ours: A2-1, the port
  v2/v3.1, the b100 / banana R2 line, the orchard macros) against the nine lifecycle properties (a)–(i),
  IMPLEMENTED / ABSENT / UNKNOWN with code paths and traces. Read the complete-funding run's primary review first.
  Say whether TURNOVER survives as non-duplicate, or is DUPLICATE_HYPOTHESIS, and what follows.
- **E3 `LINEAGE-DIFF-<date>.md`** — what V439's `bot.rs` contains that our champion of record
  (`readable/denial-off-champion.rs`) and the old champion with the denial bonus do not; which additions carry measured
  evidence in the neighbour's ledger; whether the same-day readings (08-28: their V2 23.03 / rank 32 against our
  champion 18.19 / 85 and orchard 6 18.84 / 70; 09-04/05: 19.23 / 60 against 23.43 / 28) put the neighbour's lineage
  above ours for reasons in the code rather than in the field; and what, if anything, is worth carrying from V439
  into a unified champion, with its evidence and the cost to test it.
- **E4 `SCOREBOARD-v2.md`** — the neighbour rows' mature dates from the readings ledgers; the top-ten boundaries from
  the three leaderboard freezes and the top-15 inventory; the same-day pairs; NA where the record is silent.
- **E5 `TOOLING-<date>.md`** — the tooling as code, both sides: their unranked real-agent collector (twelve-game limit,
  manifests, identity checks), rank monitor, replay/command audit, panel runner and legacy gate; our sealed-holdout
  runner, field panel and `cgauto/field_panel.py`. For each: what it does, what it needs, whether it serves your
  Phases 3–5 as written, and the exact gap (the chunked, resumable execution path).
- **E6 `CANDIDATE-CENSUS-<date>.md`** — every V-candidate V1–V630 from the ledger, the results files and the published
  builders and sources, clustered by mechanism family with counts and the best mature or paired outcome per family.
- **E7 `PLAN-<date>-v2.md`, `OWNER-PAGE-v2.md`** — fold E1–E6 in; keep the three one-word decisions or replace them
  with better ones; if E2 finds the mechanism already implemented and lost, say so and name the next hypothesis.

If the published repository or the snapshot still lacks something you need, say exactly which in a progress message
and continue; I fetch it. A handoff pinning the commit when done. — the coordinator
