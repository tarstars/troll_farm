# handoff: 20260730-transport-protocol-fix

- From: chatgpt_1
- To: claude_1
- CC: all agents, user
- Created UTC: 2026-07-30T09:02:00Z
- Task: 20260730-transport-protocol-fix
- Branch: `agent/chatgpt_1-transport-protocol`
- Base: `session-2026-07-01` at `e21dbd4daca24a1c1e548f25742566a2e2a81584`
- Protocol commit: `07fb441e1b89249a84457de6e0df2c490cb037b2`
- Requires acknowledgement: yes
- User-directed shared-hotspot edit: yes

## Reason

The user identified a recurring and annoying coordination failure: an agent may tell the user
that it has updated status or sent a message while the change exists only in its working tree or
local branch. Other agents coordinate only through fetchable GitHub refs, so until push succeeds
they know nothing about it.

The old protocol contained the sentence “pushing is part of sending” only at the end of §10. That
was technically correct but operationally too easy to miss and too weak to govern status reports.

## Change

`coordination/multi-agent-protocol.md` now makes this a top-level invariant:

> **Unpushed means unsent.** Working-tree edits, local commits, terminal output, and chat
> statements have no cross-agent coordination effect. A coordination event exists only after its
> commit is pushed to `origin` and the remote SHA is fetchable.

The rule is now applied explicitly to:

- task records and claims;
- agent status updates;
- immutable messages;
- progress leases and long-running phase markers;
- blockers, handoffs, acknowledgements, releases, and integration notices;
- conflict resolution and ownership claims;
- the definition of done;
- user-facing statements that work was sent, pushed, published, handed off, integrated, or done.

The lifecycle is restated as `write -> commit -> push -> verify -> announce`. If push fails, the
claim is inactive, the lease is not renewed, and the handoff is not delivered. Chat can report a
transport failure but cannot substitute for repository communication.

## Review points

Please verify that the wording is strict enough without making normal operation ambiguous. In
particular:

1. only remotely visible claims participate in conflict resolution;
2. only remotely inspectable progress renews the 15-minute lease;
3. a receiver must fetch before declaring that a peer has not communicated;
4. a sender must verify the remote SHA before reporting success to the user;
5. integrated session state remains distinct from merely published agent-branch state.

## Requested action

- `claude_1`: acknowledge and integrate the protocol patch, or reply with a correction.
- All agents: immediately follow the new operational shorthand: **unpushed = unsent; unverified
  push = not yet sent; chat is an alert channel, not the coordination bus.**

## Safety

No source code, experiment artifact, data, Arena state, or other shared documentation was changed.
The only shared-hotspot edit is the user-requested coordination protocol clarification.
