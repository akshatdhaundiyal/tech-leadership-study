# Pattern catalog

A compact catalog of the building blocks the system-design playbook keeps
reaching for, with the questions that decide whether a given feature needs
them. Every entry has the same shape: what it is, use when, avoid when,
trade-offs. The last section maps canonical systems (chat, feed,
notifications, ...) to their standard building blocks.

## Contents

1. [Scaling the serving layer](#1-scaling-the-serving-layer)
2. [Caching](#2-caching)
3. [Asynchrony and queues](#3-asynchrony-and-queues)
4. [Data storage and consistency](#4-data-storage-and-consistency)
5. [APIs, real-time transport and pagination](#5-apis-real-time-transport-and-pagination)
6. [Rate limiting and ID generation](#6-rate-limiting-and-id-generation)
7. [Reliability](#7-reliability)
8. [Observability](#8-observability)
9. [Security and multi-tenancy](#9-security-and-multi-tenancy)
10. [Canonical systems and their building blocks](#10-canonical-systems-and-their-building-blocks)

---

## 1. Scaling the serving layer

**Vertical scaling.** Bigger box. Use when: the numbers fit one node with
headroom and you want zero new moving parts. Avoid when: you need
availability (one box is a SPOF) or growth is unbounded. Trade-off: cheapest
in complexity, hard ceiling, no redundancy.

**Stateless servers + load balancer.** Session state lives in a shared store
(DB, Redis, signed cookie), so any instance can serve any request. Use when:
more than one instance, rolling deploys, autoscaling. Avoid when: a single
instance is fine and nobody expects uptime guarantees. Trade-off: every bit of
per-user state must move out of process memory (in-memory caches become
per-instance and inconsistent; WebSocket connections pin to an instance).

**CDN.** Edge cache for static assets and cacheable responses. Use when:
assets, images, public pages, large downloads; users far from the origin.
Avoid when: content is per-user and uncacheable, or invalidation must be
instant and you cannot version URLs. Trade-off: cache invalidation
(versioned/hashed filenames solve it for assets), cost per GB.

**Read replicas.** Copies of the primary DB serving reads. Use when: reads
dominate and the primary's CPU/IO is the bottleneck; reporting queries hurt
OLTP. Avoid when: readers need their own writes immediately (replication lag
breaks "I just saved it and it's gone"). Trade-off: eventual consistency on
replicas; routing logic in the app.

**Sharding (horizontal partitioning).** Split rows across DB nodes by a
shard key. Use when: a single node cannot hold the data or the write load;
usually past hundreds of GB or thousands of writes/s. Avoid when: you are
under that; sharding is the most expensive pattern to adopt and to undo.
Trade-offs: cross-shard joins and transactions vanish; hot shards (celebrity
tenants); resharding needs consistent hashing or a directory service. The
shard key is usually tenant id or user id in SaaS.

**Multi-region.** Copies of the whole stack close to users. Use when:
latency across continents is a product problem or regulation demands data
residency. Avoid otherwise; it multiplies every consistency problem.

## 2. Caching

**Where caches live** (closest to the user first): browser HTTP cache → CDN
→ client state cache (TanStack Query, SWR, Apollo) → API gateway → application
cache (Redis/Memcached) → DB page cache. Each layer has its own invalidation
story; pick the closest layer that still gives correct results.

**Cache-aside (lazy loading).** App checks cache, on miss reads DB and
writes cache. Use when: read-heavy, tolerates slightly stale data, keys are
requested repeatedly. Trade-offs: first request pays; stale until TTL or
explicit invalidation; "thundering herd" when a hot key expires (mitigate with
locking, early recompute, jittered TTL).

**Write-through / write-behind.** Write to cache and DB together (through)
or to cache first and DB later (behind). Use when: read-after-write must hit
cache. Write-behind risks data loss on cache failure; rarely worth it outside
counters.

**TTL vs explicit invalidation.** TTL is simple and self-healing; explicit
invalidation is precise but every write path must remember it. Combine: short
TTL as a safety net plus invalidation on known writes.

**Eviction.** LRU by default; LFU for skewed popularity. Size the cache from
the working set, not the whole dataset.

**Client-side caching (SPA).** Stale-while-revalidate: show cached data,
refetch in background. Decide `staleTime` per data class (reference data:
minutes; live data: seconds or push-invalidated). Invalidate by query key
after mutations; use optimistic updates only when rollback UI is designed.

**When NOT to cache.** Data that changes on every read (counters with strict
accuracy), per-user data with low repeat rate, anything where a stale value
causes a wrong decision (balances, permissions, inventory at checkout).

**Hot keys.** One key (a popular tenant, a global config) hammered by every
request. Mitigate: replicate the key across several cache nodes with a
suffix, local in-process cache with a short TTL, or precompute.

## 3. Asynchrony and queues

**Message queue (work queue).** Producer enqueues; one worker consumes each
message. Use when: the work is slow, flaky or external (email, SMS, PDF,
third-party API); you want retries and backpressure; the user does not need
the result synchronously. Avoid when: the user waits for the result anyway
(then it is just latency plus complexity) or the volume is tiny *and* nothing
can fail. Trade-offs: at-least-once delivery → consumers must be idempotent;
ordering is per-partition/queue at best; a new runtime to operate.

**Pub/sub.** One event, many independent subscribers. Use when: several
consumers react to the same fact (audit log, search index, notifications,
analytics). Trade-off: implicit coupling through event schemas; versioning
events is a real job.

**Fan-out on write vs fan-out on read** (the news-feed question). On write:
precompute each recipient's inbox/feed when the event happens; fast reads,
expensive and wasteful for recipients who never look, hot for celebrity
producers. On read: compute on demand from sources; cheap writes, slow reads.
Hybrid: on write for normal users, on read for celebrity/hot sources.
Notifications are almost always fan-out on write (per-recipient rows).

**Retries, backoff, DLQ.** Retry transient failures with exponential backoff
and jitter; cap attempts; park poison messages in a dead-letter queue with
alerting. Without a DLQ a single bad message can block a queue forever.

**Idempotent consumers.** Dedup by a message id or a natural key (`event_id`,
`(user_id, notification_type, entity_id)`) with a unique constraint or a
"processed" table. This is the single most common bug in async systems.

**Transactional outbox.** Write the business row and the event in the same DB
transaction into an `outbox` table; a relay publishes it. Solves "DB committed
but publish failed" and the reverse. Use when: an event must exist iff the
write happened (payments, orders, anything audited).

**Change data capture.** Stream DB changes (WAL) to consumers. Use when: you
need derived views (search index, cache, analytics) kept in sync without
touching every write path.

**Scheduled jobs.** Cron-like batch. Use when: periodic reconciliation,
digests, cleanup. Design for overlap (a run takes longer than the interval)
with a lock or a lease, and for partial failure (resume from a checkpoint).

**Exactly-once is a contract, not a transport feature.** Achieve it with
at-least-once delivery plus idempotent processing.

## 4. Data storage and consistency

**Relational DB.** Default choice for business data: transactions, joins,
constraints, mature tooling. Scales further than people assume (hundreds of
GB, thousands of tps on one node). Design keys, indexes and unique constraints
deliberately; most "DB is slow" is a missing index or an N+1.

**Document store.** Flexible schema, document-shaped reads. Use when: the
read unit really is the document and relations are few. Trade-off: joins and
multi-document transactions are weak; schema drift moves into code.

**Key-value store** (Redis, DynamoDB-style). Sub-millisecond gets/puts by
key. Use when: cache, sessions, counters, rate limits, leaderboards (sorted
sets), presence, locks with TTL. The distributed KV design from the playbook
(consistent hashing, replication N with quorum W/R, vector clocks or
last-write-wins, hinted handoff, anti-entropy with Merkle trees) is what
managed stores do under the hood; you need to know it to reason about their
consistency knobs.

**Wide-column / time-series.** Write-heavy, time-ordered, range-scanned
data (metrics, events, logs). Use when: millions of rows a day with
time-window queries. Partition by time, downsample, expire.

**Search index** (Elasticsearch/OpenSearch, Meilisearch, Postgres FTS).
Full-text, fuzzy, faceted. Use when: `LIKE '%x%'` across many rows or fields;
relevance ranking. Trade-off: a derived store that must be kept in sync
(CDC/outbox) and can lag.

**Object storage** (S3-compatible). Files, exports, media. Never store blobs
in the DB past a few KB; store the key and metadata. Serve through a CDN or
pre-signed URLs, never through the API server.

**Indexes.** Every query shape the feature introduces needs a matching
index, composite in the order of equality → range → sort. Partial indexes for
status columns; covering indexes for hot lists. Each index costs write
throughput and storage.

**Denormalisation.** Copy a value to avoid a join (e.g. `author_name` on a
comment). Use when: the read path is hot and the source rarely changes.
Trade-off: an update path that must fan out, or an accepted staleness.

**CAP and PACELC, practically.** During a partition you choose availability
or consistency; the rest of the time you choose latency or consistency. SaaS
business data usually wants consistency (one primary, synchronous commit);
social/feed data usually wants availability and tolerates staleness.

**Consistency models you will actually pick between.** Strong (read what was
just written, one primary) · read-your-own-writes (route a user's reads to the
primary briefly after a write) · monotonic reads (a user never sees time go
backwards) · eventual (replicas, caches, derived stores). Name the model per
read path in the brief.

**Transactions and concurrency.** Use DB transactions for multi-row
invariants. Prevent double-processing with conditional updates
(`UPDATE ... WHERE status = 'pending'` and check rows affected), optimistic
locking (`version` column), or `SELECT ... FOR UPDATE` for short critical
sections. Distributed transactions across services → sagas with compensating
actions, or avoid by keeping the invariant inside one DB.

**Soft delete, retention, archival.** Decide at design time what grows
forever and where it goes after N months. Partition large append-only tables
by time so old partitions can be dropped.

## 5. APIs, real-time transport and pagination

**REST.** Resource-oriented, cacheable, boring in the good way. Default for
CRUD and public APIs.

**GraphQL.** Client-shaped queries, one endpoint. Use when: many clients
with different data needs, deep object graphs. Trade-offs: caching is harder,
N+1 on resolvers (needs batching/dataloader), query cost control.

**gRPC.** Typed, binary, streaming. Use when: service-to-service with strict
contracts and high volume. Avoid for browser clients unless you want a proxy.

**Real-time transport.** Decide by "how fresh must it be" and "how many
clients":

| Transport | Use when | Cost |
| --- | --- | --- |
| Short polling | Freshness of 10-60 s is fine; few clients | Wasted requests; simplest |
| Long polling | Freshness of seconds; proxies hostile to sockets | Holds connections; complex timeouts |
| SSE | Server → client only (feeds, progress, notifications) | One-way; auto-reconnect built in |
| WebSocket | Bidirectional, sub-second (chat, collaboration, presence) | Stateful connections; need a pub/sub layer to scale past one node |

Scaling sockets: connections pin to a node; publish events through a broker
(Redis pub/sub, NATS, Kafka) so every node can push to its own clients.
Handle reconnect with a resume cursor so missed events are replayed, not
lost.

**Pagination.** Offset (`LIMIT/OFFSET`) is fine for small, stable lists and
admin tables; it degrades as offset grows and skips/duplicates rows when data
changes. Cursor/keyset (`WHERE (created_at, id) < (?, ?) ORDER BY ... LIMIT`)
is stable and O(1) per page; use it for feeds, infinite scroll and anything
large. Return a `next_cursor`, never expose raw offsets as the contract.

**Idempotency keys.** For any non-idempotent POST that a client might retry
(payments, submissions, "send"): client sends a key, server stores
`(key → result)` and returns the same result on replay.

**Versioning and compatibility.** Additive changes only on live contracts;
new required fields or renamed fields = new version or a migration window.
Mobile clients and other services cannot be force-updated.

**Batching.** Replace N calls with one (`/items?ids=`, `POST /batch`),
especially over mobile networks. Watch payload size and partial failure
semantics.

## 6. Rate limiting and ID generation

**Rate limiting algorithms.** Token bucket (bursts allowed up to bucket size;
the usual default) · leaky bucket (smooth output rate) · fixed window
(simple, bursty at edges) · sliding window log (exact, memory per request) ·
sliding window counter (good approximation, cheap). Store counters in a KV
store so all instances share them; limit by user, tenant, IP and endpoint
class; return `429` with `Retry-After`. Decide what to do when the limiter
itself is down (fail open for internal, fail closed for abuse-prone public
endpoints).

**Unique IDs.** Auto-increment (simple, leaks counts, single writer) · UUIDv4
(random, index-unfriendly at scale) · UUIDv7 / ULID (time-ordered, index
friendly; the modern default) · Snowflake-style (time + node + sequence;
64-bit, sortable, needs node ids) · ticket server (central counter; SPOF).
Pick time-ordered when IDs are primary keys in large tables or used as
cursors.

**Short codes / hashes** (URL shortener shape). Base62 of a sequence id, or
hash + collision check. Decide if codes must be unguessable (then random, not
sequential).

## 7. Reliability

**Single points of failure.** List them explicitly: one DB primary, one
queue broker, one third-party, one socket node, one cron box. Decide which are
acceptable at this stage and what the recovery time is.

**Timeouts everywhere.** Every network call has a timeout shorter than the
caller's. A missing timeout turns a slow dependency into an outage.

**Retries with jitter, budgeted.** Retry only idempotent calls or calls with
an idempotency key; exponential backoff with jitter; a retry budget so a
dependency's outage does not become a retry storm.

**Circuit breaker.** After N failures stop calling a dependency for a while
and fail fast; probe to recover. Use when: a slow dependency can exhaust your
threads/connections.

**Bulkheads.** Separate pools/queues per dependency or tenant so one slow
thing cannot starve the rest.

**Graceful degradation.** Define the degraded mode up front: show cached
data, hide the widget, queue the action for later, disable a feature flag.
The user should see a smaller product, not an error page.

**Backpressure.** When producers outpace consumers: bounded queues, `429`,
shed low-priority work, slow the producer. Unbounded buffers are outages
deferred.

**Deploy safety.** Feature flags with a kill switch, canary/percentage
rollout, backward-compatible migrations (expand → migrate → contract),
rollback plan written before deploy.

**Capacity signals.** Decide the metric and the threshold that triggers the
next scaling step and put it in the brief ("add a replica when primary CPU
> 60 % for a week").

## 8. Observability

**Metrics.** Counters (requests, errors, events processed), gauges (queue
depth, connections), histograms (latency p50/p95/p99). The feature's SLI is
one of these; the alert is a threshold on it.

**Logs.** Structured, with request id / trace id / tenant id; never log PII
or secrets. Log the decision points (why a notification was skipped), not
every step.

**Traces.** Propagate a trace id across HTTP, queue messages and jobs so one
user action can be followed end to end.

**Dashboards and alerts.** One dashboard per feature with: throughput,
errors, latency, queue depth/lag, dependency health. Alert on symptoms
(users affected) not causes, with a runbook link.

**Frontend.** Web vitals, JS error tracking with release tags, API latency as
seen by the client, remote-module load failures.

## 9. Security and multi-tenancy

- Authorisation at the data layer: every query carries the tenant id; prefer
  row-level security or a mandatory scope in the repository layer over
  per-endpoint checks.
- Validate all external input at the boundary (schemas), including webhook
  payloads and queue messages from other services.
- PII: minimise what is stored, encrypt at rest where required, keep it out
  of logs, queues and analytics events; define retention.
- Public or unauthenticated endpoints get rate limits, size limits and
  CAPTCHAs/abuse checks before launch, not after.
- Secrets in a vault/env, never in code; third-party keys scoped per
  environment.
- Signed URLs with expiry for file access; never guessable object keys.

## 10. Canonical systems and their building blocks

Map the feature to the closest shape; the row gives the parts such systems
usually need, which doubles as a checklist.

| Shape | Looks like | Standard building blocks | Classic traps |
| --- | --- | --- | --- |
| **Rate limiter** | Throttle API/users/tenants | Token/sliding-window counters in a shared KV, middleware, 429 + headers | Per-instance counters; limiter outage behaviour undefined |
| **Key-value store** | Sessions, config, feature flags, presence | Consistent hashing, replication + quorum, TTL, LRU | Treating eventual consistency as strong |
| **Unique ID generator** | IDs across services/shards | UUIDv7/ULID or Snowflake | Random UUIDs as clustered PKs |
| **URL shortener / short codes** | Invite links, share links | Sequence → base62 or random code + unique index, 301/302 choice, click analytics async | Predictable codes where unguessable is required |
| **Web crawler / importer** | Bulk import, sync from external system | Frontier queue, dedup set, politeness/rate limit per host, checkpointing, retries | No dedup; no resume after crash |
| **Notification system** | In-app, email, push, SMS for events | Event → queue → per-channel workers, per-recipient rows, user preferences, dedup by `(user, event)`, template service, provider adapters, retry + DLQ, unread counters | Duplicate sends on retry; blocking the request on provider; no opt-out |
| **News feed / activity stream** | Timeline, activity log per user | Fan-out on write to per-user inbox (hybrid for hot producers), cursor pagination, cache of recent items | Fan-out on read for everything; offset pagination on infinite scroll |
| **Chat / messaging** | 1:1 and group chat, support chat | WebSocket servers + pub/sub, message store ordered by `(room, seq)`, delivery/read receipts, presence with heartbeat TTL, push notifications for offline, resume cursor on reconnect | Single socket node; ordering by wall clock; losing messages on reconnect |
| **Search autocomplete / typeahead** | Employee search, command palette | Prefix index (trie or search engine), top-k precomputed, client debounce, result cache | Hitting the main DB with `LIKE` per keystroke |
| **Video / large media** | Uploads, transcoding, playback | Direct-to-object-storage upload (pre-signed), async transcoding pipeline, CDN delivery, status polling | Streaming bytes through the API |
| **File storage / sync** | Documents, attachments, "drive" | Metadata DB + object storage, chunking for large files, versioning, dedup by hash, share permissions, signed URLs | Blobs in the DB; ACL checks only in UI |
| **Proximity / geo** | Nearby offices, map search | Geohash or quadtree index, bounding-box query, cache per cell | Haversine over the whole table |
| **Nearby friends / live location** | Live presence, tracking | WebSocket + pub/sub per region cell, TTL'd location in KV | Persisting every ping to the main DB |
| **Metrics / monitoring** | Product analytics, audit events | Event ingestion queue, time-series store, aggregation windows, downsampling, retention tiers | Writing events row-by-row into the OLTP DB |
| **Ad-click / event aggregation** | Counting, dedup of events at volume | Stream processing with windows, exactly-once via idempotent sinks, reconciliation batch | Counting twice on retry |
| **Hotel / resource reservation** | Booking rooms, slots, interview time | Inventory table with constraints, conditional update or `FOR UPDATE`, hold with TTL then confirm, idempotent booking key | Check-then-insert race → double booking |
| **Distributed email / inbox** | Internal messaging, mass mail | Queue per recipient, spam/abuse checks, attachments in object storage, search index | Synchronous fan-out |
| **Object storage (S3-like)** | Internal blob service | Metadata service + data nodes, content hash, replication, lifecycle rules | Rebuilding S3; use a managed one |
| **Real-time leaderboard / ranking** | Top performers, gamification | Sorted set in KV, periodic snapshot to DB | Sorting in the DB per request |
| **Payment system / wallet / ledger** | Payroll, benefits, balances | Idempotency keys, double-entry ledger (append-only), reconciliation job against provider, exactly-once via outbox, state machine with explicit transitions | Mutating a balance column in place; retrying non-idempotent charges |
| **Stock exchange / matching** | Auction, allocation with strict order | In-memory single-threaded matcher, sequenced event log, deterministic replay | Lock contention; nondeterministic replay |
| **Workflow / approval engine** | Leave requests, document sign-off, onboarding | Explicit state machine, transitions as conditional updates, audit trail, timers via scheduled jobs, idempotent actions | Status strings mutated from many places; no audit |
| **Export / report generation** | CSV/XLSX export, PDF reports | Async job + progress, streaming/chunked generation, object storage + signed URL, row limits, rate limit per user | Building a 2M-row file in request memory |
| **Bulk import** | CSV upload of employees, migrations | Validate → stage → apply in batches, per-row errors report, idempotent re-run, dry-run mode | All-or-nothing transaction over 100k rows; no error report |
