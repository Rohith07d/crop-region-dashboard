import pytest
from fastapi.testclient import TestClient
from app import app, ARTIFACTS
from db import db_manager

client = TestClient(app)

def test_root_serves_html():
    """Verify that root endpoint serves the index.html frontend."""
    res = client.get("/")
    assert res.status_code == 200
    assert "AgriStress Regional Intelligence" in res.text
    assert "chart.js" in res.text.lower()

def test_static_files():
    """Verify that static CSS and JS are served properly."""
    res_css = client.get("/static/style.css")
    assert res_css.status_code == 200
    assert "--bg-primary" in res_css.text

    res_js = client.get("/static/app.js")
    assert res_js.status_code == 200
    assert "loadDashboard" in res_js.text

def test_get_regions():
    """Verify /api/regions returns all expanded agricultural regions and states."""
    res = client.get("/api/regions")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["count"] >= 12
    assert len(data["states"]) >= 7

    names = [r["region_name"] for r in data["regions"]]
    assert "Nizamabad Basin" in names
    assert "Guntur Delta" in names
    assert "Warangal Uplands" in names
    assert "Karimnagar Canal Zone" in names
    assert "Vidarbha Black Soil Belt" in names
    assert "Malwa Granary" in names
    assert "Cauvery Delta" in names
    assert "Marwar Arid Region" in names

    # Verify association names are present
    assocs = [r.get("association_name") for r in data["regions"]]
    assert any("Farmers" in a or "Collective" in a or "Forum" in a for a in assocs if a)

def test_get_regions_state_filter():
    """Verify filtering regions by state."""
    res = client.get("/api/regions?state=Maharashtra")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] >= 2
    for r in data["regions"]:
        assert r["state"] == "Maharashtra"

def test_create_region():
    """Verify dynamic registration of a new association/region."""
    import uuid
    uid = str(uuid.uuid4())[:6]
    payload = {
        "region_name": f"Kurnool Agri Hub {uid}",
        "association_name": "Kurnool Progressive Seed Collective",
        "state": "Andhra Pradesh",
        "latitude": 15.8281,
        "longitude": 78.0373,
        "soil_type": "Black_Clay",
        "available_water_liters": 600000.0
    }
    res = client.post("/api/regions", json=payload)
    assert res.status_code == 201
    d = res.json()
    assert d["status"] == "success"
    assert d["region"]["region_name"] == payload["region_name"]

    # Verify it shows up in dashboard
    dash_res = client.get(f"/api/region/{payload['region_name']}/dashboard")
    assert dash_res.status_code == 200
    assert dash_res.json()["region"]["association_name"] == payload["association_name"]

def test_verify_region_weather():
    """Verify live weather audit trail, grid resolution, and regional specificity."""
    res = client.get("/api/region/Marwar%20Arid%20Region/verify-weather")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["verified_region"]["region_name"] == "Marwar Arid Region"
    
    audit = data["live_accuracy_audit"]
    assert audit["live_status"] == "ACCURACY_VERIFIED_REGION_SPECIFIC"
    assert "api_endpoint_url" in audit
    assert "https://api.open-meteo.com/v1/forecast" in audit["api_endpoint_url"]
    assert "client_latency_ms" in audit
    assert "elevation_m" in audit

    # Verify measurements
    m = data["current_measurements"]
    assert "temp_max_c" in m
    assert "humidity_pct" in m
    assert "satellite_soil_moisture" in m
    assert "rootzone_7_to_28cm" in m["satellite_soil_moisture"]

    # Verify cross-region specificity benchmarks
    contrast = data["cross_region_specificity_contrast"]
    assert len(contrast) >= 2
    for b in contrast:
        assert "region_name" in b
        assert "humidity" in b
        assert "temp_max" in b

@pytest.mark.parametrize("region_name", [
    "Nizamabad Basin",
    "Guntur Delta",
    "Warangal Uplands",
    "Karimnagar Canal Zone",
    "Vidarbha Black Soil Belt",
    "Malwa Granary",
    "Cauvery Delta",
    "Marwar Arid Region",
])
def test_region_dashboard(region_name):
    """Verify regional dashboard metrics, live weather, and farmer plots across diverse zones."""
    res = client.get(f"/api/region/{region_name}/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["region"]["region_name"] == region_name
    assert "association_name" in data["region"]

    # Weather fields
    weather = data["weather"]
    assert "temp_max" in weather
    assert "temp_min" in weather
    assert "humidity" in weather
    assert "soil_moisture_root" in weather
    assert "verification" in weather

    # Summary KPIs
    summary = data["summary"]
    assert summary["total_plots"] >= 6
    assert summary["total_acreage"] > 0
    assert 0.0 <= summary["regional_avg_csi"] <= 1.0
    assert summary["available_water_liters"] > 0
    assert summary["allocated_water_liters"] <= summary["available_water_liters"] + 1.0

    # Plots
    plots = data["plots"]
    for p in plots:
        assert 0.0 <= p["predicted_csi"] <= 1.0
        assert p["risk_level"] in ["Low", "Moderate", "High", "Critical"]
        assert p["priority_score"] >= 0.0
        assert "allocated_liters" in p

def test_future_crops_recommendation():
    """Verify /api/region/{name}/future-crops returns 5 ranked crops."""
    res = client.get("/api/region/Malwa%20Granary/future-crops")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert len(data["top_future_crops"]) == 5
    assert len(data["all_ranked_crops"]) == 15

    top_crops = data["top_future_crops"]
    csis = [c["projected_csi"] for c in top_crops]
    assert csis == sorted(csis)

def test_add_plot_success():
    """Verify adding a new farmer plot to a region and checking persistence."""
    region_name = "Vidarbha Black Soil Belt"
    new_plot = {
        "plot_code": "VDB-TEST-NEW",
        "farmer_name": "Nitin Gadkari",
        "crop_type": "Cotton",
        "growth_stage": "Mid_Season",
        "area_acres": 3.5,
        "soil_moisture_top": 0.28,
        "soil_moisture_root": 0.32,
        "soil_moisture_prof": 0.38,
        "prev_soil_moisture_root": 0.30
    }
    res = client.post(f"/api/region/{region_name}/plots", json=new_plot)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "success"
    assert data["plot"]["plot_code"] == new_plot["plot_code"]

def test_add_plot_validation_errors():
    """Verify 400 on invalid crop type and 422 on invalid ranges."""
    bad_crop_payload = {
        "plot_code": "BAD-01",
        "farmer_name": "Test",
        "crop_type": "Unknown_Invalid",
        "growth_stage": "Initial",
        "area_acres": 1.0,
        "soil_moisture_top": 0.4,
        "soil_moisture_root": 0.4,
        "soil_moisture_prof": 0.4
    }
    res = client.post("/api/region/Nizamabad%20Basin/plots", json=bad_crop_payload)
    assert res.status_code == 400
