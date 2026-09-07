# Verification and integration record

Task `20260907-two-project-analysis-and-plan`, author chatgpt_1, 2026-09-07. This record distinguishes checks actually run in this session from checks requested of the coordinator.

## Packet

Start with [OWNER-PAGE.md](OWNER-PAGE.md). The substantive deliverables are [ANALYSIS-2026-09-07.md](ANALYSIS-2026-09-07.md), [PLAN-2026-09-07.md](PLAN-2026-09-07.md), [SCOREBOARD.md](SCOREBOARD.md), and the alternative-specific costs/falsifiers in [DECISION-MATRIX.md](DECISION-MATRIX.md). [audit.py](audit.py) reproduces the stated arithmetic and optionally validates the main final-reading transcription.

Evidence source pin: `fb7801a740c8c16eca7e3e22cb2c008fd9e58b17`. Neighbour evidence is the copied working tree under `neighbour/separate_troll_farm/`, not a separately accessible remote and not limited to its older HEAD date. No game, source-policy build, panel, cluster job, platform operation, seal open or key read was performed.

## Executed checks

1. `python3 audit.py --self-test`: **6/6 PASS**. Tests cover final-record uniqueness/counts, five-reading arithmetic, independent SD calculation, minimum sample-size calculations, rejection of duplicate/incomplete final records, exclusion of early polls from sample count, game-budget arithmetic and invalid arguments.
2. `python3 audit.py`: successful deterministic JSON output. The source-verification status is explicitly **NOT_RUN** without a pinned checkout. Principal outputs: recent champion mean **18.264**, sample SD **0.8154937154877409**, range **2.19**; normal-approximation six-per-arm half-width **0.9228180** and 21-per-arm half-width **0.4932670**. Older-SD sensitivity requires **18/70** per arm for one/half-point half-width, versus **6/21** under the recent SD. These are sensitivity calculations, not empirical ladder confidence guarantees.
3. The optional source-root path was deliberately pointed at a missing checkout. It exited **2** with `SOURCE AUDIT FAILED`, rather than claiming verification from the manually transcribed inputs.
4. The tested local script and the remotely published script have identical length **10,128 bytes** and identical Git blob **f48d1504e28852f5ed8a5eb5234f4cd5843427e4**. SHA-256 of the tested script: **73e194494f7e034b1d7e52f1c7e6f031daf25ca587739312f85e3c044c459964**.
5. GitHub's published directory read at artifact ancestor `17920ec713952dae7de3d4f17a20d148c8904285` resolved the analysis, plan, owner page, corrected scoreboard and script. The decision matrix was published subsequently at `d8b33c5637f93f9fd751cb5d7b72a44a9dd55548`.
6. GitHub compare from starting agent-branch commit `bb9771bbc58690b02ba0f31be8b6423c5a4d82a3` through `d8b33c5637f93f9fd751cb5d7b72a44a9dd55548` reports nine commits, no divergence, and changes only to the six packet files plus my ACK/progress messages. This verification file and the final handoff are additional own-namespace/documentation changes. No bot or neighbour source was changed.

The combined scoreboard count is a document inventory: **15 L + 16 J + 33 N = 64 completed-reading assertions**, plus one non-independent later poll. It is not 64 exchangeable measurements. The historical incomplete V1/V542 and prematurely replaced main candidates remain excluded, and 161/162-game exceptions are explicitly retained as exceptions.

## Reproduction commands after integration

```sh
python3 chatgpt_1/two-project-plan/audit.py --self-test
python3 chatgpt_1/two-project-plan/audit.py
python3 chatgpt_1/two-project-plan/audit.py --source-root /path/to/source-checkout
```

The third command requires the original `local_claude_1/ladder-queue/readings.jsonl` blob **2909dab7526e157f2cbb1f2d9ae04cc2c09c70f0** at the evidence pin. The script checks that blob, all 16 final submission/rating/rank triples, and the exact five-source-hash champion group. It flags the historical 162-game row. It does not open any holdout, fetch any network data, run any bot, or verify raw game maturity.

## Not independently verified here

The entire old main and neighbour raw battle archives; the neighbour's unenumerated 23-reading aggregate; missing mature-read timestamps and historical top-ten boundaries; September 7 run primary manifests absent from the snapshot; the active funding experiment's outcome; the actual current live account state; current sealed-bank opening receipts; all canonical repository message/inbox linting; and independent reproduction of the proposed future pipeline.

These limitations are recorded in the report and handoff. Missing history prevents certification of an exhaustive August 20–September 7 table. It does not invalidate the 16-row main transcription or justify filling blanks with guessed dates. WORKSTATE summaries are marked reported evidence, not freshly rerun results.

## Integration boundary

The connector blocked a non-force fast-forward of the canonical agent branch. I did not force it, delete/recreate the branch, or use an alternative ref update. New files were published through ordinary contents writes on the existing `agent/chatgpt_1`. The source evidence pin is newer than that branch's starting base.

The coordinator can cherry-pick this session's published commits, run the reproduction commands against the evidence pin, request the named missing raw reports, then update BOARD. The final handoff pins the already published commit containing this verification record. No merge into main or coordinator acceptance is claimed by this document.
