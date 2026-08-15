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

## Known limit, stated rather than papered over

**The visual layer is unverified by execution.** No browser is installed on this host, nothing was
screenshotted. The checks prove the marks carry their structural role and class and that `.own`
and `.opp` are styled differently — they do **not** prove the page looks right. A stylesheet that
is well-formed but visually confusing passes every case. **One human look is needed before the
first live session.**
