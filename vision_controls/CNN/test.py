import torch
import cv2
import numpy as np
import os

# Function to load the model
def load_yolo_model(model_path):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file {model_path} not found")
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    try:
        # Load as scripted model
        model = torch.load(model_path, map_location=device)
        model.eval()
        print("Loaded model as torch.jit scripted model")
    except RuntimeError as e:
        print(f"Scripted model load failed: {e}")
        # Fallback: Load as state_dict (requires architecture)
        try:
            from ultralytics.models.yolo import YOLOv8  # Adjust for YOLOv5 if needed
            model = YOLOv8()  # Instantiate model (replace with correct architecture, e.g., yolov8n.yaml)
            state_dict = torch.load(model_path, map_location=device)
            model.load_state_dict(state_dict)
            model.eval()
            print("Loaded model as state_dict")
        except ImportError:
            raise ImportError("YOLO architecture not found. Install ultralytics or provide model definition.")
    
    return model.to(device)

# Preprocess image
def preprocess_image(image_path, input_size=(640, 640)):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file {image_path} not found")
    
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, input_size)
    img = img.astype(np.float32) / 255.0
    img = np.transpose(img, (2, 0, 1))
    img = np.expand_dims(img, axis=0)
    img_tensor = torch.from_numpy(img).to('cuda' if torch.cuda.is_available() else 'cpu')
    return img_tensor, img

# Post-process outputs
def postprocess_outputs(outputs, conf_thres=0.25, iou_thres=0.45, input_size=(640, 640), img_shape=(480, 640)):
    pred = outputs[0].cpu().numpy()  # Shape: (1, num_boxes, 4 + 1 + num_classes)
    boxes = pred[..., :4]  # x_center, y_center, width, height
    scores = pred[..., 4]  # Objectness scores
    class_probs = pred[..., 5:]  # Class probabilities
    class_ids = np.argmax(class_probs, axis=-1)
    
    mask = scores > conf_thres
    boxes = boxes[mask]
    scores = scores[mask]
    class_ids = class_ids[mask]
    
    img_h, img_w = img_shape
    input_h, input_w = input_size
    boxes[:, [0, 2]] *= img_w / input_w
    boxes[:, [1, 3]] *= img_h / input_h
    boxes[:, [0, 1]] -= boxes[:, [2, 3]] / 2  # Convert to top-left (x_min, y_min)
    
    indices = cv2.dnn.NMSBoxes(boxes.tolist(), scores.tolist(), conf_thres, iou_thres)
    if len(indices) > 0:
        indices = indices.flatten()
        boxes = boxes[indices]
        scores = scores[indices]
        class_ids = class_ids[indices]
    
    return boxes, scores, class_ids

# Draw boxes
def draw_boxes(img, boxes, scores, class_ids, class_names=None):
    if class_names is None:
        class_names = [str(i) for i in range(max(class_ids) + 1)]
    
    for box, score, class_id in zip(boxes, scores, class_ids):
        x_min, y_min, w, h = box
        x_max, y_max = x_min + w, y_min + h
        x_min, y_min, x_max, y_max = map(int, [x_min, y_min, x_max, y_max])
        cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
        label = f"{class_names[class_id]}: {score:.2f}"
        cv2.putText(img, label, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 255, 0), 2)
    
    return img

# Main
try:
    # Verify GPU
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available.")
    print(f"Using GPU: {torch.cuda.get_device_name(0)}")

    # Load model
    model_path = "yolo/my_model.pt"  # Update path
    model = load_yolo_model(model_path)
    print(f"Model device: {next(model.parameters()).device}")

    # Load and preprocess image
    image_path = "test.jpg"  # Update path
    input_size = (640, 640)  # Adjust if needed
    img_tensor, img_orig = preprocess_image(image_path, input_size)

    # Inference
    torch.cuda.empty_cache()
    with torch.no_grad():
        outputs = model(img_tensor)
    print(f"Inference completed on: {outputs[0].device}")

    # Post-process
    boxes, scores, class_ids = postprocess_outputs(outputs, conf_thres=0.25, iou_thres=0.45, input_size=input_size, img_shape=img_orig.shape[:2])

    # Visualize
    class_names = ["person", "car", ...]  # Replace with your classes
    img_annotated = draw_boxes(img_orig.copy(), boxes, scores, class_ids, class_names)
    output_path = "output_image.jpg"
    cv2.imwrite(output_path, cv2.cvtColor(img_annotated, cv2.COLOR_RGB2BGR))
    print(f"Output image saved as {output_path}")
    cv2.imshow("YOLO Detection", cv2.cvtColor(img_annotated, cv2.COLOR_RGB2BGR))
    cv2.waitKey(0)
    cv2.destroyAllWindows()
except FileNotFoundError as e:
    print(f"Error: {e}")
except RuntimeError as e:
    print(f"GPU Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")