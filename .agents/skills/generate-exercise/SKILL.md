---
name: generate-exercise
description: "Generates production-grade, adversarial Technical PM and Engineering Leadership exercises with quantitative NFRs, unit economics, sequential milestones, submission templates, and hidden rubrics. Supports both syllabus progression and custom domain prompts."
argument-hint: '<track-id> [custom-topic-or-company]'
---

# Generate Exercise: Technical Leadership & TPM Engine

This skill creates mathematically grounded, business-aligned technical leadership exercises. It produces three synchronized artifacts:
1. `exercises/<track>/<slug>/problem.md` (Public problem statement)
2. `exercises/<track>/<slug>/submission.md` (Direct candidate workspace ready for solution input)
3. `.rubrics/<track>/<slug>.md` (Hidden adversarial evaluation rubric)
It then registers the new exercise into `PROGRESS.md`.

---

## 1. Supported Tracks

- `01-product-management` (Product Strategy & Execution)
- `02-system-design` (Distributed System Design & Architecture)
- `03-data-science` (Data Science, Statistics & Experimentation)
- `04-machine-learning` (Applied Machine Learning & Production MLOps)
- `05-generative-ai` (Generative AI, RAG & LLM Systems)

---

## 2. Modes of Operation

### Mode A: Autonomous / Curriculum Progression
Triggered when no custom topic is passed (e.g. `/generate-exercise 04` or `/generate-exercise track-2`).
The generator checks `PROGRESS.md` for existing exercises in that track and selects the next topic from the **Curated Curriculum Syllabus**:

#### Track 1: Product Strategy & Execution
1. `01-enterprise-search-prd`: B2B SaaS Search Revamp (JTBD, workarounds, North Star & perverse incentives)
2. `02-pricing-migration-usage`: Migrating Seat-Based SaaS to Usage-Based Pricing (Cannibalization, gross margins)
3. `03-feature-sunset-migration`: Deprecating a legacy API used by 40% of enterprise customers (SLA breaches, churn)
4. `04-marketplace-liquidity-matching`: Two-sided gig platform supply/demand matching under cold-start conditions
5. `05-workflow-engine-prioritization`: Evaluating workflow engine custom build vs. third-party OEM using RICE

#### Track 2: Distributed System Design & Architecture
1. `01-payment-idempotency`: High-throughput settlement engine with zero-duplicate guarantee (12k write QPS)
2. `02-realtime-collab-sync`: Real-time collaborative document engine (OT vs. CRDT, memory footprint, fan-out)
3. `03-global-rate-limiter`: Multi-region distributed token bucket / rate limiter under clock drift
4. `04-video-transcoding-pipeline`: Scalable asynchronous video ingestion & chunked transcoding (Egress economics)
5. `05-order-matching-engine`: Financial exchange matching engine with microsecond P99 SLA and deterministic replay

#### Track 3: Data Science, Statistics & Experimentation
1. `01-recs-engine-ab-test`: Recommendation algorithm A/B test (Power calculation, sample sizing, MDE, peeking bias)
2. `02-search-ranking-interleaving`: Evaluating search rankers via Team-Draft Interleaving vs. standard A/B test
3. `03-two-sided-network-experiment`: Ride-share surge pricing test with spatial interference (Cluster randomization)
4. `04-retention-uplift-modeling`: Causal uplift modeling for customer win-back campaigns
5. `05-metric-variance-reduction`: Applying CUPED with historical pre-experiment covariates to reduce test duration

#### Track 4: Applied Machine Learning & Production MLOps
1. `01-realtime-fraud-detection`: Sub-20ms fraud classification with extreme class imbalance & asymmetric FP/FN cost
2. `02-two-stage-recs-serving`: Large-scale e-commerce candidate retrieval (ANN) + re-ranking under 50ms P99
3. `03-clinical-diagnosis-pipeline`: Clinical decision support with temporal splitting, target leakage audits, and shadow deployment
4. `04-drift-monitoring-retraining`: Covariate shift (PSI/KS-test) and concept drift detection with automated retrain triggers
5. `05-edge-defect-inspection`: Quantized edge computer vision (TensorRT/ONNX) with intermittent cloud connectivity

