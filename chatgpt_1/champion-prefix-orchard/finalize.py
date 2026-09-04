#!/usr/bin/env python3
from __future__ import annotations

import collections
import json
import math
import random
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIR = ROOT / "chatgpt_1" / "champion-prefix-orchard"
RESULT = json.loads((DIR / "results" / "result.json").read_text())
ARTIFACT = "2fc4d285c391b66fc575ae2fec00d0957ea3c9e2"
INCOMING = "coordination/messages/local_claude_1/20260904T133200Z-20260904-champion-prefix-orchard-handoff.md"
OUTGOING = "coordination/messages/chatgpt_1/20260904T144000Z-20260904-champion-prefix-orchard-handoff.md"


def ci(values, seed):
    values = list(map(float, values))
    n = len(values)
    rng = random.Random(seed)
    means = [statistics.fmean(values[rng.randrange(n)] for _ in range(n)) for _ in range(10000)]
    means.sort()
    return {
        "n": n,
        "mean": statistics.fmean(values),
        "lower95": means[int(.025 * 9999)],
        "upper95": means[int(.975 * 9999)],
    }


def fmt(value):
    return f"{value:.2f}"


normal = RESULT["normal"]
choices = normal["per_map_oracle_choices"]
all_rows = normal["all_policy_rows"]
oracle_rows = [all_rows[name][index] for index, name in enumerate(choices)]
oracle_margin = ci((row["delta_margin"] for row in oracle_rows), 20260910)
oracle_own = ci((row["delta_own"] for row in oracle_rows), 20260911)
oracle_signs = collections.Counter(
    "positive" if row["delta_margin"] > 0 else "negative" if row["delta_margin"] < 0 else "zero"
    for row in oracle_rows
)
choice_counts = collections.Counter(choices)
valid = RESULT["mechanics"]["globally_valid_policies"]
invalid_count = len(RESULT["mechanics"]["invalid_policies"])
fixed = normal["policy_summaries"]

# Descriptive only: calibration of the hindsight per-map upper bound.  Infinite
# row ratios are represented plainly when a forecasted tree yielded no wood.
ratios = []
predicted = 0.0
realized = 0.0
for row in oracle_rows:
    p = float(row["predicted_orchard_wood"])
    a = float(row["realized_orchard_wood"])
    predicted += p
    realized += a
    if p > 0:
        ratios.append(math.inf if a <= 0 else p / a)
ratios.sort()
p90 = None if not ratios else ratios[min(len(ratios) - 1, math.ceil(.9 * len(ratios)) - 1)]

policy_table = []
for name in valid:
    summary = fixed[name]
    policy_table.append(
        "| {name} | {m:.2f} [{ml:.2f}, {mu:.2f}] | {o:.2f} [{ol:.2f}, {ou:.2f}] | {p:.2f} | {f:.2f} |".format(
            name=name,
            m=summary["delta_margin"]["mean"],
            ml=summary["delta_margin"]["lower95"],
            mu=summary["delta_margin"]["upper95"],
            o=summary["delta_own"]["mean"],
            ol=summary["delta_own"]["lower95"],
            ou=summary["delta_own"]["upper95"],
            p=summary["plants_mean"],
            f=summary["fells_mean"],
        )
    )

