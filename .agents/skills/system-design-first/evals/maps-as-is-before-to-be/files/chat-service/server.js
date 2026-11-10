const express = require('express');

const app = express();
app.use(express.json());

// room id -> array of messages, newest last. Lost on restart.
const rooms = new Map();
let nextId = 1;

const getRoom = (id) => {
  if (!rooms.has(id)) rooms.set(id, []);
  return rooms.get(id);
};

// Polling endpoint: returns messages with id > since.
app.get('/rooms/:id/messages', (req, res) => {
  const since = Number(req.query.since || 0);
  const messages = getRoom(req.params.id).filter((m) => m.id > since);
  res.json({ messages });
});

app.post('/rooms/:id/messages', (req, res) => {
  const { authorId, text } = req.body;
  if (!authorId || !text) return res.status(400).json({ error: 'authorId and text are required' });
  const message = { id: nextId++, roomId: req.params.id, authorId, text, createdAt: Date.now() };
  getRoom(req.params.id).push(message);
  res.status(201).json(message);
});

app.get('/health', (_req, res) => res.send('ok'));

app.listen(process.env.PORT || 3000, () => console.log('chat-service listening'));
