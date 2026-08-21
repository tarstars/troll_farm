# ⚠ STALE — this is NOT the authoritative oscillation library

**Do not read a case out of this directory.** It is the **parent lineage** library, kept only
because immutable messages and dated reports from 2026-08-10/11 cite these paths. The IDs in here
are **not** the IDs the investigation, the graders, the task cards and the rulings use.

- **Authoritative library:** `claude_1/banana-restoration-r2/oscillation-library-98628e98/library/`
  (34 cases, subject `98628e98…` — the resident readable-no-orchard bot). Every tool on this
  branch already loads it: `oscillation_library.SUBJECT_DIR`, `claude_1/t1/fixture_harness.py`
  (`LIB`), `claude_1/viewer/build_viewer.py` (`LIB_DIR`). Verified by grep across every `.py`,
  `.rs`, `.sh`, `.toml` and `.json` on `agent/claude_1`: the only code reference to this directory
  is `oscillation_library.PARENT_LINEAGE_DIR`, which names it "retained for comparison only" and
  is **read by nothing** — `DEFAULT_DIR` is `SUBJECT_DIR`. The harm is therefore a **human or
  agent reading by path**, which is exactly what happened on 2026-08-21
  (`local_claude_1/adjudications/4b-bucket-B-ruling-2026-08-21.md`).
- **This directory:** 33 cases, subject
  `a8eb3b2b…` = `cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`,
  corpus `c3-train-engine-authority-2026-08-09`. A **different bot on different games**, not a
  renumbering of the same corpus.

## The ID map — only 14 of 33 IDs mean the same thing in both

Matched on the game `(map_id, seed, seat)` and then on the window's `(turn_start, turn_end,
cells)`. "same ID, same window/cells" means reading that ID here gets you the same case as the
frozen library; everything else does not.

| this (STALE) ID | its window | what it is in the authoritative library |
|---|---|---|
| `OSC-001` | 6–200 | same ID, same window/cells |
| `OSC-002` | 12–200 | same ID, same window/cells |
| `OSC-003` | 2–36 | same game as frozen OSC-009, OSC-028, different window/cells |
| `OSC-004` | 7–18 | **= frozen OSC-005** |
| `OSC-005` | 9–20 | same game as frozen OSC-004, different window/cells |
| `OSC-006` | 29–39 | **no counterpart in the frozen library at all** |
| `OSC-007` | 12–20 | same game as frozen OSC-025, different window/cells |
| `OSC-008` | 9–17 | **no counterpart in the frozen library at all** |
| `OSC-009` | 12–18 | same game as frozen OSC-006, different window/cells |
| `OSC-010` | 80–86 | same ID, same window/cells |
| `OSC-011` | 8–14 | same game as frozen OSC-007, different window/cells |
| `OSC-012` | 8–200 | same ID, same window/cells |
| `OSC-013` | 14–200 | same ID, same window/cells |
| `OSC-014` | 33–197 | same game as frozen OSC-014, different window/cells |
| `OSC-015` | 44–200 | same ID, same window/cells |
| `OSC-016` | 7–200 | same ID, same window/cells |
| `OSC-017` | 7–200 | same ID, same window/cells |
| `OSC-018` | 10–200 | same ID, same window/cells |
| `OSC-019` | 23–200 | same ID, same window/cells |
| `OSC-020` | 29–200 | same ID, same window/cells |
| `OSC-021` | 32–200 | same ID, same window/cells |
| `OSC-022` | 106–200 | same ID, same window/cells |
| `OSC-023` | 27–100 | same ID, same window/cells |
| `OSC-024` | 5–67 | same game as frozen OSC-024, different window/cells |
| `OSC-025` | 17–23 | same game as frozen OSC-026, different window/cells |
| `OSC-026` | 3–24 | **= frozen OSC-027** |
| `OSC-027` | 24–31 | **= frozen OSC-030** |
| `OSC-028` | 11–200 | **= frozen OSC-031** |
| `OSC-029` | 91–200 | **= frozen OSC-032** |
| `OSC-030` | 58–200 | **= frozen OSC-033** |
| `OSC-031` | 61–200 | **no counterpart in the frozen library at all** |
| `OSC-032` | 6–99 | **= frozen OSC-034** |
| `OSC-033` | 61–68 | **no counterpart in the frozen library at all** |

**14/33 agree. 19 do not**, and six of those are silent renumberings that give you a real case
under the wrong name — including the two the current cause-attribution task is about:

- this `OSC-029` (turns 91–200) is the frozen **OSC-032**; this `OSC-030` (58–200) is the frozen
  **OSC-033**. So this directory's own `OSC-032` (turns 6–99) is a *different game entirely*, and
  it has no `OSC-034`.
- four cases here (`OSC-006`, `OSC-008`, `OSC-031`, `OSC-033`) have **no counterpart at all** in
  the authoritative library. `OSC-033` here does not even carry a `provenance.map_id`.

## The builder's `--out` default aims here — a trap that is detected, not prevented

`../build_oscillation_library.py` defaults `--out` to **this directory**
(`build_oscillation_library.py:808`). Both other arguments are required, so a bare invocation is
impossible; but a run that supplies `--games`/`--panel-config` and *omits* `--out` would rewrite
this tree. `write_library` unlinks `*.json` only, so **this README would survive and be left
describing 33 cases that are no longer here** — a false document at the exact path the marker
exists to protect.

The default is **not** changed, and this is deliberate: `build_oscillation_library.py` is pinned
by SHA-256 `4b9fce4c…` in `oscillation-library-2026-08-10.md` and
`oscillation-library-subject-correction-2026-08-11.md`, and the authoritative
`oscillation-library-98628e98/` tree rests its provenance on that builder being **unmodified**.
Editing it to close the trap would falsify an attestation two accepted artifacts depend on. That
is a worse defect than the hazard.

So the hazard is **detected instead**, by three tests in
`test_oscillation_library.TestParentLineageIsLabelled`: the pinned `library_sha256`
(`5858d351…`), the index's `WRONG SUBJECT` note (which a rebuild drops entirely), and the ID map
below, which is checked against the files actually present. Verified 2026-08-21 by executing a
simulated default run into a throwaway copy: the untouched copy passes all three, the overwritten
copy fails all three, and deleting the README alone fails exactly the third. Use
`--out` explicitly, always.

## Why it was kept rather than deleted

Deleting it would leave dangling paths in immutable v2 messages
(`20260810T133000Z-…-m3a-oscillation-library-handoff.md`,
`20260811T193000Z-…-m3a-correct-subject-handoff.md` and others) and in dated reports that are part
of the record. A loud README at the root fixes the actual failure mode — reading by path — without
rewriting history. The subject error itself is written up in
`claude_1/banana-restoration-r2/oscillation-library-subject-correction-2026-08-11.md`.

Card: `coordination/messages/local_claude_1/20260821T082315Z-20260815-oscillation-deep-dive-policy.md`.
Written by claude_1, 2026-08-21. The table above is generated from the two libraries' own records,
not transcribed.
