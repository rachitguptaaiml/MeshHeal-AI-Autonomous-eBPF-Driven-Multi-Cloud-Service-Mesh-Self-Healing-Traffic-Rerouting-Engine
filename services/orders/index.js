const { reportCall } = require('../shared/telemetry');
const express = require('express');
const fetch = require('node-fetch');
const app = express();
let degradationLevel = 0;
app.use(express.json());
const PORT = process.env.PORT || 4002;
const PAYMENTS_URL = process.env.PAYMENTS_URL || 'http://localhost:4003';
app.post('/place', async (req, res) => {
  const delay = degradationLevel * 200;
  await new Promise((resolve) => setTimeout(resolve, delay));

  const startTime = Date.now();
  const response = await fetch(`${PAYMENTS_URL}/charge`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ item: req.body.item }),
  });
  const result = await response.json();
  const latency = Date.now() - startTime;
  await reportCall('orders', 'payments', latency, true);
  res.json({ ordered: true, paymentsResult: result });
});
app.post('/set-degradation', (req, res) => {
  degradationLevel = req.body.level;
  res.json({ degradationLevel: degradationLevel });
});
app.listen(PORT, () => {
  console.log(`Orders service running on port ${PORT}`);
});