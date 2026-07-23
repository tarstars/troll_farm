# D150a population value-support audit — result

Date: 2026-07-23  
Decision: **collect exact conditional-second counterfactual replays**

The join is mechanically exact across 66,560 population rows, 909 manifests, and 2,508 candidate
groups. Every one of the 776 active first/second chosen actions is observed and no joined slot falls
outside its replayed legal action set.

First-action return support is already strong: the 388 active first groups join 15,979 terminal
episodes and 5,059 distinct actions. 381/388 groups observe at least four actions, median legal
coverage is 90%, and 99/388 = 25.52% contain a nonselected action within five margin points of the
observed maximum. D148 can therefore support first-stage value/near-tie labels without another
search.

Conditional-second support is sparse. The 388 active second groups join only 843 exact-first-path
episodes and 797 actions. Median legal coverage is 11.11%; 153 groups expose only the selected
action, 126 expose two, and only 46 expose four or more. Just 29/388 = 7.47% contain a nonselected
near-tie. Although raw second count/coverage floors barely pass, the combined first/second near-tie
rate is 128/776 = 16.49%, below the frozen 20% gate.

Do not fit another argmax classifier or reinterpret the threshold. Reuse each of the 909 selected
first trajectories, branch every legal action at its replayed second state (including control), and
record exact terminal returns. This targeted corpus needs roughly 15k useful branches and no fresh
maps; sharding the consumed 64-map panel on YT is cheaper and more informative than repeating the
66,560-episode schedule search. Reserved maps remain untouched.

Result JSON SHA: `29a53c70...`.
