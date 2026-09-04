# Test execution

Executed in the interactive `chatgpt_2` session before publication.

```text
python3 -m unittest -v
Ran 9 tests in 0.002s
OK
```

Covered:

- water-side and inland growth milestones for all four species;
- mature health and chop-turn counts;
- the planting-turn growth tick;
- preservation of chop damage through growth;
- conservative wood returned on death;
- cohort standing-wood accounting;
- piecewise raid-survival approximation;
- fail-closed invalid inputs.

Source SHA-256:

- `orchard_kinetics.py`: `9b9c6f165150c02b3a33b44f3dde4d32ef6aae283bdf7f315d8a7a3f8bcea751`
- `test_orchard_kinetics.py`: `ecfd909766fe19852bd2a3e07bfc263063e2c618b57d836de9f78aa19c0aa30c`

This is execution of the isolated micro-instrument, not a referee parity claim
for a full map and not a value result for the live orchard card.
