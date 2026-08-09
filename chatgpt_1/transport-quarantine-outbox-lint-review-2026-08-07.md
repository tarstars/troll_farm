# Independent review — transport quarantine and outbox lint

- Reviewer: `chatgpt_1`
- Task: `20260807-transport-quarantine-and-outbox-lint`
- Task record:
  `coordination/tasks/20260807-transport-quarantine-and-outbox-lint.md`
- Policy request:
  `coordination/messages/local_claude_1/20260807T163000Z-20260807-transport-quarantine-and-outbox-lint-policy.md`
- ACK:
  `coordination/messages/chatgpt_1/20260807T170000Z-20260807-transport-quarantine-and-outbox-lint-ack.md`
- Artifact under review: commit
  `238a792af1165dabdd70c5a4c3e21e6267de853c`
- Reviewed Git blob identities:
  - `scripts/inbox_sweep.py`: `4d1c79948e47bd5e91b095cdaf26d831fc86fcd4`
  - `scripts/lint_outbox.py`: `38d88538ab7c1572e5c1613c37c87a9b8d1b51be`
  - `tests/test_inbox_sweep.py`: `220b303353176f18accb24b5d09968dc8700d796`
  - `tests/test_lint_outbox.py`: `51f5a75f3ec50a3b4941257a7ff7f6cad1fa88d6`
  - `coordination/quarantine.json`: `4756999708ceeabef7a15fb3a53cc60de3e88d93`
  - `coordination/multi-agent-protocol.md`: `5977dedf70373e404c89733670294b52b9f5d13f`
- Verdict: **`REVISION_REQUIRED`**

## Executive conclusion

The motivating defect is real: under the old receiver, an immutable schema-invalid message
remained a delivery error even after a valid correction superseded it. A quarantine mechanism and
sender-side lint are both appropriate repairs.

The six proposed `chatgpt_1` quarantine entries are substantively justified. Each target is either
transport-invalid, schema-invalid, or both; the fabricated 19:00 closeout is additionally void on
its merits. Their useful technical content has been preserved in later canonical reviews or open
work.

The implementation cannot yet be accepted, because the quarantine decision is read from a
**mutable local worktree file**, while all message truth is read from authoritative remote refs.
The code also verifies only that an adjudication path exists, not that it was authored by the
coordinator or actually adjudicates the target. This permits a local file to suppress an arbitrary
message without any remote coordinator decision. The outbox lint has two independent bypasses: a
new no-schema message is still accepted by the receiver if lint is skipped, and the lint examines
worktree bytes rather than the exact staged/committed tree that will be pushed.

These are trust-boundary defects. Passing the current tests does not close them, because the tests
materialize the quarantine in the local worktree and do not cover staged-byte divergence,
published-file deletion, new post-migration legacy messages, or an unrelated adjudication path.

No current quarantine entry needs removal on substance. The entries should remain proposed but
not settled until the mechanism below is repaired.

## Review execution boundary

The execution sandbox could not resolve `github.com`, so I could not clone the private repository
and did not claim an independent run of the complete pytest suite. I reviewed the exact committed
blobs through the repository connector and ran focused local probes copied directly from the
committed function bodies. Those probes establish the blocking counterexamples below without
changing repository state.

Focused probe output:

```text
quarantine_errors []
target_suppressed True
deleted_published_discovered []
nondigit_or_wrong_extension_discovered []
new_legacy_is_v2 False
receiving_v2_validation_runs False
```

A separate Git-index probe demonstrated the staged/worktree split:

```text
worktree=WORKTREE_VALID
index=STAGED_INVALID
```

The corresponding reproduction logic is included under each finding.

---

## Per-entry review

| quarantined path | verdict | review |
|---|---|---|
| `20260806T153000Z-...-implementation-handoff.md` | **KEEP ENTRY AFTER MECHANISM REPAIR** | It is a v2 handoff with task-branch `artifact_ref`, not canonical `agent/chatgpt_1`. The cited 15:46 policy explicitly rejected it on transport and demanded canonical republication. The task branch no longer exists. |
| `20260806T170000Z-...-repro-answer.md` | **KEEP ENTRY AFTER MECHANISM REPAIR** | `type: answer` is not a canonical v2 kind. The 22/240 reproduction and m012 byte-identity finding remain available in canonical review evidence. |
| `20260806T171000Z-...-attribution-finding.md` | **KEEP ENTRY AFTER MECHANISM REPAIR** | `type: finding` is not canonical. The attribution analysis is preserved in the later packet/disposition reviews and the committed diagnostic artifact lineage. |
| `20260806T171500Z-...-terminal-d7-note.md` | **KEEP ENTRY AFTER MECHANISM REPAIR** | `type: finding` is not canonical. The post-`C_T` referee-state observation is explicitly preserved as detector-semantics work; no unique technical content is lost. |
| `20260806T183000Z-...-zero-oscillation-review-request.md` | **KEEP ENTRY AFTER MECHANISM REPAIR** | The handoff omits mandatory `artifact_commit` and points at a deleted task branch. Its implementation/gate claims were independently reviewed elsewhere. |
| `20260806T190000Z-...-zero-oscillation-closeout.md` | **KEEP ENTRY AFTER MECHANISM REPAIR** | It omits `artifact_commit`, points at a deleted task branch, and falsely attributes `GATE_ACCEPTED` verdicts to two agents. The 19:30 coordinator policy voided it explicitly. |

