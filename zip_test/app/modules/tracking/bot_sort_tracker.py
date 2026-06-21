import numpy as np

class BurstTracker:
    """
    Analyzes temporal trajectories from an Evidence Burst (sequence of images)
    to determine vehicle movement direction and stationary status.
    """
    def __init__(self):
        self.tracks = {}  # {track_id: [(x, y, timestamp_index), ...]}
        
    def update(self, detections: list, frame_index: int):
        for det in detections:
            track_id = det.get("track_id")
            if track_id is not None:
                # Calculate centroid
                x1, y1, x2, y2 = det["bbox"]
                cx = (x1 + x2) / 2.0
                cy = (y1 + y2) / 2.0
                
                if track_id not in self.tracks:
                    self.tracks[track_id] = []
                self.tracks[track_id].append((cx, cy, frame_index))
                
    def get_trajectory_analysis(self, track_id: int):
        """
        Calculates total movement and general direction.
        Returns: 
        - is_stationary: True if movement is negligible across the burst.
        - direction: Vector representing overall direction (dx, dy).
        """
        history = self.tracks.get(track_id, [])
        if len(history) < 2:
            return {"is_stationary": True, "direction": (0, 0), "displacement": 0}
            
        start_pt = history[0]
        end_pt = history[-1]
        
        dx = end_pt[0] - start_pt[0]
        dy = end_pt[1] - start_pt[1]
        
        displacement = np.sqrt(dx**2 + dy**2)
        
        # Threshold for considering a vehicle "stationary" across the burst
        # Assuming burst covers ~2-5 seconds, movement < 20 pixels is considered stationary
        is_stationary = displacement < 20.0
        
        return {
            "is_stationary": is_stationary,
            "direction": (dx, dy),
            "displacement": displacement
        }
