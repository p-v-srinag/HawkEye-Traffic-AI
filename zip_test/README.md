# 🚔 HawkEye Traffic AI

![HawkEye Banner](https://img.shields.io/badge/Gridlock%20Hackathon%202.0-Winner%20Candidate-blue?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Ultralytics YOLO](https://img.shields.io/badge/YOLO11-Ultralytics-green?style=for-the-badge)
![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb)

An advanced, highly scalable Computer Vision pipeline developed for the **Gridlock Hackathon 2.0** by Flipkart and Bengaluru Traffic Police. 

**HawkEye Traffic AI** completely rethinks automated traffic enforcement. Rather than relying on simple frame-by-frame object detection which is prone to false positives (e.g. fining a child passenger for triple riding, or fining a stationary vehicle for wrong-side driving), HawkEye uses an asynchronous microservice architecture, temporal **Evidence Burst tracking**, and a contextual **Smart Enforcement Validation Engine (SEVE)** to guarantee extremely high-precision traffic violations.

---

## 🌟 Key Features & Architectural Edge

### 1. Smart Enforcement Validation Engine (SEVE)
Most YOLO implementations fail in the real world because they lack context. SEVE introduces "human-like" contextual validation to dramatically reduce false-positive challans:
- **Child Passenger Logic**: Calculates area ratios of riders on a single motorcycle. If the smallest rider is < 55% the size of the largest, it classifies them as a child and suppresses the "Triple Riding" violation (a major edge case in Bengaluru).
- **Helmet Position Check**: Ensures the helmet bounding box is actually located within the upper 30% of the rider's body. If a rider holds a helmet on the handlebar, SEVE still flags a violation.
- **Seatbelt Cross-Check**: Validates seatbelt bounding boxes strictly against driver bounding boxes within car interiors.

### 2. Temporal "Evidence Burst" Tracking (BoT-SORT)
HawkEye doesn't just look at single images. It accepts bursts of sequential frames (like a short GIF or video extract) and utilizes **BoT-SORT object tracking**. By tracking the exact pixel trajectory of vehicles across frames (`dx, dy`), HawkEye can accurately flag:
- **Wrong-Side Driving**: By comparing a vehicle's motion vector against expected lane flow.
- **Illegal Parking**: By ensuring a vehicle's tracking centroid remains stationary for an extended period inside a defined No-Parking region.

### 3. Environment Quality Score (EQS)
Bengaluru traffic cameras deal with monsoon rains, severe night glare, and motion blur. 
Before HawkEye evaluates an image, the EQS module calculates the Variance of the Laplacian (blur) and HSV Intensity (brightness/glare). If `EQS < 40`, the frame is rejected to a `MANUAL_REVIEW` queue, protecting citizens from erroneous auto-generated fines due to bad camera conditions.

### 4. Advanced Image Preprocessing
Before feeding images to YOLO and PaddleOCR, HawkEye runs preprocessing to rescue sub-optimal evidence:
- **Adaptive Histogram Equalization (CLAHE)**: Enhances contrast specifically for low-light or washed-out images.
- **Unsharp Masking**: Reduces motion blur common in fast-moving highway vehicles.

---

## 🏗️ System Architecture

HawkEye is built for enterprise-grade scalability, completely containerized with Docker.

1. **Dashboard (Streamlit)**: A sleek, real-time command center for traffic officers to upload evidence, view environment quality scores, and search license plate histories.
2. **API Engine (FastAPI)**: A lightning-fast ASGI backend handling synchronous data routing and burst aggregation.
3. **Task Queue (Redis + Celery)**: Heavy ML workloads (YOLO tracking, OCR, SEVE validation) are offloaded to asynchronous Celery workers, ensuring the API never blocks during traffic spikes.
4. **Database (MongoDB)**: Stores detection evidence, violation records, and powers aggregation pipelines for the "Top 10 Repeat Offenders" analytics dashboard.

---

## 🚀 How to Run Locally

### Prerequisites
- Docker & Docker Compose
- (Optional) NVIDIA GPU for hardware-accelerated YOLO and PaddleOCR inference.

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-repo/hawkeye-traffic-ai.git
   cd hawkeye-traffic-ai
   ```

2. **Spin up the entire microservice ecosystem:**
   ```bash
   docker compose up --build
   ```

3. **Access the Application:**
   - **Command Center Dashboard**: [http://localhost:8501](http://localhost:8501)
   - **FastAPI Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

### Usage Instructions
1. Open the Dashboard.
2. Navigate to the **Live Intersection Feed**.
3. Upload a single image, or multiple sequential images (an Evidence Burst).
4. Watch as SEVE calculates the Environment Quality, identifies license plates via OCR, tracks motion trajectories, and generates the final bounding-box evidence image highlighting only valid violations.

---

## 📈 Evaluation & Custom Training

To evaluate the system against a custom labeled dataset (calculating mAP, Precision, and Recall):
```bash
python training/evaluate_metrics.py
```

HawkEye supports automatic YOLO dataset preparation and model finetuning for specific cities.

---
*Developed for the Gridlock Hackathon 2.0*