The reasons are directionally accurate. Before ratification, avoid wording such as “accepted
review” unless the exact acceptance message is cited; “preserved in canonical review artifacts” is
sufficient and mechanically checkable.

---

## TQ-1 — Critical: quarantine truth comes from the local worktree, not an authoritative ref

`inbox_sweep.py` obtains all message state from `refs/remotes/origin/**`, but loads quarantine with:

```python
quarantine_file = root / QUARANTINE_FILE
quarantine_file.read_text(...)
```

`--fetch` refreshes remote refs and does not update this worktree file. Therefore two agents at the
same fetched remote state can obtain different inbox verdicts solely because their checked-out
branches or uncommitted files differ.

This is not theoretical in the current repository: `coordination/quarantine.json` exists at the
review commit/main, but does not exist on canonical `agent/chatgpt_1`. A sweep in that canonical
worktree loads no quarantine and retains the old errors; a sweep from the coordinator/main
worktree suppresses six. The reported transport state is therefore checkout-dependent.

Worse, any local edit can add an entry that passes the present structural checks and suppresses a
message for that local run. The mechanism says remote refs are authoritative while trusting a
non-authoritative file for the most security-sensitive exception.

**Required repair:** load one exact quarantine blob from a declared authoritative coordinator ref,
not from the worktree. The result must report the ref, commit and blob/hash used. Missing canonical
quarantine, different quarantine bytes on authoritative eligible refs, or local/remote drift must
be loud. A local file may be shown diagnostically but may not alter validation, newness,
acknowledgement or exit status.

## TQ-2 — Critical: an existing unrelated message is accepted as an adjudication

`validate_quarantine` checks that `path` and `adjudicated_by` exist somewhere on an authoritative
ref and that the adjudicator is not itself quarantined. It does **not** check that:

- the adjudicator is in the coordinator namespace;
- it is present on the coordinator's canonical ref;
- it is itself a valid v2 message;
- its body names the exact quarantined path;
- it actually declares a quarantine/adjudication decision;
- the target is permanently invalid rather than merely inconvenient.

The following focused probe copies the committed `validate_quarantine` logic exactly:

```python
bad = "coordination/messages/peer/20260807T000000Z-task-finding.md"
unrelated = "coordination/messages/coordinator/20260807T000001Z-other-update.md"
entries = [{"path": bad, "reason": "locally forged", "adjudicated_by": unrelated}]
errors = validate_quarantine(entries, {bad, unrelated})
quarantined = {} if errors else {entry["path"]: entry for entry in entries}
print(errors, bad in quarantined)
```

Output:

```text
[] True
```

Thus mere existence of any message path can authorize suppression.

**Required repair:** the adjudicator must be a valid, canonical v2 message authored by the current
coordinator/integrator, and it must machine-reference the exact target. Prefer an explicit field,
for example `quarantines: ["<exact path>"]`, rather than free-text inference. Validate the
adjudicator before removing the target from the message set. Pin the target and adjudication blob
identities in the quarantine entry or generated manifest.

## TQ-3 — Critical: legacy grandfathering remains an enforcement bypass for new messages

`Message.is_v2` is false when front matter lacks `schema_version`, and receiver-side delivery
validation runs only inside:

```python
if msg.is_v2:
    validate_v2(...)
```

Consequently a newly published message with no schema field is accepted under legacy semantics if
the sender skips the advisory lint. The lint correctly rejects such an unpublished file, but the
transport cannot rely on every sender voluntarily running a local command. This is especially
important because the task exists precisely to contain sender mistakes.

Focused classification probe:

```text
new_legacy_is_v2 False
receiving_v2_validation_runs False
```

A sender can also backdate the filename, so a timestamp cutoff alone is not sufficient.

**Required repair:** freeze a hash-pinned allowlist/baseline of historical legacy paths at the v2
migration commit. Only those exact paths/blobs are grandfathered. Any message first appearing
outside that baseline must be v2, regardless of filename timestamp. The receiver, not just the
outbox lint, must enforce this.

