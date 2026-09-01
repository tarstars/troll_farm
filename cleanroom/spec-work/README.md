# spec-work — the spec-writer's instruments (NOT part of the package)

Nothing in this directory goes to the implementer. `cleanroom/package/` is the package;
this directory is how it was made, kept so the numbers in it can be re-derived.

| file | what it does |
|------|--------------|
| `corpus.py` | decodes the champion's 160 recorded ladder games into per-turn board states paired with its commands. **Drops every `MSG` at the source** — the champion of record is the diagnostics build and its `MSG` line narrates its internals, which is a leak into a document written from observable play only. |
| `measure.py` | recomputes every number cited in `cleanroom/package/CHAMPION-BEHAVIOUR.md` and writes `observations.json` with counts and (game id, turn) citations; also writes `cleanroom/package/champion-purchases.json` (the per-match purchase data the implementer gets, §4 of the behaviour document). |
| `observations.json` | the output of `measure.py`; the audit trail behind the behaviour document. |
| `export_maps.py` | freezes 24 real starting positions into `cleanroom/package/harness/maps/`. Six per map height, by ascending match id, so the slice is not a selection. |
| `reference_parity.py` | proves the harness's stripped, announcement-free reference binary plays identically to the champion of record. |

## Reproducing the package's numbers

    python3 cleanroom/spec-work/measure.py            # ~40 s; rewrites observations.json
    python3 cleanroom/spec-work/export_maps.py        # rewrites the 24 frozen maps

## Rebuilding the reference binary

The harness ships the champion of record as a compiled, stripped executable. It is built from
`readable/denial-off-champion.rs` with two changes, neither of which touches play:

1. the two turn-1 announcement strings (which name the bot's internal roles) are blanked, and the
   `MSG` push is removed;
2. the binary is `strip`ped — **unstripped, its Rust symbol names expose the bot's entire
   internal structure**, which is the loudest leakage channel found on this card.

    RUSTC=~/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustc
    # blank the announcements, drop the MSG push, then:
    $RUSTC --edition=2021 -O -Awarnings reference.rs -o reference
    strip reference -o cleanroom/package/harness/reference-bot
    python3 cleanroom/spec-work/reference_parity.py <champion-binary> \
        cleanroom/package/harness/reference-bot cleanroom/package/harness/maps

The parity run of 2026-09-01 compared **9,502 seat-turns over the 24 frozen maps and found
0 differences** (`MSG` ignored). `strings` on the shipped binary finds **0** Rust-mangled
symbols.

Shipped binary SHA-256: `b24c3a0e3d14da390ed92ab9c6d909d79336eea2eb1ebcddd0c6f801a1afe68c`
Built from `readable/denial-off-champion.rs` SHA-256 `4ce3d1e85e8962d84c0ecb1a071de46e844d24f7dbe5a31bd6ca0579db552143`.
