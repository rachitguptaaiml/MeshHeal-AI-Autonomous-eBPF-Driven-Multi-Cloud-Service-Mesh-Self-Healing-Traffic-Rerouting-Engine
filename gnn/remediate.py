import torch
import requests
import subprocess
import json
import time
import statistics
from datetime import datetime
from build_graph import build_graph_from_sample, SERVICE_INDEX, SERVICES
from model import MeshHealGNN

# --- Config ---
MODEL_PATH = "meshheal_gnn.pth"
TELEMETRY_URL = "http://localhost:5000/telemetry"
AUDIT_LOG_PATH = "audit_log.json"
NUM_NODE_FEATURES = 4
NUM_CLASSES = 5

SERVICE_PORTS = {
    "gateway":   "http://localhost:4000",
    "auth":      "http://localhost:4001",
    "orders":    "http://localhost:4002",
    "payments":  "http://localhost:4003",
    "inventory": "http://localhost:4004",
}

# --- Audit Log ---
def write_audit(entry):
    try:
        with open(AUDIT_LOG_PATH, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"Audit log error: {e}")

# --- Load Model ---
def load_model():
    model = MeshHealGNN(num_node_features=NUM_NODE_FEATURES, num_classes=NUM_CLASSES)
    model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    model.eval()
    return model

# --- Fetch metrics from telemetry collector ---
def fetch_metrics():
    try:
        r = requests.get(TELEMETRY_URL)
        data = r.json()
        if not data:
            return []
        seen = {}
        for entry in reversed(data):
            key = (entry['source'], entry['target'])
            if key not in seen:
                seen[key] = {
                    "source": entry['source'],
                    "target": entry['target'],
                    "latencyMs": entry['latencyMs'],
                    "errorRate": 0.0 if entry.get('success', True) else 1.0
                }
        return list(seen.values())
    except Exception as e:
        print(f"Error fetching telemetry: {e}")
        return []

# --- Run GNN inference ---
def predict_degraded_service(model, telemetry):
    sample = {"telemetry": telemetry}
    edge_index, edge_attr = build_graph_from_sample(sample)
    num_nodes = len(SERVICES)
    node_latency = [0.0] * num_nodes
    node_error_rate = [0.0] * num_nodes
    node_out_latency = [0.0] * num_nodes
    node_call_count = [0.0] * num_nodes
    for entry in telemetry:
        target_idx = SERVICE_INDEX[entry['target']]
        source_idx = SERVICE_INDEX[entry['source']]
        node_latency[target_idx] = entry['latencyMs']
        node_error_rate[target_idx] = entry.get('errorRate', 0.0)
        node_out_latency[source_idx] = entry['latencyMs']
        node_call_count[target_idx] += 1.0
    all_lat = node_latency + node_out_latency
    mean_lat = statistics.mean(all_lat) if any(all_lat) else 0
    std_lat = statistics.stdev(all_lat) if len(set(all_lat)) > 1 else 1
    node_latency = [(v - mean_lat) / std_lat for v in node_latency]
    node_out_latency = [(v - mean_lat) / std_lat for v in node_out_latency]
    x = torch.tensor(
        list(zip(node_latency, node_error_rate, node_out_latency, node_call_count)),
        dtype=torch.float
    )
    batch = torch.zeros(x.size(0), dtype=torch.long)
    with torch.no_grad():
        out = model(x, edge_index, batch)
    predicted_idx = out.argmax(dim=1).item()
    return SERVICES[predicted_idx]

# --- Remediation actions ---
def remediate(service, dry_run=True):
    timestamp = datetime.now().isoformat()

    # DRY RUN — log what we would do
    dry_run_entry = {
        "timestamp": timestamp,
        "phase": "DRY_RUN",
        "service": service,
        "action": "reset_degradation",
        "status": "pending"
    }
    write_audit(dry_run_entry)
    print(f"[{timestamp}] [DRY-RUN] Would reset degradation on: {service}")

    if dry_run:
        return

    # EXECUTE — reset degradation via API
    port = SERVICE_PORTS.get(service)
    if not port:
        print(f"[{timestamp}] Unknown service port for: {service}")
        return

    try:
        r = requests.post(
            f"{port}/set-degradation",
            json={"level": 0},
            timeout=3
        )
        success = r.status_code == 200
    except Exception as e:
        success = False
        print(f"[{timestamp}] Failed to reach {service}: {e}")

    # Also restart container as backup
    container = f"meshheal-ai-{service}-1"
    restart_result = subprocess.run(
        ["docker", "restart", container],
        capture_output=True, text=True
    )
    container_ok = restart_result.returncode == 0

    # AUDIT — log result
    result_entry = {
        "timestamp": datetime.now().isoformat(),
        "phase": "EXECUTED",
        "service": service,
        "action": "reset_degradation",
        "degradation_reset": success,
        "container_restarted": container_ok,
        "status": "success" if (success or container_ok) else "failed"
    }
    write_audit(result_entry)
    print(f"[{datetime.now()}] [EXECUTED] degradation_reset={success} container_restarted={container_ok}")

# --- Main loop ---
if __name__ == "__main__":
    print("Loading MeshHeal-AI model...")
    model = load_model()
    print("Model loaded. Starting monitoring loop...\n")

    cycle = 0
    while True:
        cycle += 1
        telemetry = fetch_metrics()
        if len(telemetry) == 0:
            print(f"[{datetime.now()}] No telemetry data, skipping...")
        else:
            degraded = predict_degraded_service(model, telemetry)
            # First cycle: dry run. After that: execute
            dry_run = (cycle == 1)
            remediate(degraded, dry_run=dry_run)

        time.sleep(30)