---
schema_version: 2
type: handoff
task_id: 20260815-banana-farm-two-specs
from: local_claude_1
to: ["codex_1", "claude_1"]
cc: ["user"]
message_id: coordination/messages/local_claude_1/20260817T091633Z-20260815-banana-farm-two-specs-v4-handoff.md
requires_ack: true
ack_for: []
supersedes: ["coordination/messages/local_claude_1/20260815T194221Z-20260815-banana-farm-two-specs-v3-handoff.md"]
artifact_ref: agent/local_claude_1
artifact_commit: 96f1b400ac53ea7b86738deb2ee5646456d45cba
artifact_paths: ["docs/superpowers/specs/2026-08-15-banana-farm-spec-a-unconditional.md", "docs/superpowers/specs/2026-08-15-banana-farm-spec-b-conditional.md"]
created_utc: 2026-08-17T09:16:33Z
---

- To: codex_1 (pool 7b re-review), claude_1 (informational)
- CC: user
- Task: 20260815-banana-farm-two-specs (pool item 7a → 7b)
- Requires acknowledgement: yes (codex_1)

# handoff: Spec v4 — both blocking corrections addressed; one scope question for the reviewer

Artifact `96f1b400`, pushed and remote-verified. Shared skeleton (§3–§8) re-verified
byte-identical between the two files after editing. Supersedes the v3 handoff.

## Correction 1 — the abort sensor's false "safe direction" claim (§7, both files)

Withdrawn and replaced with a BOTH-directions characterization:

- **fires too often** (total-outcome sensor; replant loop banks nothing) — as before;
- **fires too late or NEVER** (new): `score()` (:120–121) sums all banked stock and
  `WOOD_POINTS = 4` (:82) against 1 per banana — our trained troll's wood income can
  mask enemy banana gain, including gain from our own farm.

Added requirement: **measurement reports both** — every abort event, and every FARM
phase ending without one, logs each side's score growth since FARM entry decomposed
into wood and non-wood components. The provenance variant's adoption condition is now
symmetric (either failure mode material), not "fires too often" only.

## Correction 2 — K_futility (§4, both files)

- Relabelled **FROZEN, and a HEURISTIC**. The growth-cycle half of the justification
  stands (10 > the 8-turn base cooldown); the **"more than one in-flight chop" span
  claim is WITHDRAWN** — travel-plus-chop is unbounded by 10.
- **Completion gate added:** `futility_reached` additionally requires ≥1 COMPLETED
  focus-species chop of ours within the current non-decrease run (one boolean, no new
  constants, no ownership inference). A completed chop removes a tree, so non-decrease
  across a completion means the enemy replaced the species — the owner's "sustains
  against our chopping", made literal. A run with no completion can never latch,
  however long — the review's constructed in-flight case becomes structurally
  impossible rather than merely tested-against.
- **New acceptance gate GK** (§10, both files, Spec-B-phrased for its unconsumed
  latch): the in-flight negative arm and the replacement positive twin, both observed,
  fail-first.

## The scope question, asked openly

The completion gate is a small MECHANISM addition, not just text. Your review said
"no new design decision is required" and offered "add a constructed case … or provide
the missing bound". The missing bound does not exist (travel is unbounded), and a
constructed must-not-misfire case FAILS against the v3 mechanism by construction — so
the minimal way to satisfy your own required test is this gate. **Please rule in the
re-review whether it stays within textual/test-gate scope**; if you judge it a design
decision, it goes on the owner's approval list next to B-1 and the K_futility freeze
(it is flagged there in the text either way).

## For the owner, in plain words

Your two banana-farm rule books are corrected as the checker required. First, we no
longer claim the emergency-stop can only err by stopping too early — it can also stay
silent while the enemy raids the farm, because our wood income (worth four points a
log) can hide their banana gains; every stop, and every non-stop, will now be logged
with a wood-vs-fruit breakdown so both mistakes are visible in measurement. Second,
the "give up the chopping war after 10 fruitless turns" rule is now honestly labelled
a judgment call, and it gained a safeguard: it can only trigger if we actually
FINISHED cutting a tree in that window and the enemy replaced it — a troll merely
walking to a distant tree can no longer be mistaken for futility. Both books remain
identical in their shared parts, and the two decisions reserved for you (the B-1
floor and freezing the 10) are unchanged and clearly marked.

## Boundaries

No implementation, no resident mutation, no Arena action. Owner approval remains the
gate after 7b. The two OWNER-DECISION items (B-1, K_futility) stand as flagged.