final = f"""# Champion-prefix orchard experiment — final result

Date: 2026-09-04  
Task: `20260904-champion-prefix-orchard`  
Artifact pin: `{ARTIFACT}`  
Verdict: **`DEAD_ON_NORMAL_PAIRED_REPLAY`**

## Answer

A small fixed near-shack orchard added after the unchanged champion's own second troll **does not beat the champion's continuation in this experiment**. The registered primary selector — leave one map out, choose one globally valid policy on the other 23 maps, then score it on the held-out map — selected **`NO_PLANT` in all 24 folds**. Therefore paired final margin and paired own score are both exactly **0.00**, with 95% bootstrap intervals **[0.00, 0.00]**.

This triggers the pre-registered dead condition that the paired final-margin lower bound must be above zero. The experiment stopped before high raid, panel, holdout, or ladder work.

## Integrity and mechanics

- The executable in both arms was the unchanged champion, SHA-256 `{RESULT['champion']['sha256']}`.
- All candidate streams were byte-identical to the champion through its own second `TRAIN`.
- The second troll's talent tuple and training turn were unchanged on every run.
- Third training was disabled; `NO_PLANT` was always legal.
- Baseline mechanics were clean on all 24 map-seats.
- Six instrument tests passed, including the planter self-occupancy regression.
- The corrected experiment evaluated 20 planting policies on 24 maps, plus 24 cached champion baselines: **504 complete 300-turn executions**.
- **{invalid_count}/20** planting policies were rejected because they introduced a new long-inactivity interval; this alarm is not called a loss or crash.

The first execution had a real instrument defect: when the planter reached its target, the target was rejected because it was occupied by the planter itself. That run planted zero trees and was discarded. The repair changed only that transition and added a test; policies and thresholds remained frozen. The artifact pin above is the corrected execution.

## Fixed-policy results

Only three planting policies survived the activity gate on every map. None had positive mean paired margin:

| fixed policy | Δ final margin, mean [95% CI] | Δ own score, mean [95% CI] | plants/game | fells/game |
|---|---:|---:|---:|---:|
{chr(10).join(policy_table)}

The best planting policy by mean margin, `BANANA-s100-k4-d4`, still measured **−1.58** margin points per game. Its own-score mean was +0.38, but both intervals crossed zero and opponent score moved enough to make final margin negative. The in-sample global choice was therefore also `NO_PLANT`.

## Heterogeneity, and why it is not a rescue

A hindsight per-map oracle chose an orchard on **16/24** maps and `NO_PLANT` on **8/24**. Counts were:

```json
{json.dumps(dict(sorted(choice_counts.items())), indent=2)}
```

That hindsight upper bound had paired margin mean **{fmt(oracle_margin['mean'])}**, 95% interval **[{fmt(oracle_margin['lower95'])}, {fmt(oracle_margin['upper95'])}]**, and paired own-score mean **{fmt(oracle_own['mean'])}**, interval **[{fmt(oracle_own['lower95'])}, {fmt(oracle_own['upper95'])}]**. Map signs were `{dict(oracle_signs)}`.

This is descriptive only: it chooses after observing the exact final result on the same map. It demonstrates map-dependent opportunity, not a deployable selector. The registered leave-one-map-out rule could not predict those maps and correctly fell back to the champion. Building a map classifier now from the same 24 development maps would be post-result tuning and is outside this card.

The hindsight rows also do not pass the wood-calibration idea cleanly: predicted convertible wood totaled **{predicted:.2f}**, realized orchard wood **{realized:.2f}**, and the row-wise 90th-percentile overstatement is `{'infinite' if p90 == math.inf else p90}` because some selected orchard plans predicted wood but banked none. This is another warning against treating the oracle upper bound as a policy.

## Interpretation

The positive kinetics result remains true: nearby mature banana wood is much faster to convert than distant wild wood. What failed is the stronger whole-game claim that a simple fixed orchard schedule captures enough of that advantage after paying its opportunity cost. The champion already uses those workers, cells, seeds, and opponent interactions; a locally attractive reserve often displaced more valuable continuation work.

The experiment also confirms that preserving the champion prefix repairs the architectural disease seen in the previous builds. The orchard result is not confounded by an altered second troll. It is simply not positive under a policy that generalizes across these development maps.

## Recommendation

**Close this orchard-optimizer line and do not give it a ladder slot.** Do not tune start turns, counts, inactivity thresholds, or a map selector on these 24 maps. Preserve the per-map heterogeneity as a clue for future strategic work, but a new orchard card would require a genuinely new, pre-specified map-conditioned signal and fresh development cases—not another sweep of this grid.

Per the task card, `claude_1` should now independently reproduce the measurement without reading this implementation. No ladder, platform, Arena, panel, holdout, cluster, champion, or `main` action was taken.

## Reproduction

```bash
bash chatgpt_1/champion-prefix-orchard/run.sh
```

Raw policy-by-map rows are in `results/result.json`; the frozen policy and action manifests are `policies.json` and `action-vocabulary.json`.
"""
(DIR / "FINAL.md").write_text(final)

status = f"""# chatgpt_1 status

- Updated UTC: 2026-09-04T14:40:00Z
- Branch: `agent/chatgpt_1`
- Identity: original `chatgpt_1` — opening-solver review, DP oracle, Rust anytime planner
- Current task: `20260904-champion-prefix-orchard`
- State: complete; dead on registered normal paired-replay condition; handoff published

## Result

The unchanged champion prefix and second `TRAIN` were preserved exactly. Twenty planting policies were evaluated over 24 development map-seats; 17 failed the long-inactivity guard. Of the three globally valid planting policies, all had negative mean paired final margin. The registered leave-one-map-out selector chose `NO_PLANT` in all 24 folds, giving Δmargin 0.00 [0.00, 0.00] and Δown 0.00 [0.00, 0.00].

Artifact pin: `{ARTIFACT}`  
Report: `chatgpt_1/champion-prefix-orchard/FINAL.md`  
Raw result: `chatgpt_1/champion-prefix-orchard/results/result.json`

## Disposition

Close the line; no ladder slot and no tuning on the 24 development maps. `claude_1` is requested to reproduce independently under the task card. No platform, Arena, panel, holdout, cluster, champion, or `main` action was taken.
"""
(ROOT / "coordination" / "status" / "chatgpt_1.md").write_text(status)

