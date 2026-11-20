from contextlib import asynccontextmanager
from typing import Literal, Optional

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ARTIFACTS = {}

RISK_LABELS = {0: "Low", 1: "Moderate", 2: "High", 3: "Critical"}
STAGE_WEIGHTS = {
    "Initial": 0.65,
    "Development": 0.80,
    "Mid_Season": 1.00,
    "Late_Season": 0.35,
}

SoilType = Literal["Black_Clay", "Red_Sandy", "Alluvial_Loam"]
GrowthStage = Literal["Initial", "Development", "Mid_Season", "Late_Season"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        ARTIFACTS.update(joblib.load("crop_stress_artifacts.joblib"))
        print(
            f"Loaded artifacts: {ARTIFACTS['reg_model_name']} & {ARTIFACTS['cls_model_name']}"
        )
    except FileNotFoundError:
        raise RuntimeError(
            "crop_stress_artifacts.joblib not found. Place it in the same folder as main.py."
        )
    yield
    ARTIFACTS.clear()


app = FastAPI(
    title="Crop Water Stress & Irrigation Priority API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------
class WeatherSoilInput(BaseModel):
    soil_moisture_top: float = Field(..., ge=0.0, le=1.0, example=0.45)
    soil_moisture_root: float = Field(..., ge=0.0, le=1.0, example=0.48)
    soil_moisture_prof: float = Field(..., ge=0.0, le=1.0, example=0.52)
    prev_soil_moisture_root: Optional[float] = Field(None, ge=0.0, le=1.0)
    temp_max: float = Field(..., ge=-10.0, le=60.0, example=39.2)
    temp_min: float = Field(..., ge=-10.0, le=50.0, example=26.5)
    humidity: float = Field(..., ge=0.0, le=100.0, example=42.0)
    wind_speed: float = Field(..., ge=0.0, le=50.0, example=3.1)
    solar_radiation: float = Field(..., ge=0.0, le=40.0, example=21.5)
    rainfall_10d: float = Field(..., ge=0.0, example=12.0)
    et0_10d: float = Field(..., ge=0.0, example=58.4)
    soil_type: SoilType = "Red_Sandy"
    growth_stage: GrowthStage = "Mid_Season"


class StressRequest(WeatherSoilInput):
    crop_type: str = Field(..., example="Rice")


class PlotInput(StressRequest):
    plot_id: str = Field(..., example="Plot_A")
    area_acres: float = Field(1.0, gt=0.0, example=1.5)


class PrioritizeRequest(BaseModel):
    total_water_liters: float = Field(..., gt=0.0, example=50000.0)
    min_csi_threshold: float = Field(0.10, ge=0.0, le=1.0)
    plots: list[PlotInput] = Field(..., min_length=1)


# ---------------------------------------------------------------------------
# Inference & Priority Helpers
# ---------------------------------------------------------------------------
def run_inference(data: WeatherSoilInput, crop_type: str) -> dict:
    crop_registry = ARTIFACTS["crop_registry"]
    if crop_type not in crop_registry:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown crop_type '{crop_type}'. Available: {list(crop_registry.keys())}",
        )

    traits = crop_registry[crop_type]
    kc = traits["kc"][data.growth_stage]
    crit_sm = traits["crit_sm"]
    temp_max_tol = traits["temp_max_tol"]
    root_depth = traits["root_depth"]

    prev_sm = (
        data.prev_soil_moisture_root
        if data.prev_soil_moisture_root is not None
        else data.soil_moisture_root
    )

    t_avg = (data.temp_max + data.temp_min) / 2.0
    es = 0.6108 * np.exp((17.27 * t_avg) / (t_avg + 237.3))
    vpd = float(es * (1.0 - (data.humidity / 100.0)))

    moisture_margin = data.soil_moisture_root - crit_sm
    heat_excess = data.temp_max - temp_max_tol

    row = {
        "soil_moisture_top": data.soil_moisture_top,
        "soil_moisture_root": data.soil_moisture_root,
        "soil_moisture_prof": data.soil_moisture_prof,
        "temp_max": data.temp_max,
        "temp_min": data.temp_min,
        "humidity": data.humidity,
        "wind_speed": data.wind_speed,
        "solar_radiation": data.solar_radiation,
        "rainfall_10d": data.rainfall_10d,
        "et0_10d": data.et0_10d,
        "kc": kc,
        "crit_sm": crit_sm,
        "temp_max_tol": temp_max_tol,
        "root_depth": root_depth,
        "vpd": vpd,
        "temp_range": data.temp_max - data.temp_min,
        "net_water_balance": data.rainfall_10d - data.et0_10d,
        "heat_excess": heat_excess,
        "moisture_margin": moisture_margin,
        "prev_soil_moisture_root": prev_sm,
        "soil_moisture_delta": data.soil_moisture_root - prev_sm,
        "growth_stage_encoded": ARTIFACTS["stage_order"][data.growth_stage],
        "soil_type_Alluvial_Loam": 1 if data.soil_type == "Alluvial_Loam" else 0,
        "soil_type_Black_Clay": 1 if data.soil_type == "Black_Clay" else 0,
        "soil_type_Red_Sandy": 1 if data.soil_type == "Red_Sandy" else 0,
    }

    X = pd.DataFrame([row])[ARTIFACTS["feature_cols"]]
    csi = float(np.clip(ARTIFACTS["reg_model"].predict(X)[0], 0.0, 1.0))
    risk_idx = int(ARTIFACTS["cls_model"].predict(X)[0])

    drivers = []
    if moisture_margin < 0:
        drivers.append(f"Root moisture below critical threshold by {abs(moisture_margin):.2f}")
    if heat_excess > 0:
        drivers.append(f"Max temp exceeds crop tolerance by {heat_excess:.1f}°C")
    if vpd > 2.5:
        drivers.append(f"High atmospheric drying demand (VPD {vpd:.2f} kPa)")
    if not drivers:
        drivers.append("Conditions within optimal physiological range")

    return {
        "crop_type": crop_type,
        "crop_category": traits["category"],
        "predicted_csi": round(csi, 4),
        "risk_level": RISK_LABELS[risk_idx],
        "stress_drivers": drivers,
    }


def compute_priority_score(csi: float, growth_stage: str) -> float:
    stage_w = STAGE_WEIGHTS[growth_stage]
    return round(100.0 * (0.70 * csi + 0.30 * stage_w), 2)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "Crop Water Stress & Irrigation Priority API is running."}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "regression_model": ARTIFACTS.get("reg_model_name"),
        "classification_model": ARTIFACTS.get("cls_model_name"),
        "supported_crops": list(ARTIFACTS.get("crop_registry", {}).keys()),
    }


