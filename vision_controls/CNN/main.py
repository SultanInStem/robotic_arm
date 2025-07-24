import torch
import cv2
import numpy as np
import torchvision.ops as ops
from PIL import Image
import yaml
import os
# Load checkpoint
checkpoint = torch.load("oculus/my_model.pt", map_location='cpu', weights_only=False)

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

print("Loaded on: ",next(model.parameters()).device)


######################################



def letterbox(img, new_shape=640, color=(114, 114, 114)):
    shape = img.shape[:2]  # current shape [height, width]
    ratio = new_shape / max(shape)  # scale ratio
    new_unpad = (int(shape[1] * ratio), int(shape[0] * ratio))
    img_resized = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
    dw = new_shape - new_unpad[0]
    dh = new_shape - new_unpad[1]
    top, bottom = 0, dh
    left, right = 0, dw
    img_padded = cv2.copyMakeBorder(img_resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
    return img_padded, ratio, (left, top)

def preprocess(img_path, img_size=640):
    img0 = cv2.imread(img_path)  # BGR
    assert img0 is not None, f"Image not found: {img_path}"
    img, ratio, pad = letterbox(img0, new_shape=img_size)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32) / 255.0
    img = np.transpose(img, (2, 0, 1))
    img_tensor = torch.from_numpy(img).unsqueeze(0).to(device)
    return img0, img_tensor, ratio, pad


def postprocess(prediction, conf_thres=0.25, iou_thres=0.45):
    # prediction: [batch, num_boxes, 85]
    pred = prediction[0]  # batch size 1
    
    # Apply sigmoid to objectness and class scores
    pred[..., 4:] = pred[..., 4:].sigmoid()

    # Boxes in xywh format
    boxes = pred[..., :4]

    # Objectness score
    obj_conf = pred[..., 4]

    # Class confidence and class id
    cls_conf, cls_ids = pred[..., 5:].max(dim=2)

    # Combined confidence
    conf = obj_conf * cls_conf

    # Filter by confidence threshold
    mask = conf > conf_thres
    boxes = boxes[mask]
    conf = conf[mask]
    cls_ids = cls_ids[mask]

    if boxes.shape[0] == 0:
        return [], [], []

    # Convert xywh to xyxy
    xyxy = torch.zeros_like(boxes)
    xyxy[:, 0] = boxes[:, 0] - boxes[:, 2] / 2
    xyxy[:, 1] = boxes[:, 1] - boxes[:, 3] / 2
    xyxy[:, 2] = boxes[:, 0] + boxes[:, 2] / 2
    xyxy[:, 3] = boxes[:, 1] + boxes[:, 3] / 2

    # NMS
    keep = ops.nms(xyxy, conf, iou_thres)
    return xyxy[keep], conf[keep], cls_ids[keep]



def scale_coords(boxes, ratio, pad):
    # boxes: xyxy format
    boxes[:, [0, 2]] -= pad[0]  # x padding
    boxes[:, [1, 3]] -= pad[1]  # y padding
    boxes /= ratio
    return boxes

# 5. Draw boxes on image
def draw_boxes(img, boxes, scores, class_ids, class_names):
    img = img.copy()
    for box, score, cls_id in zip(boxes, scores, class_ids):
        x1, y1, x2, y2 = map(int, box)
        label = f"{class_names[cls_id]}: {score:.2f}"
        cv2.rectangle(img, (x1, y1), (x2, y2), (0,255,0), 2)
        cv2.putText(img, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
    return img




img_path = "test.jpg"
orig_img, img_tensor, ratio, pad = preprocess(img_path)

with torch.no_grad():
    preds = model(img_tensor)

boxes, scores, class_ids = postprocess(preds, conf_thres=0.25, iou_thres=0.45)

class_names = ["1", "2", "3", "4", "5", "6"]
if len(boxes) > 0:
    boxes = scale_coords(boxes, ratio, pad).cpu().numpy()
    scores = scores.cpu().numpy()
    class_ids = class_ids.cpu().numpy()

    annotated_img = draw_boxes(orig_img, boxes, scores, class_ids, class_names)
    cv2.imwrite("output.jpg", annotated_img)
    cv2.imshow("YOLOv5 Detection", annotated_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("No detections found.")