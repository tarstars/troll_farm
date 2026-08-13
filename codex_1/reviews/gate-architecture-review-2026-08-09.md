# Independent acceptance-gate architecture review

- Reviewer: `codex_1`
- Task: `20260807-gate-architecture-review`
- Artifact under review: `claude_1/pipeline/design-gate-redesign-2026-08-07.md`
- Pinned author commit: `3ca092abba353b4dd07b63e85f6d25deb9852d0d`
- Verdict: **REVISION_REQUIRED**

## Scope and binding rule

This is an architecture review only. I made no detector, panel, configuration, candidate,
workflow, frozen-artifact, or Arena change.

I treat the owner's standing rule as axiomatic: raw D-1 and D-4 must each be zero on the
pinned 120-map x 2-seat x 200-turn panel, without inherited-parent or aligned-prefix
exemption. D-5 through D-9 remain active blockers. I do not recommend weakening or
reclassifying that rule.

## Verdict

**REVISION_REQUIRED.** The proposal contains useful provenance and coverage ideas, but its
operative acceptance rule conflicts with the standing strict rule and its load-bearing D-9
classification uses the wrong aggregation unit. The two-sided acceptance criterion is not
currently achievable with the unmodified parent. Section 4.6 also cannot guarantee "no new
failure" from per-map counts alone.

## Findings

### F1 — Section 4.4 is auditable exemption, not a different acceptance semantics

The proposed ledger is materially better than runtime parent comparison for provenance:
it is finite, inspectable, hash-pinned, and ratified. That is a real governance difference.
It is not a meaningful semantic difference in the verdict: both mechanisms allow a
candidate episode that would otherwise block because the parent lineage is known to exhibit
it. Moving the exemption from a runtime comparison into a manifest changes visibility, not
what the gate accepts.

This distinction is decisive under the task's binding rule:

- D-1 and D-4 may not be Tier B, waived, delta-gated, or otherwise compared with the
  parent's nonzero floor. They must be raw-zero blockers.
- Classifying D-9 as report-only Q also deactivates a standing D-5..D-9 blocker. That is
  incompatible with the task record unless the owner separately changes the rule; this
  review cannot do so.

Therefore the current classifications in sections 4.3 and 4.6 cannot be ratified even if
the ledger mechanism is retained for detectors outside the strict rule.

### F2 — Section 4.6's `delta <= 0` is not a no-new-failure rule

For candidate count `C_m` and floor count `F_m` on map/seat cell `m`, `C_m-F_m <= 0`
allows a candidate to replace a known floor episode with a different episode on the same
cell while keeping or reducing the count. Per-map aggregation prevents cross-map trade, but
not within-map signature substitution. The prose in section 7 that says `<= 0` permits a
fix on map Y to offset a new failure on map X is itself inconsistent with a genuinely
per-map predicate; the real remaining hole is within-map substitution.

Strict numeric `delta = 0` is not the fix: it rejects removal of a parent defect because a
negative delta is not zero. If the intended policy is "repairs allowed, no new episode,"
the architecture needs a signature-set rule such as candidate episode signatures being a
subset of the ratified floor signatures, plus an explicit definition of signature identity.
For D-1 and D-4, the binding rule is simpler: candidate raw count must equal zero.

### F3 — Section 8 criterion 3 is impossible for the current unmodified parent

The independently committed floor result has verdict BLOCK in 118/240 side-games, with
D-1 = 35 and D-4 = 6 total episodes. Those facts are established by the task and reproduced
from the committed JSON below. Since the owner requires raw zero without parent exemption,
the current unmodified parent cannot be accepted by a compliant gate.

The achievable two-sided condition is therefore:

1. BLOCK a deliberately broken candidate; and
2. ACCEPT a **repaired reference lineage** that first satisfies raw D-1 = 0, raw D-4 = 0,
   and all other standing blockers.

"ACCEPT the unmodified parent" cannot remain a present acceptance criterion. It can be an
explicitly expected-failing diagnostic until the parent is repaired. The architecture
cannot earn `ARCHITECTURE_ACCEPTED` from criterion 3 today.

### F4 — D-9's 74 versus 196 discrepancy is records versus episodes

The three calibrated Markdown reports each contain 74 side-game D-9 records. Summing each
record's declared `count` field yields:

| run | side-games with D-9 | total D-9 episodes |
|---|---:|---:|
| floor | 74 | 196 |
| `bbe54a48` | 74 | 196 |
| `7ad9d784` tip | 74 | 176 |

Thus "D-9 fires exactly 74 times in all three runs" is true only if "times" means affected
side-games. The proposal's table labels its values as detector `floor`/candidate counts and
the surrounding architecture repeatedly reasons in episodes. On the declared episode unit,
D-9 does **not** have zero variance and does not automatically qualify for Q. The
coordinator's 196 is the floor episode total and agrees with the report sum; it is not a
different calibration stage.

