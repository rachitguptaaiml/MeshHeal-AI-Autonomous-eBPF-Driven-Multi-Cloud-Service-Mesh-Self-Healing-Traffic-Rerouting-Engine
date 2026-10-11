const { reportCall } = require('../shared/telemetry');
const express = require('express');
const fetch = require('node-fetch');
const app = express();
app.use(express.json());
const PORT = process.env.PORT || 4000;
const AUTH_URL = process.env.AUTH_URL || 'http://localhost:4001';
app.post('/checkout', async (req, res) => {
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
app.listen(PORT, () => {
  console.log(`Gateway service running on port ${PORT}`);
});