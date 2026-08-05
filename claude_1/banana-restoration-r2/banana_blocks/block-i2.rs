// I2 — YamoBot struct fields: the dedicated banana reservation seam.
// Inserted inside the anchor `external_protected_tree:Option<Cell>,}` right
// after the `,` (i.e. before the closing `}` of `pub struct YamoBot{...}`).
// `banana_idle_unit` mirrors `external_idle_unit` (worker reservation);
// `banana_protected_cell` mirrors `external_protected_tree` (single protected
// mother, integrator correction C5). Both default to None (I3) so the parent
// behavior is unchanged until BananaBot writes them (check 4 inertness).
banana_idle_unit: Option<i32>,
banana_protected_cell: Option<Cell>,
