from ultralytics import YOLO
import time

def evaluate_model(weights_path="weights/yolo11n.pt", data_yaml="datasets/traffic/data.yaml"):
    """
    Evaluates the HawkEye Traffic AI model on the validation dataset.
    Calculates Accuracy, Precision, Recall, F1-score, and mAP50-95.
    """
    print("==================================================")
    print("🚔 HawkEye AI - Performance Evaluation Module")
    print("==================================================")
    
    try:
        model = YOLO(weights_path)
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    print(f"\nEvaluating weights: {weights_path}")
    print("Running validation... This may take a moment depending on the dataset size.\n")

    start_time = time.time()
    
    try:
        # Run YOLO validation
        metrics = model.val(data=data_yaml, split="val")
        
        # Extract metrics
        precision = metrics.results_dict.get('metrics/precision(B)', 0.0)
        recall = metrics.results_dict.get('metrics/recall(B)', 0.0)
        map50 = metrics.results_dict.get('metrics/mAP50(B)', 0.0)
        map50_95 = metrics.results_dict.get('metrics/mAP50-95(B)', 0.0)
        
        # Calculate F1-Score
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        # Note: True 'Accuracy' in object detection is often represented by mAP, 
        # but if we wanted classification accuracy, it would be a separate metric.
        # We will print mAP as the primary accuracy metric.
        
        end_time = time.time()
        eval_time = end_time - start_time
        
        print("\n" + "="*50)
        print("📊 Evaluation Results:")
        print("="*50)
        print(f"Precision: {precision:.4f}")
        print(f"Recall:    {recall:.4f}")
        print(f"F1-Score:  {f1_score:.4f}")
        print(f"mAP@50:    {map50:.4f}")
        print(f"mAP@50-95: {map50_95:.4f}")
        print(f"\nComputational Efficiency:")
        print(f"Evaluation Time: {eval_time:.2f} seconds")
        print(f"Inference Speed: {metrics.speed['inference']:.2f} ms/img")
        print("="*50)
        
    except Exception as e:
        print(f"\n⚠️ Note: Validation requires the dataset to be present in '{data_yaml}'.")
        print("If you haven't downloaded the dataset yet, run this script after Phase 4.")
        print(f"Error detail: {e}")

if __name__ == "__main__":
    evaluate_model()