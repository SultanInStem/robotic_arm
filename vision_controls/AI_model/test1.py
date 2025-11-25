import pyrealsense2 as rs
import numpy as np
import cv2
import time
import paramiko
from ultralytics import YOLO # Import YOLO

# Load the pre-trained YOLOv8n (nano) model
# This model will be downloaded automatically on the first run.
# You can use other models like 'yolov8s.pt' for better accuracy at the cost of speed.
model = YOLO('my_model.pt') 

# Information for SSH connection to Raspberry Pi
PI_HOST = "192.168.10.2"
PI_PORT = 22 
PI_USER = "er@er"
PI_PASSWORD = "fresnostate"
REMOTE_PATH_ON_PI = "/Desktop/robotic_arm/vision_controls/AI_model"
LOCAL_PATH = "coords_data.txt"


try:
    with open(LOCAL_PATH, 'w') as f:
        f.write("This is a test file from the Jetson.\n")
        f.write(f"Timestamp: {time.time()}\n")
        f.write("Hello, Raspberry Pi! (via SFTP with SSH Key)\n")
    print("Local file created successfully.")
except Exception as e:
    print(f"Error creating file: {e}")
    exit()

sh_client = None
try:
    print(f"Connecting to {PI_USER}@{PI_HOST} using SSH key...")
    
    # Create an SSH client object
    ssh_client = paramiko.SSHClient()
    
    # Automatically add the server's host key
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # Connect using SSH keys.
    # Paramiko will automatically look for your default keys
    # (like ~/.ssh/id_rsa) since we are not providing a password.
    ssh_client.connect(hostname=PI_HOST,
                       port=PI_PORT,
                       username=PI_USER)
                       
    print("Connected successfully.")

    # Open an SFTP session on the established SSH connection
    sftp = ssh_client.open_sftp()
    
    # Upload the file
    print(f"Uploading '{LOCAL_PATH}' to '{REMOTE_PATH_ON_PI}'...")
    sftp.put(LOCAL_PATH, REMOTE_PATH_ON_PI)
    
    print("File uploaded successfully.")
    
    # Close the SFTP session
    sftp.close()

except paramiko.AuthenticationException:
    print("Authentication failed. Did you run 'ssh-copy-id'?")
except paramiko.SSHException as e:
    print(f"SSH connection error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Always close the SSH connection
    if ssh_client:
        ssh_client.close()
        print("Connection closed.")



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
                    x_3d, z_3d, y_3d = point_3d
                    print("X ", x_3d, " Y: ", y_3d, " Depth: ", z_3d)
                    
                    # 4. Draw visualizations
                    
                    # Draw the bounding box
                    cv2.rectangle(color_image, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    
                    # Draw a circle at the center
                    cv2.circle(color_image, (cx, cy), 5, (0, 0, 255), -1)
                    
                    # Prepare text
                    text = f"{class_name}: ({x_3d:.2f}, {z_3d:.2f}, {y_3d:.2f}) m"
                    
                    # Put text above the box
                    cv2.putText(color_image, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
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