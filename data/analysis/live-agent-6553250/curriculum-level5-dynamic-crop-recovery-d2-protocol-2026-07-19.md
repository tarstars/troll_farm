# Curriculum Level 5 dynamic crop-site recovery D2 protocol — frozen 2026-07-19

## Question

Does deterministic crop-site replanning repair the complete-active-opponent feasibility failure,
or is the remaining gap caused by broader rival growth and resource competition?

The rejected complete-baseline D0 failed at 57.4%; 212/213 teacher failures ended without the
tracked crop and 186 teacher selections targeted an occupied planned cell.  The accepted natural
forager proves that movement and initial fruit competition alone are already solved.  D2 tests the
localized site-validity mechanism on fresh development seeds 1,000--1,499.

## Paired environments

Both arms use the identical deterministic complete Rhea/SchedBot FastState opponent, eight recipes,
player-0 teacher, reward, success contract, 240-turn horizon, and observation/action ABI.

- **Fixed-site control:** the rejected D0 environment, with one crop cell chosen at reset.
- **Dynamic-recovery candidate:** before the tracked player-0 crop exists, if the planned cell is
  occupied by any plant, deterministically call the unchanged free-home-cell selector again.  The
  selector retains its existing ordering: water-adjacent first, then home radius, `(y, x)`.

The candidate changes `planned_crop` only.  The existing move mask and objective-distance channel
automatically reflect that coordinate.  It does not reserve a cell, remove an opponent plant,
change planting legality, grant inventory, alter the opponent, add a channel, or change terminal
credit.  Once player 0 creates the tracked BANANA crop, replanning stops.

## Integrity gates

- deterministic repeat identity for both arms;
- all prior waiting, natural-forager, and complete-opponent tests remain passing;
- unchanged 104x11x22 observation and 13x11x22 action ABI;
- complete opponent materially activates and exceeds one worker in at least 95% of both arms; and
- identical recipe assignment for each paired seed.

## Consumed D2 decision gates

Run the fixed teacher control and dynamic teacher candidate on all 500 seeds.  The dynamic arm must:

- reach at least 90% overall and 85% nontrivial success;
- reach at least 75% in every recipe and 80% in every height;
- reach at least 90% crop creation and 85% renewable harvest;
- emit zero illegal teacher selections;
- improve overall success and crop creation by at least 25 percentage points over the paired fixed
  control; and
- preserve material/multiworker complete-opponent activation at at least 95%.

Failure closes this exact replanning rule without tuning on seeds 1,000--1,499.  Passing permits
random-legal and accepted-Level-4 zero-shot diagnostics on the dynamic arm, followed by a separate
prospective protocol.  No training or prospective seed is authorized by D2 itself.

## Exclusions

D2 does not change crop radius/order, opponent constants, recipe selection, worker count, reward,
network, recurrence, teacher action priorities, deployment, field gates, or Arena state.  It is a
single state-validity recovery mechanism under a paired complete-opponent challenge.
