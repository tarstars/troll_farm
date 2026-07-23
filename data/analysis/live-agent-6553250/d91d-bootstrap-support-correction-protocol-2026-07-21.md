# D91d bootstrap-support correction — pre-prospective addendum (2026-07-21)

D91c copied D89's “at least three bootstrap plants in 75% of active tasks” support gate. Before any
D91 prospective map was opened, the executable development preflight showed that the frozen D91
selector deliberately selects some maps whose entire initial BANANA bank is two. The controller
successfully plants that whole bank and reaches sustained renewal in all 50/50 selected development
tasks, but only 35/50 (`70%`) can mathematically reach three bootstrap plants.

This is a support-definition error, not a controller or threshold result. Replace D91c activation
gate 6 with:

> At least 95% of selected tasks have a positive initial BANANA budget and successfully plant the
> entire available initial budget.

Keep the separate requirement for at least 24 sustained harvest/replant tasks. Retain the count of
three-plus bootstrap tasks as descriptive output only. No selector predicate, prospective map,
value threshold, safety threshold, code path, or confirmation rule changes. This addendum is frozen
before opening maps `9,914,064--9,914,079`.
