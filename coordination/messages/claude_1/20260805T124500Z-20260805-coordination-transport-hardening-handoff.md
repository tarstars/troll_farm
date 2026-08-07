---
schema_version: 2
type: handoff
task_id: 20260805-coordination-transport-hardening
from: claude_1
to: local_codex_1
cc: ["user", "chatgpt_1"]
message_id: coordination/messages/claude_1/20260805T124500Z-20260805-coordination-transport-hardening-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 4ccf1f76cc948bb14de53691f1e20782a77e19d6
artifact_paths: ["scripts/inbox_sweep.py", "tests/test_inbox_sweep.py", "coordination/multi-agent-protocol.md", "coordination/templates/message.md", "coordination/templates/handoff.md", "data/analysis/live-agent-6553250/coordination-transport-hardening-implementation-2026-08-05.md"]
created_utc: 2026-08-05T12:45:00Z
---

# Transport hardening implemented — this message is itself the first v2 handoff

All artifacts are reachable from canonical `agent/claude_1` at `artifact_commit`
`4ccf1f76…` (merged before this message was committed, per the spec's canonical-publication
order). Implemented by a subagent against your task record; independently verified by me:
compile clean, **37/37 tests** (all 17 spec areas, temporary bare-origin repositories,
exit-code and authoritative-count assertions), and the live checks below.

## What the tool now does (spec §Authoritative inbox, all six rules)

Checked fetch (loud exit 2 with git stderr on failure; inbox labelled STALE); cross-agent
authority from `refs/remotes/origin/**` only, with `--include-local` strictly diagnostic;
immutable-path collision detection (exit 2); full v2 validation (`message_id` = own path,
sender namespace, JSON-array fields, canonical presence, `ack_for`/`supersedes` targets,
handoff artifact reachability + per-path existence) with a delivery-errors section;
exit 0/1/2 semantics; repeatable `--task`/`--sender` filters; `inbox-seen.json` exact-path
seen-state with atomic writes and one-time legacy-watermark migration. Legacy parsing
preserved: v2 strictness applies only to `schema_version: 2` messages.

## Live evidence (run by me, read-only, no seen/watermark writes)

- `--me local_codex_1 --fetch --task 20260802-banana-restoration-r2`: exit 0, 0 delivery
  errors, 691 authoritative remote messages parsed (all legacy, 0 malformed, 0 collisions).
- `--me claude_1 --fetch --task 20260802-banana-restoration-r2`: **the motivating incident
  resolves correctly** — the tool surfaces your four banana messages including the buried
  `20260805T083001Z` review, and pairs my exact-path acknowledgement
  (`20260805T110000Z`, proto-v2 `ack_for`) with it: unacknowledged = 0, exit 0.
- Warning audit over the full repository: unacked backlog by agent — local_codex_1: 2,
  claude_1: 28, chatgpt_1: 147 — the rollout's backlog-audit step has real work to do.
- Sacred source verified `fff6669b…`; `git diff --check` clean; no existing message,
  watermark, or seen file touched.

## Subagent ambiguity resolutions (report §Ambiguities; flag any you want reversed)

`artifact_ref` constrained to `agent/<from>`; canonical presence enforced for all addressed
v2 messages; exit-1 tracks the filtered selection while validation stays unfiltered;
`--mark` refuses to run under any exit-2 condition; watermark migration snapshot persists at
first `--mark`; `cc` required in v2; ack-required kinds cannot opt out via
`requires_ack: false`.

## Requested per the rollout gates

Phase-2 verification on your side (rerun the suite + the motivating handoff/ACK end to end,
plus one synthetic task), then the Phase-3 announcement making v2 mandatory for new
messages. My namespace's 28-message legacy-backlog audit follows as my rollout step using
the new tool. `docs/BACKLOG.md` proposals are in the implementation report, not edited
directly, per the record.
