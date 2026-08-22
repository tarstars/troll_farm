# D2 Phase 1 — troll-moves viewer

**What it is, plainly.** One web page per recorded oscillation, showing the board and letting you
step through the stuck turns with the arrow keys. It is for looking, not for deciding: it records
nothing and offers no opinion about what the bot should have done.

Authorized by `local_claude_1` policy `20260815T070500Z` (owner ruling: form approved,
display-only, live sessions). Claimed `c5f1add3`. Phase 2 — Decision Packet overlay and blind
mode — is gated on P-1 and a separate go, and is not built.

## Use

```
python3 claude_1/viewer/build_viewer.py --self-test          # 11 checks, each observed rejecting
python3 claude_1/viewer/build_viewer.py --out claude_1/viewer/out
```

Then open `claude_1/viewer/out/index.html`. No server. Each page is self-contained: no external
script, stylesheet, font or image, so it works from a file:// URL and offline.

Keys: `←` `→` step a turn, `Home` / `End` jump to the ends.

## What is fact and what is inference — the point of the design

A command is an **order**, not a landing. `engine.rs::next_cell` returns the ordered target only
when `d <= speed`, so a distant `MOVE` lands part-way; and simultaneous resolution against the
opponent can change the result again. The opponent's own commands are **not in this library**, so
no realized position can be reconstructed from it.

So the pages distinguish three things, and never blur them:

| drawn as | meaning |
|---|---|
| verbatim command line, solid text | **ground truth** — copied from the referee transcript |
| solid red circle, solid letters | **ground truth at entry** — opponent and plants, frozen |
| **dashed hollow blue circle** | **inference** — where our troll would be *if* the order completed |

Every side panel is stamped `at entry` and never advances. Plant growth, harvests, cargo and
inventories cannot be derived honestly from our own commands alone.

**This generator does not re-implement the referee.** Computing a predicted landing would mean a
BFS/speed mirror of `engine.rs`, and a mirror that disagrees with the authority is worse than no
mirror at all.

## Built through the verifying loader

Pages are generated from `load_library(verify=True)`, which fails closed on any digest, file-set,
count, schema or enumeration mismatch. If the frozen library is not intact, **no page is produced
at all**. The library itself is read-only input and is never written.

## Guards — every check observed rejecting

`--self-test` runs 11 cases. Each check is demonstrated failing before it is trusted:

- unknown map character (the alphabet `# . 0 1 + ~` was measured, not assumed)
- situation-count drift
- fewer command rows than `length_turns`
- a hole in the turn sequence
- a derived position emitted without its inference marking
- inferred positions drawn with no legend explaining them
- inference not dashed; opponent drawn hollow like inference

Two of these found real defects in this code before delivery:

1. **The inference-marking check was inert.** It matched the class against the whole tag, and
   `data-role="derived-position"` itself contains the substring `derived` — so an unmarked
   element satisfied it. Only the negative control exposed that; the check now reads the `class`
   attribute specifically.
2. **The opponent was drawn hollow**, the same treatment as inference, while the legend claimed
   "solid red circle". Ground truth and assumption looked alike — the exact confusion the honesty
   rules exist to prevent.

## Revision 2 — four blockers from `codex_1`'s review, all fixed

1. **Inventory columns were mislabelled.** The build shipped `PLUM, APPLE, LEMON, BANANA, ORANGE,
   WOOD`; the subject's own constants are `PLUM, LEMON, APPLE, BANANA, IRON, WOOD` — APPLE and
   LEMON transposed, and `ORANGE` invented where the authority has `IRON`. `check_slot_order()`
   now **reads those constants out of the subject** and fails the build on disagreement. I had
   asserted a label instead of deriving it.
2. **The frozen evidence a ruling needs is now rendered**: mechanism and its evidence sentence,
   blocker state and cell, classifier version, detector counts, episode/dedupe identity, the
   `unresolved` notes, and full provenance (subject, map, seed, seat, instrument, corpus,
   content digest). The blocker's cell is marked on the board.
3. **Frame 0 is now the entry state**, before any command is applied. The entry position is the
   only exact board state in the window, and the first build skipped past it by applying turn
   one's command before the first render — so the one frame that is ground truth was the one
   frame never shown. It is drawn **solid** and labelled exact.
4. **The ordered cell has its own mark** (blue square outline). Previously the dashed unit sat on
   the target and nothing else did, so a recorded order and an assumed arrival were the same
   pixel.

Self-test is now **23 cases**, including a control that reproduces the original wrong slot order
and confirms the guard rejects it.

## Known limit, stated rather than papered over

**The visual layer is unverified by execution.** No browser is installed on this host, nothing was
screenshotted. The checks prove the marks carry their structural role and class and that `.own`
and `.opp` are styled differently — they do **not** prove the page looks right. A stylesheet that
is well-formed but visually confusing passes every case. **One human look is needed before the
first live session.**
