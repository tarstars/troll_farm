# Oscillation situation library — the CHAMPION of record `547fa706…`

**Whose episodes these are:** the Door-1 champion the owner kept on 2026-08-21,
`claude_1/chop4c/candidate-door1.rs`, sha256
`547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0`, git
`dc43d633ab30154d78bad05425b026ca5487d797`. **They are not any other bot's regression set.**

| | |
|---|---|
| subject | champion of record, judged against **itself** (`run_identity: floor`) |
| panel | the **same config** the `98628e98` library used — only the subject and the output paths differ (`panel-config-diff.json` lists every field) |
| instrument / corpus | `fuzz-panel/5-two-player-phase-merged-referee` / `c5-two-player-phase-merged-2026-08-11` |
| situations / episodes | **21 / 28** (20 D-1 + 1 P4-only), all `FULL` |
| `library_sha256` | `4d3b36558f317a05acf65c3588bd9b572939645463b938274bc4c588c11e4d45` |
| built by | `../build_oscillation_library.py` **unmodified**, digest-checked before the driver will run |

## THE RULE (owner-approved 2026-08-21)

**A recorded episode belongs to the bot that produced it.** Fixtures are exhibits for
understanding and for the owner's rulings, and regression checks for *that* bot; they are
regenerated for every kept champion and never outlive it. The sibling tree
`../oscillation-library-98628e98/` holds `readable__no_orchard`'s 34 cases — the champion
reproduces 11 of them as the same game — and the owner's rulings taken there are rulings about
**mechanisms** and stand unchanged. A mechanism with no case here has **no exhibit** on the
champion; that is not the same statement as "fixed", and no file in this tree says otherwise.

**Case numbers do not carry across the two libraries.** Old `OSC-013` is this tree's `OSC-011`;
old `OSC-017` is `OSC-010`; old `OSC-012` is `OSC-009`. The full mapping, by game, is in
`carry-over-2026-08-21.md`.

## Contents

- `library/` — 21 frozen situations + `index.json`. Literal data copied out of the referee
  transcript: map rows, plants, both players' units, inventories, and the command line for every
  turn of the window. Nothing calls back into the map generator.
- `identity.json` — **episode identity per case**: digests of exactly the two inputs
  `claude_1/t1/fixture_harness.py::episode_identity` reads (the frozen window commands and the
  entry board), so a later bot can be checked against this library without re-deriving what "the
  same episode" means. 21/21 cases are gate-ready.
- `panel-config.json` + `panel-config-diff.json` — the config, and the field-by-field proof that
  every **measured** field is identical to the old library's.
- `build_subject_library.py` (driver), `run_panel.py` (the harvest run), `build_pages.py`
  (viewer), `verify_identity.py`, `carry_over.py`, `controls.py`, `test_champion_library.py`.
- `carry-over-2026-08-21.{md,json}` — deliverable 2, the mechanism carry-over table.
- `refresh-hook-design-2026-08-21.md` — deliverable 3, **design only, not deployed**.
- `owner-note-champion-library-2026-08-21.md` — deliverable 4.
- `controls-2026-08-21.json`, `identity-verify-2026-08-21.json` — the gate evidence.
- `viewer/` — 21 pages + index, self-contained, open `viewer/index.html` from a `file://` URL.

## Scope

**This library freezes situations only.** No best action, preferred action, ranking,
recommendation, verdict, fix or remedy is recorded anywhere; the M3a silence test walks every key
and every string of every frozen file and is inherited here as
`TestChampionNoBestActionRecorded`.

## Use

```
python3 -m unittest test_champion_library                                   # 24 tests
OSC_LIB_REPLAY=1 PATH=~/.cargo/bin:$PATH python3 -m unittest test_champion_library
PATH=~/.cargo/bin:$PATH python3 controls.py                                 # 8 controls, each observed rejecting
PATH=~/.cargo/bin:$PATH python3 verify_identity.py                          # 21/21 reproduce
```

`load_library` fails **closed**: any mismatch of a per-file `content_sha256`, the index's copy of
it, `library_sha256`, the file set, the declared count, the schema, an enumerated value, a
required provenance field or a completeness claim raises `IntegrityError` and returns nothing.

## Rebuild

```
PATH=~/.cargo/bin:$PATH python3 run_panel.py --workdir <scratch>
python3 build_subject_library.py --games <scratch>/games/games.jsonl.gz
python3 build_pages.py
```

`panel-config.json` names its sources by repo-relative path plus an immutable `source_git` pin;
it is a **record** and `fuzz_panel` will refuse it in place rather than pick up a stray file.
`run_panel.py` materialises the pinned blobs and re-checks their digests before compiling.
