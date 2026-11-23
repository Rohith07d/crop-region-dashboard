import os
import sys
import mysql.connector
from mysql.connector import errorcode

# Load environment variables from .env if present
def load_env(env_path=".env"):
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))

load_env()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "crop_regional_db")

# -----------------------------------------------------------------------------
# Agricultural Seed Data
# -----------------------------------------------------------------------------
REGIONS_DATA = [
    {
        "region_name": "Nizamabad Basin",
        "state": "Telangana",
        "latitude": 18.67,
        "longitude": 78.09,
        "soil_type": "Alluvial_Loam",
        "available_water_liters": 650000.0,
        "temp_max": 33.5, "temp_min": 21.0, "humidity": 60.0, "wind_speed": 2.6,
        "solar_radiation": 18.5, "rainfall_10d": 12.0, "et0_10d": 42.0
    },
    {
        "region_name": "Guntur Delta",
        "state": "Andhra Pradesh",
        "latitude": 16.30,
        "longitude": 80.43,
        "soil_type": "Alluvial_Loam",
        "available_water_liters": 800000.0,
        "temp_max": 34.8, "temp_min": 24.2, "humidity": 68.0, "wind_speed": 3.4,
        "solar_radiation": 19.2, "rainfall_10d": 18.5, "et0_10d": 46.0
    },
    {
        "region_name": "Warangal Uplands",
        "state": "Telangana",
        "latitude": 17.96,
        "longitude": 79.59,
        "soil_type": "Black_Clay",
        "available_water_liters": 500000.0,
        "temp_max": 36.2, "temp_min": 23.0, "humidity": 48.0, "wind_speed": 2.8,
        "solar_radiation": 20.0, "rainfall_10d": 4.0, "et0_10d": 52.0
    },
    {
        "region_name": "Karimnagar Canal Zone",
        "state": "Telangana",
        "latitude": 18.43,
        "longitude": 79.12,
        "soil_type": "Red_Sandy",
        "available_water_liters": 550000.0,
        "temp_max": 35.0, "temp_min": 22.5, "humidity": 52.0, "wind_speed": 2.5,
        "solar_radiation": 18.8, "rainfall_10d": 8.0, "et0_10d": 48.0
    }
]

