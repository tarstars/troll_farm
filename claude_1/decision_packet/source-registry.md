# Decision Packet source registry (generated — do not edit)

- schema: `troll-farm-decision-packet/v1`
- subject: `cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs`
- subject sha256: `98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29`
- source_registry_sha256: `e6cb7000ed1e46a3ac05ab959c4a35869c920fb4c58dcf9d99eda9b012019ff0`
- stages: 12 · intents: 13 · priority classes: 4 · sites: 22

## Known gaps at this increment

- **13 of 13 intents carry no completion / progress / invalidation predicate yet** — the §5.2 fields are present and explicitly null. They are read out of the subject in rollout step 2+, never inferred here: `WAIT`, `BANK`, `EQUIP_FOR_TRAIN`, `CLEAR_SHACK_FOR_TRAIN`, `HARVEST_FRUIT`, `MINE_IRON`, `CHOP_WOOD`, `DENY_FOCUS_SPECIES`, `REGENERATE_CARRIED_FRUIT`, `CONVERT_BANKED_FRUIT`, `COMMIT_CURRENT_CHOP`, `IDLE_HARVEST`, `UNBLOCK_UNIQUE_DOOR`.
- **The site registry is NOT yet §5.4-complete, and this increment does not claim it is.** 22 sites are pinned against 79 function definitions in the subject. §5.4 also requires ids for every *filter*, *score term* and *early return*; no `FILTER_*` or `TERM_*` id exists yet, because those are sub-function spans and this increment pins whole functions only. They arrive with rollout steps 2–3. What is frozen is exact; it is not complete.
- **5 intents have no source site bound**: `CLEAR_SHACK_FOR_TRAIN`, `DENY_FOCUS_SPECIES`, `CONVERT_BANKED_FRUIT`, `COMMIT_CURRENT_CHOP`, `IDLE_HARVEST`. An intent with no site is a name with nothing behind it, and is listed rather than dropped.

## Spec discrepancies raised, not resolved silently

- §4 example enum omits EXECUTION_UNAVAILABLE, which §4 prose requires; implemented the prose.

## Source sites

