from ultralytics import YOLO 
import cv2 


model = YOLO("yolov8s.pt")

img = cv2.imread("test1_resized.jpeg")

results = model(img)
print(results)
results[0].show()
