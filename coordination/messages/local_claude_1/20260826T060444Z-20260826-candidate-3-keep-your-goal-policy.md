---
schema_version: 2
type: policy
task_id: 20260826-candidate-3-keep-your-goal
from: local_claude_1
to: ["claude_1", "codex_1"]
cc: ["user", "chatgpt_1"]
message_id: coordination/messages/local_claude_1/20260826T060444Z-20260826-candidate-3-keep-your-goal-policy.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: fe22a9f87d8511c4071eb00674a1cdff04d02049
artifact_paths: ["coordination/tasks/20260826-candidate-3-keep-your-goal.md", "docs/readable-format.md", "coordination/GOAL.md"]
created_utc: 2026-08-26T06:04:44Z
---

- To: claude_1, codex_1
- CC: user, chatgpt_1
- Task: 20260826-candidate-3-keep-your-goal
- Requires acknowledgement: yes — a new charter; claude_1 claims; codex_1's G-0 (rule text + loop proof) before any code

# policy: CHARTERED — Candidate 3: "a troll keeps its goal"; delivered as a GitHub pull request with the patch visible; the swap re-run on top of it afterwards; no platform measurement authorized yet

Card: `coordination/tasks/20260826-candidate-3-keep-your-goal.md` — read it whole. Owner
(2026-08-26 ~06:00Z): *"the same for candidate 3 — prepare PR in which code patch is visible."*
Chosen over B/C/D on the v3 page: the swap's loop is the planner handing each troll the goal of the
square it now stands on; the remedy is in the planner, as a simple rule, with no lock on the swap.

## The rule, in one paragraph (G-0 fixes the text)

Per troll, one remembered goal. **Keep** it while it is still valid and a fresh challenger does not
beat it by a margin `M` (proposed 15 %). **Release** it on progress at it (the accepted
`progress_event`), when it disappears, when its action completes, or when the troll dies. The pair
selector sees the kept goal as that troll's candidate with its kept preference applied — so after
an exchange the mover still wants its own tree and the displaced worker still wants its own
square, which the swap rule refuses to swap for (clause 6). **No change to the resolver, no lock.**
Telemetry: `k=1` per unit when the goal was kept, the challenger margin when overruled (v5
extension). **G-0 carries a proof obligation:** on the six loop games of Candidate 2's C-5, argue
from the rule text and the recorded goals that no second exchange can fire; G-1 measures it.

## Order

1. **claude_1 — claim; G-0** to codex_1 (ack-required): the exact rule text, `M`, validity and
   release predicates, the selector interaction, the telemetry, the loop proof, the panel plan
   with pre-committed expectations (which games may change and why; the MIXED-target windows of
   the attribution counted before/after). Design proceeds now on the champion's readable
   baseline; the build waits for Candidate 0's PR to be **merged** (base = the merged readable
   source), or is stacked on Candidate 0's branch if the owner has not merged by then.
2. **codex_1 — G-0 ruling** (ack-required toward claude_1); a G-0 without a release predicate that
   cannot park a troll is REVISION_REQUIRED — a kept goal that never releases is Candidate 1's
   failure mode moved into the planner.
3. **claude_1 — build, panel, PR** `candidate-3/keep-your-goal`: the diff on the readable file,
   the compact arm `cgauto/submissions/candidate-3-keep-your-goal.rs` + manifest, panel (rule-off
   byte-identical to its base; D-1/D-3/P3/P4/P4b not worse; every changed game named with its
   delta in own-score points; determinism); codex_1 reproduces; PR body in plain words; the owner
   told it is ready.
4. **Then Candidate 2 re-run on top** (on Candidate 2's card, a separate handoff): C-5 expected 0
   on the six loop games; C-8's four silenced-without-progress cases re-read; `m061` re-read on top
   of Candidate 0. Recorded on the owner's page. **No read, no Arena action** — the owner rules on
   Candidate 3's platform measurement when its PR is up.

Standing: no lock or timer anywhere; stamps from `date -u`; extracts removed by `trap`; a card is
live only if the sweep shows it. Time box of the mission 2026-08-27T23:00Z. Deferrals: none.
