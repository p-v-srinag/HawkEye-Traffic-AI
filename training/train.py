from ultralytics import YOLO
import os

def train_custom_model():
    """
    Phase 5: Custom YOLOv11 Training Pipeline for HawkEye Traffic AI.
    This trains the model on the custom traffic dataset (helmets, plates, red lights).
    """
    print("==================================================")
    print("🚔 HawkEye AI - Initializing Custom Training Pipeline")
    print("==================================================")
    
    # Ensure dataset structure exists (Phase 4 placeholder)
    if not os.path.exists("datasets/traffic/data.yaml"):
        print("Error: data.yaml not found. Please pull the dataset from Roboflow into /datasets/traffic/")
        return

    # Initialize YOLOv11 small model (better accuracy than nano, but still fast)
    model = YOLO("yolo11s.pt") 

    # Start Training
    results = model.train(
        data="datasets/traffic/data.yaml",
        epochs=100,             # Full training cycle
        imgsz=640,              # Standard image size for traffic cameras
        batch=16,               # Batch size optimized for 16GB VRAM GPUs
        device="cpu",           # Change to '0' when running on an actual GPU server
        patience=20,            # Early stopping if mAP doesn't improve for 20 epochs
        save=True,              # Save the best weights
        project="weights",      # Output directory
        name="hawkeye_v1",      # Run name
        exist_ok=True
    )
    
    print("\n✅ Training Complete.")
    print("Best weights saved to: weights/hawkeye_v1/weights/best.pt")
    print("Next Step: Move best.pt to weights/best.pt and update YOLODetector in detection.py")

if __name__ == "__main__":
    train_custom_model()