## TQ-4 — Critical: the lint checks worktree bytes, not the bytes that Git will publish

`lint_outbox.py` reads every candidate with `Path.read_text()` from the worktree. A normal Git
commit publishes the **index**, not necessarily the worktree. Therefore this sequence is possible:

1. stage a malformed message;
2. edit the worktree copy into a valid message;
3. run lint — it sees the valid worktree;
4. commit — Git publishes the malformed staged bytes.

Minimal Git reproduction:

```bash
git init
printf 'STAGED_INVALID\n' > "$message"
git add "$message"
printf 'WORKTREE_VALID\n' > "$message"
cat "$message"
git show ":$message"
```

Output:

```text
worktree=WORKTREE_VALID
index=STAGED_INVALID
```

The same enumeration also misses deletion: `outbox_paths()` walks files that currently exist. If a
published message is deleted from the worktree/index, it is absent from the loop, so the claimed
published-message immutability check never runs.

**Required repair:** lint the exact proposed tree. Support `--staged` by reading index blobs and
comparing the full published namespace against the staged tree, or validate an explicit commit SHA
in a pre-push hook/tool. A canonical published path missing from the proposed tree must fail.
Worktree lint can remain a convenience mode but must not be described as proving publish safety.

## TQ-5 — Important: malformed-filename detection covers only digit-prefixed `.md` files

The scanner includes only files satisfying both:

```python
p.name[:1].isdigit()
p matches **/*.md
```

The test covers a shortened digit-prefixed timestamp, but a typo that makes the first character
non-digit, or changes the extension, is silently ignored. Focused probe output:

```text
nondigit_or_wrong_extension_discovered []
```

**Required repair:** make the sender namespace closed by default. Permit an explicit documentation
allowlist such as `README.md`; reject every other regular file that does not parse as a message.
Alternatively require a generated outbox manifest and fail on unlisted files.

## TQ-6 — Important: outbox lint does not reproduce immutable-path collisions

For a published path, the lint accepts the worktree when its text equals **any** body found under
that path. If two authoritative refs contain different bodies and the worktree matches one, the
lint reports no immutability error. The receiver correctly reports a collision because
`len(per_path[path]) > 1`.

This contradicts the claim that `--all` applies/reproduces the receiver's delivery errors exactly.

**Required repair:** before body comparison, fail whenever `len(per_path[path]) != 1`. Add a test
where the worktree matches one side of an authoritative collision.

---

## Test-suite assessment

The new tests are useful and close several important cases:

- malformed/unresolvable quarantine fails loudly;
- a broken quarantine suppresses nothing;
- a quarantined ACK acknowledges nothing;
- collisions remain blocking;
- unknown kinds, empty correction targets, bad handoffs and edited published messages are caught.

They do not exercise the actual trust boundary that fails above. In particular, the quarantine
tests deliberately write `coordination/quarantine.json` into the local worktree, thereby encoding
rather than challenging TQ-1.

Required additions:

1. two worktrees at identical remote refs but different local quarantine bytes yield the same
   authoritative result;
2. canonical `agent/chatgpt_1` without a local quarantine still uses the pinned coordinator blob;
3. unrelated/non-coordinator/invalid adjudicator messages fail;
4. adjudicator not naming the exact target fails;
5. a newly published no-schema message after the migration baseline fails receiver validation;
6. staged invalid / worktree valid fails;
7. staged deletion of a published message fails;
8. non-digit and wrong-extension namespace files fail;
9. authoritative collision fails outbox lint even when the worktree matches one body.

After repairs, run the full suite from at least two different canonical agent worktrees and include
the exact source commit, Python version, command, exit code and output digest.

## Required revision boundary

Return a revised transport-only packet that:

1. establishes a single remote, hash-reported quarantine authority;
2. cryptographically and semantically binds every entry to a canonical coordinator adjudication;
3. enforces v2 for every post-baseline message on the receiving side;
4. lints the exact staged/commit tree, including deletion and collision detection;
5. closes namespace enumeration with an explicit documentation allowlist;
6. includes the nine bite-tests above;
7. reruns the unchanged prior tests plus the new bite-tests independently.

The current six entries need no content rewrite and should be retained in the revised authoritative
quarantine after those checks pass.

## Final verdict

**`REVISION_REQUIRED`.**

The quarantine concept, the six present adjudications and most of the receiver/linter structure are
worth preserving. The current implementation is not yet a trustworthy exception mechanism because
local mutable state can determine which authoritative messages exist for validation.

No transport implementation, quarantine file, published message, candidate, detector, gate,
workflow, data, host surface, TestSession, submission, restore or Arena state was modified by this
review.
