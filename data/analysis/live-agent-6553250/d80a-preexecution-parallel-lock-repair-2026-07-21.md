# D80a pre-execution parallel lock repair (2026-07-21)

Two D80a diagnostic launches were stopped before either completed, created an output file, or
exposed any policy outcome. The first showed one running thread and nineteen threads waiting on
the row mutex despite a 20-worker request. After the source repair and tests, a short verification
launch revealed that `cargo test` had rebuilt only the test harness, leaving the old release
executable in place; it too was stopped with no output. An explicit `cargo build --release --bin
d80_one_shot_contested_crop` then built the accepted executable.

Rust receiver evaluation acquired `rows.lock()` before evaluating the `play(item)` argument in:

`rows.lock().expect(...).push(play(item));`

The sole repair computes `let row = play(item);` before acquiring the mutex and then pushes the
completed row. It changes no map, policy, action, feature, gate, sort, serialization, or experiment
decision. The incomplete process used runner SHA-256
`c1f7c6fb494d249ab3d8b7c07201fbafb72f2672b2aeb42e243be879e406a3a5`; the accepted runner uses
`11c1807772f5062a0301785b3ddcb08fd8b1f20f46ae443a6a7a206f0ff36456`.

The unchanged complete matrix must now run twice with 20 threads and satisfy the original D80a
byte-repeat and integrity gates. The stopped no-output diagnostics are not experiment replicates.
