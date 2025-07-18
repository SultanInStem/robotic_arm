import cv2
import numpy as np 
import torch
import pyrealsense2 as rs
import time
import torchvision

COORD_FILE = "/home/agxorin3/Desktop/strawberry/strawberry_coords.txt"
device = 'cuda' if torch.cuda.is_available() else 'cpu'
loaded = torch.load('yolo/my_model.pt', map_location=device)

# Extract the model object if stored in a dict (common practice)
model = loaded['model'] if isinstance(loaded, dict) and 'model' in loaded else loaded
model.to(device).eval()

def xywh2xyxy(x):
    """Convert nx4 boxes from [x, y, w, h] to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right."""
    y = x.clone() if isinstance(x, torch.Tensor) else np.copy(x)
    y[..., 0] = x[..., 0] - x[..., 2] / 2  # top left x
    y[..., 1] = x[..., 1] - x[..., 3] / 2  # top left y
    y[..., 2] = x[..., 0] + x[..., 2] / 2  # bottom right x
    y[..., 3] = x[..., 1] + x[..., 3] / 2  # bottom right y
    return y


def box_iou(box1, box2, eps=1e-7):
    # https://github.com/pytorch/vision/blob/master/torchvision/ops/boxes.py
    """
    Return intersection-over-union (Jaccard index) of boxes.

    Both sets of boxes are expected to be in (x1, y1, x2, y2) format.

    Arguments:
        box1 (Tensor[N, 4])
        box2 (Tensor[M, 4])

    Returns:
        iou (Tensor[N, M]): the NxM matrix containing the pairwise
            IoU values for every element in boxes1 and boxes2
    """
    # inter(N,M) = (rb(N,M,2) - lt(N,M,2)).clamp(0).prod(2)
    (a1, a2), (b1, b2) = box1.unsqueeze(1).chunk(2, 2), box2.unsqueeze(0).chunk(2, 2)
    inter = (torch.min(a2, b2) - torch.max(a1, b1)).clamp(0).prod(2)

    # IoU = inter / (area1 + area2 - inter)
    return inter / ((a2 - a1).prod(2) + (b2 - b1).prod(2) - inter + eps)
