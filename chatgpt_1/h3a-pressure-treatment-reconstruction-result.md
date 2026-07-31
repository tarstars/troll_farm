# H3a — exact Phase-21 treatment reconstruction

Date: 2026-07-31
Implementation owner: `chatgpt_1`
Reviewer/integrator: `local_codex_1`
Verdict: **`TREATMENT_REPRODUCIBLE`**

## Decision

The archived Phase-21 opponent-crop dual-value treatment is exactly reproducible from the
frozen slim fallback. Removing the same seven edits restores the fallback byte-for-byte,
and the independent archived full-parent generator produces the identical treatment.

This closes source reproducibility only. It does not authorize a conditioned runner arm,
map range, value panel, candidate, TestSession, submission, or Arena action.

## Frozen artifacts

| artifact | SHA-256 |
|---|---|
| fallback slim source | `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55` |
| treatment slim source | `083107f53e412be49fa06163f511a1453f7dc5447baed51ecda6d567785044cf` |
| sidecar file | `9811fb4f0d2ed3112b5eeef399f8ec36fc9b0a2a296f9ee1ca01fbe9415b249c` |
| digest recorded inside sidecar | `083107f53e412be49fa06163f511a1453f7dc5447baed51ecda6d567785044cf` |
| full parent source | `da53b0f66a0224bf9c8d5796d69905a9bebcf1e71ee97e4b65e72a2fdea046e9` |

The sidecar distinction is intentional: its file hash is not the treatment digest written
inside the file.

## Exact reconstruction

All five equality checks pass:

1. direct seven-edit fallback → treatment;
2. inverse seven-edit treatment → fallback;
3. archived full-parent generator → treatment;
4. repeated direct output identity;
5. repeated inverse output identity.

The complete treatment is seven edits totaling **+1,811 bytes**:

1. add provenance state fields;
2. initialize provenance state;
3. add provenance and dual-value methods;
4. reconcile provenance before otherwise unchanged opening logic;
5. apply dual value to the existing candidate vector;
6. record selected main-loop own PLANT attempts;
7. record already-emitted wrapper PLANT attempts.

Every delta belongs to provenance/lifecycle or the original scoring hook. Eligibility is
limited to an existing tracked `Target::Tree`; distance uses existing BFS and ceil-div;
the inclusive threshold is ETA ≤6; the score operation is exactly
`candidate.score += candidate.score`.

There is no new multiplier, ETA, target, command, commitment, harvest rewrite, scheduler
change, or unrelated byte.

## Fixtures and compilation

With input score 12.5, the tracked tree at ETA 6 returns 25.0. ETA 7, untracked,
non-tree, and unreachable fixtures all remain 12.5.

Both exact frozen artifacts compile:

| source | crate | binary SHA-256 | bytes |
|---|---|---|---:|
| fallback | `h3a_fallback` | `a732c30f3a4de3e3d735cef6c320f5727cb669cb99de3dd797510f6da6fa2d11` | 13,576,832 |
| treatment | `h3a_treatment` | `37b6dabc6f891a0f7906fb43b7b0d399dec63a816ae7eb612a6e1691ff4b698e` | 13,587,432 |

## Validation history

The peer implementation needed three host-found acceptance corrections: repository-root
import, valid explicit Rust crate names for `.min.rs`, and deterministic compile metadata
plus a normal namespace test import. The corrected implementation passes:

- Python compile and self-test;
- 14 focused tests;
- two byte-identical direct no-compile results;
- two byte-identical full compiled results;
- exact frozen hashes and sacred resident hash.

Result hashes:

- no-compile JSON:
  `5f392ab3466e46fc66841117b3848bcc5a7bd310f90ab3fe490b8c4405d2ff4a`;
- compiled JSON:
  `a8679546cf4225531175f5185061c26300c87f5d7f006a1e08e0303bd8a1cc32`.

Peer implementation/test commits are preserved. After peer head `8ae01f5` exceeded its
lease on a documentation-only blocker, the integrator took over the canonical result paths;
no peer file was deleted or rewritten.

## Consequence

The reconstruction prerequisite is satisfied. A separately reviewed protocol may consider
unchanged control, the exact treatment always on, and the identical treatment conditioned
on visible opponent workforce pressure. It must show conditioning is load-bearing against
both controls.

No such protocol is cut here. No runner arm, map/range, panel, candidate, platform, or
Arena action occurred.

Canonical machine result:
`data/analysis/live-agent-6553250/h3a-pressure-treatment-reconstruction-result-2026-07-31.json`.
