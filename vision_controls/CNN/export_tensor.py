from ultralytics import YOLO
import torch
import os

try:
    # Verify GPU availability
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available. Check GPU setup.")
    print(f"Using GPU: {torch.cuda.get_device_name(0)}")

    # Model path
    model_path = "yolo/train/weights/best.pt"  # Update with correct path
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file {model_path} not found")

    # Output path for TensorRT engine
    engine_path = "best.engine"

    # Load model
    model = YOLO(model_path)

    # Export to TensorRT with FP16 precision (recommended for Jetson Orin)
    print("Exporting model to TensorRT...")
    model.export(
        format="engine",  # Export format
        device="cuda",   # Use GPU for export
        half=True,       # FP16 precision for Orin
        workspace=4      # Set workspace size (in GB) to avoid memory issues
    )
    print(f"TensorRT engine saved as {engine_path}")

except FileNotFoundError as e:
    print(f"Error: {e}")
except RuntimeError as e:
    print(f"GPU Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")