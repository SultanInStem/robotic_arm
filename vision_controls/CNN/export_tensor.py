from ultralytics import YOLO
import torch
import os
model = YOLO("yolo/train/weights/best.pt")
model.export(format="onnx", device="cuda")
