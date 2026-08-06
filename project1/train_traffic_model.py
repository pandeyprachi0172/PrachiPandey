import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib


def generate_synthetic_data(n=5000, seed=42):
    rng = np.random.default_rng(seed)
    hour = rng.integers(0, 24, n)
    day_of_week = rng.integers(0, 7, n)
    current_density = rng.uniform(0, 100, n)
    weather_code = rng.integers(0, 4, n)  # 0=clear,1=rain,2=storm,3=fog
    event_flag = rng.integers(0, 2, n)

    is_peak = ((hour >= 8) & (hour <= 10)) | ((hour >= 17) & (hour <= 20))
    congestion = (
        current_density * 0.6
        + is_peak * 20
        + weather_code * 8
        + event_flag * 15
        + rng.normal(0, 5, n)
    )
    congestion = np.clip(congestion, 0, 100)

    return pd.DataFrame({
        "hour": hour, "day_of_week": day_of_week,
        "current_density": current_density,
        "weather_code": weather_code, "event_flag": event_flag,
        "congestion_30min": congestion,
    })


def train():
    df = generate_synthetic_data()
    X = df[["hour", "day_of_week", "current_density", "weather_code", "event_flag"]]
    y = df["congestion_30min"]
    model = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
    model.fit(X, y)
    joblib.dump(model, "traffic_model.pkl")
    print("Model trained and saved to traffic_model.pkl")


if __name__ == "__main__":
    train()
