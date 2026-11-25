import os
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional, Literal

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from db import db_manager
from weather_service import fetch_live_weather_and_soil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
ARTIFACT_PATH = os.path.join(BASE_DIR, "crop_stress_artifacts.joblib")

ARTIFACTS: Dict[str, Any] = {}

def load_artifacts():
    if not ARTIFACTS:
        if not os.path.exists(ARTIFACT_PATH):
            raise RuntimeError(f"Artifact file not found: {ARTIFACT_PATH}")
        ARTIFACTS.update(joblib.load(ARTIFACT_PATH))
        print(f"[ML] Loaded models: {ARTIFACTS.get('reg_model_name')} & {ARTIFACTS.get('cls_model_name')}")
        print(f"[ML] Registered crops: {len(ARTIFACTS.get('crop_registry', {}))} crops")

# Preload artifacts on import
load_artifacts()

RISK_LABELS = {0: "Low", 1: "Moderate", 2: "High", 3: "Critical"}
STAGE_WEIGHTS = {
    "Initial": 0.65,
    "Development": 0.80,
    "Mid_Season": 1.00,
    "Late_Season": 0.35,
}

LITERS_PER_MM_ACRE = 4046.86


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_artifacts()
    yield


app = FastAPI(
    title="Farmer Water & Crop Allocation Tool",
    description="Interactive Live Agronomic Water Allocation & FAO-56 Stress Modeling for AP & Telangana Farmers",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# Strict Domain Validation Schemas
# -----------------------------------------------------------------------------
GrowthStageType = Literal["Initial", "Development", "Mid_Season", "Late_Season"]
SoilTypeName = Literal["Black_Clay", "Red_Sandy", "Alluvial_Loam"]

class FarmerPlotItem(BaseModel):
    plot_id: str = Field(..., min_length=1, max_length=50, example="Plot_1")
    crop_type: str = Field(..., example="Cotton")
    growth_stage: GrowthStageType = "Mid_Season"
    area_acres: float = Field(..., gt=0.0, le=100.0, example=2.0)
    custom_soil_moisture: Optional[float] = Field(None, ge=0.05, le=0.95, example=0.38)


class SimulateAllocationRequest(BaseModel):
    cluster_name: str = Field(..., min_length=2, example="Shadnagar Ayacut Cluster")
    available_water_liters: float = Field(..., ge=1000.0, le=5000000.0, example=50000.0)
    water_source_type: Optional[str] = "Borewell"
    plots: List[FarmerPlotItem] = Field(..., min_length=1)


# -----------------------------------------------------------------------------
# Agronomic ML Inference Helpers (with Strict Physical Clamping)
# -----------------------------------------------------------------------------
def run_model_inference(
    crop_type: str,
    growth_stage: str,
    soil_type: str,
    sm_top: float,
    sm_root: float,
    sm_prof: float,
    prev_sm_root: float,
    temp_max: float,
    temp_min: float,
    humidity: float,
    wind_speed: float,
    solar_radiation: float,
    rainfall_10d: float,
    et0_10d: float,
) -> Dict[str, Any]:
    crop_registry = ARTIFACTS["crop_registry"]
    if crop_type not in crop_registry:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown crop_type '{crop_type}'. Available: {list(crop_registry.keys())}",
        )

    traits = crop_registry[crop_type]
    kc = traits["kc"][growth_stage]
    crit_sm = traits["crit_sm"]
    temp_max_tol = traits["temp_max_tol"]
    root_depth = traits["root_depth"]

    # Strict clamping to training distribution to prevent out-of-domain extrapolation
    c_sm_top = float(np.clip(sm_top, 0.05, 0.95))
    c_sm_root = float(np.clip(sm_root, 0.05, 0.95))
    c_sm_prof = float(np.clip(sm_prof, 0.05, 0.95))
    c_prev_sm = float(np.clip(prev_sm_root, 0.05, 0.95))

    c_tmax = float(np.clip(temp_max, 15.0, 50.0))
    c_tmin = float(np.clip(temp_min, 5.0, 40.0))
    c_humidity = float(np.clip(humidity, 10.0, 100.0))
    c_wind = float(np.clip(wind_speed, 0.1, 15.0))
    c_solar = float(np.clip(solar_radiation, 5.0, 35.0))
    c_rain = float(np.clip(rainfall_10d, 0.0, 300.0))
    c_et0 = float(np.clip(et0_10d, 5.0, 100.0))

    t_avg = (c_tmax + c_tmin) / 2.0
    es = 0.6108 * np.exp((17.27 * t_avg) / (t_avg + 237.3))
    vpd = float(np.clip(es * (1.0 - (c_humidity / 100.0)), 0.0, 6.0))

    moisture_margin = c_sm_root - crit_sm
    heat_excess = c_tmax - temp_max_tol
    temp_range = c_tmax - c_tmin
    net_water_balance = c_rain - c_et0
    soil_moisture_delta = float(np.clip(c_sm_root - c_prev_sm, -0.15, 0.15))

    row = {
        "soil_moisture_top": c_sm_top,
        "soil_moisture_root": c_sm_root,
        "soil_moisture_prof": c_sm_prof,
        "temp_max": c_tmax,
        "temp_min": c_tmin,
        "humidity": c_humidity,
        "wind_speed": c_wind,
        "solar_radiation": c_solar,
        "rainfall_10d": c_rain,
        "et0_10d": c_et0,
        "kc": kc,
        "crit_sm": crit_sm,
        "temp_max_tol": temp_max_tol,
        "root_depth": root_depth,
        "vpd": vpd,
        "temp_range": temp_range,
        "net_water_balance": net_water_balance,
        "heat_excess": heat_excess,
        "moisture_margin": moisture_margin,
        "prev_soil_moisture_root": c_prev_sm,
        "soil_moisture_delta": soil_moisture_delta,
        "growth_stage_encoded": ARTIFACTS["stage_order"][growth_stage],
        "soil_type_Alluvial_Loam": 1 if soil_type == "Alluvial_Loam" else 0,
        "soil_type_Black_Clay": 1 if soil_type == "Black_Clay" else 0,
        "soil_type_Red_Sandy": 1 if soil_type == "Red_Sandy" else 0,
    }

    X = pd.DataFrame([row])[ARTIFACTS["feature_cols"]]
    csi = float(np.clip(ARTIFACTS["reg_model"].predict(X)[0], 0.0, 1.0))
    risk_idx = int(ARTIFACTS["cls_model"].predict(X)[0])

    drivers = []
    if moisture_margin < -0.05:
        drivers.append(f"Root moisture severely below threshold by {abs(moisture_margin):.2f}")
    elif moisture_margin < 0:
        drivers.append(f"Root moisture below critical limit ({abs(moisture_margin):.2f})")

    if heat_excess > 2.5:
        drivers.append(f"Severe thermal stress (+{heat_excess:.1f}°C above tolerance)")
    elif heat_excess > 0:
        drivers.append(f"Mild heat excess (+{heat_excess:.1f}°C)")

    if vpd > 2.6:
        drivers.append(f"High atmospheric drying demand (VPD {vpd:.2f} kPa)")

    if net_water_balance < -35.0:
        drivers.append(f"10d net moisture deficit ({net_water_balance:.1f} mm)")

    if not drivers:
        drivers.append("Optimal physiological & moisture conditions")

    return {
        "crop_type": crop_type,
        "crop_category": traits["category"],
        "predicted_csi": round(csi, 4),
        "risk_level": RISK_LABELS.get(risk_idx, "Moderate"),
        "primary_driver": drivers[0],
        "all_drivers": drivers,
        "crit_sm": crit_sm,
        "temp_max_tol": temp_max_tol,
        "kc": kc,
        "root_depth": root_depth,
        "effective_sm_root": round(c_sm_root, 3),
    }


