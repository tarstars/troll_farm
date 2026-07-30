# Decision-evidence index — work description and review proposal

Prepared UTC: 2026-07-30T06:53:00Z  
Author: `chatgpt_1`  
Integrator: `claude_1`  
Review branch: `agent/chatgpt_1-evidence-review`  
Shared-state head inspected: `cafebbde6703102b2ed6c9f6e1bda427c42b6904`

## 1. Why this note exists

The user asked for a detailed PDF explaining the complete repository history and, most
importantly, the **proofs behind the decisions made**. During drafting, the user clarified
that the proof layer is more valuable than a polished narrative: reviewers need a transparent
index from each decision to its evidence, counterevidence, scope, corrections, and unresolved
discussion points.

This note describes the work completed so far and proposes a repository-native evidence
architecture for review. It is a design proposal, not a claim that the index already exists.
No shared documentation schema should be adopted until the integrator and peer agents review
the questions in section 8.

## 2. Work completed so far

### 2.1 Repository-history audit

I reconstructed the project story from the following evidence classes:

- early Wood/Bronze/Silver/Gold source, roadmaps, and the 227 KB append-only experiment log;
- referee-derived mechanics and simulator corrections;
- live-source recovery and phase-numbered Legend experiments;
- D-series atlas and both ledger volumes;
- maintenance-era B3/B4 audits;
- `docs/CONSTRAINTS.md`, including corrections and overturned premises;
- H1-H13 hypothesis registry and the integrated independent review;
- iteration-2 N1-N7 backlog and coordination records;
- task records, frozen protocols, result documents, JSON outputs, and public-source references.

The audit was organized into the project’s main scientific arcs: early ladder engineering,
simulator/reality corrections, curriculum learning, official-map substrate repair, persistent
job grammars, D40 teacher construction, recurrent and joint-action search, q6 selectors,
resident-native options, terminal synthesis, maintenance audits, and post-terminal hypotheses.

### 2.2 Reader-facing draft

I generated a local 31-page draft report and rendered every page for visual QA. It contains:

- a chronological project narrative;
- compact coverage of every experiment identifier or tightly coupled repair sequence;
- thematic explanations of the recurring representation, objective, transfer, and
  displacement failures;
- a terminal hypothesis-status matrix.

The draft and rendered pages are **not committed**. They were produced as working artifacts,
not as authoritative repository records.

### 2.3 Main methodological finding

A PDF alone is the wrong primary artifact. It compresses the argument and makes review hard:
readers see the conclusion but cannot reliably navigate from conclusion to protocol, lock,
result JSON, source revision, counterevidence, correction, and reopening rule.

The canonical artifact should therefore be a structured **Decision and Evidence Index**. The
PDF should be generated from that evidence layer as a reader’s view.

## 3. Important cutoff correction

The first report draft used the repository state around
`e38dca7c2f8be923ebfa7d398407db689d253849`. The shared branch then advanced materially to
`cafebbde6703102b2ed6c9f6e1bda427c42b6904`.

The current report draft is therefore stale in several load-bearing places:

- D176a is now **CLOSED-AT-MECHANISM**: incidence 8.50% -> 2.88%, zero de-novo runs and all
  value gates pass, but total value is only +0.045; the oscillation line is permanently closed.
- The owner re-scoped the goal to mature score >=25.40, with 24.70 as an interim checkpoint.
- Architecture-2 is authorized under a five-gate charter and five kill rules.
- Standing Arena authorization changed: the owner permission gate is lifted, while frozen
  qualification, noise-band value, full runbook, logging, and single-controller serialization
  remain binding.
- The 35-item breadth register is now the strategic backlog; N1, N2, and A2-0a are active.
- Repository history rewriting was explicitly declined and closed.

No current-state PDF should be integrated until these changes and any later review feedback are
incorporated. The local draft should be treated only as evidence that the history can be rendered,
not as the report of record.

## 4. Proposed canonical artifact set

### 4.1 Human index

`docs/DECISION-EVIDENCE-INDEX.md`

One row per decision or hypothesis, with:

- id;
- exact question;
- current status;
- scoped conclusion;
- decisive evidence;
- evidence strength;
- counterevidence/caveats;
- correction or supersession links;
- reopening conditions;
- decision-record link;
- open discussion-point count.

The row must expose the decisive number, not merely say “closed by D175a”.

### 4.2 Machine-readable registry

`docs/decision-evidence-index.yaml`

Suggested core schema:

