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
# Localized AP & Telangana Farm Clusters (Village / Ayacut / Canal Commands)
# Coordinates and Soil Types match local agronomic realities
# -----------------------------------------------------------------------------
REGIONS_DATA = [
    # --- TELANGANA FARM CLUSTERS ---
    {
        "region_name": "Shadnagar Ayacut Cluster",
        "association_name": "Shadnagar Red Soil Farmers Ayacut Union",
        "state": "Telangana",
        "latitude": 17.07,
        "longitude": 78.21,
        "soil_type": "Red_Sandy",
        "available_water_liters": 150000.0,
        "temp_max": 33.0, "temp_min": 21.0, "humidity": 55.0, "wind_speed": 2.8,
        "solar_radiation": 18.5, "rainfall_10d": 5.0, "et0_10d": 44.0
    },
    {
        "region_name": "Miryalaguda Canal Command",
        "association_name": "Nagarjuna Sagar Left Canal Farmers Society",
        "state": "Telangana",
        "latitude": 16.87,
        "longitude": 79.56,
        "soil_type": "Black_Clay",
        "available_water_liters": 250000.0,
        "temp_max": 34.5, "temp_min": 22.0, "humidity": 58.0, "wind_speed": 2.6,
        "solar_radiation": 19.0, "rainfall_10d": 8.0, "et0_10d": 46.0
    },
    {
        "region_name": "Bodhan Nizamsagar Block",
        "association_name": "Nizamsagar Distributary Ayacut Committee",
        "state": "Telangana",
        "latitude": 18.66,
        "longitude": 77.88,
        "soil_type": "Black_Clay",
        "available_water_liters": 200000.0,
        "temp_max": 33.8, "temp_min": 21.2, "humidity": 60.0, "wind_speed": 2.5,
        "solar_radiation": 18.2, "rainfall_10d": 10.0, "et0_10d": 43.0
    },
    {
        "region_name": "Siddipet Komaticheruvu Farms",
        "association_name": "Komaticheruvu Tank Irrigation Collective",
        "state": "Telangana",
        "latitude": 18.10,
        "longitude": 78.85,
        "soil_type": "Red_Sandy",
        "available_water_liters": 120000.0,
        "temp_max": 34.0, "temp_min": 21.5, "humidity": 52.0, "wind_speed": 2.7,
        "solar_radiation": 18.6, "rainfall_10d": 4.0, "et0_10d": 45.0
    },

    # --- ANDHRA PRADESH FARM CLUSTERS ---
    {
        "region_name": "Tenali Western Canal Block",
        "association_name": "Krishna Western Delta Water Users Association",
        "state": "Andhra Pradesh",
        "latitude": 16.24,
        "longitude": 80.64,
        "soil_type": "Alluvial_Loam",
        "available_water_liters": 280000.0,
        "temp_max": 34.2, "temp_min": 24.0, "humidity": 68.0, "wind_speed": 3.2,
        "solar_radiation": 19.1, "rainfall_10d": 15.0, "et0_10d": 44.0
    },
    {
        "region_name": "Anantapur Tadipatri Drip Zone",
        "association_name": "Tadipatri Micro-Irrigation Growers Federation",
        "state": "Andhra Pradesh",
        "latitude": 14.91,
        "longitude": 78.01,
        "soil_type": "Red_Sandy",
        "available_water_liters": 100000.0,
        "temp_max": 36.5, "temp_min": 23.0, "humidity": 42.0, "wind_speed": 3.4,
        "solar_radiation": 20.2, "rainfall_10d": 2.0, "et0_10d": 52.0
    },
    {
        "region_name": "Bhimavaram Godavari Delta Block",
        "association_name": "Godavari Western Canal Ayacut Council",
        "state": "Andhra Pradesh",
        "latitude": 16.54,
        "longitude": 81.52,
        "soil_type": "Alluvial_Loam",
        "available_water_liters": 300000.0,
        "temp_max": 33.5, "temp_min": 24.5, "humidity": 72.0, "wind_speed": 3.0,
        "solar_radiation": 18.5, "rainfall_10d": 20.0, "et0_10d": 40.0
    },
    {
        "region_name": "Nandyal KC Canal Ayacut",
        "association_name": "Kurnool-Cuddapah Canal Farmers Union",
        "state": "Andhra Pradesh",
        "latitude": 15.48,
        "longitude": 78.48,
        "soil_type": "Black_Clay",
        "available_water_liters": 180000.0,
        "temp_max": 35.2, "temp_min": 22.8, "humidity": 50.0, "wind_speed": 2.9,
        "solar_radiation": 19.5, "rainfall_10d": 6.0, "et0_10d": 48.0
    }
]

