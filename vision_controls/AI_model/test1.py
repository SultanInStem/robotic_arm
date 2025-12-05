import pyrealsense2 as rs
import numpy as np
import cv2
import time
import os
from ultralytics import YOLO # Import YOLO


model = YOLO('my_model.pt') 

file_path = "coords_data.txt"
CAMERA_WIDTH_OFFSET = (50/2)*0.001 # convert mm to meters
CAMERA_HEIGHT_OFFSET = 60*0.001
Z_OFFSET = 0.13


# Initialize pipeline
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming
profile = pipeline.start(config)

# Align depth to color
align = rs.align(rs.stream.color)

# Get camera intrinsics (needed for deprojection)
depth_profile = rs.video_stream_profile(profile.get_stream(rs.stream.depth))
intrinsics = depth_profile.get_intrinsics()

try:
    while True:
        # Wait for frames
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
        
        # --- YOLOv8 Inference ---
        # Run inference on the color image
        # verbose=False suppresses the console output for each frame
        results = model(color_image, verbose=False)

        # Process the results
        for res in results:
            # Get bounding boxes, classes, and confidences
            boxes = res.boxes.cpu().numpy() # .cpu().numpy() to move data to CPU/Numpy
            
            for box in boxes:
                # Get coordinates
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                # Get class name
                cls = int(box.cls[0])
                class_name = model.names[cls]
                
                # --- Get 3D coordinates for the center of the box ---
                
                # 1. Calculate center point
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                
                # 2. Get depth value at the center point
                depth = depth_frame.get_distance(cx, cy)
                if depth > 0:  # Check if depth is valid (not 0)
                    # 3. Deproject pixel to 3D point
                    point_3d = rs.rs2_deproject_pixel_to_point(intrinsics, [cx, cy], depth)
                    x_3d, y_3d, z_3d = point_3d
                    if x_3d > 0: 
                        x_3d = x_3d - CAMERA_WIDTH_OFFSET   # Adjust sign if necessary
                    else:
                        x_3d = x_3d + CAMERA_WIDTH_OFFSET   # Adjust sign if necessary
                    if y_3d > 0:
                        y_3d = y_3d + CAMERA_HEIGHT_OFFSET
                    else:
                        y_3d = y_3d - CAMERA_HEIGHT_OFFSET
                    z_3d = z_3d - Z_OFFSET     
                    print("X ", x_3d, " Y: ", y_3d, " Depth: ", z_3d)

                    # send the coordinates to Raspberry Pi
                    text = f"3D: ({x_3d:.3f}, {y_3d:.3f}, {z_3d:.3f}) m, Depth: {depth*1000:.1f} mm"
                    cv2.putText(color_image, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    # Mark clicked point
                    cv2.circle(color_image, (cx, cy), 5, (0, 0, 255), -1)


                    ### WRITE TO .TXT FILE ###
                    if os.path.getsize(file_path) == 0: 
                        with open(file_path, "w") as f:
                            f.write(f"{x_3d},{y_3d},{z_3d}")
                    
                
                else:
                    # Optional: Draw the box even if depth is 0, but indicate no depth
                    cv2.rectangle(color_image, (x1, y1), (x2, y2), (0, 0, 255), 2) # Red for no depth
                    text = f"{class_name}: No Depth"
                    cv2.putText(color_image, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # --- End of YOLOv8 logic ---
        
        # Apply colormap to depth
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        
        # Stack images horizontally
        images = np.hstack((color_image, depth_colormap))
        
        # Display
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        # We removed the setMouseCallback line
        cv2.imshow('RealSense', images)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    pipeline.stop()
    cv2.destroyAllWindows()