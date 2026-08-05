# 20260805-coordination-transport-hardening: make Git messages complete and reliably observable

- Status: revision required after first implementation handoff; Phase 2 not integrated
- Record owner: local_codex_1
- Work owner: claude_1
- Reviewer / integrator: local_codex_1
- Area: multi-agent coordination transport and inbox reliability
- Base commit: 27f80584f63b40f92880074c2f457199d6b59132
- Branch: `agent/claude_1-transport-hardening`; canonical delivery through `agent/claude_1`
- Progress lease: 15 minutes without remotely inspectable concrete progress
- Created UTC: 2026-08-05T09:23:51Z
- Last updated UTC: 2026-08-05T10:46:07Z

## Outcome

Replace the current timestamp-and-any-ref inbox convention with a backward-compatible transport
schema in which:

1. only fetched remote state can satisfy delivery or acknowledgement;
2. every new handoff is complete on the sender's canonical `agent/<id>` branch;
3. acknowledgements name exact immutable messages rather than relying on clock order;
4. out-of-order messages remain visible;
5. fetch, schema, immutable-path, and missing-artifact failures are loud;
6. a large historical inbox can be filtered and retired without hiding unresolved messages.

The result is a coordination/tooling change only. It must not alter any bot, experiment, replay,
Arena state, historical immutable message, or existing verdict.

## Incident motivating the task

On 2026-08-05 Claude published banana-R2 handoff
`coordination/messages/claude_1/20260805T083000Z-20260802-banana-restoration-r2-handoff.md`.
The handoff message was mirrored to canonical `agent/claude_1`, but its 39 source/test/trace
artifacts initially existed only on `agent/claude_1-banana-restoration-r2`. Commit `b2549f59`
later merged those artifacts to canonical without publishing a new immutable correction message.
Because the existing handoff path was deduplicated, a later inbox sweep correctly reported no new
message even though delivery topology had changed.

The reverse direction also failed operationally. `local_codex_1` pushed review ACK
`coordination/messages/local_codex_1/20260805T083001Z-20260802-banana-restoration-r2-ack.md`
at remote commit `27f80584` before Claude's canonical merge, but Claude's later status still said
"awaiting verdict". Running the current sweep as Claude exposes 188 new and 29 unacknowledged
messages because `claude_1/inbox-watermark.txt` is stale; the current review is present but buried.

Four tool defects make the incident repeatable:

- `git()` converts every Git/fetch error into an empty string, so stale refs can look healthy;
- working-tree and local-branch messages participate in ACK pairing, so an unpushed ACK can produce
  a false `0 unacknowledged` result;
- a scalar timestamp watermark misses late-arriving messages with older/skewed filenames;
- ACK matching by `task_id` plus lexicographic time forced a synthetic `08:30:01Z` ACK for a
  handoff committed at `05:49Z` but named `08:30Z`.

## Normative transport schema v2

### Canonical publication

- The canonical sender ref is exactly `refs/remotes/origin/agent/<sender-id>`.
- Task branches may be used for work, but a v2 handoff is not published until all handed-off
  artifacts are reachable from the sender's canonical branch.
- Publish artifacts first. Then publish the immutable handoff message in a later commit on the
  same canonical branch. This avoids an impossible self-referential commit hash.
- A repair to a published handoff is a **new** `correction` message with a new immutable path and
  an exact `supersedes` reference. Moving or copying the old message between refs is not a new
  coordination event.
- Remote task branches remain inspectable evidence, but they cannot alone satisfy a v2 handoff.

### YAML front matter

New messages use `schema_version: 2`. Lists are single-line JSON arrays so the existing dependency-
free parser can decode them with `json.loads`; do not add a PyYAML dependency.

Every v2 message contains:

```yaml
---
schema_version: 2
type: handoff
task_id: 20260805-example
from: claude_1
to: local_codex_1
cc: ["user"]
message_id: coordination/messages/claude_1/20260805T100000Z-20260805-example-handoff.md
requires_ack: true
ack_for: []
supersedes: []
created_utc: 2026-08-05T10:00:00Z
---
```

`message_id` must equal the repository-relative path at which the body is read. `from` must equal
the sender namespace in that path. `ack_for` and `supersedes` contain exact repository-relative
immutable message paths, never task ids or timestamps.

A v2 handoff additionally contains:

```yaml
artifact_ref: agent/claude_1
artifact_commit: 0123456789abcdef0123456789abcdef01234567
artifact_paths: ["claude_1/example/source.rs", "claude_1/example/manifest.json"]
```

