# MeshHeal-AI 🧠⚡

> An eBPF-inspired self-healing service mesh engine powered by a Graph Neural Network — built as a 4-week college project at GLA University.

---

## 🎯 What It Does

MeshHeal-AI continuously monitors a microservice mesh, detects degrading services using a GNN trained on telemetry data, and automatically remediates faults — all within seconds, with a full audit trail.

**Demo flow:**
1. A service degrades (high latency, cascading failures)
2. Telemetry flows to the collector
3. GNN predicts which service is at fault
4. System auto-heals: resets degradation + restarts container
5. Live dashboard shows the detection and remediation in real time

---

## 🏗️ Architecture

```
Phone/Browser
     │
     ▼
 Envoy Proxy (port 8080)        ← Layer 7 proxy, circuit breaker
     │
     ▼
 Gateway → Auth → Orders → Payments → Inventory
     │         (microservice chain)
     │
     ▼
 Telemetry Collector (port 5000)
     │
     ▼
 GNN Model (MeshHealGNN)        ← Graph Neural Network
     │
     ▼
 remediate.py                   ← Auto-healing engine
     │
     ├── reset degradation via /set-degradation API
     ├── restart Docker container
     └── write to audit_log.json
     │
     ▼
 Live Dashboard (dashboard.html)
 Payment Demo  (pay.html)
```

---

## 🗂️ Project Structure

```
meshheal-ai/
├── services/
│   ├── gateway/          Express microservice (entry point)
│   ├── auth/             Auth & forwarding service
│   ├── orders/           Order processing service
│   ├── payments/         Payment service (degradation target)
│   ├── inventory/        Inventory reservation service
│   └── telemetry-collector/  Metrics ingestion (POST /report, GET /telemetry)
├── gnn/
│   ├── build_graph.py    Graph construction from telemetry samples
│   ├── collect_data.py   Training data generation
│   ├── model.py          MeshHealGNN (GCNConv + global_mean_pool)
│   ├── train.py          Model training script
│   ├── remediate.py      Auto-healing loop (dry-run + execute)
│   ├── audit_server.py   HTTP server exposing audit_log.json
│   ├── training_data.json 75 labeled graph samples
│   └── meshheal_gnn.pth  Trained model weights
├── envoy/
│   └── envoy.yaml        Envoy proxy config (circuit breaker, routing)
├── docker-compose.yml    Full stack orchestration
├── dashboard.html        Live monitoring dashboard
├── pay.html              Fake payment demo page
└── server.py             Serves pay.html + proxies to Envoy
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Microservices | Node.js + Express |
| Containerization | Docker + Docker Compose |
| Proxy | Envoy v1.28 |
| ML Framework | PyTorch + PyTorch Geometric |
| GNN Architecture | GCNConv → ReLU → GlobalMeanPool → Linear |
| Frontend | HTML + Chart.js |
| Telemetry | Custom Node.js collector |

---

## 🧠 GNN Model Details

**Architecture:** `MeshHealGNN`
- Input: 4 node features per service (inbound latency, error rate, outbound latency, call count) — z-score normalized
- Layer 1: GCNConv (4 → 16)
- Pooling: Global Mean Pool
- Output: Linear (16 → 5 classes)

**Training:**
- Dataset: 75 labeled graph snapshots (degradation scenarios)
- Split: 80/20 train/test
- Optimizer: Adam (lr=0.01)
- Loss: CrossEntropyLoss
- Epochs: 200

**Results:**
- Initial accuracy (1 feature, no normalization): **26.67%**
- Final accuracy (4 features + z-score normalization): **93.33%**

---

## 🚀 Setup & Running

### Prerequisites
- Docker Desktop
- Python 3.9+ with pip
- Node.js 18+

### 1. Clone & Start Services
```bash
git clone https://github.com/rachitguptaaiml/meshheal-ai
cd meshheal-ai
docker-compose up -d --build
```

### 2. Set Up Python Environment
```bash
cd gnn
python -m venv gnn-env
gnn-env\Scripts\activate        # Windows
pip install torch torch-geometric requests
```

### 3. Train the GNN
```bash
python train.py
# Output: Test accuracy: 93.33% (14/15)
# Saves: meshheal_gnn.pth
```

### 4. Start Remediation Engine
```bash
python remediate.py
```

### 5. Start Audit Server (separate terminal)
```bash
python audit_server.py
```

### 6. Open Dashboard
Open `dashboard.html` in your browser.

### 7. Run Payment Demo
```bash
cd D:\meshheal-ai
python server.py
```
Open `http://localhost:8081/pay`

---

## 🎮 Demo Script

**Trigger a degradation:**
```bash
# Degrade payments service to 80%
curl -X POST http://localhost:4003/set-degradation \
  -H "Content-Type: application/json" \
  -d "{\"level\": 0.8}"

# Send traffic through the mesh
curl -X POST http://localhost:8080/checkout \
  -H "Content-Type: application/json" \
  -d "{\"item\": \"test\"}"
```

**Watch:**
- Dashboard shows latency spike + risk scores turn red
- remediate.py detects fault, logs dry-run, executes heal
- audit_log.json records every decision
- Payment page shows "⚡ Self-Healed · Payment Succeeded"

---

## 📊 Metrics

| Metric | Value |
|---|---|
| GNN Detection Accuracy | 93.33% |
| Remediation Success Rate | 100% (from audit log) |
| Avg Detection Latency | ~30s (monitoring loop interval) |
| Services Monitored | 5 |
| Audit Entries per Remediation | 2 (DRY_RUN + EXECUTED) |

---

## 🔍 What's Real vs Simulated

| Component | Status | Notes |
|---|---|---|
| Microservices | ✅ Real | Running in Docker |
| Telemetry collection | ✅ Real | Live HTTP metrics |
| GNN inference | ✅ Real | PyTorch model |
| Docker remediation | ✅ Real | Actual container restarts |
| Envoy proxy | ✅ Real | Layer 7 routing + circuit breaker |
| eBPF | 🔄 Simulated | Replaced by HTTP telemetry collector |
| Degradation injection | 🔄 Simulated | `/set-degradation` API |

> **Note:** True eBPF requires a Linux kernel ≥ 5.8 and root access. We simulate equivalent telemetry via a custom HTTP collector, which provides the same data shape (latency, error rate, call counts) that eBPF would capture at the kernel level.

---

## 🔮 Future Scope

- **Real eBPF integration** using `libbpf` on Linux for kernel-level telemetry
- **InfraMorph** — dynamic topology rewriting based on GNN predictions
- **ChaosBrain** — autonomous chaos engineering using the GNN to find failure modes
- **Multi-cluster support** — extend to Kubernetes with Istio service mesh
- **Streaming inference** — replace polling loop with event-driven remediation

---

## 👨‍💻 Author

**Rachit Gupta**  
B.Tech CSE (AI/ML) · GLA University · 2024–2028  
GitHub: [@rachitguptaaiml](https://github.com/rachitguptaaiml)

---

*Built with 🧠 + ☕ over 4 weeks*
