# Curriculum Level 5 D11 optimized Rust kernel K2 result — 2026-07-20

## Verdict

**Accept the K2 actor kernel.**  The sole preregistered persistent-workspace and bounds-elision
rewrite passes source size, direct compilation, complete numerical parity, legal-action, and every
latency gate.  It is now an eligible component for separately frozen source integration and
autonomous high-level recipe/first-move experiments.  It does not by itself create an Arena
candidate or authorize submission.

The frozen protocol SHA-256 is
`8741b9e14d1462e940dd72289100fca3af49e91bc210b3fc95fe5dfa447545bc`.

## Exact result

The generated dependency-free Rust 2021 source is 55,768 UTF-8 bytes, including 51,945 bytes for
the actor kernel and embedded payload and 3,658 bytes for its parity/benchmark harness.  It compiles
directly with `rustc 1.75.0 --edition=2021 -O` with empty stdout/stderr.

On the immutable 512-observation corpus:

- all **1,610,752 logits** are finite;
- maximum/mean Rust-versus-Python absolute logit error is
  **0.0000686646 / 0.00000312950**, passing the `1e-4` maximum;
- masked action agreement is **512/512 = 100%**;
- Rust chooses zero illegal actions and writes no stderr.

The parity values are identical to K1, confirming that the optimization preserved its operation
order.  Only after that pass, the exact frozen timing run measured initialization plus the first
two-worker pair at **22.653 ms**.  After 16 unmeasured warmup pairs, 1,000 measured two-worker pairs
were:

| Statistic | K1 | K2 | Frozen K2 gate |
|---|---:|---:|---:|
| median | 28.387 ms | **7.035 ms** | diagnostic |
| p95 | 31.484 ms | **10.246 ms** | <=45 ms |
| maximum | 129.258 ms | **34.962 ms** | <=50 ms |

Thus K2 passes the full timing conjunction with substantial headroom, including on the same busy
host where K1 exposed its tail.

## Anchors and boundary

- source SHA-256: `cd81cb3b1d10eacdf3f58f645dc6798b60e8ee4b6dae0d669bff8b7d6a4e683c`;
- binary SHA-256: `ac5bc3340ab43eb90b555a57cffb35508a82833da54cfc1395528d73f7c33907`;
- payload SHA-256: `eda4899464bde95b28691db89fe2ee171d7de50c585d2595a80c8d2d0c816832`;
- corpus compressed/raw SHA-256:
  `392bbea038a5d2e0e6a60a4dd2fd459b56752470d5b13c60a3472dca90943d62` /
  `cbb4bb88013e574c81955dd9ba083730720e464c8641c3fa7af14709ff75f77b`;
- machine-readable qualification SHA-256:
  `d561307f3bd684e0f7bcc1d61adaf1667f38b3beb57301cfffcc0acbc09298fd`.

The accepted component still receives one of eight requested worker recipes.  Integration must
account for the referee parser, observation construction, legal mask, sequential two-worker action
application, TRAIN decisions, and a high-level recipe selector.  Those missing components—not
actor quality or actor inference—are now the deployment boundary.

