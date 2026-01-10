from ultralytics import YOLO

def train_full_resolution():
    # 1. Load a pretrained YOLO (nano) model. 
    model = YOLO('yolo11n.pt')

    # 2. Start Training
    model.train(
        data='data.yaml',        # Path to your dataset config
        epochs=50,              # Enough time for the model to converge
        imgsz=1280,              # Matches your vertical game resolution (resizes to 1080x1080)
        batch=8,                 # START LOW. Increase to 8 or 16 if VRAM allows
        device=0,                # Use 0 for your NVIDIA GPU
        workers=4,               # Number of CPU threads for data loading
        exist_ok=True,           # Overwrite existing experiment folder
        pretrained=True,
        optimizer='AdamW',       # Solid optimizer for these types of patterns
        # --- PERFORMANCE OPTIMIZATION ---
        rect=True,               # Optimizes for widescreen (16:9) aspect ratios
        amp=True,                # Uses Half-Precision (saves VRAM, increases speed)
        
        # --- AUGMENTATION ---
        # These help the AI ignore background noise and focus on shapes
        hsv_h=0.015,             # Hue jitter
        hsv_s=0.7,               # Saturation jitter
        hsv_v=0.4,               # Brightness jitter

        # degrees=0.0,             # Keep 0 for FPS (enemies don't walk on walls)
        # translate=0.1,           # Randomly moves targets (prevents coordinate-lock)
        # scale=0.5,               # Randomly zooms (crucial for long-distance enemies)

        fliplr=0.5,              # Flip left/right (mirrors the world)
        mosaic=1.0,              # Combines 4 images (great for small targets)
        close_mosaic=11,
        mixup=0.1,               # Overlays images to make detection harder
        erasing=0.4,             # Erase sections of images to improve partial accuracy
    )

if __name__ == '__main__':
    train_full_resolution()