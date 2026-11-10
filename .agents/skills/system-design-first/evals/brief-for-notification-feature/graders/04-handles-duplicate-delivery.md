---
type: llm
focus: trace
weight: 1
---

design-brief.md addresses duplicate delivery explicitly: an idempotency/dedup key, a unique constraint on (recipient, event) or equivalent, so that a retried task does not send the same email or create a duplicate notification
