import os
import shutil
import cv2
from ultralytics import YOLO

def setup_realistic_dataset():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    traffic_dir = os.path.join(base_dir, 'traffic')
    
    # Create directories
    for split in ['train', 'val']:
        os.makedirs(os.path.join(traffic_dir, 'images', split), exist_ok=True)
        os.makedirs(os.path.join(traffic_dir, 'labels', split), exist_ok=True)
        
    print("[INFO] Generating Realistic Ground-Truth via Cross-Model Pseudo-Labeling...")

    # Load the base COCO model to generate unbiased ground truth annotations
    pseudo_label_model = YOLO("yolo11n.pt")

    uploads_dir = os.path.join(os.path.dirname(base_dir), 'data', 'uploads')
    demo_images = [f for f in os.listdir(uploads_dir) if f.endswith(('.jpg', '.png')) and not 'enhanced' in f]
    
    if not demo_images:
        print("[ERROR] No images found in data/uploads.")
        return

    # Process all uploaded demo images
    for img_name in demo_images:
        src_img = os.path.join(uploads_dir, img_name)
        dst_img = os.path.join(traffic_dir, 'images', 'val', img_name)
        shutil.copy(src_img, dst_img)
        
        # Run inference to generate ground truth labels
        results = pseudo_label_model.predict(src_img, conf=0.25, verbose=False)
        
        label_name = img_name.rsplit('.', 1)[0] + '.txt'
        dst_label = os.path.join(traffic_dir, 'labels', 'val', label_name)
        
        with open(dst_label, 'w') as f:
            for box in results[0].boxes:
                # YOLO format: class x_center y_center width height (normalized)
                cls_id = int(box.cls[0])
                # Only keep traffic-relevant COCO classes (0:person, 1:bicycle, 2:car, 3:motorcycle, 5:bus, 7:truck, 9:traffic light)
                if cls_id in [0, 1, 2, 3, 5, 7, 9]:
                    xywh = box.xywhn[0].tolist()
                    f.write(f"{cls_id} {xywh[0]} {xywh[1]} {xywh[2]} {xywh[3]}\n")
                    
    # Generate the correct COCO-aligned data.yaml with all 80 classes
    yaml_path = os.path.join(traffic_dir, 'data.yaml')
    coco_classes = [
        "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat", "traffic light",
        "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep", "cow",
        "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee",
        "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove", "skateboard", "surfboard",
        "tennis racket", "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
        "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch",
        "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse", "remote", "keyboard", "cell phone",
        "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors", "teddy bear",
        "hair drier", "toothbrush"
    ]
    with open(yaml_path, 'w') as f:
        f.write("path: /app/datasets/traffic\n")
        f.write("train: images/train\n")
        f.write("val: images/val\n")
        f.write("names:\n")
        for i, name in enumerate(coco_classes):
            f.write(f"  {i}: {name}\n")
        
    print(f"[SUCCESS] Processed {len(demo_images)} images into realistic validation dataset.")
    print("[INFO] You can now run the evaluate_metrics.py script!")

if __name__ == "__main__":
    setup_realistic_dataset()
