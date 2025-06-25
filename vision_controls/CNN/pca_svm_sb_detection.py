import cv2
import numpy as np
import joblib
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Load the trained model and PCA
classifier = joblib.load("svm_model.pkl")  # Load trained SVM model
scaler = joblib.load("scaler.pkl")  # Load scaler
pca = joblib.load("pca.pkl")  # Load PCA model

# Initialize the camera
cap = cv2.VideoCapture(0)  # Change to the correct camera index if needed

if not cap.isOpened():
    print("Error: Did not open the camera")
    exit()

def preprocess_frame(frame):
    """Resize and preprocess a frame for PCA transformation."""
    frame = cv2.resize(frame, (50, 50))  # Resize to match training images
    frame = frame.flatten().reshape(1, -1)  # Flatten and reshape
    frame = scaler.transform(frame)  # Standardize
    frame_pca = pca.transform(frame)  # Apply PCA
    return frame_pca

def detect_strawberries(frame):
    """Detects strawberries using color thresholding and contour detection."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_red = np.array([0, 120, 70])  # Adjust based on strawberry color
    upper_red = np.array([10, 255, 255])
    
    mask1 = cv2.inRange(hsv, lower_red, upper_red)  # Red color mask (lower range)

    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)  # Red color mask (upper range)

    mask = mask1 + mask2  # Combine both masks

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    strawberries = []
    for contour in contours:
        if cv2.contourArea(contour) > 500:  # Adjust minimum area threshold
            x, y, w, h = cv2.boundingRect(contour)
            strawberries.append((x, y, w, h))

    return strawberries

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read the frame")
        break

    strawberries = detect_strawberries(frame)

    for (x, y, w, h) in strawberries:
        strawberry_roi = frame[y:y+h, x:x+w]  # Extract the detected strawberry
        frame_pca = preprocess_frame(strawberry_roi)  # Preprocess
        prediction = classifier.predict(frame_pca)[0]

        # Assign label and bounding box color
        if prediction == 1:
            label = "Pickable" 
            color = (0, 255, 0)

        # Draw bounding box and label
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    cv2.imshow("Strawberry Detector", frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
