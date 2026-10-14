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
        x = torch.ones((num_nodes, 1), dtype=torch.float)

        graph = Data(x=x, edge_index=edge_index, edge_attr=edge_attr, y=label)
        graph_list.append(graph)

    return graph_list