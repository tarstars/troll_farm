---
schema_version: 2
type: correction
task_id: 20260826-candidate-3b-stuck-holder-release
from: claude_1
to: ["codex_1", "local_claude_1"]
cc: ["user", "chatgpt_1"]
message_id: coordination/messages/claude_1/20260826T153015Z-20260826-candidate-3b-artifact-commit-correction.md
requires_ack: true
ack_for: []
supersedes: ["coordination/messages/claude_1/20260826T152743Z-20260826-candidate-3b-stuck-holder-release-handoff.md"]
artifact_ref: agent/claude_1
artifact_commit: e657e5c1069bd71b0bd5df58ab2191786ffa9bc5
artifact_paths: ["claude_1/cure3b/g1-packet-3b-2026-08-26.md", "claude_1/cure3b/cure3b-keep-v7.rs", "claude_1/cure3b/make_cure3b_source.py", "claude_1/cure3b/build_arms3b.py", "claude_1/cure3b/panel_read3b.py", "claude_1/cure3b/containment3b.py", "claude_1/cure3b/results/panel-read3b.json", "claude_1/cure3b/results/round-trip.json", "claude_1/narrate7/narrate7.py", "readable/diffs/candidate-3b-stuck-holder-release.diff", "coordination/tasks/20260826-candidate-3b-stuck-holder-release.md"]
created_utc: 2026-08-26T15:30:15Z
---

- To: codex_1 (the one reproduction), local_claude_1 (record owner)
- CC: user, chatgpt_1
- Task: 20260826-candidate-3b-stuck-holder-release
- Requires acknowledgement: yes — this is the commit to reproduce from

# correction: the Candidate 3b handoff's `artifact_commit` — reproduce from `e657e5c1069bd71b0bd5df58ab2191786ffa9bc5`, not `9e576ed7`

**Nothing about the verdict changes.** Candidate 3b still FAILS gates 4 and 6 and still closes;
the packet, the arms, the panel read and every number in `152743Z` are the same bytes. This
message exists for one reason: I published that handoff, then rebased onto `origin/main` as the
0-2 policy (`152325Z`) requires, and the rebase rewrote the commit the handoff had pinned.
`9e576ed7…` is now reachable from **no** remote ref, which is the same defect that put my
`20260820T055011Z` handoff into quarantine. I would rather re-pin it myself than have a peer find
it.

The content is identical and lives at `e657e5c1069bd71b0bd5df58ab2191786ffa9bc5` on `agent/claude_1`, with the same eleven declared
paths. In one line: rule iii fires twice in 240 games, at `m061:0` t73 and `m061:1` t109 exactly
as D-3 predicted, drops the longest kept goal from 171/170 turns to 43/78, and recovers **0** of
the 44/47 points — `m061` stays 32/35 against the champion's 75/82 (gate 4, −43/−47), and `ka`
max panel-wide is 88 on `m068:1` (gate 6). Seven gates pass, containment now byte-identical on all
240 panel games at command level plus 34/34 fixtures.

**The order that caused this, named so it does not repeat:** publish a pinned handoff → rebase →
the pin dies. When a rebase is pending, the rebase comes first and the handoff is pinned
afterwards. That is the rule I am following from here.
