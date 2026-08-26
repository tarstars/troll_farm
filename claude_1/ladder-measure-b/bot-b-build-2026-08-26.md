# L-1 bot B: the cured dancing troll, compacted for the ladder (2026-08-26)

Task `20260826-ladder-measure-cured-dancing-troll`, board row L-1, step 1.
Builder: claude_1. Checker: codex_1 (step 2). Arena operator: local_claude_1.

## What was built, in plain words

Bot B is the champion bot with one rule switched on — **"a troll keeps its goal"** (Candidate 3,
the cure for the swap-and-swap-back dance) — and with the same per-turn diagnostic line that
bot A carries. It is not a new program: it is the **instrument arm** that already passed the
Candidate 3 gates, squeezed down to fit the platform by the same squeezer that produced bot A.

The two bots on the ladder differ by **exactly one line** of readable source:

    line 602   A:  const KEEP_RULE_ENABLED: bool = false; const NARRATE_V6_ENABLED: bool = true;
               B:  const KEEP_RULE_ENABLED: bool = true;  const NARRATE_V6_ENABLED: bool = true;

That is the whole experiment. Everything else — the play logic, the resolver, the narrator — is
byte-identical between the two submissions' sources.

## The objects

| what | path | sha256 |
| --- | --- | --- |
| base of record (readable champion) | `readable/door1-champion.rs` | `ad1ae4ef…0bfb` |
| ladder champion (compacted base) | `cgauto/submissions/candidate-door1-pure-deletion.rs` | `547fa706…70b0` |
| the one source | `claude_1/cure3/cure3-keep-v6.rs` | `01b61444…b3b3` |
| gated instrument arm (= B readable) | `claude_1/cure3/arm-instrument.rs` | `01b61444…b3b3` |
| **B, readable** | `claude_1/ladder-measure-b/candidate-3-keep-v6-instrument.rs` | `01b61444…b3b3` |
| **B, submission** | `cgauto/submissions/candidate-3-keep-v6-instrument.rs` | `04e3db43865121e8b…` (see report) |
| A, submission (for contrast) | `cgauto/submissions/candidate-champion-v6-instrument.rs` | `72673124…` |

Round-trip report: `readable/reports/candidate-3-keep-v6-instrument.round-trip.json`
(also `claude_1/ladder-measure-b/results/build.json`), verdict
`CANDIDATE_3_KEEP_V6_INSTRUMENT_ROUND_TRIP_EXACT`.
Sidecar: `cgauto/submissions/candidate-3-keep-v6-instrument.rs.sha256`.

Sizes: B 63,961 bytes; A 63,962 bytes; the un-instrumented champion 75,653 bytes. B is smaller
than the bot already accepted by the platform, so there is no size risk in the submission itself.

## What the builder refuses on

`claude_1/ladder-measure-b/make_candidate3_v6.py` regenerates the arm; it does not copy it. Every
link below is checked and every failure is fatal (`BUILD REFUSED`, exit 2):

1. the readable base hashes to `ad1ae4ef…`;
2. the compacted champion hashes to `547fa706…` **and** has the same canonical token stream as
   the readable base — the base really is the bot on the ladder;
3. the one source hashes to `01b61444…`;
4. the flag line occurs exactly once, and B's arm differs from the source in **zero** lines
   (B *is* the source arm; A's rule-off arm is the one that differs in one line);
5. the regenerated arm is byte-identical to the already-gated `arm-instrument.rs`;
6. the arm compiles (`rustc --edition=2021 -O`);
7. the compacted file is written, re-read, its token stream compared against the arm's, and the
   written file compiled again;
8. the written file's token stream is **not** A's — a measurement that compared A with A would
   otherwise pass silently.

Run output:

    arm         01b61444a109c1d1  3129 lines  (flag line 602, 0 lines differ from source)
    compacted   04e3db43865121e8  63961 bytes  -> cgauto/submissions/candidate-3-keep-v6-instrument.rs
    vs bot A    different token stream (A 726731247910d846)
    round trip  EXACT -> readable/reports/candidate-3-keep-v6-instrument.round-trip.json

## What this build does NOT claim

- It does not re-run the 240-game parity. The claim it rests on is the recorded one from the
  Candidate 3 packet (`claude_1/cure3/g1-packet-2026-08-26.md` §: the instrument arm with `MSG`
  stripped is byte-identical in play to the candidate arm on all 240 games). Step 2 of the card
  asks codex_1 to confirm that the *submission* inherits it — that check is codex_1's, not mine.
- It says nothing about score. B cost 65 fruit over 240 local games; whether that shows on the
  ladder is exactly what the measurement is for. **No KEEP/REVERT comes out of this task**, and
  the champion of record is unchanged.
- The diagnostic line is not shown here to survive the platform's `MSG` truncation. The wire
  budget was measured for the v6 narrator on row 0-3a (328 characters); whether a *collected*
  game decodes without truncation is still open, and the card's "dead means" clause covers it.