@app.post("/predict-stress")
def predict_stress(req: StressRequest):
    result = run_inference(req, req.crop_type)
    result["priority_score"] = compute_priority_score(
        result["predicted_csi"], req.growth_stage
    )
    return result


@app.post("/prioritize-irrigation")
def prioritize_irrigation(req: PrioritizeRequest):
    evaluated = []
    for plot in req.plots:
        pred = run_inference(plot, plot.crop_type)
        priority_score = compute_priority_score(
            pred["predicted_csi"], plot.growth_stage
        )
        demand_weight = (
            priority_score * plot.area_acres
            if pred["predicted_csi"] >= req.min_csi_threshold
            else 0.0
        )
        evaluated.append(
            {
                "plot_id": plot.plot_id,
                "crop_type": plot.crop_type,
                "growth_stage": plot.growth_stage,
                "area_acres": plot.area_acres,
                "predicted_csi": pred["predicted_csi"],
                "risk_level": pred["risk_level"],
                "priority_score": priority_score,
                "demand_weight": demand_weight,
                "stress_drivers": pred["stress_drivers"],
            }
        )

    total_demand = sum(p["demand_weight"] for p in evaluated)
    for p in evaluated:
        if total_demand > 0 and p["demand_weight"] > 0:
            share = p["demand_weight"] / total_demand
            p["water_share_pct"] = round(share * 100.0, 1)
            p["allocated_liters"] = round(req.total_water_liters * share, 1)
        else:
            p["water_share_pct"] = 0.0
            p["allocated_liters"] = 0.0
        del p["demand_weight"]

    ranked = sorted(evaluated, key=lambda x: x["priority_score"], reverse=True)
    for idx, p in enumerate(ranked, start=1):
        p["priority_rank"] = idx

    return {
        "total_water_liters": req.total_water_liters,
        "plots_evaluated": len(ranked),
        "allocation_plan": ranked,
    }


@app.post("/recommend-crops")
def recommend_crops(req: WeatherSoilInput):
    recommendations = []
    for crop_name in ARTIFACTS["crop_registry"].keys():
        pred = run_inference(req, crop_name)
        recommendations.append(
            {
                "crop_type": crop_name,
                "crop_category": pred["crop_category"],
                "suitability_score_pct": round((1.0 - pred["predicted_csi"]) * 100.0, 1),
                "predicted_csi": pred["predicted_csi"],
                "risk_level": pred["risk_level"],
            }
        )
    recommendations.sort(key=lambda x: x["predicted_csi"])
    return {
        "soil_type": req.soil_type,
        "growth_stage": req.growth_stage,
        "top_recommendations": recommendations[:5],
        "all_crops_ranked": recommendations,
    }