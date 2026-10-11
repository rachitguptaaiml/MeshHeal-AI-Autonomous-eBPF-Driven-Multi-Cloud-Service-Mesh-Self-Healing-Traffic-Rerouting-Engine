const { reportCall } = require('../shared/telemetry');
const express = require('express');
const fetch = require('node-fetch');
const app = express();
let degradationLevel = 0;
app.use(express.json());
const PORT = process.env.PORT || 4001;
const ORDERS_URL = process.env.ORDERS_URL || 'http://localhost:4002';
app.post('/validate-and-forward', async (req, res) => {
  const tokenValid = true;

  if (!tokenValid) {
    return res.status(401).json({ error: 'invalid token' });
  }

  const delay = degradationLevel * 200;
  await new Promise((resolve) => setTimeout(resolve, delay));

  const startTime = Date.now();
  const response = await fetch(`${ORDERS_URL}/place`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ item: req.body.item }),
  });
  const result = await response.json();
  const latency = Date.now() - startTime;
  await reportCall('auth', 'orders', latency, true);
  res.json({ authorized: true, ordersResult: result });
});
app.post('/set-degradation', (req, res) => {
  degradationLevel = req.body.level;
  res.json({ degradationLevel: degradationLevel });
});
app.listen(PORT, () => {
  console.log(`Auth service running on port ${PORT}`);
});
