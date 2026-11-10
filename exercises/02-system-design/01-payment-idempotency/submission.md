# Candidate Submission: High-Throughput Payment Idempotency Engine

- **Candidate**: 
- **Date**: 
- **Track**: Distributed System Design & Architecture (`exercises/02-system-design`)
- **Exercise**: `01-payment-idempotency`

---

## Milestone 1: Scale Math & Sizing

### 1.1 Ingress Bandwidth Calculations
*Show your arithmetic for peak write bandwidth, read bandwidth, and combined network ingress:*

### 1.2 72-Hour Hot-Tier RAM Footprint
*Show your calculation for transaction volume, memory overhead per record, replication factor, and total cluster RAM:*

### 1.3 7-Year Cold Storage Projection
*Show your calculation for 7-year audit data accumulation, replication across regions, and indexing overhead:*

### 1.4 Cost-Driver Identification
*State which tier drives recurring cloud infrastructure costs and explain why:*

---

## Milestone 2: API Contract & Idempotency Key Specification

### 2.1 HTTP Request & Response Headers
*Define required headers, client-supplied keys, and fingerprinting headers:*

### 2.2 Payload Hashing & Mutation Defense
*Specify the hashing algorithm, canonicalization approach, and behavior when an identical key arrives with mutated payload:*

### 2.3 Status Code & State Semantics
*Define HTTP response codes for in-flight requests, completed requests, and parameter conflicts:*

---

## Milestone 3: Distributed State Machine & Locking Topology

### 3.1 State Machine Transitions
*Diagram or state table for transition between PENDING, PROCESSING, SUCCESS, and FAILED:*

### 3.2 Locking & Storage Engine Evaluation
*Evaluate your storage and lock management choice. Defend against clock drift, node crash, and thundering herd:*

---

## Milestone 4: Failure Modes & Partition Tolerance

### 4.1 Downstream Gateway Timeout Resolution
*How do you handle gateway timeouts without double-charging or delaying retries indefinitely?*

### 4.2 Network Partition & CAP Posture
*Define your availability vs. consistency guarantee during cross-region or datastore partitions:*

### 4.3 Dead-Letter Queue & Reconciliation
*Explain the background reconciliation loop and dead-letter queue design:*

---

## Milestone 5: Economic & Cloud COGS Defense

### 5.1 Infrastructure Bill Breakdown
*Estimate node counts, IOPS costs, memory pricing, and network transit:*

### 5.2 Unit Cost Validation
*Demonstrate that total monthly infrastructure cost divided by monthly settlement volume is $\le \$0.0008$:*
