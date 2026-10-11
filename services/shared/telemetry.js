const fetch = require('node-fetch');
const COLLECTOR_URL = process.env.TELEMETRY_URL || 'http://localhost:5000/report';
async function reportCall(sourceService, targetService, latencyMs, success) {
  const packetLossPercent = (Math.random() * 2).toFixed(2);
  const retransmitPercent = (Math.random() * 1.5).toFixed(2);

  const payload = {
    source: sourceService,
    target: targetService,
    latencyMs: latencyMs,
    packetLossPercent: parseFloat(packetLossPercent),
    retransmitPercent: parseFloat(retransmitPercent),
    success: success,
    timestamp: Date.now(),
  };

  try {
    await fetch(COLLECTOR_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  } catch (err) {
    console.log('Telemetry report failed:', err.message);
  }
}
module.exports = { reportCall };