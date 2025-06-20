
import torch
import torch.nn as nn
import torch.nn.functional as F

class SimCLR_Loss(nn.Module):
    def __init__(self, temperature=0.5):
        super().__init__()
        self.temperature = temperature
        self.criterion = nn.CrossEntropyLoss(reduction="sum")
        self.similarity_f = nn.CosineSimilarity(dim=2)

    def forward(self, z_i, z_j):
        batch_size = z_i.size(0)
        N = 2 * batch_size

        z = torch.cat((z_i, z_j), dim=0)
        sim = self.similarity_f(z.unsqueeze(1), z.unsqueeze(0)) / self.temperature

        mask = torch.ones((N, N), dtype=bool, device=z.device)
        mask.fill_diagonal_(0)
        for i in range(batch_size):
            mask[i, batch_size + i] = 0
            mask[batch_size + i, i] = 0

        sim_i_j = torch.diag(sim, batch_size)
        sim_j_i = torch.diag(sim, -batch_size)
        positives = torch.cat((sim_i_j, sim_j_i), dim=0).reshape(N, 1)
        negatives = sim[mask].reshape(N, -1)

        logits = torch.cat((positives, negatives), dim=1)
        labels = torch.zeros(N, dtype=torch.long, device=z.device)

        return self.criterion(logits, labels) / N

class ProtoNetLoss(nn.Module):
    def __init__(self):
        super().__init__()
        self.criterion = nn.CrossEntropyLoss()

    def forward(self, logits, targets):
        return self.criterion(logits, targets)