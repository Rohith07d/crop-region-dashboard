import pytest
from fastapi.testclient import TestClient
from app import app, ARTIFACTS
from db import db_manager

client = TestClient(app)

CLUSTERS_ALL = [
    "Shadnagar Ayacut Cluster",
    "Miryalaguda Canal Command",
    "Bodhan Nizamsagar Block",
    "Siddipet Komaticheruvu Farms",
    "Tenali Western Canal Block",
    "Anantapur Tadipatri Drip Zone",
    "Bhimavaram Godavari Delta Block",
    "Nandyal KC Canal Ayacut",
]

def test_root_serves_html():
    """Verify that root endpoint serves the Farmer Water & Crop Allocator HTML."""
    res = client.get("/")
    assert res.status_code == 200
    assert "AgriStress — Farmer Water & Crop Allocator" in res.text
    assert "chart.js" in res.text.lower()
    assert "id=\"clusterSelect\"" in res.text
    assert "id=\"waterSupplyInput\"" in res.text

def test_static_files():
    """Verify that static CSS and JS are served properly with earthy theme variables."""
    res_css = client.get("/static/style.css")
    assert res_css.status_code == 200
    assert "--bg-page: #EAE5D9;" in res_css.text
    assert "--primary-dark: #312C18;" in res_css.text
    assert "--accent-forest: #4C543D;" in res_css.text
    assert "--accent-sage: #A4B092;" in res_css.text

    res_js = client.get("/static/app.js")
    assert res_js.status_code == 200
    assert "simulateAllocation" in res_js.text
    assert "renderAllocationBarChart" in res_js.text

def test_get_regions():
    """Verify /api/regions returns all 8 localized AP & Telangana farm clusters."""
    res = client.get("/api/regions")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["count"] >= 8
    assert sorted(data["states"]) == ["Andhra Pradesh", "Telangana"]

    cluster_names = [r["region_name"] for r in data["regions"]]
    for expected in CLUSTERS_ALL:
        assert expected in cluster_names

    # Check 15 model trained crops
    supported_crops = data["supported_crops"]
    assert len(supported_crops) == 15
    expected_crops = [
        "Rice", "Cotton", "Maize", "Soybean", "Groundnut",
        "Chilli_Export", "Turmeric", "Gherkins", "Dragon_Fruit",
        "Pomegranate", "Avocado", "Quinoa", "Bell_Pepper",
        "Guava_Export", "Okra_Export"
    ]
    for c in expected_crops:
        assert c in supported_crops

def test_get_regions_state_filter():
    """Verify filtering clusters by state (Telangana and Andhra Pradesh)."""
    # Telangana filter
    res_ts = client.get("/api/regions?state=Telangana")
    assert res_ts.status_code == 200
    data_ts = res_ts.json()
    assert data_ts["count"] == 4
    for r in data_ts["regions"]:
        assert r["state"] == "Telangana"

    # Andhra Pradesh filter
    res_ap = client.get("/api/regions?state=Andhra%20Pradesh")
    assert res_ap.status_code == 200
    data_ap = res_ap.json()
    assert data_ap["count"] == 4
    for r in data_ap["regions"]:
        assert r["state"] == "Andhra Pradesh"

