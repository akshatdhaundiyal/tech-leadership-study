---
tags: [system-design-first, l3, visualization]
max_turns: 40
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

The chat-service folder is our internal support chat backend (~800 agents use it today). Next quarter it becomes the customer-facing chat for all our clients: about 50,000 concurrently connected users at peak, messages must appear within a second. Design how it should work and draw the architecture: as-is vs to-be in the terminal, and a design folder with the diagrams I can open in a browser. No implementation yet.
Input files: chat-service/package.json, chat-service/server.js, chat-service/README.md