def compute_priority_score(csi: float, growth_stage: str) -> float:
    stage_w = STAGE_WEIGHTS.get(growth_stage, 0.70)
    return round(100.0 * (0.70 * csi + 0.30 * stage_w), 2)


# -----------------------------------------------------------------------------
# Static Files & Root
# -----------------------------------------------------------------------------
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def get_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Farmer Water & Crop Allocation Tool is running."}


# -----------------------------------------------------------------------------
# Functional API Endpoints
# -----------------------------------------------------------------------------
@app.get("/api/regions")
def get_regions(state: Optional[str] = Query(None, description="Filter clusters by State")):
    """Returns the list of localized Telangana & Andhra Pradesh farm clusters."""
    regions = db_manager.get_all_regions(state_filter=state)
    all_regions = db_manager.get_all_regions()
    unique_states = sorted(list(set(r["state"] for r in all_regions)))
    crops_list = list(ARTIFACTS.get("crop_registry", {}).keys())
    return {
        "status": "success",
        "database_backend": db_manager.db_type,
        "count": len(regions),
        "states": unique_states,
        "regions": regions,
        "supported_crops": crops_list,
    }


@app.get("/api/region/{region_name}/dashboard")
def get_cluster_dashboard(region_name: str):
    """Initial dashboard load: fetches farm cluster metadata, live Open-Meteo

    weather, and pre-populated default farmer plots.
    """
    region = db_manager.get_region_by_name(region_name)
    if not region:
        raise HTTPException(
            status_code=404,
            detail=f"Farm Cluster '{region_name}' not found.",
        )

    # Fetch live weather with real latency
    weather = fetch_live_weather_and_soil(
        latitude=float(region["latitude"]),
        longitude=float(region["longitude"]),
        fallback_data=region,
    )

    if weather.get("is_live"):
        try:
            db_manager.update_region_weather(region["id"], weather)
        except Exception:
            pass

    # Retrieve pre-populated cluster plots
    raw_plots = db_manager.get_plots_for_region(region["id"])
    prefill_plots = []
    for p in raw_plots:
        prefill_plots.append({
            "plot_id": p["plot_code"],
            "farmer_name": p["farmer_name"],
            "crop_type": p["crop_type"],
            "growth_stage": p["growth_stage"],
            "area_acres": float(p["area_acres"]),
            "custom_soil_moisture": float(p["soil_moisture_root"]),
        })

    # Default farmer available water for initial planner view (50,000 L)
    default_available_water = 50000.0

    return {
        "status": "success",
        "database_backend": db_manager.db_type,
        "cluster": {
            "id": region["id"],
            "region_name": region["region_name"],
            "association_name": region.get("association_name", "Local Farm Cluster"),
            "state": region["state"],
            "latitude": float(region["latitude"]),
            "longitude": float(region["longitude"]),
            "soil_type": region["soil_type"],
            "default_water_liters": default_available_water,
        },
        "weather": {
            "source": weather.get("source", "Live via Open-Meteo"),
            "is_live": weather.get("is_live", True),
            "today_date": weather.get("today_date"),
            "temp_max": weather["temp_max"],
            "temp_min": weather["temp_min"],
            "humidity": weather["humidity"],
            "wind_speed": weather["wind_speed"],
            "solar_radiation": weather["solar_radiation"],
            "rainfall_10d": weather["rainfall_10d"],
            "et0_10d": weather["et0_10d"],
            "soil_moisture_top": weather["soil_moisture_top"],
            "soil_moisture_root": weather["soil_moisture_root"],
            "soil_moisture_prof": weather["soil_moisture_prof"],
            "client_latency_ms": weather.get("verification", {}).get("client_latency_ms", 120),
        },
        "default_plots": prefill_plots,
        "supported_crops": list(ARTIFACTS.get("crop_registry", {}).keys()),
    }


