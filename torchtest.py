import torch

# Check if CUDA is available
print("CUDA available:", torch.cuda.is_available())

# Create a tensor on GPU
x = torch.rand(3, 3).cuda()
y = torch.rand(3, 3).cuda()

# Do a computation
z = x @ y  # Matrix multiplication
print("Result on GPU:", z)

# Confirm where it lives
print("Is CUDA tensor:", z.is_cuda)

