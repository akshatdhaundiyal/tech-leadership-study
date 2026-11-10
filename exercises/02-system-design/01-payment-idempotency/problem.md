# Exercise 01: High-Throughput Payment Idempotency Engine

## Track
Distributed System Design & Architecture (`exercises/02-system-design`)

---

## 1. Business Context & Problem Statement

You are the Technical Product Manager / Lead Systems Architect for a high-growth B2B payments platform. The platform handles vendor payouts, contractor disbursements, and corporate card settlements across multiple banking partners and payment gateways.

### The Problem
During peak transaction events (e.g., end-of-month corporate payroll runs and merchant batch settlements), banking partners experience transient connectivity drops, latency spikes, and 504 Gateway Timeouts. 

When timeouts occur, upstream client applications retry settlement requests. Because the existing settlement service lacks a deterministic, distributed idempotency guarantee, retries have resulted in:
1. **Duplicate Payouts**: Millions of dollars in duplicate disbursements requiring manual bank clawbacks.
2. **Reconciliation Lag**: Finance teams spending days identifying duplicate ledger entries.
3. **Merchant Churn**: Key enterprise customers threatening to churn due to unreliable transaction accounting.

The VP of Engineering and VP of Product have tasked you with designing a resilient, horizontally scalable **Payment Ingest & Idempotency Engine**.

---

## 2. Quantitative Non-Functional Requirements (NFRs)

Before proposing any components or database choices, your design must satisfy these exact operational boundaries:

| Requirement | Metric / Target | Justification |
| :--- | :--- | :--- |
| **Peak Throughput** | 12,000 write QPS (settlement requests) | Scaled for 3x current peak payroll load. |
| **Query Profile** | 95:5 Read:Write ratio | 228,000 status queries / balance checks per second vs. 12,000 writes. |
| **Latency SLA** | P99 write $\le 80\text{ ms}$; P99.9 $\le 150\text{ ms}$ | Downstream API timeout from partner enterprise ERPs is 200ms. |
| **Availability** | $99.99\%$ for Ingest API ($< 52.6\text{ min}$ downtime/year) | Tier-1 financial infrastructure uptime commitment. |
| **Data Retention** | 7 years immutable audit trail; 72-hour hot idempotency window | Financial compliance requirement (SOX/PCI-DSS) + short retry window. |
| **Unit Economics** | Compute & DB infra cost $\le \$0.0008$ per settlement | Margin requirement against $\$0.15$ average revenue per transaction. |
| **Consistency** | Strict single-execution guarantee ($0$ duplicate executions permitted) | Absolute zero tolerance for duplicate bank settlement calls. |

---

## 3. The Core Architectural Decisions

You must define and defend:
1. **Idempotency Key Protocol & Schema**: How the client generates keys, payload fingerprinting (hashing), collision mitigation, and state machine transitions (`PENDING`, `PROCESSING`, `SUCCESS`, `FAILED`).
2. **Distributed Storage & Caching Layer**: Where idempotency keys are stored and locked. Evaluate Redis (Redlock vs single instance vs cluster) vs. DynamoDB/Cassandra conditional writes vs. relational DB (Postgres `ON CONFLICT DO NOTHING`).
3. **Downstream Gateway Timeout Handling**: How the engine differentiates between "gateway failed to receive request" vs. "gateway received request, executed payment, but response timed out".
4. **Failure Recovery & Edge Cases**:
   - Cache crash / node failure during transaction processing.
   - Client sends identical key with altered payload (fingerprint mismatch).
   - Network partitions (CAP theorem posture between API gateway and idempotency datastore).

---

## 4. Deliverables & Milestones

Do not write a monolithic design doc all at once. Address the milestones sequentially:

- **Milestone 1**: Scale Math & Storage Sizing (Bandwidth, hot storage, and 7-year cold storage calculations).
- **Milestone 2**: API Contract & Idempotency Key Specification (HTTP headers, payload hashing, status codes).
- **Milestone 3**: Distributed State Machine & Locking Topology (Diagram + race condition mitigations).
- **Milestone 4**: Failure Modes & Partition Tolerance (Timeout recovery, gateway reconciliation, DLQ design).
- **Milestone 5**: Economic & COGS Justification (Server count, DB I/O, cache provisioning cost modeling).
