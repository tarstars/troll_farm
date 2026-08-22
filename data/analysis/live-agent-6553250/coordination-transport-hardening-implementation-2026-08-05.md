# Coordination transport hardening — implementation report

- Task: `coordination/tasks/20260805-coordination-transport-hardening.md`
- Implementing agent: claude_1
- Branch: `agent/claude_1-transport-hardening`
- Date UTC: 2026-08-05
- Test runner note: `python3 -m pytest` is unavailable on this host
  (`/usr/bin/python3: No module named pytest`); the suite was run with
  `$HOME/.local/bin/uvx pytest -q tests/test_inbox_sweep.py`.

## Design summary — what changed in `scripts/inbox_sweep.py` and why

**Checked Git layer (spec: authoritative inbox rule 1; tool defect 1).** The old `git()`
converted every failure into an empty string, so stale refs looked healthy. `git()` now
raises `GitError` carrying stderr; `--fetch` runs a checked `git fetch origin` and on
failure prints Git stderr, prints `inbox: STALE / NOT AUTHORITATIVE`, and exits 2 without
claiming any message or ACK state.

**Remote-refs-only authority (rule 2; defect 2).** Delivery and acknowledgement scan only
`refs/remotes/origin/**` (excluding `origin/HEAD`). Local branches and the working tree
are shown only behind `--include-local` in a section labeled
`local diagnostics — unpublished, NOT authoritative`, and never change counts or exit
status. An unpushed or local-branch-only ACK therefore acknowledges nothing.

**Immutable-path collision detection (rule 3).** The scan records blob OIDs per path per
remote ref (`git ls-tree -r`). The same path with different bytes on two authoritative
refs is reported under `immutable-path collisions (N)` and exits 2; identical copies
deduplicate normally.

**v2 validation with delivery errors (rule 4; normative schema).** Messages declaring
`schema_version: 2` (or higher) are validated strictly: required front-matter fields
(`schema_version, type, task_id, from, to, cc, message_id, requires_ack, ack_for,
supersedes, created_utc`), `message_id` == repository-relative path, `from` == sender
namespace, `ack_for`/`supersedes` as single-line JSON arrays via `json.loads` (no PyYAML
dependency added), targets must be existing authoritative message paths, presence on
canonical `refs/remotes/origin/agent/<from>`, a v2 `ack` needs a non-empty `ack_for`, a
`correction` a non-empty `supersedes`, and a `handoff` needs `artifact_ref` equal to the
sender's canonical branch, a full 40-hex `artifact_commit` that exists and is reachable
from `origin/<artifact_ref>`, and every `artifact_path` present in that commit. Failures
for addressed messages appear under `delivery errors (N)` and exit 2.

**Exact acknowledgements (defects 2 and 4).** A v2 ACK (from my namespace, on remote
refs, and itself valid) acknowledges exactly the paths in `ack_for`. The legacy
task-plus-strictly-earlier-timestamp rule survives as fallback for legacy messages only
and can never acknowledge a v2 message. `correction` was added to the kind vocabulary and
requires acknowledgement by default.

**Seen state replaces the watermark (defect 3).** Newness is exact-path membership in
agent-owned `<agent-id>/inbox-seen.json` (schema_version 1, `migrated_watermark`,
sorted `seen_message_paths`), written deterministically through a temporary sibling plus
`os.replace`. While the file is absent, the legacy `<agent-id>/inbox-watermark.txt` is
read once as a migration hint (currently existing addressed messages at or before it are
treated as seen); the legacy file is never rewritten or deleted. `--mark` adds only the
currently selected, addressed, authoritative remote paths (plus, on the first marking run,
the migrated snapshot) and never acknowledges anything. Once the file exists, an
out-of-order remote message with an older timestamp is still new if its exact path is
absent.

**Exit codes and filters (rules 5-6).** Exit 0 healthy/nothing unacknowledged; exit 1
healthy with unacknowledged ack-required messages in the current selection; exit 2 for
failed fetch, malformed seen-state file, immutable-path collision, or delivery errors.
Repeatable `--task <exact-task-id>` and `--sender <exact-agent-id>` filters affect display
and `--mark` only; validation always runs over all addressed messages.

**Docs.** `coordination/multi-agent-protocol.md` §4 documents the v2 front matter,
exact-path ACKs, correction kind, and the canonical-publication rule; §10 documents
remote-only authority, the exit semantics, the seen-state, and per-agent migration
commands. `coordination/templates/message.md` and `templates/handoff.md` now carry the
same v2 front matter and rules.

## Acceptance outputs (exact)

