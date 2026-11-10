---
name: system-design-first
description: >-
  System-design pass before building a feature with its own data flow:
  requirements, load estimates, as-is vs to-be, pattern trade-offs, and a short
  design brief with the "why". Use when a task adds a service, an endpoint with
  storage, an integration, a real-time channel, an event pipeline, a scheduled
  job or a data-model change; when the user asks how to design or scale
  something, to explain or diagram an architecture; or when load, latency,
  consistency, fan-out, queues or caching decide the approach. Copy edits,
  renames, styling and local bug fixes go straight to the code.
license: MIT
metadata:
  version: "0.2.1"
  author: Baukaalm
  homepage: https://github.com/Baukaalm/system-design-first
---

# System design first

Most tickets describe *what* to build and hide the questions that decide
whether it survives contact with production: how many users, how often, how
much data, what happens when a dependency is slow, who owns the truth when two
writers race. This skill makes those questions explicit **before** code is
written, in a form the task's author can read and push back on.

The pass is: scope → estimate → high-level design → deep dive → wrap-up,
applied to real work: there is an existing codebase, an author with intent,
and a budget. The goal is a crisp picture of the feature from the system's
point of view.

Reply in the language the user writes in. The brief is for them, not for you.

## 1. Gauge the depth first

Over-designing a typo fix is as wrong as under-designing a payment flow. Pick
the level, say it in one line, and spend accordingly.

| Level | Typical task | What you produce |
| --- | --- | --- |
| **L0 – trivial** | Copy change, rename, style tweak, obvious bug with a local fix | Nothing extra. One sentence at most if a hidden risk exists ("this label is also cached in the CDN for 24h"). Then just do the task. |
| **L1 – local change** | New field, new filter, small endpoint change, a hook, a query tweak | A 3-7 line **design check** inline: what it touches, the load it rides on, the one thing that could bite (N+1, cache invalidation, pagination, idempotency). Then implement. |
| **L2 – feature** | New screen with data flow, new endpoint + storage, notifications, search, export, integration with a third party | The **design brief** (section 4), about one page. Then implement per the brief. |
| **L3 – subsystem** | New service, real-time channel, event pipeline, multi-tenant data model, migration of a hot path, anything with "scale" in the ticket | Full brief plus a **deep dive** per risky component, alternatives considered, migration path, what to measure after launch. |

Signals that push a task *up* a level: user-facing latency, concurrent writers,
fan-out (one event → many recipients), unbounded growth of a table or list,
third-party rate limits, money, PII, anything that runs on a schedule, or
"temporary" solutions that will obviously stay. Signals that push it *down*:
internal tooling with a handful of users, data that fits in memory forever,
feature-flagged experiments with a kill switch.

If the user explicitly asks for a design review or a deeper analysis, treat it
as L3 regardless of size.

## 2. The pass, step by step

Work through these in order. For L1 compress them into a few lines; for L2/L3
each step becomes a section of the brief. `references/framework.md` has the
question checklists for each step; read it the first time you run an L2+ pass
in a session.

### Step 1 — Understand and scope

- Restate the feature in one paragraph as the *system* sees it: actors,
  triggers, inputs, outputs, side effects.
- Separate **functional** requirements (what it does) from **non-functional**
  ones (how well: scale, latency, availability, consistency, durability,
  security, cost, operability). Tickets almost never state the second kind; infer
  them from the product context and say they are inferred.
- Write down what is **out of scope**, so the brief does not silently grow.
- Collect the **author's intent**: ticket text, PR description, comments,
  linked designs, existing ADRs, how similar features were built in this repo.
  The author usually has a design in their head; surface it rather than
  replacing it.
