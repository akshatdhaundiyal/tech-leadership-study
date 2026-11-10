# Grading Rubric: Payment Idempotency Engine

This rubric defines the adversarial evaluation criteria for the Payment Idempotency Engine exercise.

---

## Evaluation Grid

| Milestone | Passing Criteria (Meets Bar) | Failure Modes (Below Bar) |
| :--- | :--- | :--- |
| **Milestone 1: Scale Math & Sizing** | - Computes peak and average network bandwidth (KB/s and MB/s) assuming realistic payload sizes (e.g., 2–5 KB).<br>- Calculates RAM footprint for 72-hour hot TTL in memory/cache.<br>- Sizes 7-year cold ledger storage with replication factor $\ge 3$. | - Waves hands on payload sizes or omits hot vs. cold storage tiering.<br>- Fails to account for index and metadata overhead in cache sizing. |
| **Milestone 2: API Contract & Key Semantics** | - Specifies explicit headers (`Idempotency-Key`).<br>- Implements payload fingerprinting (e.g., SHA-256) to detect reused keys with mutated parameters.<br>- Returns HTTP 422/409 on fingerprint mismatch; returns HTTP 409 or 200 with cached body on in-flight or completed duplicates. | - Trusts client keys without payload hashing (vulnerable to silent payload spoofing/mutations).<br>- Poor HTTP semantics (e.g. returning 500 for duplicate requests). |
| **Milestone 3: Distributed Locking & Topology** | - Concrete lock lease / TTL duration to prevent deadlocks on worker crashes.<br>- Atomicity guarantee (e.g. Redis `SET NX EX` or database conditional upsert).<br>- Explicit mitigation for cache stampede (thundering herd) when multiple concurrent retries arrive. | - Recommends simple naive locking without lease timeout or owner validation.<br>- Ignores race condition when two requests with the same key hit different pods simultaneously. |
| **Milestone 4: Timeout Recovery & Partition Tolerance** | - Solves the "two generals problem" for gateway timeouts: async polling / status inquiry jobs or webhook reconciliations.<br>- Dead-letter queue (DLQ) topology with exponential backoff and jitter.<br>- Clear CAP trade-off stance during network partitions. | - Assumes timeouts mean the transaction failed and immediately issues a blind refund/re-execution.<br>- No dead-letter queue or reconciliation loop. |
| **Milestone 5: COGS & Unit Economics** | - Demonstrates that the total monthly infrastructure bill (compute nodes, memory cache cluster, persistent storage I/O) divided by monthly transaction volume is $\le \$0.0008$. | - Proposes an over-engineered multi-region cluster with cloud bills exceeding customer unit margins. |
