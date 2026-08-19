# 20260819-sentinel-wake-on-work — the blocking inbox sentinel + its description

- Status: OPEN — OWNER-CHARTERED 2026-08-19 in session ("create task for
  claude_1 to implement this tool and .md description for it"). Design:
  owner's sentinel variant, recorded in
  `docs/superpowers/specs/2026-08-19-doorbell-wake-on-work-design.md`
  (amendment at top).
- Record owner: local_claude_1 · Work owner: **claude_1** ·
  Reviewer: **codex_1** (tool review, instrument-first standards) ·
  Integrator: local_claude_1
- Area: coordination transport tooling (`scripts/`, `docs/`); no game code.
- Priority: **does NOT preempt the owner's predictor-fix focus lane** — work
  it after gate-1-lane items in your queue, or in its review gaps.
- Created UTC: 2026-08-19T13:21:42Z (clock-read; first draft carried a
  predicted stamp — caught pre-publication, the standing lesson)

## THE GOAL

Two deliverables, one review unit:

1. **`scripts/sentinel.py`** — a no-LLM blocking watcher an agent runs in its
   session background; it hangs while nothing changes and EXITS when that
   agent's actionable set grows, so the harness re-invokes the agent warm.
2. **`docs/sentinel.md`** — the plain-language description + operator manual
   (what it is, how to start it, exit codes, the restart ritual, failure
   modes, what it deliberately does not do).

## Behavior contract (from the accepted design conversation)

- `sentinel.py --me <agent>`: snapshot the agent's **actionable set** using
  `inbox_sweep` AS A LIBRARY (shared-runners rule — never a reimplemented
  scan): (a) unseen messages addressed to the agent (to/cc), (b) ack-required
  messages awaiting THAT agent's ack, (c) the agent's own self-addressed
  `DEFERRED:` items still unacked. Then loop: `git fetch origin` (default
  every 45 s; `--interval` flag; metered-network flag file → back off to
  10 min) → recompute → on GROWTH relative to the snapshot: **print the
  triggering paths, one per line, and exit 0**.
- **Exit codes are the whole interface:** 0 = work (paths on stdout) · 2 =
  max-lifetime keepalive reached (default 6 h, `--max-lifetime`; agent does a
  liveness sweep and restarts) · 3 = N consecutive fetch failures (default 5;
  agent reports transport trouble instead of guessing) · 1 = refused to start
  (pidfile shows a live sibling; stale pidfiles broken with a log line).
- `--notify` mode (owner channel): never exits on work; emits a
  desktop/Telegram notification for messages addressed to `user` carrying
  owner-decision content. May be delivered as a stub honoring notify-send
  only; channel choice stays an owner activation item.
- **No LLM anywhere; no message-body interpretation** beyond the sweep's own
  fields; read-only on git (fetch only — never merge, never mark, never
  touch `inbox-seen.json`).

## Gates (fail-first, the house standard)

1. **Per-harness re-invocation verified BY EXECUTION, not assumption:** show
   a real background-started sentinel exiting and the harness re-invoking the
   agent, for (a) Claude Code and (b) the codex_1 harness. This is the
   design's load-bearing assumption; if either harness lacks the behavior,
   STOP and report — do not build around it silently.
2. **Controls observed firing both ways:**
   - a message pushed for the agent → exit 0 with exactly the new paths;
   - a message for a DIFFERENT agent only → keeps hanging (no exit);
   - keepalive timeout → exit 2 (use a short `--max-lifetime` in the test);
   - fetch failure injection → exit 3 after N;
   - double start → exit 1, first instance untouched;
   - seen-state and `inbox-seen.json` byte-identical before/after a full run.
3. **codex_1 review** of tool + doc + test evidence as ONE unit (the
   instrument-and-result lesson applies to tools).
4. Integrator then wires the ritual text (protocol §10 amendment: "restart
   the sentinel as the last action") — AFTER review, not before.

## Boundaries

No Arena action, no resident/game code, no protocol edits by this task (the
ritual amendment is the integrator's, post-review). No standing activation:
agents ADOPT the sentinel only after the owner's separate go on the rollout
(spec §Rollout). The tool must be safe to run and kill at any time.

- Authority: owner charter in session, 2026-08-19.
