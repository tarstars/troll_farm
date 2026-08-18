# METHODS LEDGER — how this team measures and coordinates, lesson by lesson

Consolidated 2026-08-18 (iteration pool #8, integrator). Sibling of
`docs/RULES-LEDGER.md`, which holds owner-approved rules about WINNING THE GAME;
this file holds the rules about DOING THE WORK — measurement, review, and
coordination methods, each earned by a named incident and cited by exact path;
entries are referred to by slug (e.g. "verdict-equals-message"). Owner-ruled
entries are law; the rest are standing team rules unless the owner
overrules. Transport rules that are already lint-enforced (WIP limit, evidence
gate, canonical v2 kinds — `coordination/multi-agent-protocol.md`) are not
restated here.

## shared-runners — reuse the shared runner or prove parity; never re-implement the loop

A half-copied loop is how a mirror disagrees with its authority. Audit runners
REUSE the shared runner, or prove parity with explicit controls (plain/plain,
omitted-grow). This project paid twice: `next_cell` (main/sim divergence era)
and the h-starve-1 runner bug (2026-08-16).

- Origin: `coordination/messages/local_claude_1/20260816T163830Z-20260816-h-starve-1-runner-bug-adjudication-ack.md` item 5.

## observed-failing — every new check is observed FAILING before its green is trusted

Fail-first is not waived by the author's honesty about debt; a check that has
never failed has never been shown to check anything. Applied from fixture gates
(cure-C G1: fixtures observed failing on the unmodified resident) to negative
controls (walled-in / zero-capability arms observed firing).

- Origin (standing formulation): `coordination/messages/local_claude_1/20260816T182042Z-20260816-t1-gates-integration-ack.md` Ruling 2.
- Instance (2026-08-18, chop4c r2): a module contract LISTED a reordered-chain
  negative control that was never built, while the reconciler sorted rows
  before checking order — a check structurally unable to see the disorder it
  existed to detect. claude_1's own naming, adopted: **"a claim carried by
  prose instead of by execution"** — docstrings and contracts assert nothing;
  only an observed failure does.
  (`codex_1/reviews/osc031-chop4c-instrument-r2-review-2026-08-18.md`;
  repaired same hour with the control observed failing,
  `coordination/messages/claude_1/20260818T082319Z-20260818-osc031-instrument-r3-handoff.md`.)

## matched-floors — compare only against a MATCHED floor

Numbers from a different pairing, corpus, instrument, or config are "two numbers
that are not the same thing". When a charter's reference numbers turn out
mismatched, measuring a fresh matched floor (subject vs itself, same corpus,
same instrument, same config) is the correct execution of the reporting INTENT —
and the deviation is flagged visibly, never buried; the unreconciled reference
stays on the record as an open question.

- Origin: `coordination/messages/local_claude_1/20260816T182042Z-20260816-t1-gates-integration-ack.md` Ruling 1 (8.50%/2.88% references).

## verdict-equals-message — a verdict is not delivered until its MESSAGE is published

Pushing the review file is not publication. The message goes out in the same
push as the file, `requires_ack: true` whenever it changes anyone's queue — "a
verdict nobody must acknowledge is a verdict nobody is guaranteed to read."
Three parties made that mistake within twenty-four hours (spec-v3 verdict unread
26 h; stale "complete" status; the original no-ack spec verdict).

- Origins: `coordination/messages/local_claude_1/20260817T150607Z-20260816-h-starve-1-pool2-verdict-integration.md` §2;
  `coordination/messages/local_claude_1/20260817T090423Z-20260816-h-starve-1-pool1-reopened-redirect.md`.
- Instance 3 (2026-08-18, chop4c G-4c.2 stall — account CORRECTED same hour by
  the implementer): a reviewer's method APPROVAL went out `requires_ack: false`
  (the transport hazard: an approval that unblocks work changes a queue as
  surely as a ruling that reopens it — the second clause covers both
  directions). The implementer in fact READ it and deferred the build for a
  stated budget reason — but published no deferral, so their truthful
  "empty inbox" report implied "nothing in flight"; the coordinator meanwhile
  reported the build "presumably" in flight without checking that any message
  charged anyone (adjacent to no-unchecked-endorsement). Caught by the OWNER
  asking why idle agents contradicted the status. Refinement adopted from the
  implementer's own correction: **a deferral is a status, not a silence** — 
  "not started, deferred, because X" is published the moment the decision is
  made. Repair + correction:
  `coordination/messages/local_claude_1/20260818T093139Z-20260818-osc031-g4c2-build-directive.md`;
  `coordination/messages/claude_1/20260818T093409Z-20260818-osc031-g4c2-go-ack.md`.

## never-blind-mark — never `--mark` outside a displayed-and-read sweep

Marking inside automation chains is how delivered mail becomes invisible: a
publish chain that runs `--mark` right after fetch marks the just-arrived
verdict seen without it ever being displayed, defeating the ritual the mark
exists to serve. Sweep → read ALL new → then mark, as its own step.

- Origin: `coordination/messages/local_claude_1/20260817T162802Z-20260816-h-starve-1-pools-closed-and-record-correction.md` (the false "queue inversion"/"third quiet verdict" forensics).
- Instance 2 (self-reported near-miss, claude_1, 2026-08-18): marked a 3-unseen
  sweep having read 2 — a message arrived during the publish window. No content
  lost; caught by the count mismatch. Refinement adopted from the report:
  **re-count between the read and the mark** — the read set must equal the
  marked set at mark time, not at the earlier sweep.
  (`coordination/messages/claude_1/20260818T072908Z-20260818-osc031-controls-received-and-a-blind-mark.md`)

## no-unchecked-endorsement — never endorse a peer's claim about the record without checking the refs

An endorsement is a claim of my own. The integrator endorsed a false premise
("codex_1's only published work since was spec reviews") without checking the
refs, then built a public accusation on it; reflog proved the premise false, and
the endorsement was retracted with the claims. Verify by execution before
co-signing (the standing verify-by-execution trust posture, adopted after the
2026-08-06 fabricated-acceptance incident).

- Origin: same correction message as never-blind-mark, §2–3.

## self-audit-is-not-the-gate — self-audit is not a substitute for the review gate

(claude_1, verbatim, credited.) However many defects a self-audit fixes — even
with observed-firing evidence, even when the audit proves the CODE right and the
TEST wrong — the work still passes the independent review gate. Self-audit
raises the floor; it does not open the gate.

- Origin: `coordination/messages/local_claude_1/20260817T115452Z-20260816-h-starve-1-pool1-revision-ack.md` (deadlock paragraph).

## smuggled-verdict — self-criticism can carry a verdict

(claude_1, verbatim, credited:) "Withdrawing my own claim felt like rigour,
which is exactly why I did not notice it was still a claim." Phrases like
"over-counted", "the behaviour was correct", "explained" are VERDICTS even when
aimed at one's own work; attributions and measurements stand, scope and harm
judgments are the owner's. Neutral wording (e.g. "deliberate phase-gate
composition gap") until the owner rules.

- Origin: codex_1's catch, accepted at `coordination/messages/local_claude_1/20260817T190915Z-20260816-h-starve-1-pool5-revision-integration-ack.md`.

## arrival-order-queues — reviewer queues are consumed by arrival order (prophylaxis)

Unless the coordinator enforces priority per message — a queue note inside the
lower-priority handoff itself — same-day revisions arrive as fresh requests and
preempt the intended order. Recorded as caution, explicitly
never-instantiated-by-codex_1: the alleged 2026-08-17 instance did not occur
(see never-blind-mark's forensics); the one real occurrence was the integrator's own five
same-day spec revisions preempting pool #2.

- Origins: `coordination/messages/local_claude_1/20260817T134927Z-20260816-h-starve-1-queue-reassertion.md`;
  corrected scope per the never-blind-mark correction message.

## turn-coverage-de-novo — de-novo harm is counted in TURN COVERAGE (owner law, 2026-08-18)

A candidate's de-novo damage is judged by whether it ADDS newly-affected TURNS
versus the matched floor; episode-count deltas without turn coverage do not
convict (a fix that merges or re-times episodes is not thereby harming). Origin
case m106 (counting artifact cleared).

- Origin: owner ruling, `coordination/messages/local_claude_1/20260818T041052Z-20260817-cure-c-owner-rulings.md`.

## pre-existing-hole — the two-pronged exception, reviewer-verified (owner law, 2026-08-18)

A fix is not blamed for an OLD pothole it reaches by playing better — but only
when BOTH prongs are independently verified by the reviewer: (a) the candidate's
path into the state is legitimate better play, and (b) the hole pre-exists in
the resident in the candidate's live states. Origin case m061 (resident
generator probed WAIT-only on every probed turn of window 39–99). The named-cost
discipline rides with it: what the exception does NOT clear travels in every
report by name (m082, score 12 → 1).

- Origin: owner ruling, same message as turn-coverage-de-novo; verification method
  `codex_1/reviews/cure-c-g4-owner-rulings-review-2026-08-18.md`.

## probe-the-live-states — identity of outputs is not identity of mechanism

Byte-identical tails under a diagnostic variant prove nothing when the variant's
alternate branch is never entered — the identity was evidence of nothing.
Establish properties of a generator by probing it DIRECTLY in the exact states
at issue (codex_1's m061 method: `endgame_candidates` probed in the candidate's
live states). claude_1's acceptance on record: "the conclusion survives, the
reasoning is theirs."

- Origins: `codex_1/reviews/cure-c-g4-owner-rulings-review-2026-08-18.md`;
  `coordination/messages/claude_1/20260818T042800Z-20260817-cure-c-green-handoff-for-submission.md` §"Two corrections".

## clock-read-timestamps — timestamps are read off the clock, never predicted

`message_id` stamps come from `date -u` at write time. Future-stamping (writing
the timestamp you expect to publish at) produced a +50 min stamp on a published
message (2026-08-18) and +4 to +42 min drift across nine messages (measured
2026-08-12). A published wrong stamp is FLAGGED, never quietly renamed.

- Origins: `coordination/messages/claude_1/20260818T042800Z-20260817-cure-c-green-handoff-for-submission.md` §"Two corrections" (self-flag);
  stamp-drift measurement restated in `coordination/messages/local_claude_1/20260812T193800Z-20260810-guards-that-cannot-fail-quarantine-adjudication-v2-policy.md`.

## Cross-references (law living elsewhere)

- Owner top-down judgment rule (judge from game state down, never from code up;
  winning rules are the OUTPUT): `docs/ADJUDICATION-TEMPLATE-2026-08-15.md`,
  `docs/RULES-LEDGER.md`.
- M-1 measurement rule for paired Arena nights (ABAB @~2 h, paired-difference
  95% CI, σ=1.501, 1.0 materiality floor, max two extensions, honesty clause):
  `coordination/tasks/20260815-banana-farm-two-specs.md:103-117`.
- Plain-language rule for all owner-facing text:
  `coordination/multi-agent-protocol.md`.
- WIP limit / evidence gate / canonical kinds / quarantine authority:
  `coordination/multi-agent-protocol.md` + `scripts/lint_outbox.py`,
  `scripts/inbox_sweep.py`.
