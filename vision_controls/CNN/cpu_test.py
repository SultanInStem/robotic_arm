from ultralytics import YOLO
import cv2
import os

# Load the pre-trained YOLO model
model = YOLO("yolo/train/weights/best.pt")  # Replace with the path to your model if not in the current directory

# Path to the input image
image_path = "test.jpg"  # Replace with your image file path

# Perform inference on the image
results = model(image_path, device="cpu", weights_only=False)

# Process results
# Results are returned as a list of detections
for result in results:
    # Get the annotated image with bounding boxes
    annotated_image = result.plot()  # This adds bounding boxes and labels to the image

    # Save the output image
    output_path = "output_image.jpg"
    cv2.imwrite(output_path, annotated_image)
    print(f"Output image saved as {output_path}")

    # Optionally, display the image
    cv2.imshow("YOLO Detection", annotated_image)
    cv2.waitKey(0)  # Wait for a key press to close the window
    cv2.destroyAllWindows()

    # Print detection details (class, confidence, bounding box coordinates)
    for detection in result.boxes:
        class_id = int(detection.cls)  # Class ID
        class_name = model.names[class_id]  # Class name
        confidence = detection.conf  # Confidence score
        bbox = detection.xyxy[0].tolist()  # Bounding box coordinates [x_min, y_min, x_max, y_max]
        print(f"Detected: {class_name} (Confidence: {confidence:.2f}, BBox: {bbox})")