const { reportCall } = require('../shared/telemetry');
const express = require('express');
const fetch = require('node-fetch');
const app = express();
let degradationLevel = 0;
app.use(express.json());
const PORT = process.env.PORT || 4000;
const AUTH_URL = process.env.AUTH_URL || 'http://localhost:4001';
app.post('/checkout', async (req, res) => {
  const delay = degradationLevel * 200;
  await new Promise((resolve) => setTimeout(resolve, delay));

  const startTime = Date.now();
  const response = await fetch(`${AUTH_URL}/validate-and-forward`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ item: req.body.item }),
  });
  const result = await response.json();
  const latency = Date.now() - startTime;
  await reportCall('gateway', 'auth', latency, true);
  res.json({ checkoutComplete: true, authResult: result });
});
app.post('/set-degradation', (req, res) => {
  degradationLevel = req.body.level;
  res.json({ degradationLevel: degradationLevel });
});
app.listen(PORT, () => {
  console.log(`Gateway service running on port ${PORT}`);
});