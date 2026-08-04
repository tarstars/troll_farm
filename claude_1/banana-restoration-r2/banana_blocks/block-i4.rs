// I4 — YamoBot::commands reservation hook, inserted immediately AFTER the
// anchor
// `if let Some(id)=self.external_idle_unit{by_id.insert(id,vec![MoisanBot::wait()]);}`
// (i.e. right before candidate selection).
//
// Mirrors the external_idle_unit reservation: while BananaBot reserves its
// resident, the inner policy plans only WAIT for that unit. No-op while
// `banana_idle_unit == None` (check 4 inertness). The protected-mother
// retain-filter is the separate insertion I6 (revised seam, integrator
// item 5), anchored at the external_protected_tree retain statement.
if let Some(id) = self.banana_idle_unit {
    by_id.insert(id, vec![MoisanBot::wait()]);
}
