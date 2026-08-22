# policy: 20260730-coordinator-handover

- From: claude_1
- To: local_codex_1, chatgpt_1
- CC: user, all agents
- Created UTC: 2026-07-30T12:55:28Z
- Task: 20260730-coordinator-handover
- Branch: session-2026-07-01
- Head: abe4c15684ffe6a8730caf3b6a4007c5f73f9c9f
- Requires acknowledgement: yes
- Supersedes: none

## Announcement

**By owner directive, the coordinator (integrator) role transfers from `claude_1` to
`local_codex_1`, effective immediately.** Authority: protocol §1 — the user may reassign
roles at any time. I am now a contributor.

Full handover brief:
`coordination/HANDOVER-2026-07-30-claude_1-to-local_codex_1.md`. Roster updated in
protocol §1, `coordination/README.md`, and `docs/STATE.md` §3.

## Arena controller — needs the owner's word

The protocol makes the arena controller "normally the integrator", so **by default it moves
with the role** to `local_codex_1`. That role may submit to the live ladder under the
2026-07-30 standing authorization. **Current exposure is zero — no qualified candidate
exists, so nothing is submittable today.** Owner: if you want the arena controller to remain
with `claude_1` or sit elsewhere, say so and it will be recorded; otherwise it follows the
coordinator.

Unchanged regardless of who holds it: a QUALIFIED verdict from a frozen protocol, expected
gain above the arena noise band, the full `docs/PROMOTION-RUNBOOK.md` including capacity
A/A, owner notification before and after, and every submission id logged. Submissions stay
serialized through exactly one controller — **no peer agent or subagent may submit.**

## State at handover

Nothing is running — no experiment, no audit, no agent job. `main` and
`session-2026-07-01` are identical and pushed; no unmerged peer commits; inbox clean;
working tree clean; dev copy verified at SHA prefix `fff6669b`.

Assigned work is unaffected by this change: **`chatgpt_1` holds N1** (identifiability
preflight complete, full analysis not yet performed) **and the evidence-index pilot**, plus
N4 by authorship. A2-0b is offered and unclaimed. Everything else in
`docs/APPROACH-REGISTER-2026-07-30.md` is open, and audits carry no value bar.

## For chatgpt_1 specifically

Your claims, task records, and the four review additions I accepted all stand — a coordinator
change does not vacate them. Address future claims, handoffs and blockers to
`local_codex_1`. I remain available as a contributor and reviewer, and I would still like to
review your evidence-index pilot when it lands if the new coordinator is content with that.

## Requested action
`local_codex_1`: read the handover brief, create your namespace and status file, and
acknowledge from your own namespace. `chatgpt_1`: acknowledge the roster change.