- Ask the user only questions that change the design materially (e.g. "must
  this be visible within a second, or is a minute fine?"). For everything else,
  state an assumption and move on; assumptions go into the brief.

### Step 2 — Estimate

Numbers turn opinions into decisions. Do a back-of-the-envelope estimate even
when the ticket has none; `references/estimation.md` holds the reference
numbers (latency ladder, powers of two, availability nines, per-node
capacities) and worked examples.

- Users / tenants → daily active → actions per day → **average and peak QPS**
  (peak is usually 2-5× average, more for bursty flows like "everyone opens
  the app at 9:00").
- **Read/write ratio**, payload size → storage per day / year, bandwidth.
- Growth: what is the number in 12 months if the product succeeds?
- Where real numbers exist (analytics, DB row counts, existing dashboards,
  config limits), use them and cite the source; otherwise give a range and mark
  it as an assumption.

Then use the numbers to **kill patterns**, not just to justify them: "at 30
writes/s a Postgres table with an index is fine; a queue is not needed for
throughput, only if we want retries and decoupling from the email provider."

### Step 3 — Map the current design (as-is)

Read the code before describing it. Name real files, modules, tables,
endpoints, jobs, caches, queues. Do not invent components.

- Which components does the feature touch? Draw the data flow in a short
  text diagram (`client → BFF → service → Postgres`, `event → queue → worker`).
- Where is the state and who owns it (DB, cache, client store, URL)?
- What existing primitives can be reused (an outbox table, a job runner, a
  query cache, a WebSocket hub, a shared `Pagination` component)?
- Hot paths, known bottlenecks, existing SPOFs, current limits (rate limits,
  page sizes, timeouts) that the feature inherits.
- For a frontend task the as-is is still a system: data-fetching layer, cache
  policy, bundle boundaries, real-time transport — see
  `references/frontend.md`.

### Step 4 — Propose the target design (to-be)

Start from the author's intent. If it is sound, say so and tighten it; if it
conflicts with the numbers or with a well-known failure mode, show the
conflict with its consequence and offer the smallest change that fixes it. The
author decides; your job is to make the trade-off visible.

- High-level design as a text diagram, plus the **API contract** (endpoints /
  events / messages with shapes) and the **data model** (tables, keys,
  indexes, retention).
- For every non-trivial choice name the **pattern** and the **alternative** you
  rejected, with the reason tied to Step 2's numbers. `references/patterns.md`
  is the catalog: scaling, caching, async/queues, data stores and consistency,
  API styles and real-time transport, rate limiting, ID generation,
  reliability, observability — each with "use when / avoid when / trade-offs".
- Map the feature to a **canonical system** when one fits ("this is a
  notification system: queue + per-channel workers + dedup", "this is news-feed
  fan-out", "this is a rate limiter"). The catalog's last section lists the
  canonical shapes and their standard building blocks. The analogy gives the
  reader a known reference point and a checklist of what such systems usually
  need.
- Prefer the repo's existing primitives and the simplest design that meets the
  numbers *with headroom*. Say explicitly which upgrades are deferred and what
  signal would trigger them ("add a read replica when p95 of this query passes
  200 ms or the table passes 50M rows").

### Step 5 — Deep dive on what can break

For L2 pick the one or two riskiest parts; for L3 go through all of them.
Standard questions, in rough order of how often they bite:

1. **Concurrency & idempotency** — double submits, retries, two writers, at-least-once delivery. Where is the idempotency key? What is the unique constraint?
2. **Consistency** — who reads stale data and for how long; is that acceptable; cache invalidation path; read-your-own-writes.
3. **Failure of a dependency** — provider down, queue lagging, remote module failing to load. Timeouts, retries with jitter, circuit breaker, graceful degradation, what the user sees.
4. **Hot spots** — hot keys, celebrity tenants, unbounded lists, N+1, full-table scans, missing index, thundering herd on cache expiry.
5. **Growth** — the table/list/queue that grows without bound; retention, archival, pagination (cursor over offset), partitioning.
6. **Migration & rollout** — backfill, dual-write period, feature flag, rollback path, backward-compatible contract changes.
7. **Security & privacy** — authz at the data level (tenant isolation), PII in logs/queues, rate limiting on public endpoints, input validation.
8. **Observability** — which metric proves it works (SLI), which alert fires when it does not, what to log for debugging a single request.

### Step 6 — Wrap up, offer the visualization

Diagrams cost tokens, so they are **opt-in**. The brief itself uses only
one-line text flows (`client → API → Postgres`).

For L2 and L3, end the brief with one question, together with the open
questions, in the user's language:

> Draw the architecture? **1** — as-is / to-be diagram in the terminal ·
> **2** — plus a design folder (Mermaid + `architecture.html`) · **3** — no

- Draw only after the user picks 1 or 2, following
  `references/visualization.md`. Do not wait for the answer to start
  implementing; if the user moves on without answering, it is a "no".
- Skip the question and draw right away only when the user already asked for
  a diagram, a picture, a visualization or the design folder.
- If nobody can answer (a non-interactive run, CI, an eval), do not draw and
  do not ask; mention in one line that diagrams are available on request.
- Never offer it for L0 or L1.

Produce the brief (next section), then **continue with the task**: implement
according to the brief, keep the brief in the PR / MR description as well,
and list open questions for the author rather than deciding them silently.

## 3. Judgment rules

- **Numbers before patterns.** Never recommend Kafka, sharding, CQRS, a
  dedicated cache cluster or microservices without an estimate that needs
  them. Simplicity is a feature; complexity must earn its place.
- **Explain, do not lecture.** Each recommendation carries a one-sentence
  "because" the author can verify. Analogies to canonical systems are
  welcome; buzzword lists are not.
- **Respect the author's design.** Present disagreements as "X will cause Y
  at Z load; the cheapest fix is W". If they still prefer their way, implement
  their way and note the risk in the brief.
- **Existing code is evidence.** Read it. A brief that describes components
  that do not exist is worse than no brief.
- **Separate must-have from nice-to-have.** Mark each recommendation as
  "needed now", "needed before launch" or "needed at ~N users".
- **Frontend counts.** Client caching, pagination, optimistic updates,
  real-time transport, bundle boundaries and failure isolation are system
  design; `references/frontend.md` covers the client-side version of every
  step.
- **Stay in the user's language and vocabulary.** Translate pattern names if
  the team does; keep the English term in parentheses the first time.

## 4. The design brief

Use this structure for L2 and L3. Keep headings; drop a section only when it
is genuinely empty and say so in one line. Target one page for L2.
`references/brief-template.md` has a filled example and the compact L1 form.

```markdown
# Design brief: <feature>

**Depth:** L2 · **Status:** proposal · **Author's intent:** <one line>

## 1. Scope
Functional: ...
Non-functional (inferred unless stated): scale · latency · availability · consistency · security · cost
Out of scope: ...
Assumptions: ...

## 2. Estimates
| Metric | Now | +12 months | Source |
| --- | --- | --- | --- |
| DAU / tenants | | | |
| Peak QPS (read / write) | | | |
| Storage growth | | | |
Conclusion: <what the numbers allow / forbid>

## 3. Current design (as-is)
<one-line text flow> · state ownership · reusable primitives · inherited limits
Files: ...

## 4. Target design (to-be)
<one-line text flow> · API contract · data model · canonical-system analogy
Pattern choices: <pattern> — because <reason>; rejected <alternative> because <reason>.

## 5. Risks and deep dives
1. <risk> → mitigation (needed now / before launch / at N)
...

## 6. Rollout, migration, observability
Flags, backfill, rollback · SLI + alert · what to log

## 7. Open questions for the author
- ...
- Draw the architecture? 1 — terminal diagram · 2 — plus design folder · 3 — no

## 8. Implementation plan
Ordered steps, each small enough to review.
```

## 5. References — what to read when

| File | Read when |
| --- | --- |
| `references/framework.md` | First L2+ pass in a session: question checklists per step, NFR list, how to extract the author's intent, analysis anti-patterns. |
| `references/estimation.md` | Any time you need a number: latency ladder, nines, per-node capacities, QPS/storage math, worked examples. |
| `references/patterns.md` | Choosing or justifying a pattern; mapping a feature to a canonical system (chat, feed, notifications, search autocomplete, file sync, rate limiter, KV store, ID generator, payments, ...). Has a table of contents. |
| `references/frontend.md` | The task is a UI / SPA / micro-frontend change: data-fetching cache, pagination, real-time, bundle boundaries, failure isolation, client-side numbers. |
| `references/brief-template.md` | Writing the brief: full L2 example and the compact L1 inline form. |
| `references/visualization.md` | Only after the user asked for diagrams (Step 6). Drawing them: terminal box-diagram rules, Mermaid conventions, design-folder layout, how to fill `assets/architecture.html`. |
