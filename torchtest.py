import torch
print("Torch built with CUDA:", torch.backends.cuda.is_built())
print("CUDA available:", torch.cuda.is_available())
print("CUDA version (from torch):", torch.version.cuda)
