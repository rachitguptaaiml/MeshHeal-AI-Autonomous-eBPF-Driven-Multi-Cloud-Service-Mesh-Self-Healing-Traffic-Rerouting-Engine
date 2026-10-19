import json
import torch
import random
from torch_geometric.loader import DataLoader
from build_graph import build_dataset, SERVICES
from model import MeshHealGNN
data = json.load(open('training_data.json'))
graphs = build_dataset(data)
random.shuffle(graphs)

split_point = int(len(graphs) * 0.8)
train_graphs = graphs[:split_point]
test_graphs = graphs[split_point:]

print(f"Training on {len(train_graphs)} graphs, testing on {len(test_graphs)}")
model = MeshHealGNN(num_node_features=1, num_classes=5)
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
loss_function = torch.nn.CrossEntropyLoss()
train_loader = DataLoader(train_graphs, batch_size=8, shuffle=True)

for epoch in range(200):
    total_loss = 0
    for batch in train_loader:
        optimizer.zero_grad()
        out = model(batch.x, batch.edge_index, batch.batch)
        loss = loss_function(out, batch.y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    if epoch % 40 == 0:
        print(f"Epoch {epoch}, Loss: {total_loss:.4f}")
correct = 0
for graph in test_graphs:
    batch_tensor = torch.zeros(graph.x.size(0), dtype=torch.long)
    out = model(graph.x, graph.edge_index, batch_tensor)
    predicted = out.argmax(dim=1).item()
    actual = graph.y.item()
    if predicted == actual:
        correct += 1


accuracy = correct / len(test_graphs)
print(f"Test accuracy: {accuracy:.2%} ({correct}/{len(test_graphs)})")