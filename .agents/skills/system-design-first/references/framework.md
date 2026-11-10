# The analysis framework

The pass runs in four moves: understand the problem and set scope, propose a
high-level design and get buy-in, deep dive, wrap up. Real work adds two facts
a whiteboard exercise lacks: there is already a system, and there is an author
with intent. This file turns each move into a checklist you can run
against a ticket.

Use it for L2 and L3 passes. For L1, skim the "questions that change the
design" list and move on.

## Move 1 — Understand and scope

### Restate the feature as the system sees it

One paragraph: *who* triggers it (user, cron, webhook, another service), *what*
comes in (shape, size, rate), *what* must come out (response, event, file,
side effect), *where* the result must be visible and *how soon*.

### Functional requirements

- Happy path in 3-5 bullet points.
- Edge cases the ticket implies but does not state (empty list, deleted
  parent, tenant with 50k employees, user with no permission, duplicate
  submit).
- Explicit non-goals: write them, otherwise reviewers add them back later.

### Non-functional requirements (the ones tickets omit)

Go through the list; for each, either take the number from the ticket, infer
it from product context (and mark it inferred) or say "not relevant here".

| NFR | Question to answer |
| --- | --- |
| Scale | How many users / tenants / items now and in 12 months? Peak vs average? |
| Latency | What does the user wait for, and what is "too slow" for that action? Interactive (< 200 ms), page load (< 1-2 s), background (seconds-minutes)? |
| Availability | What happens to the business if this is down for 10 minutes? An hour? |
| Consistency | Can a reader see a stale value? For how long? Must a writer see their own write immediately? |
| Durability | Can a lost event be regenerated, or is it the only record (payments, audit, legal)? |
| Security / privacy | Who may read/write; tenant isolation; PII in transit, storage, logs; abuse vectors on public endpoints. |
| Cost | Third-party calls with a price (SMS, email, LLM, maps), storage that grows forever, compute that runs per request. |
| Operability | Who gets paged; how do we know it works; how do we replay or backfill. |
| Compatibility | Clients on old versions, other services consuming the same API, mobile apps that cannot be force-updated. |

### Extract the author's intent

The author is usually a product manager, a lead or the user themselves. Look
for their design in:

- the ticket body and acceptance criteria;
- comments and linked threads (Jira, Linear, Slack exports);
- the branch name, draft PR, or stubbed code already in the tree;
- how the *previous* similar feature was built in this repo (the strongest
  signal of what the team considers normal);
- ADRs, architecture docs, `docs/` folders, `README`s of the touched modules.

Write the intent in one line at the top of the brief. If you cannot find any,
say "no stated design; proposing from scratch".

### Questions that change the design

Ask the user only when an answer flips a decision. Typical ones:

- "Must it be visible within a second (push/WebSocket) or is a minute fine
  (polling / next page load)?"
- "Is a lost event acceptable (best-effort) or must every one be delivered
  (durable queue + retries)?"
- "Who are the heaviest tenants, and how many items do they have?"
- "Is this per-tenant or cross-tenant data?"
- "Is there a budget / contract for the third-party service?"

Everything else becomes an assumption in the brief. Assumptions are cheap to
correct; blocked work is not.

## Move 2 — Estimate

See `estimation.md` for the numbers. The output of this move is three or four
lines, not a spreadsheet:

```
~3k DAU × ~20 list views/day ≈ 60k reads/day ≈ 0.7 rps avg, ~4 rps peak.
Writes: ~500/day. Table grows ~200 rows/day → ~75k rows/year. Fits one Postgres
node with an index for years; no cache, no queue needed for throughput.
```

The sentence after the numbers is the point: what they *allow* and what they
*forbid*.

## Move 3 — Current design (as-is)

Read before you write. The brief must name real things.

Checklist:

- Entry point(s): route, controller, handler, job, consumer, UI screen.
- Data flow in one text line; mark sync vs async hops.
- Storage: tables/collections, their keys and indexes, approximate row
  counts (ask the DB or look at migrations and seed sizes).
- State ownership: server DB, cache, client store, URL, local storage.
- Existing primitives you can reuse: job runner, outbox, event bus, query
  cache, pagination helper, rate limiter middleware, WebSocket hub, file
  storage adapter, feature flags.
- Inherited limits: page sizes, timeouts, max payload, third-party quotas,
  connection pool sizes.
- Known pain: TODOs, issues, slow-query logs, previous incidents in the area.

If the codebase is not available (greenfield or no access), say so and
describe the as-is from what the user told you.

## Move 4 — Target design (to-be)

### Order of preference

1. The author's design, if it meets the numbers with headroom.
2. The author's design with the smallest change that removes a concrete
   failure mode.
3. A different design, presented as an alternative with the trade-off, not as
   a replacement.

### What the section must contain

- Components and flow in a one-line text flow; say which are new or
  changed. Box diagrams only if the user opts in (`visualization.md`).
- API contract: method + path (or event name) and request/response shapes,
  including error cases and pagination.
- Data model: tables, keys, indexes, unique constraints, retention.
- For every pattern used: name, reason, rejected alternative. Use
  `patterns.md` as the catalog.
- Canonical-system analogy when one applies.
- Deferred upgrades with their trigger signal.

### Headroom rule of thumb

Design for roughly 10× the 12-month estimate at the level of *data model and
API contract* (those are expensive to change), and for 2-3× at the level of
*infrastructure* (replicas, caches, queues can be added later when the signal
appears). Changing a primary key or a public contract is a migration;
adding a read replica is a config change.

## Move 5 — Deep dive

Pick the risky components. "Risky" means: concurrent writers, fan-out,
unbounded growth, external dependency, money, PII, or anything on the
critical user path. For each, answer:

1. What is the failure mode, concretely ("two approvers click at once; both
   requests pass the `status = pending` check; two notifications go out")?
2. What is the cheapest mitigation ("`UPDATE ... WHERE status = 'pending'`
   and check rows affected; idempotency key on the notification")?
3. When is it needed: now, before launch, or at N?

## Move 6 — Wrap up

- Write the brief.
- List open questions for the author separately from assumptions you made.
- Turn the to-be into an ordered implementation plan where each step is
  reviewable on its own and leaves the system working (contract first, then
  storage, then write path, then read path, then UI, then observability).
- Continue with the implementation unless the user asked only for the
  analysis.

## Anti-patterns of the analysis itself

- **Solution first.** Naming a technology before the numbers.
- **Buzzword list.** "Consider caching, sharding, CQRS and event sourcing"
  with no reason tied to this feature.
- **Fictional as-is.** Describing a queue or cache that does not exist in the
  code.
- **No numbers.** "This should scale fine" without an estimate.
- **Ignoring the author.** Proposing a rewrite when the ticket already has a
  workable design.
- **Hiding assumptions.** Deciding "polling is fine" without writing it down.
- **Analysis without implementation.** The brief is a means; the user asked
  for the feature.
