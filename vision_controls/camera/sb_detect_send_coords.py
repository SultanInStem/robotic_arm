import cv2
import numpy as np
import joblib
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Load trained model and PCA
classifier = joblib.load("svm_model.pkl")
scaler = joblib.load("scaler.pkl")
pca = joblib.load("pca.pkl")

# Initialize the camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
	print("Error: Camera did not open")
	exit()
   	 
# File path for Raspberry Pi
COORD_FILE = "/home/agxorin3/Desktop/strawberry/strawberry_coords.txt"

def preprocess_frame(frame):
	"""Resize and preprocess a frame for PCA transformation."""
	frame = cv2.resize(frame, (50, 50))
	frame = frame.flatten().reshape(1, -1)
	frame = scaler.transform(frame)
	frame_pca = pca.transform(frame)
	return frame_pca

def detect_strawberries(frame):
	"""Detects strawberries using color thresholding and contour detection."""
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

while True:
	ret, frame = cap.read()
	if not ret:
		print("Error: Could not read the frame")
	if not cap.isOpened():
		print("Error: Can't see")
   	 

	strawberries = detect_strawberries(frame)
	pickable_strawberries = []

	for (x, y, w, h) in strawberries:
		strawberry_roi = frame[y:y+h, x:x+w]
		frame_pca = preprocess_frame(strawberry_roi)
		prediction = classifier.predict(frame_pca)[0]
		if prediction == 1:  # Only save "Pickable" strawberries
			label = "Pickable"
			color = (0, 255, 0)
			center_x = x + w // 2
			center_y = y + h // 2
			pickable_strawberries.append((center_x, center_y))
		cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
		cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
		
	with open(COORD_FILE, "w") as f:
		if len(pickable_strawberries) > 0:
			berry = pickable_strawberries[0]
			f.write(f"{berry[0]} {berry[1]}")

	cv2.imshow("Strawberry Detector", frame)

	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

cap.release()
cv2.destroyAllWindows()
