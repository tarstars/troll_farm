# Candidate 2 complete G-1 execution review — packet reproduced; stop-and-asks remain

- Task: `20260825-dance-cure-candidate-2-swap`
- Handoff: `agent/claude_1@7cd82f0811e616e9eff3da14a6fdfb3f7f8192bf`
- Review verdict: **G-1 packet accepted as reproducible measurement; Candidate 2 remains STOP AND ASK**

I extracted the handoff pin into a fresh temporary archive, regenerated the rule-off and
instrument panels, and ran the complete control driver set. The panel, controls C-1 through C-16,
and the candidate-arm P3 read reproduce the handoff.

Thirteen deterministic result files reproduced byte-for-byte after using their full chartered
populations (including `c7_poison_control.py --panel` and `c16_scoping_control.py --extend`).
The determinism result differs only in the explicitly clock-random P-13b poison fixture identities;
all four determinism layers reproduce PASS, including 1,096/1,096 game-arms on both streams and
1,096/1,096 build-to-build.

Key reproduced findings:

- rule-off parity: 34/34 fixtures twice and 240/240 panel games;
- Candidate 2: 46 exchanges on 28 games; D-1 falls 27 episodes in 25 games to 13 in 12;
- C-5: 12 within-six-turn pair repeats on four panel games, plus five on two fixtures — the
  preregistered STOP AND ASK remains open;
- C-6: zero consecutive-turn repeats; the poison arm raises C-5 from 17 to 350 and C-6 from
  0 to 344 over the full fixture-plus-panel population;
- C-8: nine restored-progress positives and four detector-silenced failures;
- C-10: 66/66 realised exchanges; C-11: 54,800/54,800 previous-cell reads;
- C-15: 10 score-changing games, seven better and three worse, net **−24 own-score points**;
  `m061` contributes **−75 own-score points** across two seats and remains a separate owner ruling;
- C-16: scoped 0 versus unscoped 9 P3 violations on the full 60-view population; candidate-arm
  P3 has 0 violations, with exits A/B/C = 228/12/0;
- C-12, under the record owner's ruled definition: corpus 0.3818% versus 0.7323%, no newly
  above-bar unit life, **PASS**. The 16 episodes remain qualified by 107/384 evaluable unit lives
  and 277 blind.

The packet is accepted as a faithful and reproducible record. It does not qualify Candidate 2,
authorize an Arena action, or resolve the owner's C-5, Candidate 0, and `m061` questions. The
two-game exchange tick-budget breach is contained in the open C-5 set and remains visible.

The narrator-parameter repair remains follow-up charter `20260826-p4b-narrator-param`; no gate
code was changed during this review.
