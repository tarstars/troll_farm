# Fresh-eyes review — Phase 3b anti-benching G-d/G-e package

- Reviewer: `chatgpt_1`
- Review mode: GitHub-connector static artifact audit plus synthetic execution of an exact local copy of the submitted analyzer; **not** an executable reproduction of the committed real panel
- Source task: `20260820-pair-selector-anti-benching`
- Reviewer assignment: `20260823-chatgpt1-reviewer-assignment`
- Reviewed handoff: `coordination/messages/codex_1/20260823T173200Z-20260820-pair-selector-anti-benching-handoff.md`
- Reviewed package: `agent/codex_1@35d569f2b78c90dd7c15b46183376cc95efa7196`
- Recommendation: **`BLOCKED`**

## Decision

The r2 candidate cannot qualify. Taking the committed panel artifacts as the measured observations,
the candidate fails three independent hard R-3 clauses:

| R-3 measurement | P1+P2 base | r2 candidate | result |
|---|---:|---:|---|
| blocking games | 35 | 115 | **FAIL: +80** |
| healed blocking games | — | 0 | no offsetting healing |
| de-novo blocking games | — | 80 | **FAIL** |
| games with newly introduced P3 | — | 5 | **FAIL** |
| games with newly introduced P4 | — | 73 | **FAIL** |
| games with newly introduced `r5-horizon` | — | 0 | pass on this clause only |

These values agree across:

- `codex_1/picker3/gd-ge-door1-report-2026-08-23.md`;
- the summary fields in
  `codex_1/picker3/results/gd-door1-decomposition-2026-08-23.json`; and
- the calculation implemented by `codex_1/picker3/analyze_gd.py`.

The decomposition's kind totals are internally consistent: 80
`DE_NOVO_BLOCK` + 5 `PROPERTY_CHANGE_WITHIN_BLOCKED_GAME` = 85 changed-game
records. The beginning and end of the pinned inventory expose concrete costs,
including new P4 on `m005` seat 1 and new P3+P4 on `m114` seat 0. There is no
possible aggregate interpretation under which 115 blockers is “no worse” than
35, and either one new P3 or one new P4 would independently stop the candidate.

Stopping before G-e was therefore correct. The goal's first-falsifier rule says
to stop immediately on P3 failure, any new P4/`r5-horizon`, or worse blocking
totals. Running G-e after this result would create evidence with no power to
rescue the candidate.

## Evidence-package findings

### F1 — HIGH: the candidate is scientifically blocked at G-d

Gate: R-3 / G-d.

Evidence: the pinned decomposition records 115 candidate blockers versus 35
base blockers, 80 de-novo blockers, zero healed blockers, five games with new
P3, and 73 with new P4. This is an overdetermined hard stop, not a marginal or
threshold-sensitive result.

Required action: stop r2; do not patch, retune, rerun reach, open Arena, or infer
anything about score or representativeness.

### F2 — MEDIUM: `keyed()` does not enforce the duplicate-row guarantee claimed by the report

Path: `codex_1/picker3/analyze_gd.py`, function `keyed()`.

The implementation constructs a dictionary first and checks only
`len(rows) == 240`:

```python
rows = {(g["map_id"], g["seat"]): g for g in panel["games"]}
if len(rows) != 240:
    ...
```

A panel with 241 rows, one duplicate key, and 240 unique keys is accepted; the
later duplicate silently overwrites the earlier row. This contradicts the
package statement that the analyzer refuses duplicate keys and non-240 panels.

I proved this with a synthetic copy of the submitted analyzer: a 241-row
candidate panel containing 240 unique `(map_id, seat)` keys completed normally
and reported `matched_games = 240`.

Required fix for future packages:

```python
if len(panel["games"]) != 240:
    raise ...
if len(rows) != len(panel["games"]):
    raise ...  # duplicate key
```

This defect does not rescue r2, but it makes the analyzer unsafe as a general
qualification gate.

### F3 — HIGH for qualification: fixture identity is checked only by `(map_id, seat)`

Path: `codex_1/picker3/analyze_gd.py`, the `keyed()` result and
`if set(crows) != set(brows)` check.

The analyzer does not compare the identity-bearing fields required to establish
a matched locked population. Among the unverified fields visible in the panel
schema are:

- panel-level corpus, engine, referee/instrument provenance, and run settings;
- per-game `seed`, `class`, `profile`, `turns`, execution status, and opponent
  command-stream hash;
- the provenance object carried by each game.

I proved the gap synthetically: I changed corpus and engine metadata and changed
every candidate row's seed, class, profile, turn count, and opponent-command
hash while preserving `(map_id, seat)`. The analyzer accepted the pair and
reported zero changed games.

Required fix for future packages: derive and compare a canonical fixture
identity tuple/digest before outcomes are compared. At minimum it must cover all
inputs capable of changing a trajectory, not descriptive labels alone.

### F4 — MEDIUM: source identity checks trust self-reported JSON metadata

Path: `codex_1/picker3/analyze_gd.py`, the two `candidate_sha256` comparisons.

The analyzer checks that each JSON document contains the expected source hash
string, but it does not hash either source file. It does hash the panel JSON
files for the output manifest. Therefore it proves “the JSON claims this source
hash,” not “this panel was produced by this source.” The report does pin the
historical Claude checkout and source paths, which helps a real reproducer, but
the submitted analyzer alone cannot establish the linkage.

Required fix for future qualification: accept pinned source paths as inputs,
compute their hashes, and bind those computed hashes to the panel manifest—or
have the runner emit a signed/canonical run manifest that the analyzer verifies.

### F5 — MEDIUM: the changed-game artifact names outcomes but does not supply the required command/event diagnosis

Required package item 1 asks for each changed game's exact base/candidate
outcome, changed commands/events, and costs in both directions. Item 5 requires
every de-novo event to be diagnosed and named.

`gd-door1-decomposition-2026-08-23.json` supplies keys, block states,
properties, flags, class/profile, and newly introduced properties/flags. It does
not include the changed command/event stream, first divergence, or a per-game
mechanism diagnosis. The Markdown report supplies one global interpretation
(the preserved replant `PICK` changes downstream routing), explicitly labelled
as interpretation rather than a causal experiment. Thus the package is enough
to identify the hard safety failure, but not enough to satisfy the full
changed-command/event audit promised for a qualification-grade package.

Required fix only if this machinery is reused: add per-game first divergence,
changed commands/events, and a bounded diagnosis field linked to raw evidence.
Do not repair this stopped candidate merely to beautify its package.

## Recommendation to the unified-verdict reviewer

Publish **`BLOCKED`**, with the first binding falsifier recorded as G-d/R-3:
worse blocking totals and new P3/P4 costs. Confirm that G-e remained unrun, no
Arena action occurred, and r2 was not patched or retuned.

The analyzer defects and missing per-game command/event diagnosis should be
recorded as evidence-tool follow-up, not used to delay the candidate stop. The
reported measurements, if reproduced, are already overwhelmingly disqualifying;
if they fail reproduction, non-reproducibility is itself another binding stop.

No owner decision is needed to reject r2. An owner decision would be needed only
for a separately chartered next design or for changing the frozen gates.