PLOTS_DATA = {
    "Nizamabad Basin": [
        {"plot_code": "NZB-P01", "farmer_name": "Ramesh Reddy", "crop_type": "Rice", "growth_stage": "Mid_Season", "area_acres": 2.5, "sm_top": 0.42, "sm_root": 0.45, "sm_prof": 0.50, "prev_sm": 0.44},
        {"plot_code": "NZB-P02", "farmer_name": "Kavitha Rao", "crop_type": "Turmeric", "growth_stage": "Development", "area_acres": 1.8, "sm_top": 0.38, "sm_root": 0.40, "sm_prof": 0.45, "prev_sm": 0.41},
        {"plot_code": "NZB-P03", "farmer_name": "Srinivas Goud", "crop_type": "Soybean", "growth_stage": "Mid_Season", "area_acres": 3.0, "sm_top": 0.35, "sm_root": 0.38, "sm_prof": 0.42, "prev_sm": 0.40},
        {"plot_code": "NZB-P04", "farmer_name": "Anjaiah Naidu", "crop_type": "Maize", "growth_stage": "Initial", "area_acres": 2.0, "sm_top": 0.44, "sm_root": 0.46, "sm_prof": 0.48, "prev_sm": 0.45},
        {"plot_code": "NZB-P05", "farmer_name": "Mallesham V.", "crop_type": "Rice", "growth_stage": "Late_Season", "area_acres": 2.8, "sm_top": 0.30, "sm_root": 0.34, "sm_prof": 0.40, "prev_sm": 0.37},
        {"plot_code": "NZB-P06", "farmer_name": "Padma Bai", "crop_type": "Gherkins", "growth_stage": "Mid_Season", "area_acres": 1.5, "sm_top": 0.36, "sm_root": 0.39, "sm_prof": 0.43, "prev_sm": 0.41},
        {"plot_code": "NZB-P07", "farmer_name": "Chandra Shekar", "crop_type": "Groundnut", "growth_stage": "Development", "area_acres": 2.2, "sm_top": 0.39, "sm_root": 0.41, "sm_prof": 0.45, "prev_sm": 0.40},
    ],
    "Guntur Delta": [
        {"plot_code": "GNT-P01", "farmer_name": "Venkat Raman", "crop_type": "Chilli_Export", "growth_stage": "Mid_Season", "area_acres": 2.4, "sm_top": 0.35, "sm_root": 0.38, "sm_prof": 0.44, "prev_sm": 0.40},
        {"plot_code": "GNT-P02", "farmer_name": "Lakshmi Devi", "crop_type": "Rice", "growth_stage": "Mid_Season", "area_acres": 3.2, "sm_top": 0.48, "sm_root": 0.52, "sm_prof": 0.56, "prev_sm": 0.50},
        {"plot_code": "GNT-P03", "farmer_name": "Subba Rao", "crop_type": "Cotton", "growth_stage": "Development", "area_acres": 4.0, "sm_top": 0.40, "sm_root": 0.42, "sm_prof": 0.48, "prev_sm": 0.43},
        {"plot_code": "GNT-P04", "farmer_name": "Narayana Murthy", "crop_type": "Bell_Pepper", "growth_stage": "Mid_Season", "area_acres": 1.5, "sm_top": 0.33, "sm_root": 0.36, "sm_prof": 0.42, "prev_sm": 0.38},
        {"plot_code": "GNT-P05", "farmer_name": "Bhavani Shankar", "crop_type": "Turmeric", "growth_stage": "Initial", "area_acres": 2.0, "sm_top": 0.45, "sm_root": 0.47, "sm_prof": 0.50, "prev_sm": 0.46},
        {"plot_code": "GNT-P06", "farmer_name": "Koti Reddy", "crop_type": "Okra_Export", "growth_stage": "Mid_Season", "area_acres": 1.7, "sm_top": 0.37, "sm_root": 0.40, "sm_prof": 0.45, "prev_sm": 0.41},
        {"plot_code": "GNT-P07", "farmer_name": "Venkateswarlu P.", "crop_type": "Rice", "growth_stage": "Late_Season", "area_acres": 3.5, "sm_top": 0.42, "sm_root": 0.46, "sm_prof": 0.50, "prev_sm": 0.47},
        {"plot_code": "GNT-P08", "farmer_name": "Sita Mahalakshmi", "crop_type": "Maize", "growth_stage": "Development", "area_acres": 2.1, "sm_top": 0.38, "sm_root": 0.41, "sm_prof": 0.46, "prev_sm": 0.40},
    ],
    "Warangal Uplands": [
        {"plot_code": "WGL-P01", "farmer_name": "Rajeshwar Rao", "crop_type": "Cotton", "growth_stage": "Mid_Season", "area_acres": 3.5, "sm_top": 0.28, "sm_root": 0.32, "sm_prof": 0.40, "prev_sm": 0.36},
        {"plot_code": "WGL-P02", "farmer_name": "Thirupathi Reddy", "crop_type": "Chilli_Export", "growth_stage": "Mid_Season", "area_acres": 2.0, "sm_top": 0.24, "sm_root": 0.28, "sm_prof": 0.36, "prev_sm": 0.32},
        {"plot_code": "WGL-P03", "farmer_name": "Suresh Patel", "crop_type": "Maize", "growth_stage": "Development", "area_acres": 2.5, "sm_top": 0.30, "sm_root": 0.34, "sm_prof": 0.42, "prev_sm": 0.36},
        {"plot_code": "WGL-P04", "farmer_name": "Yadagiri Goud", "crop_type": "Pomegranate", "growth_stage": "Mid_Season", "area_acres": 3.0, "sm_top": 0.26, "sm_root": 0.30, "sm_prof": 0.38, "prev_sm": 0.33},
        {"plot_code": "WGL-P05", "farmer_name": "Swarna Latha", "crop_type": "Dragon_Fruit", "growth_stage": "Initial", "area_acres": 1.5, "sm_top": 0.22, "sm_root": 0.25, "sm_prof": 0.34, "prev_sm": 0.27},
        {"plot_code": "WGL-P06", "farmer_name": "Balaraju M.", "crop_type": "Groundnut", "growth_stage": "Late_Season", "area_acres": 2.2, "sm_top": 0.31, "sm_root": 0.35, "sm_prof": 0.42, "prev_sm": 0.38},
        {"plot_code": "WGL-P07", "farmer_name": "Komuraiah K.", "crop_type": "Soybean", "growth_stage": "Mid_Season", "area_acres": 2.8, "sm_top": 0.27, "sm_root": 0.31, "sm_prof": 0.39, "prev_sm": 0.34},
    ],
    "Karimnagar Canal Zone": [
        {"plot_code": "KRM-P01", "farmer_name": "Devender Rao", "crop_type": "Rice", "growth_stage": "Mid_Season", "area_acres": 2.6, "sm_top": 0.32, "sm_root": 0.35, "sm_prof": 0.41, "prev_sm": 0.38},
        {"plot_code": "KRM-P02", "farmer_name": "Mohan Reddy", "crop_type": "Cotton", "growth_stage": "Mid_Season", "area_acres": 3.0, "sm_top": 0.26, "sm_root": 0.29, "sm_prof": 0.36, "prev_sm": 0.33},
        {"plot_code": "KRM-P03", "farmer_name": "Saraswathi Bai", "crop_type": "Guava_Export", "growth_stage": "Development", "area_acres": 2.0, "sm_top": 0.29, "sm_root": 0.33, "sm_prof": 0.40, "prev_sm": 0.35},
        {"plot_code": "KRM-P04", "farmer_name": "Prabhakar G.", "crop_type": "Maize", "growth_stage": "Initial", "area_acres": 1.8, "sm_top": 0.35, "sm_root": 0.38, "sm_prof": 0.43, "prev_sm": 0.39},
        {"plot_code": "KRM-P05", "farmer_name": "Laxman Rao", "crop_type": "Quinoa", "growth_stage": "Mid_Season", "area_acres": 1.6, "sm_top": 0.24, "sm_root": 0.27, "sm_prof": 0.35, "prev_sm": 0.30},
        {"plot_code": "KRM-P06", "farmer_name": "Rajitha K.", "crop_type": "Okra_Export", "growth_stage": "Mid_Season", "area_acres": 1.4, "sm_top": 0.30, "sm_root": 0.34, "sm_prof": 0.40, "prev_sm": 0.36},
        {"plot_code": "KRM-P07", "farmer_name": "Bhaskar Reddy", "crop_type": "Turmeric", "growth_stage": "Late_Season", "area_acres": 2.2, "sm_top": 0.33, "sm_root": 0.36, "sm_prof": 0.42, "prev_sm": 0.38},
        {"plot_code": "KRM-P08", "farmer_name": "Santhosh V.", "crop_type": "Avocado", "growth_stage": "Development", "area_acres": 1.9, "sm_top": 0.28, "sm_root": 0.31, "sm_prof": 0.38, "prev_sm": 0.33},
    ]
}

