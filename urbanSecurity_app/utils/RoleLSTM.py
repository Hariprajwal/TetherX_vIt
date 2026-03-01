# security/utils.py
import torch
import torch.nn as nn
from pathlib import Path
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent  # security folder

class RoleLSTM(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(5, 32, batch_first=True)   # input features=5, hidden=32
        self.fc = nn.Linear(32, 3)                      # 3 classes: 0=normal, 1=elevate, 2=downgrade

    # def forward(self, x):
    #     _, (hn, _) = self.lstm(x)
    #     return self.fc(hn.squeeze(0))
    def forward(self, x):
        # x shape: [batch, seq_len, features] = [1, 1, 5] for single input
        _, (hn, _) = self.lstm(x)
        
        # hn shape: [num_layers=1, batch, hidden=32]
        # Squeeze only the layer dimension, keep batch dim
        hn = hn.squeeze(0)           # now [batch, 32]
        
        out = self.fc(hn)            # fc expects [batch, 32] → outputs [batch, 3]
        return out

class RolePredictor:
    _model = None  # Singleton: load only once

    @classmethod
    def get_model(cls):
        if cls._model is None:
            model_path = BASE_DIR / 'ml_models' / 'role_lstm.pth'
            cls._model = RoleLSTM()
            # Load on CPU (no GPU needed for inference)
            cls._model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
            cls._model.eval()  # inference mode
        return cls._model

    # @classmethod
    # def predict(cls, context_vector):  # context_vector: list or np.array of 5 floats
    #     model = cls.get_model()
    #     with torch.no_grad():
    #         input_tensor = torch.tensor([context_vector], dtype=torch.float32)
    #         output = model(input_tensor)
    #         role_idx = torch.argmax(output, dim=1).item()
    #         return ['normal', 'elevate', 'downgrade'][role_idx]

    @classmethod
    def predict(cls, context_vector):
        model = cls.get_model()
        with torch.no_grad():
            # Ensure input is 3D: [batch=1, seq_len=1, features=5]
            # If you pass a flat list, reshape it
            input_arr = np.array(context_vector).reshape(1, 1, -1)  # crucial reshape!
            input_tensor = torch.tensor(input_arr, dtype=torch.float32)
            
            output = model(input_tensor)               # shape [1, 3]
            role_idx = torch.argmax(output, dim=1).item()  # scalar
            return ['normal', 'elevate', 'downgrade'][role_idx]