# -----------------------------------------------------------------------------
# Realistic Pre-Populated Farmer Plots (3-4 plots per cluster)
# Strictly uses ONLY the 15 supported crops, valid stages, and realistic baselines
# -----------------------------------------------------------------------------
PLOTS_DATA = {
    "Shadnagar Ayacut Cluster": [
        {"plot_code": "SHD-P01", "farmer_name": "K. Venkataiah", "crop_type": "Cotton", "growth_stage": "Mid_Season", "area_acres": 2.5, "sm_top": 0.32, "sm_root": 0.35, "sm_prof": 0.40, "prev_sm": 0.34},
        {"plot_code": "SHD-P02", "farmer_name": "M. Laxmi Bai", "crop_type": "Maize", "growth_stage": "Development", "area_acres": 1.5, "sm_top": 0.35, "sm_root": 0.38, "sm_prof": 0.42, "prev_sm": 0.37},
        {"plot_code": "SHD-P03", "farmer_name": "P. Srinivas", "crop_type": "Groundnut", "growth_stage": "Mid_Season", "area_acres": 2.0, "sm_top": 0.30, "sm_root": 0.34, "sm_prof": 0.39, "prev_sm": 0.32},
        {"plot_code": "SHD-P04", "farmer_name": "G. Chandrasekhar", "crop_type": "Dragon_Fruit", "growth_stage": "Initial", "area_acres": 1.0, "sm_top": 0.28, "sm_root": 0.31, "sm_prof": 0.36, "prev_sm": 0.29},
    ],
    "Miryalaguda Canal Command": [
        {"plot_code": "MRG-P01", "farmer_name": "V. Ramachandra Reddy", "crop_type": "Rice", "growth_stage": "Mid_Season", "area_acres": 3.0, "sm_top": 0.44, "sm_root": 0.48, "sm_prof": 0.52, "prev_sm": 0.46},
        {"plot_code": "MRG-P02", "farmer_name": "B. Yadagiri", "crop_type": "Cotton", "growth_stage": "Mid_Season", "area_acres": 2.5, "sm_top": 0.36, "sm_root": 0.39, "sm_prof": 0.44, "prev_sm": 0.38},
        {"plot_code": "MRG-P03", "farmer_name": "T. Anjamma", "crop_type": "Soybean", "growth_stage": "Development", "area_acres": 2.0, "sm_top": 0.38, "sm_root": 0.41, "sm_prof": 0.45, "prev_sm": 0.40},
    ],
    "Bodhan Nizamsagar Block": [
        {"plot_code": "BDH-P01", "farmer_name": "S. Rajeshwar", "crop_type": "Turmeric", "growth_stage": "Mid_Season", "area_acres": 2.2, "sm_top": 0.40, "sm_root": 0.43, "sm_prof": 0.47, "prev_sm": 0.42},
        {"plot_code": "BDH-P02", "farmer_name": "K. Govind Rao", "crop_type": "Rice", "growth_stage": "Development", "area_acres": 3.5, "sm_top": 0.46, "sm_root": 0.50, "sm_prof": 0.54, "prev_sm": 0.48},
        {"plot_code": "BDH-P03", "farmer_name": "D. Shankar", "crop_type": "Soybean", "growth_stage": "Late_Season", "area_acres": 2.0, "sm_top": 0.35, "sm_root": 0.38, "sm_prof": 0.42, "prev_sm": 0.37},
    ],
    "Siddipet Komaticheruvu Farms": [
        {"plot_code": "SDP-P01", "farmer_name": "E. Prabhakar", "crop_type": "Maize", "growth_stage": "Mid_Season", "area_acres": 2.0, "sm_top": 0.34, "sm_root": 0.37, "sm_prof": 0.42, "prev_sm": 0.36},
        {"plot_code": "SDP-P02", "farmer_name": "N. Sravanthi", "crop_type": "Chilli_Export", "growth_stage": "Development", "area_acres": 1.5, "sm_top": 0.36, "sm_root": 0.39, "sm_prof": 0.44, "prev_sm": 0.38},
        {"plot_code": "SDP-P03", "farmer_name": "J. Mallesham", "crop_type": "Pomegranate", "growth_stage": "Initial", "area_acres": 2.5, "sm_top": 0.30, "sm_root": 0.33, "sm_prof": 0.38, "prev_sm": 0.32},
    ],
    "Tenali Western Canal Block": [
        {"plot_code": "TNL-P01", "farmer_name": "Ch. Nageswara Rao", "crop_type": "Rice", "growth_stage": "Mid_Season", "area_acres": 3.0, "sm_top": 0.45, "sm_root": 0.49, "sm_prof": 0.53, "prev_sm": 0.47},
        {"plot_code": "TNL-P02", "farmer_name": "G. Subbalakshmi", "crop_type": "Turmeric", "growth_stage": "Development", "area_acres": 1.8, "sm_top": 0.40, "sm_root": 0.43, "sm_prof": 0.48, "prev_sm": 0.41},
        {"plot_code": "TNL-P03", "farmer_name": "K. Sambasiva Rao", "crop_type": "Maize", "growth_stage": "Initial", "area_acres": 2.0, "sm_top": 0.42, "sm_root": 0.45, "sm_prof": 0.49, "prev_sm": 0.43},
    ],
    "Anantapur Tadipatri Drip Zone": [
        {"plot_code": "ATP-P01", "farmer_name": "B. Ramanjaneyulu", "crop_type": "Groundnut", "growth_stage": "Mid_Season", "area_acres": 3.5, "sm_top": 0.22, "sm_root": 0.26, "sm_prof": 0.34, "prev_sm": 0.25},
        {"plot_code": "ATP-P02", "farmer_name": "S. Nagabhushanam", "crop_type": "Dragon_Fruit", "growth_stage": "Development", "area_acres": 2.0, "sm_top": 0.24, "sm_root": 0.28, "sm_prof": 0.35, "prev_sm": 0.26},
        {"plot_code": "ATP-P03", "farmer_name": "K. Venkataramudu", "crop_type": "Pomegranate", "growth_stage": "Mid_Season", "area_acres": 2.5, "sm_top": 0.25, "sm_root": 0.29, "sm_prof": 0.36, "prev_sm": 0.28},
        {"plot_code": "ATP-P04", "farmer_name": "Y. Obulamma", "crop_type": "Quinoa", "growth_stage": "Initial", "area_acres": 1.5, "sm_top": 0.20, "sm_root": 0.24, "sm_prof": 0.32, "prev_sm": 0.22},
    ],
    "Bhimavaram Godavari Delta Block": [
        {"plot_code": "BMV-P01", "farmer_name": "P. Krishnam Raju", "crop_type": "Rice", "growth_stage": "Mid_Season", "area_acres": 4.0, "sm_top": 0.48, "sm_root": 0.52, "sm_prof": 0.56, "prev_sm": 0.50},
        {"plot_code": "BMV-P02", "farmer_name": "M. Kanaka Durga", "crop_type": "Okra_Export", "growth_stage": "Mid_Season", "area_acres": 1.8, "sm_top": 0.42, "sm_root": 0.45, "sm_prof": 0.49, "prev_sm": 0.43},
        {"plot_code": "BMV-P03", "farmer_name": "K. Satyanarayana", "crop_type": "Bell_Pepper", "growth_stage": "Development", "area_acres": 1.5, "sm_top": 0.38, "sm_root": 0.41, "sm_prof": 0.46, "prev_sm": 0.40},
    ],
    "Nandyal KC Canal Ayacut": [
        {"plot_code": "NDL-P01", "farmer_name": "D. Madhava Reddy", "crop_type": "Cotton", "growth_stage": "Mid_Season", "area_acres": 3.0, "sm_top": 0.32, "sm_root": 0.36, "sm_prof": 0.42, "prev_sm": 0.35},
        {"plot_code": "NDL-P02", "farmer_name": "C. Jayaramaiah", "crop_type": "Chilli_Export", "growth_stage": "Mid_Season", "area_acres": 2.2, "sm_top": 0.30, "sm_root": 0.34, "sm_prof": 0.40, "prev_sm": 0.33},
        {"plot_code": "NDL-P03", "farmer_name": "G. Ramasubbamma", "crop_type": "Maize", "growth_stage": "Development", "area_acres": 2.0, "sm_top": 0.35, "sm_root": 0.39, "sm_prof": 0.44, "prev_sm": 0.37},
    ]
}

