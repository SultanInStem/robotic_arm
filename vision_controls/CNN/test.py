import torch
import cv2
import numpy as np
import torchvision.ops as ops
import yaml
import os
# Load checkpoint
checkpoint = torch.load("yolo/my_model.pt", map_location='cpu', weights_only=False)

# Choose the weights to load: EMA weights if available (better), else regular model weights
weights = checkpoint['ema'] if checkpoint.get('ema') is not None else checkpoint['model']

# weights might be a PyTorch model or a state_dict, let's check:
if hasattr(weights, 'state_dict'):
    # If it's a model, get its state dict
    state_dict = weights.state_dict()
else:
    # Otherwise, assume it's already a state dict
    state_dict = weights

# Now load model architecture YAML
import yaml
from models.yolo import Model  # Make sure you have YOLOv5 repo in your PYTHONPATH or current dir

with open('models/yolov5m.yaml') as f:  # adjust if you used yolov5s, yolov5l, etc.
    cfg = yaml.safe_load(f)

# Instantiate model
model = Model(cfg=cfg)

# Sometimes keys have 'module.' prefix from DataParallel, remove if necessary
clean_state_dict = {k.replace('module.', ''): v for k, v in state_dict.items()}

# Load weights
model.load_state_dict(clean_state_dict, strict=False)
model.eval()

# Now model is ready for inference on CPU or move to GPU if available
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model.to(device)


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

def non_max_suppression(prediction, conf_thresh=0.25, iou_thresh=0.45):
    boxes, scores, class_ids = [], [], []

    for pred in prediction:  # batch loop
        if pred is None or len(pred) == 0:
            continue

        pred = pred[pred[:, 4] > conf_thresh]
        if len(pred) == 0:
            continue

        xywh = pred[:, :4]
        conf = pred[:, 4]
        cls_conf, cls_id = pred[:, 5:].max(1)

        conf_score = conf * cls_conf

        # Convert xywh to xyxy
        xyxy = torch.zeros_like(xywh)
        xyxy[:, 0] = xywh[:, 0] - xywh[:, 2] / 2
        xyxy[:, 1] = xywh[:, 1] - xywh[:, 3] / 2
        xyxy[:, 2] = xywh[:, 0] + xywh[:, 2] / 2
        xyxy[:, 3] = xywh[:, 1] + xywh[:, 3] / 2

        keep = ops.nms(xyxy, conf_score, iou_thresh)

        boxes.append(xyxy[keep].cpu().numpy())
        scores.append(conf_score[keep].cpu().numpy())
        class_ids.append(cls_id[keep].cpu().numpy())

    return boxes, scores, class_ids

def draw_boxes(img, boxes, scores, class_ids, class_names=None):
    if class_names is None:
        class_names = [str(i) for i in range(max(class_ids[0]) + 1)] if class_ids else []

    for box_arr, score_arr, class_id_arr in zip(boxes, scores, class_ids):
        for box, score, cls_id in zip(box_arr, score_arr, class_id_arr):
            x1, y1, x2, y2 = box.astype(int)
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"{class_names[cls_id]}: {score:.2f}"
            cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
    return img

def main(image_path):
    img_tensor, img_orig = preprocess_image(image_path)
    with torch.no_grad():
        preds = model(img_tensor)[0]
    print(type(preds))

    boxes, scores, class_ids = non_max_suppression([preds])

    img_with_boxes = draw_boxes(img_orig.copy(), boxes, scores, class_ids, class_names=None)

    # Convert RGB to BGR for OpenCV
    img_with_boxes = cv2.cvtColor(img_with_boxes, cv2.COLOR_RGB2BGR)
    cv2.imshow('YOLOv5 Detection', img_with_boxes)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Optionally save the result
    cv2.imwrite("output.jpg", img_with_boxes)
    print("Result saved to output.jpg")

if __name__ == "__main__":
    test_image = "test.jpg"  # path to your test image
    main(test_image)