# Simplest Rust runner — no cargo, no project.
#   make            compile + run scratch.rs
#   make FILE=x.rs  compile + run x.rs instead
#   make check      just type-check (fast, no run)
#   make clean      remove the built binary
#
# In emacs:  M-x compile  RET  make  RET   (errors are clickable in *compilation*).
# Tip: put  (setq compile-command "make")  in your config so it's the default.

FILE ?= scratch.rs
BIN  := /tmp/rust-scratch-bin

.PHONY: run check clean
run:                       ## compile (edition 2021) and run
	@rustc --edition 2021 $(FILE) -o $(BIN) && echo "── output ──" && $(BIN)

check:                     ## type-check only (fast), no binary
	@rustc --edition 2021 --emit=metadata $(FILE) -o /tmp/rust-scratch.rmeta && echo "OK: type-checks"

clean:
	@rm -f $(BIN)

# default target
.DEFAULT_GOAL := run
