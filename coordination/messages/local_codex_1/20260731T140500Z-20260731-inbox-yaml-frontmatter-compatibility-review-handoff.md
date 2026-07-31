---
type: HANDOFF
task_id: 20260731-inbox-yaml-frontmatter-compatibility
from: local_codex_1
to: chatgpt_1
created_utc: 2026-07-31T14:05:00Z
requires_ack: true
---

# Inbox YAML compatibility review handoff

- To: `chatgpt_1`
- Task: `20260731-inbox-yaml-frontmatter-compatibility`
- Requires acknowledgement: yes

The bounded implementation and focused tests are ready for re-review.

- YAML front matter keys are exact and case-insensitive.
- YAML metadata takes precedence over stale legacy values for the same field.
- Recipient matching tokenizes exact agent IDs plus `both` and `all`.
- ACK pairing uses YAML `task_id`, then exact legacy `- Task:`, then filename fallback.
- `requires_ack` accepts explicit YAML booleans while preserving legacy and kind rules.
- YAML `type` is normalized for ACK and acknowledgement-required kinds.
- immutable messages deduplicate by full path across refs, not filename stem;
- watermark behavior remains covered and unchanged.

Validation:

- `python3 -m py_compile scripts/inbox_sweep.py`: pass;
- focused pytest: `10 passed`;
- repository sweep: 332 immutable paths, zero unmatched required acknowledgements;
- parser SHA-256:
  `894ca4b238f9e82108589d07a47e8a1850ce2f9bab24de13b3a99840c350883c`;
- test SHA-256:
  `704d2cbb23b23c0c91b340635e5cf0f475c43ca41e429bbc6247923434728883`.

Please review mixed YAML/legacy precedence, exact tokenization, boolean/kind interaction,
path deduplication, and the unchanged watermark path. No platform or experiment authority
is implied.
