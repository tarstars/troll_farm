// ── Rust scratch pad ──────────────────────────────────────────────────────
// Edit this file, then run `make` (in emacs: M-x compile RET make RET).
// It compiles + runs this single file. No cargo, no project — just Rust.
//
// The examples below map to the constructs explained in the tutorial PDF.
// Delete/replace them and try your own ideas. `main` is the entry point.

use std::collections::HashMap;

fn main() {
    // &str vs String — a borrowed view vs an owned, growable string.
    let name: &str = "world";           // &str: reference into fixed text
    let mut greeting: String = String::from("hello, "); // String: owned
    greeting.push_str(name);            // can grow (owns its buffer)
    println!("{greeting}");             // -> hello, world

    // Vec<T> — a growable array. HashMap<K,V> — a dictionary.
    let nums: Vec<i32> = vec![3, 1, 4, 1, 5, 9];
    let mut counts: HashMap<i32, i32> = HashMap::new();
    for n in &nums {                    // &nums: borrow, don't move it
        *counts.entry(*n).or_insert(0) += 1; // *n: deref the &i32
    }
    println!("counts of 1 = {}", counts[&1]); // -> 2

    // Iterators + closures — .filter()/.map()/.sum() with |x| ... lambdas.
    let sum_of_evens: i32 = nums.iter().filter(|&&x| x % 2 == 0).sum();
    println!("sum of evens = {sum_of_evens}"); // -> 4

    // Option<T> + match / if let — Rust's "maybe null", made explicit.
    let biggest: Option<&i32> = nums.iter().max();
    match biggest {
        Some(b) => println!("biggest = {b}"),
        None => println!("empty"),
    }
    if let Some(b) = biggest {
        println!("biggest again = {b}");
    }

    // A struct + a method (impl). Ownership: `p` owns its fields.
    struct Point { x: i32, y: i32 }
    impl Point {
        fn manhattan(&self) -> i32 { self.x.abs() + self.y.abs() } // &self = borrow
    }
    let p = Point { x: 3, y: -4 };
    println!("manhattan = {}", p.manhattan()); // -> 7
}