### 1. `python3 -m py_compile scripts/inbox_sweep.py`

Exit 0, no output.

### 2. Test suite

`python3 -m pytest -q tests/test_inbox_sweep.py` → `/usr/bin/python3: No module named
pytest` (exit 1; pytest is not installed system-wide). Recorded runner:

```text
$ $HOME/.local/bin/uvx pytest -q tests/test_inbox_sweep.py
.....................................                                    [100%]
37 passed in 6.28s
```

### 3. Live read-only filtered sweep

```text
$ python3 scripts/inbox_sweep.py --me local_codex_1 --fetch --task 20260802-banana-restoration-r2
agent: local_codex_1
authority: refs/remotes/origin/** (50 remote refs); scanned 691 authoritative messages (691 legacy, 0 v2)
seen-state: local_codex_1/inbox-seen.json missing; migrating legacy watermark 20260731T173500Z
filters: task=20260802-banana-restoration-r2

immutable-path collisions (0):

delivery errors (0):

new (unseen) (10):
  coordination/messages/claude_1/20260804T171500Z-20260802-banana-restoration-r2-ack.md   [refs/remotes/origin/agent/claude_1]
  coordination/messages/claude_1/20260804T180000Z-20260802-banana-restoration-r2-progress.md   [refs/remotes/origin/agent/claude_1]
  coordination/messages/claude_1/20260804T190000Z-20260802-banana-restoration-r2-progress.md   [refs/remotes/origin/agent/claude_1]
  coordination/messages/claude_1/20260804T194500Z-20260802-banana-restoration-r2-review-request.md   [refs/remotes/origin/agent/claude_1]
  coordination/messages/claude_1/20260804T203000Z-20260802-banana-restoration-r2-ack.md   [refs/remotes/origin/agent/claude_1]
  coordination/messages/claude_1/20260804T213000Z-20260802-banana-restoration-r2-handoff.md   [refs/remotes/origin/agent/claude_1]
  coordination/messages/claude_1/20260804T220000Z-20260802-banana-restoration-r2-ack.md   [refs/remotes/origin/agent/claude_1]
  coordination/messages/claude_1/20260805T063000Z-20260802-banana-restoration-r2-progress.md   [refs/remotes/origin/agent/claude_1]
  coordination/messages/claude_1/20260805T083000Z-20260802-banana-restoration-r2-handoff.md   [refs/remotes/origin/agent/claude_1]
  coordination/messages/claude_1/20260805T110000Z-20260802-banana-restoration-r2-ack.md   [refs/remotes/origin/agent/claude_1]

unacknowledged, ack required (0):
```

Exit 0; no delivery errors; only `refs/remotes/origin/**` counted; no watermark or
seen-state file was written for `local_codex_1` (`--mark` not passed; `git status
--porcelain -- local_codex_1 claude_1 chatgpt_1` stayed empty and no
`local_codex_1/inbox-seen.json` exists).

### 4. Sacred source hash

```text
$ sha256sum rust/src/bin/yamo_orchard_live.rs
fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f  rust/src/bin/yamo_orchard_live.rs
```

### 5. `git diff --check`

Exit 0, no output (no whitespace errors).

## Warning-mode audit over the real repository (no `--mark`, no writes)

All runs on 50 remote refs, 691 authoritative message paths, all legacy
(`schema_version` absent), 0 v2, 0 malformed, 0 immutable-path collisions, 0 delivery
errors. No agent directory was modified by any run.

| agent | seen-state | new (unseen) | unacknowledged, ack required | exit |
|---|---|---|---|---|
| local_codex_1 | missing; migrating legacy watermark 20260731T173500Z | 131 | 2 | 1 |
| claude_1 | missing; migrating legacy watermark 20260802T062800Z | 188 | 28 | 1 |
| chatgpt_1 | missing; no legacy watermark | 528 | 147 | 1 |

Legacy messages parsed: 691 of 691 (100%); malformed: none. (The task record cited 689
existing paths at authoring time; two more legacy messages have since been published.)
claude_1's unacknowledged count dropped from the incident's 29 to 28 because the
motivating review ACK
`coordination/messages/local_codex_1/20260805T083001Z-20260802-banana-restoration-r2-ack.md`
has since been covered by a later ACK from claude_1's own namespace (remote commit
`20c1f3b9`). Corrected per the integrator review: that acknowledging message
(`coordination/messages/claude_1/20260805T110000Z-20260802-banana-restoration-r2-ack.md`)
carries a proto-v2 `ack_for` line but no `schema_version: 2`, so this implementation
treats it as legacy and pairs it via the legacy same-task/strictly-later-timestamp
fallback — not via exact `ack_for` path pairing, as an earlier draft of this report
misstated. Exact-path ACK behavior is evidenced by the test suite (and by the
genuinely-v2 ACK in the revision appendix below), not by that live legacy message. Per
the task's rollout section that acknowledgement was not written by this implementation.

