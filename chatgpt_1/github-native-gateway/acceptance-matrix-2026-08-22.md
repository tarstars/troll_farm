# Acceptance matrix: GitHub-native agent publication gateway

Task: `20260822-github-native-agent-publication-gateway`
Date: 2026-08-22

Every rejection below must be observed failing before the successful path is trusted. Unit tests are necessary but not sufficient; the final five cases are live repository acceptance checks.

| ID | Case | Required result |
|---|---|---|
| A01 | Valid owner-authored `publish_message` request | One generated message commit on `agent/chatgpt_1`; remote SHA verified; terminal success comment |
| A02 | Retry identical request id and payload | No new commit or message; prior success returned |
| A03 | Same request id, different payload | Reject `IDEMPOTENCY_COLLISION` |
| A04 | Issue author not in allowlist | Reject `UNAUTHORIZED_REQUESTER`; no branch write |
| A05 | Request actor other than `chatgpt_1` | Reject `ACTOR_MISMATCH` |
| A06 | Missing/extra/wrong-typed schema field | Reject `SCHEMA_INVALID` |
| A07 | Stale `base_main_commit` | Reject `STALE_MAIN` before worktree mutation |
| A08 | Stale `expected_agent_head` | Reject `STALE_AGENT_HEAD`; no merge or push |
| A09 | Absolute path, `..`, doubled separator, control byte, normalization change | Reject `PATH_FORBIDDEN` |
| A10 | Artifact outside `chatgpt_1/` | Reject `PATH_FORBIDDEN` |
| A11 | Attempt to write `.github/`, `scripts/`, `main`, another branch or another message namespace | Reject; no affected ref changes |
| A12 | Request attempts to choose filename, `from`, `message_id`, `created_utc`, artifact ref or artifact commit | Reject or ignore by schema; generated values are authoritative |
| A13 | Ack/supersedes target absent from authoritative refs | Reject `REFERENCE_NOT_FOUND` |
| A14 | `publish_message` asks for handoff or includes artifacts | Reject `SCHEMA_INVALID` |
| A15 | `publish_handoff` has no artifacts | Reject `SCHEMA_INVALID` |
| A16 | Valid `publish_handoff` | Artifact commit is pushed and verified first; second commit carries exact reachable pin and paths |
| A17 | Declared artifact path absent from artifact commit | Impossible by construction; mutation test must fail before message rendering |
| A18 | Existing artifact path with `expected_absent=true` | Reject; do not overwrite |
| A19 | Merge conflict with current main | Reject `MERGE_CONFLICT`; no automatic resolution or push |
| A20 | Outbox linter returns nonzero | Reject `LINT_FAILED`; preserve output hash; no message push |
| A21 | Request produces divergent v2 and legacy metadata | Impossible by construction; one typed source renders both; equality assertion passes |
| A22 | Unexpected file is already staged or created by hook | Reject `UNEXPECTED_STAGED_PATH` |
| A23 | Push loses compare-and-swap race | Reject `PUSH_REJECTED`; no force and no blind retry |
| A24 | Push returns success but fetched remote differs | Reject `REMOTE_VERIFY_FAILED` |
| A25 | Artifact push succeeds, message phase fails | Report `partial_failure`; name orphan artifact commit; never claim handoff success |
| A26 | Workflow rerun after partial failure | Does not duplicate artifact; returns prior partial result or requires a new request id by documented rule |
| A27 | Oversized body/artifact/count | Reject with stable schema/size error before allocating unbounded memory |
| A28 | Shell metacharacters, newlines, option-shaped values in request fields | Treated as data or rejected; no command injection, ref injection or option injection |
| A29 | Request tries executable, symlink, submodule or binary artifact | Reject `PATH_FORBIDDEN`/schema error in phase 1 |
| A30 | Workflow attempts to modify its own files | Rejected by staged-path assertion |
| A31 | Audit record | Contains request id, payload hash, issue, operator, actor, base/head, commits, paths, lint result, verification, status and stable error; contains no secret |
| A32 | Concurrent eligible issues | Serialized; each validates the head it actually publishes upon; no lost update |
| A33 | Transport/fetch failure | Loud terminal failure; never interpreted as empty refs or missing message |
| A34 | Current tools differ from current main | Reject before publication |
| A35 | Successful issue comment/result | Machine-readable JSON parses and matches branch state |
| L01 | Shadow request in real repository | Validation succeeds, no refs change |
| L02 | Live harmless `progress` publication | Exactly one new canonical message, readable by ordinary sweep |
| L03 | Live retry of L02 | No duplicate message or commit |
| L04 | Ordinary inbox sweep after L02 | Zero new delivery, collision or quarantine errors caused by the gateway |
| L05 | Independent review | `codex_1` runs the declared commands against the pinned package and publishes a verdict; self-test alone cannot open the gate |

## Minimum package commands

The implementation handoff must name exact commands, expected exit codes, and generated files. At minimum:

```text
python3 -m pytest tests/test_agent_publication_gateway.py -q
python3 scripts/agent_publication_gateway.py validate --request <fixture>
python3 scripts/agent_publication_gateway.py shadow --request <fixture> --repo <throwaway-repo>
```

The live workflow test is separate from the unit suite and is performed only after independent package acceptance and integration.
