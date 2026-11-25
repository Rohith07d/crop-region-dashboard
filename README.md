# Regional Crop & Water Intelligence Web Application

A regional agricultural monitoring, stress prediction, and water allocation system powered by **FastAPI**, **Scikit-Learn ML Models**, **Open-Meteo Live High-Resolution Satellite & Weather Feed (ECMWF 11km Grid)**, **MySQL / Persistent SQLite Store**, and **Vanilla HTML/CSS/JavaScript with Chart.js**.

---

## 🌟 Key Features

1. **Expanded National Agricultural Database (12 Agro-Climatic Regions & Associations)**
   - Covers 8 major farming states across India with real agricultural associations and collectives:
     - **Telangana**: Nizamabad Basin (*Paddy & Turmeric Assoc*), Warangal Uplands (*Kakatiya Cotton & Chilli Union*), Karimnagar Canal Zone (*Lower Manair Canal Users Assoc*).
     - **Andhra Pradesh**: Guntur Delta (*Guntur Mirchi & Cotton Collective*).
     - **Maharashtra**: Vidarbha Black Soil Belt (*Vidarbha Cotton & Soybean Collective*), Nashik Horticulture Zone (*Nashik District Horticulture & Export Co-op*).
     - **Punjab**: Malwa Granary (*Punjab Progressive Paddy & Maize Growers Forum*).
     - **Karnataka**: Dharwad-Belagavi Agri Belt (*North Karnataka Pulses & Oilseed Federation*), Mysuru-Mandya Canal Belt (*Cauvery Basin Ryot Sangha*).
     - **Gujarat**: Saurashtra Groundnut Hub (*Saurashtra Oilseed & Cash Crop Co-op*).
     - **Tamil Nadu**: Cauvery Delta (*Thanjavur Cauvery Delta Paddy Farmers Forum*).
     - **Rajasthan**: Marwar Arid Region (*Thar Drought-Resilient Crop Producers Alliance*).
   - Allows farmers, agronomists, and cooperatives to filter by **State/Zone** and register new association regions dynamically (`POST /api/regions`).

2. **Live Data Accuracy & Region-Specificity Verification Inspector**
   - Independent verification audit modal and endpoint (`GET /api/region/{region_name}/verify-weather`).
   - Displays exact target GPS coordinates, matched 11km ECMWF grid cell, terrain elevation (m AMSL), and query latency (ms).
   - Direct verification link to the live Open-Meteo REST API JSON payload for full source-of-truth transparency.
   - **Cross-Region Specificity Contrast Matrix**: Compares live measurements (temperature, humidity, precipitation, and 3-layer satellite soil moisture) against contrasting Indian climates simultaneously, proving authentic localized data.

3. **Physiological Crop Stress (FAO-56) & Water Allocation**
   - Blends mesoscale satellite soil moisture (60%) with farmer microplot baseline moisture (40%).
   - Generates 25 agronomic features (Vapor Pressure Deficit, heat excess, moisture margin, net water balance, stage encoding, soil type one-hot).
   - Random Forest Regressor predicts Crop Stress Index ($\text{CSI} \in [0.0, 1.0]$) and Random Forest Classifier assigns physiological risk (`Low`, `Moderate`, `High`, `Critical`).
   - Prioritizes irrigation water using:
     $$\text{Priority Score} = 100 \times (0.70 \times \text{CSI} + 0.30 \times \text{Stage Weight})$$
   - Optimally divides regional water reservoir across farmer plots while respecting conservation of water.

4. **14-Day Climate Forecast & Next-Season Crop Suitability**
   - Extracts 14-day daily projections from Open-Meteo.
   - Evaluates all 15 supported crops in `crop_stress_artifacts.joblib` under projected heat and drought demand.
   - Ranks the Top 5 recommended crops with agronomic rationales.

5. **Zero-Build Vanilla Frontend**
   - Clean, modern, responsive agricultural dark theme.
   - Top Bar: State Filter, Region & Association selector, Live Open-Meteo status pill with latency telemetry, and "Verify Live Data" button.
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
- If your MySQL instance is running and credentials match, it uses MySQL.
- If MySQL credentials are not yet configured, the application **automatically uses the built-in persistent local store (`crop_regional_db.sqlite`)**, ensuring zero downtime or startup failures.

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
| `GET` | `/api/regions` | Returns registered regions with optional `?state=` filter and state list |
| `POST` | `/api/regions` | Registers a new region & farmer association with coordinates and quota |
| `GET` | `/api/region/{region_name}/dashboard` | Real-time weather, blended soil moisture, stress predictions & water allocations |
| `GET` | `/api/region/{region_name}/verify-weather` | Live data audit, elevation, direct API URL, and cross-state specificity contrast |
| `POST` | `/api/region/{region_name}/plots` | Adds a new farmer plot to the region and recalculates allocations |
| `GET` | `/api/region/{region_name}/future-crops` | Evaluates 14-day Open-Meteo weather forecast and ranks Top 5 future crops |

---

## 🧪 Automated Testing
Run the test suite verifying all endpoints, weather integration, and ML boundaries:
```bash
pytest test_app.py -v
```
