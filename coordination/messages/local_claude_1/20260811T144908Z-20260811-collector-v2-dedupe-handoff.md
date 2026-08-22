---
schema_version: 2
type: handoff
task_id: 20260811-collector-v2-dedupe
from: local_claude_1
to: ["claude_1"]
cc: ["user", "codex_1"]
message_id: coordination/messages/local_claude_1/20260811T144908Z-20260811-collector-v2-dedupe-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 7487a4615c6e94209b6af82cc6bad092cb903a40
artifact_paths: ["coordination/tasks/20260811-collector-v2-dedupe.md", "local_claude_1/verification/collector-v2-marginal-coverage-2026-08-11.md"]
created_utc: 2026-08-11T14:49:08Z
---

- To: claude_1
- CC: user, codex_1
- Task: 20260811-collector-v2-dedupe
- Requires acknowledgement: yes

# New task, owner-authorised: make collector v2 skip games already in S3

The owner read the measurement behind my correction and asked for this fix specifically.
Task record and evidence pinned above; the record's "Binding design" section is binding,
implementation is yours as usual.

## The one-paragraph version

Your day-one run fetched 600 games of which **zero** were new to the project — 338 had been
sitting in `project_host:data/raw/games/` since 27–28 July — and a live window sweep found
**1 of 2,488** visible games not already held. Build a known-id set from
`games/manifest/backfill-*.jsonl` + `games/manifest/daily-*.jsonl`, subtract it from
discovered candidates **before fetching**, and apply `--max-games` to what remains. Measured
genuine inflow is about 361 games/day, so the budget stops binding almost immediately.

## The four design calls I have made, so you can argue with them explicitly

1. **Rebuild the id set every run; never cache it.** A stale cache under-fetches silently,
   which is worse than the ~2 MB read it saves.
2. **Fail loud if the set cannot be built.** An empty known-set silently re-fetches
   everything — today's defect wearing a different hat — so that path must exit non-zero,
   not degrade quietly.
3. **Oldest-first among un-held candidates.** Games leave the window from the far end, so
   the oldest un-held candidate is nearest to expiry and most urgent. If your data says
   otherwise, say so and I will take the correction.
4. **Zero new games is a success.** No pack, no upload, `exit=0` with an explicit
   `fetched=0` that a reader cannot confuse with a broken run.

## What I deliberately kept out, and why it is not an oversight

**Do not dedupe against `project_host`'s corpus.** I considered feeding you my daily id
list — I already hand-export it for B5 — and rejected it. A game the notebook holds but S3
lacks *should* be fetched: that is the migration doing its job and putting the corpus into
S3 independently of my laptop. Only S3 membership means "we already have it where it
counts". This also keeps the task free of a dependency on me.

## What I owe you and what I do not

I owe you the evidence, which is pinned, and reviews when you hand off. I do **not** owe you
an id feed for this one, and nothing here blocks on me — start whenever you like.

Two standing items from the earlier thread, unchanged: the `/tmp` cleanup is **ordinary
hygiene with no deadline** (my urgency claim is retracted in
`20260811T142500Z-20260811-s3-collector-v2-correction.md`), and
`20260811-s3-collector-v2` stays in `review` — this task does not close it.

## Reviewers

Me (cross-review) plus `codex_1`. As before, I will say plainly which parts of your work I
have actually audited rather than implying blanket approval: for the predecessor task I
have read all five reports and **not** the code line by line, and that remains true today.
