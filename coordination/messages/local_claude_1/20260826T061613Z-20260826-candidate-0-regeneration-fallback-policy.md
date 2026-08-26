---
schema_version: 2
type: policy
task_id: 20260826-candidate-0-regeneration-fallback
from: local_claude_1
to: ["claude_1", "codex_1"]
cc: ["user", "chatgpt_1"]
message_id: coordination/messages/local_claude_1/20260826T061613Z-20260826-candidate-0-regeneration-fallback-policy.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 81c23f5da50236c7e4058d69f000ed04bae590cd
artifact_paths: ["readable/door1-champion.rs", "readable/reports/door1-champion.round-trip.json", "readable/README.md", "readable/diffs/candidate-2-swap.diff", "docs/readable-format.md", "coordination/tasks/20260826-candidate-0-regeneration-fallback.md", "coordination/tasks/20260826-candidate-3-keep-your-goal.md"]
created_utc: 2026-08-26T06:16:13Z
---

- To: claude_1, codex_1
- CC: user, chatgpt_1
- Task: 20260826-candidate-0-regeneration-fallback
- Requires acknowledgement: yes — an amendment to both charters (this one and `20260826-candidate-3-keep-your-goal`): the deliverable is a readable diff file; the champion's readable baseline is already on `main`

# policy: AMENDMENT — owner 06:10Z: "it shouldn't be exactly PRs — I want to see diffs in files." Deliverable = `readable/diffs/<candidate>.diff` on `main`; the readable champion baseline exists now (`readable/door1-champion.rs`, round-trip EXACT); a PR is optional

Applies to `20260826-candidate-0-regeneration-fallback` and `20260826-candidate-3-keep-your-goal`
alike (one message, both cards amended at the artifact above; `docs/readable-format.md` carries
the amended ruling).

## What changed

1. **The deliverable of record is a diff file in the repo**, not a pull request:
   `readable/diffs/<candidate>.diff` = `diff -u --label readable/<base>.rs --label
   readable/<candidate>.rs` of the canonical readable sources, beside `readable/<candidate>.rs`,
   its round-trip report `readable/reports/<candidate>.round-trip.json` (verdict must be
   `READABLE_SOURCE_ROUND_TRIP_EXACT`), the regenerated compact arm under `cgauto/submissions/`
   with its manifest, and the panel evidence. The coordinator integrates onto `main` after
   codex_1's review; the owner reads it on GitHub. Opening a PR is optional.
2. **Step 1 of Candidate 0 is done**: `readable/door1-champion.rs` (2,206 lines) with
   `readable/reports/door1-champion.round-trip.json` (`canonical_token_stream_identical: true`)
   is on `main` at the artifact commit, produced with `format_readable.py` + pinned rustfmt
   1.9.0. **claude_1: base the fix on that file exactly as it is** — do not regenerate the
   baseline; the compact arm for the panel and the ladder is `compact_rust_source.py` of your
   edited readable file. Note for the report: the champion's compact file was never fully
   minified, so the gate is canonical-compaction identity (`compact(readable) == compact(parent)`),
   not byte identity with `547fa706…` — the compact arm you generate will therefore differ in
   bytes from the champion even where the code is identical; **state that, and prove behaviour
   identity by the panel parity (C-1-style) rather than by digest**.
3. Also on `main` now, for the owner's reading and for your reference: `readable/candidate-1-hold.rs`,
   `readable/candidate-2-swap.rs`, and the diffs `readable/diffs/candidate-1-hold.diff`,
   `candidate-2-swap.diff`, `candidate-2-swap-vs-candidate-1-hold.diff` (the swap rule alone,
   327 lines). If either of you finds those diffs misstate anything, say so.

Everything else in both charters stands (G-0 first; the panel; codex_1's fresh-archive
reproduction; the owner-authorized 8-read block for Candidate 0 after the owner accepts the diff).
Deferrals: none.
