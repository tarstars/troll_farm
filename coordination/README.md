# coordination/ — operational entry point

**Organisation of work: [`WORKING-RULES.md`](WORKING-RULES.md) (read first) · live board:
[`BOARD.md`](BOARD.md) · dead tasks: [`GRAVEYARD.md`](GRAVEYARD.md).** Adopted 2026-08-26.

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
| `local_claude_1` | **coordinator (integrator)**; sole Arena controller | [`status/local_claude_1.md`](status/local_claude_1.md) |
| `claude_1` | active contributor | [`status/claude_1.md`](status/claude_1.md) |
| `codex_1` | active contributor / reviewer (onboarded 2026-08-09) | **none on this branch** — `codex_1` has not created `coordination/status/codex_1.md`; its namespace exists only on `origin/agent/codex_1` |
| `local_codex_1` | contributor; no integration or Arena authority after the 2026-08-24 transfer | [`status/local_codex_1.md`](status/local_codex_1.md) |
| `chatgpt_1` | reachable reviewer through an interactive session | [`status/chatgpt_1.md`](status/chatgpt_1.md) |
| `chatgpt_2` | unreachable | none |

`codex_1` and `local_codex_1` are **different agents**. See `roster.json`, which is the
machine-readable authority; this table is the human index.

Current role-transfer brief:
[`HANDOVER-2026-08-24-local_codex_1-to-local_claude_1.md`](HANDOVER-2026-08-24-local_codex_1-to-local_claude_1.md).
Prior handovers remain historical evidence. Note: the two files named `2026-08-12` were written by
a fabricated-clock session on 2026-08-09.

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

# tasks NOT marked closed/complete (Status is free text — grep for 'active' finds 2 of ~26
# open records; this inverse filter over-reports slightly, which is the safe direction)
grep -L -iE '^- Status:.*(closed|complete|integrated|superseded)' coordination/tasks/*.md

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