This does not prove that D-9 is informative. It proves only that section 5's zero-information
argument is unsupported by the stated statistic. The D-9 affordability semantics and tier
assignment remain referred to `local_codex_1`; I do not decide them.

### F5 — interactions with referred questions

- The affordability change in section 5 might produce a grounded D-9 predicate, but this
  review neither approves nor rejects it. F4 means it cannot be justified by constant
  episode count as currently written.
- D-2, D-3, and D-8 have zero observed episodes in the floor run. The proposed U label is
  honest, but the 240-game panel supplies no empirical acceptance evidence for those
  detectors. Whether that panel is sufficient is reserved to `local_codex_1`.
- The proposal says tier is recomputed from the FST each run, yet candidate variance cannot
  be computed from a parent-versus-parent FST alone. A successor design must pin the
  calibration population and aggregation unit or defer tier assignment to the referred
  semantics review. I report this interaction without assigning I-16..I-18 tiers.

## Explicit compatibility statement

The following proposal elements are incompatible with the owner's standing strict rule:

1. Tier-B treatment, floor delta, or waiver-ledger entries for D-1 or D-4.
2. Any criterion requiring acceptance of the current unmodified parent while it has raw
   D-1/D-4 episodes.
3. Report-only quarantine of D-9 while D-9 remains a standing active blocker.

The FST, manifest provenance, HARNESS DRIFT outcome, honest U/UNPROVEN reporting, and bite-test
concept are not inherently incompatible with the strict rule.

## Reproducible evidence

Run from any checkout containing the cited Git objects.

### Input hashes

```text
design proposal
3fa4cb77e588ea6bd874f559368f1805f52dafe88251e259d6db47bc3e714743
floor calibrated report
25a934d3944f463aef2be4221e25dea338e6475713de9f97859b546c5760dbd3
bbe54a48 calibrated report
8b98935de9c6fd52a3a688e88d3788a22784370668123b293a2d5b32728ad6d4
tip calibrated report
1eff4bbe796d5c85fa84576bd79976376dd0a52a434806d4440533ac76fae9da
coordinator floor JSON
322895ee57ae9305a500d1238e998ad3bcd44c4c5e2e36c6929d1e1664c66380
coordinator floor README
888c6f438e17296d8398eb4c09ab6369f0726a039b37948e522719ce1f3b058e
fuzz_panel.py at pinned author commit
cc7db6f2f048a1739e587cff9e26e5783d08f69672e233b227a6294f03b6571d
fuzz-panel-config.json at pinned author commit
f5394e7a8b974062b07f42bc535e113dca2e9d67b64c9b196c1a4b63660b99fe
authoritative corrected task record
84334cd303a30baedb085d85ce0429aaec2d24e343307371d20a71535251242a
```

Hash command pattern:

```bash
git show <commit-or-ref>:<path> | sha256sum
```

### D-9 aggregation command

Run once for each of the three filenames below:

```bash
git show 3ca092abba353b4dd07b63e85f6d25deb9852d0d:claude_1/pipeline/verification/fable-verify-floor-calibrated.md |
python3 -c 'import re,sys; s=sys.stdin.read(); xs=[int(x) for x in re.findall(r"\*\*P1\*\*: \{\"count\": (\d+), \"detector\": \"D-9\"",s)]; print(len(xs),sum(xs),sorted(set(xs)))'
```

Replace the filename with `fable-verify-bbe54a48-calibrated.md` and
`fable-verify-7ad9d784-calibrated.md`. Observed output:

```text
74 196 [2, 4]
74 196 [2, 4]
74 176 [1, 2, 3, 4]
```

### Independent floor totals command

```bash
git show origin/main:local_claude_1/verification/local_claude_1-floor-selftest-result-2026-08-07.json |
python3 -c 'import json,sys,collections; x=json.load(sys.stdin); c=collections.Counter(); [c.update(g["detector_counts"]) for g in x["games"]]; print(x["verdict"],x["stats"]["blocking_games"],x["stats"]["games"],dict(sorted(c.items())))'
```

Observed material fields: `BLOCK 118 240`, D-1 `35`, D-4 `6`, D-9 `196`, and D-2/D-3/D-8
all `0`.

## Required revision before re-review

1. Make D-1/D-4 raw-zero absolute blockers throughout; remove their Tier-B/waiver path.
2. Reconcile D-9 using an explicit aggregation unit and do not infer Q from constant 74
   affected side-games.
3. Replace count-only per-map delta with a rule that cannot hide within-map episode
   substitution, or state the weaker claim honestly.
4. Rewrite criterion 3 around a repaired compliant reference; retain the current parent as
   an expected-failing diagnostic until repair.
5. Specify the pinned data needed to compute variance-driven tiers; the FST alone cannot do it.

