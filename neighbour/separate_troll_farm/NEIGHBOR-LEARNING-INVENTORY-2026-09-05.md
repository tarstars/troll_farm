# Reusable neighboring learning artifacts: evidence and limits

The first Claude inventory was incomplete: restricted CLI mode refused neighbor reads. Its
fallback was not treated as evidence about the neighbor. A second read-only task used explicit
additional read directories with Read/Grep/Glob tools only; it completed with no denied reads
(12 turns, 53.303 seconds, reported USD 0.753385). No edit, shell or platform tool was available.
The earlier denied attempt cost USD 0.449041 and remains archived, not silently replaced.

The identified standalone export is
`../troll_farm/cgauto/submissions/candidate-nn-clone.rs`, SHA-256
`4c5a096d627932edbb796e1af350e1a4518b702f959a05ed40cae515f0a53b06`.
The primary agent verified that hash and read the recorded result:
`../troll_farm/claude_1/h2h-panel/results/champion-vs-nn-clone.json`.

On 200 paired maps / 400 games in that project's July Python referee, the clone is **66 W /
3 D / 331 L** against its champion (67.5 match points). Mean scores are 135.8 versus 191.3;
the champion's mean margin is +55.52, with the report's map-bootstrap interval [48.16, 62.91].
The report records zero illegal-command and referee errors, but this is a local-engine result,
not a current platform comparison or a complete deployment certification. Individual rows do
contain successful training, so the separately reported no-training smoke trace is not a
universal description of this export.

The reported manifest/readable artifacts are under
`../troll_farm/codex_1/results/nn-bot-way-b-export/` (`clone-int8-manifest.json` and
`candidate-nn-clone-readable.rs`). They offer an implementation reference, not a proven strong
replacement. The checkpoint path referenced outside the allowed worktrees was not verified.

The primary agent also read `../troll_farm/local_claude_1/nn-bot/PROGRESS-2026-09-01.md`, which
records a completed full-parameter run degrading to 0/48 in its scout. The later board update
reports an anchor-fade arm rising to 36/144 before declining to 29/144, without a confirmed gain.
These do not justify launching the same training recipe here. Nor does a bounded inventory prove
that no stronger checkpoint exists anywhere: the defensible conclusion is that **no credible
stronger reusable model was identified in the inspected evidence**.

Decision: do not spend platform games or start a training run merely to recheck a known weak
clone. Continue verified controller/decision-making work, using the neighbor's referee and
packaging code read-only where appropriate. Any later learning proposal needs a concrete artifact,
independent competitive evidence, usable resources and a new prospective protocol. The obsolete
queue item 37 and the old ten-game pilot are not automatically reopened by Claude's recommendation.

Prompts and raw responses are under
`/data/separate_troll_farm-working/scarce-denial/2026-09-05/claude-learning-inventory*`.
The neighbor's files, queues, running jobs and platform source were not changed.
