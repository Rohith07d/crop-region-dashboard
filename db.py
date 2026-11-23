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

# Seed data references
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
            # Test connecting to MySQL server
            conn = self._get_mysql_connection(create_db=True)
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            cursor.execute(f"USE {DB_NAME};")
            cursor.close()
            conn.close()

            # Connection succeeded, use MySQL
            self.use_mysql = True
            self.db_type = "MySQL"
            print(f"[DB] Successfully connected to MySQL at {DB_HOST}:{DB_PORT}/{DB_NAME}")
            self._ensure_mysql_schema_and_seed()
        except Exception as exc:
            print(f"[DB] MySQL connection notice: {exc}")
            print(f"[DB] Active fallback enabled: Using local persistent SQLite store ({SQLITE_DB_PATH}).")
            print(f"[DB] (To use MySQL, set DB_PASSWORD in .env and run seed_data.py).")
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

        # Check if regions are populated
        cursor.execute("SELECT COUNT(*) AS cnt FROM regions")
        res = cursor.fetchone()
        if res and res["cnt"] == 0:
            print("[DB] Seeding MySQL with default agricultural regions and plots...")
            for r in REGIONS_DATA:
                cursor.execute(
                    """
                    INSERT INTO regions (
                        region_name, state, latitude, longitude, soil_type, available_water_liters,
                        temp_max, temp_min, humidity, wind_speed, solar_radiation, rainfall_10d, et0_10d
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        r["region_name"], r["state"], r["latitude"], r["longitude"], r["soil_type"],
                        r["available_water_liters"], r["temp_max"], r["temp_min"], r["humidity"],
                        r["wind_speed"], r["solar_radiation"], r["rainfall_10d"], r["et0_10d"]
                    )
                )
                reg_id = cursor.lastrowid
                plots = PLOTS_DATA.get(r["region_name"], [])
                for p in plots:
                    cursor.execute(
                        """
                        INSERT INTO region_plots (
                            region_id, plot_code, farmer_name, crop_type, growth_stage,
                            area_acres, soil_moisture_top, soil_moisture_root, soil_moisture_prof, prev_soil_moisture_root
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            reg_id, p["plot_code"], p["farmer_name"], p["crop_type"], p["growth_stage"],
                            p["area_acres"], p["sm_top"], p["sm_root"], p["sm_prof"], p["prev_sm"]
                        )
                    )
            conn.commit()
            print("[DB] MySQL seeded successfully.")
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

        cursor.execute("SELECT COUNT(*) FROM regions")
        cnt = cursor.fetchone()[0]
        if cnt == 0:
            print("[DB] Seeding SQLite database with default agricultural regions and plots...")
            for r in REGIONS_DATA:
                cursor.execute(
                    """
                    INSERT INTO regions (
                        region_name, state, latitude, longitude, soil_type, available_water_liters,
                        temp_max, temp_min, humidity, wind_speed, solar_radiation, rainfall_10d, et0_10d
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        r["region_name"], r["state"], r["latitude"], r["longitude"], r["soil_type"],
                        r["available_water_liters"], r["temp_max"], r["temp_min"], r["humidity"],
                        r["wind_speed"], r["solar_radiation"], r["rainfall_10d"], r["et0_10d"]
                    )
                )
                reg_id = cursor.lastrowid
                plots = PLOTS_DATA.get(r["region_name"], [])
                for p in plots:
                    cursor.execute(
                        """
                        INSERT INTO region_plots (
                            region_id, plot_code, farmer_name, crop_type, growth_stage,
                            area_acres, soil_moisture_top, soil_moisture_root, soil_moisture_prof, prev_soil_moisture_root
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            reg_id, p["plot_code"], p["farmer_name"], p["crop_type"], p["growth_stage"],
                            p["area_acres"], p["sm_top"], p["sm_root"], p["sm_prof"], p["prev_sm"]
                        )
                    )
            conn.commit()
            print("[DB] SQLite database seeded successfully.")
        cursor.close()
        conn.close()

    def get_all_regions(self) -> List[Dict[str, Any]]:
        if self.use_mysql:
            conn = self._get_mysql_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM regions ORDER BY id ASC")
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return rows
        else:
            conn = sqlite3.connect(SQLITE_DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM regions ORDER BY id ASC")
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