def seed_database():
    print(f"Connecting to MySQL server at {DB_HOST}:{DB_PORT} as '{DB_USER}'...")
    try:
        # 1. Connect without selecting database to ensure database creation
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        print(f"Connected successfully to MySQL server.")

        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        print(f"Database '{DB_NAME}' created or verified.")

        cursor.execute(f"USE {DB_NAME};")

        # 2. Execute schema DDL
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        if os.path.exists(schema_path):
            with open(schema_path, "r") as f:
                schema_sql = f.read()
            # Split commands by semicolon
            for statement in schema_sql.split(";"):
                stmt = statement.strip()
                if stmt:
                    cursor.execute(stmt)
            print("Schema tables verified successfully.")

        # 3. Seed Regions
        region_id_map = {}
        for r in REGIONS_DATA:
            query = """
            INSERT INTO regions (
                region_name, state, latitude, longitude, soil_type, available_water_liters,
                temp_max, temp_min, humidity, wind_speed, solar_radiation, rainfall_10d, et0_10d
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                state=VALUES(state),
                latitude=VALUES(latitude),
                longitude=VALUES(longitude),
                soil_type=VALUES(soil_type),
                available_water_liters=VALUES(available_water_liters);
            """
            cursor.execute(query, (
                r["region_name"], r["state"], r["latitude"], r["longitude"], r["soil_type"],
                r["available_water_liters"], r["temp_max"], r["temp_min"], r["humidity"],
                r["wind_speed"], r["solar_radiation"], r["rainfall_10d"], r["et0_10d"]
            ))
            # Retrieve ID
            cursor.execute("SELECT id FROM regions WHERE region_name = %s", (r["region_name"],))
            reg_id = cursor.fetchone()[0]
            region_id_map[r["region_name"]] = reg_id

        print(f"Seeded {len(region_id_map)} agricultural regions.")

        # 4. Seed Plots
        total_plots_seeded = 0
        for reg_name, plots in PLOTS_DATA.items():
            reg_id = region_id_map[reg_name]
            for p in plots:
                plot_query = """
                INSERT INTO region_plots (
                    region_id, plot_code, farmer_name, crop_type, growth_stage,
                    area_acres, soil_moisture_top, soil_moisture_root, soil_moisture_prof, prev_soil_moisture_root
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    farmer_name=VALUES(farmer_name),
                    crop_type=VALUES(crop_type),
                    growth_stage=VALUES(growth_stage),
                    area_acres=VALUES(area_acres),
                    soil_moisture_top=VALUES(soil_moisture_top),
                    soil_moisture_root=VALUES(soil_moisture_root),
                    soil_moisture_prof=VALUES(soil_moisture_prof),
                    prev_soil_moisture_root=VALUES(prev_soil_moisture_root);
                """
                cursor.execute(plot_query, (
                    reg_id, p["plot_code"], p["farmer_name"], p["crop_type"], p["growth_stage"],
                    p["area_acres"], p["sm_top"], p["sm_root"], p["sm_prof"], p["prev_sm"]
                ))
                total_plots_seeded += 1

        conn.commit()
        print(f"Successfully seeded {total_plots_seeded} farmer plots across 4 regions!")
        cursor.close()
        conn.close()
        return True

    except mysql.connector.Error as err:
        print(f"\n[ERROR] MySQL Database Error: {err}")
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Hint: Check DB_USER and DB_PASSWORD in .env")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print(f"Hint: Database '{DB_NAME}' does not exist.")
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error during seeding: {e}")
        return False

if __name__ == "__main__":
    success = seed_database()
    sys.exit(0 if success else 1)
