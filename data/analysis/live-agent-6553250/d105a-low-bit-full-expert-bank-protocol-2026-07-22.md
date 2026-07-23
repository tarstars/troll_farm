# D105a low-bit full-expert bank — frozen protocol

Date: 2026-07-22  
Status: frozen before quantized population generation, proposal reconstruction, or value access

## Question

D104a's 64-expert union has the required joint coordination value, while D104b shows that deleting
experts loses it. Can all 64 proposal experts instead be represented by low-bit signed integers,
with a prospective fidelity-selected precision, while retaining D104a's causal value and fitting
comfortably below the 100 kB agent limit?

This is a representation audit, not policy selection. Quantization and bit-width selection may
inspect source weights, current-state proposals, and immutable D97 action semantics only. Terminal
scores, winners, D104a oracle rows, family deltas, and outcome ranks remain unread until one bit
width is irrevocably locked.

No learner, new terminal simulation, candidate, platform access, submission, or resident mutation
is permitted.

## Immutable inputs and implementation

- quantizer `cgauto/make_d105a_quantized_expert_population.py`:
  `c9efaea2f22c6225ac2731b80e55952e2f6b85a4c533029a1fd6a62dc0a4599b`;
- unchanged D104 proposal runner:
  `c68652529212d9d5067d533d3abee8865667aa821b544b8adce2b7aaff096393`;
- D98 source population:
  `3bff0c4a9ddffdf33bac305a23a99e1f5a04655c5d6bb7af428697b237db253e`;
- exact D104a proposals:
  `54bd509e60d83d3caa09d9dfed310b1e7422e186935917ec529bd854c7f07cd9`;
- D97 manifest:
  `ed5a6ffeb73032006fed7e08518e82c6cf549e2b8f24f7798cbceb82837c157e`;
- D104a result, unavailable before lock:
  `c27e5ac38aabbb91ce02f175dd130d7edc01b6d9294f2817186ca26dd951f8bc`;
- D97 terminal arms and baselines, unavailable before lock:
  `c6ee144a4c89d4a504d7c7bf356628a7b3fc506b1ba29b991c1cc0caa0b08d33` and
  `8936d7007074a240f21073aea4c5fa43851093cfd90e1827a4fe4370609b40b6`.

## Frozen quantization

Evaluate bit widths in the fixed order `4, 6, 8`. For each expert independently, parse its 153
source coefficients as IEEE-754 `f32`, set `qmax = 2^(bits-1)-1` and
`scale = max(abs(weight))/qmax`, then encode each coefficient as round-to-nearest-ties-to-even of
`weight/scale`, clipped to `[-qmax, qmax]`. A zero vector remains zero.

The positive scale need not be stored or applied: every option scored by one expert would be
multiplied by the same scale, so its argmax and tie order are unchanged when the integer vector is
used directly. The 64 labels, four-use budget, 153-feature ordering, D104 executor, and proposal
tie order remain unchanged.

Packed coefficient size is `ceil(64*153*bits/8)`. The source-size proxy is unpadded base85,
conservatively counted as `ceil(raw_bytes/4)*5`: 6,120 bytes at four bits, 9,180 at six bits, and
12,240 at eight bits. Runtime decoder/controller code is outside this audit; require this payload
to be at most 13,000 bytes.

Generate all three populations and reconstruct their 15,360 proposal rows with one local worker.
These runs stop at the D97 root and do not access terminal outcomes.

## Frozen outcome-blind fidelity selection

Compare each width only with exact D104a proposal identities and manifest action support. Examine
widths in ascending order and lock the first satisfying every gate:

1. exactly 64 experts by 240 roots, unique `(root_id, expert)`, exact root metadata, finite hashes,
   and 100% supported paired-boundary proposals;
2. exact `arm_id` agreement with the full-precision expert in at least 80% of all rows;
3. for each root, compare deduplicated noncontrol arm sets: mean exact-set recall at least 85%,
   minimum recall at least 50%, and mean Jaccard similarity at least 75%;
4. at least 14 unique noncontrol proposals per root on average, never fewer than six, and a joint
   proposal at every root;
5. at least 48 experts emit a noncontrol proposal in at least 25% of roots;
6. the union spans all four jobs, natural/own/opponent provenance, both seats, all eight opponent
   families, and reversed worker-role order; and
7. packed base85 coefficient payload at most 13,000 bytes.

If no width passes, close low-bit quantization. Do not inspect terminal value for any width. If a
width passes, serialize its width, population/proposal hashes, fidelity metrics, and rejected
lower-width diagnostics as an outcome-blind lock before reading any terminal file. Do not inspect
higher-width fidelity after the first pass. Do not compare terminal value across widths.

After locking, rerun only the selected width with twenty local workers and require byte identity
with its one-worker proposal file.

## Integrity gates after lock

1. all immutable, generated-population, proposal, and lock hashes match;
2. generation repeated from source produces byte-identical populations;
3. the selected one-worker and twenty-worker proposal matrices are byte-identical;
4. all D104a root, proposal-support, source-order, feature-hash, action, expert-hash, and mirror
   invariants hold for the selected matrix;
5. the exact D104a audit and D97 terminal/control integrity reproduce; and
6. the lock demonstrably predates terminal-value access and contains no outcome field.

Any integrity failure permits measurement repair only.

## Frozen selected-union value gates

After the bit width is locked, join its deduplicated proposals to immutable D97 outcomes with the
unchanged D104a hindsight tie order. Tasks without roots remain D40. Require all:

1. mean margin gain over D40 at least `+28` and at least 90% of D104a's full-precision union gain;
2. capture at least 78% of D97's complete joint-or-control oracle;
3. strictly improve at least 82% of rooted tasks and gain at least `+15` in every opponent family;
4. mean own-score delta nonnegative and opponent-score delta nonpositive;
5. crop creation exactly 100% and worker-three reach within five points of D40;
6. mean rooted gain at least `+2` beyond D97's complete best-single oracle;
7. select a joint proposal in at least 50% of roots and have a joint strictly beat best-single in
   at least 35%; and
8. selected proposals span at least three jobs, two provenance classes, both seats, all families,
   and reversed worker-role order.

No expert, proposal, precision, or arm may be selected from favorable terminal outcomes.

## Decision rule

- **Full pass:** freeze the quantized proposal ABI and open D105b, a fresh-map recurrent
  opponent-aware proposal-controller mechanics and signal preflight.
- **Fidelity failure:** close the full-bank low-bit representation without weakening fidelity
  gates or trying wider-than-eight-bit coefficients on these roots.
- **Value failure:** close quantization without choosing a different bit width after outcomes.
- **Integrity failure:** repair measurement only.

No result authorizes PPO-scale training, packaging as a submission, TestSession, Arena, submission,
or resident mutation.
