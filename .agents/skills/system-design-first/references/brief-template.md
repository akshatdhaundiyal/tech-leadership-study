# Brief template and examples

Two forms: the compact **L1 design check** that lives inline before the
implementation, and the full **L2/L3 design brief**. Both exist to make the
system view of a feature explicit and reviewable; neither replaces doing the
task.

## L1 design check (inline, 3-7 lines)

```
Design check (L1)
Touches: <components / files / tables>
Load: <the number it rides on and where it came from>
Risk: <the one thing that can bite> → <mitigation>
Reuse: <existing primitive used instead of a new one>
```

Example — "add a `department` filter to the employee list":

```
Design check (L1)
Touches: GET /api/employees (filters), EmployeeList query key, URL search params.
Load: largest tenant 12k employees (DB count); list is paginated by 50; ~5 rps peak on this endpoint.
Risk: filtering in SQL on `department_id` without an index → seq scan on 12k rows per request; fine today, add a composite index (tenant_id, department_id) since the column is already indexed alone for other screens — cheap now, painful at 100k.
Reuse: existing `useListFilters` keeps the filter in the URL; add the key to the query key so the cache does not serve a stale list.
```

Then implement.

## L2 design brief — full example

Task as given: *"Add CSV export of the employees report. Users click
'Export' and get a file. Some tenants are big."*

```markdown
# Design brief: Employees report CSV export

**Depth:** L2 · **Status:** proposal · **Author's intent:** sync endpoint that streams a CSV, button in the report toolbar (from ticket HR-412 and the stub in `reports/export.py`).

## 1. Scope
Functional: user with `reports:read` exports the current report view (same filters) as CSV; file contains the visible columns; UTF-8 with BOM so Excel opens Cyrillic correctly.
Non-functional (inferred): p95 "file ready" < 10 s for tenants under 20k rows, minutes acceptable for the largest; export must not degrade the report page for other users; no PII beyond what the report already shows; audit who exported what.
Out of scope: XLSX, scheduled exports, column selection.
Assumptions: exports are rare (a few per tenant per week); the largest tenant has ~250k rows (DB count); report query already exists and is indexed.

## 2. Estimates
| Metric | Now | +12 months | Source |
| --- | --- | --- | --- |
| Exports / day | ~50 | ~200 | assumed from 300 tenants × weekly |
| Rows per export | median 2k, max 250k | max 500k | DB counts |
| File size | median 400 KB, max 60 MB | 120 MB | ~250 B/row |
Conclusion: throughput is negligible; the problem is the single big export — 250k rows takes tens of seconds and 60 MB in memory, which is too long for a request and risks a worker-timeout. Small exports can stay synchronous.

## 3. Current design (as-is)
`ReportPage → GET /api/reports/employees?filters → ReportService.query() → Postgres (indexed view)`.
(If the user later asks for diagrams, they go to `docs/design/2026-11-05-employees-csv-export/`; see `visualization.md`.)
Report query is paginated (cursor, 100/page). No job runner for user-facing work; a Celery worker exists for emails (`tasks/email.py`). Object storage adapter exists (`storage/s3.py`) with pre-signed URL support. `reports/export.py` has a stub that builds the whole CSV in memory.
Inherited limits: HTTP timeout 30 s at the proxy; worker memory 512 MB.

## 4. Target design (to-be)
Hybrid: sync streaming for small exports, async job for large ones (the **export / report generation** shape).

ReportPage → POST /api/reports/employees/export {filters}
  ├─ rows ≤ 20k: stream CSV in the response (chunked), reusing the cursor query → done
  └─ rows > 20k: create `report_exports` row (status=queued) → enqueue job → 202 {export_id}
       worker: stream query by cursor → write CSV to object storage in chunks → status=ready, url
ReportPage polls GET /api/reports/exports/{id} every 3 s (SSE deferred) → shows "Download" (signed URL, 1 h expiry).

API contract: POST returns either `200 text/csv` or `202 {export_id}`; GET export returns `{status: queued|running|ready|failed, row_count, url?, error?}`.
Data model: `report_exports(id ulid pk, tenant_id, user_id, filters jsonb, status, row_count, object_key, created_at, finished_at)`; index `(tenant_id, user_id, created_at desc)`; retention: delete rows and objects after 7 days (daily cleanup task).
Pattern choices: async job — because a 250k-row export exceeds the 30 s proxy timeout and the request memory budget; rejected "raise the timeout" because it blocks a web worker for a minute and still fails at 500k. Streaming by cursor — because it keeps memory flat; rejected `fetchall` in the stub. Object storage + signed URL — because files should not go through the API and the user may download later; rejected "store in DB". Count threshold 20k — because that is ~5 s with the measured 4k rows/s; make it a config value.
Canonical analogy: export / report generation (patterns.md §10).

## 5. Risks and deep dives
1. Double click → two jobs for the same filters → dedupe by `(tenant_id, user_id, hash(filters))` with status in (queued, running); return the existing export (needed now).
2. Worker dies mid-export → job stays `running` forever → lease with heartbeat; cleanup marks stale `running` > 15 min as failed and requeues once (before launch).
3. Report query drifts from export query → both use `ReportService.iter_rows(filters)` so columns and filters cannot diverge (now).
4. Big tenant exports during the 9:00 peak → the job runs on the email worker pool and competes with emails → separate queue `exports` with concurrency 2 (before launch).
5. PII in object storage → objects keyed by ulid, private bucket, signed URLs 1 h, 7-day lifecycle rule (now).

## 6. Rollout, migration, observability
Feature flag `reports.export`; no data migration beyond the new table. SLI: share of exports reaching `ready` within 60 s; alert on any export older than 15 min not finished; log export id, tenant, row count, duration. Dashboard: exports/day, p95 duration, failures.

## 7. Open questions for the author
- Should a user be allowed only one running export at a time, or one per filter set?
- Keep files 7 days, or until downloaded?
- Draw the architecture? 1 — terminal diagram · 2 — plus design folder · 3 — no

## 8. Implementation plan
1. `ReportService.iter_rows(filters)` cursor iterator + CSV writer that streams (unit test on a 1k-row fixture, memory flat).
2. `report_exports` table + migration; repository with dedupe lookup.
3. POST endpoint: sync path (≤ 20k) with streaming response.
4. Export job on a dedicated `exports` queue; object storage upload; status transitions as conditional updates.
5. GET status endpoint + signed URL; cleanup task.
6. UI: Export button → spinner → download link; polling hook with backoff; error state.
7. Flag, metrics, dashboard, alert.
```

The brief ends with the visualization offer (SKILL.md, Step 6). Only if the
user picks 1 or 2 does the agent draw the terminal diagrams (example in
`visualization.md`) and, for 2, save the brief as `README.md` in a design
folder with the same diagrams as Mermaid.

The brief is about a page. Everything in it is tied to a number or to a file
that exists; each pattern has a reason and a rejected alternative; the
author's design (sync streaming) was kept for the common case rather than
replaced.

## L3 additions

For a subsystem (new service, real-time channel, event pipeline) add:

- **Alternatives considered** as a short table: option · pros · cons ·
  why not.
- **Deep dive per component**: the design of the risky parts at the level of
  data structures and sequences (e.g. message ordering per room, reconnect
  resume protocol, exactly-once sink).
- **Migration path**: expand → migrate → contract steps with the dual-write or
  backfill window and the rollback point.
- **Capacity plan**: the signal and threshold that triggers each next step.
- **Operational runbook stub**: how to pause, replay, backfill, and what the
  on-call sees.
