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
# Expanded Agricultural Seed Data: 12 Distinct Regions Across India
# -----------------------------------------------------------------------------
REGIONS_DATA = [
    # 1. Telangana - Nizamabad Basin
    {
        "region_name": "Nizamabad Basin",
        "association_name": "Nizamabad Basin Paddy & Turmeric Farmers Association",
        "state": "Telangana",
        "latitude": 18.67,
        "longitude": 78.09,
        "soil_type": "Alluvial_Loam",
        "available_water_liters": 650000.0,
        "temp_max": 33.5, "temp_min": 21.0, "humidity": 60.0, "wind_speed": 2.6,
        "solar_radiation": 18.5, "rainfall_10d": 12.0, "et0_10d": 42.0
    },
    # 2. Andhra Pradesh - Guntur Delta
    {
        "region_name": "Guntur Delta",
        "association_name": "Guntur Mirchi & Cotton Growers Collective",
        "state": "Andhra Pradesh",
        "latitude": 16.30,
        "longitude": 80.43,
        "soil_type": "Alluvial_Loam",
        "available_water_liters": 800000.0,
        "temp_max": 34.8, "temp_min": 24.2, "humidity": 68.0, "wind_speed": 3.4,
        "solar_radiation": 19.2, "rainfall_10d": 18.5, "et0_10d": 46.0
    },
    # 3. Telangana - Warangal Uplands
    {
        "region_name": "Warangal Uplands",
        "association_name": "Kakatiya Cotton & Chilli Producers Union",
        "state": "Telangana",
        "latitude": 17.96,
        "longitude": 79.59,
        "soil_type": "Black_Clay",
        "available_water_liters": 500000.0,
        "temp_max": 36.2, "temp_min": 23.0, "humidity": 48.0, "wind_speed": 2.8,
        "solar_radiation": 20.0, "rainfall_10d": 4.0, "et0_10d": 52.0
    },
    # 4. Telangana - Karimnagar Canal Zone
    {
        "region_name": "Karimnagar Canal Zone",
        "association_name": "Lower Manair Canal Water Users Association",
        "state": "Telangana",
        "latitude": 18.43,
        "longitude": 79.12,
        "soil_type": "Red_Sandy",
        "available_water_liters": 550000.0,
        "temp_max": 35.0, "temp_min": 22.5, "humidity": 52.0, "wind_speed": 2.5,
        "solar_radiation": 18.8, "rainfall_10d": 8.0, "et0_10d": 48.0
    },
    # 5. Maharashtra - Vidarbha Black Soil Belt (Nagpur/Wardha)
    {
        "region_name": "Vidarbha Black Soil Belt",
        "association_name": "Vidarbha Cotton & Soybean Farmers Collective",
        "state": "Maharashtra",
        "latitude": 21.14,
        "longitude": 79.08,
        "soil_type": "Black_Clay",
        "available_water_liters": 700000.0,
        "temp_max": 35.5, "temp_min": 21.5, "humidity": 46.0, "wind_speed": 3.0,
        "solar_radiation": 19.5, "rainfall_10d": 2.0, "et0_10d": 50.0
    },
    # 6. Maharashtra - Nashik Horticulture Zone
    {
        "region_name": "Nashik Horticulture Zone",
        "association_name": "Nashik District Horticulture & Export Co-op",
        "state": "Maharashtra",
        "latitude": 19.99,
        "longitude": 73.78,
        "soil_type": "Alluvial_Loam",
        "available_water_liters": 600000.0,
        "temp_max": 31.0, "temp_min": 17.5, "humidity": 58.0, "wind_speed": 2.9,
        "solar_radiation": 18.0, "rainfall_10d": 6.0, "et0_10d": 41.0
    },
    # 7. Punjab - Malwa Granary (Ludhiana)
    {
        "region_name": "Malwa Granary",
        "association_name": "Punjab Progressive Paddy & Maize Growers Forum",
        "state": "Punjab",
        "latitude": 30.90,
        "longitude": 75.85,
        "soil_type": "Alluvial_Loam",
        "available_water_liters": 900000.0,
        "temp_max": 28.5, "temp_min": 15.0, "humidity": 62.0, "wind_speed": 2.4,
        "solar_radiation": 16.5, "rainfall_10d": 14.0, "et0_10d": 36.0
    },
    # 8. Karnataka - Dharwad-Belagavi Agri Belt
    {
        "region_name": "Dharwad-Belagavi Agri Belt",
        "association_name": "North Karnataka Pulses & Oilseed Federation",
        "state": "Karnataka",
        "latitude": 15.45,
        "longitude": 75.00,
        "soil_type": "Black_Clay",
        "available_water_liters": 520000.0,
        "temp_max": 32.5, "temp_min": 19.0, "humidity": 56.0, "wind_speed": 2.7,
        "solar_radiation": 18.2, "rainfall_10d": 5.0, "et0_10d": 44.0
    },
    # 9. Karnataka - Mysuru-Mandya Canal Belt
    {
        "region_name": "Mysuru-Mandya Canal Belt",
        "association_name": "Cauvery Basin Ryot Sangha & Agri Union",
        "state": "Karnataka",
        "latitude": 12.30,
        "longitude": 76.64,
        "soil_type": "Red_Sandy",
        "available_water_liters": 620000.0,
        "temp_max": 30.5, "temp_min": 19.5, "humidity": 65.0, "wind_speed": 2.6,
        "solar_radiation": 17.8, "rainfall_10d": 16.0, "et0_10d": 38.0
    },
    # 10. Gujarat - Saurashtra Groundnut Hub (Rajkot)
    {
        "region_name": "Saurashtra Groundnut Hub",
        "association_name": "Saurashtra Oilseed & Cash Crop Cooperative",
        "state": "Gujarat",
        "latitude": 22.30,
        "longitude": 70.80,
        "soil_type": "Black_Clay",
        "available_water_liters": 480000.0,
        "temp_max": 35.8, "temp_min": 22.0, "humidity": 50.0, "wind_speed": 3.8,
        "solar_radiation": 19.8, "rainfall_10d": 1.0, "et0_10d": 54.0
    },
    # 11. Tamil Nadu - Cauvery Delta (Thanjavur)
    {
        "region_name": "Cauvery Delta",
        "association_name": "Thanjavur Cauvery Delta Paddy Farmers Forum",
        "state": "Tamil Nadu",
        "latitude": 10.78,
        "longitude": 79.13,
        "soil_type": "Alluvial_Loam",
        "available_water_liters": 750000.0,
        "temp_max": 33.0, "temp_min": 24.0, "humidity": 72.0, "wind_speed": 3.2,
        "solar_radiation": 18.4, "rainfall_10d": 22.0, "et0_10d": 42.0
    },
    # 12. Rajasthan - Marwar Arid Region (Jodhpur)
    {
        "region_name": "Marwar Arid Region",
        "association_name": "Thar Drought-Resilient Crop Producers Alliance",
        "state": "Rajasthan",
        "latitude": 26.23,
        "longitude": 73.02,
        "soil_type": "Red_Sandy",
        "available_water_liters": 400000.0,
        "temp_max": 38.0, "temp_min": 21.0, "humidity": 30.0, "wind_speed": 3.5,
        "solar_radiation": 21.0, "rainfall_10d": 0.0, "et0_10d": 58.0
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
    ],
    "Vidarbha Black Soil Belt": [
        {"plot_code": "VDB-P01", "farmer_name": "Gajanan Patil", "crop_type": "Cotton", "growth_stage": "Mid_Season", "area_acres": 4.5, "sm_top": 0.25, "sm_root": 0.29, "sm_prof": 0.38, "prev_sm": 0.33},
        {"plot_code": "VDB-P02", "farmer_name": "Archana Deshmukh", "crop_type": "Soybean", "growth_stage": "Mid_Season", "area_acres": 3.8, "sm_top": 0.27, "sm_root": 0.31, "sm_prof": 0.39, "prev_sm": 0.34},
        {"plot_code": "VDB-P03", "farmer_name": "Baburao Wankhede", "crop_type": "Turmeric", "growth_stage": "Development", "area_acres": 2.2, "sm_top": 0.30, "sm_root": 0.34, "sm_prof": 0.42, "prev_sm": 0.37},
        {"plot_code": "VDB-P04", "farmer_name": "Pravin Thakre", "crop_type": "Okra_Export", "growth_stage": "Initial", "area_acres": 1.8, "sm_top": 0.32, "sm_root": 0.36, "sm_prof": 0.41, "prev_sm": 0.38},
        {"plot_code": "VDB-P05", "farmer_name": "Sunita Kale", "crop_type": "Cotton", "growth_stage": "Late_Season", "area_acres": 3.0, "sm_top": 0.22, "sm_root": 0.26, "sm_prof": 0.35, "prev_sm": 0.30},
        {"plot_code": "VDB-P06", "farmer_name": "Vijay Bhoyar", "crop_type": "Maize", "growth_stage": "Mid_Season", "area_acres": 2.5, "sm_top": 0.28, "sm_root": 0.32, "sm_prof": 0.40, "prev_sm": 0.35},
        {"plot_code": "VDB-P07", "farmer_name": "Kishor Raut", "crop_type": "Pomegranate", "growth_stage": "Development", "area_acres": 2.0, "sm_top": 0.24, "sm_root": 0.28, "sm_prof": 0.36, "prev_sm": 0.31},
    ],
    "Nashik Horticulture Zone": [
        {"plot_code": "NSK-P01", "farmer_name": "Hemant Shinde", "crop_type": "Gherkins", "growth_stage": "Mid_Season", "area_acres": 2.2, "sm_top": 0.38, "sm_root": 0.42, "sm_prof": 0.46, "prev_sm": 0.43},
        {"plot_code": "NSK-P02", "farmer_name": "Deepali Chavan", "crop_type": "Bell_Pepper", "growth_stage": "Mid_Season", "area_acres": 1.9, "sm_top": 0.35, "sm_root": 0.39, "sm_prof": 0.44, "prev_sm": 0.40},
        {"plot_code": "NSK-P03", "farmer_name": "Sanjay Jadhav", "crop_type": "Pomegranate", "growth_stage": "Development", "area_acres": 3.2, "sm_top": 0.32, "sm_root": 0.36, "sm_prof": 0.42, "prev_sm": 0.38},
        {"plot_code": "NSK-P04", "farmer_name": "Rohini More", "crop_type": "Guava_Export", "growth_stage": "Initial", "area_acres": 2.5, "sm_top": 0.40, "sm_root": 0.44, "sm_prof": 0.48, "prev_sm": 0.42},
        {"plot_code": "NSK-P05", "farmer_name": "Nilesh Tambe", "crop_type": "Chilli_Export", "growth_stage": "Mid_Season", "area_acres": 2.0, "sm_top": 0.34, "sm_root": 0.38, "sm_prof": 0.43, "prev_sm": 0.39},
        {"plot_code": "NSK-P06", "farmer_name": "Kavita Gaikwad", "crop_type": "Avocado", "growth_stage": "Development", "area_acres": 1.6, "sm_top": 0.36, "sm_root": 0.40, "sm_prof": 0.45, "prev_sm": 0.41},
        {"plot_code": "NSK-P07", "farmer_name": "Mahesh Nikam", "crop_type": "Soybean", "growth_stage": "Late_Season", "area_acres": 2.8, "sm_top": 0.30, "sm_root": 0.33, "sm_prof": 0.39, "prev_sm": 0.35},
    ],
    "Malwa Granary": [
        {"plot_code": "MLW-P01", "farmer_name": "Harpreet Singh", "crop_type": "Rice", "growth_stage": "Mid_Season", "area_acres": 5.0, "sm_top": 0.45, "sm_root": 0.48, "sm_prof": 0.52, "prev_sm": 0.47},
        {"plot_code": "MLW-P02", "farmer_name": "Gurmeet Kaur", "crop_type": "Maize", "growth_stage": "Development", "area_acres": 3.5, "sm_top": 0.40, "sm_root": 0.43, "sm_prof": 0.47, "prev_sm": 0.42},
        {"plot_code": "MLW-P03", "farmer_name": "Jaswinder Dhillon", "crop_type": "Bell_Pepper", "growth_stage": "Mid_Season", "area_acres": 2.0, "sm_top": 0.38, "sm_root": 0.41, "sm_prof": 0.45, "prev_sm": 0.40},
        {"plot_code": "MLW-P04", "farmer_name": "Balwinder Gill", "crop_type": "Okra_Export", "growth_stage": "Initial", "area_acres": 2.2, "sm_top": 0.42, "sm_root": 0.45, "sm_prof": 0.49, "prev_sm": 0.44},
        {"plot_code": "MLW-P05", "farmer_name": "Kuldeep Sandhu", "crop_type": "Rice", "growth_stage": "Late_Season", "area_acres": 4.2, "sm_top": 0.34, "sm_root": 0.37, "sm_prof": 0.43, "prev_sm": 0.39},
        {"plot_code": "MLW-P06", "farmer_name": "Simranjit Cheema", "crop_type": "Gherkins", "growth_stage": "Development", "area_acres": 1.8, "sm_top": 0.39, "sm_root": 0.42, "sm_prof": 0.46, "prev_sm": 0.41},
        {"plot_code": "MLW-P07", "farmer_name": "Amandeep Brar", "crop_type": "Soybean", "growth_stage": "Mid_Season", "area_acres": 3.0, "sm_top": 0.37, "sm_root": 0.40, "sm_prof": 0.44, "prev_sm": 0.39},
    ],
    "Dharwad-Belagavi Agri Belt": [
        {"plot_code": "DHW-P01", "farmer_name": "Basavaraj Bommai", "crop_type": "Soybean", "growth_stage": "Mid_Season", "area_acres": 3.6, "sm_top": 0.28, "sm_root": 0.32, "sm_prof": 0.40, "prev_sm": 0.35},
        {"plot_code": "DHW-P02", "farmer_name": "Shivaleela Patil", "crop_type": "Cotton", "growth_stage": "Development", "area_acres": 4.0, "sm_top": 0.26, "sm_root": 0.30, "sm_prof": 0.38, "prev_sm": 0.33},
        {"plot_code": "DHW-P03", "farmer_name": "Mallikarjun Hiremath", "crop_type": "Maize", "growth_stage": "Mid_Season", "area_acres": 2.8, "sm_top": 0.31, "sm_root": 0.35, "sm_prof": 0.42, "prev_sm": 0.37},
        {"plot_code": "DHW-P04", "farmer_name": "Kasturi Kulkarni", "crop_type": "Groundnut", "growth_stage": "Initial", "area_acres": 2.4, "sm_top": 0.33, "sm_root": 0.37, "sm_prof": 0.43, "prev_sm": 0.38},
        {"plot_code": "DHW-P05", "farmer_name": "Irappa Nayak", "crop_type": "Chilli_Export", "growth_stage": "Mid_Season", "area_acres": 2.0, "sm_top": 0.25, "sm_root": 0.29, "sm_prof": 0.37, "prev_sm": 0.32},
        {"plot_code": "DHW-P06", "farmer_name": "Renuka Angadi", "crop_type": "Turmeric", "growth_stage": "Late_Season", "area_acres": 2.2, "sm_top": 0.29, "sm_root": 0.33, "sm_prof": 0.39, "prev_sm": 0.35},
        {"plot_code": "DHW-P07", "farmer_name": "Shankar Gouda", "crop_type": "Pomegranate", "growth_stage": "Development", "area_acres": 2.5, "sm_top": 0.27, "sm_root": 0.31, "sm_prof": 0.38, "prev_sm": 0.34},
    ],
    "Mysuru-Mandya Canal Belt": [
        {"plot_code": "MYS-P01", "farmer_name": "Nanjunde Gowda", "crop_type": "Rice", "growth_stage": "Mid_Season", "area_acres": 2.8, "sm_top": 0.38, "sm_root": 0.42, "sm_prof": 0.47, "prev_sm": 0.43},
        {"plot_code": "MYS-P02", "farmer_name": "Sowmya Murthy", "crop_type": "Turmeric", "growth_stage": "Development", "area_acres": 2.1, "sm_top": 0.35, "sm_root": 0.39, "sm_prof": 0.44, "prev_sm": 0.40},
        {"plot_code": "MYS-P03", "farmer_name": "Chetan Kumar", "crop_type": "Avocado", "growth_stage": "Mid_Season", "area_acres": 1.7, "sm_top": 0.33, "sm_root": 0.37, "sm_prof": 0.43, "prev_sm": 0.39},
        {"plot_code": "MYS-P04", "farmer_name": "Manjula Devegowda", "crop_type": "Bell_Pepper", "growth_stage": "Initial", "area_acres": 1.5, "sm_top": 0.40, "sm_root": 0.43, "sm_prof": 0.48, "prev_sm": 0.42},
        {"plot_code": "MYS-P05", "farmer_name": "Prakash Kempegowda", "crop_type": "Maize", "growth_stage": "Late_Season", "area_acres": 2.4, "sm_top": 0.31, "sm_root": 0.34, "sm_prof": 0.41, "prev_sm": 0.36},
        {"plot_code": "MYS-P06", "farmer_name": "Pushpa Latha", "crop_type": "Guava_Export", "growth_stage": "Development", "area_acres": 2.0, "sm_top": 0.36, "sm_root": 0.40, "sm_prof": 0.45, "prev_sm": 0.41},
        {"plot_code": "MYS-P07", "farmer_name": "Siddaraju B.", "crop_type": "Okra_Export", "growth_stage": "Mid_Season", "area_acres": 1.8, "sm_top": 0.34, "sm_root": 0.38, "sm_prof": 0.44, "prev_sm": 0.39},
    ],
    "Saurashtra Groundnut Hub": [
        {"plot_code": "SRT-P01", "farmer_name": "Mansukhbhai Patel", "crop_type": "Groundnut", "growth_stage": "Mid_Season", "area_acres": 4.2, "sm_top": 0.24, "sm_root": 0.28, "sm_prof": 0.36, "prev_sm": 0.32},
        {"plot_code": "SRT-P02", "farmer_name": "Ghanshyambhai Vora", "crop_type": "Cotton", "growth_stage": "Development", "area_acres": 3.8, "sm_top": 0.22, "sm_root": 0.26, "sm_prof": 0.35, "prev_sm": 0.30},
        {"plot_code": "SRT-P03", "farmer_name": "Kailashben Jadeja", "crop_type": "Dragon_Fruit", "growth_stage": "Mid_Season", "area_acres": 1.8, "sm_top": 0.20, "sm_root": 0.24, "sm_prof": 0.33, "prev_sm": 0.27},
        {"plot_code": "SRT-P04", "farmer_name": "Dineshbhai Ahir", "crop_type": "Pomegranate", "growth_stage": "Initial", "area_acres": 2.5, "sm_top": 0.27, "sm_root": 0.31, "sm_prof": 0.38, "prev_sm": 0.33},
        {"plot_code": "SRT-P05", "farmer_name": "Labhubhai Solanki", "crop_type": "Quinoa", "growth_stage": "Mid_Season", "area_acres": 2.0, "sm_top": 0.21, "sm_root": 0.25, "sm_prof": 0.34, "prev_sm": 0.28},
        {"plot_code": "SRT-P06", "farmer_name": "Bhavnaben Chudasama", "crop_type": "Soybean", "growth_stage": "Late_Season", "area_acres": 3.0, "sm_top": 0.25, "sm_root": 0.29, "sm_prof": 0.37, "prev_sm": 0.31},
        {"plot_code": "SRT-P07", "farmer_name": "Ashokbhai Makwana", "crop_type": "Okra_Export", "growth_stage": "Development", "area_acres": 1.6, "sm_top": 0.28, "sm_root": 0.32, "sm_prof": 0.39, "prev_sm": 0.34},
    ],
    "Cauvery Delta": [
        {"plot_code": "CAU-P01", "farmer_name": "Murugesan K.", "crop_type": "Rice", "growth_stage": "Mid_Season", "area_acres": 3.8, "sm_top": 0.44, "sm_root": 0.48, "sm_prof": 0.54, "prev_sm": 0.49},
        {"plot_code": "CAU-P02", "farmer_name": "Selvi Annamalai", "crop_type": "Turmeric", "growth_stage": "Development", "area_acres": 2.4, "sm_top": 0.40, "sm_root": 0.43, "sm_prof": 0.48, "prev_sm": 0.44},
        {"plot_code": "CAU-P03", "farmer_name": "Palanisamy G.", "crop_type": "Maize", "growth_stage": "Mid_Season", "area_acres": 2.5, "sm_top": 0.38, "sm_root": 0.41, "sm_prof": 0.46, "prev_sm": 0.42},
        {"plot_code": "CAU-P04", "farmer_name": "Kavitha Rajendran", "crop_type": "Okra_Export", "growth_stage": "Initial", "area_acres": 1.6, "sm_top": 0.42, "sm_root": 0.45, "sm_prof": 0.49, "prev_sm": 0.44},
        {"plot_code": "CAU-P05", "farmer_name": "Dharmalingam V.", "crop_type": "Rice", "growth_stage": "Late_Season", "area_acres": 4.0, "sm_top": 0.36, "sm_root": 0.39, "sm_prof": 0.45, "prev_sm": 0.41},
        {"plot_code": "CAU-P06", "farmer_name": "Subramanian N.", "crop_type": "Gherkins", "growth_stage": "Development", "area_acres": 1.5, "sm_top": 0.39, "sm_root": 0.42, "sm_prof": 0.47, "prev_sm": 0.43},
        {"plot_code": "CAU-P07", "farmer_name": "Balamurugan S.", "crop_type": "Bell_Pepper", "growth_stage": "Mid_Season", "area_acres": 1.9, "sm_top": 0.37, "sm_root": 0.40, "sm_prof": 0.46, "prev_sm": 0.41},
    ],
    "Marwar Arid Region": [
        {"plot_code": "MWR-P01", "farmer_name": "Hanuman Ram Choudhary", "crop_type": "Quinoa", "growth_stage": "Mid_Season", "area_acres": 3.0, "sm_top": 0.16, "sm_root": 0.19, "sm_prof": 0.28, "prev_sm": 0.22},
        {"plot_code": "MWR-P02", "farmer_name": "Shanti Devi Bishnoi", "crop_type": "Dragon_Fruit", "growth_stage": "Mid_Season", "area_acres": 2.2, "sm_top": 0.18, "sm_root": 0.21, "sm_prof": 0.30, "prev_sm": 0.24},
        {"plot_code": "MWR-P03", "farmer_name": "Malaram Godara", "crop_type": "Pomegranate", "growth_stage": "Development", "area_acres": 2.5, "sm_top": 0.19, "sm_root": 0.23, "sm_prof": 0.32, "prev_sm": 0.25},
        {"plot_code": "MWR-P04", "farmer_name": "Pemaram Siyag", "crop_type": "Groundnut", "growth_stage": "Initial", "area_acres": 2.0, "sm_top": 0.22, "sm_root": 0.25, "sm_prof": 0.33, "prev_sm": 0.27},
        {"plot_code": "MWR-P05", "farmer_name": "Kishnaram Saran", "crop_type": "Guava_Export", "growth_stage": "Development", "area_acres": 1.8, "sm_top": 0.20, "sm_root": 0.24, "sm_prof": 0.31, "prev_sm": 0.26},
        {"plot_code": "MWR-P06", "farmer_name": "Geeta Devi Meghwal", "crop_type": "Okra_Export", "growth_stage": "Mid_Season", "area_acres": 1.4, "sm_top": 0.18, "sm_root": 0.22, "sm_prof": 0.29, "prev_sm": 0.23},
        {"plot_code": "MWR-P07", "farmer_name": "Jagdish Prasad", "crop_type": "Cotton", "growth_stage": "Late_Season", "area_acres": 2.6, "sm_top": 0.17, "sm_root": 0.20, "sm_prof": 0.29, "prev_sm": 0.22},
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

        region_id_map = {}
        for r in REGIONS_DATA:
            query = """
            INSERT INTO regions (
                region_name, association_name, state, latitude, longitude, soil_type, available_water_liters,
                temp_max, temp_min, humidity, wind_speed, solar_radiation, rainfall_10d, et0_10d
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                association_name=VALUES(association_name),
                state=VALUES(state),
                latitude=VALUES(latitude),
                longitude=VALUES(longitude),
                soil_type=VALUES(soil_type),
                available_water_liters=VALUES(available_water_liters);
            """
            cursor.execute(query, (
                r["region_name"], r.get("association_name", "Regional Agricultural Association"),
                r["state"], r["latitude"], r["longitude"], r["soil_type"],
                r["available_water_liters"], r["temp_max"], r["temp_min"], r["humidity"],
                r["wind_speed"], r["solar_radiation"], r["rainfall_10d"], r["et0_10d"]
            ))
            cursor.execute("SELECT id FROM regions WHERE region_name = %s", (r["region_name"],))
            reg_id = cursor.fetchone()[0]
            region_id_map[r["region_name"]] = reg_id

        print(f"Seeded {len(region_id_map)} agricultural regions.")

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
        print(f"Successfully seeded {total_plots_seeded} farmer plots across {len(region_id_map)} regions!")
        cursor.close()
        conn.close()
        return True

    except mysql.connector.Error as err:
        print(f"\n[ERROR] MySQL Database Error: {err}")
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error during seeding: {e}")
        return False

if __name__ == "__main__":
    success = seed_database()
    sys.exit(0 if success else 1)
