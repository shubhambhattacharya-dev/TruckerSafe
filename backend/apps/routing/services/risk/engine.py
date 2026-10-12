from enum import IntEnum
from typing import Dict, Any, Tuple, Optional


class RiskBand(IntEnum):
    """
    Risk bands mapped 1 to 5 to enable deterministic 'worst-of-three'
    aggregation via Python's built-in max().
    """
    LOW = 1
    MODERATE = 2
    HIGH = 3
    SEVERE = 4
    NO_TRAVEL = 5


def classify_wind(wind_mph: float) -> RiskBand:
    """PDF Wind Thresholds: <25 (Low), 25-34 (Mod), 35-44 (High), 45-54 (Severe), >=55 (No Travel)"""
    if wind_mph >= 55.0:
        return RiskBand.NO_TRAVEL
    if wind_mph >= 45.0:
        return RiskBand.SEVERE
    if wind_mph >= 35.0:
        return RiskBand.HIGH
    if wind_mph >= 25.0:
        return RiskBand.MODERATE
    return RiskBand.LOW


def classify_rain(rain_in_hr: float) -> RiskBand:
    """PDF Rain Thresholds: <0.10 (Low), 0.10-0.25 (Mod), 0.25-0.50 (High), 0.50-1.00 (Severe), >1.00 (No Travel)"""
    if rain_in_hr > 1.00:
        return RiskBand.NO_TRAVEL
    if rain_in_hr >= 0.50:
        return RiskBand.SEVERE
    if rain_in_hr >= 0.25:
        return RiskBand.HIGH
    if rain_in_hr >= 0.10:
        return RiskBand.MODERATE
    return RiskBand.LOW


def classify_snow(snow_in_hr: float) -> RiskBand:
    """PDF Snow Thresholds: <0.5 (Low), 0.5-1.0 (Mod), 1.0-2.0 (High), 2.0-3.0 (Severe), >3.0 (No Travel)"""
    if snow_in_hr > 3.00:
        return RiskBand.NO_TRAVEL
    if snow_in_hr >= 2.00:
        return RiskBand.SEVERE
    if snow_in_hr >= 1.00:
        return RiskBand.HIGH
    if snow_in_hr >= 0.50:
        return RiskBand.MODERATE
    return RiskBand.LOW


def classify_checkpoint(
    wind_mph: float, 
    rain_in_hr: float, 
    snow_in_hr: float, 
    load_lb: float
) -> Tuple[RiskBand, Dict[str, Any]]:
    """
    1. Evaluates independent weather condition bands (wind, rain, snow).
    2. Determines base risk by taking the worst condition across the three.
    3. Applies vehicle load weight safety overrides from PDF:
       - Wind >= 55 mph -> No Travel (any load)
       - Wind 45-54 mph + load > 30,000 lb -> No Travel
       - Wind 35-44 mph + load > 40,000 lb -> Severe
    """
    w_band = classify_wind(wind_mph)
    r_band = classify_rain(rain_in_hr)
    s_band = classify_snow(snow_in_hr)

    
    base_band = max(w_band, r_band, s_band)
    final_band = base_band
    load_rule_triggered = False
    override_reason: Optional[str] = None

    if w_band == RiskBand.NO_TRAVEL:
        load_rule_triggered = True
        final_band = RiskBand.NO_TRAVEL
        override_reason = "Wind speed >= 55 mph triggers No Travel for any load."
    elif w_band == RiskBand.SEVERE and load_lb > 30000.0:
        load_rule_triggered = True
        final_band = RiskBand.NO_TRAVEL
        override_reason = "Wind 45-54 mph with load > 30,000 lb triggers No Travel."
    elif w_band == RiskBand.HIGH and load_lb > 40000.0:
        load_rule_triggered = True
        if final_band < RiskBand.SEVERE:
            final_band = RiskBand.SEVERE
        override_reason = "Wind 35-44 mph with load > 40,000 lb upgrades risk to Severe."

    metadata = {
        "wind_band": w_band.name,
        "rain_band": r_band.name,
        "snow_band": s_band.name,
        "base_band": base_band.name,
        "final_band": final_band.name,
        "load_rule_triggered": load_rule_triggered,
        "load_override_changed_risk": (final_band != base_band),
        "load_override_applied": (final_band != base_band),
        "override_reason": override_reason,
    }
    return final_band, metadata
