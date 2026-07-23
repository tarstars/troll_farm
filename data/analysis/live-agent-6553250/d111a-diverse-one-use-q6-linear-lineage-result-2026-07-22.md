# D111a diverse one-use q6 linear lineage — result

Date: 2026-07-22  
Decision: **mechanics/search pass; no selection admission; held panel remains sealed**

## Execution

D111a completes five 64-policy generations over rotating four-map blocks, then evaluates the eight
final survivors on a separate 16-map / 256-task selection panel. The six matrices contain 45,632
policy rows and 576 exact D40 baselines. Matrix execution takes 2,346.31 seconds (39.11 minutes).

Every grid is complete. Exact zero rows reproduce D40; rewards and controller counters reconcile;
all values are finite; direct-command, provenance, and deposit failures are zero; crops remain
100%; and worker-three reach always clears the paired safety floor. The survivor cap preserves
eight founders after generation one, five after generation two, and the frozen minimum of four
thereafter. The optimizer therefore does not repeat D77's single-founder collapse.

## Search dynamics

The lineage produces attractive complete policies on individual 64-task blocks, but their value is
not stable:

- generation 2 finds `l0117` at `+5.516` mean, 48.44% strict wins, seven positive families,
  `-0.500` worst family, `+4.828` own score, and 78.13% activity;
- on the immediately following fresh block, the same policy falls to `-0.859`, with mybot
  `-20.875`, four positive families, and fitness changing from `+1.916` to `-18.431`; and
- generation 4's best policy gains `+1.922` with zero worst-family and p10 loss, but falls to
  `+0.109` and fitness `-1.841` on generation 5.

Fitness correlations for shared parents on consecutive blocks are `-0.517`, `-0.679`, `-0.016`,
and `+0.537`. Final-generation versus selection-panel fitness correlation is `-0.479`. Diversity
preservation therefore fixes ancestry collapse but not objective generalization.

## Independent selection

No final survivor passes the unchanged D110 discovery rule, so no champion is emitted and untouched
held seeds `9,842,000--9,842,031` remain unexecuted. On the 256-task selection panel:

- survivor means range from `-0.645` to only `+0.094`, with two policies exactly reproducing D40;
- strict improvements never exceed 8.20%;
- activity ranges from 0% to 17.19%, with six of eight below the 10% floor or effectively inert;
- no survivor has five positive families or mean at least `+1.5`; and
- crops remain 100%, worker-three reach exactly matches D40's 92.58%, and mechanics remain exact.

This is a value/activity transfer failure, not a safety, implementation, CPU, or lineage-diversity
failure.

## Conclusion and next abstraction

Close this exact one-use linear controller and lineage optimizer. Do not retain the generation-2
outlier, choose another final survivor, increase block size, extend generations, or tune the
mutation, activity penalty, or robust fitness on consumed maps. D110 and D111 jointly show that
whole-episode selection can find profitable q6 policies but cannot identify them reliably from
sparse terminal samples.

The next warranted branch changes credit density. At every eligible D40 boundary, evaluate every
deduplicated q6 proposal by an offline exact continuation. Work backward along each trajectory so
control means *wait for the best later one-use opportunity*, not merely never intervene. Train a
small deployable scorer on these act-now-versus-wait advantages using new maps, and qualify the
frozen scorer closed-loop on still-new maps. This is an offline Monte-Carlo teacher; no runtime
simulation or hidden opponent identity is permitted.

Result JSON: `fcb67beee3a8353e94a13c2f1280623dc5be35e5f3d1897b6a90241d2bbc5313`  
Orchestrator: `2895635fed71f2c3d9116af7a554bf6dfb7752cad94081624f56ac31ed09f98c`