def non_max_suppression(
    prediction,
    conf_thres=0.25,
    iou_thres=0.45,
    classes=None,
    agnostic=False,
    multi_label=False,
    labels=(),
    max_det=300,
    nm=0,  # number of masks
):
    """
    Non-Maximum Suppression (NMS) on inference results to reject overlapping detections.

    Returns:
         list of detections, on (n,6) tensor per image [xyxy, conf, cls]
    """
    # Checks
    assert 0 <= conf_thres <= 1, f"Invalid Confidence threshold {conf_thres}, valid values are between 0.0 and 1.0"
    assert 0 <= iou_thres <= 1, f"Invalid IoU {iou_thres}, valid values are between 0.0 and 1.0"
    if isinstance(prediction, (list, tuple)):  # YOLOv5 model in validation model, output = (inference_out, loss_out)
        prediction = prediction[0]  # select only inference output

    device = prediction.device
    mps = "mps" in device.type  # Apple MPS
    if mps:  # MPS not fully supported yet, convert tensors to CPU before NMS
        prediction = prediction.cpu()
    bs = prediction.shape[0]  # batch size
    nc = prediction.shape[2] - nm - 5  # number of classes
    xc = prediction[..., 4] > conf_thres  # candidates

    # Settings
    # min_wh = 2  # (pixels) minimum box width and height
    max_wh = 7680  # (pixels) maximum box width and height
    max_nms = 30000  # maximum number of boxes into torchvision.ops.nms()
    time_limit = 0.5 + 0.05 * bs  # seconds to quit after
    redundant = True  # require redundant detections
    multi_label &= nc > 1  # multiple labels per box (adds 0.5ms/img)
    merge = False  # use merge-NMS

    t = time.time()
    mi = 5 + nc  # mask start index
    output = [torch.zeros((0, 6 + nm), device=prediction.device)] * bs
    for xi, x in enumerate(prediction):  # image index, image inference
        # Apply constraints
        # x[((x[..., 2:4] < min_wh) | (x[..., 2:4] > max_wh)).any(1), 4] = 0  # width-height
        x = x[xc[xi]]  # confidence

        # Cat apriori labels if autolabelling
        if labels and len(labels[xi]):
            lb = labels[xi]
            v = torch.zeros((len(lb), nc + nm + 5), device=x.device)
            v[:, :4] = lb[:, 1:5]  # box
            v[:, 4] = 1.0  # conf
            v[range(len(lb)), lb[:, 0].long() + 5] = 1.0  # cls
            x = torch.cat((x, v), 0)

        # If none remain process next image
        if not x.shape[0]:
            continue

        # Compute conf
        x[:, 5:] *= x[:, 4:5]  # conf = obj_conf * cls_conf

        # Box/Mask
        box = xywh2xyxy(x[:, :4])  # center_x, center_y, width, height) to (x1, y1, x2, y2)
        mask = x[:, mi:]  # zero columns if no masks

        # Detections matrix nx6 (xyxy, conf, cls)
        if multi_label:
            i, j = (x[:, 5:mi] > conf_thres).nonzero(as_tuple=False).T
            x = torch.cat((box[i], x[i, 5 + j, None], j[:, None].float(), mask[i]), 1)
        else:  # best class only
            conf, j = x[:, 5:mi].max(1, keepdim=True)
            x = torch.cat((box, conf, j.float(), mask), 1)[conf.view(-1) > conf_thres]

        # Filter by class
        if classes is not None:
            x = x[(x[:, 5:6] == torch.tensor(classes, device=x.device)).any(1)]

        # Apply finite constraint
        # if not torch.isfinite(x).all():
        #     x = x[torch.isfinite(x).all(1)]

        # Check shape
        n = x.shape[0]  # number of boxes
        if not n:  # no boxes
            continue
        x = x[x[:, 4].argsort(descending=True)[:max_nms]]  # sort by confidence and remove excess boxes

        # Batched NMS
        c = x[:, 5:6] * (0 if agnostic else max_wh)  # classes
        boxes, scores = x[:, :4] + c, x[:, 4]  # boxes (offset by class), scores
        i = torchvision.ops.nms(boxes, scores, iou_thres)  # NMS
        i = i[:max_det]  # limit detections
        if merge and (1 < n < 3e3):  # Merge NMS (boxes merged using weighted mean)
            # update boxes as boxes(i,4) = weights(i,n) * boxes(n,4)
            iou = box_iou(boxes[i], boxes) > iou_thres  # iou matrix
            weights = iou * scores[None]  # box weights
            x[i, :4] = torch.mm(weights, x[:, :4]).float() / weights.sum(1, keepdim=True)  # merged boxes
            if redundant:
                i = i[iou.sum(1) > 1]  # require redundancy

        output[xi] = x[i]
        if mps:
            output[xi] = output[xi].to(device)
        if (time.time() - t) > time_limit:
            print("WARNING ⚠️ NMS time limit")
            break  # time limit exceeded

    return output



def pixel_to_metric(intrinsics, x,y, depth): 
    point = rs.rs2_deproject_pixel_to_point(intrinsics, [x,y], depth)
    return point[0], point[1], point[2] # Returns X,Y,Z in meters
def preprocess(image, img_size=640):
    h0, w0 = image.shape[:2]
    r = img_size / max(h0, w0)
    new_unpad = int(w0 * r), int(h0 * r)
    image_resized = cv2.resize(image, new_unpad, interpolation=cv2.INTER_LINEAR)

    dw = img_size - new_unpad[0]
    dh = img_size - new_unpad[1]
    top, bottom = dh // 2, dh - (dh // 2)
    left, right = dw // 2, dw - (dw // 2)

    image_padded = cv2.copyMakeBorder(image_resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114,114,114))
    image_rgb = cv2.cvtColor(image_padded, cv2.COLOR_BGR2RGB)

    # Convert to tensor and ensure float16
    img_tensor = torch.from_numpy(image_rgb).permute(2,0,1).float() / 255.0
    img_tensor = img_tensor.to(device, dtype=torch.float16)  # Convert to float16
    img_tensor = img_tensor.unsqueeze(0)  # Add batch dimension

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

