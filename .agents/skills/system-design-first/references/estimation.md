# Back-of-the-envelope estimation

Estimates do not need to be right; they need to be the right order of
magnitude, so that a decision ("do we need a queue?") becomes obvious. Round
aggressively, state your inputs, and mark every guessed number as a guess.

## Handy constants

| Thing | Value | Use |
| --- | --- | --- |
| Seconds per day | 86,400 ≈ 10^5 | 1 M events/day ≈ 12/s ≈ 10/s |
| Seconds per month | ≈ 2.6 M | |
| 2^10 | 1 thousand (KB) | |
| 2^20 | 1 million (MB) | |
| 2^30 | 1 billion (GB) | |
| 2^40 | 1 trillion (TB) | |
| ASCII char | 1 byte; UTF-8 Cyrillic ≈ 2 bytes | |
| UUID as text | 36 bytes; as binary 16 | |
| Typical JSON row with 10-20 fields | 0.5-2 KB | |
| Small image / avatar | 20-100 KB | |
| Photo | 1-5 MB | |
| 1 minute of 1080p video | ~50-100 MB raw upload, ~10-20 MB transcoded | |

## Latency ladder (orders of magnitude)

Exact figures vary by hardware; the ratios are what matter.

| Operation | Approx. |
| --- | --- |
| L1 cache reference | 1 ns |
| Main memory reference | 100 ns |
| Compress 1 KB (fast codec) | 2-3 µs |
| Send 1 KB over 1 Gbps network | 10 µs |
| SSD random read | 20-100 µs |
| Read 1 MB sequentially from memory | 10-250 µs |
| Round trip inside one datacenter / AZ | 0.5 ms |
| Read 1 MB sequentially from SSD | ~1 ms |
| HDD seek | ~10 ms |
| Read 1 MB from HDD | ~20 ms |
| Round trip same continent | 20-50 ms |
| Round trip across continents | ~150 ms |
| Mobile network round trip (4G) | 50-150 ms |

Consequences you will use constantly:

- Anything in memory is ~1000× faster than anything on disk, and disk is
  ~100× faster than a cross-region hop. Caches work because of the first
  ratio; CDNs because of the second.
- A page that makes 5 sequential API calls on a mobile network spends
  ~0.5 s just in round trips before any work happens. Batch or parallelise.
- One cross-datacenter call per request puts a floor of tens of milliseconds
  under your p50.

## Availability: what the nines mean

| Availability | Downtime per year | Per month | Per day |
| --- | --- | --- | --- |
| 99 % | 3.65 days | 7.3 h | 14.4 min |
| 99.9 % | 8.76 h | 43.8 min | 1.44 min |
| 99.99 % | 52.6 min | 4.4 min | 8.6 s |
| 99.999 % | 5.26 min | 26 s | 0.86 s |

A chain of dependencies multiplies: two 99.9 % services in series give
99.8 %. Redundant parallel copies improve it: two 99 % nodes in parallel give
99.99 % *if* failover is automatic. "Internal HR tool" usually lives
comfortably at 99.9 %; payments and auth want more.

## Throughput math

```
QPS_avg  = users_active_per_day × actions_per_user_per_day / 86,400
QPS_peak = QPS_avg × peak_factor         (2-3 for smooth traffic,
                                          5-10 for "everyone at 9:00" or campaigns)
```

Worked examples:

- 20,000 employees, each opens the app twice a day and views ~10 screens →
  400k reads/day → ~5 rps average, ~25-50 rps peak at 9:00. One API node and
  one Postgres handle this with room to spare.
- A notification feature where each of 2,000 daily events fans out to ~5
  recipients across 3 channels → 30k deliveries/day → 0.35/s. The queue is
  there for retries and decoupling from the email provider, not for load.
- A chat with 50,000 concurrent users each sending 1 message per 2 minutes →
  ~420 msg/s inbound; if the average room has 10 members, ~4,200 pushes/s
  outbound. This needs a pub/sub layer and horizontally scalable socket
  servers; one node will not hold 50k sockets *and* do fan-out comfortably.

## Storage math

```
rows_per_day × bytes_per_row × 365 × years × replication_factor (× index overhead ~1.5-2)
```

- 200 rows/day × 1 KB → 73 MB/year: a rounding error.
- 1 M events/day × 500 B → 180 GB/year before indexes: still one Postgres,
  but you now care about retention, partitioning by month and not indexing
  everything.
- 100 M rows/day → partitioning, columnar/time-series storage, tiered
  retention; this is a pipeline, not a table.

Bandwidth: `QPS × payload`. 50 rps × 20 KB = 1 MB/s = ~8 Mbps: trivial. File
downloads and video change this picture entirely; put them on object storage
behind a CDN, never through the API server.

## Single-node capacity, rough

Measure before trusting these; they are starting points for "do we need more
than one of X".

| Component | Rule of thumb |
| --- | --- |
| Relational DB (Postgres/MySQL), simple indexed reads | 5,000-20,000 qps per well-sized node |
| Relational DB, writes with fsync | 1,000-5,000 tps |
| Relational DB connections | hundreds, not thousands → use a pooler |
| Redis / in-memory KV | ~100k simple ops/s per core |
| Stateless API node (JSON over HTTP) | 1,000-10,000 rps depending on work per request |
| Reverse proxy / static files | 50k+ rps |
| WebSocket server | 10k-100k idle connections per node; fan-out throughput is the real limit |
| Message broker partition / queue | tens of MB/s or tens of thousands msg/s each |
| Full-text search node | thousands of queries/s for small indices; depends heavily on query shape |
| Browser main thread | 16 ms per frame at 60 fps; ~50 ms blocking is noticeable |

## Frontend numbers

| Thing | Target |
| --- | --- |
| LCP (largest contentful paint) | < 2.5 s |
| INP (interaction to next paint) | < 200 ms |
| CLS | < 0.1 |
| Initial JS budget (compressed) | 150-300 KB for an app shell; each remote / route chunk ≤ 100-200 KB |
| List rendering without virtualisation | fine up to a few hundred rows; thousands need windowing |
| Debounce for search-as-you-type | 200-400 ms |
| Polling interval that users accept as "live" | 5-30 s for lists; < 1 s wants push |
| TanStack Query stale time for "reference" data | minutes; for "live" data | seconds or push-driven invalidation |

## How to present an estimate

Three lines: inputs (with source or "assumed"), result, conclusion.

```
Inputs: 300 tenants × ~70 employees (DB count) ≈ 20k users; ~2 sessions/day (analytics); 10 screens/session (assumed).
Result: ~400k reads/day ≈ 5 rps avg, ~50 rps at the 9:00 peak; writes ~2k/day.
Conclusion: no cache or queue for throughput; a queue only if we need retries for email.
```
