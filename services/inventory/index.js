const express = require('express');
const app = express();
app.use(express.json());
const PORT = process.env.PORT || 4004;
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});
app.post('/reserve', (req, res) => {
  const item = req.body.item;
  res.json({ reserved: true, item: item });
});
app.listen(PORT, () => {
  console.log(`Inventory service running on port ${PORT}`);
});