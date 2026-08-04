# 20260804-readable-no-orchard-arena: submit exact readable 1,470-line source

- Status: in progress — preflight complete, mutation gated on remote record verification
- Priority: direct owner assignment
- Record owner / work owner / Arena controller: `local_codex_1`
- Created UTC: 2026-08-04T11:25:02Z
- Last updated UTC: 2026-08-04T11:25:02Z

## Objective and authority

Submit the exact readable orchard-stripped source requested by the owner. This is the readable
artifact itself, not its behavior-equivalent compact expansion. The owner knows the orchard's
measured value and explicitly chose this no-orchard deployment, so this is an owner-directed Arena
override rather than a frozen-gate promotion. Only `local_codex_1` may mutate the Arena.

## Exact candidate

- Path: `local_codex_1/readable-orchard-code-cost/e7a-without-orchard-readable.rs`
- Size: 75,634 bytes; 1,475 physical lines; 1,470 nonblank/noncomment code lines
- SHA-256: `98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29`
- Behavior-equivalent compact parent SHA-256: `102caecd...`
- Publication: candidate and verification report are committed and remotely verified at
  `e9e2fabbf44dcbf6fb9635597b068bdd0f8651e5`.

The readable file compiles directly, passes empty input, expands lexically to the compact parent
byte-for-byte, and is exact to that parent over all 25 frozen live fixtures / 7,234 commands. Its
hash is new to the Arena registry. The behavior is a deliberate orchard ablation; prior live
no-orchard evidence was lower than orchard, so no value-gate or capacity-A/A claim is made.

## Pre-mutation baseline

At 2026-08-04T11:24:35Z, exact orchard resident `6592744` / submission `41087983` has 160/160
finished games, score 22.88, rank 32/137, 99W/2T/59L, 19 catastrophes, negative-margin mass
4,703, zero runtime signals, and clean identity. Read-only platform recovery confirms exact
62,820-byte E7a SHA-256 `97bfe71e...`. Protected
`rust/src/bin/yamo_orchard_live.rs` remains exact at SHA prefix `fff6669b`.

## Serialized execution

1. Commit, push, and remotely verify this task, start message, status, state, ledger opening, and
   preflight checkpoint before mutation.
2. Submit the exact candidate path with `cgauto/api_submit_once.py` exactly once and preserve its
   complete response and returned submission id.
3. Do not retry an ambiguous response. Discover the resulting agent id, recover the live source
   against the exact readable SHA, and record the new identity.
4. Capture an initial submission-scoped health checkpoint after enough games finish to detect
   compile/runtime/identity damage. Leave the requested source active if source, identity, and
   runtime health are clean; this task does not reject it merely for a cold-start score.
5. Restore exact orchard only on an unambiguous source/identity/runtime failure, not merely weak
   performance. Any restore is one canonical call and is recorded before closure.
6. Publish the result, reconcile state/ledger/status, and notify the owner and peers.

## Write set and exclusions

- `data/analysis/live-agent-6553250/readable-no-orchard-arena-20260804/`;
- this task, own status/messages, live STATE and ledger;
- submission history metadata if the accepted identity is unambiguous.

Unrelated simplification artifacts, collector cache changes, raw games, cron, external storage,
sealed map ranges, and all bot source files except read-only access to the exact candidate are out
of scope. `cgauto/api_submit.py` keeps the exact orchard safety default unless separately decided.