handoff = f"""---
schema_version: 2
type: handoff
task_id: 20260904-champion-prefix-orchard
from: chatgpt_1
to: ["local_claude_1"]
cc: ["user", "claude_1", "chatgpt_2"]
message_id: {OUTGOING}
requires_ack: true
ack_for: ["{INCOMING}"]
supersedes: []
artifact_ref: agent/chatgpt_1
artifact_commit: {ARTIFACT}
artifact_paths: ["chatgpt_1/champion-prefix-orchard/FINAL.md", "chatgpt_1/champion-prefix-orchard/RESULTS.md", "chatgpt_1/champion-prefix-orchard/results/result.json", "chatgpt_1/champion-prefix-orchard/oracle.py", "chatgpt_1/champion-prefix-orchard/policies.json", "chatgpt_1/champion-prefix-orchard/action-vocabulary.json", "coordination/status/chatgpt_1.md", "coordination/BOARD.md"]
created_utc: 2026-09-04T14:40:00Z
---

# HANDOFF — champion-prefix orchard is dead on normal paired replay

The owner-authorized experiment is complete at the artifact pin. The unchanged champion was the executable in both arms and every candidate command stream was byte-identical through the champion's own second `TRAIN`; the second troll's specification and turn never changed. Third training was disabled and `NO_PLANT` was legal.

After correcting a tested planter self-occupancy instrument bug without changing the frozen grid or thresholds, the oracle evaluated 20 planting policies over 24 development map-seats plus cached champion baselines. Seventeen planting policies introduced a new long-inactivity interval and were excluded. The three globally valid planting policies all had negative mean paired final margin. The registered leave-one-map-out selector chose `NO_PLANT` in all 24 folds:

```text
Δ final margin: 0.00, 95% bootstrap interval [0.00, 0.00], n=24
Δ own score:    0.00, 95% bootstrap interval [0.00, 0.00], n=24
```

This triggers dead condition 3. High raid, panel, holdout and ladder stages were not run. A hindsight per-map oracle chose an orchard on 16/24 maps, but that is an optimistic upper bound selected from the same final outcomes, not a policy; the pre-registered cross-map selector could not generalize it.

**Recommendation: close row 3-8, no ladder slot, no parameter or map-selector tuning on this development set.** Per the card, please charter `claude_1` to reproduce the measurement independently without reading this implementation. The detailed fixed-policy decomposition, hindsight upper bound, calibration warning and reproduction command are in `FINAL.md`.
"""
out = ROOT / OUTGOING
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(handoff)

board = ROOT / "coordination" / "BOARD.md"
text = board.read_text()
old = "Last updated: 2026-09-04T13:3xZ — "
new = (
    "Last updated: 2026-09-04T14:4xZ — **ROW 3-8 COMPLETE AND DEAD ON ITS REGISTERED NORMAL PAIRED-REPLAY GATE:** "
    "chatgpt_1 preserved the unchanged champion through its own second `TRAIN`, evaluated 20 planting policies on 24 development map-seats, and the leave-one-map-out selector chose `NO_PLANT` in all 24 folds (Δmargin 0.00 [0.00, 0.00]; Δown 0.00 [0.00, 0.00]). Seventeen planting policies failed the long-inactivity guard; all three globally valid planting policies had negative mean margin. No high-raid, panel, holdout or ladder work followed. Artifact `2fc4d285c391b66fc575ae2fec00d0957ea3c9e2`; `claude_1` is now due to reproduce independently. Previous: 2026-09-04T13:3xZ — "
)
if old not in text:
    raise SystemExit("BOARD update boundary not found")
board.write_text(text.replace(old, new, 1))

# The branch-only execution workflows have served their purpose.  Removing
# them prevents accidental reruns after the dead verdict.
for rel in (
    ".github/workflows/chatgpt1-champion-prefix-orchard.yml",
    ".github/workflows/chatgpt1-champion-prefix-orchard-finalize.yml",
):
    path = ROOT / rel
    if path.exists():
        path.unlink()

print(json.dumps({
    "artifact": ARTIFACT,
    "verdict": RESULT["verdict"],
    "valid_policies": valid,
    "invalid_planting_policies": invalid_count,
    "primary_margin": normal["leave_one_map_out_delta_margin"],
    "primary_own": normal["leave_one_map_out_delta_own"],
    "hindsight_oracle_margin": oracle_margin,
    "hindsight_oracle_own": oracle_own,
    "hindsight_choice_counts": dict(choice_counts),
}, indent=2, sort_keys=True))
