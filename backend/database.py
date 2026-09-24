import os
import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from backend.models import MealLog, FoodItem, Vitals, DashboardSummary, ChatMessage, UserProfile

# Ensure environment variables are loaded
load_dotenv()

logger = logging.getLogger("macroly.database")
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
DEFAULT_SQLITE_PATH = os.path.join(os.path.dirname(__file__), "macroly.db")
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", DEFAULT_SQLITE_PATH).strip()

def is_postgres() -> bool:
    return DATABASE_URL.startswith("postgresql://") or DATABASE_URL.startswith("postgres://")

ELENA_USER_ID = "elena-demo-account-000000000001"

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
    def __init__(self):
        self.use_postgres = is_postgres()
        self.chat_histories: Dict[str, List[ChatMessage]] = {}
        # Initialize tables & seed baseline
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
        """Create users, meal_logs, and user_vitals tables in PostgreSQL or SQLite fallback."""
        if self.use_postgres:
            try:
                import psycopg2
                conn = psycopg2.connect(DATABASE_URL)
                cursor = conn.cursor()
                # 1. users table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id VARCHAR(255) PRIMARY KEY,
                    email VARCHAR(255) NOT NULL,
                    display_name VARCHAR(255) DEFAULT 'User',
                    calorie_goal INTEGER DEFAULT 2000,
                    protein_goal REAL DEFAULT 130.0,
                    carb_goal REAL DEFAULT 220.0,
                    fat_goal REAL DEFAULT 65.0,
                    is_onboarded BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)

                # 2. meal_logs table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS meal_logs (
                    id VARCHAR(255) PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL DEFAULT 'Elena',
                    food_name VARCHAR(255) NOT NULL,
                    quantity REAL DEFAULT 1.0,
                    unit VARCHAR(50) DEFAULT 'serving',
                    calories INTEGER DEFAULT 0,
                    protein REAL DEFAULT 0.0,
                    carbs REAL DEFAULT 0.0,
                    fats REAL DEFAULT 0.0,
                    meal_type VARCHAR(50) NOT NULL,
                    timestamp VARCHAR(50) NOT NULL,
                    items_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_meal_logs_user_id ON meal_logs(user_id);")

                # 3. user_vitals table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_vitals (
                    user_id VARCHAR(255) PRIMARY KEY,
                    workout_kcal INTEGER DEFAULT 0,
                    workout_mins INTEGER DEFAULT 0,
                    hydration_liters REAL DEFAULT 0.0,
                    hydration_target REAL DEFAULT 3.0,
                    weight_kg REAL DEFAULT 65.0
                );
                """)

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
        db_path = DATABASE_URL.replace("sqlite:///", "") if DATABASE_URL.startswith("sqlite:///") else SQLITE_DB_PATH
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
            is_onboarded INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

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
            items_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_meal_logs_user_id ON meal_logs(user_id);")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_vitals (
            user_id TEXT PRIMARY KEY,
            workout_kcal INTEGER DEFAULT 0,
            workout_mins INTEGER DEFAULT 0,
            hydration_liters REAL DEFAULT 0.0,
            hydration_target REAL DEFAULT 3.0,
            weight_kg REAL DEFAULT 65.0
        );
        """)

        self._seed_elena(cursor, is_pg=False)

        conn.commit()
        conn.close()
        logger.info("Database initialized successfully in SQLite (%s)", db_path)

    def _seed_elena(self, cursor, is_pg: bool):
        placeholder = "%s" if is_pg else "?"
        # 1. Seed Elena user
        cursor.execute(f"SELECT COUNT(*) FROM users WHERE id = {placeholder} OR id = 'Elena'", (ELENA_USER_ID,))
        row = cursor.fetchone()
        count = row[0] if row else 0
        if count == 0:
            if is_pg:
                cursor.execute("""
                INSERT INTO users (id, email, display_name, calorie_goal, protein_goal, carb_goal, fat_goal, is_onboarded)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """, (ELENA_USER_ID, "elena@macroly.test", "Elena", 2200, 140.0, 220.0, 65.0, True))
            else:
                cursor.execute("""
                INSERT OR IGNORE INTO users (id, email, display_name, calorie_goal, protein_goal, carb_goal, fat_goal, is_onboarded)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (ELENA_USER_ID, "elena@macroly.test", "Elena", 2200, 140.0, 220.0, 65.0, 1))

        # 2. Seed Elena vitals
        cursor.execute(f"SELECT COUNT(*) FROM user_vitals WHERE user_id = {placeholder}", (ELENA_USER_ID,))
        row = cursor.fetchone()
        if (row[0] if row else 0) == 0:
            if is_pg:
                cursor.execute("""
                INSERT INTO user_vitals (user_id, workout_kcal, workout_mins, hydration_liters, hydration_target, weight_kg)
                VALUES (%s, 320, 45, 2.1, 3.0, 64.2)
                ON CONFLICT (user_id) DO NOTHING
                """, (ELENA_USER_ID,))
            else:
                cursor.execute("""
                INSERT OR IGNORE INTO user_vitals (user_id, workout_kcal, workout_mins, hydration_liters, hydration_target, weight_kg)
                VALUES (?, 320, 45, 2.1, 3.0, 64.2)
                """, (ELENA_USER_ID,))

        # 3. Seed Elena meals
        cursor.execute(f"SELECT COUNT(*) FROM meal_logs WHERE user_id = {placeholder} OR user_id = 'Elena'", (ELENA_USER_ID,))
        row = cursor.fetchone()
        if (row[0] if row else 0) == 0:
            for m in BASELINE_MEALS:
                if is_pg:
                    cursor.execute("""
                    INSERT INTO meal_logs (id, user_id, food_name, quantity, unit, calories, protein, carbs, fats, meal_type, timestamp, items_json)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """, (
                        m["id"], ELENA_USER_ID, m["food_name"], m["quantity"], m["unit"],
                        m["calories"], m["protein"], m["carbs"], m["fats"],
                        m["meal_type"], m["timestamp"], json.dumps(m["items"])
                    ))
                else:
                    cursor.execute("""
                    INSERT OR IGNORE INTO meal_logs (id, user_id, food_name, quantity, unit, calories, protein, carbs, fats, meal_type, timestamp, items_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        m["id"], ELENA_USER_ID, m["food_name"], m["quantity"], m["unit"],
                        m["calories"], m["protein"], m["carbs"], m["fats"],
                        m["meal_type"], m["timestamp"], json.dumps(m["items"])
                    ))

    # --- User Profile & Goals Management ---

    def get_user(self, user_id: str) -> Optional[UserProfile]:
        """Fetch user profile by user_id."""
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
                    is_onboarded=bool(d.get("is_onboarded"))
                )
            return None
        except Exception as e:
            logger.error("Error fetching user %s: %s", user_id, e)
            return None

    def get_or_create_user(self, user_id: str, email: str, display_name: str = "User") -> UserProfile:
        """Fetch user profile or create new one with sensible generic defaults."""
        user = self.get_user(user_id)
        if user:
            return user

        # Map Elena backwards compatibility
        if user_id == "Elena" or (email and email.lower().startswith("elena")):
            user = self.get_user(ELENA_USER_ID)
            if user:
                return user

        placeholder = "%s" if self.use_postgres else "?"
        # Sensible generic defaults for new users (not Elena's specific values)
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
                INSERT INTO users (id, email, display_name, calorie_goal, protein_goal, carb_goal, fat_goal, is_onboarded)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET email = EXCLUDED.email
                """, (user_id, email, display_name, default_cal, default_p, default_c, default_f, is_onboarded))
            else:
                cursor.execute("""
                INSERT OR REPLACE INTO users (id, email, display_name, calorie_goal, protein_goal, carb_goal, fat_goal, is_onboarded)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, email, display_name, default_cal, default_p, default_c, default_f, 0))
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
            is_onboarded=is_onboarded
        )

    def update_user_goals(self, user_id: str, calorie_goal: int, protein_goal: float, carb_goal: float, fat_goal: float, display_name: Optional[str] = None) -> Optional[UserProfile]:
        """Update user goals and mark as onboarded."""
        placeholder = "%s" if self.use_postgres else "?"
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if display_name:
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

    # --- User Vitals Management ---

    def get_vitals(self, user_id: str) -> Vitals:
        """Fetch user-scoped vitals or return defaults."""
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
                    weight_kg=float(d.get("weight_kg") or 65.0)
                )
        except Exception as e:
            logger.error("Error fetching vitals for %s: %s", user_id, e)

        # Fallback default vitals
        return Vitals(workout_kcal=0, workout_mins=0, hydration_liters=0.0, hydration_target=3.0, weight_kg=65.0)

    def log_workout(self, user_id: str, duration_mins: int, calories_burned: int):
        """Add workout minutes and burned calories for the authenticated user."""
        current = self.get_vitals(user_id)
        new_mins = current.workout_mins + duration_mins
        new_kcal = current.workout_kcal + calories_burned
        placeholder = "%s" if self.use_postgres else "?"
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if self.use_postgres:
                cursor.execute("""
                INSERT INTO user_vitals (user_id, workout_kcal, workout_mins, hydration_liters, hydration_target, weight_kg)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE SET
                    workout_kcal = EXCLUDED.workout_kcal,
                    workout_mins = EXCLUDED.workout_mins
                """, (user_id, new_kcal, new_mins, current.hydration_liters, current.hydration_target, current.weight_kg))
            else:
                cursor.execute("""
                INSERT OR REPLACE INTO user_vitals (user_id, workout_kcal, workout_mins, hydration_liters, hydration_target, weight_kg)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, new_kcal, new_mins, current.hydration_liters, current.hydration_target, current.weight_kg))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error("Error logging workout for %s: %s", user_id, e)

    def add_hydration(self, user_id: str, liters: float):
        """Add hydration for authenticated user."""
        current = self.get_vitals(user_id)
        new_hydration = round(current.hydration_liters + liters, 1)
        placeholder = "%s" if self.use_postgres else "?"
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if self.use_postgres:
                cursor.execute("""
                INSERT INTO user_vitals (user_id, workout_kcal, workout_mins, hydration_liters, hydration_target, weight_kg)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE SET hydration_liters = EXCLUDED.hydration_liters
                """, (user_id, current.workout_kcal, current.workout_mins, new_hydration, current.hydration_target, current.weight_kg))
            else:
                cursor.execute("""
                INSERT OR REPLACE INTO user_vitals (user_id, workout_kcal, workout_mins, hydration_liters, hydration_target, weight_kg)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, current.workout_kcal, current.workout_mins, new_hydration, current.hydration_target, current.weight_kg))
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

        # Determine image asset thumbnail if available
        image_url = None
        f_lower = row_dict["food_name"].lower()
        if "avocado" in f_lower:
            image_url = "/static/assets/avocado_toast.jpg"
        elif "quinoa" in f_lower:
            image_url = "/static/assets/quinoa_bowl.jpg"
        elif "yogurt" in f_lower:
            image_url = "/static/assets/greek_yogurt.jpg"

        return MealLog(
            id=str(row_dict["id"]),
            user_id=str(row_dict.get("user_id", "")),
            title=row_dict["food_name"],
            meal_type=row_dict["meal_type"],
            timestamp=row_dict["timestamp"],
            items=items,
            total_calories=int(row_dict["calories"]),
            protein=float(row_dict["protein"]),
            carbs=float(row_dict["carbs"]),
            fats=float(row_dict["fats"]),
            subtitle=f"{row_dict['meal_type']} • {row_dict['timestamp']}",
            image_url=image_url
        )

    def get_all_meals(self, user_id: str) -> List[MealLog]:
        """Fetch all meal logs directly for the specified user."""
        placeholder = "%s" if self.use_postgres else "?"
        # Match Elena backwards compatibility
        alt_id = "Elena" if user_id == ELENA_USER_ID else user_id
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT * FROM meal_logs WHERE user_id = {placeholder} OR user_id = {placeholder} ORDER BY created_at ASC",
                (user_id, alt_id)
            )
            rows = cursor.fetchall()
            conn.close()
            return [self._row_to_meal(r) for r in rows]
        except Exception as e:
            logger.error("Error reading meal_logs from database for user %s: %s", user_id, e)
            return []

    def get_meal_by_id(self, meal_id: str, user_id: Optional[str] = None) -> Optional[MealLog]:
        """Fetch meal by id, optionally verifying ownership."""
        placeholder = "%s" if self.use_postgres else "?"
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if user_id:
                alt_id = "Elena" if user_id == ELENA_USER_ID else user_id
                cursor.execute(
                    f"SELECT * FROM meal_logs WHERE id = {placeholder} AND (user_id = {placeholder} OR user_id = {placeholder})",
                    (meal_id, user_id, alt_id)
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
        """Persist meal strictly under the authenticated user's ID."""
        placeholder = "%s" if self.use_postgres else "?"
        items_json = json.dumps([it.dict() for it in meal.items]) if meal.items else None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if self.use_postgres:
                sql = """
                INSERT INTO meal_logs (id, user_id, food_name, quantity, unit, calories, protein, carbs, fats, meal_type, timestamp, items_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    food_name = EXCLUDED.food_name,
                    calories = EXCLUDED.calories,
                    protein = EXCLUDED.protein,
                    carbs = EXCLUDED.carbs,
                    fats = EXCLUDED.fats,
                    meal_type = EXCLUDED.meal_type,
                    timestamp = EXCLUDED.timestamp,
                    items_json = EXCLUDED.items_json
                """
                cursor.execute(sql, (
                    meal.id, user_id, meal.title, 1.0, "serving",
                    meal.total_calories, meal.protein, meal.carbs, meal.fats,
                    meal.meal_type, meal.timestamp, items_json
                ))
            else:
                sql = """
                INSERT OR REPLACE INTO meal_logs (id, user_id, food_name, quantity, unit, calories, protein, carbs, fats, meal_type, timestamp, items_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(sql, (
                    meal.id, user_id, meal.title, 1.0, "serving",
                    meal.total_calories, meal.protein, meal.carbs, meal.fats,
                    meal.meal_type, meal.timestamp, items_json
                ))
            conn.commit()
            conn.close()
            logger.info("Persisted meal '%s' (%s) for user %s", meal.title, meal.id, user_id)
        except Exception as e:
            logger.error("Error saving meal to meal_logs: %s", e)

    def update_meal(self, meal_id: str, updated_data: Dict[str, Any], user_id: Optional[str] = None) -> Optional[MealLog]:
        """Update meal verifying user ownership."""
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

        items_json = json.dumps([it.dict() for it in current_meal.items]) if current_meal.items else None
        placeholder = "%s" if self.use_postgres else "?"

        try:
            conn = self.get_connection()
            cursor = conn.cursor()
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
        placeholder = "%s" if self.use_postgres else "?"
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if user_id:
                alt_id = "Elena" if user_id == ELENA_USER_ID else user_id
                sql = f"DELETE FROM meal_logs WHERE id = {placeholder} AND (user_id = {placeholder} OR user_id = {placeholder})"
                cursor.execute(sql, (meal_id, user_id, alt_id))
            else:
                sql = f"DELETE FROM meal_logs WHERE id = {placeholder}"
                cursor.execute(sql, (meal_id,))
            deleted = cursor.rowcount > 0
            conn.commit()
            conn.close()
            logger.info("Deleted meal %s (success: %s)", meal_id, deleted)
            return deleted
        except Exception as e:
            logger.error("Error deleting meal %s: %s", meal_id, e)
            return False

    def get_dashboard(self, user_id: str) -> DashboardSummary:
        """Build user-isolated dashboard summary."""
        user = self.get_user(user_id)
        if not user:
            user = self.get_or_create_user(user_id, f"{user_id}@macroly.app", "User")

        all_meals = self.get_all_meals(user_id)
        vitals = self.get_vitals(user_id)

        consumed_cal = sum(m.total_calories for m in all_meals)
        p_consumed = round(sum(m.protein for m in all_meals), 1)
        c_consumed = round(sum(m.carbs for m in all_meals), 1)
        f_consumed = round(sum(m.fats for m in all_meals), 1)

        left = max(0, user.calorie_goal - consumed_cal + vitals.workout_kcal)
        # Exclude placeholder morning matcha if Elena
        visible_meals = [m for m in all_meals if m.id != "meal_0"]

        now_hour = datetime.now().hour
        greeting_time = "Good morning" if now_hour < 12 else ("Good afternoon" if now_hour < 17 else "Good evening")
        date_str = datetime.now().strftime("%A, %b %d")

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
        placeholder = "%s" if self.use_postgres else "?"
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            alt_id = "Elena" if user_id == ELENA_USER_ID else user_id
            cursor.execute(f"DELETE FROM meal_logs WHERE user_id = {placeholder} OR user_id = {placeholder}", (user_id, alt_id))
            cursor.execute(f"DELETE FROM user_vitals WHERE user_id = {placeholder}", (user_id,))
            if user_id == ELENA_USER_ID:
                self._seed_elena(cursor, is_pg=self.use_postgres)
            conn.commit()
            conn.close()
            logger.info("Reset user %s data", user_id)
        except Exception as e:
            logger.error("Error resetting user data for %s: %s", user_id, e)

    # --- Chat History Management ---

    def get_chat_history(self, user_id: str) -> List[ChatMessage]:
        return self.chat_histories.get(user_id, [])

    def add_chat_message(self, user_id: str, message: ChatMessage):
        if user_id not in self.chat_histories:
            self.chat_histories[user_id] = []
        self.chat_histories[user_id].append(message)

    # Dynamic property for backward compatibility
    @property
    def meals(self) -> List[MealLog]:
        return self.get_all_meals(ELENA_USER_ID)

data_store = DataStore()
