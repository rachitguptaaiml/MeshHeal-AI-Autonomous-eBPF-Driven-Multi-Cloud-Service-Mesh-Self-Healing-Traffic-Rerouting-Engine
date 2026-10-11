const express = require('express');
const app = express();
app.use(express.json());
const PORT = process.env.PORT || 5000;
const telemetryLog = [];
app.post('/report', (req, res) => {
  const entry = {
    source: req.body.source,
    target: req.body.target,
    latencyMs: req.body.latencyMs,
    success: req.body.success,
    timestamp: Date.now(),
  };
  telemetryLog.push(entry);
  console.log(`[telemetry] ${entry.source} -> ${entry.target} | ${entry.latencyMs}ms | success: ${entry.success}`);
  res.json({ received: true });
});
app.get('/telemetry', (req, res) => {
  res.json(telemetryLog);
});
app.listen(PORT, () => {
  console.log(`Telemetry collector running on port ${PORT}`);
});