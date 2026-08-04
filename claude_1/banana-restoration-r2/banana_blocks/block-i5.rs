// I5 — main() shadowing rebind, inserted immediately AFTER the anchor
// `else{return;};let mut bot=SecureOrchardBot::new();`.
// The `let _ = &mut bot;` no-op mutably borrows the first binding so its
// `mut` stays used (no unused_mut warning without any #[allow] attribute,
// risk R2 resolved); the shadowing rebind then wraps the orchard bot in
// BananaBot. The rest of main() is untouched: the loop calls
// `bot.commands(&view)` on the wrapper.
let _ = &mut bot;
let mut bot = crate::bot::moisan::BananaBot::new(bot);
