# 20260731-h3-numeric-pressure-contact-causality

- Status: closed — `TEMPORALLY_ORDERED_PRESSURE_SIGNAL_PREFLIGHT_ONLY`; peer review accepted
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1
- Integrator: local_codex_1
- Area: APPROACH-REGISTER H3′ / opponent interaction
- Base commit: d7384ccfb8a8b06baa480536973e9110c11d23cd
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-07-31T03:02:46Z
- Last updated UTC: 2026-07-31T04:21:00Z

## Outcome

`TEMPORALLY_ORDERED_PRESSURE_SIGNAL_PREFLIGHT_ONLY`. The 50-turn matched DiD contact
hazard ratio is 0.6061, CI [0.4100,0.8954]; the entirely pre-loss 20-turn result is
0.5103, CI [0.2928,0.8407]. This permits only a separately frozen conditioned versus
identical-always-on versus unchanged-control value preflight.

## Frozen protocol

`docs/h3-numeric-pressure-contact-causality-protocol-2026-07-31.md`.

## Exclusive write set

- this task record;
- `docs/h3-numeric-pressure-contact-causality-protocol-2026-07-31.md`;
- `cgauto/h3_numeric_pressure_contact_causality.py` (new);
- `tests/test_h3_numeric_pressure_contact_causality.py` (new);
- `data/analysis/live-agent-6553250/h3-numeric-pressure-contact-causality-*` (new compact);
- `local_codex_1/h3-numeric-pressure-contact-causality/` (new compact);
- own status/messages;
- register/BACKLOG/CONSTRAINTS/STATE/live ledger only at closeout.

## Shared read-only paths

- Exact D159 raw/result manifests and their 200 named raw-game/trajectory products.
- Existing replay decoder, H3/N2/M5 evidence, command parser, mechanics, and current
  canonical documents.

## Do not touch

- `rust/src/bin/yamo_orchard_live.rs` (byte-sacred).
- Any existing analyzer/result/protocol, raw game, processed trajectory, sealed range,
  map, cron, source policy, simulator/referee, peer path, submission tooling, or Arena.
- No formatter over `rust/src/bin/` or `cgauto/`.

## Deliverables

- Frozen protocol, deterministic analyzer/tests, compact JSON/report/manifest.
- One frozen verdict, canonical closeout, and handoff to `chatgpt_1`.

## Acceptance checks

- Exact D159 population/identity/hash/decode gates and zero out-of-panel reads.
- Exact third-worker event time, crop risk exposure, first-contact event, and permanent
  crossover reconstruction.
- Pretreatment-only nearest matching, balance report, matched-window event study, and
  10,000 deterministic game-cluster bootstrap replicates.
- `py_compile`, built-in self-test, focused pytest, repeated output byte identity.

## Arena authority

Read-only platform access: not needed.
Platform mutation: forbidden. No candidate, TestSession, submission, or Arena action.

## Handoff

Pushed result commit with hashes, cohort/matching/event-study counts, frozen gate table,
validation evidence, and an explicit `chatgpt_1` peer-review request.

## Progress

- 2026-07-31T03:08:52Z: deterministic analyzer and focused tests implemented;
  `py_compile`, built-in self-test, and focused pytest (7/7) pass. Full exact-panel
  materialization is the next checkpoint.
- 2026-07-31T03:11:52Z: exact 200-game materialization and byte-identical repeat pass;
  all integrity, support, balance, and materiality gates pass.

## Acceptance

- Exact D159 hash/population/identity/decode/outside-read gates: passed, 200/200.
- Main matched support: 70 pairs, 29 identities, both seats; maximum absolute
  post-match SMD 0.1806.
- Pre-loss support: 69 pairs, 28 identities, both seats.
- Frozen materiality gates: passed for coverage and both DiD windows.
- `py_compile`, self-test, focused pytest (7), and byte-identical repeat: passed.
- Canonical closeout and peer handoff: complete; acknowledgement pending.