```yaml
- id: D175a
  kind: experiment
  question: Does bounded early planting restore the resident plant-reap economy?
  status: closed
  scope: current-resident
  confidence: high
  decision_date: 2026-07-29
  evidence_strength: controlled_causal_experiment
  conclusion: Early planting alone is harmful for the current resident.
  decisive_evidence:
    - claim: Trigger fidelity
      value: 153/153
      source: data/analysis/.../d175a-result.json
    - claim: Paired margin
      value: -26.44
      interval: [-28.96, -23.92]
      source: data/analysis/.../d175a-result.json
  does_not_prove:
    - Farming is universally harmful.
    - A new harvest-capable architecture cannot farm.
  reopening_conditions:
    - A new architecture jointly changes harvest capability, crop protection, and scheduling.
  discussion: [D175a-Q1]
```

The Markdown index should be generated from or validated against this registry, not maintained
independently by hand.

### 4.3 Individual decision records

`docs/decisions/<id>-<slug>.md`

Each record should include:

1. question;
2. decision and exact scope;
3. preregistered rule, when one exists;
4. mechanism evidence;
5. outcome evidence;
6. argument from evidence to conclusion;
7. what the result proves;
8. what it does not prove;
9. counterevidence and limitations;
10. corrections/supersessions;
11. reopening conditions;
12. direct evidence files, commits, hashes, and JSON paths;
13. linked discussion points.

This is the place where “proof of a decision” lives. The index is navigation, not proof by itself.

### 4.4 Discussion records

`docs/decision-discussions/<decision-id>.md`

Discussion points should be first-class, reviewable objects with stable IDs:

```markdown
## D175a-Q1 — Is displacement fully identified?

- Raised by: <agent>
- Status: open
- Affects: mechanism confidence, not the observed negative value
- Claim under review: The loss is primarily displaced suppression.
- Evidence for: ...
- Evidence against: ...
- Required resolution: decomposition or a suppression-preserving arm
```

Suggested statuses: `open`, `answered`, `accepted`, `rejected`, `superseded`, `out-of-scope`.
A resolved point is retained; it is never deleted.

### 4.5 Evidence hierarchy

Every decisive claim should carry one of these labels:

1. `mechanics_proof` — referee or source-code guarantee;
2. `controlled_causal_experiment` — frozen paired intervention;
3. `prospective_transfer` — held panel or Arena evidence;
4. `observational_audit` — read-only field association;
5. `accounting_model` — conditional bound/stress test;
6. `public_source_statement` — another player’s stated design;
7. `inference_or_hypothesis` — not yet established.

This prevents observational correlations, accounting assumptions, and frozen causal results from
being presented with equal authority.

### 4.6 Decision relations

The registry should support at least:

- `supports`;
- `contradicts`;
- `corrects`;
- `supersedes`;
- `narrows`;
- `opens`;
- `closes`;
- `constrains`;
- `does_not_close`.

Example:

```text
B3.9 --opens--> D174a
D174a --corrects--> B3.9
D174a --constrains--> H1
H1 --closes_for_resident--> four-lever patch
H1 --does_not_close--> Architecture-2
```

Many project conclusions are scoped corrections, not simple true/false statements. The relation
graph must preserve that distinction.

### 4.7 Validation tooling

Proposed tools:

- `cgauto/build_decision_evidence_index.py` — generate Markdown tables and graph extracts;
- `cgauto/check_decision_evidence_index.py` — fail when evidence paths, hashes, IDs, relations,
  statuses, or mandatory scope fields are missing;
- report generator that consumes the same registry and decision records.

Checks should include:

- every closed decision has at least one decisive evidence item;
- every numeric decisive claim points to a file and, where possible, JSON path;
- every invalidated implementation is distinct from scientific closure;
- every correction names the corrected claim;
- every closure states scope and reopening conditions;
- every linked file exists;
- optional source/result hashes match;
- no discussion ID is orphaned;
- generated Markdown is reproducible.

### 4.8 PDF as generated view

The final PDF should contain:

- narrative history;
- experiment explanations grouped into coherent branches;
- summaries generated from the canonical decision records;
- an appendix of open discussion points;
- an evidence manifest and cutoff commit.

It should explicitly state:

> In case of disagreement, the individual decision record and linked frozen artifacts are
> authoritative. The PDF is a generated reader’s view.

## 5. Proposed proof standard for a decision record

A decision record is review-ready only when a reviewer can follow this chain without searching
the whole repository:

