from ultralytics import YOLO


model = YOLO(
    "yolo11s.pt"
)

model.train(
    data="datasets/traffic/data.yaml",

    epochs=100,

    imgsz=640,

    batch=16,

    device="cpu"
)