@pytest.mark.parametrize("cluster_name", CLUSTERS_ALL)
def test_cluster_dashboard(cluster_name):
    """Verify cluster dashboard metadata, live Open-Meteo weather, and pre-populated plots."""
    res = client.get(f"/api/region/{cluster_name}/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"

    cluster = data["cluster"]
    assert cluster["region_name"] == cluster_name
    assert cluster["state"] in ["Telangana", "Andhra Pradesh"]
    assert cluster["soil_type"] in ["Black_Clay", "Red_Sandy", "Alluvial_Loam"]
    assert cluster["default_water_liters"] == 50000.0

    weather = data["weather"]
    assert "temp_max" in weather
    assert "temp_min" in weather
    assert "humidity" in weather
    assert "soil_moisture_root" in weather
    assert weather["client_latency_ms"] >= 0

    plots = data["default_plots"]
    assert len(plots) >= 3
    valid_crops = list(ARTIFACTS.get("crop_registry", {}).keys())
    for p in plots:
        assert p["crop_type"] in valid_crops
        assert p["growth_stage"] in ["Initial", "Development", "Mid_Season", "Late_Season"]
        assert p["area_acres"] > 0
        assert 0.05 <= p["custom_soil_moisture"] <= 0.95

def test_cluster_dashboard_not_found():
    """Verify 404 for unknown farm cluster."""
    res = client.get("/api/region/NonExistentCluster/dashboard")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()

def test_simulate_allocation_surplus():
    """Verify water allocation simulation under surplus supply."""
    payload = {
        "cluster_name": "Shadnagar Ayacut Cluster",
        "available_water_liters": 250000.0,
        "water_source_type": "Borewell",
        "plots": [
            {
                "plot_id": "Plot_1",
                "crop_type": "Cotton",
                "growth_stage": "Mid_Season",
                "area_acres": 0.8,
                "custom_soil_moisture": 0.40
            },
            {
                "plot_id": "Plot_2",
                "crop_type": "Maize",
                "growth_stage": "Development",
                "area_acres": 0.5,
                "custom_soil_moisture": 0.45
            },
            {
                "plot_id": "Plot_3",
                "crop_type": "Groundnut",
                "growth_stage": "Initial",
                "area_acres": 0.6,
                "custom_soil_moisture": 0.50
            }
        ]
    }
    res = client.post("/api/simulate-allocation", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["cluster_name"] == "Shadnagar Ayacut Cluster"

    wb = data["water_budget"]
    assert wb["water_status"] == "SURPLUS"
    assert wb["available_water_liters"] == 250000.0
    assert wb["water_balance_liters"] >= 0
    assert wb["coverage_pct"] >= 100.0
    assert "Sufficient Water Reserve" in wb["feedback_message"]

    plots = data["plots"]
    assert len(plots) == 3

    # Conservation of water: sum of allocated liters equals available water
    total_allocated = sum(p["allocated_liters"] for p in plots)
    assert total_allocated == pytest.approx(250000.0, abs=1.0)

    # Water share percentages sum to 100%
    total_shares = sum(p["water_share_pct"] for p in plots)
    assert total_shares == pytest.approx(100.0, abs=0.5)

    # Priority rank order (1, 2, 3)
    ranks = [p["priority_rank"] for p in plots]
    assert ranks == [1, 2, 3]

    # Priority score descending
    scores = [p["priority_score"] for p in plots]
    assert scores == sorted(scores, reverse=True)

    # Water depth check
    for p in plots:
        assert p["allocated_depth_mm"] > 0
        assert 0.0 <= p["predicted_csi"] <= 1.0

def test_simulate_allocation_deficit():
    """Verify water allocation simulation under deficit supply (prioritization triggers)."""
    payload = {
        "cluster_name": "Miryalaguda Canal Command",
        "available_water_liters": 15000.0,
        "water_source_type": "Canal Lift",
        "plots": [
            {
                "plot_id": "Plot_Critical_Rice",
                "crop_type": "Rice",
                "growth_stage": "Mid_Season",
                "area_acres": 4.0,
                "custom_soil_moisture": 0.15
            },
            {
                "plot_id": "Plot_Tolerant_DragonFruit",
                "crop_type": "Dragon_Fruit",
                "growth_stage": "Late_Season",
                "area_acres": 2.0,
                "custom_soil_moisture": 0.35
            }
        ]
    }
    res = client.post("/api/simulate-allocation", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"

    wb = data["water_budget"]
    assert wb["water_status"] == "DEFICIT"
    assert wb["water_balance_liters"] < 0
    assert wb["coverage_pct"] < 100.0
    assert "Water Deficit Warning" in wb["feedback_message"]

    plots = data["plots"]
    assert len(plots) == 2
    # Critical Rice in Mid_Season with dry soil must get Rank 1
    assert plots[0]["plot_id"] == "Plot_Critical_Rice"
    assert plots[0]["priority_rank"] == 1
    assert plots[0]["allocated_liters"] > plots[1]["allocated_liters"]

    # Sum of allocated liters equals available water
    total_allocated = sum(p["allocated_liters"] for p in plots)
    assert total_allocated == pytest.approx(15000.0, abs=1.0)

def test_simulate_allocation_validation_errors():
    """Verify 400 on invalid crop and 422 on invalid ranges."""
    # Unknown crop
    bad_crop_req = {
        "cluster_name": "Shadnagar Ayacut Cluster",
        "available_water_liters": 50000.0,
        "plots": [
            {
                "plot_id": "P1",
                "crop_type": "Pineapple_Not_Supported",
                "growth_stage": "Mid_Season",
                "area_acres": 2.0
            }
        ]
    }
    res = client.post("/api/simulate-allocation", json=bad_crop_req)
    assert res.status_code == 400
    assert "Unknown crop_type" in res.json()["detail"]

    # Invalid area (negative or 0)
    bad_area_req = {
        "cluster_name": "Shadnagar Ayacut Cluster",
        "available_water_liters": 50000.0,
        "plots": [
            {
                "plot_id": "P1",
                "crop_type": "Cotton",
                "growth_stage": "Mid_Season",
                "area_acres": -1.0
            }
        ]
    }
    res = client.post("/api/simulate-allocation", json=bad_area_req)
    assert res.status_code == 422

    # Cluster not found
    bad_cluster_req = {
        "cluster_name": "Unknown_Cluster_XYZ",
        "available_water_liters": 50000.0,
        "plots": [
            {
                "plot_id": "P1",
                "crop_type": "Cotton",
                "growth_stage": "Mid_Season",
                "area_acres": 2.0
            }
        ]
    }
    res = client.post("/api/simulate-allocation", json=bad_cluster_req)
    assert res.status_code == 404

def test_future_crops_recommendation():
    """Verify /api/region/{name}/future-crops returns Top 5 crops and 15 ranked crops."""
    res = client.get("/api/region/Anantapur%20Tadipatri%20Drip%20Zone/future-crops")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["cluster_name"] == "Anantapur Tadipatri Drip Zone"
    assert len(data["top_future_crops"]) == 5
    assert len(data["all_ranked_crops"]) == 15

    top_crops = data["top_future_crops"]
    csis = [c["projected_csi"] for c in top_crops]
    assert csis == sorted(csis)
    for c in top_crops:
        assert 0.0 <= c["projected_csi"] <= 1.0
        assert 0.0 <= c["suitability_score_pct"] <= 100.0
        assert c["crop_type"] in ARTIFACTS["crop_registry"]
