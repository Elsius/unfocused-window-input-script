import cv2
import numpy as np
from mss import mss
import time
import os
import cv_util

# Use to quickly scout an initial dataset
# --- SETTINGS ---
windowName = ""
threshold = 0.65  
CLASS_ID = 0
SAVE_DIR = r"opencv_scout\training_data"
os.makedirs(f"{SAVE_DIR}/images", exist_ok=True)
os.makedirs(f"{SAVE_DIR}/labels", exist_ok=True)
save = False

# Load sprite
template_l = cv2.imread(r'opencv_scout\sprites\green_mushroom.png', 0)
tw, th = template_l.shape[::-1]
template_r = cv2.flip(template_l,1)

gameWindow = cv_util.WindowCapture(windowName)
sct = mss()
monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}

while True:
    screenshot = gameWindow.get_screenshot()
    if screenshot is None or not hasattr(screenshot, 'shape') or screenshot.shape[0] == 0:
        continue

    try:
        frame = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    except Exception:
        print('failed to frame')
        continue

    # Multi-match detection
    res_l = cv2.matchTemplate(gray, template_l, cv2.TM_CCOEFF_NORMED)
    res_r = cv2.matchTemplate(gray, template_r, cv2.TM_CCOEFF_NORMED)

    loc_l = np.where(res_l >= threshold)
    loc_r = np.where(res_r >= threshold)
    # Build initial rectangle list
    rects = []
    for pt in zip(*loc_l[::-1]):
        rects.append([int(pt[0]), int(pt[1]), tw, th])
        rects.append([int(pt[0]), int(pt[1]), tw, th])
    for pt in zip(*loc_r[::-1]):
        rects.append([int(pt[0]), int(pt[1]), tw, th])
        rects.append([int(pt[0]), int(pt[1]), tw, th])

    # Apply grouping
    rects, weights = cv2.groupRectangles(rects, groupThreshold=1, eps=0.5)

    if len(rects) > 0:
        timestamp = int(time.time() * 1000)
        labels = []
        img_h, img_w = frame.shape[:2]
        for (x, y, w, h) in rects:
            # Draw visual feedback
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Calculate YOLO Normalized Coordinates for each target
            x_center = (x + tw/2) / img_w
            y_center = (y + th/2) / img_h
            w_norm = tw / img_w
            h_norm = th / img_h
            labels.append(f"{CLASS_ID} {x_center} {y_center} {w_norm} {h_norm}")

        # Save Image and multi-target Label file
        if save == True:
            cv2.imwrite(f"{SAVE_DIR}/images/frame_{timestamp}.jpg", frame)
            with open(f"{SAVE_DIR}/labels/frame_{timestamp}.txt", "w") as f:
                f.write("\n".join(labels))
            time.sleep(0.5)
        
        print(f"Captured {len(rects)} targets in frame_{timestamp}")

    cv2.imshow("Multi-Target Scout", frame)
    if cv2.waitKey(1) == ord('q'): break

cv2.destroyAllWindows()