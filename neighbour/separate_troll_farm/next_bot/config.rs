// Investment profile. Both profiles share the productive fallback and stock ledger.
const PARALLEL_CAPITAL: bool = true;
// Ceiling on own workers, including the starting one. 4 keeps the historical policy.
const WORKER_LIMIT: usize = 4;
// Scarce-fruit denial inside the live production comparison. false is the archived
// behaviour; the exporter substitutes true for the enabled variant.
const RESOURCE_DENIAL: bool = false;
