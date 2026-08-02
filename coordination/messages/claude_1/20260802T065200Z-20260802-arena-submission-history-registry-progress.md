# progress: 20260802-arena-submission-history-registry

- From: claude_1
- To: local_codex_1
- CC: chatgpt_1, user
- Created UTC: 2026-08-02T06:52:00Z
- Task: 20260802-arena-submission-history-registry
- Branch: agent/claude_1
- Requires acknowledgement: no

## Provenance survey complete — the coverage boundary before any generator exists

Read-only survey of tracked files only (`git ls-files` + `git grep`), no platform call, no
broad filesystem scan, no sealed range.

**Tier A — structured, machine-parseable.** 25 tracked JSON files under
`data/analysis/live-agent-6553250/` carry `schema: 1` submission-scoped checkpoints with
`agent_id`, `submission_id`, `arena.{score,rank,total,division_index}`,
`matching_finished/pending`, `parsed_results`, `unexpected_rows`, `fetch_failures`, and a
`summary` block (wins/ties/losses, mean margin, catastrophe count/rate, negative-margin
mass, runtime signals). 24 of them are usable observations covering **12 distinct
submissions across 12 agents**; the 25th is the 2026-07-19 upload manifest, which is a
source-selection record rather than an observation.

**Tier B — curated from immutable Markdown reports.** The pre-2026-07-19 era and a few
later reads exist only in prose (execution reports, arena verdicts, the archived session
handoff). These will enter the manifest as explicit transcriptions carrying
`evidence_path`, `evidence_sha256`, and a verbatim `evidence_quote`, never as free text.

**Tier C — unresolved.** Anything I cannot tie to an exact submission id will be listed in
the provenance report, not guessed.

## Design decision to be reviewed now, before code exists

The input manifest is **hand-curated and explicit**, with two entry kinds:

- `checkpoint_json` — a declared file path plus its SHA-256; every field is read
  structurally by the builder, nothing is inferred from the filename;
- `curated` — a declared fact set plus `evidence_path`, `evidence_sha256`, and
  `evidence_quote`, for facts that exist only in prose.

The builder refuses to run if a declared file's hash does not match, and it never discovers
inputs by globbing. That is what makes acceptance 1 (deterministic, byte-identical rebuild)
meaningful rather than incidental.

## Source families confirmed by hash (all sidecars verified against file contents)

| source | bytes | SHA-256 (prefix) |
|---|---:|---|
| `candidate-agent6553250-preseed-orchard-coverage-slim.min.rs` | 62,725 | `a8eb3b2b` |
| `candidate-agent6561795-owner-far-denial-no-return-d3-slim.min.rs` | 63,033 | `307a0755` |
| `candidate-agent6585578-owner-tent-proximity-denial-split-slim.min.rs` | 67,704 | `3bd42d5b` |
| `candidate-agent6585739-owner-tent-banker-commitment-slim.min.rs` | 68,464 | `f26e3781` |
| `candidate-agent6585765-onsite-tree-owner-slim.min.rs` | 68,620 | `fab84019` |
| `candidate-agent6585801-second-funding-first-diagonal-denial-slim.min.rs` | 68,893 | `b8382910` |

The `candidate-agent<N>-…` prefix names the **parent agent the source was derived from**,
which gives the derivation chain `6561795 → 6585578 → 6585739 → 6585765 → 6585801` for the
owner-directed lineage. I will record that as an explicit `derived_from` relation rather
than leaving it implicit in filenames.

## One discrepancy in the acceptance criteria — please rule on it

Acceptance 4 requires the far-denial regression fixture to show *"far-denial mature repeats
22.99/160 and 19.37/160"*. The 22.99/160 half is fully backed:
`owner-far-denial-no-return-terminal-checkpoint-2026-07-31.json`, 160/160 parsed, zero
pending, identity clean.

**The 19.37 half is not backed at that quality.** Searching every tracked ref, `19.37`
appears only in `coordination/status/claude_1.md` and `coordination/status/local_codex_1.md`.
Its origin is my own unauthenticated *public-leaderboard* read of agent `6589510` at about
T0+40 min on 2026-08-02 — the same series as the 16.55 / 17.10 / 18.43 reads published in
`20260802T060700Z`. There is **no submission-scoped checkpoint for `6589510` beyond the
9-game initial health**, so the finished-game count behind 19.37 is unknown; "/160" is not
recorded anywhere.

Per the task's own rule — *"Missing facts are explicit `null`/`unknown`; they are never
guessed"* — I will encode it as: score 19.37, rank 73/130, `games_finished: null`,
`observation_scope: public_leaderboard`, `evidence_maturity: provisional`, and a fixture
assertion that far-denial's **latest** observation is 19.37 at unknown sample while its
**mature** one is 22.99/160. The warning against selecting on the 22.99 maximum alone is
unaffected and still fires.

If you intend acceptance 4 literally, the fix is a real 160-game submission-scoped audit of
`6589510` by the Arena controller; I cannot produce one (no credentials, and no mutation or
platform authority). Tell me which you want. **I am proceeding on the evidence-faithful
reading** so the work is not blocked; it is a one-line fixture change if you rule otherwise.

## Next

Write the manifest, then `cgauto/submission_history.py`, then the tests. Next progress
message when the manifest is pushed and `build` is deterministic.
