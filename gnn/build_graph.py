import json
import torch
from torch_geometric.data import Data
SERVICES = ["gateway", "auth", "orders", "payments", "inventory"]
SERVICE_INDEX = {name: i for i, name in enumerate(SERVICES)}
def build_graph_from_sample(sample):
    edge_list = []
    edge_latencies = []

    for entry in sample['telemetry']:
        source_idx = SERVICE_INDEX[entry['source']]
        target_idx = SERVICE_INDEX[entry['target']]
        edge_list.append([source_idx, target_idx])
        edge_latencies.append(entry['latencyMs'])

    edge_index = torch.tensor(edge_list, dtype=torch.long).t()
    edge_attr = torch.tensor(edge_latencies, dtype=torch.float).unsqueeze(1)

    return edge_index, edge_attr
def build_dataset(samples):
    graph_list = []

    for sample in samples:
        edge_index, edge_attr = build_graph_from_sample(sample)
        label_idx = SERVICE_INDEX[sample['degraded_service']]
        label = torch.tensor([label_idx], dtype=torch.long)

        num_nodes = len(SERVICES)
        node_latency = [0.0] * num_nodes
        node_error_rate = [0.0] * num_nodes
        node_out_latency = [0.0] * num_nodes
        node_call_count = [0.0] * num_nodes

        for entry in sample['telemetry']:
            target_idx = SERVICE_INDEX[entry['target']]
            source_idx = SERVICE_INDEX[entry['source']]
            node_latency[target_idx] = entry['latencyMs']
            node_error_rate[target_idx] = entry.get('errorRate', 0.0)
            node_out_latency[source_idx] = entry['latencyMs']
            node_call_count[target_idx] += 1.0

        # z-score normalize latency
        import statistics
        all_lat = node_latency + node_out_latency
        mean_lat = statistics.mean(all_lat) if any(all_lat) else 0
        std_lat = statistics.stdev(all_lat) if len(set(all_lat)) > 1 else 1
        node_latency = [(v - mean_lat) / std_lat for v in node_latency]
        node_out_latency = [(v - mean_lat) / std_lat for v in node_out_latency]

        x = torch.tensor(
            list(zip(node_latency, node_error_rate, node_out_latency, node_call_count)),
            dtype=torch.float
        )

        graph = Data(x=x, edge_index=edge_index, edge_attr=edge_attr, y=label)
        graph_list.append(graph)

    return graph_list