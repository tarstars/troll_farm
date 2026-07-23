# Best-current-candidate Arena submission — 2026-07-19

## Outcome

The explicitly authorized exact resident artifact was submitted **once**.  CodinGame accepted
submission `41015603`, which landed as agent `6561795`.  No other source was submitted and no
resubmission occurred.

The platform's saved-source endpoint returned the exact intended 62,725-byte source at SHA-256
`a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55` after submission.

## Frozen source and pre-submit checks

- source:
  `cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`;
- bytes: 62,725;
- SHA-256:
  `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`;
- matching SHA sidecar: pass;
- standalone Rust 2021 compilation with warnings denied: pass.

Immediately before the write, the existing resident was agent `6560353`, submission `41012883`,
rank 41/107 Legend at 22.49.  Its submission-scoped battle list contained 160 finished games and
zero pending games.

## Single submission transaction

The exact command was:

```text
.venv/bin/python cgauto/api_submit.py cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs
```

The first submit endpoint returned HTTP 200 with body `41015603`; the helper stopped immediately
after that success.  This was one helper invocation and one accepted submit request.

The first post-submit identity read found submission `41015603` in ten pending battles under new
agent `6561795`.  At that instant the filtered ladder had cold-landed at rank 105/107 and 0.0,
while the room endpoint still showed old agent `6560353`.  That stale/cold observation is not a
performance result.

## First completed placement reads

At `2026-07-19T17:49:24Z`, 12 games were finished and one was pending.  The endpoints were already
on new agent `6561795` but still asynchronous:

- room: rank 65/107 at 20.10;
- filtered ladder: rank 50/107 at 21.55.

The final short checkpoint began at `2026-07-19T17:50:28Z` and was identity-clean:

- room: rank 61/107 Legend at 20.51;
- filtered ladder: rank 48/107 at 21.79;
- 16 matching battle rows: 15 finished, one pending;
- parsed results: 15/15, with no fetch failures or unexpected rows;
- record: 12 wins, zero ties, three losses, mean margin +36.33;
- one catastrophic loss and zero candidate runtime/validity signals.

This is an **immature placement read**, not a mature comparison with the old 160-game 22.49
bracket.  Polling stopped after the first identity-clean completed wave, as requested; the source
was not resubmitted.

## Audit artifacts

- first-read checkpoint:
  `data/analysis/live-agent-6553250/best-current-candidate-submission-first-read-2026-07-19.json`;
- checkpoint SHA-256:
  `089d2408e8540001c341057b70cceda33db945863526c4b6c5690a926e3a500b`;
- upload manifest:
  `data/analysis/live-agent-6553250/best-current-candidate-upload-manifest-2026-07-19.json`;
- selection result:
  `data/analysis/live-agent-6553250/best-current-candidate-selection-result-2026-07-19.md`.

The candidate source, research code, and `cgauto/api_submit.py` were not edited by this
transaction.
