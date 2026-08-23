# 20260822-github-native-agent-publication-gateway — a fail-closed publisher for agents with no shell

- Status: **CLOSED 2026-08-23 by owner ruling — never chartered, nothing built.** Owner:
  *"I think we can remove 9. somehow it can publish its work, ok"*. `chatgpt_1` published five
  messages by its own means on 2026-08-22, so the gateway addresses a nuisance, not a blocker, and
  a five-shared-path build is not worth that. **Nothing was implemented; no write set was ever
  assigned.** The frozen architecture package stays in `chatgpt_1/github-native-gateway/` for
  reference. **Reopening requires a fresh owner decision** — this record is not a live queue item
  and must not be revived as one.
- Superseded status: BACKLOG — recorded, not chartered. Owner-authorized in the interactive
  `chatgpt_1` session 2026-08-22 (confirmed with the owner directly the same day, because the
  decision was made off the bus and I will not act on an authorization I cannot verify).
- Record owner: local_claude_1 · Architecture: **chatgpt_1** (frozen package, below) ·
  Implementation/review roles: **assigned at activation, by me, not before**.
- Created UTC: 2026-08-22T18:45:00Z

## The problem, which is real

`chatgpt_1` has no shell, no local checkout and no Git index. It publishes by writing GitHub
Actions workflows that act for it. On 2026-08-22 two of those runs failed nine seconds in
while the message they carried was provably valid — I linted its staged handoff myself in a
throwaway worktree: `errors (0)`, exit 0. An agent whose only route to the bus is bespoke
per-message automation will keep losing deliveries to plumbing.

**Note the premise moved the same evening:** it then published a handoff, a merge and a
correction successfully, minutes apart. So the gateway is now a *reliability* argument, not an
*unblocking* one. That is why this is backlogged rather than chartered.

## The frozen architecture (chatgpt_1's, not mine)

`agent/chatgpt_1@63f29c028a0935c1a4b8a236d80ace5c32f594e2`:
`chatgpt_1/github-native-gateway/{owner-decision,spec,acceptance-matrix}-2026-08-22.md`.

Owner's choices as recorded there: publication **model 2** (a trusted server-side publisher for
runtimes with no checkout), interface **1.A** (GitHub-native: a labelled issue carries one typed
request), operating mode **interactive** — no autonomous wake, no persistent executor.

Phase-1 authority, which is tight and is the reason this is recordable at all: the gateway
publishes **only as `chatgpt_1`**, **only to `agent/chatgpt_1`**, and may not write `main`,
another agent's namespace, Arena state, repository settings, secrets, or arbitrary workflow
files. Validation, commit, push and remote verification are **one fail-closed operation**;
a partial or ambiguous result is a failure; requests are idempotent and leave an audit record.

## Proposed shared write set (chatgpt_1's proposal, unassigned)

`.github/workflows/agent-publication-gateway.yml` · `scripts/agent_publication_gateway.py` ·
`tests/test_agent_publication_gateway.py` · `docs/agent-publication-gateway.md` ·
`coordination/gateway/request-schema-v1.json`

Every one of those is a **shared** path, not `chatgpt_1/`. That is precisely why the roles are
mine to assign and why this waits: a permanent Action with repository write access is a
privileged surface, and it is the same mechanism as this agent's 2026-08-06 quarantine — not
the same act, but the same machinery, and it gets reviewed accordingly.

## Conditions for activation

1. **It does not preempt** `20260822-alpha-progress-regrade` or the anti-benching Phase 3b
   chain. Both bear on the live architecture question; a publishing convenience does not.
2. **`chatgpt_1` publishes its architecture position first.** It was revived to argue, the
   argument has been written since 08:17Z, and it is still undelivered. Infrastructure that
   delays the deliverable it exists to carry has the priority backwards.
3. At activation: codex_1 reviews the workflow **before** it is deployed, the acceptance
   matrix's rejection cases are observed failing first, and the first successful live request
   is not trusted until an identical retry creates no duplicate and the ordinary sweep reads
   the result with no new transport error. (Those three are chatgpt_1's own conditions; I am
   adopting them rather than inventing weaker ones.)

## What this record does NOT do

It charters no implementation, assigns no write set, authorizes no workflow deployment, and
grants `chatgpt_1` no scope beyond architecture. Its charter is unchanged:
`coordination/revival-prompt-chatgpt_1-2026-08-22.md`.
