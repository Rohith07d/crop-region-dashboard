# Regional Crop & Water Intelligence Web Application

A regional agricultural monitoring and predictive water allocation system powered by **FastAPI**, **Scikit-Learn ML Models**, **Open-Meteo Live Satellite/Weather API**, **MySQL / Persistent DB**, and **Vanilla HTML/CSS/JavaScript with Chart.js**.

---

## 🌟 Key Features

1. **Live Open-Meteo Satellite & Weather Feed**
   - Automatically queries real-time weather and 3-layer satellite soil moisture:
     - Topsoil layer: 0–7 cm (`soil_moisture_0_to_7cm`)
     - Rootzone layer: 7–28 cm (`soil_moisture_7_to_28cm`)
     - Deep profile layer: 28–100 cm (`soil_moisture_28_to_100cm`)
   - Computes live FAO-56 inputs: $T_{\text{max}}$, $T_{\text{min}}$, mean RH%, wind speed (m/s), solar radiation ($\text{MJ/m}^2$), 10-day historical precipitation sum, and 10-day reference evapotranspiration ($\text{ET}_0$).
   - Built-in fallback cache if Open-Meteo is temporarily unreachable.

2. **Physiological Crop Stress (FAO-56) & Water Allocation**
   - Blends mesoscale satellite soil moisture (60%) with farmer microplot baseline moisture (40%).
   - Generates 25 agronomic features (Vapor Pressure Deficit, heat excess, moisture margin, net water balance, stage encoding, soil type one-hot).
   - Random Forest Regressor predicts Crop Stress Index ($\text{CSI} \in [0.0, 1.0]$) and Random Forest Classifier assigns physiological risk (`Low`, `Moderate`, `High`, `Critical`).
   - Prioritizes irrigation water using:
     $$\text{Priority Score} = 100 \times (0.70 \times \text{CSI} + 0.30 \times \text{Stage Weight})$$
   - Optimally divides regional water reservoir across farmer plots while respecting conservation of water.

3. **14-Day Climate Forecast & Next-Season Crop Suitability**
   - Extracts 14-day daily projections from Open-Meteo.
   - Evaluates all 15 supported crops in `crop_stress_artifacts.joblib` under projected heat and drought demand.
   - Ranks the Top 5 recommended crops with agronomic rationales.

4. **Zero-Build Vanilla Frontend**
   - Clean, modern, responsive agricultural dark theme.
   - Section 1: 4 KPI summary cards, Risk Donut Chart, and Water Allocation vs Area Bar Chart.
   - Section 2: Farmer Plot Ledger with priority ranking, risk badges, and interactive "+ Register New Plot" modal.
   - Section 3: 14-Day Forecast Dual-Axis Chart (Temp, Rain, ET0) and 5 Future Crop Recommendation Cards.

---

## 🚀 Quickstart

### 1. Requirements & Setup
Ensure dependencies are installed:
```bash
cd /Users/rohith/crop-region-dashboard
pip install -r requirements.txt mysql-connector-python pytest
```

### 2. Configure Database (`.env`)
By default, the application connects to MySQL using settings in `.env`:
```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=crop_regional_db
```
- If your MySQL instance is running and credentials match, it uses MySQL!
- If MySQL is not configured or credentials are pending, the application **automatically uses the built-in persistent local store (`crop_regional_db.sqlite`)**, ensuring zero downtime or startup failures.

To explicitly seed your MySQL database:
```bash
python3 seed_data.py
```

### 3. Start the Web Application
```bash
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```
Open your browser at:
👉 **`http://127.0.0.1:8000/`**

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the single-page agricultural dashboard |
| `GET` | `/api/regions` | Returns all 4 registered regions and active DB backend |
| `GET` | `/api/region/{region_name}/dashboard` | Real-time weather, blended soil moisture, stress predictions & water allocations |
| `POST` | `/api/region/{region_name}/plots` | Adds a new farmer plot to the region and recalculates allocations |
| `GET` | `/api/region/{region_name}/future-crops` | Evaluates 14-day Open-Meteo weather forecast and ranks Top 5 future crops |

---

## 🧪 Automated Testing
Run the test suite verifying all endpoints, weather integration, and ML boundaries:
```bash
pytest test_app.py -v
```
