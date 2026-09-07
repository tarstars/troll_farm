# Claude-led development, Astra checkpoints

The owner requested this workflow on 2026-09-06 to conserve primary-model tokens.
Optimize for tested improvements and real competitive outcomes, not report count.
`EVALUATION.md` remains the authority for measuring progress toward rank <=7.

## Division of work

- Claude owns code discovery, implementation, focused tests, experiments, debugging,
  and concise evidence reports. Use the installed `claude-proxy` wrapper unchanged.
- Astra assigns a bounded outcome, reviews the result and relevant risky changes,
  and chooses accept/revise/stop. Astra coordinates platform evaluation/publication.
- Only one writer/expensive local panel runs at a time. Do not edit files owned by
  another active job. Existing untracked work is preserved, not silently adopted.

## One batch

1. Read `WORKSTATE.md` and the latest result, not the full history. Write a short
   ticket: outcome, owned files, hypothesis, baseline, test budget, decision rule,
   permitted external actions, and stop condition. Freeze comparisons before use.
2. Run `bash run_claude_task.sh TASK.md 30`. The helper uses a lock and wall-clock
   limit, preserves logs under working storage, and returns a compact `RESULT.md`.
   Default 30 minutes; at most 60 for an explicitly larger batch. Do not retry an
   interrupted job until inspecting its process state and partial outputs.
   Claude receives an absolute UTC deadline and high reasoning effort. Timing checks
   must run without competing panels/compiles; collect launched jobs before returning.
3. Claude implements and checks the whole scoped task, including ordinary repairs,
   without asking Astra about routine choices. Aim for a runnable candidate in the
   first batch; use diagnostics only to resolve a named implementation blocker.
   At most two predeclared candidate variants per batch, not endless parameter scans.
4. Astra reads the <=400-word result, a diff summary, then only necessary evidence
   and changed code. Independently rerun a focused check; deepen review for unsafe
   transactions, simulator changes, evaluation logic, or publication tooling.
   A Claude verdict alone is not verification. Do not duplicate the whole analysis.
5. Accept, request one targeted repair, or close the tested implementation. Record
   the current state and one next action in `WORKSTATE.md`; keep it <=80 lines.
   Detailed reports/logs stay in their run directories and are linked, not copied.

## Token and experiment discipline

- Target <=2,000 Astra tokens per ordinary review checkpoint. This is an operating
  target, not an enforced billing cap; report when a substantial review needs more.
- No continuous primary-agent waiting/polling loop. Inspect at completion or on a
  user status request; use product completion notifications where available.
- No automatic unlimited research loop. One ticket buys one bounded batch. Continue
  with a new ticket only while active user authorization covers the work; stop for
  missing authority, a material choice, or repeated failures needing a new direction.
- Run focused tests while iterating. Full regression and exact-export checks are
  for a finalist or cross-cutting changes, not every analysis-only result.
- A failed shallow learner does not prove all cheap strategies impossible. A small
  local win does not predict ladder rank. Use precise, implementation-level claims.
- Negative results count as information, not bot improvement. After two batches
  without a runnable candidate or newly resolved deployment blocker, stop expanding
  analysis and use one short review to choose a concrete implementation or park it.
- Existing official comparison rules still apply. Do not tune on confirmation data,
  drop deployment failures, repeatedly resubmit failed source hashes, or substitute
  an arbitrary local score threshold for competitive evidence.

## Handoff and publication

`RESULT.md` (<=400 words): verdict; changed files and candidate source hash; test
commands and measured results; evidence paths; limitations; one next action.
Keep full logs out of Astra's context unless diagnosing a specific failure.

Ordinary tickets are offline. A platform ticket must identify exact source/opponents,
request budget, decision rule, and whether unranked tests or publication are allowed.
The supplied launcher is offline-only; Astra runs platform tickets separately.
Publish one reviewed exact candidate at a time and retain its identity. During
rollout, delegate useful offline work. Success requires the mature exact-agent
top-seven observation defined in `EVALUATION.md`, not a transient placement.

The helper's allowlisted tools and task instructions are not a filesystem security
sandbox. Read-only neighbor access remains a strict working rule. The wrapper's
existing authentication is preserved; subscription coverage and billing are not
verified by this workflow. No paid-API fallback or account changes are authorized.
