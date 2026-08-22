# E7a frozen sector candidate — owner-override Arena execution

Date: 2026-08-02

## Decision status

The live bounded-ring implementation exhibited severe period-2 movement and read 11.0 at rank
129/131 immediately before replacement. The owner explicitly directed publication of the existing
sector candidate.

This is an owner override, not a frozen-protocol promotion. The candidate's consumed-panel estimate
is +4.0083 mean margin against the stable parent, root-cluster bootstrap 95% interval
[-1.5875, +13.1015]. It is mechanically exact but not prospectively value-qualified.

## Exact source and preflight

- source: `cgauto/submissions/candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs`
- bytes: 62,820
- SHA-256: `97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595`
- stable parent SHA-256: `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`
- regenerated artifact byte-exact: pass
- focused tests: 5/5 pass
- standalone optimized compile: pass
- semantic bridge: 16/16 full results exact, zero runtime/command faults
- recovered displaced ring source: exact `d2d8f658...`
- sacred source: exact `fff6669b...`
- sole controller/no concurrent submit process: pass
- pushed pre-submit notice: `85cc8e444177de901c534a09765d8e575f85d1ad`

## Submit response

The first client invocation used a relative path absent from the credentialed worktree and failed
locally at `Path.read_text`, before creating a session or making a submit request. The unambiguous
pre-request failure is preserved in the raw log. The controller then invoked the same verified
artifact by absolute path.

- `TestSession/submit`: HTTP 200
- submission: `41081503`
- platform agent: `6590141`
- actual submit requests: exactly one
- ambiguous response/retry: none
- platform source recovery after submission: exact candidate SHA-256

Raw log: `e7a-sector-owner-override-submit-20260802T174300Z.log`.

## First clean checkpoint

`e7a-sector-owner-override-initial-checkpoint-20260802T174600Z.json`, SHA-256
`8b6bfd08e1ceac46881a33dfa44a4d843ee6da7fcaf8b0af395a3b27c2054816`:

- 17 exact matching rows: 16 finished/fetched/parsed plus one pending;
- identity clean; zero unexpected rows, fetch failures, or runtime/validity signals;
- score 19.42, rank 69/131;
- 11W/1T/4L, mean margin +41.6875;
- zero catastrophes, negative-margin mass 175.

An adjacent Arena-room read during convergence reported 21.1 at rank 49/131. The immutable
submission-scoped checkpoint above is the canonical initial observation.

## Disposition

**LIVE / OWNER OVERRIDE / CLEAN INITIAL HEALTH / VALUE UNRESOLVED.** Monitoring is read-only. The
default of `cgauto/api_submit.py` remains the exact stable parent as the intentional fallback; it is
not silently changed to this exploratory live source.
