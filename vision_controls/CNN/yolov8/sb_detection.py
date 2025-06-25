import cv2
from ultralytics import YOLO

model = YOLO("best.pt")
class_names = model.names

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

while True:
    success, frame = cap.read()
    if not success:
        break

    results = model(frame, stream=True)

    for r in results:
        boxes = r.boxes
        for box in boxes:
            confidence = float(box.conf[0])
            if confidence < 0.5:
                continue
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls = int(box.cls[0])
            label = f'{class_names[cls]} {round(confidence * 100, 1)}%'

            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 0, 255), 2)

    cv2.imshow('Webcam', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
