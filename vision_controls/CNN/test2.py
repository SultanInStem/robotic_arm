import pyrealsense2 as rs
import numpy as np
import cv2
import torch
from ultralytics import YOLO

model = YOLO('yolov5m.pt')  # This will not require torchvision


# Load the YOLOv5 model
model.eval()

# Initialize Intel RealSense pipeline
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

pipeline.start(config)

try:
    while True:
        # Wait for a coherent frame
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            continue

        # Convert RealSense frame to numpy array
        frame = np.asanyarray(color_frame.get_data())

        results = model(frame)
        # Preprocess image for YOLOv5 (resize, normalize, convert to tensor)
        img = cv2.resize(frame, (640, 640))
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB and HWC to CHW
        img = np.ascontiguousarray(img, dtype=np.float32) / 255.0
        img_tensor = torch.from_numpy(img).unsqueeze(0)

        if torch.cuda.is_available():
            img_tensor = img_tensor.cuda()
            model = model.cuda()

        # Inference
        with torch.no_grad():
            pred = model(img_tensor)[0]

        # Apply confidence threshold and NMS manually (you can tweak thresholds)
        conf_thresh = 0.25
        nms_thresh = 0.45
        pred = pred[pred[:, 4] > conf_thresh]

        # Convert predictions to CPU
        pred = pred.cpu().numpy()

        # Draw boxes
        for *box, conf, cls in pred:
            x1, y1, x2, y2 = map(int, box)
            label = f'Strawberry {conf:.2f}'
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Show image
        cv2.imshow("Strawberry Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    pipeline.stop()
    cv2.destroyAllWindows()
