# The test set that is still a test

Use the open maps to build; use the sealed maps once to judge a frozen build.

| Set | May we look? | What its number means |
| --- | --- | --- |
| Development | Yes, without limit | Useful for defects, mechanics, tuning, and choosing a gate. It says nothing new about generalisation. |
| `holdout-001` | No, until one frozen gate | A paired result on unseen official seeds. After that result starts, these maps become development data. |
| External opponents | Names and IDs are open; results require a gate | Performance against five exact public agents rather than our own family of champion variants. |

`development-manifest.json` retires the old 24-map smoke, 200-map H2H panel, and 72-map neural panel into development. `external-opponents.json` locks, in order, delineate `6479768`, wala `6481141`, escdemon `6483545`, norxondor `6480540`, and laconic `6482055`.

## What is sealed now

The active set and its already-drawn disjoint successor each contain 512 seeds for `rust/src/game/official_mapgen.rs::generate_official(i64)`, pinned to main commit `370fa63cae12eda129ff5553c33a7086dfcb87c2` and source SHA-256 `5746607acdbaabed91720a9f7e75d73b55b6d87fdfe37f4f14ae3e4934d67971`. The source is the official Java-SHA1PRNG map-generator port, not the synthetic generator.

The reserved population is `[4,000,000,000, 4,000,100,000)`. Before the draw, `population-audit.json` scanned every blob at all nine authoritative remote tips: 13,461 unique blobs, 668,884,608 bytes, zero literal seed tokens in that range. The champion froze before this population was declared, the selected seeds were never written in plaintext to the repository, and neither their values nor their maps were printed during creation.

The size is measured, not borrowed from the ladder. Thirteen local candidate/control pairings on the retired 200-map panel give player-0 paired-arm SD `40.203456`. The player-0 unit matches TestSession. At `n = 512`, the required calculation is:

```text
1.96 * 40.203456 * sqrt(2 / 512) = 4.924923 score
```

So a true paired mean advantage needs to exceed about 4.93 score points for the normal-approximation 95% lower bound to clear zero. The direct paired-difference SD is `47.930793`; its check is a 4.152-score half-width. See `size-calibration.json` for every pinned input and pair.

## Check without looking

The coordinator-private encryption keys, secret allocation key, and audit state are at `/home/tarstars/.cache/troll-farm/sealed-holdout/coordinator/20260904`, outside Git and shared artifact storage. The allocation key ranks the full 100,000-seed population once; each holdout receives the next non-overlapping 512-seed slice without decrypting any active holdout. This command checks key commitments, ciphertext SHA-256 and HMAC, tracked/private lifecycle agreement, and read markers. It does not decrypt the payload:

```bash
python3 codex_1/sealed-holdout/seal.py verify \
  --root codex_1/sealed-holdout \
  --key-dir /home/tarstars/.cache/troll-farm/sealed-holdout/coordinator/20260904
```

Today it must say `active=holdout-001`, `standby=holdout-002`, and `authorized_opens=0`.

## The one-read gate

Finish all diagnostics on development maps first. Freeze the baseline, candidate, exact decision rule, opponent manifest, and active seal in one Git commit. The helper creates the gate manifest without opening the seal:

```bash
python3 codex_1/sealed-holdout/seal.py prepare-gate \
  --root codex_1/sealed-holdout \
  --baseline path/to/baseline.rs \
  --candidate path/to/candidate.rs \
  --external-opponents codex_1/sealed-holdout/external-opponents.json \
  --decision-rule 'all 512 pairs valid and paired mean score delta lower 95% bound > 0' \
  --output path/to/gate.json
```

Commit those exact files. Then pass the full 40-hex commit to `open`:

```bash
python3 codex_1/sealed-holdout/seal.py open \
  --root codex_1/sealed-holdout \
  --key-dir /home/tarstars/.cache/troll-farm/sealed-holdout/coordinator/20260904 \
  --gate-manifest path/to/gate.json \
  --gate-commit FULL_40_HEX_COMMIT \
  --reveal-path path/to/retired/holdout-001-seed-bank.json
```

`open` refuses an uncommitted gate, changed source bytes, a changed opponent manifest, a second authorized read, or any read without a sealed successor. On success it emits a `cgauto/field_panel.py --seed-bank` compatible bank: each hidden seed is assigned round-robin over the five locked opponents, and the baseline/candidate must use that same `(opponent_agent, seed)` block as player 0. It writes a permanent private open marker and tracked receipt, retires `holdout-001` to development, activates `holdout-002`, and leaves no standby. A failed or partial platform run still consumes the opened holdout.

Before `holdout-002` can ever be opened, create and commit another disjoint standby:

```bash
python3 codex_1/sealed-holdout/seal.py add-standby \
  --root codex_1/sealed-holdout \
  --key-dir /home/tarstars/.cache/troll-farm/sealed-holdout/coordinator/20260904
```

## What the seal does not promise

The seal prevents accidental repository inspection, detects ciphertext or manifest edits and ordinary worktree rollback, and makes the authorized-read history executable. It is not protection from a privileged process or person who can copy a private key, derive allocations, decrypt outside this tool, or roll back/delete both Git state and the private audit directory. It also cannot prove the platform never produced an identical map geometry from another seed, make TestSession deterministic or available, prove that a later runner used the committed candidate bytes, or guarantee that external-game variance matches the local sizing sample. If external variance is larger, the 4.93-point resolution is optimistic. Those are explicit review conditions, not hidden assumptions.
