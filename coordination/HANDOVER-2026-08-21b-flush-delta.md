# HANDOVER 2026-08-21b — flush delta (AMENDS, does not supersede, the 08-21 handover)

Read `coordination/HANDOVER-2026-08-21-owner-rulings-and-4b.md` FIRST. Everything
in it is still true. This file records only what changed between 04:42Z and
07:00Z and what I leave owed. This session was read-only: no commits to code, no
Arena action, no message published, no ruling made.

## What changed since the 08-21 handover

1. **Session 3 advanced one pair and stalled at nothing.** Pair 1 = **0.0** — A1
   23.7 rank 26/176 (agent 6643835, read 02:51:30Z), B1 23.7 rank 26/176 (agent
   6644257, read 04:48:57Z). **A2 read 06:46:25Z: 21.3, rank 40/176** (agent
   6644785) — 2.4 points below A1 on the SAME arm, which is one arm and not a
   pair: pair 2 is A2 − B2 and B2 was submitted 06:46:28Z (id 41170974). Do not
   report a fall; the arithmetic is pre-registered and the pair is not closed.
   It is a plain reminder that a single read carries ~1.5 of spread. Four pairs
   remain, ~8 h. Nothing here needs action — night_runner owns it, and it pushed
   this read to my own branch at `ac8ad8ab` while I was writing this file.
2. **The OSC-032/033 charter is DELIVERED, in one night, in charter order.**
   claude_1 deferred it at 05:30Z, then ran it: codex_1 reviewed the instrument
   first (`ACCEPTED_FOR_G3`, 06:41:56Z) and G-3 landed at 06:51:07Z
   (`50fa5a8e`, `claude_1/nogoal/`). **The finding:** on every one of OSC-032's
   110 and OSC-033's 143 idle turns, the main generator returned exactly one
   candidate — a seeded `WAIT` — through `IDLE_REGEN_FALLBACK`, with
   carried=0 / free_cap=2 / safe_regen=true / no chops on all of them. Nothing
   real was formed, so **nothing real was discarded**. Phase 3's shape (two real
   `PICK`s built then thrown away on 101 of OSC-013's 170 idle turns) does
   **not** carry across. Owner brief exists:
   `claude_1/nogoal/owner-brief-2026-08-21.md`. It names no bug and asks the
   owner for nothing.
3. **A transport defect was found and repaired: self-addressed cards were
   invisible.** `inbox_sweep.py` built its addressed set as
   `m.sender != me and addressed_to_me(...)`, which drops every message an agent
   sends to itself before addressing is consulted — so the deferral rule's
   "self-address it so my own sweep surfaces it" half **never once worked**.
   claude_1 measured it, repaired it in the shared predicate (`8c531096`, on the
   sentinel card, cross-tasked to `20260818-deferral-rule`), and the repair
   immediately turned claude_1's own count from **0 unacked to 12** — twelve
   never-discharged cards. It then triaged nine against their real deliveries,
   verifying every cited commit reachable with `git merge-base --is-ancestor`,
   and discharged them by doing the check, not by asserting it
   (`20260821T061633Z` correction). One card (`20260821T053050Z`) was genuinely
   live and is now discharged by the G-3 delivery.
   - The generalizable bit, which is ours not just claude_1's: **`supersedes` is
     inert for discharge; only `ack_for` discharges.** A Phase-1 handoff named
     its card in `supersedes` and the card stayed open for a day while the work
     shipped and was reviewed.
   - This is the same family as my extraction ruling: one predicate, one code
     path. The repair landing in the SHARED predicate is why it fixed the sweep
     and the sentinel at once.

## What I leave owed (nothing is blocked on it, but it is real)

- **I ran `inbox_sweep.py --me local_claude_1 --fetch` and did NOT run `--mark`.**
  That is deliberate: my successor re-sees all 24 as new rather than inheriting a
  silent "already seen". `local_claude_1/inbox-seen.json` is untouched.
- **Seven messages are unacknowledged with ack required**, all from claude_1, all
  from this morning. My successor's first job is to read them properly and ack:
  | message | what it is |
  |---|---|
  | `20260821T053050Z-...-osc032-033-...-deferred` | card 4 postponed — since discharged by G-3 |
  | `20260821T053322Z-20260818-self-addressed-deferral-inert-blocker` | the defect above, addressed to me as **rule owner** |
  | `20260821T060112Z-20260818-deferral-rule-backlog-blocker` | the 12 revealed cards |
  | `20260821T061246Z-...-osc032-033-...-deferred` | G-1/G-3 sequencing |
  | `20260821T061633Z-20260818-deferral-rule-backlog-closure-correction` | the nine triaged and discharged |
  | `20260821T063253Z-...-g3-deferred` | G-3 postponed to await codex_1 |
  | `20260821T065107Z-...-g3-handoff` | **the delivery** — addressed to me as integrator |
  Also unread by me in full: three claude_1 sentinel handoffs, the G-1 revision
  handoff, the pair-selector update, and eight codex_1 acks.
- **A coordinator decision is waiting in the blocker at `20260821T053322Z`:** it
  is addressed to me as rule owner and the deferral rule's text still describes a
  mechanism that did not work until today. The rule text likely needs amending to
  match the repaired behaviour. I did not rule on it.

## What did NOT change

Champion of record `547fa706…`. D3 = HOLD. The six 4b stamps HELD, still the
owner's nearest available decision (viewer links, `claude_1/viewer/out/<CASE>.html`).
The owner's extend-versus-replace question still unruled and nobody building
against it — and note that item 2 above **narrows** it rather than touching it:
OSC-032/033 turn out not to be more of OSC-013's case. OSC-031 still not fixed on
the champion. No reaper chartered; the VM disk will refill.

Worktree clean at `aec4138b`, branch `agent/local_claude_1`, dev copy untouched,
Arena untouched.
