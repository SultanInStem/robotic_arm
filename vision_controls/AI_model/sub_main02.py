import pyrealsense2 as rs
import numpy as np
import cv2
import socket
import time
import os

# ─────────────────────────────────────────────
# MODEL CONFIG
# ─────────────────────────────────────────────
MODEL_PATH  = "my_model.onnx"
NAMES_PATH  = "my_model.names"
INPUT_SIZE  = (640, 640)
CONF_THRESH = 0.5
NMS_THRESH  = 0.4

# ─────────────────────────────────────────────
# DETECTION CONFIG
# ─────────────────────────────────────────────
file_path            = "coords_data.txt"
CAMERA_WIDTH_OFFSET  = (50 / 2) * 0.001
CAMERA_HEIGHT_OFFSET = -60 * 0.001
Z_OFFSET             = 0.13
DETECTION_FRAMES     = 20
delta                = 0.15
THRESHOLD            = 50
BRIGHTNESS_THRESHOLD = 30
frame_center_x       = 640 // 2
frame_center_y       = 480 // 2

# ─────────────────────────────────────────────
# SERVER CONFIG
# ─────────────────────────────────────────────
SERVER_HOST       = '192.168.10.2'
SERVER_PORT       = 65432
BUFFER_SIZE       = 4096
REMOTE_PATH_ON_PI = "/Desktop/robotic_arm/vision_controls/AI_model"


# ─────────────────────────────────────────────
# LOAD MODEL
# ─────────────────────────────────────────────
def load_model(model_path):
    net = cv2.dnn.readNetFromONNX(model_path)
    if cv2.cuda.getCudaEnabledDeviceCount() > 0:
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        print("✅ Using CUDA backend")
    else:
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        print("⚠️  CUDA not found, using CPU")
    return net


def load_classes(names_path):
    with open(names_path, "r") as f:
        return [line.strip() for line in f.readlines()]


def get_output_layers(net):
    layer_names = net.getLayerNames()
    unconnected = net.getUnconnectedOutLayers()
    if isinstance(unconnected[0], (list, np.ndarray)):
        return [layer_names[i[0] - 1] for i in unconnected]
    return [layer_names[i - 1] for i in unconnected]


# ─────────────────────────────────────────────
# LETTERBOX — matches ultralytics preprocessing
# ─────────────────────────────────────────────
def letterbox(image, target_size=(640, 640)):
    h, w = image.shape[:2]
    th, tw = target_size
    scale = min(tw / w, th / h)
    new_w = int(w * scale)
    new_h = int(h * scale)

    resized = cv2.resize(image, (new_w, new_h))

    # Pad with grey (114 = ultralytics default)
    canvas = np.full((th, tw, 3), 114, dtype=np.uint8)
    pad_x = (tw - new_w) // 2
    pad_y = (th - new_h) // 2
    canvas[pad_y:pad_y + new_h, pad_x:pad_x + new_w] = resized

    return canvas, scale, pad_x, pad_y


# ─────────────────────────────────────────────
# DETECT — YOLOv8 ONNX (1, 6, 8400)
# ─────────────────────────────────────────────
def detect(net, frame, class_names):
    h, w = frame.shape[:2]

    # Letterbox to match ultralytics preprocessing
    letterboxed, scale, pad_x, pad_y = letterbox(frame, INPUT_SIZE)

    blob = cv2.dnn.blobFromImage(letterboxed, 1/255.0, INPUT_SIZE,
                                  swapRB=True, crop=False)
    net.setInput(blob)
    outputs = net.forward(get_output_layers(net))

    # YOLOv8 output: (1, 6, 8400) → (8400, 6)
    output = np.squeeze(outputs[0]).T

    boxes, confidences, class_ids = [], [], []

    for det in output:
        scores = det[4:]
        cid    = int(np.argmax(scores))
        conf   = float(scores[cid])

        if conf < CONF_THRESH:
            continue

        # Convert from letterboxed space back to original frame coords
        cx = (det[0] - pad_x) / scale
        cy = (det[1] - pad_y) / scale
        bw = det[2] / scale
        bh = det[3] / scale

        x1 = int(cx - bw / 2)
        y1 = int(cy - bh / 2)
        x2 = int(cx + bw / 2)
        y2 = int(cy + bh / 2)

        boxes.append([x1, y1, x2 - x1, y2 - y1])
        confidences.append(conf)
        class_ids.append(cid)

    indices = cv2.dnn.NMSBoxes(boxes, confidences, CONF_THRESH, NMS_THRESH)
    results = []
    if len(indices) > 0:
        for i in indices.flatten():
            x, y, bw, bh = boxes[i]
            label = class_names[class_ids[i]] if class_ids[i] < len(class_names) else str(class_ids[i])
            results.append((label, confidences[i], x, y, x + bw, y + bh))
    return results


# ─────────────────────────────────────────────
# REALSENSE SETUP
# ─────────────────────────────────────────────
pipeline = rs.pipeline()
config   = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

profile       = pipeline.start(config)
align         = rs.align(rs.stream.color)
depth_profile = rs.video_stream_profile(profile.get_stream(rs.stream.depth))
intrinsics    = depth_profile.get_intrinsics()

# ─────────────────────────────────────────────
# LOAD MODEL + CLASSES
# ─────────────────────────────────────────────
net         = load_model(MODEL_PATH)
class_names = load_classes(NAMES_PATH)
print(f"Loaded {len(class_names)} classes: {class_names}")

