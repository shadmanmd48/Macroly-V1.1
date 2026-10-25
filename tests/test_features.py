"""
Unit Tests for Macroly Backend Features and Security
Covers:
1. Multi-user height and weight change (isolation & persistence)
2. Meal deletion via chat and direct API
3. Category prompting (Breakfast, Lunch, Snacks, Cheat Meal, Dinner) and cancellation
4. IST Midnight rollover, Day Transition status, and Daily History archival
5. Heuristic nutrition lookup fallback without network
6. Demo auth backdoor rejection when disabled
"""

import os
import sys
import unittest
import tempfile

# Guarantee test mode before any backend modules are imported
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = ""

# Ensure repository root is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.models import UpdateVitalsRequest, MealLog, FoodItem
from backend.database import DataStore, get_ist_today_str, get_ist_now
from backend.ai_interpreter import AIInterpreter, VALID_MEAL_TYPES
from backend.nutrition_service import NutritionService


class TestMacrolyFeatures(unittest.TestCase):
    def setUp(self):
        # Create a unique temporary SQLite database for clean test isolation
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.test_db_path = self.temp_file.name
        self.temp_file.close()

        self.store = DataStore(db_path=self.test_db_path)
        self.ai = AIInterpreter()
        self.ai.pending_food_logs.clear()

        # Create two test users to verify multi-user isolation
        self.user_a = "user_alpha_1"
        self.user_b = "user_beta_2"

        self.store.get_or_create_user(
            user_id=self.user_a,
            email="alpha@test.com",
            display_name="Alpha User"
        )
        self.store.get_or_create_user(
            user_id=self.user_b,
            email="beta@test.com",
            display_name="Beta User"
        )

    def tearDown(self):
        self.store.close()
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except OSError:
                pass

    # =========================================================================
    # 1. Multiuser Height & Weight Change Option
    # =========================================================================
    def test_multiuser_vitals_update_and_isolation(self):
        """User A and User B should be able to update height and weight independently without interference."""
        vitals_a = self.store.update_vitals(
            user_id=self.user_a,
            weight_kg=75.5,
            height_cm=180.0,
            target_weight_kg=70.0
        )
        self.assertEqual(vitals_a.weight_kg, 75.5)
        self.assertEqual(vitals_a.height_cm, 180.0)
        self.assertEqual(vitals_a.target_weight_kg, 70.0)

        vitals_b = self.store.update_vitals(
            user_id=self.user_b,
            weight_kg=55.0,
            height_cm=160.0,
            target_weight_kg=52.0
        )
        self.assertEqual(vitals_b.weight_kg, 55.0)
        self.assertEqual(vitals_b.height_cm, 160.0)
        self.assertEqual(vitals_b.target_weight_kg, 52.0)

        dash_a = self.store.get_dashboard(self.user_a)
        self.assertEqual(dash_a.vitals.weight_kg, 75.5)
        self.assertEqual(dash_a.vitals.height_cm, 180.0)
        self.assertEqual(dash_a.vitals.target_weight_kg, 70.0)

        dash_b = self.store.get_dashboard(self.user_b)
        self.assertEqual(dash_b.vitals.weight_kg, 55.0)
        self.assertEqual(dash_b.vitals.height_cm, 160.0)
        self.assertEqual(dash_b.vitals.target_weight_kg, 52.0)

    # =========================================================================
    # 2. Meal Deletion via Chat & Database
    # =========================================================================
    def test_meal_deletion_via_chat_and_db(self):
        """User asking 'remove this meal' or 'delete lunch' should remove meal from DB and dashboard."""
        today_str = get_ist_today_str()

        lunch = MealLog(
            id="meal_lunch_101",
            title="Grilled Chicken Rice",
            meal_type="Lunch",
            total_calories=550,
            protein=45.0,
            carbs=60.0,
            fats=12.0,
            timestamp="1:30 PM",
            date_str=today_str,
            items=[FoodItem(name="Grilled Chicken", quantity=1.0, unit="plate", calories=550, protein=45.0, carbs=60.0, fats=12.0)]
        )
        self.store.add_meal(lunch, user_id=self.user_a)

        dash_before = self.store.get_dashboard(self.user_a)
        self.assertEqual(len(dash_before.meals), 1)
        self.assertEqual(dash_before.calories_consumed, 550)

        current_meals = [m.model_dump() for m in dash_before.meals]
        chat_res = self.ai.process_message(
            "remove this meal please",
            current_meals=current_meals,
            user_id=self.user_a
        )

        self.assertEqual(chat_res.get("type"), "meal_deleted")
        deleted_id = chat_res.get("deleted_meal_id")
        self.assertEqual(deleted_id, lunch.id)

        delete_success = self.store.delete_meal(deleted_id, user_id=self.user_a)
        self.assertTrue(delete_success)

        dash_after = self.store.get_dashboard(self.user_a)
        self.assertEqual(len(dash_after.meals), 0)
        self.assertEqual(dash_after.calories_consumed, 0)

    # =========================================================================
    # 3. AI Category Prompting & Confirmation
    # =========================================================================
    def test_ai_category_prompting_and_confirmation(self):
        """When user logs food without a category, AI prompts for meal category, then logs under chosen meal."""
        msg_1 = self.ai.process_message(
            "I ate 2 whole wheat rotis and paneer butter masala",
            current_meals=[],
            user_id=self.user_a
        )

        self.assertTrue(msg_1.get("meal_prompt"), "AI should return meal_prompt: True")
        self.assertIn("options", msg_1)
        for expected_cat in ["Breakfast", "Lunch", "Snacks", "Cheat Meal", "Dinner"]:
            self.assertIn(expected_cat, msg_1["options"])

        self.assertIn(self.user_a, self.ai.pending_food_logs)
        self.assertNotIn(self.user_b, self.ai.pending_food_logs)

        msg_2 = self.ai.process_message(
            "Cheat Meal",
            current_meals=[],
            user_id=self.user_a
        )

        self.assertIn("meal", msg_2)
        meal = msg_2["meal"]
        self.assertEqual(meal.meal_type, "Cheat Meal")
        self.assertGreater(meal.total_calories, 0)
        self.assertNotIn(self.user_a, self.ai.pending_food_logs)

    def test_ai_category_prompt_cancellation(self):
        """User should be able to cancel pending food log by saying cancel or nevermind."""
        self.ai.process_message("I had a slice of chocolate cake", current_meals=[], user_id=self.user_a)
        self.assertIn(self.user_a, self.ai.pending_food_logs)

        cancel_res = self.ai.process_message("never mind, cancel that", current_meals=[], user_id=self.user_a)
        self.assertNotIn(self.user_a, self.ai.pending_food_logs)
        self.assertIn("cancelled", cancel_res["reply_text"].lower())

    # =========================================================================
    # 4. Day Transition (IST Midnight Rollover) & Daily History
    # =========================================================================
    def test_day_transition_and_history_archival(self):
        """Verify rollover detection following IST and clean daily reset with history archival."""
        yesterday_str = "2026-10-22"
        conn = self.store.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET last_active_date = ? WHERE id = ?", (yesterday_str, self.user_a))
        conn.commit()
        conn.close()

        m1 = MealLog(
            id="meal_yesterday_1",
            title="Oatmeal & Berries",
            meal_type="Breakfast",
            total_calories=350,
            protein=15.0,
            carbs=55.0,
            fats=6.0,
            timestamp="8:00 AM",
            date_str=yesterday_str,
            items=[]
        )
        self.store.add_meal(m1, user_id=self.user_a)

        m2 = MealLog(
            id="meal_yesterday_2",
            title="Salmon Salad",
            meal_type="Dinner",
            total_calories=500,
            protein=40.0,
            carbs=20.0,
            fats=22.0,
            timestamp="8:30 PM",
            date_str=yesterday_str,
            items=[]
        )
        self.store.add_meal(m2, user_id=self.user_a)

        conn = self.store.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET last_active_date = ? WHERE id = ?", (yesterday_str, self.user_a))
        conn.commit()
        conn.close()

        status = self.store.check_day_transition(self.user_a)
        self.assertTrue(status["show_transition"], "Should show transition when today != last_active_date")
        self.assertIsNotNone(status.get("yesterday_summary"))
        summary = status["yesterday_summary"]
        self.assertEqual(summary["date_str"], yesterday_str)
        self.assertEqual(summary["calories"], 850)
        self.assertEqual(summary["protein"], 55.0)
        self.assertEqual(summary["carbs"], 75.0)
        self.assertEqual(summary["fats"], 28.0)
        self.assertEqual(summary["meals_count"], 2)

        fresh_dash = self.store.start_new_day(self.user_a)
        self.assertEqual(fresh_dash.calories_consumed, 0)

        status_after = self.store.check_day_transition(self.user_a)
        self.assertFalse(status_after["show_transition"])

        dash_today = self.store.get_dashboard(self.user_a)
        self.assertEqual(dash_today.calories_consumed, 0)
        self.assertEqual(len(dash_today.meals), 0)

        history = self.store.get_user_history(self.user_a)
        self.assertGreaterEqual(len(history), 1)
        archived_item = next((item for item in history if item["date_str"] == yesterday_str), None)
        self.assertIsNotNone(archived_item)
        self.assertEqual(archived_item["calories"], 850)
        self.assertEqual(archived_item["protein"], 55.0)
        self.assertEqual(archived_item["meals_count"], 2)

    # =========================================================================
    # 5. Heuristic Nutrition Service Fallback (Offline Resilience)
    # =========================================================================
    def test_heuristic_nutrition_fallback(self):
        """NutritionService should provide accurate heuristic nutritional approximations when offline."""
        svc = NutritionService()
        salad = svc._resolve_heuristic_or_estimate("caesar salad", quantity=1.0, unit="bowl")
        self.assertIsNotNone(salad)
        self.assertEqual(salad["calories"], 150)
        self.assertEqual(salad["protein"], 4.0)

        egg = svc._resolve_heuristic_or_estimate("boiled egg", quantity=2.0, unit="egg")
        self.assertIsNotNone(egg)
        self.assertEqual(egg["calories"], 150)
        self.assertEqual(egg["protein"], 12.6)

    # =========================================================================
    # 6. Security: Demo Token Backdoor Guard
    # =========================================================================
    def test_demo_token_disabled_by_default(self):
        """Verify that demo token is rejected when ENABLE_DEMO_AUTH is disabled."""
        from backend.auth import verify_supabase_token
        from fastapi import HTTPException
        with self.assertRaises(HTTPException) as ctx:
            verify_supabase_token("elena-demo-token")
        self.assertEqual(ctx.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()

