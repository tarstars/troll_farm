# The reference bot — handed over only after version 0 is frozen

This directory is **not part of the package** the implementer receives at the start. It holds:

| file | what it is |
|------|-----------|
| `reference-bot` | the existing bot as a compiled, stripped executable (sha256 `b24c3a0e…`); reads the protocol of `RULES.md` §13 on standard input, one command line per turn on standard output |
| `reference-vs-reference-48.json` | the bot against itself on the 24 frozen maps in both seats — the step-2 baseline (scores 59–220, mean 130; 16 wins, 16 losses, 16 draws) |

## Why it is held back

A stripped executable is still machine code, and a runner is an oracle: with both in hand from
the first minute, an implementer could recover the bot's decisions from the binary or from
unlimited queries instead of from the written description — and the experiment would then
measure the wrong thing. So the description is tested first, on its own:

1. The implementer receives `cleanroom/package/` alone: the rules, the constraints, the
   behaviour document, the domain dossier, the frozen maps and the referee. Step 1 of the
   acceptance ladder (legal, complete matches) is run **against its own bot** in both seats.
2. The implementer delivers a complete **version 0** and its source hash is recorded on the card
   before anything here is released.
3. Only then is this directory handed over, for the pre-registered refinement loop:
   the 48-match scout and the 144-cell locked panel against the reference, played through
   `referee.py --trace` with every trace archived under `cleanroom/refinement/`; the gaps are
   listed as game observations; the description is refined **once**; the bot is rebuilt.
   That is the whole query budget — no other use of the executable.

## What the implementer may not do with it

Run it through `referee.py`. Nothing else: no `strings`, no disassembly, no debugger, no
tracing of its system calls, no patching, no byte-level comparison, no reading of its memory.
The executable is an opponent, not a document.
