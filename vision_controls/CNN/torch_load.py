import torch
import cv2
import numpy as np
import torchvision.ops as ops
from PIL import Image
import yaml
import os
# Load checkpoint
checkpoint = torch.load("oculus_s/my_model.pt", map_location='cpu', weights_only=False)

# Choose the weights to load: EMA weights if available (better), else regular model weights
weights = checkpoint['ema'] if checkpoint.get('ema') is not None else checkpoint['model']

# weights might be a PyTorch model or a state_dict, let's check:
if hasattr(weights, 'state_dict'):
    # If it's a model, get its state dict
    state_dict = weights.state_dict()
else:
    # Otherwise, assume it's already a state dict
    state_dict = weights

# Now load model architecture YAML
import yaml
from models.yolo import Model  # Make sure you have YOLOv5 repo in your PYTHONPATH or current dir

with open('models/yolov5s.yaml') as f:  # adjust if you used yolov5s, yolov5l, etc.
    cfg = yaml.safe_load(f)

# Instantiate model
model = Model(cfg=cfg)

# Sometimes keys have 'module.' prefix from DataParallel, remove if necessary
clean_state_dict = {k.replace('module.', ''): v for k, v in state_dict.items()}

# Load weights
model.load_state_dict(clean_state_dict, strict=False)
model.eval()

# Now model is ready for inference on CPU or move to GPU if available
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model.to(device)

print("Loaded on: ",next(model.parameters()).device)


######################################



