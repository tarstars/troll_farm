# Owner decision: GitHub-native interactive publication gateway

Date: 2026-08-22
Task: `20260822-github-native-agent-publication-gateway`
Record owner: `local_claude_1`
Architecture contributor: `chatgpt_1`

## Frozen choices

The owner made the following choices in the interactive `chatgpt_1` session:

1. **Publication model: model 2.** A trusted server-side publisher validates and performs repository publication for agent runtimes that do not have a local checkout, Git index, or shell.
2. **Interface: 1.A, GitHub-native gateway.** Phase 1 uses GitHub as the reachable request and result channel.
3. **Operating mode: interactive.** `chatgpt_1` participates when the owner invokes the session. No autonomous wake process or persistent execution worker is authorized.
4. **Start authorization:** the owner said `go on` after the proposed bootstrap sequence was explained.

## Phase-1 authority

- Git remains the authoritative coordination and evidence store.
- The gateway may publish only as `chatgpt_1`.
- The gateway may update only `agent/chatgpt_1`.
- Routine analysis, acknowledgements, questions, progress messages, and valid handoffs may be published without a second owner confirmation.
- The gateway may not write `main`, another agent's namespace, Arena state, repository settings, secrets, or arbitrary workflow files.
- Validation, commit, push, and remote verification are one fail-closed operation. A partial or ambiguous result is a failure.
- Requests are idempotent and leave a machine-readable audit record.

## Explicit non-decisions

This decision does not authorize:

- autonomous `chatgpt_1` sessions;
- a general-purpose code executor;
- direct integration to `main`;
- review verdicts, gate amendments, candidate builds, or Arena mutations;
- promotion of `coordd` from shadow mode;
- rewriting any existing message or quarantine record.

## Bootstrap roles

- `chatgpt_1`: specification, threat model, acceptance conditions.
- `claude_1`: implementation, after the coordinator creates and assigns the task.
- `codex_1`: independent review.
- `local_claude_1`: task record, integration, deployment, and record ownership.
