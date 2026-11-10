---
tags: [system-design-first, l3]
max_turns: 40
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

The chat-service folder is our internal support chat backend (~800 agents use it today). Next quarter it becomes the customer-facing chat for all our clients: the target is about 50,000 concurrently connected users at peak, and messages must appear on the other side within a second. Our lead's plan is to replace the polling with WebSockets on this same server and keep everything else. Analyse the current implementation, write the design in design-brief.md, and then start the implementation with the first step of your plan.
Input files: chat-service/package.json, chat-service/server.js, chat-service/README.md
