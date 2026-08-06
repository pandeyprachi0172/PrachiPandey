from threading import Lock

_lock = Lock()

state = {
    "traffic_level": "Low",
    "flood_risk": {"risk_percent": 0, "level": "Low"},
    "waste_alerts": 0,
    "streetlights_faulty": 5,  # static demo value; wire to a real fault-detection feed
    "emergency_active": 0,
    "alerts": [],
}


def push_alert(message: str):
    with _lock:
        state["alerts"].insert(0, message)
        state["alerts"] = state["alerts"][:20]


def update(key, value):
    with _lock:
        state[key] = value


def snapshot():
    with _lock:
        return dict(state)
