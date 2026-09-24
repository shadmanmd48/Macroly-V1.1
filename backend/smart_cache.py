import os
import json
import logging
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("macroly.database")

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
DEFAULT_SQLITE_PATH = os.path.join(os.path.dirname(__file__), "macroly.db")
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", DEFAULT_SQLITE_PATH).strip()

def is_postgres() -> bool:
    return DATABASE_URL.startswith("postgresql://") or DATABASE_URL.startswith("postgres://")

def get_database_info() -> Dict[str, Any]:
    if is_postgres():
        target = DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else "PostgreSQL"
        return {"engine": "PostgreSQL", "target": target, "is_postgres": True}
    elif DATABASE_URL.startswith("sqlite:///"):
        return {"engine": "SQLite", "target": DATABASE_URL.replace("sqlite:///", ""), "is_postgres": False}
    else:
        return {"engine": "SQLite (Fallback)", "target": SQLITE_DB_PATH, "is_postgres": False}

SEEDED_FOODS = [
    # Item Name, Serving Unit, Default Qty, Calories, Protein, Carbs, Fats, Tags
    ("whole wheat roti", "roti", 1.0, 110, 3.0, 22.0, 1.0, "indian,bread,staple"),
    ("roti", "roti", 1.0, 110, 3.0, 22.0, 1.0, "indian,bread"),
    ("chapati", "chapati", 1.0, 110, 3.0, 22.0, 1.0, "indian,bread"),
    ("chicken curry bowl", "bowl", 1.0, 280, 32.0, 8.0, 12.0, "curry,poultry,dinner"),
    ("chicken curry", "bowl", 1.0, 280, 32.0, 8.0, 12.0, "curry,poultry"),
    ("cucumber salad", "bowl", 1.0, 40, 1.0, 6.0, 0.5, "salad,greens,veggie"),
    ("dal makhani", "bowl", 1.0, 260, 9.0, 28.0, 12.0, "dal,lentils,indian"),
    ("dal", "bowl", 1.0, 180, 8.0, 24.0, 4.0, "dal,lentils"),
    ("yellow dal tadka", "bowl", 1.0, 180, 8.0, 24.0, 4.0, "dal,indian"),
    ("egg", "egg", 1.0, 72, 6.3, 0.4, 4.8, "breakfast,protein"),
    ("boiled egg", "egg", 1.0, 72, 6.3, 0.4, 4.8, "breakfast,protein"),
    ("fried egg", "egg", 1.0, 90, 6.3, 0.4, 7.0, "breakfast,protein"),
    ("slice of toast", "slice", 1.0, 80, 2.5, 15.0, 1.0, "bread,breakfast"),
    ("toast", "slice", 1.0, 80, 2.5, 15.0, 1.0, "bread,breakfast"),
    ("sourdough toast", "slice", 1.0, 100, 3.5, 19.0, 1.0, "bread,artisan"),
    ("avocado sourdough & poached eggs", "plate", 1.0, 420, 22.0, 34.0, 18.0, "breakfast,avocado"),
    ("avocado sourdough", "plate", 1.0, 420, 22.0, 34.0, 18.0, "breakfast"),
    ("mediterranean quinoa bowl", "bowl", 1.0, 580, 46.0, 48.0, 16.0, "lunch,quinoa,salad"),
    ("greek yogurt & berry crunch", "parfait", 1.0, 240, 24.0, 18.0, 4.0, "snack,yogurt,berries"),
    ("greek yogurt", "cup", 1.0, 130, 17.0, 6.0, 4.0, "dairy,snack"),
    ("morning coffee", "cup", 1.0, 15, 0.5, 1.0, 0.5, "beverage,coffee"),
    ("black coffee", "cup", 1.0, 5, 0.3, 0.0, 0.0, "beverage,coffee"),
    ("iced latte with oat milk", "glass", 1.0, 140, 3.0, 20.0, 4.5, "coffee,beverage"),
    ("latte", "cup", 1.0, 120, 6.0, 10.0, 5.0, "coffee,beverage"),
    ("peanut butter", "tbsp", 1.0, 95, 4.0, 3.0, 8.0, "spread,fat"),
    ("white rice", "bowl", 1.0, 205, 4.2, 45.0, 0.4, "grain,staple"),
    ("brown rice", "bowl", 1.0, 215, 5.0, 45.0, 1.8, "grain,fiber"),
    ("paneer tikka", "plate", 1.0, 270, 18.0, 8.0, 18.0, "indian,appetizer"),
    ("palak paneer", "bowl", 1.0, 240, 12.0, 7.0, 17.0, "curry,indian"),
    ("protein shake", "shake", 1.0, 140, 25.0, 3.0, 2.0, "supplement,protein"),
    ("apple", "apple", 1.0, 95, 0.5, 25.0, 0.3, "fruit,snack"),
    ("banana", "banana", 1.0, 105, 1.3, 27.0, 0.4, "fruit,snack"),
    ("oatmeal bowl", "bowl", 1.0, 220, 7.0, 38.0, 4.0, "breakfast,oats"),
    ("grilled chicken breast", "breast", 1.0, 220, 43.0, 0.0, 5.0, "poultry,lean"),
    ("salmon fillet", "fillet", 1.0, 280, 34.0, 0.0, 15.0, "fish,healthy-fats"),
    ("almonds", "handful", 1.0, 160, 6.0, 6.0, 14.0, "nuts,snack"),
]

