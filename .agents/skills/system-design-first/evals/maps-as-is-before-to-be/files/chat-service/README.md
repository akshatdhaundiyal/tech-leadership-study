# chat-service

Internal support chat backend. Single Node process behind nginx, deployed on one VM.
Clients poll `GET /rooms/:id/messages?since=<id>` every 5 seconds.
Messages live in process memory and are lost on restart (acceptable so far: ~800 support agents, ~2k messages/day).
