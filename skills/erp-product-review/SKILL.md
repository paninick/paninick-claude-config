---
name: erp-product-review
description: Review ERP completion, deviation from plan, scope control, feature closure, roadmap quality, and business priority alignment for this repository. Use when the user asks about 完成度, 偏离度, 规划, 产品评审, 范围控制, 路线图, 是否该继续做某功能, or wants a high-signal project review grounded in repo evidence.
---

# ERP Product Review

## Overview

Review the product reality of the repo, not just the intent in documents. Compare what the plan claims, what the code actually implements, what remains open, and what should happen next.

Keep the work read-only unless the user explicitly asks for plan or document edits.

## Workflow

### 1. Build the three-source truth

Always compare these three sources:

1. Plan documents
2. Current code and pages
3. Audit / handoff / issue trackers

Do not trust any one of them alone.

Primary files usually include:

- `ERP_MASTER_PLAN.md`
- `docs/audit/AUDIT_TRACKER.md`
- `docs/session-handoff.md`
- major controller, service, mapper, page, and SQL locations

### 2. Separate existence from closure

For every major product area, distinguish:

- `planned`
- `implemented`
- `closed`
- `verified`

Rules:

- A page existing is not closure
- A controller existing is not business readiness
- A claim in a plan is not reality
- A fix claim without independent validation is not verified

### 3. Review six product dimensions

Evaluate:

1. Capability coverage
2. Workflow closure
3. Plan drift
4. Priority discipline
5. Risk backlog
6. Roadmap quality

### 4. Capability coverage

Measure breadth first:

- core modules present
- major business objects present
- frontend coverage for backend capability
- approval, traceability, and reporting support

Then state whether the codebase is:

- `narrow but deep`
- `broad but shallow`
- `balanced`

### 5. Workflow closure

Check whether each high-value workflow is actually end-to-end.

Examples:

- sales order to production
- plan to produce job
- purchase to stock in
- quality inspection to release
- approval submit to approve/reject to audit trail

Flag where the repo has:

- CRUD without closure
- approval endpoints without lock/freeze behavior
- data isolation without consistent enforcement
- backend-first or frontend-first drift

### 6. Plan drift

Compare plan claims against code reality.

For each major item, classify:

- `plan says missing, code says present`
- `plan says present, code says partial`
- `plan and code aligned`
- `unknown`

Treat plan drift as a product management problem because it breaks prioritization and trust.

### 7. Priority discipline

Review whether the team is still working on the right thing.

Flag:

- broad feature spread before closure
- open audit/security debt while adding new surface area
- repeated work on low-value UI while critical backend closure is incomplete
- governance overhead that does not reduce delivery risk

### 8. Risk backlog

Use audit and handoff artifacts to identify what still blocks confidence.

Group risks into:

- `release risk`
- `data risk`
- `security risk`
- `execution risk`
- `documentation risk`

When possible, tie each risk to a concrete file or tracker entry.

### 9. Roadmap quality

Assess whether the next plan is likely to succeed.

Good roadmap traits:

- closes open loops before expanding scope
- sequences dependencies clearly
- has verification steps
- has explicit not-in-scope boundaries

Weak roadmap traits:

- mixes new features and repair work
- ignores open audits
- assumes docs are current when they are not
- lacks measurable completion criteria

### 10. Output format

Return five sections in this order:

1. `Verdict`
2. `Findings`
3. `Completion view`
4. `Deviation view`
5. `Recommended roadmap`

### 11. Verdict

Use one short paragraph that answers:

- How complete is the project really
- What kind of shape is it in
- What mode it should enter next

Examples:

- `broad but shallow; move to closure mode`
- `core workflows mostly present; verification lags`

### 12. Findings

Put the most important findings first.

Use severity-minded language, but product-oriented:

- `critical misalignment`
- `high delivery risk`
- `medium drift`
- `low-priority cleanup`

Every finding should point to evidence.

### 13. Completion view

Summarize practical completion by area, for example:

- core master data
- approvals
- production execution
- quality
- finance
- frontend parity
- release readiness

Use plain labels such as:

- `strong`
- `partial`
- `weak`

### 14. Deviation view

Explicitly list where the project has drifted from plan.

Useful patterns:

- plan is stale
- implementation order changed
- documented gap already solved in code
- code changed without updating the plan

### 15. Recommended roadmap

End with a staged roadmap:

1. `stabilize`
2. `verify`
3. `consolidate`
4. `expand`

Each stage should be short and opinionated.

## Project-specific heuristics

- For this ERP, default to valuing closure over breadth
- Open audit items outweigh speculative feature additions
- Approval, factory isolation, SQL migration safety, and testability are product readiness concerns, not just engineering concerns
- If the repo is broad but shallow, recommend closure mode before new module work
- If governance docs are ahead of code or behind code, say so plainly

