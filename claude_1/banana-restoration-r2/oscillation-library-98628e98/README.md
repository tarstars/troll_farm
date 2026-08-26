# Oscillation situation library — the M3a subject `readable__no_orchard`

**This tree is the M3a deliverable.** The sibling tree `../oscillation-library/`
is **not**: it was harvested from the parent program and is retained, labelled,
only as a parent-lineage comparison.

| | |
|---|---|
| subject | `readable__no_orchard` = `cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs` |
| subject SHA-256 | `98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29` |
| read as | `git show origin/main:cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs` |
| judged against | **itself** — `run_identity: floor`, candidate bytes == parent bytes, machine-checked by `fuzz_panel._check_run_identity` |
| instrument / corpus | `fuzz-panel/5-two-player-phase-merged-referee` / `c5-two-player-phase-merged-2026-08-11` |
| situations / episodes | **34 / 46** (38 D-1 + 8 P4-only), all `FULL` |
| `library_sha256` | `1370384da9cad46e4f60617b2c9edd076de6ffd9f26d30d0066528de414f9174` |

## Contents

- `library/` — 34 frozen situations (`OSC-001.json` … `OSC-034.json`) plus
  `index.json`. Each situation is literal data copied verbatim out of a referee
  transcript — map rows, plants, units of both players, inventories, and the
  per-turn command line for every turn of the window — so no call back into the
  map generator is needed to replay it, and a generator change cannot silently
  move it.
- `panel-config.json` — the exact floor config used, SHA-256
  `eca5cb32e8fc5daa61dd69d0753f9a3962eff5cbce10cf12e8410ba36c903fe5`.
- `build_subject_library.py` — the driver. It imports and calls
  `../build_oscillation_library.py` **unmodified**: the harvest, classifier,
  idleness criterion, dedupe key, freezing discipline and integrity hashing are
  the previously accepted code. The driver only pins the subject, corrects the
  provenance note, and excludes the one `REAL_CORPUS` record (which came from a
  third program, `f26e3781…`).

## Scope — M3a only

M3a enumerates and freezes. **No best action, preferred action, ranking,
recommendation, verdict, fix or remedy is recorded anywhere in this library.**
That judgement is M3b, is blocked on the Decision Packet, and must be reached
independently of the scorer that produced these situations — deriving it here
would poison M3b with exactly the circularity it exists to avoid. The silence is
enforced by `TestSubjectNoBestActionRecorded`, which walks every key and every
string of every frozen file against forbidden lists.

## Use

```
cd ..
python3 oscillation_library.py --dir oscillation-library-98628e98/library
python3 -m unittest test_oscillation_library                       # 88 tests, stdlib only
OSC_LIB_REPLAY=1 PATH=~/.cargo/bin:$PATH python3 -m unittest test_oscillation_library
```

`load_library` fails **closed**: any mismatch of a per-file `content_sha256`,
the index's copy of it, `library_sha256`, the file set, the declared count, the
schema, an enumerated value, a required provenance field or a completeness claim
raises `IntegrityError` and returns nothing. There is no partially-verified
load.

## Rebuild

```
PATH=~/.cargo/bin:$PATH python3 ../../pipeline/fuzz_panel.py \
  --config panel-config.json --report /tmp/r.md --json /tmp/p.json
python3 build_subject_library.py --games <games_dir>/games.jsonl.gz
```

Full method, measurements and the three-way reconciliation with `chatgpt_1`:
`../oscillation-library-subject-correction-2026-08-11.md`.

## Provenance note added 2026-08-21 (card `20260821-champion-subject-library`, control C-1)

The `panel-config.json` **in this directory today** hashes to
`49bb35516b0b3a43781253cf1f9ac7be7c3da772d8871ffe60740cd183b0cbbd`, not to the
`eca5cb32e8fc5daa61dd69d0753f9a3962eff5cbce10cf12e8410ba36c903fe5` quoted in the table above and
recorded inside every frozen situation. That is not drift in the library: the config was edited on
2026-08-12 by the source-portability repair (commit `07cb2bd7`), **after** this library was
accepted on 2026-08-11. The config as frozen is `d9d041bb:…/panel-config.json`.

Measured, not assumed: rebuilding all 34 situations from the current config reproduces every
window, world state, command line, classification, detector count and index histogram
**byte-identically**; the only differing fields anywhere are `provenance.panel_config_sha256` and
the `content_sha256` that covers it, and restoring the frozen digest reproduces all 34
`content_sha256` values exactly. Evidence:
`../oscillation-library-547fa706/controls-2026-08-21.json`, checks C-1a / C-1b / C-1c.

**Whose episodes these are:** `readable__no_orchard` (`98628e98…`), which is no longer the
champion. The champion of record's own exhibits are in `../oscillation-library-547fa706/`.
