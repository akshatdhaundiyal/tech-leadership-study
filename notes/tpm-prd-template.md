# Technical PRD Template & Defense Guide

A problem-first Product Requirements Document template optimized for Technical Product Managers (TPMs).

---

## 1. Problem Space & Jobs-to-be-Done (JTBD)
- **Target Persona**: Who experiences this pain directly? (e.g. Enterprise DevOps Engineer, Merchant Reconciliation Analyst).
- **Core JTBD**: "When [context/trigger], I want to [motivation/action], so that [desired outcome]."
- **Current Workarounds**: How do users solve this today without our feature? (e.g., custom scripts, manual CSV reconciliation).
- **Quantified Cost of Inaction**: What does the company or customer lose by doing nothing? (e.g., $400k/quarter in manual labor, 3.2% churn).

---

## 2. Metric Defensibility & Success Criteria
- **North Star Metric**: Single primary metric defining customer value realization.
- **Input Metrics**: Controllable levers driving the North Star (e.g., latency, error rate, onboarding step completion).
- **Guardrail Metrics**: What metrics MUST NOT degrade? (e.g., infrastructure COGS per MAU, unsubscribe rate, checkout conversion).
- **Perverse Incentive Audit**: How could engineering, sales, or users game this metric? (e.g., artificially boosting clicks via clickbait UI while tanking 30-day retention).

---

## 3. Scope & Prioritization (RICE Framework)

$$\text{RICE Score} = \frac{\text{Reach} \times \text{Impact} \times \text{Confidence}}{\text{Effort}}$$

- **Explicit Non-Goals (Scope Cut)**: What are we explicitly NOT building in V1?
- **P0 Requirements**: Hard launch blockers.
- **P1 Requirements**: Fast follows scheduled for subsequent sprint.

---

## 4. Technical Constraints & Data Model
- **API Contracts & Integrations**: Upstream and downstream dependencies.
- **SLA & Latency Requirements**: P95/P99 latency boundaries.
- **Privacy & Compliance**: GDPR, SOC2, PCI-DSS data retention and deletion policies.