def normalize_key(name: str) -> str:
    cleaned = name.lower().strip()
    for char in [",", ".", "!", "?", "(", ")", "/", "-"]:
        cleaned = cleaned.replace(char, " ")
    return " ".join(cleaned.split())

class SmartCache:
    def __init__(self):
        self.use_postgres = is_postgres()
        self.init_db()

    def get_connection(self):
        if self.use_postgres:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        else:
            import sqlite3
            db_path = DATABASE_URL.replace("sqlite:///", "") if DATABASE_URL.startswith("sqlite:///") else SQLITE_DB_PATH
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            return conn

    def init_db(self):
        if self.use_postgres:
            try:
                import psycopg2
                conn = psycopg2.connect(DATABASE_URL)
                cursor = conn.cursor()
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS food_cache (
                    id SERIAL PRIMARY KEY,
                    food_key VARCHAR(255) UNIQUE,
                    name VARCHAR(255),
                    serving_unit VARCHAR(50),
                    serving_qty REAL,
                    calories REAL,
                    protein REAL,
                    carbs REAL,
                    fats REAL,
                    tags VARCHAR(255),
                    hit_count INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)
                cursor.execute("SELECT COUNT(*) FROM food_cache")
                count = cursor.fetchone()[0]
                if count == 0:
                    for name, unit, qty, cal, p, c, f, tags in SEEDED_FOODS:
                        key = normalize_key(name)
                        cursor.execute("""
                        INSERT INTO food_cache (food_key, name, serving_unit, serving_qty, calories, protein, carbs, fats, tags)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (food_key) DO NOTHING
                        """, (key, name.title(), unit, qty, cal, p, c, f, tags))
                conn.commit()
                conn.close()
                masked = DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else "PostgreSQL Target"
                logger.info("Connected to PostgreSQL successfully at %s (food_cache ready)", masked)
            except Exception as e:
                logger.error("Failed to connect to PostgreSQL via DATABASE_URL: %s. Falling back to SQLite.", e)
                self.use_postgres = False
                self._init_sqlite()
        else:
            logger.warning(
                "[Database Notice] DATABASE_URL is not set to Postgres. Using SQLite database at: %s",
                SQLITE_DB_PATH
            )
            self._init_sqlite()

    def _init_sqlite(self):
        import sqlite3
        db_path = DATABASE_URL.replace("sqlite:///", "") if DATABASE_URL.startswith("sqlite:///") else SQLITE_DB_PATH
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS food_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_key TEXT UNIQUE,
            name TEXT,
            serving_unit TEXT,
            serving_qty REAL,
            calories REAL,
            protein REAL,
            carbs REAL,
            fats REAL,
            tags TEXT,
            hit_count INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        cursor.execute("SELECT COUNT(*) FROM food_cache")
        if cursor.fetchone()[0] == 0:
            for name, unit, qty, cal, p, c, f, tags in SEEDED_FOODS:
                key = normalize_key(name)
                cursor.execute("""
                INSERT OR IGNORE INTO food_cache (food_key, name, serving_unit, serving_qty, calories, protein, carbs, fats, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (key, name.title(), unit, qty, cal, p, c, f, tags))
        conn.commit()
        conn.close()

    def lookup(self, food_name: str, quantity: float = 1.0, unit: Optional[str] = None) -> Optional[Dict[str, Any]]:
        key = normalize_key(food_name)
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            param_placeholder = "%s" if self.use_postgres else "?"

            # 1. Exact match
            cursor.execute(f"SELECT * FROM food_cache WHERE food_key = {param_placeholder}", (key,))
            row = cursor.fetchone()

            # 2. Substring match (e.g. 'chicken curry bowl' matching 'chicken curry')
            if not row:
                cursor.execute(f"SELECT * FROM food_cache WHERE food_key LIKE {param_placeholder} OR {param_placeholder} LIKE CONCAT('%%', food_key, '%%') ORDER BY LENGTH(food_key) DESC LIMIT 1", (f"%{key}%", key))
                row = cursor.fetchone()

            if row:
                row_dict = dict(row)
                cursor.execute(f"UPDATE food_cache SET hit_count = hit_count + 1 WHERE id = {param_placeholder}", (row_dict["id"],))
                conn.commit()
                conn.close()

                base_qty = row_dict["serving_qty"] or 1.0
                scale = quantity / base_qty if base_qty > 0 else quantity

                return {
                    "name": row_dict["name"],
                    "quantity": quantity,
                    "unit": unit or row_dict["serving_unit"],
                    "calories": int(round(row_dict["calories"] * scale)),
                    "protein": round(row_dict["protein"] * scale, 1),
                    "carbs": round(row_dict["carbs"] * scale, 1),
                    "fats": round(row_dict["fats"] * scale, 1),
                    "cached": True,
                    "hits": row_dict["hit_count"] + 1
                }

            conn.close()
            return None
        except Exception as e:
            logger.error("Error during food_cache lookup: %s", e)
            return None

    def save(self, name: str, quantity: float, unit: str, calories: int, protein: float, carbs: float, fats: float, tags: str = ""):
        key = normalize_key(name)
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            unit_scale = 1.0 / quantity if quantity > 0 else 1.0

            if self.use_postgres:
                cursor.execute("""
                INSERT INTO food_cache (food_key, name, serving_unit, serving_qty, calories, protein, carbs, fats, tags, hit_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
                ON CONFLICT (food_key) DO UPDATE SET
                    calories = EXCLUDED.calories,
                    protein = EXCLUDED.protein,
                    carbs = EXCLUDED.carbs,
                    fats = EXCLUDED.fats,
                    hit_count = food_cache.hit_count + 1
                """, (
                    key,
                    name.title(),
                    unit,
                    1.0,
                    round(calories * unit_scale),
                    round(protein * unit_scale, 1),
                    round(carbs * unit_scale, 1),
                    round(fats * unit_scale, 1),
                    tags
                ))
            else:
                cursor.execute("""
                INSERT INTO food_cache (food_key, name, serving_unit, serving_qty, calories, protein, carbs, fats, tags, hit_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                ON CONFLICT(food_key) DO UPDATE SET
                    calories=excluded.calories,
                    protein=excluded.protein,
                    carbs=excluded.carbs,
                    fats=excluded.fats,
                    hit_count=food_cache.hit_count + 1
                """, (
                    key,
                    name.title(),
                    unit,
                    1.0,
                    round(calories * unit_scale),
                    round(protein * unit_scale, 1),
                    round(carbs * unit_scale, 1),
                    round(fats * unit_scale, 1),
                    tags
                ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error("Error saving to food_cache: %s", e)

# Singleton cache instance
smart_cache = SmartCache()
