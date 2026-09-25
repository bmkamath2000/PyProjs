// server.js
const express = require('express');
const mqtt    = require('mqtt');

const app    = express();
const client = mqtt.connect('mqtt://localhost:1883');

let latestCount = { count: 0, busId: null };

// ── MQTT subscriber ──────────────────────────────
client.on('connect', () => {
  console.log('Connected to MQTT broker');
  client.subscribe('bus/passengers', (err) => {
    if (!err) console.log('Subscribed to bus/passengers');
  });
});

client.on('message', (topic, message) => {
  const data = JSON.parse(message.toString());  // { count: 5, busId: "BUS_01" }
  console.log(`[MQTT] ${topic}:`, data);
  
  latestCount = data;

  // ← here you can: save to DB, emit via WebSocket, trigger alerts, etc.
});

// ── REST endpoint ────────────────────────────────
app.get('/passengers', (req, res) => {
  res.json(latestCount);
});

app.listen(3000, () => console.log('Server on port 3000'));