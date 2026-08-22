---
schema_version: 2
type: handoff
task_id: 20260819-sentinel-wake-on-work
from: claude_1
to: ["local_claude_1", "codex_1"]
cc: ["user"]
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260820T103815Z-20260819-sentinel-launcher-deploy-card.md"]
supersedes: []
message_id: coordination/messages/claude_1/20260820T134904Z-20260819-launcher-unattended-drain-handoff.md
artifact_ref: agent/claude_1
artifact_commit: "fa95afd2ea2f2058fc6245a3053893e19a886efc"
artifact_paths: ["claude_1/evidence/launcher-wake-3-unattended-drain-2026-08-20.md", "claude_1/evidence/launcher-permission-grant-probe-2026-08-20.md", "claude_1/evidence/launcher-session-permission-starvation-2026-08-20.log"]
created_utc: 2026-08-20T13:49:04Z
---

- To: local_claude_1, codex_1 (package review)
- CC: user
- Task: 20260819-sentinel-wake-on-work
- Requires acknowledgement: yes

# handoff: WAKE TEST #3 PASSED — a launched session drained and pushed its own queue, unattended

**The card's acceptance bar is MET.** Card step 4 required "ONE real self-launch end-to-end …
a headless session that drains it. That observed wake IS the acceptance evidence." This is that
wake, and this message was written by it.

```
Aug 20 13:45:56 … {'event': 'wake', 'agent': 'claude_1', 'pid': 3293323, 'n': 1,
                   'paths': ['…/20260820T134159Z-20260819-launcher-full-permissions-ruling.md']}
```

Ancestry read from inside this session: `bash(3295930) -> claude(3293323) -> python3(3286799)
-> systemd(1)`. The pid the launcher logged and my own process ancestor are the same number and
the chain ends at systemd — no tty, no interactive shell, no human.

## Bookkeeping, stated plainly

This does **not** discharge the card as a transport event: my 11:18:06Z handoff already named it
in `ack_for` and `ack_for` discharge is idempotent, so the card left the queue then. What that
handoff carried was a deployment whose acceptance bar was UNMET and which codex_1 rejected on
exactly that ground. This message supplies the missing half. I am not claiming a second discharge;
I am closing the substance.

## What the wake actually did, in ritual order

1. `inbox_sweep.py --me claude_1 --fetch` — exit 1; **1 new / 1 ack-required** (the ruling).
   Both lists reported, because zero-unacknowledged is not zero-unread.
   0 collisions · 0 delivery errors · 0 quarantine errors · 12 quarantined.
2. Read the ruling in full.
3. Published the `ack` (`20260820T134818Z-20260819-launcher-full-permissions-ack.md`) and this handoff.
4. `--mark` run as its own step, after reading.
5. Committed and pushed to `agent/claude_1` through `publish_outbox.sh` (lint `--staged` armed
   as the gate, with a non-empty staged set — an empty one lints 0 files and passes).
6. Worktree left clean.

Pre-sweep hygiene, both clean this wake: `scripts/` and `tests/` diffed identical against
`origin/main` AND `origin/agent/local_claude_1` (no drift); `coordination/quarantine.json`
byte-identical to the coordinator's authoritative blob `0921f135c3dd`.

## The capability delta, since that is the whole causal claim

Same wrapper (`claude-proxy`), same ritual prompt, same worktree as the two starved wakes
(#1 pid 3203009 12:38:16Z, #2 pid 3218751 12:47:15Z). One thing changed: the owner's
`--dangerously-skip-permissions` on the claude_1 lane. `git fetch`, `python3`, file writes,
`git commit` and `git push` were all DENIED on #1/#2 and all succeeded here. The full table is
in the evidence artifact. The earlier repair — sharpening the ritual prompt to "end pushed" — was
tested by wake #2 and refused; a prompt cannot lift a permission denial. That line is still right
and I am still holding it; it was never what broke.

## What this does NOT prove — for the reviewer

- One unattended drain of a **one-message** queue. Nothing is shown about a contended queue, a
  lint rejection mid-ritual, or a merge conflict on `agent/claude_1`.
- Wake cap 4/h, pause file, single-flight lock and debounce were **not re-tested this wake**; they
  stand on the 10:38Z–11:48Z shadow and live rounds.
- The mechanism no longer prevents an out-of-scope action by a launched session. Per the ruling
  that is intentional; the guarantee is now protocol plus the git record, and the git record is
  only as good as the reading of it.
- codex_1 lane unchanged: `enabled: false`, `codex exec` still 403s on this host.

## Open, carried forward — not part of this delivery

- **VM disk was 98% / 541M free** at 12:53Z and has already blocked one deploy with ENOSPC.
  Eight checkouts live on this host. Unowned; flagging, not claiming.
- Card 2 (sentinel warm-waits) still blocked on the integrator's `actionable_set()` extraction
  ruling — with the standing note that `agent_launcher.py:58` already gets the actionable set by
  parsing `inbox_sweep.py` stdout section headers, which needs no ruling and fails silently to
  "no work" if a header is reworded.
- Card 3 (pair-selector Phase 1) still deferred behind the OSC-031 KEEP/REVERT.

Both remain carded elsewhere; neither is postponed by this message, so no new `DEFERRED:` card
is owed here.

## For the owner, in plain words

It worked. You gave the workers hands at 13:41; four minutes later the doorbell rang by itself,
a session started with nobody watching, read your ruling, answered it, filed the paperwork and
pushed it — and this sentence was typed by that session. The era of starting sessions by hand is
over. The honest caveat: the locks are off, so what keeps these sessions in bounds is the rulebook
and the fact that everything they do is written down where you can read it.
