---
name: erp-devops-review
description: Review ERP deployment readiness, environment configuration, observability, release safety, backup/rollback posture, and operator friction for this repository. Use when the user asks about 运维, 部署, 发布准备, 环境配置, 配置安全, 日志监控, 回滚方案, CI/CD, startup failures, or overall operational readiness for the ERP system.
---

# ERP DevOps Review

## Overview

Audit the repo from an operator's point of view. Focus on whether this ERP can be built, configured, deployed, monitored, rolled back, and handed off safely.

Keep the review read-only unless the user explicitly asks for fixes.

## Workflow

### 1. Establish the deployment surface

Inspect only the files needed to understand runtime and release flow:

- Root docs that describe build, startup, release, or environment handling
- Backend runtime config such as `application.yml`, profile files, Redis/MySQL settings, Quartz, upload path settings
- Frontend build and deploy config
- SQL migration and initialization layout
- CI/CD, scripts, hooks, and release helpers when present

Summarize:

- What must be deployed
- What stateful dependencies exist
- Which steps are manual vs automated

### 2. Check six operational dimensions

Review the repo against these dimensions:

1. Build and startup
2. Environment and secret management
3. Database migration and data safety
4. Observability and diagnostics
5. Backup, rollback, and release safety
6. Operator and onboarding friction

For each dimension, classify as:

- `ready`
- `partial`
- `fragile`
- `missing`

### 3. Build and startup

Check whether a new operator can answer:

- Which command builds backend and frontend
- Which JDK, Node, Maven, database, Redis versions are required
- Which profiles or env vars are required to boot
- Which module is the runtime entrypoint
- What the first failure signals look like

Flag:

- Missing startup docs
- Hidden machine-specific assumptions
- Hardcoded local paths
- Startup steps split across too many places

### 4. Environment and secret management

Check whether secrets and environment-specific values are separated cleanly from code.

Look for:

- JWT secrets
- Redis/MySQL credentials
- upload paths
- callback URLs
- monitoring credentials
- any hardcoded internal IP, path, token, or password

Flag:

- weak defaults
- fail-open config
- missing production override strategy
- config duplicated across files with drift risk

### 5. Database migration and data safety

Check:

- Whether schema changes are additive and traceable
- Whether SQL file naming is consistent enough for operators
- Whether seed, hotfix, migration, and one-off repair scripts are clearly separated
- Whether rollback or recovery steps are documented

Flag:

- ad hoc SQL sprawl
- destructive scripts without guardrails
- unclear migration order
- data fixes mixed with schema migration

### 6. Observability and diagnostics

Check whether operators can quickly answer:

- Did startup succeed
- Why did login fail
- Why did a background job fail
- Which request hit which error
- Which business flow is timing out or breaking

Review:

- request IDs
- structured logging or at least usable logging
- health endpoints
- error messages
- scheduler visibility
- audit log or release traceability

Flag:

- silent failure paths
- missing health checks
- poor diagnostics
- no operator-facing troubleshooting path

### 7. Backup, rollback, and release safety

Check whether a real release can be reversed safely.

Look for:

- backup guidance
- database snapshot expectations
- rollback notes
- staged migration safety
- release checklist or smoke checklist

Flag:

- one-way schema risk
- no backup-before-change ritual
- no post-release verification path
- no owner handoff for incidents

### 8. Operator friction

Estimate the friction for a new engineer or operator.

Focus on:

- number of setup steps
- clarity of sequencing
- docs drift
- local-only tribal knowledge
- number of places to inspect during failure

Use simple language such as:

- `low friction`
- `moderate friction`
- `high friction`

### 9. Output format

Return four sections in this order:

1. `Operational verdict`
2. `Findings`
3. `Readiness table`
4. `Next-step plan`

For findings:

- Put the highest-risk issues first
- Use file references
- Separate `confirmed`, `likely`, and `unknown`

### 10. Readiness table

Use a compact table like:

| Dimension | Status | Notes |
| --- | --- | --- |
| Build/startup | partial | Backend compile path exists, but operator bootstrap docs are fragmented |

### 11. Next-step plan

End with a short staged plan:

1. Stabilize now
2. Remove operator risk
3. Automate later

## Project-specific heuristics

- Prefer mechanical release safety over markdown-only governance
- Treat SQL layout drift as an operational problem, not just a code-style problem
- Treat missing tests for startup, migration, and approval-critical flows as release blockers
- For this ERP, pay extra attention to MySQL, Redis, scheduled jobs, upload paths, and factory-specific configuration drift

