# H3a — Phase-21 treatment reconstruction

Prepared UTC: 2026-07-31T07:16:00Z

Task: `20260731-h3a-pressure-treatment-reconstruction`

Verdict: **`TREATMENT_REPRODUCIBLE`**

This canonical report supersedes `chatgpt_1/h3a-reconstruction-result-2026-07-31.md`.
The canonical machine result is
`data/analysis/live-agent-6553250/h3a-pressure-treatment-reconstruction-result-2026-07-31.json`.

## Decision

The archived Phase-21 opponent-crop dual-value treatment is exactly reproducible from the
frozen slim fallback. The inverse transformation restores the fallback byte-for-byte, and
the independent archived full-parent generator produces the identical frozen treatment.

The source delta is fully classified as provenance tracking plus the original existing-tree
candidate score transformation. No unrelated source change exists.

This result answers source reproducibility only. It does not authorize a conditioned arm,
map range, value panel, candidate, TestSession, submission, or Arena action.

## Frozen artifacts

| artifact | SHA-256 |
|---|---|
| fallback slim source | `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55` |
| treatment slim source | `083107f53e412be49fa06163f511a1453f7dc5447baed51ecda6d567785044cf` |
| digest recorded inside treatment sidecar | `083107f53e412be49fa06163f511a1453f7dc5447baed51ecda6d567785044cf` |
| treatment sidecar file | `9811fb4f0d2ed3112b5eeef399f8ec36fc9b0a2a296f9ee1ca01fbe9415b249c` |
| full parent source | `da53b0f66a0224bf9c8d5796d69905a9bebcf1e71ee97e4b65e72a2fdea046e9` |

The sidecar content records the treatment source digest. The SHA-256 of the sidecar file
itself is a different quantity and is listed separately above.

Paths:

- fallback:
  `cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`;
- treatment:
  `cgauto/submissions/candidate-agent6553250-opponent-crop-dual-value-e6-slim.min.rs`;
- treatment sidecar:
  `cgauto/submissions/candidate-agent6553250-opponent-crop-dual-value-e6-slim.min.rs.sha256`;
- archived generator:
  `cgauto/make_opponent_crop_dual_value_candidate.py`.

## Exact equality checks

All five pass:

1. direct seven-edit fallback → treatment;
2. inverse seven-edit treatment → fallback;
3. archived full-parent generator → treatment;
4. repeated direct output identity;
5. repeated inverse output identity.

The complete treatment is seven classified edits totaling **+1,811 bytes**.

## Seven edits

1. **Provenance state fields** — adds plant-history initialization, previous live plants,
   own plant attempts, and tracked opponent crops.
2. **Provenance initialization** — initializes only those four fields.
3. **Provenance and scoring methods** — tracks newly appearing live plants not preceded by
   our PLANT; retains them only while live; considers only existing `Target::Tree`
   candidates; computes existing BFS/ceil-div ETA; and doubles the existing score when
   ETA ≤ 6 using exactly `candidate.score += candidate.score`.
4. **Lifecycle reconciliation** — updates provenance before otherwise unchanged opening
   logic.
5. **Scoring hook** — applies the method to the already-generated candidate vector.
6. **Main-loop own-attempt recording** — records selected own PLANT commands after unchanged
   conflict resolution.
7. **Wrapper own-attempt recording** — records already-emitted orchard-wrapper PLANT
   commands without changing them.

The exhaustive classification finds:

- no new multiplier;
- no different ETA threshold;
- no new target or command;
- no commitment;
- no harvest rewrite;
- no scheduler change;
- no unrelated byte change.

## Eligibility fixtures

With input score 12.5:

| fixture | output |
|---|---:|
| tracked tree target, ETA 6 | 25.0 |
| tracked tree target, ETA 7 | 12.5 |
| untracked tree | 12.5 |
| tracked non-tree target | 12.5 |
| unreachable target | 12.5 |

This confirms the exact inclusive ETA-6 boundary and every required ineligible case.

## Host validation

Coordinator validation commit:

`c7d8959be7c2269139410aaaee6ffad3f28602b9`

Observed:

- Python compile: pass;
- built-in self-test: pass;
- focused pytest: **14 passed**;
- direct no-compile output repeated byte-identically;
- full compiled output repeated byte-identically;
- `git diff --check`: pass.

Machine-result hashes:

- no-compile JSON:
  `5f392ab3466e46fc66841117b3848bcc5a7bd310f90ab3fe490b8c4405d2ff4a`;
- compiled JSON:
  `a8679546cf4225531175f5185061c26300c87f5d7f006a1e08e0303bd8a1cc32`.

Both exact frozen artifacts compile with explicit valid crate names:

| source | crate | binary SHA-256 | bytes |
|---|---|---|---:|
| fallback | `h3a_fallback` | `a732c30f3a4de3e3d735cef6c320f5727cb669cb99de3dd797510f6da6fa2d11` | 13,576,832 |
| treatment | `h3a_treatment` | `37b6dabc6f891a0f7906fb43b7b0d399dec63a816ae7eb612a6e1691ff4b698e` | 13,587,432 |

## Consequence

The reconstruction prerequisite for a possible H3a three-arm protocol is satisfied. A future
protocol may compare:

- unchanged resident;
- exact treatment always on under its archived eligibility;
- the identical treatment armed only after visible opponent roster reaches three.

That protocol remains a separate decision. The conditioned arm must beat both the identical
always-on arm and unchanged control. This result alone does not reserve a seed range or
authorize implementation or execution.

## Safety

No existing source was modified. No runner arm was created. No map, game, raw/sealed data,
simulator, referee, resident, module registry, submission tooling, TestSession, or Arena
surface was read or changed beyond compiling the two frozen standalone source artifacts.
