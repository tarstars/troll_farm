// Thin CG-protocol shim (Phase R): the entire bot lives in the library module
// `troll_farm::botmain` so tests and the equality harness can reach it; the single-file
// arena submission is produced by tools/bundle.py (botmain.rs + this trampoline).
fn main() {
    troll_farm::botmain::run();
}
