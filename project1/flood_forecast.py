def predict_flood_risk(rainfall_mm: float, river_level_pct: float, drainage_capacity_pct: float) -> dict:
    """
    Weighted risk score (0-100%).
    rainfall_mm: recent rainfall in mm
    river_level_pct: current level as % of danger threshold
    drainage_capacity_pct: % drainage capacity still available (higher = safer)
    """
    rainfall_norm = min(rainfall_mm / 100, 1.0)
    river_norm = river_level_pct / 100
    drainage_risk = 1 - (drainage_capacity_pct / 100)

    risk = round(min(max((rainfall_norm * 0.4 + river_norm * 0.4 + drainage_risk * 0.2) * 100, 0), 100), 1)

    if risk >= 75:
        level, message = "Critical", f"Flood risk {risk}%. Prepare emergency response and evacuation planning."
    elif risk >= 50:
        level, message = "High", f"Flood risk {risk}%. Alert drainage and emergency teams."
    elif risk >= 25:
        level, message = "Medium", f"Flood risk {risk}%. Monitor conditions closely."
    else:
        level, message = "Low", f"Flood risk {risk}%. No immediate action needed."

    return {"risk_percent": risk, "level": level, "message": message}
