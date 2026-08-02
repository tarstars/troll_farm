# Wide corpus catch-up — 2026-08-02

Status: **COMPLETE / QA PASS / ZERO PARSE FAILURES**

## Cron diagnosis

The owner's suspected collection gap was not present in the cron log. The installed entry
still runs `data/scripts/collect_wide_cron.sh` at 05:17 local time. Consecutive successful
runs added 507 games on July 29, 444 on July 30, 290 on July 31, 620 on August 1, and 196
on August 2. The cache was already at 10,188 before this manual run; `docs/STATE.md` was
stale at 9,082. No cron configuration was changed.

## Manual collection

The established idempotent driver ran once with current agent `6589709` as resident and
the full visible windows of Legend ranks 1–50. Snapshot:
`data/raw/snapshots/20260802T092656Z-d61p-wide`.

- completed: 2026-08-02T09:30:28.490Z;
- selected agents: 50; battle lists fetched/failed: 50/0;
- unique games wanted: 6,682;
- already present: 6,400; newly fetched: 282;
- requests: 333; acquisition failures: 0;
- manifest SHA-256: `27f00b482266f9290903a529ea4119dc96d2bb7825fef53b2ce38cbcae2fcfe4`.

Snapshot QA parsed all 6,682 eligible replays with zero acquisition or parse failures and
zero duplicate trajectory groups. It contains 160 current-resident games, 6,675 open games,
and seven games segregated by the established parser as sealed-confirmation material; no
manual analysis opened that material. QA SHA-256:
`f64096ba7c692b9a3574457875801610d1a0a304143cbea0e334a415ec785dab`.

The cumulative rebuild reports 10,470 raw games, 10,470 parsed, zero failures, 10,470 unique
maps, 513 unique agents, 272 names, and 32 boss games. Cache size is 3.1 GB. Processed stats
SHA-256: `1fbc346b0ada28bbad52d91ff889454e4e04c6a77fb89ee27fd9acaf8bc71903`.

## Active submission recovered with the corpus

All 160 resident battle rows identify exact agent/submission `6589709`/`41079653`, and all
160 corresponding replays were newly fetched. A separate repository-standard checkpoint
confirms score 23.12, rank 32/130, 101W/2T/57L, mean margin +23.44375, ten catastrophes
(6.25%), negative-margin mass 3,318, clean identity, and zero runtime signals. Checkpoint:
`owner-top-score-opponent-crop-mature-checkpoint-20260802T094000Z.json`, SHA-256
`f6367e7feb6b1a6ce219eaedb08d575e3d1ab9ce0ec6eab2be7671ac38f13831`.

The current repeat is 1.77 below the source's historical 24.89 run. Its two-run cross-era
median is 24.005, so the registry now ranks the four-run preseed source first at 24.19.
This evidence update performs no Arena mutation.
