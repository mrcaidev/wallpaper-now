import torch
import torch.nn as nn
import numpy as np

class ImageTextFusion(nn.Module):
    def __init__(self, image_dim=512, text_dim=768, hidden_dim=2048, output_dim=512, use_residual=True):
        super().__init__()
        self.use_residual = use_residual
        self.project = nn.Sequential(
            nn.Linear(image_dim + text_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, output_dim)
        )
        self.text_proj = nn.Sequential(
            nn.Linear(text_dim, 512),
            nn.ReLU(),
            nn.Linear(512, 512)
        )

    def forward(self, image_vec, text_vec):
        x = torch.cat([image_vec, text_vec], dim=-1)
        fused = self.project(x)
        if self.use_residual:
            fused += image_vec[:, :fused.shape[1]] * 0.5 + text_vec[:, :fused.shape[1]] * 0.5
        fused = nn.functional.normalize(fused, p=2, dim=-1)
        return fused
