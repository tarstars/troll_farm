# D141a task-balanced best-stop selection — frozen protocol

Date: 2026-07-22  
Status: frozen after D140 closure and before any D141 fit

## Hypothesis

D140 closes the unchanged D138 learner on eight-block transfer. Its raw gate recalls only
13.79%--16.23% of held positive tasks at zero while recalling 81.13%--87.22% of waits. D137's
hard-stop BCE is flattened across valid roots: tasks average 5.54 roots and reach 25, so long tasks
and their negative roots receive more objective mass even though selection metrics weight tasks
equally.

Retain D140 exactly except for hard-stop normalization. Continue to use D137's temperature-10
soft task-choice cross entropy. For the hard term, first compute a loss per task:

- a positive task assigns half its hard-loss mass to its one best positive root and half to the
  mean of its valid negative roots;
- if a positive task has no negative root, use its positive loss alone;
- a wait task uses the mean loss of its valid negative roots; and
- average these task losses equally, independent of root count.

The soft and new hard terms retain coefficient 1. Keep the `379 -> 16 -> 1` ranker, `84 -> 8 -> 1`
winner gate, 6,786 parameters, 80+80 epochs, seeds 13401/13701 through 13404/13704, D138's exact
positive-stop count plus three percentage points, and first-positive runtime unchanged.

## Selection and execution

Use D133 blocks 0--3 and D139 blocks 4--7. Train eight leave-one-block-out folds for every seed
pair, with the same parent-loaded read-only fold and four one-thread fork workers as D140. Apply
the unchanged held gates and family-floor-first selection key. Require a second complete selection
artifact to match byte-for-byte. Abort rather than swap-thrash.

An eligible exact repeat permits one all-eight-block fit and the unchanged consumed-D126 veto.
D126 cannot tune, select, recalibrate, or rescue the controller. Only a complete veto pass may
open the still-untouched seeds `9,843,800--9,843,815` under a separate frozen protocol.

D141 cannot collect maps, integrate Rust, submit, mutate the resident, or interact with
TestSession/Arena.
