import cv2
import numpy as np
import pyrealsense2 as rs
from ultralytics import YOLO 
import torch

# File path for Raspberry Pi
COORD_FILE = "/home/agxorin3/Desktop/strawberry/strawberry_coords.txt"
model = YOLO("/yolo/my_model/train12/weights/best.pt")

def detect_strawberries(frame):
    """Detects strawberries using color thresholding and contour detection"""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_red = np.array([0, 120, 70])
    upper_red = np.array([10, 255, 255])
    
    mask1 = cv2.inRange(hsv, lower_red, upper_red)
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

    mask = mask1 + mask2
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    strawberries = []
    for contour in contours:
        if cv2.contourArea(contour) > 500:
            x, y, w, h = cv2.boundingRect(contour)
            strawberries.append((x, y, w, h))

    return strawberries
def pixel_to_metric(intrinsics, x,y, depth): 
    point = rs.rs2_deproject_pixel_to_point(intrinsics, [x,y], depth)
    return point[0], point[1], point[2] # Returns X,Y,Z in meters

# Initializing the 3D camera
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
        color_image = np.asanyarray(color_frame.get_data())
        depth_intrin = depth_frame.profile.as_video_stream_profile().intrinsics
        strawberries = detect_strawberries(color_image)
        coords = []

        for (x, y, w, h) in strawberries:
            roi = color_image[y:y+h, x:x+w]
            cv2.rectangle(color_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(color_image, "Strawberry", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Compute center coordinates
            cx, cy = x + w // 2, y + h // 2
            depth = round(depth_frame.get_distance(cx,cy), 3)
            X, Y, Z = pixel_to_metric(depth_intrin, cx, cy, depth)
            coords.append((X, Y, Z))
            cv2.putText(color_image, f"X: {round(X, 3)}", (0,100),  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(color_image, f"Y: {round(Y, 3)}", (150,100),  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(color_image, f"Z: {round(Z, 3)}", (300,100),  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            print("Depth: ", depth)


        # Write bounding box center coordinates (X, Y) to the file for Raspberry Pi
        with open(COORD_FILE, "w") as f:
            if len(coords) > 0:
                berry = coords[0]
                f.write(f"{berry[0]} {berry[1]} {berry[2]}")

        cv2.imshow("Strawberry Detector", color_image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally: 
    pipeline.stop()        
    cv2.destroyAllWindows()
    print("stopped")