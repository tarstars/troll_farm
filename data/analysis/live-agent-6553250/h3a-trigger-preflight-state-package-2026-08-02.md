# H3a authoritative-state reconstruction package — 2026-08-02

## Purpose and consumption boundary

This package supplies one static-map record per exact open game and one outcome-blind state
record per resident decision for the H3a trigger preflight. It exists because the public-frame
export does not directly contain the referee's tree input list.

The records are sufficient to inspect cells, units, inventories, tree state, causal
planting provenance, and raw resident commands. They do **not** themselves prove that a tree
was admitted to the archived A1 candidate set or received its score transformation. Claude
still owns that equality proof and the gate-4 verdict.

No sealed map/game, holdout, future game, outcome label, score, final margin, or future-turn
field appears in a decision row.

## Package files

- `h3a-trigger-preflight-state-package-2026-08-02.maps.jsonl.gz`: 17 rows, 3,322 bytes;
  SHA-256 `decfa8f49580a0fb5723c5a35549f3d2b10a423f247bc77fc84ab46aed94ccd7`;
  uncompressed SHA-256
  `ea35cda59db6c145e27bed7ca85461c9546169798c864a6b3ff671ce732380d7`.
- `h3a-trigger-preflight-state-package-2026-08-02.decisions.jsonl.gz`: 5,100 rows,
  271,903 bytes; SHA-256
  `a60cbf05a81fecd33c1cda48d514f238199a9ea3171ed5e2cef98ef6c4980f1d`;
  uncompressed SHA-256
  `c7c6567f53d02a0103fd0cff255f9c4c01979243eba7e7b29e39b1d012ac4a0d`.
- `h3a-trigger-preflight-state-package-2026-08-02.manifest.json`: 20,721 bytes;
  SHA-256 `4336ce47a1529c47ce920a1fdccc515b8b22383e48107740c630afcd2c9b152e`.

Every game has exactly 300 resident decision rows. Maps preserve width, height, authoritative
walkable cells, perspective-normalized shacks, iron, water, starting inventories, and seed.
Decision rows preserve both inventories, full resident and opponent troll states, opponent
roster count, `next_id`, ordered tree input, causal `created_by`, and raw issued commands.

Trees have no persistent referee ID. `tree_index` is only the current input-list order; the
archived policy's exact identity is `(x,y)` through `Target::Tree(Cell)`.

## Exactness boundary discovered during regeneration

A raw-command replay through the unchanged locked A2-0b referee was not sufficient:

1. The locked parser accepts numeric fruit aliases `0..3` but passes the numeric token into
   the historical engine, which panics. Exactly 213 accepted `PICK`/`PLANT` aliases occur in
   four games. The wrapper canonicalizes only those aliases to their named fruit; raw commands
   remain unchanged in decision rows.
2. Continued movement RNG first disagreed with the public landed position in game `897781216`
   at turn 12. The wrapper therefore feeds the unchanged referee each same-turn public MOVE
   landing as a direct target; a MOVE with no landed event becomes `WAIT`. There are 11,145
   public landings and 232 no-landing MOVE commands.
3. The platform accepts empty `MSG ;`, while the locked parser trims it to unknown `MSG`.
   Exactly 600 such inert messages are supplied inert text only for the replay step.

This makes the result a **causal, public-outcome-anchored state reconstruction**, not an
independent continued-RNG reproduction. A turn's public outcomes are used only to apply that
turn and construct the next decision state. They never enter the decision row for the turn
that produced them, and no later outcome enters an earlier row.

The unchanged locked action mechanics then apply harvest, plant, chop, pick, train, drop,
mine, plant ticking, inventory changes, and tree changes. All wrapper interventions and their
per-game counts are explicit in the manifest. Claude must either accept this integrity basis
for gate 4 or return `BLOCKED_INTEGRITY_OR_REPRODUCTION`; it must not silently call it a pure
locked replay.

## Validation

All passed:

- 17/17 regenerated terrain records byte-equivalent to the public frame-0 maps;
- 5,117/5,117 public inventory snapshots matched (17 initial plus 5,100 post-turn);
- 11,145/11,145 public landed MOVE facts matched unit positions;
- 48/48 landed TRAIN facts matched roster changes;
- 779/779 landed PLANT facts matched creator, troll, and species;
- 17/17 final score vectors reproduced from final inventories;
- zero critical and zero unclassified referee issues;
- five supported noncritical issues: four `no_fruit`, one `pick_stock_lost`;
- 17 maps, 5,100 decisions, exact game/turn ordering, valid provenance labels, and no outcome
  fields in decisions;
- Python compilation/self-test, release build, gzip integrity, JSON parse, sacred and locked
  source hashes, and a second byte-identical full export.

Locked SHA-256 anchors remained unchanged: referee `518c2228...`, locked A2-0b runner
`1054a047...`, and sacred resident `fff6669b...`.

## Reproduction

```bash
cd rust
cargo build --release --bin h3a_open_trajectory_state_export
cd ..
python3 local_codex_1/h3a_authoritative_state_export.py \
  --package data/analysis/live-agent-6553250/h3a-trigger-preflight-package-2026-08-02.games.jsonl.gz \
  --source-manifest data/analysis/live-agent-6553250/h3a-trigger-preflight-package-2026-08-02.manifest.json \
  --binary rust/target/release/h3a_open_trajectory_state_export \
  --output-prefix data/analysis/live-agent-6553250/h3a-trigger-preflight-state-package-2026-08-02 \
  --created-utc 2026-08-02T15:17:51Z \
  --repo-root .
```

Exporter source SHA-256:
`914bba2735509e0be8ef1d8d5c3e9d48460699d00c6d50cac81461b4ce3dda2c`.
Rust helper source SHA-256:
`61b0a8dfb8685b056ac2cb331e485e4c0830db402a5a1be3390551c364406447`.
Built helper SHA-256:
`e4635d17dab25578d7f83c19dda85d2daf1d6b533b3440e76c4ad97cee8dd1bb`.
