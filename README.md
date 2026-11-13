# Technical Leadership & Product Mentorship Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Curriculum: 5 Tracks](https://img.shields.io/badge/Curriculum-5_Tracks-success.svg)](#curriculum-tracks)
[![Role: Technical PM & Engineering Leadership](https://img.shields.io/badge/Role-TPM_%7C_Eng_Leadership-orange.svg)](#primary-objective)

A rigorous self-study training ground for aspiring **Technical Product Managers (TPMs / Technical PMs)** and **Engineering Leaders** who aim to combine deep engineering credibility with sharp business acumen.

---

## Table of Contents
- [Primary Objective](#primary-objective)
- [Mentorship Philosophy & Rules of Engagement](#mentorship-philosophy--rules-of-engagement)
- [Overarching Business & Technical Lenses](#overarching-business--technical-lenses)
- [Curriculum Tracks](#curriculum-tracks)
  - [1. Product Strategy & Execution](#track-1-product-strategy--execution)
  - [2. Distributed System Design & Architecture](#track-2-distributed-system-design--architecture)
  - [3. Data Science, Statistics & Experimentation](#track-3-data-science-statistics--experimentation)
  - [4. Applied Machine Learning & Production MLOps](#track-4-applied-machine-learning--production-mlops)
  - [5. Generative AI, RAG & LLM Systems](#track-5-generative-ai-rag--llm-systems)
- [Repository Structure](#repository-structure)
- [Hands-On Sandbox & Empirical Prototyping (`uv`)](#hands-on-sandbox--empirical-prototyping-uv)
- [Agent Skill Setup](#agent-skill-setup)
- [Feedback & Critique Framework](#feedback--critique-framework)
- [How to Engage with the Assistant](#how-to-engage-with-the-assistant)

---

## Primary Objective

Bridging the gap between software architecture, data systems, and business outcomes. This repository serves as an interactive workshop where problems are framed from the dual perspective of an **Adversarial Principal Engineer** and a **VP of Product / Business Unit Leader**.

---

## Mentorship Philosophy & Rules of Engagement

The agent assistant embedded in this repo follows the **Socratic Adversarial Method** defined in [`AGENTS.md`](AGENTS.md):

1. **No Turnkey Solutions Upfront**: The assistant will not hand out finished PRDs, finalized system topologies, or turnkey scripts. You supply the reasoning, calculations, scale math, and trade-offs first.
2. **Sequential Milestones**: Complex challenges are broken into progressive steps. Each milestone must be justified before advancing to the next.
3. **Socratic Guidance**: If you encounter roadblocks, the assistant provides targeted hints, boundary conditions, and trade-off comparisons rather than answers.

### The Honor System

This repo cannot enforce its own rules. Any chat UI will hand you a full answer if you ask, and `.rubrics/` is a plain file you can open. The method only works if you do the thinking first: write your attempt in `submission.md`, and open a rubric or ask for a solution only after you have submitted. Peeking costs you the learning, not the repo.

---

## Overarching Business & Technical Lenses

Every proposal across all five tracks is evaluated through four foundational lenses:

```
                  ┌──────────────────────────────────────────────┐
                  │           Core Evaluation Lenses             │
                  └──────────────────────┬───────────────────────┘
                                         │
        ┌────────────────────┬───────────┴───────────┬────────────────────┐
        ▼                    ▼                       ▼                    ▼
┌───────────────┐    ┌───────────────┐       ┌───────────────┐    ┌───────────────┐
│Unit Economics │    │  Buy vs Build │       │    SLA vs     │    │ Delivery Risk │
│  & Cloud COGS │    │  & Opp. Cost  │       │ Business ROI  │    │   vs Scope    │
└───────────────┘    └───────────────┘       └───────────────┘    └───────────────┘
```

1. **Unit Economics & Cloud COGS**:
   - Cost per unit, per monthly active user (MAU), or per transaction/inference.
   - *Example*: At 1M daily queries, what is the token bill and vector DB egress cost against Customer ARPU?
2. **Buy vs. Build & Opportunity Cost**:
   - Challenging in-house reinvention when managed solutions or battle-tested APIs deliver faster time-to-market.
   - Engineering time spent on commoditized plumbing represents foregone core product differentiation.
3. **SLA vs. Business ROI**:
   - Reality-checking reliability targets: Does the customer segment genuinely require 99.99% uptime, or does a 99.9% SLA prevent a 3x infrastructure cost increase?
4. **Delivery Risk vs. Scope**:
   - Identifying architectural rabbit holes. If a proposal adds 6 weeks of runway, what market window or business value is compromised?

---

## Curriculum Tracks

### Track 1: Product Strategy & Execution
📁 [`exercises/01-product-management/`](exercises/01-product-management/)

- **Problem Space vs. Solution Trap**: Rigorous definition of Target Personas, Core Jobs-to-be-Done (JTBD), and Current Workarounds before features are conceived.
- **Metric Defensibility**: Establishing North Star metrics, identifying input vs. output drivers, and auditing for perverse incentives (e.g., short-term engagement hacks that cannibalize long-term retention).
- **Prioritization Frameworks**: Explicit trade-off matrices using RICE, Opportunity Solution Trees, and Kano analysis.
- **PRD Standards**: Problem-first specifications with quantitative baselines and target criteria.

### Track 2: Distributed System Design & Architecture
📁 [`exercises/02-system-design/`](exercises/02-system-design/)

- **Scale Math First**: Deriving concrete Non-Functional Requirements (NFRs) prior to topology design:
  - Peak Write/Read QPS, Read:Write ratio, P99 latency SLAs, network egress, and 3-year raw + replicated storage sizing.
- **Contracts & Interfaces**: Protocol selection (gRPC vs. REST vs. WebSocket/event-driven), idempotency tokens, rate limiting, and schema versioning.
- **Resilience & Storage**: Cache eviction policies, stampede (thundering herd) mitigations, Kafka partitioning and consumer lag strategies, dead-letter queues (DLQs), and CAP theorem trade-offs.

### Track 3: Data Science, Statistics & Experimentation
📁 [`exercises/03-data-science/`](exercises/03-data-science/)

- **A/B Testing Rigor**: Formulating hypotheses, calculating statistical power ($1-\beta$), significance levels ($\alpha$), Minimum Detectable Effect (MDE), and sample size estimation.
- **Experiment Guardrails**: Safeguards against peeking/early-stopping bias, variance reduction techniques (CUPED), and novelty effect handling.
- **Data Hygiene**: Pre-experiment audits for survivorship bias, selection bias, covariate shift, and multicollinearity.

### Track 4: Applied Machine Learning & Production MLOps
📁 [`exercises/04-machine-learning/`](exercises/04-machine-learning/)

- **Baselines Before Models**: Rejecting complex architectures until a simple heuristic baseline (rule engine, mean predictor, logistic regression) is benchmarked.
- **Metric & Cost Asymmetry**: Auditing asymmetric classification costs (dollar value of False Positives vs. False Negatives; PR-AUC vs. ROC-AUC on imbalanced sets).
- **Data Leakage & Split Hygiene**: Temporal splitting on time-dependent data, feature transformations fit strictly on training splits, and online-offline feature consistency.
- **Production Serving & Drift**: Real-time RPC vs. Batch vs. Streaming, model quantization (ONNX, TensorRT), fallback heuristics, drift detection (KS-test, PSI), and safe deployments (shadow, canary, blue/green).

### Track 5: Generative AI, RAG & LLM Systems
📁 [`exercises/05-generative-ai/`](exercises/05-generative-ai/)

- **Retrieval Architecture**: Chunking trade-offs (semantic vs. sliding window vs. hierarchical), hybrid search (dense embeddings + BM25), and re-ranking latency overhead.
- **Deterministic vs. Agentic**: Enforcing state machines and structured JSON outputs over fragile autonomous agent loops where deterministic logic suffices.
- **Evaluation Harnesses (Evals)**: Automated synthetic test suites, deterministic assertion pipelines, and LLM-as-a-judge scoring rubrics before prompt or parameter modifications.
- **Cost & Token Economics**: Token budget modeling, caching strategies, prompt injection defenses, and graceful degradations.

---

## Repository Structure

```text
tech-leadership-study/
├── .agents/
│   └── skills/                   # Curated technical leadership & review skills
├── .rubrics/                     # Grading rubrics (tracked; opening one before you submit defeats the exercise)
├── exercises/
│   ├── 01-product-management/    # Strategy briefs, PRDs, and prioritization exercises
│   ├── 02-system-design/         # High-level architecture, scale math, and NFR exercises
│   ├── 03-data-science/          # Experiment designs, power analyses, and statistical briefs
│   ├── 04-machine-learning/      # Heuristic baselines, feature pipelines, and MLOps exercises
│   └── 05-generative-ai/         # RAG architectures, LLM evals, and prompt systems
├── notes/                        # Reference notes, cheat sheets, and architectural templates
├── AGENTS.md                     # Core curriculum contract & mentorship behavioral engine
├── CLAUDE.md                     # Project instruction entrypoint (imports AGENTS.md)
├── LICENSE                       # MIT License
├── PROGRESS.md                   # Milestone tracker with dates and uncovered blind spots
├── README.md                     # Workspace guide and track overview
├── pyproject.toml                # uv project definition (DuckDB, SciPy, LanceDB, Pydantic)
├── uv.lock                       # Deterministic uv dependency lockfile
└── skills-lock.json              # Agent skill dependency lockfile
```

---

## Hands-On Sandbox & Empirical Prototyping (`uv`)

While 80% of leadership exercises focus on strategic reasoning and architectural documentation in Markdown, 20% benefit from quick empirical verification. The workspace is configured with [`uv`](https://docs.astral.sh/uv/) and zero-server embedded tooling:

- **DuckDB**: Fast in-process analytical SQL for Track 3 (sample ratio mismatch, CUPED simulations).
- **SciPy & NumPy**: Statistical power, distribution shifts, and KS-test/PSI drift calculations for Tracks 3 & 4.
- **LanceDB**: Serverless embedded vector database for Track 5 RAG and hybrid search benchmarks.
- **Pydantic**: Contract and schema definitions for Track 2 APIs.

```bash
# Sync local virtualenv
uv sync

# Run any empirical test or scratchpad script
uv run python path/to/script.py
```

---

## Agent Skill Setup

Skills live in `.agents/skills/`. Claude Code only discovers skills under `.claude/skills/`, and `.claude/` is gitignored, so each clone needs a one-time local link:

```powershell
# Windows (PowerShell)
New-Item -ItemType Directory -Force .claude | Out-Null
New-Item -ItemType Junction -Path .claude\skills -Target (Resolve-Path .agents\skills)
```

```bash
# macOS / Linux
mkdir -p .claude && ln -s ../.agents/skills .claude/skills
```

Restart the session afterwards so `/generate-exercise` and the other skills are picked up.

---

## Feedback & Critique Framework

All work in this repository is reviewed using a standardized 3-part critique:

1. **Strengths**: Technically sound, business-aligned decisions made well.
2. **Blind Spots & Vulnerabilities**: Architectural bottlenecks, unhandled edge cases, unit economic traps, or data leakage risks.
3. **The Next Milestone Challenge**: Exactly 1 or 2 targeted questions forcing you to resolve the design trade-off at the next layer of depth.

---

## How to Engage with the Assistant

1. **Request an Interactive Challenge**:
   - *"Give me a System Design challenge in Track 2 focusing on an event-driven payment ledger."*
   - *"Set up an A/B testing scenario in Track 3 for evaluating a recommendation engine."*
   - *"Give me an MLOps design exercise in Track 4 for real-time fraud scoring."*
2. **Submit a Milestone for Review**:
   - Write your attempt in the matching milestone section of `exercises/<track>/<slug>/submission.md`.
   - Ask: *"Review my Milestone 1 for `01-payment-idempotency`."* The assistant grades it against `.rubrics/<track>/<slug>.md` and updates `PROGRESS.md`.
3. **Run Through Architectural Deep Dives**:
   - Step through the scale math, API schemas, failover strategies, and cost estimates milestone by milestone.
