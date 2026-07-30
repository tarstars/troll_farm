# OWNER-ARENA-20260730 — Standing Arena authorization with evidence gates

**Status:** `authorized`  
**Review state:** `proposed`  
**Decision date:** 2026-07-30  
**Scope:** Live ladder mutation by the single arena controller under the promotion runbook.

## Question

May the arena controller submit qualified candidates without requesting per-candidate owner permission?

## Decision

Yes. The permission gate is lifted for candidates that pass frozen qualification and promotion checks; evidence, notification, logging, and serialization requirements remain binding.

## Decisive evidence

- **noise_band**: expected gain must exceed ±0.5–1 rating noise band  
  Population: qualified candidate promotion decisions  
  Evidence: `docs/STATE.md` (lines 47-69) [public_source_statement]
- **controller_count**: exactly one arena controller  
  Population: all live submission cycles  
  Evidence: `docs/STATE.md` (lines 47-69) [public_source_statement]

## Attempts

- per-candidate permission gate
- standing authorization

## What this does not prove

- Any current candidate is qualified.
- The promotion runbook may be shortened.
- Peer agents may submit.
- Arena evidence requirements are waived.

## Limitations and counterevidence

- Authorization is operational and can be reassigned or revoked by the owner.
- The policy does not authorize more than one cycle in flight.


## Relations

- `supersedes` → `external:PER-CANDIDATE-PERMISSION`
- `constrains` → `external:ARENA-CONTROLLER`

## Reopening conditions

- An explicit owner policy change.

## Discussions

- None.

## Canonical machine block

The JSON block below is part of this human-reviewed Markdown record. Generated YAML and indexes are projections of this block.

<!-- DECISION-EVIDENCE-JSON
{
  "acceptance": {
    "author": "chatgpt_1",
    "reviewer": "local_codex_1",
    "state": "proposed"
  },
  "attempts": [
    "per-candidate permission gate",
    "standing authorization"
  ],
  "claims_ladder_effect": false,
  "conclusion": "Yes. The permission gate is lifted for candidates that pass frozen qualification and promotion checks; evidence, notification, logging, and serialization requirements remain binding.",
  "constraint_projection": {
    "bullet": "Standing Arena authorization: the single arena controller may submit candidates that pass frozen qualification and the full promotion runbook without per-candidate permission. Expected gain must exceed the ±0.5–1 rating noise band; owner notification, serialization, and complete logging remain mandatory. [owner decision 2026-07-30]",
    "section": "Arena policy",
    "source": {
      "locator": "lines 47-69",
      "path": "docs/STATE.md"
    }
  },
  "cost": {
    "actual": "owner policy decision and integrator scope record",
    "class": "low",
    "compute": "none"
  },
  "decision_date": "2026-07-30",
  "decisive_claims": [
    {
      "binding": true,
      "display": "expected gain must exceed ±0.5–1 rating noise band",
      "evidence_strength": "public_source_statement",
      "name": "noise_band",
      "population": "qualified candidate promotion decisions",
      "source": {
        "locator": "lines 47-69",
        "path": "docs/STATE.md"
      }
    },
    {
      "binding": true,
      "display": "exactly one arena controller",
      "evidence_strength": "public_source_statement",
      "name": "controller_count",
      "population": "all live submission cycles",
      "source": {
        "locator": "lines 47-69",
        "path": "docs/STATE.md"
      }
    }
  ],
  "discussions": [],
  "does_not_prove": [
    "Any current candidate is qualified.",
    "The promotion runbook may be shortened.",
    "Peer agents may submit.",
    "Arena evidence requirements are waived."
  ],
  "id": "OWNER-ARENA-20260730",
  "kind": "operational_policy",
  "limitations": [
    "Authorization is operational and can be reassigned or revoked by the owner.",
    "The policy does not authorize more than one cycle in flight."
  ],
  "primary_evidence_strength": "public_source_statement",
  "question": "May the arena controller submit qualified candidates without requesting per-candidate owner permission?",
  "relations": [
    {
      "target": "external:PER-CANDIDATE-PERMISSION",
      "type": "supersedes"
    },
    {
      "target": "external:ARENA-CONTROLLER",
      "type": "constrains"
    }
  ],
  "reopening_conditions": [
    "An explicit owner policy change."
  ],
  "schema_version": 1,
  "scope": "Live ladder mutation by the single arena controller under the promotion runbook.",
  "status": "authorized",
  "textual_evidence": [
    {
      "claim": "Qualified candidates may be submitted without asking; unqualified live experiments must be surfaced before acting.",
      "source": {
        "locator": "lines 47-69",
        "path": "docs/STATE.md"
      }
    }
  ],
  "title": "Standing Arena authorization with evidence gates"
}
END-DECISION-EVIDENCE-JSON -->
