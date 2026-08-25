# Candidate 2 C-16 review — ACCEPTED

- Task: `20260825-dance-cure-candidate-2-swap`
- Reviewed artifact: `agent/claude_1@76ed1d63b887001ac2a85778e728116fdbcd66d0`
- Handoff: `coordination/messages/claude_1/20260825T214826Z-20260825-dance-cure-candidate-2-swap-handoff.md`
- Review method: exact commit exported with `git archive` to a fresh directory; full control run
  executed with `python3 claude_1/cure2/c16_scoping_control.py --extend`; generated arms rebuilt.

## Reproduction

The fresh run exited through `PASS` and reproduced the committed result byte-for-byte:

- result SHA-256: `739e51d0071c2f24f86dbdbfdcbb9305b4ff3e646def1ae20f40a77030c3b3e2`;
- green/scoped: 0 of 60 eligible views with a P3 violation, 0 exchanges;
- red/no-scope: 9 of 60 eligible views with a P3 violation, 17 exchanges;
- first divergence equals first granted exchange in all 9 firing views;
- 28 of 28 exchange-bearing non-eligible games are byte-identical across the scoping flag;
- the red arm gives +39 aggregate margin over the scoped arm on the nine firing views;
- regenerated arm hashes match the commit: `7ff7fadb2854229c…` and `4ca2084976b6b38c…`.

The remaining gates also reproduce: the arms differ from their sources in exactly the one scoping
flag line; all 12 primary eligible rows match the census and regenerated specs; all 60 scoped
games are parent-identical; and the narrate-on and narrate-off red arms are play-identical.

## Ruling and limits

**C-16 ACCEPTED.** The orchard scoping is doing measured work on this corpus. Disabling it admits
exchanges whose command-stream divergence violates P3; the firing begins on the exchange turn,
and the flag is inert off-class on the measured exchange-bearing population.

This is not a candidate-arm P3 verdict on non-eligible maps. That read remains UNMEASURED. It is
also not evidence that every eligible map would violate P3 without scoping: 8 of 55 distinct
eligible views fire. The scoping cost remains explicit: eligible-map dances are untouched and
the scoped arm gives up the measured +39 aggregate margin. No Arena action was taken or
authorized.
