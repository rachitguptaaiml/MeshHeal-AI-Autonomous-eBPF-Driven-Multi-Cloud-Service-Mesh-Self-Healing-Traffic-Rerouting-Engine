const express = require('express');
const app = express();
let degradationLevel = 0;
app.use(express.json());
const PORT = process.env.PORT || 4004;
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});
app.post('/set-degradation', (req, res) => {
  degradationLevel = req.body.level;
  res.json({ degradationLevel: degradationLevel });
});
app.post('/reserve', (req, res) => {
  const item = req.body.item;
  const delay = degradationLevel * 200;
  setTimeout(() => {
    res.json({ reserved: true, item: item });
  }, delay);
});
app.listen(PORT, () => {
  console.log(`Inventory service running on port ${PORT}`);
});