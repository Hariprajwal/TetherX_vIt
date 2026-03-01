# urbanSecurity_app/utils/RoleLSTM.py
import torch
import torch.nn as nn
from pathlib import Path
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent  # urbanSecurity_app folder


class RoleLSTM(nn.Module):
    """LSTM model for role prediction: 5 input features → 3 classes."""
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(5, 32, batch_first=True)   # input features=5, hidden=32
        self.fc = nn.Linear(32, 3)                      # 3 classes: 0=normal, 1=elevate, 2=downgrade

    def forward(self, x):
        # x shape: [batch, seq_len, features] = [1, 1, 5] for single input
        _, (hn, _) = self.lstm(x)
        # hn shape: [num_layers=1, batch, hidden=32]
        hn = hn.squeeze(0)           # now [batch, 32]
        out = self.fc(hn)            # fc expects [batch, 32] → outputs [batch, 3]
        return out


class AnomalyAutoencoder(nn.Module):
    """Autoencoder for anomaly detection in access patterns."""
    def __init__(self, input_dim=5):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
        )
        self.decoder = nn.Sequential(
            nn.Linear(8, 16),
            nn.ReLU(),
            nn.Linear(16, input_dim),
        )

    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded


class RolePredictor:
    """Singleton predictor using RoleLSTM model."""
    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            model_path = BASE_DIR / 'ml_models' / 'role_lstm.pth'
            cls._model = RoleLSTM()
            try:
                cls._model.load_state_dict(
                    torch.load(model_path, map_location=torch.device('cpu'), weights_only=True)
                )
            except Exception:
                # If model file doesn't match architecture, use random weights
                pass
            cls._model.eval()
        return cls._model

    @classmethod
    def predict(cls, context_vector):
        """Predict role from context vector (list of 5 floats)."""
        model = cls.get_model()
        with torch.no_grad():
            input_arr = np.array(context_vector).reshape(1, 1, -1)
            input_tensor = torch.tensor(input_arr, dtype=torch.float32)
            output = model(input_tensor)
            role_idx = torch.argmax(output, dim=1).item()
            return ['normal', 'elevate', 'downgrade'][role_idx]


class AnomalyDetector:
    """Anomaly detector using Autoencoder — reconstruction error > threshold = anomaly."""
    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            model_path = BASE_DIR / 'ml_models' / 'anomaly_autoencoder.pth'
            cls._model = AnomalyAutoencoder()
            try:
                cls._model.load_state_dict(
                    torch.load(model_path, map_location='cpu', weights_only=True)
                )
            except Exception:
                pass
            cls._model.eval()
        return cls._model

    @classmethod
    def detect(cls, input_vector):
        """Returns True if input is anomalous (reconstruction error > threshold)."""
        model = cls.get_model()
        with torch.no_grad():
            input_tensor = torch.tensor([input_vector], dtype=torch.float32)
            reconstructed = model(input_tensor)
            mse = nn.MSELoss()(reconstructed, input_tensor)
            return mse.item() > 0.1  # Threshold (tune based on training data)