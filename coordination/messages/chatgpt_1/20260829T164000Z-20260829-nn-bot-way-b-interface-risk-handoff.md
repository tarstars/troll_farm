---
schema_version: 2
type: handoff
task_id: 20260829-nn-bot-way-b
from: chatgpt_1
to: ["local_claude_1"]
cc: ["codex_1", "claude_1", "local_codex_1", "user"]
message_id: coordination/messages/chatgpt_1/20260829T164000Z-20260829-nn-bot-way-b-interface-risk-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/chatgpt_1
artifact_commit: 2f46e531447e6a575d07bb4cc81f81d85293fd05
artifact_paths: ["chatgpt_1/nn-way-b/interface-risk-audit-2026-08-29.md"]
created_utc: 2026-08-29T16:40:00Z
---

- To: local_claude_1
- CC: codex_1, claude_1, local_codex_1, user
- Task: `20260829-nn-bot-way-b`
- Requires acknowledgement: yes — please rule whether these become exact interface edits before the dataset pilot
- Artifact: `agent/chatgpt_1@2f46e531447e6a575d07bb4cc81f81d85293fd05`

# HANDOFF — Way B is viable, but the current Rust/Python boundary can create wrong labels and a roster-dependent PPO objective

Owner-directed fresh-eyes audit completed against `main@bcef07ef`, `agent/codex_1@2c5519f8`, and `agent/claude_1@0ac974d8`. I claim no build row and no competing review authority; `local_claude_1` remains the assigned reviewer.

Four findings need an early ruling:

1. **Seat frame is absent from the action codec.** Observations and masks are player-relative, but `tf_full_encode_command` / `tf_full_decode_action` have no seat. They cannot by themselves encode an absolute seat-1 reached cell into the relative action index required by the dataset.
2. **Non-spatial command encoding cannot produce the canonical legal label.** The mask places verbs at the active troll's relative cell; the implementation returns `plane * 242`, coordinate `(0,0)`, because the helper has no active-cell input. The undocumented caller-side relocation must become an explicit API or the helper must be narrowed to MOVE only.
3. **`tf_full_obs_from_state` is semantically fail-open.** It accepts impossible phase/active/plan combinations and malformed staged-action sequences; negative staged actions are coerced and other invalid entries are ignored. This can normalize extraction bugs instead of failing the 1,000-state drift gate.
4. **The signed reward rule duplicates one full-turn reward over `n+1` mini-step transitions.** A conventional PPO loop then optimizes `(n+1) * reward` while `episode_returns` records reward once. Because `n` changes with training, the objective depends on roster size. Turn-boundary reward/discount semantics must be frozen before PPO.

Recommended immediate sequence:

```text
seat-aware + active-cell-aware codec
→ strict reconstructed-context validator
→ both-seat/all-verb conformance fixtures
→ explicit turn-boundary reward and GAE rule
→ continue environment/dataset integration
```

The artifact gives exact failure cases, API options, and negative controls. It does not ask to abandon Way B or stop mechanics work. It asks not to freeze labels or accept the PPO wrapper until the boundary is coherent.

Pinned audit:

`agent/chatgpt_1@2f46e531447e6a575d07bb4cc81f81d85293fd05:chatgpt_1/nn-way-b/interface-risk-audit-2026-08-29.md`

No code, build, test, environment, dataset, trainer, panel, submission, or Arena state was changed or run.
