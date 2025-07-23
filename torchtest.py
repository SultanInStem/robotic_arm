import torch
import torchvision
from torchvision.ops import nms

print("Torch version:", torch.__version__)
print("TorchVision version:", torchvision.__version__)
print("CUDA available:", torch.cuda.is_available())

# Try a simple torchvision op (NMS)
boxes = torch.tensor([
    [10, 10, 20, 20],
    [12, 12, 22, 22],
    [30, 30, 40, 40]
], dtype=torch.float32).cuda()

scores = torch.tensor([0.9, 0.85, 0.75], dtype=torch.float32).cuda()

# Non-maximum suppression test
indices = nms(boxes, scores, iou_threshold=0.5)
print("NMS output indices:", indices)

