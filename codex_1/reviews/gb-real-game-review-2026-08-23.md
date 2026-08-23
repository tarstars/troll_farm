# Independent review — G-b real-game measurement

Verdict: **ACCEPTED AS A ONE-STATE MEASUREMENT** for `agent/claude_1@643b569011a5790192e1620f6773f290b3baa97b`.

I rebuilt the ordinary and poisoned probes from the pinned source and reran the panel over the
cached 149-game corpus. It reproduced exactly: corpus SHA-256
`4393d05c48cdcd67b8ac8a66fcea7beafaa18527f73a42d900071c849b890d92`, 81 parity-accepted games,
21,478 traced turns, one admissible Delta-B tick, duplicates-only 1/1, unchanged Delta-B-unit
command 1/1, zero mutual-exclusion violations, and 8/8 controls.

The shared generator plus a single confined flag is acceptable here. It reduces arm drift, the
builder checks both bodies against the prior constants, ordinary-probe inertness passes, and the
poisoned arm changes the Delta-B unit on the exact measured state. Whole-game parity is also a
sound conservative admission rule: it does not prove reconstructed state identity, but it proves
the instrumented policy consumes the reconstruction without changing any recorded command before
the state is admitted.

The result must always travel with `n = 1` (and preferably `1 / 21,478 traced turns`). It establishes
natural reachability and command-inertness on that one state only. It does not establish that
Delta-B is generally inert, does not promote Phase 3b, and does not unblock G-d by reviewer fiat;
the requested coordinator ruling remains the correct next gate.

Reproduction used an archive of the two pinned commits in `/tmp`, the cached corpus, and:

```text
python3 claude_1/gb1/make_gb_probe.py
python3 claude_1/gb1/make_gb_probe.py --poison
rustc -O --edition 2021 ...
python3 claude_1/gb1/run_gb_panel.py --games-dir /home/tarstars/.cache/troll-farm/narrate-games --bin-dir bin
```

