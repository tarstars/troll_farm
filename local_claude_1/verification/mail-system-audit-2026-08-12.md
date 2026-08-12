# Interagent mail system audit — 2026-08-12 ~21:10Z (owner-requested)

**Verdict: transport integrity CLEAN. The confusion is real and has a precise cause: a
three-day-old "ghost conversation" stamped with today's date, interleaved with today's
real traffic in every filename-ordered view.**

## Measured state (authoritative remote refs, 21:05Z)

| check | result |
|---|---|
| messages scanned | 1,115 (691 legacy-pinned, 413 v2, +11 quarantined) |
| delivery errors | **0** |
| quarantine errors | **0** (11 entries, all adjudicated, target blobs pinned) |
| immutable-path collisions | **0** |
| my unacknowledged obligations | **0** |
| claude_1's obligations (reconstructed from their tracked seen-state) | **1** — the 21:03Z composition-approval, minutes old |
| codex_1 traffic | current; three routine acks, all chains closed |

Every `requires_ack` message from every live sender has a discharging ack by exact path.
No message content is lost: quarantined items are content-preserved via retirements or
restatements in adjudications.

## Why claude_1's messages read as "stale or something" — three stacked causes

**1. The Aug-9 ghost conversation (the big one).** The 2026-08-09 fabricated-clock
session — the incident `check_clock` was built for — ran on BOTH sides and conducted a
complete conversation while believing it was 2026-08-12. It left **~17 claude_1 messages
(`163000Z`–`233500Z`) and at least 2 local_claude_1 replies (`204000Z`, `210000Z`), all
committed 2026-08-09, all stamped 2026-08-12**. They are fully processed (seen-state:
yes; acks: discharged by exact path within that same era; example: the `194000Z`
question is acked by `210000Z`, committed 2026-08-09T17:53Z). They are immutable history
and correct to keep — but any filename-sorted listing interleaves them with today's REAL
Aug-12 traffic. It even contains a same-minute stamp collision: claude_1's Aug-9
transport `blocker` and my real Aug-12 quarantine adjudication are both stamped
`…T193500Z`. A reader has no visual cue which era a message belongs to.

**2. Today's live stamp drift.** claude_1's real morning messages ran +4 to +42 minutes
ahead of their commit times (their own measured table; the worst two were `082000Z` and
`083000Z`). Corrected mid-day to `date -u`-only; their evening messages stamp honestly.
Reading the morning thread in filename order scrambles causality (e.g. the G2 handoff
appears "after" messages that reacted to it).

**3. claude_1's "new (unseen): 254".** Their tracked seen-state file lags far behind —
cosmetic, not integrity: novelty flags are per seen-state, while obligations derive from
content, and theirs compute to exactly 1. A screen showing 254 "new" messages, many
weeks old, looks exactly like a broken mailbox while being a stale watermark.

## Rules that already govern this, confirmed working

- `coordination/multi-agent-protocol.md`: *"Filename timestamps are human-readable
  ordering hints only"* — commit time is authoritative. The audit's confusion is what
  happens when a reader (human or agent) trusts the hint.
- Ack requirement is kind-based first (ruled today); supersession does not discharge an
  ack; retirement does not carry `ack_for`.
- The sweep fails closed: an invalid quarantine entry re-exposed all 11 quarantined
  messages rather than suppressing anything (observed live today, twice).

## Audit-of-the-auditor (defects in my own audit process, disclosed)

1. First drift table cut `%cI` to HH:MM, discarding the DATE — which is precisely how
   the Aug-9 tranche masqueraded as afternoon-today until a full-date read exposed it.
2. First seen-state check used `.get('paths', [])` against a file whose real key is
   `seen_message_paths` — a silent empty default produced a false "ABSENT" — the exact
   fixture-returns-empty class G3 exists to catch. Both corrected in-audit; both are
   arguments for the era-annex below rather than ad-hoc greps.

## Recommendations (no history rewrite; hygiene only)

1. **Era annex:** a small tracked JSON listing the Aug-9-committed/Aug-12-stamped paths
   (both senders), so tools and readers can label the ghost conversation without
   touching immutable messages. One-shot, mechanical.
2. **Viewer rule in the runbook:** when reading message directories, sort by commit
   time (`git log --format` per path), never by filename, for anything spanning the
   fabricated-clock era.
3. claude_1 to advance their seen-state watermark (one `--mark` + push) so their "new"
   count reflects reality — their obligations are already clean.
