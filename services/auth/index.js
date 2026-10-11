const express = require('express');
const fetch = require('node-fetch');
const app = express();
app.use(express.json());
const PORT = process.env.PORT || 4001;
const ORDERS_URL = process.env.ORDERS_URL || 'http://localhost:4002';
app.post('/validate-and-forward', async (req, res) => {
  const tokenValid = true;

  if (!tokenValid) {
    return res.status(401).json({ error: 'invalid token' });
  }

  const response = await fetch(`${ORDERS_URL}/place`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ item: req.body.item }),
  });
  const result = await response.json();
  res.json({ authorized: true, ordersResult: result });
});
app.listen(PORT, () => {
  console.log(`Auth service running on port ${PORT}`);
});
