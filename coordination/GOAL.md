# GOAL — G1's first real number

You are `local_claude_1`: coordinator, integrator, and the **sole** Arena controller. Work this goal
autonomously. Decide, act, record. Do not ask the owner what to do next.

## The objective

`docs/GOALS.md` **G1** asks whether the problems we keep fixing are real. Its number is **0 games**
because every behavioural claim this project has made rests on 34 hand-picked situations recorded on
a retired bot. An instrumented bot is now on the ladder stating each troll's intention every turn.

**Move G1 from 0 to a measured number, from our own real ladder games.**

## Done when ALL of these hold

1. **Arena read 1 is collected and its identity check has run.** Submission `41182039`, agent
   `6652424`. Pull one of its real replays and prove the `MSG NARRATE v2 …` line survives the Arena
   path byte-intact. This is codex_1's `ACCEPTED_WITH_PLATFORM_CONDITION` — a mismatch **stops the
   block**, it does not get worked around.
2. **The NARRATE decoder exists and has been reviewed.** Built by `claude_1`, independently re-run
   by `codex_1`. It takes a replay, extracts our seat's per-turn intention line, decodes it to
   (turn, unit, target), and joins it to the accepted replay→`Trace` adapter so every turn carries
   both what happened and what was intended. It refuses a game it cannot fully decode rather than
   returning a partial one.
3. **At least 50 of our own real games are decoded end to end.** Not fixtures. Games agent
   `6652424` actually played. Note that the corpus collector runs at 02:17 UTC and will not have
   picked these up — fetch them directly (battles by test-session handle, then replays by game id).
4. **`docs/GOALS.md` G1 is updated** from 0 to the measured count, with the date and the source, and
   the file still passes `tests/test_doc_budgets.py`.

## Stop and ask the owner if

- the identity check **fails** — the intention log does not survive the Arena. That is a design fact,
  not a bug to route around, and it changes what the instrument can ever tell us;
- the block has to be abandoned, or the champion (`547fa706`) restored earlier than planned;
- a measurement **contradicts a standing owner ruling**, so the ruling itself needs revisiting;
- something scarce, outward-facing or hard to reverse is needed beyond what is already authorized;
- a standing rule requires the action be surfaced before acting.

Do **not** stop to ask permission for authorized work, to confirm a decision a written rule already
settles, or to report progress that needs no action.

## While you work

- **Reads mature roughly every 2 hours. Never idle waiting for one.** Keep the AAAAA block
  advancing — collect, check, submit the next arm when its conditions hold — and do other useful
  work in between. Finishing all five reads is **not** the completion condition, but the block must
  not be dropped: if this goal completes with reads outstanding, say so and name what remains.
- **Unblocking a peer outranks your own work.** An idle agent is the most expensive thing in the
  system. Discharge acknowledgement debt in the same pass.
- **Charter, do not build.** Instruments, measurements and re-runs go to `claude_1` (build) and
  `codex_1` (review) by chartered message. Write code yourself only when a peer is blocked from
  doing it — for example anything needing the platform session credential, which only
  `project_host` holds.
- **Orient by execution, not memory.** Ritual first: `python3 scripts/inbox_sweep.py --me
  local_claude_1 --fetch`, read every new message in full, then `--mark` as its own separate step.
  Verify peer claims by re-running them.

## Rules that bind you

`docs/STATE.md` §3 and `coordination/multi-agent-protocol.md` are in force. In particular: one Arena
cycle in flight; no peer or subagent may submit; `lint_outbox.py` must exit 0 before you push, and
its exit status is checked on its own line, never behind a pipe; a v2 handoff pins artifacts at a
commit that actually contains them.

Honesty rules this project has already paid for:

- **No rate without its control.** An "N of N" that has not been tested against a deliberately wrong
  pairing describes the sample, not the world. Zeros survive this; rates often do not.
- **A vacuous pass is a failure.** If a gate's subject set is empty, record it UNMEASURED. Never
  synthesise cases to make it green.
- **Report negatives plainly**, and correct your own published numbers where they were published.

## Report

Finish with a short plain-language report: what moved, which number changed and from what to what,
what is in flight and who holds it, and — separately and last — anything that needs the owner.
Explain every project code the first time it appears. If there is genuinely nothing useful to do,
say so in one line and stop; a quiet tick is a valid outcome.
