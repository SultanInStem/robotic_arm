import cv2
import pyrealsense2 as rs
import numpy as np
import cv2
import time 
from ultralytics import YOLO 

original_width = 640 
original_height = 480
interval = 2
last_time = time.time()

model = YOLO("oculus_s/my_model.pt")
# Global variables to store clicked point
clicked_point = None

# Mouse callback function to capture click coordinates
def mouse_callback(event, x, y, flags, param):
    global clicked_point
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_point = (x, y)

# Initialize pipeline
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming
pipeline.start(config)

# Align depth to color
align = rs.align(rs.stream.color)

# Get camera intrinsics (needed for deprojection)
profile = pipeline.get_active_profile()
depth_profile = rs.video_stream_profile(profile.get_stream(rs.stream.depth))
intrinsics = depth_profile.get_intrinsics()

try:
    while True:
        # Wait for frames
        current_time = time.time()
        frames = pipeline.wait_for_frames()
        # Align frames
        aligned_frames = align.process(frames)
        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()
        
        if not depth_frame or not color_frame:
            continue
        
        # Convert to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        
        # Apply colormap to depth
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)



        # Using YOLO 
        def run_yolo_detection(): 
            results = model(color_image, device="cpu")
            scale_x = original_width / 640
            scale_y = original_height / 640
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0]  # bounding box in 640x640
                    x1, y1, x2, y2 = x1.item(), y1.item(), x2.item(), y2.item()

                    # Map to original frame size
                    x1_orig = int(x1 * scale_x)
                    y1_orig = int(y1 * scale_y)
                    x2_orig = int(x2 * scale_x)
                    y2_orig = int(y2 * scale_y)

                    # Draw on original frame
                    cv2.rectangle(color_image, (x1_orig, y1_orig), (x2_orig, y2_orig), (0, 255, 0), 2)

                    # Print center point in original frame
                    cx = (x1_orig + x2_orig) // 2
                    cy = (y1_orig + y2_orig) // 2
                    print(f"Object at (x, y): ({cx}, {cy}) in RealSense frame")
      

        if current_time - last_time >= interval: 
            run_yolo_detection()
            last_time = time.time()
        # Stack images horizontally
        images = np.hstack((color_image, depth_colormap))
        # print(len(images))
        # print(type(images))

        
        # Handle clicked point
        # if clicked_point is not None:
        #     x, y = clicked_point
        #     if x < color_image.shape[1]:  # Ensure click is in color image
        #         # Get depth value (in meters)
        #         depth = depth_frame.get_distance(x, y)
                
        #         if depth > 0:  # Valid depth
        #             # Deproject pixel to 3D point
        #             point_3d = rs.rs2_deproject_pixel_to_point(intrinsics, [x, y], depth)
        #             x_3d, y_3d, z_3d = point_3d
                    
        #             # Display coordinates on image
        #             text = f"3D: ({x_3d:.3f}, {y_3d:.3f}, {z_3d:.3f}) m, Depth: {depth*1000:.1f} mm"
        #             cv2.putText(color_image, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        #             # Mark clicked point
        #             cv2.circle(color_image, (x, y), 5, (0, 0, 255), -1)
        #             # Update stacked image
        #             images = np.hstack((color_image, depth_colormap))
        
        # Display
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback('RealSense', mouse_callback)
        cv2.imshow('RealSense', images)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    pipeline.stop()
    cv2.destroyAllWindows()