#### Track 5: Generative AI, RAG & LLM Systems
1. `01-enterprise-rag-evals`: Compliance policy RAG with hybrid dense/sparse retrieval and deterministic assertions
2. `02-llm-judge-eval-suite`: Authoring an LLM-as-a-judge evaluation harness with synthetic test generation
3. `03-structured-extraction-pipeline`: High-throughput PDF contract extraction using state machines vs. agent loops
4. `04-code-copilot-caching`: Code completion service with prompt caching, speculative decoding, and token budget modeling
5. `05-prompt-injection-defense`: Defense-in-depth architecture against direct and indirect prompt injections for enterprise tools

---

### Mode B: Custom / On-Demand Scenario
Triggered when the user provides a custom scenario (e.g. `/generate-exercise 02 "Uber surge pricing recalculation engine"`).
The generator retains the specific domain, constraints, and business context requested by the user, while strictly applying the **5 Invariants**.

---

## 3. The 5 Invariants of Every Problem Statement

When authoring `problem.md`, you MUST enforce:

1. **Concrete Unit Economics & Cloud COGS**:
   - Provide an Average Revenue Per User/Transaction (ARPU/ARPT) and a hard infrastructure cost cap (e.g. "Revenue is $0.12/transaction; compute + storage infra cost cannot exceed $0.0006").
2. **Irreconcilable Architectural / Product Tensions**:
   - Force difficult choices (e.g., consistency vs. latency, precision vs. recall, time-to-market vs. long-term technical runway).
3. **Grounded Scale Math & NFRs**:
   - Explicit Peak QPS, Read:Write ratio, P99 latency SLA, availability SLA (e.g., 99.99%), data retention horizon, and payload byte size.
4. **Zero Solution Leakage**:
   - State the problem, boundary conditions, and failure modes. Never suggest specific tools, database engines, or algorithms in `problem.md`.
5. **Sequential Milestones**:
   - Always structure into 4 to 5 sequential milestones (e.g., Milestone 1: Scale Math, Milestone 2: Contracts, Milestone 3: Core Topology, Milestone 4: Failure Modes, Milestone 5: Economics).

---

## 4. File Generation Specifications

### File 1: `exercises/<track>/<slug>/problem.md`
Must follow this exact structure:
- `# Exercise XX: <Title>`
- `## Track`: `<Track Name>`
- `## 1. Business Context & Problem Statement`
- `## 2. Quantitative Non-Functional Requirements (NFRs)` (Markdown table with targets and justifications)
- `## 3. The Core Architectural / Product Decisions` (Key decisions to defend, without answers)
- `## 4. Deliverables & Milestones` (List of sequential milestones)

### File 2: `exercises/<track>/<slug>/submission.md`
Must provide a ready-to-edit workspace for the user:
- `# Candidate Submission: <Exercise Title>`
- `# Candidate Name: <Name>`
- Template sections corresponding exactly to each milestone with guiding questions and empty workspace blocks ready for the candidate's solution.

### File 3: `.rubrics/<track>/<slug>.md`
The hidden adversarial evaluation rubric:
- Must NEVER be placed in `exercises/`. Always place in `.rubrics/<track>/<slug>.md`.
- Contains:
  - **Core Evaluation Pillars**.
  - **Adversarial Failure Traps**: Explicit traps the candidate is likely to fall into (e.g., clock drift in distributed locks, target leakage in feature engineering, peeking bias in A/B tests).
  - **Milestone Evaluation Grid**: Passing criteria vs. Failure modes for each milestone.

### File 4: Update `PROGRESS.md`
- Increment the exercise count for that track.
- Add the new exercise to the track table:
  `| **M1** | <Deliverable> | Pending | — | — |`
- Update track status to `In Progress`.

---

## 5. Execution Checklist
When invoked:
1. Parse track and optional custom prompt.
2. Determine slug (e.g., `02-realtime-collab-sync`).
3. Create target directory `exercises/<track>/<slug>/`.
4. Create directory `.rubrics/<track>/`.
5. Write `problem.md`.
6. Write `submission.md` (ready for candidate solution).
7. Write `.rubrics/<track>/<slug>.md`.
8. Update `PROGRESS.md`.
9. Notify user with the exercise summary, key tensions, and instructions to begin Milestone 1.
