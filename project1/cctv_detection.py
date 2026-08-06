import cv2
import numpy as np
from ultralytics import YOLO

# Pretrained general object detector (COCO classes: person, car, truck, bus...)
_model = YOLO("yolov8n.pt")

VEHICLE_CLASSES = {"car", "truck", "bus", "motorcycle"}
PERSON_CLASS = "person"


def analyze_frame(image_bytes: bytes) -> dict:
    """
    Runs YOLOv8 on a single CCTV frame and returns traffic density,
    crowd detection, a fire/smoke heuristic, and an accident proxy.
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("Could not decode image")

    results = _model(frame, verbose=False)[0]
    names = results.names

    vehicle_count = 0
    person_count = 0
    boxes = []

    for box in results.boxes:
        cls_id = int(box.cls[0])
        label = names[cls_id]
        conf = float(box.conf[0])
        xyxy = box.xyxy[0].tolist()
        boxes.append({"label": label, "confidence": round(conf, 2), "bbox": xyxy})
        if label in VEHICLE_CLASSES:
            vehicle_count += 1
        elif label == PERSON_CLASS:
            person_count += 1

    fire_detected = _detect_fire_color(frame)
    accident_suspected = _detect_accident_proxy(boxes)
    crowd_detected = person_count >= 15  # tune per camera zone

    if vehicle_count >= 20:
        congestion_level = "High"
    elif vehicle_count >= 8:
        congestion_level = "Medium"
    else:
        congestion_level = "Low"

    alert = None
    if fire_detected:
        alert = "🔥 Fire/smoke suspected in camera feed. Verify immediately."
    elif accident_suspected:
        alert = "🚨 Possible accident detected — overlapping vehicles identified."
    elif crowd_detected:
        alert = f"👥 Crowd formation detected ({person_count} people)."
    elif congestion_level == "High":
        alert = f"🚦 Heavy congestion detected ({vehicle_count} vehicles)."

    return {
        "vehicle_count": vehicle_count,
        "person_count": person_count,
        "congestion_level": congestion_level,
        "fire_detected": fire_detected,
        "accident_suspected": accident_suspected,
        "crowd_detected": crowd_detected,
        "alert": alert,
        "detections": boxes,
    }


def _detect_fire_color(frame: np.ndarray) -> bool:
    """
    HSV color-threshold heuristic. Good enough for a demo; replace with a
    trained fire/smoke YOLO model (e.g. a Roboflow fire-smoke dataset)
    for real accuracy.
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower = np.array([18, 150, 150])
    upper = np.array([35, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    fire_ratio = np.count_nonzero(mask) / mask.size
    return fire_ratio > 0.05


def _iou(box1, box2) -> float:
    x1, y1 = max(box1[0], box2[0]), max(box1[1], box2[1])
    x2, y2 = min(box1[2], box2[2]), min(box1[3], box2[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union = area1 + area2 - inter
    return inter / union if union > 0 else 0


def _detect_accident_proxy(boxes: list) -> bool:
    """
    Proxy heuristic: two vehicles overlapping heavily in a single frame
    often indicates a collision. Real accident detection needs multi-frame
    tracking (sudden deceleration, orientation change) — this is a
    single-frame stand-in for the demo.
    """
    vehicle_boxes = [b["bbox"] for b in boxes if b["label"] in VEHICLE_CLASSES]
    for i in range(len(vehicle_boxes)):
        for j in range(i + 1, len(vehicle_boxes)):
            if _iou(vehicle_boxes[i], vehicle_boxes[j]) > 0.3:
                return True
    return False
