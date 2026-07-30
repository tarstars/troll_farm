# OWNER-GOAL-20260730 — Re-scope the project goal to mature score 25.40

**Status:** `accepted`  
**Review state:** `proposed`  
**Decision date:** 2026-07-30  
**Scope:** Project objective and completion rule for the Legend practice ladder.

## Question

What score target should govern the project after passive maturity and all eight current-architecture routes are closed?

## Decision

Primary goal becomes mature score ≥25.40 with 24.70 as an interim checkpoint; rank ≤3 is superseded.

## Decisive evidence

- **primary_target**: mature score ≥25.40  
  Population: Legend practice-ladder goal  
  Evidence: `docs/STATE.md` (lines 24-43) [public_source_statement]
- **interim_target**: 24.70 interim checkpoint  
  Population: yamo source-design score checkpoint  
  Evidence: `docs/STATE.md` (lines 24-43) [public_source_statement]
- **architectural_demonstration**: 25 Legend agents at ranks 7–54 use the exact two-worker roster  
  Population: 25 Legend agents in the cited ladder census  
  Evidence: `docs/STATE.md` (lines 24-43) [observational_audit]

## Attempts

- rank≤3 goal
- maturity re-baselining
- owner goal re-scope

## What this does not prove

- 25.40 is easy.
- A2 is required to reach the target.
- Rank is irrelevant as an observational metric.

## Limitations and counterevidence

- The target is a governance choice informed by current ladder evidence and may be superseded by a later owner decision.


## Relations

- `supersedes` → `external:GOAL-RANK-3`
- `narrows` → `external:PROJECT-COMPLETION`

## Reopening conditions

- An explicit owner decision citing new target evidence.

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
    "rank≤3 goal",
    "maturity re-baselining",
    "owner goal re-scope"
  ],
  "claims_ladder_effect": false,
  "conclusion": "Primary goal becomes mature score ≥25.40 with 24.70 as an interim checkpoint; rank ≤3 is superseded.",
  "constraint_projection": {
    "bullet": "Owner goal re-scope: primary target is mature score ≥25.40, interim 24.70, with mature read plus later confirmation; rank≤3 is superseded. The target is architecturally grounded by 25 Legend agents at ranks 7–54 using the exact two-worker roster. [owner decision 2026-07-30]",
    "section": "Governance",
    "source": {
      "locator": "lines 24-43",
      "path": "docs/STATE.md"
    }
  },
  "cost": {
    "actual": "owner decision after evidence synthesis",
    "class": "low",
    "compute": "none"
  },
  "decision_date": "2026-07-30",
  "decisive_claims": [
    {
      "binding": true,
      "display": "mature score ≥25.40",
      "evidence_strength": "public_source_statement",
      "name": "primary_target",
      "population": "Legend practice-ladder goal",
      "source": {
        "locator": "lines 24-43",
        "path": "docs/STATE.md"
      }
    },
    {
      "binding": true,
      "display": "24.70 interim checkpoint",
      "evidence_strength": "public_source_statement",
      "name": "interim_target",
      "population": "yamo source-design score checkpoint",
      "source": {
        "locator": "lines 24-43",
        "path": "docs/STATE.md"
      }
    },
    {
      "binding": true,
      "display": "25 Legend agents at ranks 7–54 use the exact two-worker roster",
      "evidence_strength": "observational_audit",
      "name": "architectural_demonstration",
      "population": "25 Legend agents in the cited ladder census",
      "source": {
        "locator": "lines 24-43",
        "path": "docs/STATE.md"
      }
    }
  ],
  "discussions": [],
  "does_not_prove": [
    "25.40 is easy.",
    "A2 is required to reach the target.",
    "Rank is irrelevant as an observational metric."
  ],
  "id": "OWNER-GOAL-20260730",
  "kind": "governance_decision",
  "limitations": [
    "The target is a governance choice informed by current ladder evidence and may be superseded by a later owner decision."
  ],
  "primary_evidence_strength": "public_source_statement",
  "question": "What score target should govern the project after passive maturity and all eight current-architecture routes are closed?",
  "relations": [
    {
      "target": "external:GOAL-RANK-3",
      "type": "supersedes"
    },
    {
      "target": "external:PROJECT-COMPLETION",
      "type": "narrows"
    }
  ],
  "reopening_conditions": [
    "An explicit owner decision citing new target evidence."
  ],
  "schema_version": 1,
  "scope": "Project objective and completion rule for the Legend practice ladder.",
  "status": "accepted",
  "textual_evidence": [
    {
      "claim": "Completion requires a mature read plus a later confirmation, never a single spike.",
      "source": {
        "locator": "lines 24-43",
        "path": "docs/STATE.md"
      }
    }
  ],
  "title": "Re-scope the project goal to mature score 25.40"
}
END-DECISION-EVIDENCE-JSON -->