def seed_database():
    print(f"Connecting to MySQL server at {DB_HOST}:{DB_PORT} as '{DB_USER}'...")
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        print(f"Connected successfully to MySQL server.")

        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        cursor.execute(f"USE {DB_NAME};")

        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        if os.path.exists(schema_path):
            with open(schema_path, "r") as f:
                schema_sql = f.read()
            for statement in schema_sql.split(";"):
                stmt = statement.strip()
                if stmt:
                    cursor.execute(stmt)
            print("Schema tables verified successfully.")

        # Clean existing tables for fresh cluster seeds
        cursor.execute("DELETE FROM region_plots;")
        cursor.execute("DELETE FROM regions;")

        region_id_map = {}
        for r in REGIONS_DATA:
            query = """
            INSERT INTO regions (
                region_name, association_name, state, latitude, longitude, soil_type, available_water_liters,
                temp_max, temp_min, humidity, wind_speed, solar_radiation, rainfall_10d, et0_10d
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            cursor.execute(query, (
                r["region_name"], r.get("association_name", "Local Farm Cluster"),
                r["state"], r["latitude"], r["longitude"], r["soil_type"],
                r["available_water_liters"], r["temp_max"], r["temp_min"], r["humidity"],
                r["wind_speed"], r["solar_radiation"], r["rainfall_10d"], r["et0_10d"]
            ))
            cursor.execute("SELECT id FROM regions WHERE region_name = %s", (r["region_name"],))
            reg_id = cursor.fetchone()[0]
            region_id_map[r["region_name"]] = reg_id

        print(f"Seeded {len(region_id_map)} localized farm clusters.")

        total_plots_seeded = 0
        for reg_name, plots in PLOTS_DATA.items():
            reg_id = region_id_map[reg_name]
            for p in plots:
                plot_query = """
                INSERT INTO region_plots (
                    region_id, plot_code, farmer_name, crop_type, growth_stage,
                    area_acres, soil_moisture_top, soil_moisture_root, soil_moisture_prof, prev_soil_moisture_root
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
                cursor.execute(plot_query, (
                    reg_id, p["plot_code"], p["farmer_name"], p["crop_type"], p["growth_stage"],
                    p["area_acres"], p["sm_top"], p["sm_root"], p["sm_prof"], p["prev_sm"]
                ))
                total_plots_seeded += 1

        conn.commit()
        print(f"Successfully seeded {total_plots_seeded} farmer plots across {len(region_id_map)} farm clusters!")
        cursor.close()
        conn.close()
        return True

    except mysql.connector.Error as err:
        print(f"\n[INFO] MySQL connection note: {err}")
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error during seeding: {e}")
        return False

if __name__ == "__main__":
    success = seed_database()
    sys.exit(0 if success else 1)
