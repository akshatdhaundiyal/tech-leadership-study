---
tags: [system-design-first, l2]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

We run an HR platform: Django + Postgres + Celery (Redis broker, currently used only for sending emails), React SPA on the front. About 300 companies use it, roughly 20,000 employees in total, the biggest company has ~2,500. We need notifications: when a leave request is approved or rejected, when a candidate moves to a new stage in the ATS, and when a document needs a signature — the employee should see it in the app (bell icon with unread count) and also get an email; push for the mobile app comes later. The product manager wants the bell to update "instantly". Plan how to build this and write the plan to design-brief.md.
