---
schema_version: 2
type: handoff
task_id: 20260819-osc031-forecast-fix-door1b
from: claude_1
to: ["codex_1"]
cc: ["local_claude_1", "user"]
message_id: coordination/messages/claude_1/20260820T152959Z-20260819-osc031-forecast-fix-door1b-handoff.md
requires_ack: true
ack_for: ["coordination/messages/codex_1/20260820T152133Z-20260819-osc031-forecast-fix-door1b-ack.md"]
supersedes: []
created_utc: 2026-08-20T15:29:59Z
artifact_ref: agent/claude_1
artifact_commit: c8d69b14d1af5dc2911ee2a448172c78c75c326a
artifact_paths: ["claude_1/night-tree/mutation_control.py", "claude_1/night-tree/night-tree-implementation-2026-08-20.md"]
---

- To: codex_1
- CC: local_claude_1, user
- Task: 20260819-osc031-forecast-fix-door1b
- Requires acknowledgement: yes

# Control repaired: the pre-patch check now reads a pinned copy, not a moving branch

## For the owner, in plain words

When I built the overnight decision code I also wrote a check whose job was to
show what the code did *before* my change, so the improvement was demonstrated
rather than asserted. codex_1 reviewed it and found that the check had quietly
stopped working: it fetched "the old code" from the shared main branch, and once
my change was deployed there, the shared branch **was** the new code. The check
was reading the new code and calling it the old one. Nothing the overnight runner
does was affected -- the runner itself is fine and its two test suites pass --
but that one piece of evidence was not reproducible by anyone else.

It now fetches the old code from a fixed, permanently frozen copy that cannot
change, and it refuses to run if that copy turns out to contain any part of the
new change. It also cleans up its temporary files. This is the same mistake this
project keeps meeting in different clothes: **a check pointed at something that
moves is not a check.**

## Technical

codex_1's evidence correction (`20260820T152133Z`) is **accepted in full and is
correct as stated**. `prepatch_control()` read
`git show origin/main:cgauto/night_runner.py`. After deploy commit `3f189cad`
landed the patch on `main`, that read returns the patched runner, so the control
entered the session-3 path instead of completing the asserted pre-patch stop.
The review was right not to reproduce the claim.

Repair in `c8d69b14d1af5dc2911ee2a448172c78c75c326a`:

- `PREPATCH_BLOB = 92264bead9f02a23226baedf90296fe5f301d563` --
  `cgauto/night_runner.py` at `3f189cad^`, byte-identical to the blob at
  `966d0aff`. Read with `git cat-file blob`: an immutable object, reachable no
  matter where any branch moves next.
- Wrong-pin guard: the control asserts the blob contains none of
  `EXTENSION_PAIRS`, `PREREGISTERED_BARS`, `session-3`, `SESSION 3`, and that it
  differs from the deployed runner. A pin that silently went post-patch now fails
  loudly instead of passing vacuously.
- `tempfile.TemporaryDirectory` replaces `mkdtemp`, so no synthetic files are
  left behind.
- The implementation note records the defect, the correction and its attribution.

Re-run on this branch after the repair:

- pre-patch control: exit 0, ledger carries `BLOCK COMPLETE`, no extension, no
  session 3, no further submission;
- mutants: **6/6 KILLED**, runner restored byte-exact, suite green afterwards;
- `test_post_b5_tree.py` **26/26**, `test_publish_recovery.py` **9/9**.

The deployed runner is untouched by this commit -- only the control script and
the note changed. No KEEP/REVERT ruling, no submission, and no authority beyond
the carded work is implied here.
