# Arena submission history — provenance coverage report

Task `20260802-arena-submission-history-registry`. Compiled 2026-08-02 by `claude_1` from
tracked files only (`git ls-files`, `git grep`); no platform call, no sealed range, no scan
outside the repository. Registry: `data/analysis/arena-submission-history.json`, generated
from `data/analysis/arena-submission-history-inputs.json`.

**Covered:** 9 source families, 17 deployment records, 35 observations, 5 explicit
unresolved items.

## 1. Included — structured (Tier A)

24 observations are parsed directly out of `schema: 1` submission-scoped checkpoint JSONs
under `data/analysis/live-agent-6553250/`. Each is pinned in the manifest by SHA-256, and
the builder additionally requires the agent and submission ids *inside* the file to match
what the manifest declares. Nothing about these is transcribed by hand.

One cross-check worth recording: the manifest hash for
`owner-far-denial-no-return-terminal-checkpoint-2026-07-31.json`,
`c6937bab4c314b1c907cb89d7f09d669b066076e3ce9890561ccb39a5ccb2de6`, is the same value the
2026-07-31 execution report states independently. The two agree.

## 2. Included — curated from prose (Tier B)

11 observations exist only in immutable Markdown. Each carries `evidence_path`,
`evidence_sha256` and a verbatim quote.

| observation | fact | evidence |
|---|---|---|
| `obs-6557204-prereset` | agent 6557204 at 24.4, rank 23/104 | `compact-gold-rollout-arena-verdict-2026-07-18.md` |
| `obs-41009795-games125` | 125 games @ 23.6 | same |
| `obs-41009795-games142` | 142 games @ 24.1 | same |
| `obs-41009911-games120` | 120 games @ 21.7 | same |
| `obs-41070584-games20` | 20 games @ 18.22 | `owner-far-denial-no-return-arena-execution-2026-07-31.md` |
| `obs-41070584-games95` | 95 games @ 20.14 | same |
| `obs-41071360-mature265` | 265/265 @ 16.37, rank 109/130 | `owner-best-far-denial-restore-execution-2026-08-02.md` |
| `obs-41079354-public-t11a/b`, `-t21` | 16.55 / 17.10 / 18.43 | `coordination/messages/claude_1/20260802T060700Z-…-progress.md` |
| `obs-41079354-public-t40` | 19.37, rank 73/130 | `coordination/messages/claude_1/20260802T072000Z-…-evidence-transcription.md` |

### The one maturity override

`obs-6557204-prereset` (24.4) has no recorded game count. The rule would make it
`provisional`; the manifest overrides it to `mature` because the 2026-07-18 verdict treats
it as the settled pre-reset resident row and uses it as the capacity gate reference. The
projection records `maturity_source: "manifest_override"`, and because its sample size is
unknown the observation is still **excluded from every aggregate** — it appears in
`preflight` as an explicitly labelled `EXCLUDED` line. Nothing else in the registry is
overridden.

### The 19.37 read — quality note

This is the weakest included fact and it concerns the currently live agent. It is an
unauthenticated public-leaderboard read at about T0+40 min whose only surviving record was
a *replaceable* status snapshot; it was transcribed into an immutable message so the
registry could pin a stable hash. It has no game count, no catastrophe count, no identity
audit, and no preserved response hash. The registry classifies it `provisional` and the
schema forbids any public-leaderboard read from reaching mature class.

**It is therefore not the "19.37/160 mature repeat" that acceptance criterion 4 describes.**
No 160-game audit of agent 6589510 exists. This deviation from the task record was raised
with the record owner in `20260802T065200Z-…-progress.md` before implementation and is
restated in the handoff.

## 3. Ambiguous — included with a stated confidence level

Every submission carries `source_attribution_confidence`:

- `hash_verified_in_report` (15 of 17): the execution report or upload manifest states the
  exact SHA-256 that was submitted, and that hash still matches the in-repo file today
  (`test_every_source_file_still_hashes_to_its_recorded_value`).
- `asserted_by_report` (1): agent 6557204 — the report names the agent and calls it the
  pre-reset resident, but does not print a hash for that specific deployment.
- The remaining record (`41009991`) is hash-verified but has **no score observation at all**;
  it exists so the replacement chain is unbroken.

The derivation chain `preseed → far-denial → tent-proximity → tent-banker → onsite →
funding-first` is recorded as explicit `derived_from_source_id` fields. It is corroborated
by, but not taken from, the `candidate-agent<parent-agent>-…` filename convention.

## 4. Unrecoverable or out of scope — explicitly not covered

1. **The submission id for agent 6557204.** Only the agent id and score were written down.
2. **Deployment timestamps for 11 of 17 submissions.** The reports record checkpoint times,
   not submit-call times. Where a submit log survives (`41079354`) or the report prints a
   clock time (`41009795`, `41009911`, `41009991`), the timestamp is present.
3. **A submission-scoped maturity audit of the live agent 6589510 / 41079354.** Only a
   9-game initial health checkpoint exists. This is the largest gap in the registry and it
   concerns the live leg — see the recommendation below.
4. **Battle-level detail for every `arena_room` and `public_leaderboard` observation.**
   Those endpoints do not expose it, and the battle streams of replaced submissions are gone.
5. **Any Arena deployment before 2026-07-16.** Outside the restored-resident era. The
   Bronze-to-Gold and early-Legend records live in prose under `docs/archive/`; extending
   the manifest is the supported way to add them if a comparison ever needs them.

Items 1–5 are also machine-readable in the manifest's `unresolved` block and are printed by
every `preflight` run.

## 5. What the registry says about the incident that prompted it

`preflight` on the far-denial source, all history, no filter:

| source family | mature runs | median | worst | best | latest |
|---|---:|---:|---:|---:|---:|
| `opponent-crop-b100-e6-slim` | 1 | 24.89 | 24.89 | 24.89 | 24.89 |
| `preseed-orchard-coverage-slim` | 4 | 24.19 | 23.05 | 24.77 | 23.05 |
| `owner-far-denial-no-return-d3-slim` | 1 | 22.99 | 22.99 | 22.99 | 19.37 |

The preseed resident's four mature runs are 24.1/142, 24.77/160, 24.28/160 and 23.05/171,
plus the excluded 24.4. Far-denial has one mature run and fires `SINGLE_MATURE_RUN` and
`LATEST_BELOW_MEDIAN`.

Two further findings the incident report did not contain:

- **`opponent-crop-b100-e6-slim` scores highest in the whole registry (24.89/160) and was
  rejected.** Its protocol rejected it because it was only +0.12 over a *matched* control,
  not because it scored badly. A registry that ranked on score alone would recommend it.
  The `REJECTED_SOURCE` warning and the dispositions column exist for exactly this row.
- **The funding-first agent read 16.97 at 11 games and 16.37 at 265.** `docs/STATE.md`
  described the 11-game read as "clean positive first health". The gap is only −0.60, but
  it is *downward*, against the standing assumption that fresh reads sit 3–4 points below
  matured ones. One data point proves nothing; it does show that cold reads are not
  reliably pessimistic, which is why the minimum-finished gate is a hard filter rather than
  an adjustment.

## 6. Recommendation to the Arena controller

Run a submission-scoped maturity audit of agent 6589510 / submission 41079354 and add the
resulting checkpoint to the manifest. Until then the live leg's best evidence is nine games,
its own source family has a single mature run, and the registry cannot say whether the
restore is performing at 22.99 or at 19.37. That is a decision the project cannot currently
make from evidence, and no query here will pretend otherwise.
