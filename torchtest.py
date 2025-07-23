import torch
import torchvision
print("TorchVision version:", torchvision.__version__)
print("TorchVision compiled with CUDA:", torchvision._C._is_cuda_build)

print("Torch built with CUDA:", torch.backends.cuda.is_built())
print("CUDA available:", torch.cuda.is_available())
print("CUDA version (from torch):", torch.version.cuda)
