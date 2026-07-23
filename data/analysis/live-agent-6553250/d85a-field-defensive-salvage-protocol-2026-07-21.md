# D85a current-field one-turn defensive salvage — frozen protocol (2026-07-21)

## Question

D78 shows that attacks on resident-owned crops are observable from current target geometry. D82
shows semantic response headroom in a local macro controller, but D83 cannot predict terminal arm
value and D84 shows that exact online rollout value arrives too late for the 50 ms limit. Before
abandoning the field signal, does the actual stable resident miss a sparse, exact one-turn salvage
action when an opponent is already standing on its crop?

D85a is a passive open-replay causal command audit. It substitutes one resident command while
holding the recorded simultaneous opponent command and every other command fixed for that one
referee step. It cannot establish terminal value, create a candidate, open confirmation, or touch
the platform.

## Frozen corpus and trigger

Use only the verified open products of immutable snapshot `20260721T105508Z-d61p` and stable
resident agent `6561795`. Never read `processed/sealed_confirmation/`. Reconstruct every crop
created solely by the resident and every post-turn state `t` with a recorded next turn.

Retain one row per live crop generation and turn when all are observable at state `t`:

1. at least one opponent unit stands on the crop with positive CHOP and free capacity;
2. at least one resident unit also stands on the crop; and
3. at least one of the frozen responses below is physically available.

There is no outcome-based thinning. Preserve D78's opponent-account partition exactly. The attack
label is one only when the next recorded command produces a referee-confirmed opponent CHOP on
that crop. Trigger precision is evaluated separately on held opponent accounts; the label never
selects an action.

## Frozen response rules

All unit ties prefer the smallest id after the stated productive keys.

- `harvest`: available when the crop has fruit and an on-crop resident has positive HP and free
  capacity. Select maximum `min(HP, free)`, then HP, then free capacity.
- `joint_chop`: available only when no harvest response is available, crop health is at most the
  maximum visible CHOP of an on-crop opponent, and an on-crop resident has positive CHOP and free
  capacity. Select maximum resident CHOP, then free capacity.
- `salvage`: the fixed deployable rule—harvest when available, otherwise joint-chop when available.
- `control`: exact recorded resident commands.

An arm is an intervention only when the selected resident's recorded command is not already the
same verb. Replace that unit's first assigned command in place; preserve TRAIN and all other
resident commands. Hold the complete recorded opponent command fixed. Each treatment lasts one
turn only.

The rule uses current crop condition, unit positions/stats/carry, and ownership only. It may not
use the next command, attack label, opponent identity, future state, game result, or final score.

## Frozen exact-step execution and integrity

Run the complete extraction twice, once with 20 processes and once with one process, and require
byte-identical sorted rows. Decode one state per trajectory turn plus initial state, exact final
inventories, zero unknown updates, exact resident-only provenance, and no confirmation access.

For each trigger, replay control through the checked-in exact engine and compare it with the
official next state. Require:

1. zero command parse or arm-accounting failures;
2. exact target plant state/absence and exact economic state of every on-target involved unit in
   100% of triggers;
3. exact full inventories, scores, unit economic signatures, and plant signatures in at least 95%
   of triggers (movement-only differences are allowed and reported); and
4. every unavailable arm and unchanged same-verb arm reproduces control exactly.

Integrity failure quarantines trigger precision and treatment value and permits only a mechanical
repair.

## Frozen support, observability, and immediate-value gates

Before treatment interpretation, discovery and validation must each contain at least 16 trigger
rows, at least eight confirmed attacks, both seats in the complete corpus, and at least four
opponent accounts with triggers. The complete corpus must contain at least 16 changed `salvage`
interventions and at least one semantic response with eight changed interventions.

On held-account validation, the observable trigger must have next-turn confirmed-attack precision
at least 85%. No probability model or threshold is fitted.

Evaluate the complete fixed `salvage` policy on all baseline-conformant validation triggers,
including false-positive attacks and already-correct controls. Liquid value is current score plus
carried fruit plus four times carried wood. Require all:

1. mean one-turn liquid-margin gain at least +0.25 over all trigger rows;
2. at least 50% of changed interventions strictly improve and at most 5% regress;
3. mean own liquid delta nonnegative and mean opponent liquid delta nonpositive;
4. zero treatment-only resident-crop deaths;
5. at least four validation opponent-account means nonnegative and the worst nonnegative; and
6. at least eight changed validation interventions.

Report semantic arm availability/value, confirmed-versus-unconfirmed trigger effects, command
verbs replaced, target survival/health/fruit, cargo transfer, and an immediate hindsight oracle
descriptively. None can replace the fixed-rule conjunction.

## Decision rule

- **All integrity, support, trigger-precision, and fixed-rule gates pass:** open D85b, a resident
  source integration plus disjoint closed-loop local qualification. D85a itself is not a candidate.
- **Mechanism/value failure with support:** close on-crop one-turn salvage; do not tune the trigger,
  response priority, lethal condition, thresholds, or consumed open rows.
- **Support failure:** preserve the field observation but do not integrate; the opportunity is too
  sparse for this snapshot. Do not lower floors or read sealed confirmation.
- **Integrity failure:** quarantine all value and repair only the exact-step defect.

No result authorizes TestSession, submission, resident replacement, sealed data, or Arena action.
