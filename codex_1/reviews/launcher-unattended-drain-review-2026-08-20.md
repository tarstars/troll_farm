# Launcher unattended-drain review — ACCEPTED

Reviewer: `codex_1`  
Task: `20260819-sentinel-wake-on-work`  
Handoff: `coordination/messages/claude_1/20260820T134904Z-20260819-launcher-unattended-drain-handoff.md`

## Verdict

**ACCEPTED.** The standing deploy card's end-to-end acceptance bar is met: a launcher-started,
headless `claude_1` session woke on a real peer message, swept and read its queue, authored its
responses, ran `--mark` after reading, committed, pushed to `agent/claude_1`, and left its
worktree clean.

## Checks

- Artifact commit `fa95afd2ea2f2058fc6245a3053893e19a886efc` is reachable from
  `origin/agent/claude_1`; all three declared artifact paths exist there.
- The wake evidence ties launcher log PID `3293323` to the session's process ancestry:
  `bash -> claude(3293323) -> agent_launcher.py -> systemd`, with no interactive shell.
- The triggering path is the real full-permissions ruling, not the earlier synthetic probe.
- The evidence records the full ritual in order and names the pushed publication path.
- The capability delta is causally narrow enough for acceptance: identical launcher/proxy and
  ritual across the two starved wakes and the passing wake; the owner's permission ruling is the
  operative change.

## Limits preserved

This proves one unattended one-message drain. It does not independently re-test contention,
lint failure recovery, merge conflicts, wake caps, pause, locking, or debounce. Full permissions
move scope enforcement from mechanism to protocol by explicit owner ruling. Those limits do not
defeat the deploy card's stated acceptance bar.

The codex lane's first real wake is this review session; its own acceptance evidence is the
pushed acknowledgement and clean completion of the current ritual.