The source/test manifest should be included in `artifact_paths`; hashes remain in that manifest or
the handoff body. `artifact_commit` must be a full 40-hex Git object reachable from
`origin/<artifact_ref>`, and every path must exist in that commit. The handoff message itself must
exist on canonical `origin/agent/<sender-id>`.

### Exact acknowledgements

- Every v2 ACK has a non-empty `ack_for` array of exact message paths.
- One ACK may cover several exact paths, but it covers nothing not listed.
- An ACK can itself set `requires_ack: true`; the response must then target that ACK's exact path.
- Filename timestamps remain human-readable ordering hints only. They have no role in newness or
  acknowledgement correctness under v2.
- Legacy messages and ACKs remain readable. The old task-plus-timestamp rule is fallback only when
  `schema_version` is absent or less than 2. It must never acknowledge a v2 message.

### Correction messages

Add `correction` to the message kinds. It requires acknowledgement by default, contains a non-empty
`supersedes` array, and explains the delivery/content correction. The superseded message remains
immutable and visible.

## Authoritative inbox behavior

Refactor `scripts/inbox_sweep.py` with these rules:

1. `--fetch` runs a checked `git fetch origin`. On failure, print Git stderr, label the inbox
   `STALE / NOT AUTHORITATIVE`, and exit 2 without claiming a message or ACK state.
2. Cross-agent delivery and acknowledgement use only `refs/remotes/origin/**`. Local branches and
   the working tree may be shown behind `--include-local`, labeled diagnostic/unpublished, and must
   never change authoritative counts or exit status.
3. If the same immutable message path has different bytes on two authoritative remote refs, report
   an immutable-path collision and exit 2. Identical copies deduplicate normally.
4. Validate v2 `message_id`, sender namespace, JSON-array fields, canonical presence, ACK targets,
   correction targets, and handoff artifacts. Malformed or incomplete addressed messages appear in
   a `delivery errors` section and make the command exit 2.
5. Preserve exit 0 for a healthy inbox with no unacknowledged required messages; exit 1 for a
   healthy inbox with unacknowledged messages; reserve exit 2 for transport/schema/delivery errors.
6. Add repeatable `--task <exact-task-id>` and `--sender <exact-agent-id>` filters. Filters affect
   display and `--mark`, not parsing/validation of the selected messages.

## Replace the timestamp watermark

Introduce agent-owned `<agent-id>/inbox-seen.json`:

```json
{
  "schema_version": 1,
  "migrated_watermark": "20260804T143000Z",
  "seen_message_paths": ["coordination/messages/claude_1/...md"]
}
```

- Newness is exact-path membership, not `filename_timestamp > watermark`.
- `--mark` atomically adds only the currently selected, addressed, authoritative remote paths.
- Marking a message as seen does not acknowledge it; unresolved ACK-required messages continue to
  appear in the unacknowledged section.
- On first run, the legacy watermark is read as a one-time migration hint: existing messages at or
  before it are treated as seen. The legacy file is not rewritten or deleted.
- Write the JSON deterministically (sorted paths, stable indentation) through a temporary sibling
  plus atomic replacement.
- An out-of-order remote message whose timestamp is older than every known message is still new if
  its exact path is absent from `seen_message_paths`.

## Historical-backlog rollout

Do not blanket-acknowledge by timestamp and do not rewrite old messages. For each agent with a
stale backlog:

1. run the new tool with `--sender`/`--task` filters;
2. acknowledge every currently actionable message by exact path;
3. produce a compact, pushed legacy-backlog audit listing each remaining ACK-required path and its
   disposition (`already completed`, `superseded`, or `still actionable`);
4. use one explicit v2 ACK listing the audited closed/superseded paths, with the audit as evidence;
5. mark the addressed paths seen only after the ACK/audit commit is remotely verified.

For the motivating incident, Claude must explicitly acknowledge
`coordination/messages/local_codex_1/20260805T083001Z-20260802-banana-restoration-r2-ack.md`.
The implementation agent must not write this acknowledgement in Claude's namespace.

## Exclusive write set transferred to the implementing agent

- `scripts/inbox_sweep.py`
- `tests/test_inbox_sweep.py`
- `coordination/multi-agent-protocol.md`
- `coordination/templates/message.md`
- `coordination/templates/handoff.md`
- a new implementation report under `data/analysis/live-agent-6553250/`
- the implementing agent's own status/message namespace for this task

The integrator retains this task record and `docs/BACKLOG.md`; proposed changes to them arrive in
the handoff rather than direct edits.

## Shared read-only inputs

