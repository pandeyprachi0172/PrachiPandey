import joblib
import pandas as pd
from datetime import datetime

_model = joblib.load("traffic_model.pkl")
WEATHER_CODES = {"clear": 0, "rain": 1, "storm": 2, "fog": 3}


def predict_congestion(current_density: float, weather: str = "clear",
                        event_flag: bool = False, when: datetime = None) -> dict:
    when = when or datetime.now()
    features = pd.DataFrame([{
        "hour": when.hour,
        "day_of_week": when.weekday(),
        "current_density": current_density,
        "weather_code": WEATHER_CODES.get(weather, 0),
        "event_flag": int(event_flag),
    }])
    predicted = float(_model.predict(features)[0])

    if predicted >= 70:
        level, message = "High", f"Heavy congestion expected in 30 minutes ({predicted:.0f}/100). Suggest alternate routes."
    elif predicted >= 40:
        level, message = "Medium", f"Moderate congestion expected in 30 minutes ({predicted:.0f}/100)."
    else:
        level, message = "Low", f"Traffic expected to stay light ({predicted:.0f}/100)."

    return {"predicted_congestion": round(predicted, 1), "level": level, "message": message}
