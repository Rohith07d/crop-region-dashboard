import os
import sqlite3
from typing import Dict, Any, List, Optional
import mysql.connector
from mysql.connector import errorcode

# Load environment variables
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
SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), "crop_regional_db.sqlite")

# Seed data references (8 Localized AP & Telangana Farm Clusters)
from seed_data import REGIONS_DATA, PLOTS_DATA


class DatabaseManager:
    def __init__(self):
        self.use_mysql = False
        self.db_type = "uninitialized"
        self._test_and_init()

    def _get_mysql_connection(self, create_db=False):
        kwargs = {
            "host": DB_HOST,
            "port": DB_PORT,
            "user": DB_USER,
            "password": DB_PASSWORD,
            "connect_timeout": 3,
        }
        if not create_db:
            kwargs["database"] = DB_NAME
        return mysql.connector.connect(**kwargs)

    def _test_and_init(self):
        try:
            conn = self._get_mysql_connection(create_db=True)
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            cursor.execute(f"USE {DB_NAME};")
            cursor.close()
            conn.close()

            self.use_mysql = True
            self.db_type = "MySQL"
            print(f"[DB] Connected to MySQL at {DB_HOST}:{DB_PORT}/{DB_NAME}")
            self._ensure_mysql_schema_and_seed()
        except Exception as exc:
            self.use_mysql = False
            self.db_type = "SQLite"
            self._ensure_sqlite_schema_and_seed()

    def _ensure_mysql_schema_and_seed(self):
        conn = self._get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        if os.path.exists(schema_path):
            with open(schema_path) as f:
                schema_sql = f.read()
            for stmt in schema_sql.split(";"):
                stmt = stmt.strip()
                if stmt:
                    cursor.execute(stmt)
            conn.commit()

        # Check and sync valid farm cluster names
        target_names = [r["region_name"] for r in REGIONS_DATA]
        format_strings = ','.join(['%s'] * len(target_names))
        cursor.execute(f"DELETE FROM regions WHERE region_name NOT IN ({format_strings})", tuple(target_names))
        conn.commit()

        for r in REGIONS_DATA:
            cursor.execute(
                """
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
                    available_water_liters=VALUES(available_water_liters)
                """,
                (
                    r["region_name"], r.get("association_name", "Local Farm Cluster"),
                    r["state"], r["latitude"], r["longitude"], r["soil_type"],
                    r["available_water_liters"], r["temp_max"], r["temp_min"], r["humidity"],
                    r["wind_speed"], r["solar_radiation"], r["rainfall_10d"], r["et0_10d"]
                )
            )
            cursor.execute("SELECT id FROM regions WHERE region_name = %s", (r["region_name"],))
            reg_id = cursor.fetchone()["id"]

            plots = PLOTS_DATA.get(r["region_name"], [])
            for p in plots:
                cursor.execute(
                    """
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
                        prev_soil_moisture_root=VALUES(prev_soil_moisture_root)
                    """,
                    (
                        reg_id, p["plot_code"], p["farmer_name"], p["crop_type"], p["growth_stage"],
                        p["area_acres"], p["sm_top"], p["sm_root"], p["sm_prof"], p["prev_sm"]
                    )
                )
        conn.commit()
        cursor.close()
        conn.close()

    def _ensure_sqlite_schema_and_seed(self):
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS regions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                region_name TEXT NOT NULL UNIQUE,
                association_name TEXT DEFAULT 'Local Farm Cluster',
                state TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                soil_type TEXT NOT NULL,
                available_water_liters REAL NOT NULL,
                temp_max REAL DEFAULT 34.0,
                temp_min REAL DEFAULT 24.0,
                humidity REAL DEFAULT 55.0,
                wind_speed REAL DEFAULT 2.5,
                solar_radiation REAL DEFAULT 18.0,
                rainfall_10d REAL DEFAULT 5.0,
                et0_10d REAL DEFAULT 45.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS region_plots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                region_id INTEGER NOT NULL,
                plot_code TEXT NOT NULL UNIQUE,
                farmer_name TEXT NOT NULL,
                crop_type TEXT NOT NULL,
                growth_stage TEXT NOT NULL,
                area_acres REAL NOT NULL,
                soil_moisture_top REAL NOT NULL,
                soil_moisture_root REAL NOT NULL,
                soil_moisture_prof REAL NOT NULL,
                prev_soil_moisture_root REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (region_id) REFERENCES regions(id) ON DELETE CASCADE
            );
            """
        )
        conn.commit()

        # Remove old deprecated regions not in the 8 target farm clusters
        target_names = [r["region_name"] for r in REGIONS_DATA]
        placeholders = ','.join(['?'] * len(target_names))
        cursor.execute(f"DELETE FROM regions WHERE region_name NOT IN ({placeholders})", tuple(target_names))
        cursor.execute("DELETE FROM region_plots WHERE region_id NOT IN (SELECT id FROM regions);")
        conn.commit()

        # Insert / Sync the 8 localized AP & Telangana farm clusters
        for r in REGIONS_DATA:
            cursor.execute(
                """
                INSERT INTO regions (
                    region_name, association_name, state, latitude, longitude, soil_type, available_water_liters,
                    temp_max, temp_min, humidity, wind_speed, solar_radiation, rainfall_10d, et0_10d
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(region_name) DO UPDATE SET
                    association_name=excluded.association_name,
                    state=excluded.state,
                    latitude=excluded.latitude,
                    longitude=excluded.longitude,
                    soil_type=excluded.soil_type,
                    available_water_liters=excluded.available_water_liters
                """,
                (
                    r["region_name"], r.get("association_name", "Local Farm Cluster"),
                    r["state"], r["latitude"], r["longitude"], r["soil_type"],
                    r["available_water_liters"], r["temp_max"], r["temp_min"], r["humidity"],
                    r["wind_speed"], r["solar_radiation"], r["rainfall_10d"], r["et0_10d"]
                )
            )
            cursor.execute("SELECT id FROM regions WHERE region_name = ?", (r["region_name"],))
            reg_id = cursor.fetchone()[0]

            plots = PLOTS_DATA.get(r["region_name"], [])
            for p in plots:
                cursor.execute(
                    """
                    INSERT INTO region_plots (
                        region_id, plot_code, farmer_name, crop_type, growth_stage,
                        area_acres, soil_moisture_top, soil_moisture_root, soil_moisture_prof, prev_soil_moisture_root
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(plot_code) DO UPDATE SET
                        farmer_name=excluded.farmer_name,
                        crop_type=excluded.crop_type,
                        growth_stage=excluded.growth_stage,
                        area_acres=excluded.area_acres,
                        soil_moisture_top=excluded.soil_moisture_top,
                        soil_moisture_root=excluded.soil_moisture_root,
                        soil_moisture_prof=excluded.soil_moisture_prof,
                        prev_soil_moisture_root=excluded.prev_soil_moisture_root
                    """,
                    (
                        reg_id, p["plot_code"], p["farmer_name"], p["crop_type"], p["growth_stage"],
                        p["area_acres"], p["sm_top"], p["sm_root"], p["sm_prof"], p["prev_sm"]
                    )
                )
        conn.commit()
        cursor.close()
        conn.close()

    def get_all_regions(self, state_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM regions"
        params = []
        if state_filter and state_filter.lower() not in ["all", "all states"]:
            query += " WHERE state = %s" if self.use_mysql else " WHERE state = ?"
            params.append(state_filter)
        query += " ORDER BY state ASC, region_name ASC"

        if self.use_mysql:
            conn = self._get_mysql_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return rows
        else:
            conn = sqlite3.connect(SQLITE_DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            rows = [dict(r) for r in cursor.fetchall()]
            cursor.close()
            conn.close()
            return rows

    def get_region_by_name(self, region_name: str) -> Optional[Dict[str, Any]]:
        if self.use_mysql:
            conn = self._get_mysql_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM regions WHERE region_name = %s LIMIT 1", (region_name,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            return row
        else:
            conn = sqlite3.connect(SQLITE_DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM regions WHERE region_name = ? LIMIT 1", (region_name,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            return dict(row) if row else None

    def get_plots_for_region(self, region_id: int) -> List[Dict[str, Any]]:
        if self.use_mysql:
            conn = self._get_mysql_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM region_plots WHERE region_id = %s ORDER BY id ASC", (region_id,))
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return rows
        else:
            conn = sqlite3.connect(SQLITE_DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM region_plots WHERE region_id = ? ORDER BY id ASC", (region_id,))
            rows = [dict(r) for r in cursor.fetchall()]
            cursor.close()
            conn.close()
            return rows

    def add_plot(self, region_id: int, plot: Dict[str, Any]) -> Dict[str, Any]:
        if self.use_mysql:
            conn = self._get_mysql_connection()
            cursor = conn.cursor(dictionary=True)
            query = """
                INSERT INTO region_plots (
                    region_id, plot_code, farmer_name, crop_type, growth_stage,
                    area_acres, soil_moisture_top, soil_moisture_root, soil_moisture_prof, prev_soil_moisture_root
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                region_id, plot["plot_code"], plot["farmer_name"], plot["crop_type"], plot["growth_stage"],
                float(plot["area_acres"]), float(plot["soil_moisture_top"]), float(plot["soil_moisture_root"]),
                float(plot["soil_moisture_prof"]),
                float(plot["prev_soil_moisture_root"]) if plot.get("prev_soil_moisture_root") is not None else None
            ))
            conn.commit()
            new_id = cursor.lastrowid
            cursor.execute("SELECT * FROM region_plots WHERE id = %s", (new_id,))
            created = cursor.fetchone()
            cursor.close()
            conn.close()
            return created
        else:
            conn = sqlite3.connect(SQLITE_DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            query = """
                INSERT INTO region_plots (
                    region_id, plot_code, farmer_name, crop_type, growth_stage,
                    area_acres, soil_moisture_top, soil_moisture_root, soil_moisture_prof, prev_soil_moisture_root
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (
                region_id, plot["plot_code"], plot["farmer_name"], plot["crop_type"], plot["growth_stage"],
                float(plot["area_acres"]), float(plot["soil_moisture_top"]), float(plot["soil_moisture_root"]),
                float(plot["soil_moisture_prof"]),
                float(plot["prev_soil_moisture_root"]) if plot.get("prev_soil_moisture_root") is not None else None
            ))
            conn.commit()
            new_id = cursor.lastrowid
            cursor.execute("SELECT * FROM region_plots WHERE id = ?", (new_id,))
            row = cursor.fetchone()
            created = dict(row) if row else {"id": new_id, **plot}
            cursor.close()
            conn.close()
            return created

    def update_region_weather(self, region_id: int, weather: Dict[str, Any]):
        fields = ["temp_max", "temp_min", "humidity", "wind_speed", "solar_radiation", "rainfall_10d", "et0_10d"]
        vals = [weather.get(f) for f in fields]
        if self.use_mysql:
            conn = self._get_mysql_connection()
            cursor = conn.cursor()
            set_clause = ", ".join([f"{f} = %s" for f in fields])
            cursor.execute(f"UPDATE regions SET {set_clause} WHERE id = %s", (*vals, region_id))
            conn.commit()
            cursor.close()
            conn.close()
        else:
            conn = sqlite3.connect(SQLITE_DB_PATH)
            cursor = conn.cursor()
            set_clause = ", ".join([f"{f} = ?" for f in fields])
            cursor.execute(f"UPDATE regions SET {set_clause} WHERE id = ?", (*vals, region_id))
            conn.commit()
            cursor.close()
            conn.close()

db_manager = DatabaseManager()