# ─────────────────────────────────────────────
# SOCKET SETUP
# ───────────────────────────────────────────── 

def send_coords_to_pi(point=None):
    # --- 1. Create the .txt file ---
    print(f"Creating local file: {file_path}")
    file_size = os.path.getsize(file_path)
    try:
        with open(file_path, 'w') as f:
            if file_size == 0 and point is not None:
                f.write(f"{point[0]}, {point[1]}, {point[2]}\n")
        print("Local file created successfully.")
    except Exception as e:
        print(f"Error creating file: {e}")

    # --- 2. Send the file ---
    print(f"Connecting to Raspberry Pi at {SERVER_HOST}:{SERVER_PORT}...")
    file_size = os.path.getsize(file_path) 
    if file_size != 0:
        try:
            # 1. Create a socket object
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            
                # 2. Connect to the server
                s.connect((SERVER_HOST, SERVER_PORT))
                print("Connected.")
            
                # 3. Open the file in 'read binary' (rb) mode
                with open(file_path, 'rb') as f:
                    while True:
                        # 4. Read a chunk of data from the file
                        bytes_read = f.read(BUFFER_SIZE)
                    
                        # If we're at the end of the file, bytes_read will be empty
                        if not bytes_read:
                            break
                    
                        # 5. Send the data chunk to the server
                        s.sendall(bytes_read)
                    
                # 6. The 'with' block will auto-close the connection here
                print(f"File '{file_path}' sent successfully.")

        except socket.error as e:
            print(f"Socket error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")


# ─────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────
detection_count = 0
coords_buffer   = []

try:
    while True:
        frames      = pipeline.wait_for_frames()
        aligned     = align.process(frames)
        depth_frame = aligned.get_depth_frame()
        color_frame = aligned.get_color_frame()

        if not depth_frame or not color_frame:
            continue

        color_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(depth_frame.get_data())

        detections = detect(net, color_image, class_names)
        is_centered = False

        for (label, conf, x1, y1, x2, y2) in detections:

            # Clamp box to frame boundaries
            # print(f"[1] Raw Box: {label} {conf:.2f} x1={x1} y1={y1} x2={x2} y2={y2}")
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(color_image.shape[1], x2)
            y2 = min(color_image.shape[0], y2)
            # print(f"[2] Clamped: x1={x1} y1={y1} x2={x2} y2={y2}")
            # Skip if box is invalid after clamping
            if x2 <= x1 or y2 <= y1:
                print("[3] SKIPPED: invalid box after clamp")
                continue

            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            # Skip dark regions
            roi_gray = cv2.cvtColor(
                color_image[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY
            )
            if roi_gray.mean() < BRIGHTNESS_THRESHOLD:
                print("[5] SKIPPED: Below brightness threshold") 
                continue

            # Get depth (meters)
            depth_m = depth_frame.get_distance(cx, cy)
            # print(f"[6] Depth: {depth_m:.3f}m")
            if depth_m == 0:
                continue

            # Deproject pixel → 3D point
            point_3d = rs.rs2_deproject_pixel_to_point(
                intrinsics, [cx, cy], depth_m
            )
            x_3d, y_3d, z_3d = point_3d

            ### -----------------------------------
            # applying physical camera offsets 
            if x_3d > 0: 
                x_3d = x_3d - CAMERA_WIDTH_OFFSET  
            else:
                x_3d = x_3d + CAMERA_WIDTH_OFFSET   
            if y_3d > 0:
                y_3d = y_3d + CAMERA_HEIGHT_OFFSET
            else:
                y_3d = y_3d - CAMERA_HEIGHT_OFFSET
            z_3d = z_3d - Z_OFFSET 
            ### -----------------------------------



            coords_buffer.append((x_3d, y_3d, z_3d))
            print(f"Detection: {label} {conf:.2f} | X:{x_3d:.3f} Y:{y_3d:.3f} Z:{z_3d:.3f}")
            detection_count += 1

            # Draw bounding box
            cv2.rectangle(color_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                color_image,
                f"{label} {conf:.2f} | X:{x_3d:.3f} Y:{y_3d:.3f} Z:{z_3d:.3f}",
                (x1, y1 - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
            )

            is_centered = (
                abs(cx - frame_center_x) < THRESHOLD and
                abs(cy - frame_center_y) < THRESHOLD
            )
        # After N consistent frames, save + send coords
        if detection_count >= DETECTION_FRAMES and coords_buffer and is_centered:
            avg_X = np.mean([c[0] for c in coords_buffer])
            avg_Y = np.mean([c[1] for c in coords_buffer])
            avg_Z = np.mean([c[2] for c in coords_buffer])

            std_X = np.std([c[0] for c in coords_buffer])
            std_Y = np.std([c[1] for c in coords_buffer])
            std_Z = np.std([c[2] for c in coords_buffer])
            is_stable = std_X < delta and std_Y < delta and std_Z < delta
            if is_stable:
                coord_str = f"{avg_X:.4f},{avg_Y:.4f},{avg_Z:.4f}\n"
                print(f"📍 Stable detection: {coord_str.strip()}")
                # Save to file
                with open(file_path, 'w') as f:
                    f.write(f"")
                send_coords_to_pi(point=[avg_X, avg_Y, avg_Z])
                

            # Reset buffers
            detection_count = 0
            coords_buffer   = []

        cv2.imshow("RealSense CUDA Detection", color_image)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    pipeline.stop()
    cv2.destroyAllWindows()