| site_id | stage | intent | lines | io_shape | fingerprint |
|---|---|---|---|---|---|
| `GEN_BANK_CANDIDATES_FREE` | CANDIDATE_GENERATE | BANK | 371–399 | `fn bank_candidates(view:&GameState,unit:&Unit)->Vec<Candidate>` | `1437dc9dee5b…` |
| `GEN_EARLY_CANDIDATES` | CANDIDATE_GENERATE | EQUIP_FOR_TRAIN | 432–462 | `fn early_candidates(view:&GameState,unit:&Unit,desired:Stats)->Vec<Candidate>` | `d9e90af02e2e…` |
| `GEN_FRUIT_CANDIDATES` | CANDIDATE_GENERATE | HARVEST_FRUIT | 463–484 | `fn fruit_candidates(view:&GameState,unit:&Unit,kind:PlantKind,base_score:f64,)->Vec<Candidate>` | `e4dbc70954d1…` |
| `GEN_IRON_CANDIDATES` | CANDIDATE_GENERATE | MINE_IRON | 485–508 | `fn iron_candidates(view:&GameState,unit:&Unit,base_score:f64)->Vec<Candidate>` | `2cd5b14e178a…` |
| `GEN_CHOP_CANDIDATES` | CANDIDATE_GENERATE | CHOP_WOOD | 582–637 | `fn chop_candidates(view:&GameState,unit:&Unit,type_to_cut:Option<PlantKind>,)->Vec<Candidate>` | `33a5c817dcb5…` |
| `GEN_WAIT` | CANDIDATE_GENERATE | WAIT | 638–642 | `fn wait()->Candidate` | `49108636db67…` |
| `PAIR_COMPATIBLE` | PAIR_SELECT | — | 643–654 | `fn compatible(a:Target,b:Target)->bool` | `5d9bcb42cf6e…` |
| `PAIR_STOCK_COMPATIBLE` | PAIR_SELECT | — | 659–664 | `fn stock_compatible(a:&Candidate,b:&Candidate,inventory:&[i32;` | `70198808b810…` |
| `PAIR_SELECT_ARBITRATE` | PAIR_SELECT | — | 665–712 | `fn select(candidates_by_id:BTreeMap<i32,Vec<Candidate>>,inventory:&[i32;` | `6194b41fb6bc…` |
| `REWRITE_MOVE_CONFLICTS` | MOVE_RESOLVE | — | 720–722 | `fn resolve_move_conflicts(view:&GameState,commands:&mut[String])` | `9940dd24a110…` |
| `REWRITE_MOVE_CONFLICTS_PRIORITY` | MOVE_RESOLVE | — | 723–725 | `fn resolve_move_conflicts_with_priority(view:&GameState,commands:&mut[String],priority_ids:&BTreeSet<i32>,)` | `d324b35945e4…` |
| `REWRITE_MOVE_CONFLICTS_FORBIDDEN` | MOVE_RESOLVE | — | 726–780 | `fn resolve_move_conflicts_with_priority_and_forbidden(view:&GameState,commands:&mut[String],priority_ids:&BTreeSet<i32>,forbidden_for_non_priority:&BTreeSet<Cell>,)` | `1b2b1997dd5c…` |
| `OPENING_ENSURE` | OPENING_INITIALIZE | EQUIP_FOR_TRAIN | 796–804 | `fn ensure_opening(&mut self,view:&GameState)` | `5dab94b16d58…` |
| `MODE_CHOOSE_SECOND_TROLL` | MODE_SELECT | EQUIP_FOR_TRAIN | 865–898 | `fn choose_second_troll(view:&GameState,policy:YamoOpeningPolicy)->OpeningObjective` | `ece560f265e4…` |
| `TRAIN_DEADLINE_ENFORCE` | TRAIN_DEADLINE | EQUIP_FOR_TRAIN | 914–941 | `fn enforce_training_deadline(&mut self,view:&GameState)` | `2a7cd3ab6d97…` |
| `GEN_BANK_CANDIDATES_YAMO` | CANDIDATE_GENERATE | BANK | 947–955 | `fn bank_candidates(view:&GameState,unit:&Unit)->Vec<Candidate>` | `ebca61f58a5a…` |
| `FORCED_UNIQUE_DOOR_CLEAR` | FORCED_REPLACEMENT | UNBLOCK_UNIQUE_DOOR | 978–1093 | `fn force_unique_door_clear(&self,view:&GameState,candidates:&mut BTreeMap<i32,Vec<Candidate>>,)` | `331b1c0c1fb7…` |
| `STATE_RECONCILE_REGENERATION` | STATE_RECONCILE | REGENERATE_CARRIED_FRUIT | 1094–1111 | `fn reconcile_regeneration_commitments(&mut self,view:&GameState)` | `3274fefe6cc2…` |
| `COMMIT_REMEMBER_REGENERATION` | COMMITMENT_UPDATE | REGENERATE_CARRIED_FRUIT | 1112–1127 | `fn remember_selected_regeneration(&mut self,commands:&[String])` | `2c24b38c25cf…` |
| `GEN_YAMO_CHOP_CANDIDATES` | CANDIDATE_GENERATE | CHOP_WOOD | 1128–1166 | `fn yamo_chop_candidates(view:&GameState,unit:&Unit,type_to_cut:Option<PlantKind>,opponent_eta_penalty:i32,)->Vec<Candidate>` | `66f0c54cb90b…` |
| `GEN_MAIN_CANDIDATES` | CANDIDATE_GENERATE | — | 1167–1200 | `fn main_candidates(view:&GameState,unit:&Unit,type_to_cut:Option<PlantKind>,idle_regeneration:bool,safe_regeneration:bool,opponent_eta_penalty:i32,)->Vec<Candidate>` | `77a0d7829ffa…` |
| `EMIT_MAIN` | EMIT | — | 1458–1476 | `fn main()` | `81d38e4da7af…` |
