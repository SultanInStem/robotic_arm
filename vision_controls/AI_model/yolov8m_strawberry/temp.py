from ultralytics import YOLO

model = YOLO("train/weights/best.pt")
model.export(format="onnx", imgsz=640, opset=12, simplify=True)