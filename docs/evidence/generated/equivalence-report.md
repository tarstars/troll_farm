# Pilot CONSTRAINTS equivalence report

Every row maps a canonical record to the existing binding source and the generated
projection. Numeric-token coverage is checked mechanically by the validator.

| Record | Binding source | Match class | Scope | Binding decisive numbers |
|---|---|---|---|---|
| `D101` | `docs/CONSTRAINTS.md` (lines 113-116) | CONSTRAINTS-equivalent | Observed replay behavior of the resident and top-three agents; architecture diagnosis, not intervention value. | `3`, `93.3%`, `10.3%`, `24.16%`, `0.94%`, `78%` |
| `D161` | `docs/CONSTRAINTS.md` (lines 194-196) | CONSTRAINTS-equivalent | Control-substrate choice for resident-competition experiments. | `+3.42`, `−8.70`, `+15.54`, `22`, `43` |
| `D169` | `docs/CONSTRAINTS.md` (lines 732-741) | CONSTRAINTS-equivalent | Hindsight option-envelope value on the frozen 1,024-task panel; authorization for D170 only. | `+10.671`, `+9.420`, `+11.922`, `65%`, `0`, `+1.80` |
| `D172a` | `docs/CONSTRAINTS.md` (lines 451-460) | CONSTRAINTS-equivalent | D172a observation class, budget-1 decisions, linear and MLP function classes, frozen LOBO selection blocks. | `40.4%`, `27`, `392`, `+2`, `+0.14`, `+0.26`, `+1.5`, `0` |
| `D175a` | `docs/CONSTRAINTS.md` (lines 273-283) | CONSTRAINTS-equivalent | D175a bounded early-plant intervention on the exact resident scheduler and frozen paired panel. | `199`, `13`, `−26.44`, `−5.41`, `+21.09`, `229`, `130` |
| `D176a` | `docs/CONSTRAINTS.md` (lines 855-906) | CONSTRAINTS-equivalent | D176a exact-resident preference tie-break on the frozen 2,048-task panel; gate-design postmortem included. | `8.50%`, `2.88%`, `0`, `+0.045`, `−0.024`, `+0.114`, `133`, `247` |
| `D30` | `docs/CONSTRAINTS.md` (lines 201-206) | CONSTRAINTS-equivalent | Evaluation substrate and map-domain validity for all downstream controller experiments. | `80`, `−78.05`, `−72.12`, `120/120` |
| `H1` | `docs/CONSTRAINTS.md` (lines 943-958) | CONSTRAINTS-equivalent | Grounded finite-windfall accounting stress test on 220 resident games; conditional on fixed pricing constants and the current scheduler. | `−2.49`, `−2.78`, `−2.21`, `6/220`, `36.8%`, `78`, `0/220` |
| `H7` | `docs/CONSTRAINTS.md` (lines 917-922) | CONSTRAINTS-equivalent | H7’s original body-blocking hypothesis only; action contention and target races are separate questions. | textual premise only |
| `OWNER-ARENA-20260730` | `docs/STATE.md` (lines 47-69) | binding governance source; no matching CONSTRAINTS bullet | Live ladder mutation by the single arena controller under the promotion runbook. | `±0.5`, `1` |
| `OWNER-GOAL-20260730` | `docs/STATE.md` (lines 24-43) | binding governance source; no matching CONSTRAINTS bullet | Project objective and completion rule for the Legend practice ladder. | `25.40`, `24.70`, `25`, `7`, `54` |

## Interpretation

- Equality here means scope and decisive-number equivalence, not byte identity with the
  existing hand-written bullet.
- Nine scientific/hypothesis records map to existing `docs/CONSTRAINTS.md` bullets.
  The two owner decisions are governed by `docs/STATE.md`; they have no matching
  CONSTRAINTS bullet, and the report marks that absence rather than inventing equivalence.
- `void-premise` records are represented but excluded from scientific closure counts.
- The source `docs/CONSTRAINTS.md` remains untouched until the pilot is reviewed.
