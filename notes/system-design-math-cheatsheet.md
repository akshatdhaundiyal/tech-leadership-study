# System Design Scale Math & Sizing Cheat Sheet

A quick-reference guide for back-of-the-envelope calculations in distributed systems exercises.

---

## 1. Latency Hierarchy Every Architect Must Know

| Operation | Latency (Approx) | Human Scale (1 CPU cycle $\approx$ 1s) |
| :--- | :--- | :--- |
| **L1 Cache reference** | 0.5 – 1 ns | 1 second |
| **Branch mispredict** | 3 – 5 ns | 3 – 5 seconds |
| **L2 Cache reference** | 4 – 7 ns | 7 seconds |
| **Mutex lock / unlock** | 15 – 25 ns | 25 seconds |
| **Main Memory (RAM) reference** | 100 ns | 1.7 minutes |
| **Read 1 MB sequentially from RAM** | 3,000 ns (3 µs) | 50 minutes |
| **Read 1 MB sequentially from NVMe SSD**| 50 – 100 µs | 1 – 2 days |
| **Read 1 MB sequentially from 1 Gbps Net**| 10,000 µs (10 ms)| 115 days |
| **Read 1 MB sequentially from HDD** | 20,000 µs (20 ms)| 230 days |
| **Cross-datacenter / Region Round-Trip** | 50 – 150 ms | 1.5 – 4.5 years |

---

## 2. Rule-of-Thumb Conversion Multipliers

- **Seconds in a day**: $\approx 86,400\text{ s} \approx 10^5\text{ s}$ (conservative estimate: divide daily total by $10^5$ for average QPS).
- **Peak Multiplier**: Typically $2.5\times$ to $4\times$ average load.
- **Seconds in a month (30 days)**: $\approx 2.59 \times 10^6\text{ s}$.
- **Seconds in a year**: $\approx 3.15 \times 10^7\text{ s}$.
- **Seconds in 7 years**: $\approx 2.21 \times 10^8\text{ s}$.

---

## 3. Storage Sizing Checklist

Derive the formulas yourself; this list only prompts what to account for:

- Which QPS (average or peak) applies to each tier, and over what time window?
- What is stored per record, beyond the payload itself?
- What does the datastore add on top of raw bytes (indexes, allocator and metadata overhead)?
- How many copies exist, and where (replicas, AZs, regions)?
- Which tier is RAM, which is SSD, which is object storage, and what does each cost per GB-month?

---

## 4. Availability SLA to Downtime Translation

| Availability | Allowed Downtime / Year | Allowed Downtime / Month |
| :--- | :--- | :--- |
| **99% (Two 9s)** | 3.65 days | 7.2 hours |
| **99.9% (Three 9s)** | 8.76 hours | 43.8 minutes |
| **99.99% (Four 9s)** | 52.6 minutes | 4.38 minutes |
| **99.999% (Five 9s)** | 5.26 minutes | 26.3 seconds |
