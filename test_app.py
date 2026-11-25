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
    """Verify /api/regions returns all 4 agricultural regions."""
    res = client.get("/api/regions")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["count"] == 4
    names = [r["region_name"] for r in data["regions"]]
    assert "Nizamabad Basin" in names
    assert "Guntur Delta" in names
    assert "Warangal Uplands" in names
    assert "Karimnagar Canal Zone" in names

@pytest.mark.parametrize("region_name", [
    "Nizamabad Basin",
    "Guntur Delta",
    "Warangal Uplands",
    "Karimnagar Canal Zone",
])
def test_region_dashboard(region_name):
    """Verify regional dashboard metrics, live weather, and farmer plots."""
    res = client.get(f"/api/region/{region_name}/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["region"]["region_name"] == region_name

    # Check weather fields
    weather = data["weather"]
    assert "temp_max" in weather
    assert "temp_min" in weather
    assert "humidity" in weather
    assert "wind_speed" in weather
    assert "rainfall_10d" in weather
    assert "soil_moisture_root" in weather
    assert weather["is_live"] is True or weather["source"] is not None

    # Check summary KPIs
    summary = data["summary"]
    assert summary["total_plots"] >= 6
    assert summary["total_acreage"] > 0
    assert 0.0 <= summary["regional_avg_csi"] <= 1.0
    assert summary["available_water_liters"] > 0
    assert summary["allocated_water_liters"] > 0
    # Water conservation check (allocated <= available + 1.0 rounding margin)
    assert summary["allocated_water_liters"] <= summary["available_water_liters"] + 1.0

    # Check plots array
    plots = data["plots"]
    assert len(plots) == summary["total_plots"]
    for p in plots:
        assert "plot_code" in p
        assert "farmer_name" in p
        assert "crop_type" in p
        assert 0.0 <= p["predicted_csi"] <= 1.0
        assert p["risk_level"] in ["Low", "Moderate", "High", "Critical"]
        assert p["priority_score"] >= 0.0
        assert p["priority_rank"] >= 1
        assert "allocated_liters" in p

    # Verify strictly descending priority rank sorting
    scores = [p["priority_score"] for p in plots]
    assert scores == sorted(scores, reverse=True)

def test_future_crops_recommendation():
    """Verify /api/region/{name}/future-crops returns 5 ranked crops."""
    res = client.get("/api/region/Nizamabad%20Basin/future-crops")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert len(data["top_future_crops"]) == 5
    assert len(data["all_ranked_crops"]) == 15

    # Check ascending CSI order (lowest stress = best fit)
    top_crops = data["top_future_crops"]
    csis = [c["projected_csi"] for c in top_crops]
    assert csis == sorted(csis)

    # Check 14-day weather forecast array
    forecast = data["forecast_14d"]
    assert len(forecast) >= 10
    for day in forecast:
        assert "date" in day
        assert "temp_max" in day
        assert "rainfall" in day
        assert "et0" in day

def test_add_plot_success():
    """Verify adding a new farmer plot to a region and checking persistence."""
    region_name = "Warangal Uplands"
    new_plot = {
        "plot_code": f"WGL-TEST-NEW",
        "farmer_name": "Naveen Kumar",
        "crop_type": "Chilli_Export",
        "growth_stage": "Mid_Season",
        "area_acres": 2.5,
        "soil_moisture_top": 0.32,
        "soil_moisture_root": 0.35,
        "soil_moisture_prof": 0.40,
        "prev_soil_moisture_root": 0.36
    }
    res = client.post(f"/api/region/{region_name}/plots", json=new_plot)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "success"
    assert data["plot"]["plot_code"] == new_plot["plot_code"]

    # Verify dashboard now reflects the new plot
    dash_res = client.get(f"/api/region/{region_name}/dashboard")
    dash_plots = dash_res.json()["plots"]
    plot_codes = [p["plot_code"] for p in dash_plots]
    assert new_plot["plot_code"] in plot_codes

def test_add_plot_validation_errors():
    """Verify 400 on invalid crop type and 422 on invalid ranges."""
    # Invalid crop
    bad_crop_payload = {
        "plot_code": "BAD-01",
        "farmer_name": "Test",
        "crop_type": "Pineapple_Invalid",
        "growth_stage": "Initial",
        "area_acres": 1.0,
        "soil_moisture_top": 0.4,
        "soil_moisture_root": 0.4,
        "soil_moisture_prof": 0.4
    }
    res = client.post("/api/region/Nizamabad%20Basin/plots", json=bad_crop_payload)
    assert res.status_code == 400

    # Invalid soil moisture (> 1.0)
    bad_sm_payload = {
        "plot_code": "BAD-02",
        "farmer_name": "Test",
        "crop_type": "Rice",
        "growth_stage": "Initial",
        "area_acres": 1.0,
        "soil_moisture_top": 1.5,
        "soil_moisture_root": 0.4,
        "soil_moisture_prof": 0.4
    }
    res2 = client.post("/api/region/Nizamabad%20Basin/plots", json=bad_sm_payload)
    assert res2.status_code == 422
