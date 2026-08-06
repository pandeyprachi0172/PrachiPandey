import cv2
import numpy as np

# For production: fine-tune YOLOv8 on a garbage/overflow dataset
# (e.g. the TACO — Trash Annotations in Context — dataset) and load it:
#   from ultralytics import YOLO
#   _model = YOLO("garbage_model.pt")
# Fallback for this demo: visual clutter (edge density) correlates
# reasonably well with an overflowing bin vs. an empty/tidy one.


def detect_garbage_overflow(image_bytes: bytes, location: str = "unknown") -> dict:
    nparr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("Could not decode image")

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 80, 160)
    edge_density = np.count_nonzero(edges) / edges.size

    overflow_score = min(edge_density * 8, 1.0)
    is_overflowing = overflow_score > 0.35
    priority = "High" if overflow_score > 0.6 else "Medium" if is_overflowing else "Low"

    return {
        "location": location,
        "overflow_score": round(overflow_score, 2),
        "is_overflowing": is_overflowing,
        "priority": priority,
        "cleaning_request_created": is_overflowing,
    }
