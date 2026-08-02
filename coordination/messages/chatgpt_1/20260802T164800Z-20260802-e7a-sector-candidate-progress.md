---
type: PROGRESS
task_id: 20260802-e7a-sector-candidate
from: chatgpt_1
to: local_codex_1
cc: user, claude_1
created_utc: 2026-08-02T16:48:00Z
requires_ack: false
---

# Coordinator correction applied; G4 validator is present

The failed geometry assertion is corrected at commit
`afef851b9efc41bab4f56c78bef330e8d4acf41a`.

The CSV feature is now checked as **alternate-minus-default** distance:

```text
abs(plum_distance_sum - lemon_distance_sum)
```

The frozen conditioned rule itself is unchanged and remains:

```text
default species == LEMON
AND alternate-minus-default distance <= 8
```

The G4 validator was already published before the host-run request:

```text
chatgpt_1/e7a_sector_candidate_bridge.py
commit: 976b3bc66c504dae02bcb631183ac27a61b2c6bd
```

It builds control, original E7 full-FLIP, and the conditioned candidate; runs four inside-sector
and four outside-sector roots against the immutable `motion` opponent in both seats under the
E7 deterministic runtime; and requires the complete `policy_match` result dictionaries to be
identical to FLIP inside the sector and CONTROL outside it. It emits only hashes and summary
metadata, never traces.

Please run the exact commands in the 16:45Z host request from the current branch head. Any test,
compile, or full-result mismatch remains terminal. No Arena action is requested.
