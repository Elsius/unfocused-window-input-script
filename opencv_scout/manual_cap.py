import cv2
import os
import time
import numpy as np
from cv_util import WindowCapture

# CONFIG
WINDOW_NAME = "Manual Scouter - CLICK to Label | SPACE for Negative | Q to Quit"
SAVE_PATH = r"opencv_scout\training_data\images"
LABEL_PATH = r"opencv_scout\training_data\labels"
BOX_SIZE = 80  # Size of the box in pixels (w and h) around your click

os.makedirs(SAVE_PATH, exist_ok=True)
os.makedirs(LABEL_PATH, exist_ok=True)

wincap = WindowCapture("MapleStory Worlds-ChronoStory")
current_frame = None

def on_mouse(event, x, y, flags, param):
    global current_frame
    if event == cv2.EVENT_LBUTTONDOWN and current_frame is not None:
        # 1. Save Image
        timestamp = int(time.time() * 1000)
        img_name = f"manual_{timestamp}.jpg"
        txt_name = f"manual_{timestamp}.txt"
        cv2.imwrite(os.path.join(SAVE_PATH, img_name), current_frame)

        # 2. Calculate YOLO Label (Normalized)
        h, w = current_frame.shape[:2]
        x_center = x / w
        y_center = y / h
        nw = BOX_SIZE / w
        nh = BOX_SIZE / h

        # 3. Save .txt (Class 0)
        with open(os.path.join(LABEL_PATH, txt_name), "w") as f:
            f.write(f"0 {x_center:.6f} {y_center:.6f} {nw:.6f} {nh:.6f}\n")
        
        print(f"Captured Target at ({x}, {y}) -> Saved {img_name}")

cv2.namedWindow(WINDOW_NAME)
cv2.setMouseCallback(WINDOW_NAME, on_mouse)

while True:
    try:
        current_frame = wincap.get_screenshot()
        if current_frame is None: continue

        display_frame = current_frame.copy()
        
        # Draw a preview box around the mouse cursor to help aim
        # (This is just for your eyes, it won't be in the saved image)
        cv2.imshow(WINDOW_NAME, display_frame)
        
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord(' '): # SPACE for Negative Sample (No enemies)
            timestamp = int(time.time() * 1000)
            img_name = f"negative_{timestamp}.jpg"
            txt_name = f"negative_{timestamp}.txt"
            cv2.imwrite(os.path.join(SAVE_PATH, img_name), current_frame)
            # Create an EMPTY file for YOLO negative samples
            open(os.path.join(LABEL_PATH, txt_name), 'w').close()
            print(f"Saved Negative Sample: {img_name}")

    except Exception as e:
        print(f"Error: {e}")
        continue

cv2.destroyAllWindows()