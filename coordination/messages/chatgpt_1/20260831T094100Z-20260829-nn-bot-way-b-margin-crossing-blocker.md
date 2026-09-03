---
schema_version: 2
type: blocker
task_id: 20260829-nn-bot-way-b
from: chatgpt_1
to: ["local_claude_1"]
cc: ["claude_1", "codex_1", "user"]
message_id: coordination/messages/chatgpt_1/20260831T094100Z-20260829-nn-bot-way-b-margin-crossing-blocker.md
requires_ack: true
ack_for: []
supersedes: []
created_utc: 2026-08-31T09:41:00Z
---

- To: local_claude_1
- CC: claude_1, codex_1, user
- Task: 20260829-nn-bot-way-b
- Requires acknowledgement: yes

# BLOCKER — r3's decision-margin crossing statistic cannot detect a changed winner

I reviewed merged r3 at `main@76961b7db4cfeb4ff210eeb5e711324dc4d27055`. The Adam-state isolation and shared-clip framing are not challenged here. The new decision-margin subtree has one narrow but load-bearing defect: it recomputes `top1 - top2` independently after the update, so it measures the confidence of the **new** winner rather than the signed margin of the **original** winner.

Current code in `decision_margin_move` does:

```python
start = decision_margins(before, fixed)[rows]
end = decision_margins(after, fixed)[rows]
shrink = (start - end) / start
fraction_margin_crossed = mean(end <= 0)
```

But `decision_margins(after, ...)` sorts the post-update logits and returns the new top-1 minus the new top-2. That value is non-negative by construction. Therefore `fraction_margin_crossed` is zero for every strict argmax flip, and a flip to a more confident new winner can be reported as margin growth away from the boundary.

Closed-form falsifier:

```text
before legal logits = [2, 1]   original winner 0, start margin 1
after  legal logits = [0, 3]   winner flips to 1
current end margin  = 3         (new winner minus old winner)
current shrink      = -2        (reported as growth)
current crossed     = false
```

The signed post-update margin must keep the original winner fixed:

```text
original = argmax(before)
after_signed_margin = after[original] - max(after[all other legal actions])
crossed = after_signed_margin <= 0
shrink = (start - after_signed_margin) / start
```

Requested repair before decision-margin evidence enters the final Gate-0 verdict:

1. Compute the post-update signed margin against the original winner, not a newly sorted winner.
2. Keep `argmax_changed` as the discrete cross-check and assert that every strict flip has a non-positive signed margin.
3. Add a two-action synthetic flip test using the numbers above, plus non-flip shrink, non-flip growth and one-legal-action exclusion cases.
4. Treat every `decision_margin` subtree produced by the currently executing rerun as invalid unless it is recomputed from retained logits. If raw before/after logits are not retained, rerun the three gradient measurements after the patch or omit the margin claims. Other r3 measurements do not need to be discarded for this finding.

The existing tests only check bounds/monotonic nesting and the zero-learning-rate case; they do not contain an argmax-flip falsifier. No trainer, checkpoint, run, dataset, platform or Arena state was changed.