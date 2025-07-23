import torch
import torchvision

def test_torch_and_torchvision():
    print(f"torch version: {torch.__version__}")
    print(f"torchvision version: {torchvision.__version__}")
    
    # Check CUDA availability
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA device: {torch.cuda.get_device_name(0)}")
    
    # Create a dummy tensor and move it to GPU (if available)
    x = torch.randn(3, 3)
    if torch.cuda.is_available():
        x = x.cuda()
    print("Tensor on device:", x.device)
    
    # Load a pretrained model from torchvision
    model = torchvision.models.resnet18(pretrained=False)
    model.eval()
    
    # Move model to GPU if CUDA is available
    if torch.cuda.is_available():
        model = model.cuda()
    
    # Run a dummy input through the model
    dummy_input = torch.randn(1, 3, 224, 224)
    if torch.cuda.is_available():
        dummy_input = dummy_input.cuda()
    
    with torch.no_grad():
        output = model(dummy_input)
    
    print("Output shape:", output.shape)
    print("Test completed successfully.")

