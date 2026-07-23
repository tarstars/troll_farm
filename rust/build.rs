use std::env;
use std::fs;
use std::path::PathBuf;

fn main() {
    const SOURCE: &str = "src/bin/d162_resident_native_capital_option.rs";
    const INNER_DOC: &str =
        "//! D162a: bounded third-worker capital options over an always-warm exact resident.\n";
    println!("cargo:rerun-if-changed={SOURCE}");
    let source = fs::read_to_string(SOURCE).expect("read frozen D162 source");
    let inherited = source
        .strip_prefix(INNER_DOC)
        .expect("frozen D162 source starts with expected inner doc");
    let output = PathBuf::from(env::var_os("OUT_DIR").expect("OUT_DIR"))
        .join("d162_resident_native_capital_option.in.rs");
    fs::write(output, inherited).expect("write inherited D162 source");
}
