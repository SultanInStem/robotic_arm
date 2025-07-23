import sys
sys.path.insert(0, 'yolov5')  # if you're outside yolov5 folder

import torch
from models.yolo import Model
import yaml

# Load config
with open('models/yolov5m.yaml') as f:
    cfg = yaml.safe_load(f)

# Build model
model = Model(cfg=cfg)
checkpoint = torch.load("my_model.pt", map_location='cpu')

# This is the fix 👇
if 'model' in checkpoint:
    state_dict = checkpoint['model']
else:
    state_dict = checkpoint  # fallback if it's a pure state_dict

model.load_state_dict(state_dict)
model.eval()
