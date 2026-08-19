# Cure-C paired night — M-1 bookkeeping ledger (2026-08-18)

Charter: `coordination/tasks/20260817-cure-c-implementation.md` §4 — "the paired
candidate-vs-resident night runs under the M-1 rule; local_claude_1 does the
Arena bookkeeping; KEEP vs REVERT is the OWNER's ruling on the night's numbers."
M-1 (owner-ruled 2026-08-15, `coordination/tasks/20260815-banana-farm-two-specs.md:103-117`):
interleaved ABAB, one submission per ~2 h (mature 160-game read settles in ~2 h,
measured 2026-08-12); one block ≈ 20 h = 5 adjacent (A,B) pairs.

## Arms (both byte-verified this session, 04:57Z)

| arm | source | sha256 | submit command |
|---|---|---|---|
| A = cure C | `cgauto/submissions/submitted-sub41153619-cure-c-quiet.rs` (75,844 B) | `ad3bfefe4b2326f4f6b4a270dc862ea19a0e319a1cddfde44b96cc6f6d35a5d1` | `python3 cgauto/api_submit_once.py cgauto/submissions/submitted-sub41153619-cure-c-quiet.rs --expected-sha256 ad3bfefe4b2326f4f6b4a270dc862ea19a0e319a1cddfde44b96cc6f6d35a5d1` |
| B = resident | `cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs` | `98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29` | `python3 cgauto/api_submit_once.py cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs --expected-sha256 98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29` |

Submitting the archived resident COPY is not a mutation of the byte-sacred
resident file; the alternation is the chartered M-1 procedure itself.

## Verdict arithmetic (fixed in advance)

- Verdict object: 95% CI of the PAIRED difference Δ = mean over adjacent pairs of
  (A_i − B_i). Never two separate per-bot intervals.
- SE(Δ) = σ·√(2/n), σ = 1.501 (operational, closed 2026-08-14). n=5 → SE 0.949,
  1.96·SE = 1.861. Pooled n=10 → 1.32.
- Winner when |Δ| ≥ 1.96·SE. **Materiality floor: |Δ| < 1.0 → IMMATERIAL, stop**
  (point estimate; the standing value bar, not a statistical bound). Between →
  extend one ABAB block, max two extensions (30 runs, SE ≈ 0.55), then the floor
  forces the stop.
- Honesty clause: report the empirical paired-difference spread beside the
  planning σ; gross disagreement = "re-measure σ" flag, never a license to pick
  the flattering number.
- Pre-registered expectation: **+0.2 to +0.7 — IMMATERIAL is a possible HONEST
  outcome nobody re-frames.** m082 seat 1 (score 12 → 1) travels in every report
  as the named accepted cost. KEEP/REVERT = OWNER, on the numbers.

## Per-mark ritual (each ~2 h)

1. `python3 cgauto/cg_rank.py` → authoritative line (score, rank, agentId).
2. `python3 cgauto/battles.py 12` → battles-listed count (maturity sanity ≥ ~150)
   + W/L sample. If clearly immature, wait 15–30 min and re-read.
3. Record the row below, THEN submit the other arm (sha-verified command above),
   record new submission id + stamp. One mutation call per mark, fail-closed.
4. Commit + push the ledger row (no `--mark`, no lint-piping).

## Read log (times UTC, read off the clock)

| # | arm | submitted | submission id | agent id | read time | battles listed | score | rank |
|---|---|---|---|---|---|---|---|---|
| A1 | A cure-C | ~04:35Z | 41153619 | 6631618 | 06:31–06:33Z | 160 | 25.2 | 18/160 |

| B1 | B resident | 06:32:15Z | 41154017 | 6632048 | 08:27Z | 160 | 23.9 | 26/160 |
| A2 | A cure-C | 08:27:39Z | 41154515 | 6632611 | 11:03Z | 160 | 23.0 | 30/160 |
| B2 | B resident | 11:04:06Z | 41155368 | 6633209 | 12:58Z | 160 | 22.8 | 34/161 |
| A3 | A cure-C | 12:59:16Z | 41155957 | 6633433 | 14:58Z | 160 | 23.2 | 32/161 |
| B3 | B resident | 14:59:09Z | 41156649 | 6633935 | 18:11Z | 160 | 22.8 | 32/162 |
| A4 | A cure-C | 18:12:47Z | 41157565 | 6634457 | 20:58Z | 160 | 22.9 | 31/162 |
| B4 | B resident | 20:59:11Z | 41158211 | 6634792 | 22:58Z | 160 | 22.3 | 34/162 |
| A5 | A cure-C | 22:59:05Z | 41158573 | 6634986 | 00:58Z | 160 | 24.4 | 24/162 |
| B5 | B resident | 00:59:03Z | 41158835 | (at read) | — due ~02:59Z, FINAL | — | — | — |

- A5 read 00:58Z (1h59m, 160 battles). Sample 7/12, avg margin +33.
  A-windows: 25.2, 23.0, 23.2, 22.9, 24.4. Pair 5 completes at B5's read —
  THE BLOCK CLOSES THERE (no submission after the B5 read).
- B5 swap 00:59:03Z: accepted, sha `98628e98…` verified, one mutation call,
  HTTP 200, submission 41158835.