## Migration — exact commands per agent

One-time, run from each agent's own worktree after this change is integrated. Review
first, then mark, then commit and push the new seen-state file. The legacy watermark file
is left in place untouched.

```bash
# claude_1
python3 scripts/inbox_sweep.py --me claude_1 --fetch          # review; exit 2 = transport error
python3 scripts/inbox_sweep.py --me claude_1 --fetch --mark   # writes claude_1/inbox-seen.json
git add claude_1/inbox-seen.json
git commit -m "claude_1: migrate inbox seen-state to inbox-seen.json"
git push origin agent/claude_1

# local_codex_1
python3 scripts/inbox_sweep.py --me local_codex_1 --fetch
python3 scripts/inbox_sweep.py --me local_codex_1 --fetch --mark
git add local_codex_1/inbox-seen.json
git commit -m "local_codex_1: migrate inbox seen-state to inbox-seen.json"
git push origin agent/local_codex_1

# chatgpt_1
python3 scripts/inbox_sweep.py --me chatgpt_1 --fetch
python3 scripts/inbox_sweep.py --me chatgpt_1 --fetch --mark
git add chatgpt_1/inbox-seen.json
git commit -m "chatgpt_1: migrate inbox seen-state to inbox-seen.json"
git push origin agent/chatgpt_1
```

Backlog retirement follows the task's Historical-backlog rollout: acknowledge actionable
messages by exact path, publish a pushed legacy-backlog audit for the remainder, cover
closed/superseded paths with one explicit v2 ACK citing the audit, and mark paths seen
only after the ACK/audit commit is remotely verified. Do not blanket-acknowledge by
timestamp.

## Compatibility statement

All 691 existing immutable legacy messages (689 at task authoring) are untouched and
still parse: the warning-mode audit above read every one of them from remote refs with
zero malformed results and zero mutations. Legacy parsing (no `schema_version`, or < 2)
remains enabled indefinitely — task/timestamp ACK pairing, legacy `- To:`/`- Task:`
metadata, and the watermark migration hint all still work. v2 strictness applies only to
messages that themselves declare `schema_version: 2` or higher; a legacy ACK can never
acknowledge a v2 message, and a v2 ACK acknowledges only the exact paths it lists.

## Ambiguities resolved during implementation

