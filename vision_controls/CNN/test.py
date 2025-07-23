from ultralytics import YOLO
import cv2
import os
import torch

try:
    # Verify GPU availability
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available. Check GPU setup.")
    print(f"Using GPU: {torch.cuda.get_device_name(0)}")

    # Load the pre-trained YOLO model
    model_path = "yolo/train/weights/best.pt"  # Update with correct path if needed
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file {model_path} not found")
    model = YOLO(model_path).cuda()  # Explicitly move model to GPU
    print(f"Model device: {next(model.model.parameters()).device}")

    # Path to the input image
    image_path = "test.jpg"  # Update with correct path
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file {image_path} not found")

    # Clear GPU memory
    torch.cuda.empty_cache()

    # Perform inference on the image using GPU
    results = model(image_path, device="cuda")
    print(f"Inference completed on: {results[0].boxes.device}")

    # Process results
    for result in results:
        annotated_image = result.plot()  # Add bounding boxes and labels
        output_path = "output_image.jpg"
        cv2.imwrite(output_path, annotated_image)
        print(f"Output image saved as {output_path}")

        # Optionally display the image
        cv2.imshow("YOLO Detection", annotated_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # Print detection details
        for detection in result.boxes:
            class_id = int(detection.cls)
            class_name = model.names[class_id]
            confidence = float(detection.conf)
            bbox = [float(coord) for coord in detection.xyxy[0].cpu().numpy().tolist()]
            print(f"Detected: {class_name} (Confidence: {confidence:.2f}, BBox: {[round(coord, 2) for coord in bbox]})")

except FileNotFoundError as e:
    print(f"Error: {e}")
except RuntimeError as e:
    print(f"GPU Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")