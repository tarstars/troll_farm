// I6 — YamoBot per-unit candidate retain-filter for the single protected
// banana mother (revised seam 2026-08-04, integrator item 5).
// Inserted immediately AFTER the parent's external_protected_tree retain
// statement (count == 1), inside the per-unit candidate loop of
// YamoBot::commands, i.e. before `by_id.insert(unit.id, candidates)`.
//
// Exact same shape as the orchard's protected-tree filter with
// `self.banana_protected_cell` in place of `self.external_protected_tree`;
// the seam revision fixes the compacted bytes of this insertion verbatim.
// Every candidate list keeps its WAIT candidate (Target::None), so the
// filter can never empty a list. No-op while the field is None (check 4).
if let Some(protected) = self.banana_protected_cell {
    candidates.retain(|candidate| {
        !matches!(
            candidate.target,
            Target::Tree(cell) | Target::Bank(cell) | Target::Cell(cell)
                if cell == protected
        )
    });
}
