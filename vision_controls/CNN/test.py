import cv2
import numpy as np
import pyrealsense2 as rs
import torch

# File path for Raspberry Pi
COORD_FILE = "/home/agxorin3/Desktop/strawberry/strawberry_coords.txt"

# Load PyTorch model
device = 'cuda' if torch.cuda.is_available() else 'cpu'
loaded = torch.load('yolo/my_model.pt', map_location=device)

# Extract the model (if needed)
model = loaded['model'] if isinstance(loaded, dict) and 'model' in loaded else loaded
model.to(device)
model.eval()

# Converts pixel (x, y) + depth to real-world (X, Y, Z)
def pixel_to_metric(intrinsics, x, y, depth): 
    point = rs.rs2_deproject_pixel_to_point(intrinsics, [x, y], depth)
    return point[0], point[1], point[2]  # in meters

# Initialize RealSense pipeline
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

try: 
    pipeline.start(config)
except Exception as e: 
    print("Error: Could not start the camera:", e)
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
            print("Warning: Missing frame")
            continue

        color_image = np.asanyarray(color_frame.get_data())

        # Preprocess image for PyTorch model (resize, normalize, etc.)
        img = cv2.resize(color_image, (640, 640))  # adjust size if needed
        img_tensor = torch.from_numpy(img).permute(2, 0, 1).div(255.0).unsqueeze(0).to(device).half()

        # Run inference
        with torch.no_grad():
            output = model(img_tensor)[0]  # output shape: [num_detections, 6] = [x1, y1, x2, y2, conf, class]

        coords = []

        for det in output:
            x1, y1, x2, y2, conf, cls = det.tolist()
            if conf < 0.5:
                continue

            # Rescale bbox back to original image size
            scale_x = color_image.shape[1] / 640
            scale_y = color_image.shape[0] / 640
            x1 = int(x1 * scale_x)
            y1 = int(y1 * scale_y)
            x2 = int(x2 * scale_x)
            y2 = int(y2 * scale_y)

            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            depth = round(depth_frame.get_distance(cx, cy), 3)

            if depth == 0.0:
                continue

            X, Y, Z = pixel_to_metric(intrinsics, cx, cy, depth)
            coords.append((X, Y, Z))

            # Draw info
            cv2.rectangle(color_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(color_image, f"X: {round(X, 3)}", (x1, y1 - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(color_image, f"Y: {round(Y, 3)}", (x1, y1 - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(color_image, f"Z: {round(Z, 3)}", (x1, y1),     cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Save first detected coordinate to file (if any)
        if coords:
            with open(COORD_FILE + ".tmp", "w") as f:
                X, Y, Z = coords[0]
                f.write(f"{X} {Y} {Z}")
            import os
            os.replace(COORD_FILE + ".tmp", COORD_FILE)

        # Show the image
        cv2.imshow("Strawberry Detector", color_image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally: 
    pipeline.stop()
    cv2.destroyAllWindows()
    print("Stopped.")
