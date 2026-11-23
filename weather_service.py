import datetime
import requests
from typing import Dict, Any, List

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT = 12  # seconds

def fetch_live_weather_and_soil(
    latitude: float,
    longitude: float,
    fallback_data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Fetches real-time weather and satellite soil moisture from Open-Meteo with

    fallback to cached regional values on network failure.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "past_days": 10,
        "forecast_days": 16,
        "daily": (
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_sum,"
            "et0_fao_evapotranspiration,"
            "shortwave_radiation_sum,"
            "wind_speed_10m_max"
        ),
        "hourly": (
            "relative_humidity_2m,"
            "soil_moisture_0_to_7cm,"
            "soil_moisture_7_to_28cm,"
            "soil_moisture_28_to_100cm"
        ),
        "timezone": "auto",
    }

    try:
        response = requests.get(OPEN_METEO_URL, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        daily = data.get("daily", {})
        hourly = data.get("hourly", {})

        # With past_days=10, index 0..9 are past 10 days, index 10 is TODAY
        today_idx = 10
        daily_times = daily.get("time", [])

        # Past 10-day historical window
        past_precip = [p for p in daily.get("precipitation_sum", [])[:10] if p is not None]
        past_et0 = [e for e in daily.get("et0_fao_evapotranspiration", [])[:10] if e is not None]
        rainfall_10d = round(float(sum(past_precip)), 2)
        et0_10d = round(float(sum(past_et0)), 2)

        # Today's daily metrics
        t_max_list = daily.get("temperature_2m_max", [])
        t_min_list = daily.get("temperature_2m_min", [])
        ws_max_list = daily.get("wind_speed_10m_max", [])
        solar_list = daily.get("shortwave_radiation_sum", [])

        temp_max = float(t_max_list[today_idx]) if len(t_max_list) > today_idx and t_max_list[today_idx] is not None else 34.0
        temp_min = float(t_min_list[today_idx]) if len(t_min_list) > today_idx and t_min_list[today_idx] is not None else 23.0
        wind_speed_kmh = float(ws_max_list[today_idx]) if len(ws_max_list) > today_idx and ws_max_list[today_idx] is not None else 10.0
        wind_speed_ms = round(wind_speed_kmh / 3.6, 2)
        solar_radiation = float(solar_list[today_idx]) if len(solar_list) > today_idx and solar_list[today_idx] is not None else 18.0

        # Hourly metrics for today (24 hours for day 10: slice [240:264])
        start_hour = today_idx * 24
        end_hour = start_hour + 24
        
        rh_hourly = [rh for rh in hourly.get("relative_humidity_2m", [])[start_hour:end_hour] if rh is not None]
        mean_humidity = round(float(sum(rh_hourly) / len(rh_hourly)), 1) if rh_hourly else 55.0

        # Current hour index (estimate current hour of today or midday 12:00)
        now_hour = datetime.datetime.now().hour
        curr_hour_idx = min(start_hour + now_hour, len(hourly.get("soil_moisture_0_to_7cm", [])) - 1)
        prev_24h_idx = max(0, curr_hour_idx - 24)

        sm_top_raw = hourly.get("soil_moisture_0_to_7cm", [])[curr_hour_idx]
        sm_root_raw = hourly.get("soil_moisture_7_to_28cm", [])[curr_hour_idx]
        sm_prof_raw = hourly.get("soil_moisture_28_to_100cm", [])[curr_hour_idx]
        prev_sm_raw = hourly.get("soil_moisture_7_to_28cm", [])[prev_24h_idx]

        soil_moisture_top = round(float(sm_top_raw), 3) if sm_top_raw is not None else 0.35
        soil_moisture_root = round(float(sm_root_raw), 3) if sm_root_raw is not None else 0.38
        soil_moisture_prof = round(float(sm_prof_raw), 3) if sm_prof_raw is not None else 0.42
        prev_soil_moisture_root = round(float(prev_sm_raw), 3) if prev_sm_raw is not None else soil_moisture_root

        # Next 14 days of forecast (indices 11 to 24)
        future_forecast: List[Dict[str, Any]] = []
        for i in range(today_idx + 1, min(today_idx + 15, len(daily_times))):
            date_str = daily_times[i]
            day_tmax = daily.get("temperature_2m_max", [])[i]
            day_rain = daily.get("precipitation_sum", [])[i]
            day_et0 = daily.get("et0_fao_evapotranspiration", [])[i]
            future_forecast.append({
                "date": date_str,
                "temp_max": round(float(day_tmax), 1) if day_tmax is not None else temp_max,
                "rainfall": round(float(day_rain), 1) if day_rain is not None else 0.0,
                "et0": round(float(day_et0), 1) if day_et0 is not None else 4.0
            })

        return {
            "source": "Live via Open-Meteo",
            "is_live": True,
            "today_date": daily_times[today_idx] if len(daily_times) > today_idx else str(datetime.date.today()),
            "temp_max": round(temp_max, 1),
            "temp_min": round(temp_min, 1),
            "humidity": mean_humidity,
            "wind_speed": wind_speed_ms,
            "solar_radiation": round(solar_radiation, 2),
            "rainfall_10d": rainfall_10d,
            "et0_10d": et0_10d,
            "soil_moisture_top": soil_moisture_top,
            "soil_moisture_root": soil_moisture_root,
            "soil_moisture_prof": soil_moisture_prof,
            "prev_soil_moisture_root": prev_soil_moisture_root,
            "future_14d_forecast": future_forecast
        }

    except Exception as exc:
        print(f"[WARN] Open-Meteo call failed ({exc}). Using regional database fallback.")
        fb = fallback_data or {}
        # Generate synthetic 14-day flat projection based on fallback
        today_date = datetime.date.today()
        synthetic_future = []
        for d in range(1, 15):
            f_date = (today_date + datetime.timedelta(days=d)).strftime("%Y-%m-%d")
            synthetic_future.append({
                "date": f_date,
                "temp_max": fb.get("temp_max", 34.0),
                "rainfall": round(fb.get("rainfall_10d", 5.0) / 10.0, 1),
                "et0": round(fb.get("et0_10d", 45.0) / 10.0, 1)
            })

        return {
            "source": "Fallback Cache",
            "is_live": False,
            "today_date": str(today_date),
            "temp_max": float(fb.get("temp_max", 34.0)),
            "temp_min": float(fb.get("temp_min", 24.0)),
            "humidity": float(fb.get("humidity", 55.0)),
            "wind_speed": float(fb.get("wind_speed", 2.5)),
            "solar_radiation": float(fb.get("solar_radiation", 18.0)),
            "rainfall_10d": float(fb.get("rainfall_10d", 5.0)),
            "et0_10d": float(fb.get("et0_10d", 45.0)),
            "soil_moisture_top": float(fb.get("soil_moisture_top", 0.35)),
            "soil_moisture_root": float(fb.get("soil_moisture_root", 0.38)),
            "soil_moisture_prof": float(fb.get("soil_moisture_prof", 0.42)),
            "prev_soil_moisture_root": float(fb.get("prev_soil_moisture_root", 0.38)),
            "future_14d_forecast": synthetic_future
        }
