from fastapi import FastAPI, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware

from modules import cctv_detection, garbage_detection, traffic_prediction, emergency_routing, flood_forecast
import city_state

app = FastAPI(title="CityMind AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/cctv/analyze")
async def cctv_analyze(file: UploadFile = File(...), camera_zone: str = Query("Sector-21")):
    result = cctv_detection.analyze_frame(await file.read())

    if result["congestion_level"] == "High":
        city_state.update("traffic_level", "High")
    if result["alert"]:
        city_state.push_alert(f"[{camera_zone}] {result['alert']}")
        if result["fire_detected"] or result["accident_suspected"]:
            city_state.state["emergency_active"] += 1

    return result


@app.post("/garbage/detect")
async def garbage_detect(file: UploadFile = File(...), location: str = Query("Zone-A")):
    result = garbage_detection.detect_garbage_overflow(await file.read(), location)
    if result["is_overflowing"]:
        city_state.state["waste_alerts"] += 1
        city_state.push_alert(f"🗑️ Overflow at {location} — cleaning request created ({result['priority']} priority).")
    return result


@app.get("/traffic/predict")
def traffic_predict(current_density: float, weather: str = "clear", event_flag: bool = False):
    result = traffic_prediction.predict_congestion(current_density, weather, event_flag)
    city_state.update("traffic_level", result["level"])
    return result


@app.get("/flood/risk")
def flood_risk(rainfall_mm: float, river_level_pct: float, drainage_capacity_pct: float):
    result = flood_forecast.predict_flood_risk(rainfall_mm, river_level_pct, drainage_capacity_pct)
    city_state.update("flood_risk", result)
    if result["level"] in ("High", "Critical"):
        city_state.push_alert(f"🌊 {result['message']}")
    return result


@app.get("/emergency/route")
def emergency_route(incident_node: str):
    result = emergency_routing.route_emergency_vehicle(incident_node)
    if "error" not in result:
        city_state.state["emergency_active"] += 1
        city_state.push_alert(result["message"])
    return result


@app.get("/dashboard/status")
def dashboard_status():
    return city_state.snapshot()