@app.post("/api/simulate-allocation")
def simulate_farmer_allocation(req: SimulateAllocationRequest):
    """Core Feature: Dynamically simulates crop water stress for the farmer's

    chosen plots and computes optimal prioritized water allocation (in Liters and
    mm depth) against their available supply with clear deficit/surplus feedback.
    """
    region = db_manager.get_region_by_name(req.cluster_name)
    if not region:
        raise HTTPException(
            status_code=404,
            detail=f"Farm Cluster '{req.cluster_name}' not found.",
        )

    # 1. Fetch live Open-Meteo weather for this cluster's exact coordinates
    weather = fetch_live_weather_and_soil(
        latitude=float(region["latitude"]),
        longitude=float(region["longitude"]),
        fallback_data=region,
    )

    evaluated_plots = []
    min_csi_threshold = 0.10

    for idx, p in enumerate(req.plots, start=1):
        # Determine baseline root moisture
        baseline_sm = p.custom_soil_moisture if p.custom_soil_moisture is not None else weather["soil_moisture_root"]
        sm_root_blend = float(np.clip(0.60 * weather["soil_moisture_root"] + 0.40 * baseline_sm, 0.05, 0.95))
        sm_top_blend = float(np.clip(0.60 * weather["soil_moisture_top"] + 0.40 * baseline_sm, 0.05, 0.95))
        sm_prof_blend = float(np.clip(0.60 * weather["soil_moisture_prof"] + 0.40 * (baseline_sm + 0.04), 0.05, 0.95))

        # Model inference
        inf = run_model_inference(
            crop_type=p.crop_type,
            growth_stage=p.growth_stage,
            soil_type=region["soil_type"],
            sm_top=sm_top_blend,
            sm_root=sm_root_blend,
            sm_prof=sm_prof_blend,
            prev_sm_root=sm_root_blend,
            temp_max=weather["temp_max"],
            temp_min=weather["temp_min"],
            humidity=weather["humidity"],
            wind_speed=weather["wind_speed"],
            solar_radiation=weather["solar_radiation"],
            rainfall_10d=weather["rainfall_10d"],
            et0_10d=weather["et0_10d"],
        )

        csi = inf["predicted_csi"]
        p_score = compute_priority_score(csi, p.growth_stage)

        # Agronomic Ideal Water Depth (mm) to relieve physiological stress
        if csi >= min_csi_threshold:
            ideal_depth_mm = max(6.0, round(csi * 32.0 * inf["kc"], 1))
        else:
            ideal_depth_mm = 0.0

        ideal_liters = round(p.area_acres * LITERS_PER_MM_ACRE * ideal_depth_mm, 1)
        demand_weight = (p_score * p.area_acres) if csi >= min_csi_threshold else 0.05

        evaluated_plots.append({
            "plot_id": p.plot_id,
            "crop_type": p.crop_type,
            "crop_category": inf["crop_category"],
            "growth_stage": p.growth_stage,
            "area_acres": round(p.area_acres, 2),
            "blended_soil_moisture": inf["effective_sm_root"],
            "predicted_csi": csi,
            "risk_level": inf["risk_level"],
            "priority_score": p_score,
            "demand_weight": demand_weight,
            "ideal_depth_mm": ideal_depth_mm,
            "ideal_liters": ideal_liters,
            "primary_driver": inf["primary_driver"],
            "all_drivers": inf["all_drivers"],
        })

    # 2. Compute Distribution of Farmer's Available Water
    avail_water = float(req.available_water_liters)
    total_ideal_liters = round(sum(p["ideal_liters"] for p in evaluated_plots), 1)
    total_demand_weight = sum(p["demand_weight"] for p in evaluated_plots)

    for p in evaluated_plots:
        if total_demand_weight > 0 and p["demand_weight"] > 0:
            share = p["demand_weight"] / total_demand_weight
            allocated_liters = round(avail_water * share, 1)
            allocated_depth_mm = round(allocated_liters / (p["area_acres"] * LITERS_PER_MM_ACRE), 1)
            p["water_share_pct"] = round(share * 100.0, 1)
            p["allocated_liters"] = allocated_liters
            p["allocated_depth_mm"] = allocated_depth_mm
        else:
            p["water_share_pct"] = 0.0
            p["allocated_liters"] = 0.0
            p["allocated_depth_mm"] = 0.0
        del p["demand_weight"]

    # Rank plots strictly by Priority Score descending
    evaluated_plots.sort(key=lambda x: (x["priority_score"], x["predicted_csi"]), reverse=True)
    for idx, p in enumerate(evaluated_plots, start=1):
        p["priority_rank"] = idx

    # 3. Water Deficit / Surplus Feedback
    balance_liters = round(avail_water - total_ideal_liters, 1)
    coverage_pct = round((avail_water / total_ideal_liters) * 100.0, 1) if total_ideal_liters > 0 else 100.0

    if balance_liters >= 0:
        water_status = "SURPLUS"
        feedback_message = (
            f"Sufficient Water Reserve: Your available supply of {avail_water:,.0f} L covers 100% of "
            f"crop physiological stress requirements with a surplus of +{balance_liters:,.0f} L."
        )
    else:
        water_status = "DEFICIT"
        deficit = abs(balance_liters)
        feedback_message = (
            f"Water Deficit Warning: Available water covers {coverage_pct}% of stress demand "
            f"({deficit:,.0f} L deficit). Water is prioritized for critical & high-risk plots."
        )

    # Summary metrics
    total_acreage = round(sum(p["area_acres"] for p in evaluated_plots), 1)
    total_plots = len(evaluated_plots)
    farm_avg_csi = round(float(np.mean([p["predicted_csi"] for p in evaluated_plots])), 3) if evaluated_plots else 0.0

    risk_counts = {"Low": 0, "Moderate": 0, "High": 0, "Critical": 0}
    for p in evaluated_plots:
        risk_counts[p["risk_level"]] = risk_counts.get(p["risk_level"], 0) + 1

    return {
        "status": "success",
        "cluster_name": req.cluster_name,
        "state": region["state"],
        "soil_type": region["soil_type"],
        "coordinates": {"latitude": float(region["latitude"]), "longitude": float(region["longitude"])},
        "weather_summary": {
            "source": weather.get("source", "Live via Open-Meteo"),
            "is_live": weather.get("is_live", True),
            "temp_max": weather["temp_max"],
            "temp_min": weather["temp_min"],
            "humidity": weather["humidity"],
            "wind_speed": weather["wind_speed"],
            "rainfall_10d": weather["rainfall_10d"],
            "et0_10d": weather["et0_10d"],
            "soil_moisture_root": weather["soil_moisture_root"],
            "client_latency_ms": weather.get("verification", {}).get("client_latency_ms", 120),
        },
        "water_budget": {
            "available_water_liters": avail_water,
            "total_recommended_liters": total_ideal_liters,
            "water_balance_liters": balance_liters,
            "coverage_pct": coverage_pct,
            "water_status": water_status,
            "feedback_message": feedback_message,
            "water_source_type": req.water_source_type or "Borewell",
        },
        "summary": {
            "total_acreage": total_acreage,
            "total_plots": total_plots,
            "farm_avg_csi": farm_avg_csi,
            "risk_distribution": risk_counts,
        },
        "plots": evaluated_plots,
    }