- B4 read 22:58Z (1h59m, 160 battles; note: the same score was visible at the
  59-min premature peek — settled early, read taken only at the window).
  **Pair 4: A4 − B4 = 22.9 − 22.3 = +0.6.** Pairs (+1.3, +0.2, +0.4, +0.6),
  mean +0.625 at n=4.
- A5 swap 22:59:05Z: accepted, sha `ad3bfefe…` verified, one mutation call,
  HTTP 200, submission 41158573. Then B5 (final window), block close ~03:00Z.

- A4 read 20:58Z (window 2h46m, 160 battles; late fire). Sample 6/12.
  A-windows so far: 25.2, 23.0, 23.2, 22.9. Pair 4 completes at B4's read.
- B4 swap 20:59:11Z: accepted, sha `98628e98…` verified, one mutation call,
  HTTP 200, submission 41158211. Remaining: B4 read ~22:59 → A5 → B5; block
  close projected ~03:00Z (drift accumulated; windows all ≥2h, valid).

- B3 read 18:11Z — window ran LONG (3h12m: the session REPL sat busy/idle
  through the 16:33/17:33 fires). Long windows are valid (more mature, no
  bias); noted for the honesty clause. Sample 9/12 wins.
  **Pair 3: A3 − B3 = 23.2 − 22.8 = +0.4.** Running (+1.3, +0.2, +0.4),
  mean +0.633 at n=3.
- A4 swap: FIRST ATTEMPT FAILED CLEAN at 18:11:59Z — RemoteDisconnected in the
  SESSION phase, mutation_calls=0, exit 2 (fail-closed before any submit).
  Verified by read: live agent still 6633935 → nothing landed. ONE retry
  (allowed: the no-retry rule guards ambiguous MUTATIONS; this was a failed
  read) → accepted 18:12:47Z, sha `ad3bfefe…` verified, one mutation call,
  HTTP 200, submission 41157565. Legend grew again 161→162 seats.

- A3 read 14:58Z (elapsed 1h59m, 160 battles). Sample 4/12 wins. A-windows so
  far: 25.2, 23.0, 23.2. Pair 3 completes at the B3 read (~16:59Z).
- B3 swap 14:59:09Z: accepted, sha `98628e98…` verified, one mutation call,
  HTTP 200, submission 41156649.

- B2 read 12:58Z (elapsed 1h54m, 160 battles = fully mature; within the ~2h
  tolerance). Sample 7/12 wins. **Pair 2: A2 − B2 = 23.0 − 22.8 = +0.2.**
  Running: pairs (+1.3, +0.2), mean +0.75 at n=2 — far below any decision
  threshold, three pairs to go. Note Legend grew 160→161 seats mid-night
  (rank denominators shift; scores unaffected).
- A3 swap 12:59:16Z: accepted, sha `ad3bfefe…` verified, one mutation call,
  HTTP 200, submission 41155957.

- B1 sample: 5/12 wins, avg margin ~−1 vs the 23.2–25.3 band (color only).
- **Pair 1: A1 − B1 = 25.2 − 23.9 = +1.3** (n=1; SE(Δ) at n=1 ≈ 2.12 — no
  claim, four pairs to go).
- A2 swap 08:27:39Z: fail-closed submitter accepted, sha `ad3bfefe…` verified,
  one mutation call, HTTP 200, submission 41154515.
- A2 read 11:03Z (mark fired late, elapsed 2h35m — window valid): 23.0 @ 30/160,
  sample 3/12 wins. A's two windows now span 25.2 → 23.0, a 2.2 spread —
  the operational σ visible in one arm; the pairing exists for exactly this.
- B2 swap 11:04:06Z: accepted, sha `98628e98…` verified, one mutation call,
  HTTP 200, submission 41155368. B2 read due ~13:04Z.
- Cadence note 11:04Z: replaced the odd-MSK-hour cron with an HOURLY :33 cron
  (same guard; premature fires stand down in seconds). Late REPL-busy fires
  were stretching windows ~30 min per mark; hourly firing bounds drift at
  ≤1 h and self-corrects. Windows stay ≥2 h; adjacency unchanged.

- A1 sample: 10/12 wins vs the 24.2–25.4 band, avg margin +57 (color only). 25.2
  exceeds every recorded resident mature read ([19.77…24.90], six reads) — ONE
  window, no claim; the paired B windows decide.
- B swap 06:32:15Z: fail-closed submitter accepted, sha `98628e98…` verified,
  one mutation call, HTTP 200, submission 41154017.

- 04:52–04:57Z liveness check (NOT an M-1 datum, immature): score 23.1,
  rank 32/160 Legend, promotable=False, 111 battles listed, sample 5/12 wins vs
  the 22.6–24.6 band (incl. L −4 vs yamo). Games flowing; identity fresh agent
  6631618 ≠ resident agents (6604529/6614096-era).

## Schedule (approximate, drift tolerated; window = arm's own ~2 h)

A@04:35 → read A1 + submit B ~06:30 → read B1 + submit A ~08:30 → read A2 +
submit B ~10:30 → read B2 + submit A ~12:30 → read A3 + submit B ~14:30 →
read B3 + submit A ~16:30 → read A4 + submit B ~18:30 → read B4 + submit A
~20:30 → read A5 + submit B ~22:30 → read B5 ~00:30Z (block complete, n=5) →
numbers to the OWNER.
