# Bounded banana-ring b100/e6 — Arena execution

Date: 2026-08-02

## Exact mutation

- source: `local_codex_1/banana-ring-b100-successor/banana-ring-b100-e6.arena.rs`
- bytes: 99,990
- SHA-256: `d2d8f65804991fed5ca8cdaacc1b62fd90ab553ee6952c6286029497e525eecc`
- displaced agent/submission: `6590083` / `41081195`
- returned submission: `41081465`
- platform agent: `6590136`
- API result: HTTP 200, exactly one submit request; no retry

The artifact, 39 semantic checks, eight-stream research/Arena equality over 2,400 commands,
compile/empty-input/mutated-parent checks, smoke record, and pre-submit coordination notice were
pushed at commit `2ee6941412b6b3c70db0136c4375dea89cc92816`. The owner explicitly directed publication despite
weak descriptive smoke value. Platform recovery after submission matched the source hash above;
the sacred source remained `fff6669b...`.

## Initial checkpoint

`banana-ring-b100-arena-initial-clean-20260802T-postsubmit.json`, SHA-256
`5889cacda8a07a3e3dd733afd4af12094da083e8894ee241a517c6f31eff5331`:

- 11 matching rows: 10 finished/fetched/parsed plus one pending;
- exact agent/submission identity, zero unexpected rows, fetch failures, or runtime signals;
- 4W/0T/6L, mean margin -110.8;
- five catastrophes, negative-margin mass 1,301;
- submission-scoped filtered score 13.46, rank 126/131; Arena-room placement was still 0.0.

An earlier transitional checkpoint that still contained the displaced room identity is retained
for chronology but excluded from the registry.

## Terminal disposition

The owner observed live oscillation. Exact game `897829265` proves long period-2 movement; see
`banana-ring-live-oscillation-incident-2026-08-02.md`. Immediately before replacement the
authenticated room read was 11.0 at rank 129/131. The owner directed replacement with the E7a
sector candidate.

**Disposition: IMPLEMENTATION_INVALID / DISPLACED.** The source is not evidence against the
intended banana-production algorithm. It is a failed implementation trial and must not be
resubmitted or used as a banana-value observation.
