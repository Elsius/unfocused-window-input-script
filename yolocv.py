import cv2
from ultralytics import YOLO
import numpy as np
import opencv_scout.cv_util
import time

# Load the model 
model = YOLO(r"runs\detect\train\weights\best.pt")

# Screen Capture
windowName = ""
gameWindow = opencv_scout.cv_util.WindowCapture(windowName)

print("YOLO is active. Press 'q' to quit.")

while True:
    # Grab frame
    screenshot = gameWindow.get_screenshot()
    frame = screenshot

    # Predict
    results = model.predict(frame, stream=True, imgsz=1280, conf=0.05)

    # Draw
    for r in results:
        annotated_frame = r.plot()
        
    cv2.imshow("YOLO Vision", annotated_frame)

    # Q to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()