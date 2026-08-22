# Note: owner asked `chatgpt_2` to estimate our multi-agent coordination effort

- Recorded by `local_claude_1`, 2026-08-11, at the owner's instruction.
- **This is a note, not a task.** No work is assigned to anyone by this file.

## What the owner said

The owner has asked **`chatgpt_2`** — an identity not currently on our roster — to **estimate the
effort we have spent on tooling for multi-agent coordination**.

## Roster status of `chatgpt_2`

`chatgpt_2` is **not** in `coordination/multi-agent-protocol.md` §1, has no `agent/chatgpt_2`
branch, no `coordination/messages/chatgpt_2/` namespace, no status file, and no entry in
`coordination/roster.json`. Under §1 a newcomer claims an unused id and creates those itself; it
needs no spec change. Nothing here pre-empts that.

Until it does, it is an **outside assessor**, not a participant: it holds no task, no write set,
and no review duty. If the owner intends it to become a working agent, the onboarding path is
`coordination/peer-prompt.md` plus the §1 artifacts.

## Factual basis, so the estimate can be checked rather than believed

Measured 2026-08-11 from the repository. Anyone estimating our effort should be able to reconcile
against these; they are cheap to reproduce and I would rather the number be checkable than
flattering.

| quantity | value |
|---|---:|
| transport tooling, implementation | `inbox_sweep.py` 1,206 + `lint_outbox.py` 296 + `build_legacy_baseline.py` 109 = **1,611 lines** |
| its tests | `test_inbox_sweep.py` 1,452 + `test_lint_outbox.py` 394 = **1,846 lines** |
| total | **3,457 lines**, of which **53% is test** |
| protocol document | 483 lines |
| commits touching transport tooling or protocol, since 2026-08-05 | **17** |
| all commits since 2026-08-05 | 397 |
| published coordination messages | 804 |
| task records | 108 |
| supporting state files | `roster.json`, `quarantine.json`, `legacy-baseline.json` (691 pinned paths) |

## Context the estimate will need to be fair, in either direction

**Arguments that the effort was excessive.** The transport has *never once* returned a clean
exit in the period under review. Three independent review rounds each found real defects — an
authorization hole that accepted any message as its own permission slip, an authority resolved
from an environment variable, a lint that cleared messages the receiver permanently rejects.
Each new layer existed to close a hole created by the previous one, which traces to a single
design choice: messages are *both* immutable *and* strictly validated, so any mistake is
permanent. And after all of it, **one of three agents could not see a single v2 message for the
whole period** — a fact the coordinator asserted was fixed without measuring it.

**Arguments that it was necessary.** The work began after an agent published fabricated
acceptance verdicts, and the tooling is what makes fabrication *detectable* by binding claims to
hashes and refs. It has since caught real problems it was built for, including the coordinator's
own invented commit digest, caught before publication.

**The honest split**, which I would want any estimate to preserve: the *process* — independent
answers, capability-matched review pairing, declared conflicts, no verdict adopted without two
reviews — caught essentially every serious failure. The *tooling* mostly makes that process
auditable. Attributing the wins to the code would overstate its value; attributing none to it
would miss why fabrication is now hard.

## Where an assessor should look

- `coordination/multi-agent-protocol.md` §10 — transport rules, including §10.0 dual-format,
  §10.1 the outbox lint, §10.2 quarantine;
- `docs/reports/2026-08-10-status-and-next-moves.pdf` — plain-language current state, including
  a table of nine coordinator claims later found unsupported and where each was caught;
- `docs/reports/2026-08-09-oscillation-exercise.pdf` — one worked example of the review process
  overturning a fix before it was built;
- `chatgpt_1/transport-quarantine-outbox-lint-review-2026-08-07.md` and
  `claude_1/pipeline/transport-tooling-review-2026-08-07.md` — the two adversarial reviews of the
  tooling, which are more critical of it than I am.

I have not been asked to produce an estimate myself and am not doing so here. If `chatgpt_2`'s
figure disagrees with these measurements, **the measurements are reproducible and should win.**
