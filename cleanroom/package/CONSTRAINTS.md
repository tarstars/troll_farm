# CONSTRAINTS — what the platform will and will not accept

These are hard limits of the submission environment. Every one of them has cost this project a
submission at least once. They are not preferences.

---

## 1. One file, standard library only

The bot is **one source file**. There are no modules, no crates, no dependencies beyond the
language's own standard library. Nothing is read from disk at run time; nothing is downloaded.

If you write in Rust, the file must compile with a stable toolchain as:

    rustc --edition=2021 -O -Awarnings <file>

with no `Cargo.toml`, no features, and no nightly syntax. Other languages the platform supports
are equally acceptable; the one-file, standard-library-only rule is the same for all of them.

## 2. The size limit is 100,000 UTF-16 code units

The platform counts source length in **UTF-16 code units**, not bytes and not characters.

- An ASCII character is 1 unit.
- A character outside the Basic Multilingual Plane (an emoji, for instance) is **2 units**.

So a file of 100,000 bytes of ASCII is exactly at the limit; a file of 100,000 bytes containing
non-ASCII text may be well over it. Measure the way the platform measures:

    python3 -c "import sys;print(len(open(sys.argv[1],encoding='utf-8').read().encode('utf-16-le'))//2)" FILE

This limit only bites if you embed data in the source. Ordinary hand-written code is nowhere
near it.

## 3. Time: 1000 ms on turn 1, 50 ms on every other turn

The referee tolerates three overruns of at most 50 ms each; one overrun of more than 50 ms over
the limit loses the match on the spot.

**Budget well under the limit.** The judge machine is not your machine, it is shared, and it is
slower than a modern desktop. A bot that measures 45 ms locally will lose matches. Treat 15 ms
as the working target for a turn and use turn 1's larger budget for one-off setup (parsing the
map, building distance tables) rather than for per-turn work.

## 4. CPU instruction sets are not guaranteed

You may not assume AVX2, or any other post-baseline instruction set, is present on the judge
machine. If you use one you must detect it at run time and provide a plain fallback path that
produces **identical output**:

    if std::arch::is_x86_feature_detected!("avx2") { ... } else { ... }

A binary that faults on an unsupported instruction does not lose a match, it loses every match.
Unless you are hand-writing numeric kernels, the right answer is: do not use them at all.

## 5. The protocol never tells you which seat you are

Every troll's `player` field is **relative to you**: `0` means yours, `1` means the opponent's.
The map prints your shack as `0` and the opponent's as `1`. Nothing in the input stream says
whether you are the player the platform calls first or second.

If your bot needs the absolute seat — for a symmetric transformation of the board, for a
deterministic tie-break that must differ between the two sides, for anything at all — recover it
**once, on turn 1**, from the troll ids:

- on turn 1 exactly two trolls exist and their ids are exactly `{0, 1}`;
- **id 0 belongs to the first seat, id 1 to the second**;
- so: find your own troll (the one with `player == 0`); if its id is 0 you are seat 0, if its id
  is 1 you are seat 1.

Then **cache it and never recompute it** — after turn 1 new trolls appear and the id set is no
longer `{0, 1}`.

**Fail closed.** If turn 1 does not present exactly the id set `{0, 1}`, do not guess: that is a
state your assumptions do not cover, and a wrong seat produces a bot that plays confidently and
wrongly rather than one that crashes.

If your bot does not need the absolute seat, do not recover it. Everything in the rules is
expressible in the relative frame the input already gives you.

## 6. Determinism

Given the same input stream your bot must produce the same output. Do not seed a random number
generator from the clock, from the process id, or from anything else that varies between runs;
if you want randomness, derive it from the board.

Two things in the world are **not** deterministic and you cannot control them: the referee's
random tie-break between equally short paths (RULES §4), and the map draw. Any test that
requires a specific choice among equal-best paths is testing something the game does not
promise.

## 7. Output hygiene

- Everything on standard output that is not a command is a syntax error. Print your debugging
  to **standard error**, or inside a `MSG`.
- One command per troll per turn; the first one naming a troll wins and the rest are dropped.
- An unrecognised verb is an immediate loss. If you build commands by string concatenation,
  make an empty or malformed command impossible by construction — print `WAIT` rather than
  nothing.
