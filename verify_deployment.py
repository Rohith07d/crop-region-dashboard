import time
import requests
import sys

BASE_URL = "https://crop-stress-api.onrender.com"
TIMEOUT = 60  # Render cold start allowance

def main():
    print(f"=======================================================================")
    print(f"DEPLOYMENT VERIFICATION & MODEL QUALITY AUDIT")
    print(f"Target: {BASE_URL}")
    print(f"=======================================================================\n")

    results = []

    # -------------------------------------------------------------------------
    # 1. Health Checks
    # -------------------------------------------------------------------------
    # GET /
    t0 = time.perf_counter()
    res_root = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
    lat_root = (time.perf_counter() - t0) * 1000.0
    passed_root = (res_root.status_code == 200)
    results.append(("GET / (Root)", res_root.status_code, f"{lat_root:.1f}ms", "OK" if passed_root else "FAIL", res_root.text[:40]))

    # GET /health
    t0 = time.perf_counter()
    res_health = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
    lat_health = (time.perf_counter() - t0) * 1000.0
    health_data = res_health.json() if res_health.status_code == 200 else {}
    reg_ok = "Random Forest" in health_data.get("regression_model", "")
    cls_ok = "Random Forest" in health_data.get("classification_model", "")
    crops_count = len(health_data.get("supported_crops", []))
    passed_health = (res_health.status_code == 200 and reg_ok and cls_ok and crops_count == 15)
    results.append(("GET /health", res_health.status_code, f"{lat_health:.1f}ms", "OK" if passed_health else "FAIL", f"{crops_count} crops loaded"))

    # -------------------------------------------------------------------------
    # 2. Model Quality & Domain Sanity (POST /predict-stress)
    # -------------------------------------------------------------------------
    # Case A: Severe Drought + Heat Stress
    payload_a = {
        "crop_type": "Rice",
        "soil_type": "Red_Sandy",
        "growth_stage": "Mid_Season",
        "soil_moisture_top": 0.18,
        "soil_moisture_root": 0.18,
        "soil_moisture_prof": 0.18,
        "temp_max": 43.0,
        "temp_min": 28.0,
        "humidity": 25.0,
        "wind_speed": 3.5,
        "solar_radiation": 22.0,
        "rainfall_10d": 0.0,
        "et0_10d": 70.0
    }
    t0 = time.perf_counter()
    res_a = requests.post(f"{BASE_URL}/predict-stress", json=payload_a, timeout=TIMEOUT)
    lat_a = (time.perf_counter() - t0) * 1000.0
    data_a = res_a.json() if res_a.status_code == 200 else {}
    csi_a = data_a.get("predicted_csi", -1)
    risk_a = data_a.get("risk_level", "Unknown")
    passed_a = (res_a.status_code == 200 and csi_a > 0.65 and risk_a in ["High", "Critical"])
    results.append(("Case A (Severe Drought)", res_a.status_code, f"{lat_a:.1f}ms", "OK" if passed_a else "FAIL", f"CSI={csi_a}, Risk={risk_a}"))

    # Case B: Optimal Irrigated Conditions
    payload_b = {
        "crop_type": "Rice",
        "soil_type": "Alluvial_Loam",
        "growth_stage": "Initial",
        "soil_moisture_top": 0.65,
        "soil_moisture_root": 0.65,
        "soil_moisture_prof": 0.65,
        "temp_max": 30.0,
        "temp_min": 22.0,
        "humidity": 70.0,
        "wind_speed": 2.0,
        "solar_radiation": 16.0,
        "rainfall_10d": 45.0,
        "et0_10d": 35.0
    }
    t0 = time.perf_counter()
    res_b = requests.post(f"{BASE_URL}/predict-stress", json=payload_b, timeout=TIMEOUT)
    lat_b = (time.perf_counter() - t0) * 1000.0
    data_b = res_b.json() if res_b.status_code == 200 else {}
    csi_b = data_b.get("predicted_csi", -1)
    risk_b = data_b.get("risk_level", "Unknown")
    passed_b = (res_b.status_code == 200 and csi_b < 0.25 and risk_b == "Low")
    results.append(("Case B (Optimal Wet)", res_b.status_code, f"{lat_b:.1f}ms", "OK" if passed_b else "FAIL", f"CSI={csi_b}, Risk={risk_b}"))

    # Case C: Monotonicity Check (sm: 0.55 -> 0.25)
    base_c = {
        "crop_type": "Rice",
        "soil_type": "Red_Sandy",
        "growth_stage": "Mid_Season",
        "soil_moisture_top": 0.50,
        "soil_moisture_prof": 0.50,
        "temp_max": 36.0,
        "temp_min": 24.0,
        "humidity": 50.0,
        "wind_speed": 2.5,
        "solar_radiation": 18.0,
        "rainfall_10d": 5.0,
        "et0_10d": 50.0
    }
    t0 = time.perf_counter()
    res_c1 = requests.post(f"{BASE_URL}/predict-stress", json=dict(base_c, soil_moisture_root=0.55), timeout=TIMEOUT)
    res_c2 = requests.post(f"{BASE_URL}/predict-stress", json=dict(base_c, soil_moisture_root=0.25), timeout=TIMEOUT)
    lat_c = (time.perf_counter() - t0) * 1000.0
    csi_c1 = res_c1.json().get("predicted_csi", 0)
    csi_c2 = res_c2.json().get("predicted_csi", 0)
    passed_c = (res_c1.status_code == 200 and res_c2.status_code == 200 and csi_c2 > csi_c1)
    results.append(("Case C (Monotonicity)", res_c2.status_code, f"{lat_c:.1f}ms", "OK" if passed_c else "FAIL", f"0.55->{csi_c1} vs 0.25->{csi_c2}"))

    # Case D1: Invalid crop_type
    t0 = time.perf_counter()
    res_d1 = requests.post(f"{BASE_URL}/predict-stress", json=dict(base_c, soil_moisture_root=0.45, crop_type="UnknownCrop"), timeout=TIMEOUT)
    lat_d1 = (time.perf_counter() - t0) * 1000.0
    passed_d1 = (res_d1.status_code == 400)
    results.append(("Case D1 (Unknown Crop)", res_d1.status_code, f"{lat_d1:.1f}ms", "OK" if passed_d1 else "FAIL", "Expected 400"))

    # Case D2: Out of range soil moisture
    t0 = time.perf_counter()
    res_d2 = requests.post(f"{BASE_URL}/predict-stress", json=dict(base_c, soil_moisture_root=1.5), timeout=TIMEOUT)
    lat_d2 = (time.perf_counter() - t0) * 1000.0
    passed_d2 = (res_d2.status_code == 422)
    results.append(("Case D2 (SM Out of Range)", res_d2.status_code, f"{lat_d2:.1f}ms", "OK" if passed_d2 else "FAIL", "Expected 422"))

    # -------------------------------------------------------------------------
    # 3. Allocation & Recommendation Tests
    # -------------------------------------------------------------------------
    # Multi-plot allocation (50,000 L)
    # Using registered crops: Plot_A: Rice (critical), Plot_B: Maize (moderate cereal), Plot_C: Cotton (healthy)
    payload_prio = {
        "total_water_liters": 50000.0,
        "min_csi_threshold": 0.10,
        "plots": [
            {
                "plot_id": "Plot_A",
                "crop_type": "Rice",
                "soil_type": "Red_Sandy",
                "growth_stage": "Mid_Season",
                "area_acres": 2.0,
                "soil_moisture_top": 0.18,
                "soil_moisture_root": 0.18,
                "soil_moisture_prof": 0.18,
                "temp_max": 42.0,
                "temp_min": 28.0,
                "humidity": 25.0,
                "wind_speed": 3.5,
                "solar_radiation": 22.0,
                "rainfall_10d": 0.0,
                "et0_10d": 65.0
            },
            {
                "plot_id": "Plot_B",
                "crop_type": "Maize",
                "soil_type": "Alluvial_Loam",
                "growth_stage": "Development",
                "area_acres": 2.0,
                "soil_moisture_top": 0.45,
                "soil_moisture_root": 0.45,
                "soil_moisture_prof": 0.45,
                "temp_max": 34.0,
                "temp_min": 22.0,
                "humidity": 55.0,
                "wind_speed": 2.0,
                "solar_radiation": 18.0,
                "rainfall_10d": 5.0,
                "et0_10d": 45.0
            },
            {
                "plot_id": "Plot_C",
                "crop_type": "Cotton",
                "soil_type": "Black_Clay",
                "growth_stage": "Late_Season",
                "area_acres": 2.0,
                "soil_moisture_top": 0.65,
                "soil_moisture_root": 0.65,
                "soil_moisture_prof": 0.65,
                "temp_max": 32.0,
                "temp_min": 22.0,
                "humidity": 65.0,
                "wind_speed": 2.0,
                "solar_radiation": 16.0,
                "rainfall_10d": 25.0,
                "et0_10d": 38.0
            }
        ]
    }
    t0 = time.perf_counter()
    res_prio = requests.post(f"{BASE_URL}/prioritize-irrigation", json=payload_prio, timeout=TIMEOUT)
    lat_prio = (time.perf_counter() - t0) * 1000.0
    data_prio = res_prio.json() if res_prio.status_code == 200 else {}
    plan = data_prio.get("allocation_plan", [])
    plot_a = next((p for p in plan if p["plot_id"] == "Plot_A"), {})
    alloc_sum = sum(p.get("allocated_liters", 0.0) for p in plan)
    is_rank_1 = (plot_a.get("priority_rank") == 1)
    is_largest = all(plot_a.get("allocated_liters", 0) >= p.get("allocated_liters", 0) for p in plan)
    is_conserved = abs(alloc_sum - 50000.0) <= 1.0
    passed_prio = (res_prio.status_code == 200 and is_rank_1 and is_largest and is_conserved)
    results.append(("3-Plot Allocation", res_prio.status_code, f"{lat_prio:.1f}ms", "OK" if passed_prio else "FAIL", f"Plot_A Rank 1 ({plot_a.get('allocated_liters')}L), Sum={alloc_sum}L"))

    # Crop Recommendations
    payload_rec = {
        "soil_type": "Red_Sandy",
        "growth_stage": "Mid_Season",
        "soil_moisture_top": 0.20,
        "soil_moisture_root": 0.20,
        "soil_moisture_prof": 0.20,
        "temp_max": 41.0,
        "temp_min": 26.0,
        "humidity": 30.0,
        "wind_speed": 3.5,
        "solar_radiation": 22.0,
        "rainfall_10d": 0.0,
        "et0_10d": 65.0
    }
    t0 = time.perf_counter()
    res_rec = requests.post(f"{BASE_URL}/recommend-crops", json=payload_rec, timeout=TIMEOUT)
    lat_rec = (time.perf_counter() - t0) * 1000.0
    data_rec = res_rec.json() if res_rec.status_code == 200 else {}
    top_5 = data_rec.get("top_recommendations", [])
    csis = [c["predicted_csi"] for c in top_5]
    sorted_asc = (csis == sorted(csis))
    top_names = [c["crop_type"] for c in top_5]
    rice_csi = next((c["predicted_csi"] for c in data_rec.get("all_crops_ranked", []) if c["crop_type"] == "Rice"), 1.0)
    passed_rec = (res_rec.status_code == 200 and len(top_5) == 5 and sorted_asc and top_5[0]["predicted_csi"] < rice_csi)
    results.append(("Recommend Crops", res_rec.status_code, f"{lat_rec:.1f}ms", "OK" if passed_rec else "FAIL", f"Top 1: {top_names[0]} (CSI {top_5[0]['predicted_csi']}) < Rice ({rice_csi})"))

    # -------------------------------------------------------------------------
    # Print Clean Summary Table
    # -------------------------------------------------------------------------
    print(f"\n{'Test Case':<26} | {'HTTP':<5} | {'Latency':<9} | {'Status':<6} | {'Details'}")
    print("-" * 80)
    for name, code, lat, status, detail in results:
        print(f"{name:<26} | {code:<5} | {lat:<9} | {status:<6} | {detail}")

    all_passed = all(r[3] == "OK" for r in results)
    print("\n" + "=" * 80)
    print(f"OVERALL RESULT: {'ALL TESTS PASSED (100% HEALTHY)' if all_passed else 'FAILURES DETECTED'}")
    print("=" * 80)

if __name__ == "__main__":
    main()
