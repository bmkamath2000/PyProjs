// server/server.js
const express   = require('express');
const http      = require('http');
const { Server } = require('socket.io');
const mqtt      = require('mqtt');
const cors      = require('cors');

const app    = express();
const server = http.createServer(app);
const io     = new Server(server, { cors: { origin: '*' } });

app.use(cors());
app.use(express.json());

// In-memory state (replace with DB later)
let passengerCount = 0;
let history = [];

// ── MQTT ────────────────────────────────────────
const mqttClient = mqtt.connect('mqtt://localhost:1883');

mqttClient.on('connect', () => {
  console.log('MQTT connected');
  mqttClient.subscribe('bus/passengers');
});

mqttClient.on('message', (topic, message) => {
  const data = JSON.parse(message.toString());
  passengerCount = data.count;

  const entry = { ...data, timestamp: new Date().toISOString() };
  history.push(entry);
  if (history.length > 100) history.shift(); // keep last 100

  console.log('MQTT message:', entry);

  // Push to all connected React clients via WebSocket
  io.emit('passengerUpdate', entry);
});

// ── REST endpoints ───────────────────────────────
app.get('/passengers', (req, res) => {
  res.json({ count: passengerCount, busId: 'BUS_01' });
});

app.get('/history', (req, res) => {
  res.json(history);
});

// ── Start ────────────────────────────────────────
server.listen(3001, () => console.log('Server running on http://localhost:3001'));