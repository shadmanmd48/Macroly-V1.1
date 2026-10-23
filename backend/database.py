import os
import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from backend.models import MealLog, FoodItem, Vitals, DashboardSummary, ChatMessage, UserProfile, DailyHistoryItem

# Indian Standard Time (IST, UTC+5:30) helper functions
IST = timezone(timedelta(hours=5, minutes=30))

def get_ist_now() -> datetime:
    return datetime.now(IST)

def get_ist_today_str() -> str:
    return get_ist_now().strftime("%Y-%m-%d")

# Ensure environment variables are loaded
load_dotenv(override=True)

logger = logging.getLogger("macroly.database")
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
DEFAULT_SQLITE_PATH = os.path.join(os.path.dirname(__file__), "macroly.db")
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", DEFAULT_SQLITE_PATH).strip()

def is_postgres() -> bool:
    return DATABASE_URL.startswith("postgresql://") or DATABASE_URL.startswith("postgres://")

ELENA_USER_ID = "86759b8f-d1fd-4f9a-9e3d-a93bf143c10b"

# Baseline mock meals for initial Elena seeding
BASELINE_MEALS = [
    {
        "id": "meal_1",
        "user_id": ELENA_USER_ID,
        "food_name": "Avocado Sourdough & Poached Eggs",
        "quantity": 1.0,
        "unit": "plate",
        "calories": 420,
        "protein": 22.0,
        "carbs": 34.0,
        "fats": 18.0,
        "meal_type": "Breakfast",
        "timestamp": "8:30 AM",
        "items": [
            {"name": "Sourdough Toast", "quantity": 2.0, "unit": "slice", "calories": 200, "protein": 7.0, "carbs": 38.0, "fats": 2.0},
            {"name": "Fresh Avocado", "quantity": 0.5, "unit": "serving", "calories": 120, "protein": 1.5, "carbs": 6.0, "fats": 11.0},
            {"name": "Poached Eggs", "quantity": 2.0, "unit": "egg", "calories": 144, "protein": 12.6, "carbs": 0.8, "fats": 9.6},
        ]
    },
    {
        "id": "meal_2",
        "user_id": ELENA_USER_ID,
        "food_name": "Mediterranean Quinoa Bowl",
        "quantity": 1.0,
        "unit": "bowl",
        "calories": 580,
        "protein": 46.0,
        "carbs": 48.0,
        "fats": 16.0,
        "meal_type": "Lunch",
        "timestamp": "1:15 PM",
        "items": [
            {"name": "Cooked Quinoa", "quantity": 1.0, "unit": "bowl", "calories": 220, "protein": 8.0, "carbs": 39.0, "fats": 3.5},
            {"name": "Grilled Chicken", "quantity": 1.0, "unit": "breast", "calories": 260, "protein": 34.0, "carbs": 0.0, "fats": 5.5},
            {"name": "Kalamata Olives & Feta", "quantity": 1.0, "unit": "serving", "calories": 100, "protein": 4.0, "carbs": 9.0, "fats": 7.0},
        ]
    },
    {
        "id": "meal_3",
        "user_id": ELENA_USER_ID,
        "food_name": "Greek Yogurt & Berry Crunch",
        "quantity": 1.0,
        "unit": "parfait",
        "calories": 240,
        "protein": 24.0,
        "carbs": 18.0,
        "fats": 4.0,
        "meal_type": "Snack",
        "timestamp": "4:40 PM",
        "items": [
            {"name": "Greek Yogurt 0%", "quantity": 1.0, "unit": "cup", "calories": 130, "protein": 18.0, "carbs": 6.0, "fats": 0.5},
            {"name": "Mixed Forest Berries", "quantity": 0.5, "unit": "cup", "calories": 40, "protein": 0.5, "carbs": 9.0, "fats": 0.5},
            {"name": "Almond Granola Cluster", "quantity": 1.0, "unit": "handful", "calories": 70, "protein": 5.5, "carbs": 3.0, "fats": 3.0},
        ]
    },
    {
        "id": "meal_0",
        "user_id": ELENA_USER_ID,
        "food_name": "Morning Matcha & Almond Collagen",
        "quantity": 1.0,
        "unit": "cup",
        "calories": 210,
        "protein": 18.0,
        "carbs": 65.0,
        "fats": 4.0,
        "meal_type": "Breakfast",
        "timestamp": "7:45 AM",
        "items": [
            {"name": "Almond Matcha Latte", "quantity": 1.0, "unit": "cup", "calories": 210, "protein": 18.0, "carbs": 65.0, "fats": 4.0}
        ]
    }
]