```text
question
  -> frozen or stated decision rule
  -> exact intervention / dataset / model
  -> integrity and fidelity checks
  -> decisive measurements
  -> assumptions
  -> inference from measurements to scoped conclusion
  -> counterevidence and limitations
  -> correction/supersession history
  -> reopening rule
  -> raw artifacts and hashes
```

A “proof” here does not mean a mathematical theorem unless the claim is mechanics-derived. It
means a transparent, inspectable justification proportionate to the evidence type.

## 6. Suggested migration plan

### Phase 0 — schema review

Agree on authority, granularity, evidence labels, discussion workflow, and file ownership. Do not
bulk-generate records before this review.

### Phase 1 — pilot records

Create a deliberately heterogeneous pilot set:

- D30 — substrate invalidation;
- D101 — observational architecture diagnosis;
- D161 — resident-substrate dominance decision;
- D169 — positive hindsight envelope;
- D172a — definitive learning closure;
- D175a — controlled harmful mechanism;
- H1 — conditional accounting closure;
- D176a — positive mechanism but immaterial value and mis-specified gates;
- owner goal re-scope — governance decision rather than experiment;
- Arena standing authorization — operational policy decision.

The pilot should prove the schema handles causal experiments, observations, invalidations,
accounting models, corrected gates, owner decisions, and operational policy.

### Phase 2 — validators and generated index

Implement the checker before mass migration. A schema that cannot be mechanically checked will
drift into another prose ledger.

### Phase 3 — incremental migration

Migrate by scientific branch, not by filename glob:

1. early arena and simulator calibration;
2. curriculum and official-map substrate;
3. job grammar and D40;
4. q6 and learning closures;
5. resident-native cycle;
6. maintenance audits;
7. H/N/X/M/E/A2 hypotheses and owner decisions.

### Phase 4 — regenerate complete-history report

Only after the pilot and validator are accepted should the Markdown/PDF history become a generated
consumer of the evidence index.

## 7. Non-goals and safety

This proposal does not:

- rewrite or replace frozen result documents;
- reinterpret D176a’s frozen verdict because two gates were mis-specified;
- convert observational audits into causal proofs;
- make the local 31-page draft authoritative;
- touch resident source, sealed data, raw replay storage, submission tooling, or Arena state;
- change `docs/STATE.md`, `docs/CONSTRAINTS.md`, `docs/BACKLOG.md`, or ledger volumes without an
  integrator-owned task record and explicit write set.

The index should point to existing evidence, not duplicate or silently edit it.

## 8. Questions for peer review

Please review these before implementation:

1. **Authority:** Should YAML be canonical, should individual Markdown decision records be
   canonical, or should both be checked as equivalent projections of a smaller structured core?
2. **Granularity:** One record for every `Dnnn` suffix, or grouped records for inseparable repair
   sequences such as D119-D127? What rule determines grouping?
3. **Coverage:** Should the registry include only scientific decisions, or also owner goal changes,
   Arena policy, storage/history decisions, and programme authorizations?
4. **Evidence taxonomy:** Are the seven evidence-strength labels sufficient and correctly ordered?
5. **Discussion mechanism:** Repository Markdown, GitHub issues, or both? How are stable discussion
   IDs preserved if issues are used?
6. **Mutability:** Are decision records append-only after acceptance, or may wording be corrected
   in place when hashes and correction history are preserved?
7. **Supersession:** How should corrected observational claims such as B3.9 -> D174a appear in the
   index without hiding the historical claim?
8. **Invalidation:** Does the proposed schema clearly distinguish implementation-fidelity
   invalidation, gate-design error, scientific closure, and value immateriality?
9. **Evidence paths:** Should numeric claims require JSON paths, line ranges, or both? How should
   large external/symlinked artifacts be represented?
10. **Migration scope:** Pilot-first incremental migration, or one bulk conversion followed by
    review?
11. **PDF role:** Is a generated PDF still useful once the index exists, and which sections should
    remain narrative rather than generated?
12. **Review ownership:** Who approves a decision record, and what status marks it as accepted by
    the repository rather than merely proposed by one agent?

## 9. Requested disposition

Reviewers may respond per item with:

- `ACCEPT`;
- `ACCEPT WITH CHANGE`;
- `REJECT`;
- `DEFER`;
- `NEEDS EXAMPLE`.

The immediate requested outcome is a reviewed Phase-0 schema and a task record for the pilot set.
No bulk migration or final PDF integration is requested yet.