- `coordination/messages/**` (all existing messages are immutable fixtures)
- `<agent-id>/inbox-watermark.txt`
- `coordination/tasks/20260731-inbox-yaml-frontmatter-compatibility.md`
- `coordination/tasks/20260802-current-experiment-log-reconciliation.md`
- commits `de1c8c956ed6c7c836dca7ba57c6e6c13525b50d`,
  `b2549f5922cdce9a837de5a52f2e656d2d2b6bc4`, and
  `27f80584f63b40f92880074c2f457199d6b59132`

## Do not touch

- existing files under `coordination/messages/**`;
- existing agent watermark/seen files during implementation tests;
- peer status files or peer-private source directories;
- `docs/STATE.md`, `docs/CONSTRAINTS.md`, experiment protocols/locks, bot sources,
  `cgauto/submissions/`, `data/raw/games/`, sealed data, or the collection cron;
- `rust/src/bin/yamo_orchard_live.rs` (must remain SHA prefix `fff6669b`);
- Arena, TestSession, or any external mutable service.

All stateful tests use temporary repositories and temporary agent directories.

## Required tests

Extend `tests/test_inbox_sweep.py` with unit and temporary-Git integration coverage for at least:

1. checked fetch failure prints stderr and exits 2;
2. an unpushed working-tree ACK does not acknowledge a remote handoff;
3. a local-branch-only ACK does not acknowledge a remote handoff;
4. a pushed remote ACK with exact `ack_for` acknowledges only the listed v2 message;
5. two messages with one task id are independent unless both paths are listed;
6. a legacy task/time ACK still covers only an earlier legacy message;
7. a v2 message with an older timestamp is new when its path is unseen;
8. `--mark` records selected addressed remote paths only and leaves unacked state unchanged;
9. first-run migration honors an existing legacy watermark without rewriting it;
10. different bytes at one immutable path across remote refs exit 2;
11. a handoff whose artifacts exist only on a task branch fails canonical validation;
12. a canonical handoff with a reachable full commit and all paths passes;
13. missing/non-ancestor commits and missing artifact paths each fail;
14. copying an already-seen handoff path to canonical is not a new event; a new correction naming
    it in `supersedes` is new and valid;
15. malformed `message_id`, `from`, JSON-list fields, `ack_for`, or `supersedes` fail clearly;
16. `--task` and `--sender` isolate the motivating ACK from a large synthetic backlog;
17. legacy repository messages still parse without mutation.

Tests must assert exit codes and authoritative counts, not only helper functions.

## Acceptance checks

Run and record exact output for:

```bash
python3 -m py_compile scripts/inbox_sweep.py
python3 -m pytest -q tests/test_inbox_sweep.py
python3 scripts/inbox_sweep.py --me local_codex_1 --fetch \
  --task 20260802-banana-restoration-r2
sha256sum rust/src/bin/yamo_orchard_live.rs
git diff --check
```

Expected properties:

- compile and focused tests pass;
- the live filtered sweep completes without delivery errors and does not count any local/worktree
  file as authoritative;
- the sacred source retains full SHA-256
  `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`;
- no existing immutable message or watermark changes;
- protocol and both templates describe the same v2 fields and exit semantics;
- an installation/migration section gives exact commands for each agent.

## Compatibility and rollout gates

- No rewrite of the 689 existing immutable message paths.
- Legacy parsing remains enabled indefinitely; v2 strictness applies only to messages declaring
  `schema_version: 2`.
- Phase 1: land code/tests/templates and run in warning mode against the current repository.
- Phase 2: integrator verifies the motivating handoff/ACK and one synthetic task end to end.
- Phase 3: announce v2 as mandatory for newly created messages. Old messages remain readable.
- Do not remove the legacy watermark reader until every active agent has a valid seen-state file.

## Arena authority

Read-only platform access: not needed.

Platform mutation: forbidden. This task has no game, candidate, submission, or Arena scope.

## Handoff

Push a v2-complete handoff from the implementing agent's canonical `agent/<id>` branch. Include
the exact implementation commit, test output, current-repository warning audit, migration commands,
and the implementation report. The integrator independently reruns the temporary-Git suite and the
filtered live sweep before integrating or enabling v2 enforcement.

## First implementation handoff review — 2026-08-05

Claude's canonical artifact commit `4ccf1f76...` independently passes compilation, 37/37 tests,
the two motivating live filtered sweeps, canonical reachability, and the sacred-source gate. Phase
2 is not integrated yet because `artifact_paths: []` incorrectly validates, the seen-state reader
does not enforce its declared schema version or watermark type, and the report mislabels a legacy
task/time acknowledgement as exact-path pairing. Remove two duplicate assignments, add the bounded
negative tests, correct the report, and return a new v2 handoff. Full review:
`data/analysis/live-agent-6553250/coordination-transport-hardening-integrator-review-2026-08-05.md`.
