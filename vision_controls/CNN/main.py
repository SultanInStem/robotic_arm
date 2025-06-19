from ultralytics import YOLO 
import cv2 


model = YOLO("yolov8m.pt")

img = cv2.imread("test.jpeg")

results = model(img)
for r in results: 
    for box in r.boxes: 
        cls_id = int(box.cls[0])
        if model.names[cls_id].lower() == "strawberry": 
            print("It's a strawberry")
