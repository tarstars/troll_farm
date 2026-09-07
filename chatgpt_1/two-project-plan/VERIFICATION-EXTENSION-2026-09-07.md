# Extension verification and integration record

2026-09-07; chatgpt_1; task 20260907-two-project-analysis-and-plan, extension E1–E7. This record is about checks actually performed in this session. It does not inherit coordinator acceptance of the original packet.

## Deliverable status

| Extension | Artifact | Status |
|---|---|---|
| E1 | RECHECK-2026-09-07.md | Primary-source re-check delivered; three copied-file identities checked, not an all-document hash audit |
| E2 | PHASE0-AUDIT-2026-09-07.md | Requested controller families and nine properties classified with direct-code / primary-review / historical-evidence labels; generic hypothesis duplicate; unresolved cells remain explicit |
| E3 | LINEAGE-DIFF-2026-09-07.md | Structural source comparison delivered; no full local normalized-diff execution claimed |
| E4 | SCOREBOARD-v2.md and dated-neighbour.csv | Every previously enumerated neighbour rollout now dated; 65 displayed rollout assertions plus one later poll; older exhaustive archive coverage not certified |
| E5 | TOOLING-2026-09-07.md | Executable capability gaps audited; **use SOURCE-CORRECTIONS-2026-09-07.md for the corrected source hashes** |
| E6 | CANDIDATE-CENSUS-2026-09-07.md and generated index | **Bounded/partial:** 630-label index, 189 unresolved; not an exhaustive unique-build census |
| E7 | PLAN-2026-09-07-v2.md and OWNER-PAGE-v2.md | Revised conditional plan and three owner decisions delivered: UNIFY / TRACE / HOLD |

All new report files are under chatgpt_1/two-project-plan/. The earlier 08:13 packet remains unchanged. The source-corrections note records my three digest transcription errors and one unverified directory name rather than hiding them.

## Evidence pins and execution limits

M: tarstars/troll_farm at 67b2acc1e828cf25a7e6e76c2814dfcd3268a45c.
N: tarstars/separate_troll_farm at badf27efee7eca794c149f0707c087f7ed1eb0ff.
W: M's neighbour/separate_troll_farm/working-storage/ snapshot.

The connected GitHub reader supplied source and primary evidence. Direct local cloning/downloading did not provide usable complete checkouts. No full-source execution, bot compilation, panel, new game, platform/ladder/cluster action, holdout opening or private-key read occurred. W:COPY-RULE.txt says much raw TSV/log/readable-source data was pruned; a primary review's reported execution is not my own fresh reproduction.

## Executed checks

1. `python3 extension_audit.py --self-test` passes **8/8**. These are audit-helper tests: index coverage/aliases, standard-deviation arithmetic, win/draw/loss accounting, official-rank outcome mapping, request chunk budgets, rejection of incomplete/fetch-success maturity records, lexical source normalization and UTF-16/blob handling. They are not bot tests.
2. Two fresh `--out` runs produce byte-identical extension-metrics.json and candidate-index.csv, also byte-identical to the original local outputs. No random sampling or online call occurs.
3. Reusing an output directory containing the existing audit exits **2** with an explicit refusal. A missing main/neighbour checkout also exits **2**, and no completed metrics file is written. The optional source-root audit therefore does not silently claim verification when inputs are absent. Use a fresh output directory for all modes.
4. The manually transcribed dated-neighbour.csv has **32 rows and 32 unique submission IDs**; every timestamp parses with an explicit UTC zone. Remote source comparison was by direct inspection of the retained raw rows, not bulk local extraction. The older V2 schema is explicitly weaker than the 31 modern count assertions.
5. The published script and CSV were re-fetched through GitHub. Their whole-file blob IDs exactly equal the locally computed IDs below; the remotely published script is the tested script byte for byte.
6. GitHub compare from the prior handoff commit c805abd304ec27bd6353b0084242236cc8a75f7e to e87807e283a271f15c144c3dca5349c423a25b9a reports **12 commits ahead, zero behind**, with twelve added files, all in chatgpt_1/two-project-plan/. No original report, bot, neighbour source, board or task file changed. This verification file and the final handoff are subsequent additions.
7. The latest coordinator-message commit was re-read before handoff and remained 6484f3c67c0be18e7aa93ba9e54d29e47058c625, the 08:38 extension charter. This is a targeted inbox read, **not** an executed canonical inbox sweep or outbox lint.

## Tested-file identities

| File | Bytes | SHA-256 | Git blob ID |
|---|---:|---|---|
| extension_audit.py | 18,337 | ed007f78feec0c54d8930322b04b86dc65b8179eedfa5b3c200e1c15fb17ae45 | 3df48c1190b2e2ca4f7435735d56d50510dec80f |
| dated-neighbour.csv | 4,962 | 6002ec40f5163f384d2a2ba6e68a669b47057938b10cf963b8ee990a795a0578 | 2cf29156e55606b8da3c4fd451cc36c4f692c7bb |
| extension-metrics.json | 1,835 | 22b0aaddc8d5175db5664b6b57f51759a8bf89289555da4f6c8dbd8e29ce20f2 | 781f29096806ba34b7300f8e3f2a378fb89f31d0 |
| generated candidate-index.csv | 46,713 | 200f5375366ca7259d7436f70b0c458e929584c322345a60a262d9682a515c14 | f1e7cfc343a2deb23ec3f146a05d08ecc0a6ff57 |

The large generated index is reproducible from the committed script; it is not a claim of 630 distinct tested artifacts. Source inventory flags remain false and unique_completed_build_count remains null. The quoted Git blob IDs refer to file contents, not executable or compact deployment hashes.

## Reproduction

From the integrated repository:

```sh
python3 chatgpt_1/two-project-plan/extension_audit.py --self-test
python3 chatgpt_1/two-project-plan/extension_audit.py --out /path/to/a-new-audit-directory
```

The optional read-only tracked-object audit, **not executed here**, additionally needs both exact source pins available in local Git object stores:

```sh
python3 chatgpt_1/two-project-plan/extension_audit.py \
  --main-root /path/to/troll_farm \
  --neighbour-root /path/to/separate_troll_farm \
  --out /path/to/another-new-audit-directory
```

It produces source-path matches for every numeric label, copied-Markdown hash comparisons, recognized complete-count ledger records, a list of unfamiliar ledger schemas and a lexical source diff. Those outputs still require semantic review and raw-archive checks; filenames and lexical equality do not certify strategy, distinct builds or real-game parity.

## Transport and integration

The initial extension ACK write was blocked by the tool's safety validation and was not retried. It was not published. No canonical inbox-clean or outbox-lint result is claimed. The final handoff is a separate delivery of this report and pins an already fetchable artifact commit.

Coordinator action: **MERGE this agent branch**, not cherry-pick the report away from its message ancestry; reproduce the arithmetic and source checks, record the incomplete E6 tail explicitly, and update the board. No main merge or acceptance of this extension is claimed by its author.

The operational recommendation is narrower than the original packet: hold V439, resolve account authority, trace the actual missing-supply event, and require an executable resumed/failure-accounted evaluation path before a new finalist. No future activity has been scheduled by this chat.
