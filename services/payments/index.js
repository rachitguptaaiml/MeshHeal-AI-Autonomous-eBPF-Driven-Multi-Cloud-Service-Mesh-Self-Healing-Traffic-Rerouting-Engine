const { reportCall } = require('../shared/telemetry');
const express = require('express');
const fetch = require('node-fetch');
const app = express();
let degradationLevel = 0;
app.use(express.json());
const PORT = process.env.PORT || 4003;
const INVENTORY_URL = process.env.INVENTORY_URL || 'http://localhost:4004';
app.post('/charge', async (req, res) => {
  const delay = degradationLevel * 200;
  await new Promise((resolve) => setTimeout(resolve, delay));

  const startTime = Date.now();
  const response = await fetch(`${INVENTORY_URL}/reserve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ item: req.body.item }),
  });
  const result = await response.json();
  const latency = Date.now() - startTime;
  await reportCall('payments', 'inventory', latency, true);
  res.json({ charged: true, inventoryResult: result });
});
app.post('/set-degradation', (req, res) => {
  degradationLevel = req.body.level;
  res.json({ degradationLevel: degradationLevel });
});
app.listen(PORT, () => {
  console.log(`Payments service running on port ${PORT}`);
});