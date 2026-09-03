---
schema_version: 2
type: handoff
task_id: 20260901-cleanroom-champion
from: chatgpt_1
to: ["local_claude_1"]
cc: ["claude_1", "codex_1", "user"]
message_id: coordination/messages/chatgpt_1/20260901T112200Z-20260901-cleanroom-champion-review-handoff.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260901T095136Z-20260901-cleanroom-champion-review-handoff.md"]
supersedes: []
artifact_ref: agent/chatgpt_1
artifact_commit: 48c343d89b6565639de6a22eca32fd513ca56e9a
artifact_paths: ["chatgpt_1/cleanroom-champion/cross-review-2026-09-01.md"]
created_utc: 2026-09-01T11:22:00Z
---

- To: local_claude_1
- CC: claude_1, codex_1, user
- Task: 20260901-cleanroom-champion
- Requires acknowledgement: yes

# HANDOFF — adversarial clean-room package cross-review

I reviewed the exact owner-restructured package pinned by your superseding charter:

```text
agent/local_claude_1@1286af7571c4f50bb10fe534fc2e9811bdd3a8b0
```

The full review is pinned at:

```text
agent/chatgpt_1@48c343d89b6565639de6a22eca32fd513ca56e9a
chatgpt_1/cleanroom-champion/cross-review-2026-09-01.md
```

## Verdict

```text
BLOCKED_PENDING_TARGETED_CORRECTIONS
```

The package is strong and should survive one narrow correction round, but the fresh implementer
must not receive it yet.

## Ranked blockers

1. **P0 — wrong core behaviour.** Part I/A5.2 says pre-251 conversion starts whenever at most
   four trees remain. The reference also requires being behind in score. The current extractor
   proves only that observed early starts had <=4 trees; it does not prove the converse. Correct
   the replay measurement, the trigger, and the “solitaire” claim.
2. **P0 — third clean-room channel.** The stripped executable remains inspectable machine code,
   and the harness offers an unlimited exact-action oracle before version 0. Freeze a complete
   v0 before releasing the reference binary; forbid or technically prevent binary inspection;
   pre-register and archive the one refinement query budget.
3. **P1 — physics boundary mismatch.** `RULES.md` omits legal TRAIN talent ranges; the harness
   accepts impossible bundles, misstates multiple TRAIN success and shack occupancy, and can
   crash on `PLANT IRON/WOOD` where the platform rejects non-fatally. Add adversarial boundary
   tests and re-run parity.
4. **P1 — missing strength-relevant behaviour.** Part I omits two-worker target coordination,
   while “take each tree all the way down” is not established by A4.1. Measure co-targeting,
   blocking, target reservation and post-first-chop persistence, or mark them open.
5. **P1 — causal labels overclaim.** ESSENTIAL is defined as direct evidence that removal makes
   the bot weaker, but several uses are observational or arithmetic-plus-inference. Use an
   evidence-shaped label taxonomy or require an ablation/dominance proof.

The review also lists eight exact wording corrections, citation spot checks, a proposed top-ten
rebalance, and the minimum re-release gate.

The card's owner-review stop remains binding. No implementer, experiment, submission, ladder
read, leaderboard query or platform action was started by this review.