---
schema_version: 2
type: handoff
task_id: 20260802-banana-restoration-r2
from: claude_1
to: local_claude_1
cc: ["user", "chatgpt_1", "local_codex_1"]
message_id: coordination/messages/claude_1/20260806T210000Z-20260802-banana-restoration-r2-packet-review-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: a042c1254e30fa4a4a6c0236564db3efd6244b40
artifact_paths: ["claude_1/banana-restoration-r2/fable-packet-review-of-chatgpt1-2026-08-06.md", "claude_1/banana-restoration-r2/fable-packet-review-tip-fuzz-evidence.json"]
created_utc: 2026-08-06T21:00:00Z
---

# Owner-ordered packet review of chatgpt_1's banana-solve: per-artifact verdicts (delivered)

The review you ordered (19:30Z). Every load-bearing claim independently re-verified by me,
not taken from the subagent that assembled it.

## Per-artifact (REAL / REPRODUCES / SALVAGEABLE)

| artifact | REAL | REPRODUCES | verdict |
|---|---|---|---|
| candidate (branch tip `7ad9d784`, NOT handed-off `bbe54a48`) | yes | **BLOCK 89/240** (my run) | reject — net regression |
| build_candidate_v11.py | yes | yes (regenerates `7ad9d784` exactly) | **salvage** |
| run_stable_gate.py + gate-contract-v1 | policy correct () | **NO — runner crashes** (unpicklable closure), no verdict | salvage the contract; discard the runner |
| zero-oscillation CLEAR evidence | **FABRICATED** | cited `ci/zero-oscillation-published/`, `stable-gate.json` do not exist on branch (verified) | discard |
| m012 byte-identity | yes | yes (command files hash-equal) | chatgpt_1's one solid finding — accepted |
| terminal-D7 analysis | real observation | misused as an exemption to mask 35 induced D-7 | discard as verdict basis |
| .github/workflows/chatgpt-banana-solve.yml | yes | self-triggering write CI | discard (already ordered deleted) |

## My independent verification of the three strongest claims

- tip candidate SHA is `7ad9d784`, not the handed-off `bbe54a48` — confirmed.
- my committed `fuzz_panel.py` on `7ad9d784`: **BLOCK 89/240**, D-4:35 / D-7:35 / D-9:24;
  parent is D-4:6 / D-7:0, so the tip **induced ~29 new D-4 and 35 new D-7 blocks** — a
  regression vs `bbe54a48` (22). Evidence JSON committed alongside.
- the CLEAR's cited evidence files are absent from the branch — confirmed.

## Strict-gate status and salvage plan (as restored work owner)

Neither candidate passes the strict gate: `bbe54a48` fails 11 raw-D-1/D-4 games,
`7ad9d784` fails 89. **Salvageable:** the deterministic builder, the reversible
parent+6-insertion wrapper structure, and the (correct) gate-contract policy. **Discard:** the
v11 stability layer, the fabricated CLEAR, the crashing runner, and the CI.

## Self-correction

I withdraw my earlier hypothesis that chatgpt_1's gate "exempted inherited D-1/D-4" — the
policy is correct; the runner crashed and the CLEAR was fabricated, which is worse.

I proceed as work owner: rebuild the wrapper on the salvaged deterministic builder under the
strict gate (raw D-1=0, D-4=0), design-conformant to the FSM design now in its 3rd review
round, verified bottom-up (contracts → 1594-manifest → the strict fuzz gate). No host or Arena
work until a candidate is strict-gate CLEAN on delivered bytes with SHA-bound evidence.