class DataStore:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        self.use_postgres = is_postgres() if db_path is None else False
        self.chat_histories: Dict[str, List[ChatMessage]] = {}
        # Initialize tables & seed baseline
        self.init_db()

    def close(self):
        pass

    def get_connection(self):
        if self.use_postgres:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        else:
            import sqlite3
            path = self.db_path or (DATABASE_URL.replace("sqlite:///", "") if DATABASE_URL.startswith("sqlite:///") else SQLITE_DB_PATH)
            conn = sqlite3.connect(path)
            conn.row_factory = sqlite3.Row
            return conn

    def init_db(self):
        """Create users, meal_logs, user_vitals, and daily_history tables in PostgreSQL or SQLite fallback."""
        if self.use_postgres:
            try:
                import psycopg2
                conn = psycopg2.connect(DATABASE_URL)
                cursor = conn.cursor()
                # 1. users table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
                    email VARCHAR(255) NOT NULL,
                    display_name VARCHAR(255) DEFAULT 'User',
                    calorie_goal INTEGER DEFAULT 2000,
                    protein_goal REAL DEFAULT 130.0,
                    carb_goal REAL DEFAULT 220.0,
                    fat_goal REAL DEFAULT 65.0,
                    avatar_url TEXT,
                    is_onboarded BOOLEAN DEFAULT FALSE,
                    last_active_date VARCHAR(20) DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
                try:
                    cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url TEXT;")
                    cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_active_date VARCHAR(20) DEFAULT '';")
                except Exception:
                    pass

                # 2. meal_logs table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS meal_logs (
                    id VARCHAR(255) PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    food_name VARCHAR(255) NOT NULL,
                    quantity REAL DEFAULT 1.0,
                    unit VARCHAR(50) DEFAULT 'serving',
                    calories INTEGER DEFAULT 0,
                    protein REAL DEFAULT 0.0,
                    carbs REAL DEFAULT 0.0,
                    fats REAL DEFAULT 0.0,
                    meal_type VARCHAR(50) NOT NULL,
                    timestamp VARCHAR(50) NOT NULL,
                    date_str VARCHAR(20) DEFAULT '',
                    items_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_meal_logs_user_id ON meal_logs(user_id);")
                try:
                    cursor.execute("ALTER TABLE meal_logs ADD COLUMN IF NOT EXISTS date_str VARCHAR(20) DEFAULT '';")
                except Exception:
                    pass

                # 3. user_vitals table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_vitals (
                    user_id VARCHAR(255) PRIMARY KEY,
                    workout_kcal INTEGER DEFAULT 0,
                    workout_mins INTEGER DEFAULT 0,
                    hydration_liters REAL DEFAULT 0.0,
                    hydration_target REAL DEFAULT 3.0,
                    weight_kg REAL DEFAULT 65.0,
                    height_cm REAL DEFAULT 170.0,
                    target_weight_kg REAL DEFAULT 62.0
                );
                """)
                try:
                    cursor.execute("ALTER TABLE user_vitals ADD COLUMN IF NOT EXISTS height_cm REAL DEFAULT 170.0;")
                    cursor.execute("ALTER TABLE user_vitals ADD COLUMN IF NOT EXISTS target_weight_kg REAL DEFAULT 62.0;")
                except Exception:
                    pass

                # 4. daily_history table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_history (
                    id VARCHAR(255) PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    date_str VARCHAR(20) NOT NULL,
                    date_label VARCHAR(100) NOT NULL,
                    calories INTEGER DEFAULT 0,
                    protein REAL DEFAULT 0.0,
                    carbs REAL DEFAULT 0.0,
                    fats REAL DEFAULT 0.0,
                    calorie_target INTEGER DEFAULT 2000,
                    protein_target REAL DEFAULT 130.0,
                    carb_target REAL DEFAULT 220.0,
                    fat_target REAL DEFAULT 65.0,
                    meals_count INTEGER DEFAULT 0,
                    meals_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_history_user ON daily_history(user_id);")

                # Seed Elena test account if not present
                self._seed_elena(cursor, is_pg=True)

                conn.commit()
                conn.close()
                logger.info("Database initialized successfully in PostgreSQL (Supabase)")
            except Exception as e:
                logger.error("Failed to initialize PostgreSQL: %s. Falling back to SQLite.", e)
                self.use_postgres = False
                self._init_sqlite()
        else:
            self._init_sqlite()

    def _init_sqlite(self):
        import sqlite3
        db_path = self.db_path or (DATABASE_URL.replace("sqlite:///", "") if DATABASE_URL.startswith("sqlite:///") else SQLITE_DB_PATH)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            display_name TEXT DEFAULT 'User',
            calorie_goal INTEGER DEFAULT 2000,
            protein_goal REAL DEFAULT 130.0,
            carb_goal REAL DEFAULT 220.0,
            fat_goal REAL DEFAULT 65.0,
            avatar_url TEXT,
            is_onboarded INTEGER DEFAULT 0,
            last_active_date TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        try:
            cursor.execute("PRAGMA table_info(users)")
            cols = [row[1] for row in cursor.fetchall()]
            if "avatar_url" not in cols:
                cursor.execute("ALTER TABLE users ADD COLUMN avatar_url TEXT;")
            if "last_active_date" not in cols:
                cursor.execute("ALTER TABLE users ADD COLUMN last_active_date TEXT DEFAULT '';")
        except Exception:
            pass

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS meal_logs (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL DEFAULT 'Elena',
            food_name TEXT NOT NULL,
            quantity REAL DEFAULT 1.0,
            unit TEXT DEFAULT 'serving',
            calories INTEGER DEFAULT 0,
            protein REAL DEFAULT 0.0,
            carbs REAL DEFAULT 0.0,
            fats REAL DEFAULT 0.0,
            meal_type TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            date_str TEXT DEFAULT '',
            items_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_meal_logs_user_id ON meal_logs(user_id);")
        try:
            cursor.execute("PRAGMA table_info(meal_logs)")
            mcols = [row[1] for row in cursor.fetchall()]
            if "date_str" not in mcols:
                cursor.execute("ALTER TABLE meal_logs ADD COLUMN date_str TEXT DEFAULT '';")
        except Exception:
            pass

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_vitals (
            user_id TEXT PRIMARY KEY,
            workout_kcal INTEGER DEFAULT 0,
            workout_mins INTEGER DEFAULT 0,
            hydration_liters REAL DEFAULT 0.0,
            hydration_target REAL DEFAULT 3.0,
            weight_kg REAL DEFAULT 65.0,
            height_cm REAL DEFAULT 170.0,
            target_weight_kg REAL DEFAULT 62.0
        );
        """)
        try:
            cursor.execute("PRAGMA table_info(user_vitals)")
            vcols = [row[1] for row in cursor.fetchall()]
            if "height_cm" not in vcols:
                cursor.execute("ALTER TABLE user_vitals ADD COLUMN height_cm REAL DEFAULT 170.0;")
            if "target_weight_kg" not in vcols:
                cursor.execute("ALTER TABLE user_vitals ADD COLUMN target_weight_kg REAL DEFAULT 62.0;")
        except Exception:
            pass

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_history (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            date_str TEXT NOT NULL,
            date_label TEXT NOT NULL,
            calories INTEGER DEFAULT 0,
            protein REAL DEFAULT 0.0,
            carbs REAL DEFAULT 0.0,
            fats REAL DEFAULT 0.0,
            calorie_target INTEGER DEFAULT 2000,
            protein_target REAL DEFAULT 130.0,
            carb_target REAL DEFAULT 220.0,
            fat_target REAL DEFAULT 65.0,
            meals_count INTEGER DEFAULT 0,
            meals_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_history_user ON daily_history(user_id);")

        self._seed_elena(cursor, is_pg=False)

        conn.commit()
        conn.close()
        logger.info("Database initialized successfully in SQLite (%s)", db_path)

    def _seed_elena(self, cursor, is_pg: bool):
        placeholder = "%s" if is_pg else "?"
        today_ist = get_ist_today_str()
        # 1. Seed Elena user
        cursor.execute(f"SELECT COUNT(*) FROM users WHERE id = {placeholder}", (ELENA_USER_ID,))
        row = cursor.fetchone()
        count = row[0] if (isinstance(row, (tuple, list))) else (list(row.values())[0] if row else 0)
        if count == 0:
            if is_pg:
                cursor.execute("""
                INSERT INTO users (id, email, display_name, calorie_goal, protein_goal, carb_goal, fat_goal, avatar_url, is_onboarded, last_active_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """, (ELENA_USER_ID, "elena@macroly.test", "Elena", 2200, 140.0, 220.0, 65.0, "/static/assets/avatar.jpg", True, today_ist))
            else:
                cursor.execute("""
                INSERT OR IGNORE INTO users (id, email, display_name, calorie_goal, protein_goal, carb_goal, fat_goal, avatar_url, is_onboarded, last_active_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (ELENA_USER_ID, "elena@macroly.test", "Elena", 2200, 140.0, 220.0, 65.0, "/static/assets/avatar.jpg", 1, today_ist))

        # 2. Seed Elena vitals
        cursor.execute(f"SELECT COUNT(*) FROM user_vitals WHERE user_id = {placeholder}", (ELENA_USER_ID,))
        row = cursor.fetchone()
        count = row[0] if (isinstance(row, (tuple, list))) else (list(row.values())[0] if row else 0)
        if count == 0:
            if is_pg:
                cursor.execute("""
                INSERT INTO user_vitals (user_id, workout_kcal, workout_mins, hydration_liters, hydration_target, weight_kg, height_cm, target_weight_kg)
                VALUES (%s, 320, 45, 2.1, 3.0, 64.2, 172.0, 62.0)
                ON CONFLICT (user_id) DO NOTHING
                """, (ELENA_USER_ID,))
            else:
                cursor.execute("""
                INSERT OR IGNORE INTO user_vitals (user_id, workout_kcal, workout_mins, hydration_liters, hydration_target, weight_kg, height_cm, target_weight_kg)
                VALUES (?, 320, 45, 2.1, 3.0, 64.2, 172.0, 62.0)
                """, (ELENA_USER_ID,))

        # 3. Seed Elena meals
        cursor.execute(f"SELECT COUNT(*) FROM meal_logs WHERE user_id = {placeholder}", (ELENA_USER_ID,))
        row = cursor.fetchone()
        count = row[0] if (isinstance(row, (tuple, list))) else (list(row.values())[0] if row else 0)
        if count == 0:
            for m in BASELINE_MEALS:
                if is_pg:
                    cursor.execute("""
                    INSERT INTO meal_logs (id, user_id, food_name, quantity, unit, calories, protein, carbs, fats, meal_type, timestamp, date_str, items_json)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """, (
                        m["id"], ELENA_USER_ID, m["food_name"], m["quantity"], m["unit"],
                        m["calories"], m["protein"], m["carbs"], m["fats"],
                        m["meal_type"], m["timestamp"], today_ist, json.dumps(m["items"])
                    ))
                else:
                    cursor.execute("""
                    INSERT OR IGNORE INTO meal_logs (id, user_id, food_name, quantity, unit, calories, protein, carbs, fats, meal_type, timestamp, date_str, items_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        m["id"], ELENA_USER_ID, m["food_name"], m["quantity"], m["unit"],
                        m["calories"], m["protein"], m["carbs"], m["fats"],
                        m["meal_type"], m["timestamp"], today_ist, json.dumps(m["items"])
                    ))

        # 4. Seed Elena history for previous 2 days
        cursor.execute(f"SELECT COUNT(*) FROM daily_history WHERE user_id = {placeholder}", (ELENA_USER_ID,))
        row = cursor.fetchone()
        count = row[0] if (isinstance(row, (tuple, list))) else (list(row.values())[0] if row else 0)
        if count == 0:
            y_date = (get_ist_now() - timedelta(days=1)).strftime("%Y-%m-%d")
            y_label = (get_ist_now() - timedelta(days=1)).strftime("%A, %b %d")
            d2_date = (get_ist_now() - timedelta(days=2)).strftime("%Y-%m-%d")
            d2_label = (get_ist_now() - timedelta(days=2)).strftime("%A, %b %d")

            hist_items = [
                (f"hist_{ELENA_USER_ID}_{y_date}", ELENA_USER_ID, y_date, y_label, 2120, 138.0, 215.0, 62.0, 2200, 140.0, 220.0, 65.0, 3, json.dumps([
                    {"title": "Oatmeal with Blueberries & Honey", "calories": 450, "meal_type": "Breakfast"},
                    {"title": "Grilled Chicken Caesar Wrap", "calories": 680, "meal_type": "Lunch"},
                    {"title": "Salmon Fillet & Steamed Asparagus", "calories": 990, "meal_type": "Dinner"}
                ])),
                (f"hist_{ELENA_USER_ID}_{d2_date}", ELENA_USER_ID, d2_date, d2_label, 1980, 132.0, 205.0, 58.0, 2200, 140.0, 220.0, 65.0, 3, json.dumps([
                    {"title": "Greek Yogurt & Granola Parfait", "calories": 360, "meal_type": "Breakfast"},
                    {"title": "Brown Rice Bowl with Tofu", "calories": 620, "meal_type": "Lunch"},
                    {"title": "Paneer Tikka with Whole Wheat Roti", "calories": 1000, "meal_type": "Dinner"}
                ]))
            ]
            for h in hist_items:
                if is_pg:
                    cursor.execute("""
                    INSERT INTO daily_history (id, user_id, date_str, date_label, calories, protein, carbs, fats, calorie_target, protein_target, carb_target, fat_target, meals_count, meals_json)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """, h)
                else:
                    cursor.execute("""
                    INSERT OR IGNORE INTO daily_history (id, user_id, date_str, date_label, calories, protein, carbs, fats, calorie_target, protein_target, carb_target, fat_target, meals_count, meals_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, h)

    # --- User Profile & Goals Management ---

    def get_user(self, user_id: str) -> Optional[UserProfile]:
        """Fetch user profile by user_id."""
        if user_id == "Elena":
            user_id = ELENA_USER_ID
        placeholder = "%s" if self.use_postgres else "?"
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM users WHERE id = {placeholder}", (user_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                d = dict(row)
                return UserProfile(
                    id=str(d["id"]),
                    email=str(d["email"]),
                    display_name=str(d.get("display_name") or "User"),
                    calorie_goal=int(d.get("calorie_goal") or 2000),
                    protein_goal=float(d.get("protein_goal") or 130.0),
                    carb_goal=float(d.get("carb_goal") or 220.0),
                    fat_goal=float(d.get("fat_goal") or 65.0),
                    avatar_url=str(d["avatar_url"]) if d.get("avatar_url") else None,
                    is_onboarded=bool(d.get("is_onboarded"))
                )
            return None
        except Exception as e:
            logger.error("Error fetching user %s: %s", user_id, e)
            return None

    def get_or_create_user(self, user_id: str, email: str, display_name: str = "User", avatar_url: Optional[str] = None) -> UserProfile:
        """Fetch user profile or create new one with sensible generic defaults."""
        user = self.get_user(user_id)
        if user:
            # If avatar_url was passed and user doesn't have one, update it
            if avatar_url and not user.avatar_url:
                self.update_user_avatar(user_id, avatar_url)
                user.avatar_url = avatar_url
            return user

        # Map Elena backwards compatibility
        if user_id == "Elena" or (email and email.lower().startswith("elena")):
            user = self.get_user(ELENA_USER_ID)
            if user:
                return user

        placeholder = "%s" if self.use_postgres else "?"
        # Sensible generic defaults for new users
        default_cal = 2000
        default_p = 130.0
        default_c = 220.0
        default_f = 65.0
        is_onboarded = False

        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if self.use_postgres:
                cursor.execute("""
                INSERT INTO users (id, email, display_name, calorie_goal, protein_goal, carb_goal, fat_goal, avatar_url, is_onboarded)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET email = EXCLUDED.email
                """, (user_id, email, display_name, default_cal, default_p, default_c, default_f, avatar_url, is_onboarded))
            else:
                cursor.execute("""
                INSERT OR REPLACE INTO users (id, email, display_name, calorie_goal, protein_goal, carb_goal, fat_goal, avatar_url, is_onboarded)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, email, display_name, default_cal, default_p, default_c, default_f, avatar_url, 0))
            conn.commit()
            conn.close()
            logger.info("Created user profile for %s (%s)", display_name, user_id)
        except Exception as e:
            logger.error("Error creating user %s: %s", user_id, e)

        return UserProfile(
            id=user_id,
            email=email,
            display_name=display_name,
            calorie_goal=default_cal,
            protein_goal=default_p,
            carb_goal=default_c,
            fat_goal=default_f,
            avatar_url=avatar_url,
            is_onboarded=is_onboarded
        )

    def update_user_goals(self, user_id: str, calorie_goal: int, protein_goal: float, carb_goal: float, fat_goal: float, display_name: Optional[str] = None, avatar_url: Optional[str] = None) -> Optional[UserProfile]:
        """Update user goals and mark as onboarded."""
        if user_id == "Elena":
            user_id = ELENA_USER_ID
        placeholder = "%s" if self.use_postgres else "?"
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if avatar_url and display_name:
                sql = f"""
                UPDATE users
                SET calorie_goal = {placeholder},
                    protein_goal = {placeholder},
                    carb_goal = {placeholder},
                    fat_goal = {placeholder},
                    display_name = {placeholder},
                    avatar_url = {placeholder},
                    is_onboarded = {placeholder}
                WHERE id = {placeholder}
                """
                cursor.execute(sql, (calorie_goal, protein_goal, carb_goal, fat_goal, display_name, avatar_url, True, user_id))
            elif display_name:
                sql = f"""
                UPDATE users
                SET calorie_goal = {placeholder},
                    protein_goal = {placeholder},
                    carb_goal = {placeholder},
                    fat_goal = {placeholder},
                    display_name = {placeholder},
                    is_onboarded = {placeholder}
                WHERE id = {placeholder}
                """
                cursor.execute(sql, (calorie_goal, protein_goal, carb_goal, fat_goal, display_name, True, user_id))
            else:
                sql = f"""
                UPDATE users
                SET calorie_goal = {placeholder},
                    protein_goal = {placeholder},
                    carb_goal = {placeholder},
                    fat_goal = {placeholder},
                    is_onboarded = {placeholder}
                WHERE id = {placeholder}
                """
                cursor.execute(sql, (calorie_goal, protein_goal, carb_goal, fat_goal, True, user_id))
            conn.commit()
            conn.close()
            return self.get_user(user_id)
        except Exception as e:
            logger.error("Error updating user goals for %s: %s", user_id, e)
            return None

    def update_user_avatar(self, user_id: str, avatar_url: str) -> Optional[UserProfile]:
        """Update user avatar URL."""
        if user_id == "Elena":
            user_id = ELENA_USER_ID
        placeholder = "%s" if self.use_postgres else "?"
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            sql = f"UPDATE users SET avatar_url = {placeholder} WHERE id = {placeholder}"
            cursor.execute(sql, (avatar_url, user_id))
            conn.commit()
            conn.close()
            return self.get_user(user_id)
        except Exception as e:
            logger.error("Error updating user avatar for %s: %s", user_id, e)
            return None

    # --- User Vitals Management ---

    def get_vitals(self, user_id: str) -> Vitals:
        """Fetch user-scoped vitals or return defaults."""
        if user_id == "Elena":
            user_id = ELENA_USER_ID
        placeholder = "%s" if self.use_postgres else "?"
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM user_vitals WHERE user_id = {placeholder}", (user_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                d = dict(row)
                return Vitals(
                    workout_kcal=int(d.get("workout_kcal") or 0),
                    workout_mins=int(d.get("workout_mins") or 0),
                    hydration_liters=float(d.get("hydration_liters") or 0.0),
                    hydration_target=float(d.get("hydration_target") or 3.0),
                    weight_kg=float(d.get("weight_kg") or 65.0),
                    height_cm=float(d.get("height_cm") or 170.0),
                    target_weight_kg=float(d.get("target_weight_kg") or 62.0)
                )
        except Exception as e:
            logger.error("Error fetching vitals for %s: %s", user_id, e)

        return Vitals(
            workout_kcal=0,
            workout_mins=0,
            hydration_liters=0.0,
            hydration_target=3.0,
            weight_kg=65.0,
            height_cm=170.0,
            target_weight_kg=62.0
        )

    def update_vitals(
        self,
        user_id: str,
        weight_kg: Optional[float] = None,
        height_cm: Optional[float] = None,
        target_weight_kg: Optional[float] = None
    ) -> Vitals:
        """Update height, weight, and target weight for authenticated user."""
        if user_id == "Elena":
            user_id = ELENA_USER_ID
        current = self.get_vitals(user_id)
        new_weight = float(weight_kg) if weight_kg is not None else current.weight_kg
        new_height = float(height_cm) if height_cm is not None else current.height_cm
        new_target = float(target_weight_kg) if target_weight_kg is not None else current.target_weight_kg
        placeholder = "%s" if self.use_postgres else "?"
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if self.use_postgres:
                cursor.execute("""
                INSERT INTO user_vitals (user_id, workout_kcal, workout_mins, hydration_liters, hydration_target, weight_kg, height_cm, target_weight_kg)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE SET
                    weight_kg = EXCLUDED.weight_kg,
                    height_cm = EXCLUDED.height_cm,
                    target_weight_kg = EXCLUDED.target_weight_kg
                """, (user_id, current.workout_kcal, current.workout_mins, current.hydration_liters, current.hydration_target, new_weight, new_height, new_target))
            else:
                cursor.execute("""
                INSERT OR REPLACE INTO user_vitals (user_id, workout_kcal, workout_mins, hydration_liters, hydration_target, weight_kg, height_cm, target_weight_kg)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, current.workout_kcal, current.workout_mins, current.hydration_liters, current.hydration_target, new_weight, new_height, new_target))
            conn.commit()
            conn.close()
            logger.info("Updated vitals for user %s: weight=%.1f kg, height=%.1f cm, target=%.1f kg", user_id, new_weight, new_height, new_target)
            return self.get_vitals(user_id)
        except Exception as e:
            logger.error("Error updating vitals for %s: %s", user_id, e)
            return current

    def log_workout(self, user_id: str, duration_mins: int, calories_burned: int):
        """Add workout minutes and burned calories for the authenticated user."""
        if user_id == "Elena":
            user_id = ELENA_USER_ID
        current = self.get_vitals(user_id)
        new_mins = current.workout_mins + duration_mins
        new_kcal = current.workout_kcal + calories_burned
        placeholder = "%s" if self.use_postgres else "?"
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if self.use_postgres:
                cursor.execute("""
                INSERT INTO user_vitals (user_id, workout_kcal, workout_mins, hydration_liters, hydration_target, weight_kg, height_cm, target_weight_kg)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE SET
                    workout_kcal = EXCLUDED.workout_kcal,
                    workout_mins = EXCLUDED.workout_mins
                """, (user_id, new_kcal, new_mins, current.hydration_liters, current.hydration_target, current.weight_kg, current.height_cm, current.target_weight_kg))
            else:
                cursor.execute("""
                INSERT OR REPLACE INTO user_vitals (user_id, workout_kcal, workout_mins, hydration_liters, hydration_target, weight_kg, height_cm, target_weight_kg)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, new_kcal, new_mins, current.hydration_liters, current.hydration_target, current.weight_kg, current.height_cm, current.target_weight_kg))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error("Error logging workout for %s: %s", user_id, e)

    def add_hydration(self, user_id: str, liters: float):
        """Add hydration for authenticated user."""
        if user_id == "Elena":
            user_id = ELENA_USER_ID
        current = self.get_vitals(user_id)
        new_hydration = round(current.hydration_liters + liters, 1)
        placeholder = "%s" if self.use_postgres else "?"
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if self.use_postgres:
                cursor.execute("""
                INSERT INTO user_vitals (user_id, workout_kcal, workout_mins, hydration_liters, hydration_target, weight_kg, height_cm, target_weight_kg)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE SET hydration_liters = EXCLUDED.hydration_liters
                """, (user_id, current.workout_kcal, current.workout_mins, new_hydration, current.hydration_target, current.weight_kg, current.height_cm, current.target_weight_kg))
            else:
                cursor.execute("""
                INSERT OR REPLACE INTO user_vitals (user_id, workout_kcal, workout_mins, hydration_liters, hydration_target, weight_kg, height_cm, target_weight_kg)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, current.workout_kcal, current.workout_mins, new_hydration, current.hydration_target, current.weight_kg, current.height_cm, current.target_weight_kg))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error("Error logging hydration for %s: %s", user_id, e)

    # --- Meals Management ---

    def _row_to_meal(self, row: Dict[str, Any]) -> MealLog:
        row_dict = dict(row)
        items: List[FoodItem] = []
        if row_dict.get("items_json"):
            try:
                raw_items = json.loads(row_dict["items_json"])
                items = [FoodItem(**it) for it in raw_items]
            except Exception as e:
                logger.warning("Failed to deserialize items_json for meal %s: %s", row_dict.get("id"), e)

        if not items:
            items = [FoodItem(
                name=row_dict["food_name"],
                quantity=row_dict.get("quantity") or 1.0,
                unit=row_dict.get("unit") or "serving",
                calories=row_dict.get("calories") or 0,
                protein=row_dict.get("protein") or 0.0,
                carbs=row_dict.get("carbs") or 0.0,
                fats=row_dict.get("fats") or 0.0
            )]

        image_url = None
        f_lower = row_dict["food_name"].lower()
        if "avocado" in f_lower:
            image_url = "/static/assets/avocado_toast.jpg"
        elif "quinoa" in f_lower:
            image_url = "/static/assets/quinoa_bowl.jpg"
        elif "yogurt" in f_lower:
            image_url = "/static/assets/greek_yogurt.jpg"

        date_val = str(row_dict.get("date_str") or "").strip()
        if not date_val:
            date_val = get_ist_today_str()

        return MealLog(
            id=str(row_dict["id"]),
            user_id=str(row_dict.get("user_id", "")),
            title=row_dict["food_name"],
            meal_type=row_dict["meal_type"],
            timestamp=row_dict["timestamp"],
            date_str=date_val,
            items=items,
            total_calories=int(row_dict["calories"]),
            protein=float(row_dict["protein"]),
            carbs=float(row_dict["carbs"]),
            fats=float(row_dict["fats"]),
            subtitle=f"{row_dict['meal_type']} • {row_dict['timestamp']}",
            image_url=image_url
        )

    def get_all_meals(self, user_id: str, date_str: Optional[str] = None) -> List[MealLog]:
        """Fetch meal logs directly for the specified user, optionally filtering by date."""
        if user_id == "Elena":
            user_id = ELENA_USER_ID
        placeholder = "%s" if self.use_postgres else "?"
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if date_str is not None:
                cursor.execute(
                    f"SELECT * FROM meal_logs WHERE user_id = {placeholder} AND (date_str = {placeholder} OR (date_str IS NULL AND {placeholder} = '{get_ist_today_str()}')) ORDER BY created_at ASC",
                    (user_id, date_str, date_str)
                )
            else:
                cursor.execute(
                    f"SELECT * FROM meal_logs WHERE user_id = {placeholder} ORDER BY created_at ASC",
                    (user_id,)
                )
            rows = cursor.fetchall()
            conn.close()
            return [self._row_to_meal(r) for r in rows]
        except Exception as e:
            logger.error("Error reading meal_logs from database for user %s: %s", user_id, e)
            return []

    def get_meal_by_id(self, meal_id: str, user_id: Optional[str] = None) -> Optional[MealLog]:
        """Fetch meal by id, optionally verifying ownership."""
        if user_id == "Elena":
            user_id = ELENA_USER_ID
        placeholder = "%s" if self.use_postgres else "?"
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if user_id:
                cursor.execute(
                    f"SELECT * FROM meal_logs WHERE id = {placeholder} AND user_id = {placeholder}",
                    (meal_id, user_id)
                )
            else:
                cursor.execute(
                    f"SELECT * FROM meal_logs WHERE id = {placeholder}",
                    (meal_id,)
                )
            row = cursor.fetchone()
            conn.close()
            if row:
                return self._row_to_meal(row)
            return None
        except Exception as e:
            logger.error("Error fetching meal %s: %s", meal_id, e)
            return None

    def add_meal(self, meal: MealLog, user_id: str):
        """Persist meal strictly under the authenticated user's ID with IST date_str."""
        if user_id == "Elena":
            user_id = ELENA_USER_ID
        placeholder = "%s" if self.use_postgres else "?"
        items_json = json.dumps([it.model_dump() if hasattr(it, "model_dump") else it.dict() for it in meal.items]) if meal.items else None
        date_str = meal.date_str or get_ist_today_str()
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if self.use_postgres:
                sql = """
                INSERT INTO meal_logs (id, user_id, food_name, quantity, unit, calories, protein, carbs, fats, meal_type, timestamp, date_str, items_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    food_name = EXCLUDED.food_name,
                    calories = EXCLUDED.calories,
                    protein = EXCLUDED.protein,
                    carbs = EXCLUDED.carbs,
                    fats = EXCLUDED.fats,
                    meal_type = EXCLUDED.meal_type,
                    timestamp = EXCLUDED.timestamp,
                    date_str = EXCLUDED.date_str,
                    items_json = EXCLUDED.items_json
                """
                cursor.execute(sql, (
                    meal.id, user_id, meal.title, 1.0, "serving",
                    meal.total_calories, meal.protein, meal.carbs, meal.fats,
                    meal.meal_type, meal.timestamp, date_str, items_json
                ))
            else:
                sql = """
                INSERT OR REPLACE INTO meal_logs (id, user_id, food_name, quantity, unit, calories, protein, carbs, fats, meal_type, timestamp, date_str, items_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(sql, (
                    meal.id, user_id, meal.title, 1.0, "serving",
                    meal.total_calories, meal.protein, meal.carbs, meal.fats,
                    meal.meal_type, meal.timestamp, date_str, items_json
                ))
            conn.commit()
            conn.close()
            # Also ensure user's last_active_date is updated to today
            self._set_user_last_active_date(user_id, date_str)
            logger.info("Persisted meal '%s' (%s, date: %s) for user %s", meal.title, meal.id, date_str, user_id)
        except Exception as e:
            logger.error("Error saving meal to meal_logs: %s", e)

    def update_meal(self, meal_id: str, updated_data: Dict[str, Any], user_id: Optional[str] = None) -> Optional[MealLog]:
        """Update meal verifying user ownership."""
        if user_id == "Elena":
            user_id = ELENA_USER_ID
        current_meal = self.get_meal_by_id(meal_id, user_id=user_id)
        if not current_meal:
            return None

        for k, v in updated_data.items():
            if hasattr(current_meal, k) and v is not None:
                if k == "items" and isinstance(v, list):
                    typed_items = []
                    for it in v:
                        if isinstance(it, dict):
                            typed_items.append(FoodItem(**it))
                        else:
                            typed_items.append(it)
                    setattr(current_meal, k, typed_items)
                else:
                    setattr(current_meal, k, v)

        if "items" in updated_data and current_meal.items:
            current_meal.total_calories = sum(it.calories for it in current_meal.items)
            current_meal.protein = round(sum(it.protein for it in current_meal.items), 1)
            current_meal.carbs = round(sum(it.carbs for it in current_meal.items), 1)
            current_meal.fats = round(sum(it.fats for it in current_meal.items), 1)

        items_json = json.dumps([it.model_dump() if hasattr(it, "model_dump") else it.dict() for it in current_meal.items]) if current_meal.items else None
        placeholder = "%s" if self.use_postgres else "?"

        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if user_id:
                sql = f"""
                UPDATE meal_logs
                SET food_name = {placeholder},
                    calories = {placeholder},
                    protein = {placeholder},
                    carbs = {placeholder},
                    fats = {placeholder},
                    meal_type = {placeholder},
                    timestamp = {placeholder},
                    items_json = {placeholder}
                WHERE id = {placeholder} AND user_id = {placeholder}
                """
                cursor.execute(sql, (
                    current_meal.title,
                    current_meal.total_calories,
                    current_meal.protein,
                    current_meal.carbs,
                    current_meal.fats,
                    current_meal.meal_type,
                    current_meal.timestamp,
                    items_json,
                    meal_id,
                    user_id
                ))
            else:
                sql = f"""
                UPDATE meal_logs
                SET food_name = {placeholder},
                    calories = {placeholder},
                    protein = {placeholder},
                    carbs = {placeholder},
                    fats = {placeholder},
                    meal_type = {placeholder},
                    timestamp = {placeholder},
                    items_json = {placeholder}
                WHERE id = {placeholder}
                """
                cursor.execute(sql, (
                    current_meal.title,
                    current_meal.total_calories,
                    current_meal.protein,
                    current_meal.carbs,
                    current_meal.fats,
                    current_meal.meal_type,
                    current_meal.timestamp,
                    items_json,
                    meal_id
                ))
            conn.commit()
            conn.close()
            logger.info("Updated meal %s", meal_id)
            return current_meal
        except Exception as e:
            logger.error("Error updating meal %s: %s", meal_id, e)
            return None

    def delete_meal(self, meal_id: str, user_id: Optional[str] = None) -> bool:
        """Delete meal verifying user ownership."""
        if user_id == "Elena":
            user_id = ELENA_USER_ID
        placeholder = "%s" if self.use_postgres else "?"
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if user_id:
                sql = f"DELETE FROM meal_logs WHERE id = {placeholder} AND user_id = {placeholder}"
                cursor.execute(sql, (meal_id, user_id))
            else:
                sql = f"DELETE FROM meal_logs WHERE id = {placeholder}"
                cursor.execute(sql, (meal_id,))
            deleted = cursor.rowcount > 0
            conn.commit()
            conn.close()
            logger.info("Deleted meal %s for user %s (success: %s)", meal_id, user_id, deleted)
            return deleted
        except Exception as e:
            logger.error("Error deleting meal %s: %s", meal_id, e)
            return False

    def get_dashboard(self, user_id: str) -> DashboardSummary:
        """Build user-isolated dashboard summary filtered to today's date in IST."""
        if user_id == "Elena":
            user_id = ELENA_USER_ID
        user = self.get_user(user_id)
        if not user:
            user = self.get_or_create_user(user_id, f"{user_id}@macroly.app", "User")

        today_ist = get_ist_today_str()
        all_meals = self.get_all_meals(user_id, date_str=today_ist)
        vitals = self.get_vitals(user_id)

        consumed_cal = sum(m.total_calories for m in all_meals)
        p_consumed = round(sum(m.protein for m in all_meals), 1)
        c_consumed = round(sum(m.carbs for m in all_meals), 1)
        f_consumed = round(sum(m.fats for m in all_meals), 1)

        left = max(0, user.calorie_goal - consumed_cal + vitals.workout_kcal)
        visible_meals = [m for m in all_meals if m.id != "meal_0"]

        now_ist = get_ist_now()
        now_hour = now_ist.hour
        greeting_time = "Good morning" if now_hour < 12 else ("Good afternoon" if now_hour < 17 else "Good evening")
        date_str = now_ist.strftime("%A, %b %d")

        # Keep last active date up to date
        self._set_user_last_active_date(user_id, today_ist)

        return DashboardSummary(
            user_name=user.display_name,
            greeting=f"{greeting_time}, {user.display_name} 👋",
            date_str=date_str,
            calorie_target=user.calorie_goal,
            calories_consumed=consumed_cal,
            calories_burned=vitals.workout_kcal,
            calories_left=left,
            protein_consumed=p_consumed,
            protein_target=user.protein_goal,
            carbs_consumed=c_consumed,
            carbs_target=user.carb_goal,
            fats_consumed=f_consumed,
            fats_target=user.fat_goal,
            vitals=vitals,
            meals=visible_meals
        )

    def reset_to_default(self, user_id: str):
        """Resets only the specific user's meals and vitals."""
        if user_id == "Elena":
            user_id = ELENA_USER_ID
        placeholder = "%s" if self.use_postgres else "?"
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM meal_logs WHERE user_id = {placeholder}", (user_id,))
            cursor.execute(f"DELETE FROM user_vitals WHERE user_id = {placeholder}", (user_id,))
            if user_id == ELENA_USER_ID:
                self._seed_elena(cursor, is_pg=self.use_postgres)
            conn.commit()
            conn.close()
            logger.info("Reset user %s data", user_id)
        except Exception as e:
            logger.error("Error resetting user data for %s: %s", user_id, e)

    # --- Daily History & New Day Transition Management ---

    def _set_user_last_active_date(self, user_id: str, date_str: str):
        """Record last active date for day rollover tracking."""
        if user_id == "Elena":
            user_id = ELENA_USER_ID
        placeholder = "%s" if self.use_postgres else "?"
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"UPDATE users SET last_active_date = {placeholder} WHERE id = {placeholder}", (date_str, user_id))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error("Error updating last_active_date for %s: %s", user_id, e)

    def _get_history_entry_for_date(self, user_id: str, date_str: str) -> Optional[Dict[str, Any]]:
        if user_id == "Elena":
            user_id = ELENA_USER_ID
        placeholder = "%s" if self.use_postgres else "?"
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM daily_history WHERE user_id = {placeholder} AND date_str = {placeholder}", (user_id, date_str))
            row = cursor.fetchone()
            conn.close()
            if row:
                d = dict(row)
                return d
            return None
        except Exception:
            return None

    def add_daily_history(
        self,
        user_id: str,
        date_str: str,
        date_label: str,
        calories: int,
        protein: float,
        carbs: float,
        fats: float,
        calorie_target: int,
        protein_target: float,
        carb_target: float,
        fat_target: float,
        meals_count: int,
        meals: List[Dict[str, Any]]
    ):
        """Archive a full day's nutrition summary into history."""
        if user_id == "Elena":
            user_id = ELENA_USER_ID
        hist_id = f"hist_{user_id}_{date_str}"
        meals_json = json.dumps(meals)
        placeholder = "%s" if self.use_postgres else "?"
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if self.use_postgres:
                sql = """
                INSERT INTO daily_history (id, user_id, date_str, date_label, calories, protein, carbs, fats, calorie_target, protein_target, carb_target, fat_target, meals_count, meals_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    calories = EXCLUDED.calories,
                    protein = EXCLUDED.protein,
                    carbs = EXCLUDED.carbs,
                    fats = EXCLUDED.fats,
                    meals_count = EXCLUDED.meals_count,
                    meals_json = EXCLUDED.meals_json
                """
            else:
                sql = """
                INSERT OR REPLACE INTO daily_history (id, user_id, date_str, date_label, calories, protein, carbs, fats, calorie_target, protein_target, carb_target, fat_target, meals_count, meals_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
            cursor.execute(sql, (
                hist_id, user_id, date_str, date_label, calories, protein, carbs, fats,
                calorie_target, protein_target, carb_target, fat_target, meals_count, meals_json
            ))
            conn.commit()
            conn.close()
            logger.info("Archived daily history for %s on %s (%d kcal)", user_id, date_str, calories)
        except Exception as e:
            logger.error("Error saving daily history for %s: %s", user_id, e)

    def get_user_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Fetch daily nutrition history records for user, ordered by date desc."""
        if user_id == "Elena":
            user_id = ELENA_USER_ID
        placeholder = "%s" if self.use_postgres else "?"
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT * FROM daily_history WHERE user_id = {placeholder} ORDER BY date_str DESC",
                (user_id,)
            )
            rows = cursor.fetchall()
            conn.close()
            results = []
            for r in rows:
                d = dict(r)
                meals_list = []
                if d.get("meals_json"):
                    try:
                        meals_list = json.loads(d["meals_json"])
                    except Exception:
                        pass
                results.append({
                    "id": str(d["id"]),
                    "user_id": str(d["user_id"]),
                    "date_str": str(d["date_str"]),
                    "date_label": str(d["date_label"]),
                    "calories": int(d.get("calories") or 0),
                    "protein": float(d.get("protein") or 0.0),
                    "carbs": float(d.get("carbs") or 0.0),
                    "fats": float(d.get("fats") or 0.0),
                    "calorie_target": int(d.get("calorie_target") or 2000),
                    "protein_target": float(d.get("protein_target") or 130.0),
                    "carb_target": float(d.get("carb_target") or 220.0),
                    "fat_target": float(d.get("fat_target") or 65.0),
                    "meals_count": int(d.get("meals_count") or len(meals_list)),
                    "meals": meals_list
                })
            return results
        except Exception as e:
            logger.error("Error reading daily history for user %s: %s", user_id, e)
            return []

    def check_day_transition(self, user_id: str) -> Dict[str, Any]:
        """
        Checks if user is accessing on a new day in IST.
        Returns whether to show the previous day summary pop-up.
        """
        if user_id == "Elena":
            user_id = ELENA_USER_ID
        today_ist = get_ist_today_str()
        user = self.get_user(user_id)
        if not user:
            return {"show_transition": False, "today_date_str": today_ist, "previous_day": None}

        last_date = ""
        placeholder = "%s" if self.use_postgres else "?"
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT last_active_date FROM users WHERE id = {placeholder}", (user_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                d = dict(row)
                last_date = str(d.get("last_active_date") or "").strip()
        except Exception as e:
            logger.warning("Could not read last_active_date for %s: %s", user_id, e)

        # If user has no last_active_date, initialize to today and no popup
        if not last_date:
            self._set_user_last_active_date(user_id, today_ist)
            return {"show_transition": False, "today_date_str": today_ist, "previous_day": None}

        # If today is after last_active_date, a new day in IST has arrived!
        if last_date < today_ist:
            prev_meals = self.get_all_meals(user_id, date_str=last_date)
            prev_history = self._get_history_entry_for_date(user_id, last_date)

            cals = sum(m.total_calories for m in prev_meals)
            p = round(sum(m.protein for m in prev_meals), 1)
            c = round(sum(m.carbs for m in prev_meals), 1)
            f = round(sum(m.fats for m in prev_meals), 1)

            if prev_history:
                cals = int(prev_history.get("calories") or cals)
                p = float(prev_history.get("protein") or p)
                c = float(prev_history.get("carbs") or c)
                f = float(prev_history.get("fats") or f)

            try:
                dt = datetime.strptime(last_date, "%Y-%m-%d")
                date_label = dt.strftime("%A, %b %d")
            except Exception:
                date_label = last_date

            previous_day_summary = {
                "date_str": last_date,
                "date_label": date_label,
                "calories": cals,
                "calorie_target": user.calorie_goal,
                "protein": p,
                "protein_target": user.protein_goal,
                "carbs": c,
                "carbs_target": user.carb_goal,
                "fats": f,
                "fats_target": user.fat_goal,
                "meals_count": len(prev_meals),
                "meals": [{"title": m.title, "calories": m.total_calories, "meal_type": m.meal_type} for m in prev_meals]
            }

            return {
                "show_transition": True,
                "today_date_str": today_ist,
                "previous_day": previous_day_summary,
                "yesterday_summary": previous_day_summary
            }

        return {"show_transition": False, "today_date_str": today_ist, "previous_day": None, "yesterday_summary": None}

    def start_new_day(self, user_id: str) -> DashboardSummary:
        """
        Archives yesterday's intake into daily_history, resets today's vitals (hydration, workout)
        and sets last_active_date to today_ist.
        """
        if user_id == "Elena":
            user_id = ELENA_USER_ID
        today_ist = get_ist_today_str()
        user = self.get_user(user_id)
        if not user:
            user = self.get_or_create_user(user_id, f"{user_id}@macroly.app", "User")

        placeholder = "%s" if self.use_postgres else "?"
        last_date = ""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT last_active_date FROM users WHERE id = {placeholder}", (user_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                last_date = str(dict(row).get("last_active_date") or "").strip()
        except Exception:
            pass

        archive_date = last_date if (last_date and last_date < today_ist) else ""
        if archive_date:
            prev_meals = self.get_all_meals(user_id, date_str=archive_date)
            existing = self._get_history_entry_for_date(user_id, archive_date)
            if not existing and prev_meals:
                try:
                    dt = datetime.strptime(archive_date, "%Y-%m-%d")
                    date_label = dt.strftime("%A, %b %d")
                except Exception:
                    date_label = archive_date

                cals = sum(m.total_calories for m in prev_meals)
                p = round(sum(m.protein for m in prev_meals), 1)
                c = round(sum(m.carbs for m in prev_meals), 1)
                f = round(sum(m.fats for m in prev_meals), 1)
                meals_data = [{"title": m.title, "calories": m.total_calories, "meal_type": m.meal_type} for m in prev_meals]

                self.add_daily_history(
                    user_id=user_id,
                    date_str=archive_date,
                    date_label=date_label,
                    calories=cals,
                    protein=p,
                    carbs=c,
                    fats=f,
                    calorie_target=user.calorie_goal,
                    protein_target=user.protein_goal,
                    carb_target=user.carb_goal,
                    fat_target=user.fat_goal,
                    meals_count=len(prev_meals),
                    meals=meals_data
                )

        # Reset daily counters: workout_kcal=0, workout_mins=0, hydration_liters=0.0
        # while preserving weight_kg, height_cm, target_weight_kg
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if self.use_postgres:
                cursor.execute("""
                UPDATE user_vitals
                SET workout_kcal = 0, workout_mins = 0, hydration_liters = 0.0
                WHERE user_id = %s
                """, (user_id,))
            else:
                cursor.execute("""
                UPDATE user_vitals
                SET workout_kcal = 0, workout_mins = 0, hydration_liters = 0.0
                WHERE user_id = ?
                """, (user_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error("Error resetting daily vitals for %s: %s", user_id, e)

        # Update last_active_date to today_ist
        self._set_user_last_active_date(user_id, today_ist)
        return self.get_dashboard(user_id)

    # --- Chat History Management ---

    def get_chat_history(self, user_id: str) -> List[ChatMessage]:
        if user_id == "Elena":
            user_id = ELENA_USER_ID
        return self.chat_histories.get(user_id, [])

    def add_chat_message(self, user_id: str, message: ChatMessage):
        if user_id == "Elena":
            user_id = ELENA_USER_ID
        if user_id not in self.chat_histories:
            self.chat_histories[user_id] = []
        self.chat_histories[user_id].append(message)

    # Dynamic property for backward compatibility
    @property
    def meals(self) -> List[MealLog]:
        return self.get_all_meals(ELENA_USER_ID)

data_store = DataStore()

