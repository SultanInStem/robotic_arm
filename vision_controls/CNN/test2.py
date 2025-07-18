import cv2
import numpy as np 
import torch
import pyrealsense2 as rs
from utils.general import non_max_suppression


COORD_FILE = "/home/agxorin3/Desktop/strawberry/strawberry_coords.txt"
device = 'cuda' if torch.cuda.is_available() else 'cpu'
loaded = torch.load('yolo/my_model.pt', map_location=device)

# Extract the model object if stored in a dict (common practice)
model = loaded['model'] if isinstance(loaded, dict) and 'model' in loaded else loaded
model.to(device).eval()


def pixel_to_metric(intrinsics, x,y, depth): 
    point = rs.rs2_deproject_pixel_to_point(intrinsics, [x,y], depth)
    return point[0], point[1], point[2] # Returns X,Y,Z in meters
def preprocess(image, img_size=640):
    # Resize and pad to img_size, maintaining aspect ratio (letterbox)
    # This helper replicates Ultralytics' letterbox function roughly

    h0, w0 = image.shape[:2]
    r = img_size / max(h0, w0)
    new_unpad = int(w0 * r), int(h0 * r)
    image_resized = cv2.resize(image, new_unpad, interpolation=cv2.INTER_LINEAR)

    # Compute padding
    dw = img_size - new_unpad[0]
    dh = img_size - new_unpad[1]
    top, bottom = dh // 2, dh - (dh // 2)
    left, right = dw // 2, dw - (dw // 2)

    # Add border
    image_padded = cv2.copyMakeBorder(image_resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114,114,114))

    # Convert BGR to RGB
    image_rgb = cv2.cvtColor(image_padded, cv2.COLOR_BGR2RGB)

    # Convert to tensor
    img_tensor = torch.from_numpy(image_rgb).permute(2,0,1).float() / 255.0
    img_tensor = img_tensor.unsqueeze(0).to(device)  # add batch dim

    return img_tensor, r, left, top

def postprocess(prediction, conf_thres=0.5, iou_thres=0.45):
    # prediction shape: (batch, num_anchors, 6 or more) -> [x,y,w,h,conf,class,...]
    # NMS returns detections filtered by conf and iou
    return non_max_suppression(prediction, conf_thres, iou_thres)

pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
try: 
     pipeline.start(config)
except Exception as e: 
     print("Error: Could not start the camera")
     exit()
align = rs.align(rs.stream.color)
profile = pipeline.get_active_profile()
depth_profile = rs.video_stream_profile(profile.get_stream(rs.stream.depth))
intrinsics = depth_profile.get_intrinsics()


try: 
    while True:
        frames = pipeline.wait_for_frames()
        aligned_frames = align.process(frames)
        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        if not color_frame or not depth_frame:
            print("Warning: Color frame or depth frame is missing")
            continue	
        depth_intrin = depth_frame.profile.as_video_stream_profile().intrinsics
        color_image = np.asanyarray(color_frame.get_data())

        img_tensor, scale, pad_x, pad_y = preprocess(color_image)

        with torch.no_grad():
            pred = model(img_tensor)[0]  # raw predictions

        detections = non_max_suppression(pred, 0.5, 0.45)[0]  # first batch, filtered

        coords = []

        if detections is not None and len(detections):
            for *xyxy, conf, cls in detections.cpu().numpy():
                x1, y1, x2, y2 = xyxy
                # Undo padding and scaling to original image coordinates
                x1 = int((x1 - pad_x) / scale)
                y1 = int((y1 - pad_y) / scale)
                x2 = int((x2 - pad_x) / scale)
                y2 = int((y2 - pad_y) / scale)

                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2
                depth = round(depth_frame.get_distance(cx, cy), 3)
                if depth == 0.0:
                    continue

                X, Y, Z = pixel_to_metric(intrinsics, cx, cy, depth)
                coords.append((X, Y, Z))

                # Draw bbox and labels on color_image
                cv2.rectangle(color_image, (x1,y1), (x2,y2), (0,255,0), 2)
                cv2.putText(color_image, f"X:{X:.3f}", (x1, y1-40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
                cv2.putText(color_image, f"Y:{Y:.3f}", (x1, y1-20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
                cv2.putText(color_image, f"Z:{Z:.3f}", (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
        # strawberries = detect_strawberries(color_image)

        # Run Yolo 
        results = model(color_image)
        coords = []
        for box in results.boxes: 
            cls = int(box.cls.item())
            conf = float(box.conf.item())
            if conf < 0.5:
                continue 
            x1,y1,x2,y2 = map(int, box.xyxy[0])
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2 
            depth = round(depth_frame.get_distance(cx,cy), 3)
            X, Y, Z = pixel_to_metric(depth_intrin, cx, cy, depth)
            coords.append((X, Y, Z))
            cv2.putText(color_image, f"X: {round(X, 3)}", (0,100),  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(color_image, f"Y: {round(Y, 3)}", (150,100),  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(color_image, f"Z: {round(Z, 3)}", (300,100),  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Write bounding box center coordinates (X, Y) to the file for Raspberry Pi
        # with open(COORD_FILE, "w") as f:
        #     if len(coords) > 0:
        #         berry = coords[0]
        #         f.write(f"{berry[0]} {berry[1]} {berry[2]}")

        cv2.imshow("Strawberry Detector", color_image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally: 
    pipeline.stop()        
    cv2.destroyAllWindows()
    print("stopped")