1. **`artifact_ref` must equal `agent/<from>`.** Otherwise a sender could point
   `artifact_ref` at a task branch and defeat required test area 11 ("artifacts exist
   only on a task branch fails canonical validation").
2. **Canonical presence is enforced for every addressed v2 message**, not only handoffs:
   inbox rule 4 lists "canonical presence" as its own validation item and the schema
   section fixes the canonical sender ref as `refs/remotes/origin/agent/<sender-id>`.
3. **Exit 1 tracks the filtered selection.** Filters affect display and `--mark`
   (rule 6); the exit code reflects the displayed unacknowledged set. Validation and
   delivery errors are always computed over all addressed messages, so exit 2 cannot be
   filtered away.
4. **`--mark` is skipped when collisions or delivery errors are present** (the run exits
   2); seen-state is not advanced over a broken transport view.
5. **Watermark migration is a one-time snapshot.** While `inbox-seen.json` is absent,
   addressed messages currently existing at or before the watermark count as seen; the
   first `--mark` persists that snapshot plus the selection together with
   `migrated_watermark`. Afterwards the watermark is never consulted, so a late-arriving
   message with an older timestamp is new (seen-state bullet 6).
6. **`requires_ack: false` cannot disable acknowledgement for ack-required kinds**
   (handoff, correction, claim, question, blocker, policy, stop, takeover) — the existing
   safety rule is preserved for both legacy and v2 messages.
7. **`cc` is a required v2 field** (may be `[]`): the spec's "Every v2 message contains"
   block includes it.
8. **A malformed v2 ACK from the sweeping agent itself acknowledges nothing** and is
   printed as a warning rather than a delivery error (delivery errors are reserved for
   addressed messages, per rule 4).
9. `tests/test_inbox_sweep.py` already existed (11 legacy-parser unit tests). Compatible
   tests were retained verbatim; the tests of the removed watermark writer and
   ref-agnostic dedup helper were replaced by seen-state and authority integration tests.

## Revision appendix — 2026-08-05 bounded corrections per integrator review

Applied per
`data/analysis/live-agent-6553250/coordination-transport-hardening-integrator-review-2026-08-05.md`
(REVISION_REQUIRED, three bounded gaps). Scope: `scripts/inbox_sweep.py`,
`tests/test_inbox_sweep.py`, and this report only.

1. **Empty `artifact_paths` rejected.** `validate_v2_handoff` now requires a non-empty
   `artifact_paths` array; an otherwise valid canonical handoff declaring
   `artifact_paths: []` is a delivery error and exits 2. New integration test:
   `test_empty_artifact_paths_on_otherwise_valid_handoff_fails`.
2. **Seen-state schema validated strictly.** `load_seen_state` now requires the file to
   be a JSON object with `schema_version` exactly 1 (booleans rejected) and
   `migrated_watermark` a string or null; violations raise the existing
   `malformed seen-state file …` error (stderr + exit 2) before anything is marked. New
   tests (each also passes `--mark` and asserts the file stays byte-identical):
   `test_seen_state_missing_schema_version_fails`,
   `test_seen_state_unsupported_schema_version_fails`,
   `test_seen_state_non_string_migrated_watermark_fails`.
3. **Report misstatement corrected and duplication removed.** The warning-mode audit
   paragraph above now states that the live claude_1 ACK
   (`…20260805T110000Z-…-r2-ack.md`) was paired via the legacy task/timestamp fallback,
   not exact `ack_for` (it lacks `schema_version: 2`). Duplication cleanup: the review's
   literal `self.path = path` / repository-root duplicates do not appear verbatim in the
   reviewed artifact `4ccf1f76` (verified by grep and an AST scan for repeated
   assignments); the two real duplicated lookups were removed instead — the
   sender-namespace expression computed both in `Message.__init__` and again in `main()`
   (now a shared `sender_of()` helper), and the second per-ref `tree_messages` repository
   scan that rebuilt `canonical_paths_by_agent` (now derived from the single
   authoritative scan).

### Revision acceptance outputs (exact)

`python3 -m py_compile scripts/inbox_sweep.py`: exit 0, no output.

```text
$ $HOME/.local/bin/uvx pytest -q tests/test_inbox_sweep.py
.........................................                                [100%]
41 passed in 6.70s
```

Live read-only sweeps (no `--mark`; `git status --porcelain` shows no watermark,
seen-state, or message change afterwards; both exits 0):

```text
$ python3 scripts/inbox_sweep.py --me local_codex_1 --fetch --task 20260802-banana-restoration-r2
agent: local_codex_1
authority: refs/remotes/origin/** (50 remote refs); scanned 696 authoritative messages (691 legacy, 5 v2)
seen-state: local_codex_1/inbox-seen.json missing; migrating legacy watermark 20260731T173500Z
filters: task=20260802-banana-restoration-r2
immutable-path collisions (0):
delivery errors (0):
new (unseen) (12):   # the 10 previously listed plus 20260805T143000Z handoff and 20260805T150000Z reviews-ack
unacknowledged, ack required (0):
```

```text
$ python3 scripts/inbox_sweep.py --me claude_1 --fetch --task 20260805-coordination-transport-hardening
agent: claude_1
authority: refs/remotes/origin/** (50 remote refs); scanned 696 authoritative messages (691 legacy, 5 v2)
seen-state: claude_1/inbox-seen.json missing; migrating legacy watermark 20260802T062800Z
filters: task=20260805-coordination-transport-hardening
immutable-path collisions (0):
delivery errors (0):
new (unseen) (1):
  coordination/messages/local_codex_1/20260805T143002Z-20260805-coordination-transport-hardening-ack.md   [refs/remotes/origin/agent/local_codex_1]
unacknowledged, ack required (0):
```

**Live v2 exact-path pairing evidence.** A genuinely-v2 ACK now exists on origin:
`coordination/messages/claude_1/20260805T150000Z-20260805-reviews-ack.md`
(`schema_version: 2`, exact `ack_for` listing
`…local_codex_1/20260805T143001Z-20260802-banana-restoration-r2-ack.md` and
`…local_codex_1/20260805T143002Z-20260805-coordination-transport-hardening-ack.md`).
In the claude_1 sweep above, the 20260805T143002Z target is itself v2 with
`requires_ack: true`; a legacy task/timestamp ACK can never acknowledge a v2 message, so
its absence from `unacknowledged, ack required` (with zero invalid-ack warnings) is
direct live evidence that the tool validated the v2 ACK and paired it through the
exact-`ack_for` v2 path — the behavior the previous report draft could only support with
the test suite.
