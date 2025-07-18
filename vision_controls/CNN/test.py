import cv2
import numpy as np
import pyrealsense2 as rs
import torch

COORD_FILE = "/home/agxorin3/Desktop/strawberry/strawberry_coords.txt"

# Load model (auto uses GPU if available)
model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolo/my_model.pt')
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model.to(device)
model.eval()

def pixel_to_metric(intrinsics, x, y, depth):
    point = rs.rs2_deproject_pixel_to_point(intrinsics, [x, y], depth)
    return point[0], point[1], point[2]

# Initialize RealSense camera as before
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

try:
    pipeline.start(config)
except Exception as e:
    print("Error starting camera:", e)
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
            print("Missing frames")
            continue

        color_image = np.asanyarray(color_frame.get_data())

        # Run YOLOv5 inference directly on BGR numpy image (model does preprocessing)
        results = model(color_image)

        coords = []

        # results.xyxy[0] is a tensor of detections for the first image: (N,6) with columns [x1,y1,x2,y2,conf,class]
        for *box, conf, cls in results.xyxy[0].tolist():
            if conf < 0.5:
                continue

            x1, y1, x2, y2 = map(int, box)
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            depth = round(depth_frame.get_distance(cx, cy), 3)
            if depth == 0.0:
                continue

            X, Y, Z = pixel_to_metric(intrinsics, cx, cy, depth)
            coords.append((X, Y, Z))

            # Draw bounding box and text
            cv2.rectangle(color_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(color_image, f"X:{X:.3f}", (x1, y1 - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
            cv2.putText(color_image, f"Y:{Y:.3f}", (x1, y1 - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
            cv2.putText(color_image, f"Z:{Z:.3f}", (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

        # Save first strawberry coordinate if any
        if coords:
            import os
            with open(COORD_FILE + ".tmp", "w") as f:
                X, Y, Z = coords[0]
                f.write(f"{X} {Y} {Z}")
            os.replace(COORD_FILE + ".tmp", COORD_FILE)

        cv2.imshow("Strawberry Detector", color_image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    pipeline.stop()
    cv2.destroyAllWindows()
    print("Stopped.")