@app.get("/api/region/{region_name}/future-crops")
def get_future_crops_suitability(region_name: str):
    """Evaluates next-season crop suitability over the 14-day Open-Meteo weather

    forecast and ranks the Top 5 Recommended Crops from the 15 supported crops.
    """
    region = db_manager.get_region_by_name(region_name)
    if not region:
        raise HTTPException(
            status_code=404,
            detail=f"Farm Cluster '{region_name}' not found.",
        )

    weather = fetch_live_weather_and_soil(
        latitude=float(region["latitude"]),
        longitude=float(region["longitude"]),
        fallback_data=region,
    )

    forecast_14d = weather.get("future_14d_forecast", [])
    if forecast_14d:
        avg_future_tmax = float(np.mean([day["temp_max"] for day in forecast_14d]))
        sum_future_rain = float(np.sum([day["rainfall"] for day in forecast_14d]))
        sum_future_et0 = float(np.sum([day["et0"] for day in forecast_14d]))
    else:
        avg_future_tmax = weather["temp_max"]
        sum_future_rain = weather["rainfall_10d"]
        sum_future_et0 = weather["et0_10d"]

    baseline_sm = 0.38 if region["soil_type"] == "Black_Clay" else (0.34 if region["soil_type"] == "Alluvial_Loam" else 0.30)
    net_bal = sum_future_rain - sum_future_et0

    crop_evaluations = []
    crop_registry = ARTIFACTS.get("crop_registry", {})

    for crop_name, traits in crop_registry.items():
        inf = run_model_inference(
            crop_type=crop_name,
            growth_stage="Mid_Season",
            soil_type=region["soil_type"],
            sm_top=baseline_sm,
            sm_root=baseline_sm,
            sm_prof=baseline_sm + 0.04,
            prev_sm_root=baseline_sm,
            temp_max=round(avg_future_tmax, 1),
            temp_min=round(weather["temp_min"], 1),
            humidity=weather["humidity"],
            wind_speed=weather["wind_speed"],
            solar_radiation=weather["solar_radiation"],
            rainfall_10d=round(sum_future_rain * (10.0 / 14.0), 1),
            et0_10d=round(sum_future_et0 * (10.0 / 14.0), 1),
        )

        projected_csi = inf["predicted_csi"]
        suitability_pct = round((1.0 - projected_csi) * 100.0, 1)

        reasons = []
        if traits["temp_max_tol"] >= avg_future_tmax:
            reasons.append(f"High thermal tolerance ({traits['temp_max_tol']}°C > forecast {avg_future_tmax:.1f}°C)")
        else:
            reasons.append(f"Sensitive to projected heat (+{avg_future_tmax - traits['temp_max_tol']:.1f}°C excess)")

        if traits["crit_sm"] <= baseline_sm:
            reasons.append(f"Matches soil water capacity ({region['soil_type']})")
        else:
            reasons.append(f"Requires supplemental irrigation (crit moisture {traits['crit_sm']:.2f})")

        crop_evaluations.append({
            "crop_type": crop_name,
            "crop_category": traits["category"],
            "projected_csi": projected_csi,
            "suitability_score_pct": suitability_pct,
            "risk_level": inf["risk_level"],
            "temp_tolerance": traits["temp_max_tol"],
            "critical_moisture": traits["crit_sm"],
            "reasoning": " • ".join(reasons),
        })

    crop_evaluations.sort(key=lambda x: x["projected_csi"])

    return {
        "status": "success",
        "cluster_name": region_name,
        "soil_type": region["soil_type"],
        "projected_metrics": {
            "avg_future_temp_max": round(avg_future_tmax, 1),
            "sum_future_rainfall_14d": round(sum_future_rain, 1),
            "sum_future_et0_14d": round(sum_future_et0, 1),
            "projected_water_balance": round(net_bal, 1),
        },
        "forecast_14d": forecast_14d,
        "top_future_crops": crop_evaluations[:5],
        "all_ranked_crops": crop_evaluations,
    }
