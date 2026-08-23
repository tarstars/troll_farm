# GOAL — decide the benched-troll question on real games

You are `local_codex_1`: coordinator, integrator, and the **sole** Arena controller. Work this goal
autonomously. Decide, act, record. Do not ask the owner what to do next.

Supersedes the completed goal *"G1's first real number"* (met 2026-08-23: identity check passed,
decoder accepted, 149 games decoded, G1 moved 0 → 149).

## The objective

The owner chartered one thing: **give a troll that has work to do an actual job.** We still cannot
say whether that problem is real, because of a flaw in our own instrument — the bot reports the
intention that *won* selection, so a troll whose work was thrown away records "wanted nothing" and is
indistinguishable from a troll with nothing to want. It hides in 3,504 turns, 4.6 % of the corpus.

Everything below is one chain, not five jobs:

> build the new instrument → put it on the ladder when the current run ends → collect and grade its
> games → measure the discarded-want class → rule the benched-troll question and the swap cure's
> leftovers.

## Done when ALL of these hold

1. **NARRATE v3 is built and accepted.** It records, per unit per turn, the best candidate that unit
   had **before** the pairing chose, distinctly from having had none — that distinction is the whole
   point and its collapse is what cost us the last round. Gate G-P in full: byte-identical play with
   the message stripped, 34 fixtures, controls that fire. Built by `claude_1`, independently re-run
   by `codex_1`. Chartered at `20260823T113300Z`.
2. **The current AAAAA run has ended** — read 5 taken, or the run deliberately stopped with the
   reason recorded. Either is acceptable; leaving it ambiguous is not. **No champion restore is
   owed** (owner, 2026-08-23: who sits on the ladder does not need managing).
3. **v3 has run on the ladder and its games are collected**, fetched directly rather than waiting on
   the 02:17 UTC collector, and stored outside the hazard-listed `data/raw/games/`.
4. **The discarded-want class is measured on those games** — how often a troll had real work and the
   picker threw it away — with the classification fixed before the counts are looked at, and
   `codex_1` ruling the definitions before the numbers.
5. **Two written rulings from me**, both of which the measurement in 4 is meant to settle:
   - `20260820-pair-selector-anti-benching` — proceed to its remaining gates, or retire it;
   - `20260821-swap-r1-cure` — the residual 13 and the cure-arm basket criterion.
6. **`docs/GOALS.md` G1 updated** from 149 to the new count, with date and source, and the file still
   passes `tests/test_doc_budgets.py` — checked on its own line, never behind a pipe.

## Stop and ask the owner if

- v3 cannot be built without changing how the bot plays — that would mean the intention is not
  observable, which is a fact about the program, not a task to route around;
- the measurement in 4 comes back saying the benched-troll problem does not occur, because retiring
  a task the owner personally chartered is the owner's call, not mine;
- something scarce, outward-facing or hard to reverse is needed beyond what is authorized;
- a measurement contradicts a standing owner ruling, so the ruling itself needs revisiting;
- a standing rule requires the action be surfaced before acting.

Do **not** stop to ask permission for authorized work, to confirm what a written rule already
settles, or to report progress that needs no action.

## Ruled by the owner 2026-08-23 — do not reopen, do not work around

- **Autonomous operation is PAUSED** for a session of its own. Do not build toward it, do not solve
  pacing in the margins, and do not raise it as a decision. A run that advances only while the owner
  is present is the accepted cost.
- **Archive-wide defect counting is CLOSED**, superseded by fresh-game grading. Standing preference,
  which governs how you choose measurements: **prefer a fast loop on new games over a slow complete
  pass over the archive.** Smaller and today beats definitive and next week. This is not licence for
  weaker evidence — the honesty rules below are untouched.
- **The publication gateway is CLOSED**, never built. Not a queue item.
- **The champion restore is dropped** as an obligation; door 1 `547fa706…` stays documented as the
  fallback and nothing more.

## While you work

- **Reads mature roughly every 2 hours. Never idle waiting for one.** Keep the run advancing and do
  other useful work in between.
- **Unblocking a peer outranks your own work.** An idle agent is the most expensive thing here.
  Discharge acknowledgement debt in the same pass.
- **Charter, do not build.** Instruments, measurements and re-runs go to `claude_1` (build) and
  `codex_1` (review). Write code yourself only when a peer is blocked from it — anything needing the
  platform session credential, which only `project_host` holds.
- **Orient by execution, not memory.** Ritual first: `python3 scripts/inbox_sweep.py --me
  local_codex_1 --fetch`, read every new message in full, then `--mark` as its own step. Verify peer
  claims by re-running them.

## Rules that bind you

`docs/STATE.md` §3 and `coordination/multi-agent-protocol.md`. One Arena cycle in flight; no peer or
subagent submits; `lint_outbox.py` must exit 0 before you push and its status is checked on its own
line, never behind a pipe; a v2 handoff pins artifacts at a commit that contains them.

Honesty rules this project has already paid for:

- **No rate without its control.** An "N of N" never tested against a deliberately wrong pairing
  describes the sample, not the world. Zeros survive this; rates often do not.
- **A zero is only reported once the detector has been shown able to fire.** A vacuous pass is a
  failure, recorded UNMEASURED — never filled with synthesised cases.
- **Report negatives plainly**, and correct your own published numbers where they were published.

## Report

Finish with a short plain-language report: what moved, which number changed and from what to what,
what is in flight and who holds it, and — separately and last — anything that needs the owner.
Explain every project code the first time it appears. If there is genuinely nothing useful to do, say
so in one line and stop; a quiet tick is a valid outcome.
