# coordination/ — operational entry point

Normative spec: [`multi-agent-protocol.md`](multi-agent-protocol.md). Read it before
writing anything here. This file is the practical index.

## Layout

| Path | Owner | Mutability |
|---|---|---|
| `multi-agent-protocol.md` | integrator | stable; changes are policy decisions |
| `peer-prompt.md` | integrator | copy-paste onboarding text for a new agent |
| `templates/{task,status,message,handoff}.md` | integrator | blank forms |
| `tasks/<task-id>.md` | that record's owner | edited by owner only |
| `status/<agent-id>.md` | that agent | replaceable snapshot |
| `messages/<sender>/…` | that sender | **immutable** once written |
| `goals/*.md` | integrator | activated by the user by name |

Agent-private bookkeeping lives outside this tree, at `<agent-id>/` in the repo root
(e.g. `claude_1/`). No agent writes into another agent's directories — ever, including
acknowledgements, which go in the acknowledger's own message namespace.

## Roster

| id | role | status file |
|---|---|---|
| `local_codex_1` | **coordinator (integrator)**; arena controller by default | (create on join) |
| `claude_1` | contributor; former coordinator | [`status/claude_1.md`](status/claude_1.md) |
| `chatgpt_1` | contributor / reviewer; holds N1 + evidence-index pilot | [`status/chatgpt_1.md`](status/chatgpt_1.md) |

Handover brief: [`HANDOVER-2026-07-30-claude_1-to-local_codex_1.md`](HANDOVER-2026-07-30-claude_1-to-local_codex_1.md)

## First-time setup for a new agent

```bash
cd /home/tarstars/prj/troll_farm
git worktree add ../troll_farm-<id> -b agent/<id> HEAD    # never share a worktree
mkdir -p coordination/messages/<id> <id>
cp coordination/templates/status.md coordination/status/<id>.md   # then fill it in
```

Then publish an onboarding message under `coordination/messages/<id>/` and wait for a task
record before implementing anything. Full sequence: [`peer-prompt.md`](peer-prompt.md).

## Fast checks

```bash
# unacked messages addressed to me, across all refs and the working tree
python3 scripts/inbox_sweep.py --me claude_1

# who is doing what right now
head -12 coordination/status/*.md

# active tasks
grep -l 'Status: active' coordination/tasks/*.md 2>/dev/null

# the invariant that breaks everyone else's work if violated
sha256sum rust/src/bin/yamo_orchard_live.rs   # must start fff6669b
git status --short                             # must be clean before you start
```

## Sending a message

```bash
ID=claude_1; TASK=20260729-example-task; KIND=claim
F=coordination/messages/$ID/$(date -u +%Y%m%dT%H%M%SZ)-$TASK-$KIND.md
cp coordination/templates/message.md "$F"   # fill it in, then commit
```

Messages are immutable after they are committed. To correct one, write a new message whose
`Supersedes:` field names the old filename.
