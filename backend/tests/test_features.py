"""
Unit Tests for Macroly v1.1 Bug Fixes & Feature Enhancements
Covers:
1. Multi-user height and weight change (isolation & persistence)
2. Meal deletion via chat and direct API
3. Non-hardcoded meal classification prompting (Breakfast, Lunch, Snacks, Cheat Meal, Dinner)
4. IST Midnight rollover, Day Transition pop-up, and Daily History records
5. Edge cases and validations
"""

import os
import sys
import unittest

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models import UpdateVitalsRequest, MealLog, FoodItem
from database import DataStore, get_ist_today_str, get_ist_now
from ai_interpreter import AIInterpreter, VALID_MEAL_TYPES


class TestMacrolyFeatures(unittest.TestCase):
    def setUp(self):
        # Use an in-memory/isolated SQLite DB for clean testing
        self.test_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_temp.db"))
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except OSError:
                pass

        self.store = DataStore(db_path=self.test_db_path)
        self.ai = AIInterpreter()
        # Clear any pending food logs
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
        # Update User A's vitals
        vitals_a = self.store.update_vitals(
            user_id=self.user_a,
            weight_kg=75.5,
            height_cm=180.0,
            target_weight_kg=70.0
        )
        self.assertEqual(vitals_a.weight_kg, 75.5)
        self.assertEqual(vitals_a.height_cm, 180.0)
        self.assertEqual(vitals_a.target_weight_kg, 70.0)

        # Update User B's vitals
        vitals_b = self.store.update_vitals(
            user_id=self.user_b,
            weight_kg=55.0,
            height_cm=160.0,
            target_weight_kg=52.0
        )
        self.assertEqual(vitals_b.weight_kg, 55.0)
        self.assertEqual(vitals_b.height_cm, 160.0)
        self.assertEqual(vitals_b.target_weight_kg, 52.0)

        # Verify User A's vitals remain isolated and intact
        dash_a = self.store.get_dashboard(self.user_a)
        self.assertEqual(dash_a.vitals.weight_kg, 75.5)
        self.assertEqual(dash_a.vitals.height_cm, 180.0)
        self.assertEqual(dash_a.vitals.target_weight_kg, 70.0)

        # Verify User B's vitals remain isolated
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

        # Add a lunch meal to User A
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

        # Dashboard should have 1 meal and 550 calories
        dash_before = self.store.get_dashboard(self.user_a)
        self.assertEqual(len(dash_before.meals), 1)
        self.assertEqual(dash_before.calories_consumed, 550)

        # Process chat message asking to delete the meal
        current_meals = [m.model_dump() for m in dash_before.meals]
        chat_res = self.ai.process_message(
            "remove this meal please",
            current_meals=current_meals,
            user_id=self.user_a
        )

        self.assertEqual(chat_res.get("type"), "meal_deleted")
        deleted_id = chat_res.get("deleted_meal_id")
        self.assertEqual(deleted_id, lunch.id)

        # Execute DB deletion as main.py does
        delete_success = self.store.delete_meal(deleted_id, user_id=self.user_a)
        self.assertTrue(delete_success)

        # Dashboard should now be empty and calories should be 0
        dash_after = self.store.get_dashboard(self.user_a)
        self.assertEqual(len(dash_after.meals), 0)
        self.assertEqual(dash_after.calories_consumed, 0)

    # =========================================================================
    # 3. AI Category Prompting (Breakfast, Lunch, Snacks, Cheat Meal, Dinner)
    # =========================================================================
    def test_ai_category_prompting_and_confirmation(self):
        """When user logs food without a category, AI prompts for meal category, then logs under chosen meal."""
        # 1. User says what they ate without stating meal category
        msg_1 = self.ai.process_message(
            "I ate 2 whole wheat rotis and paneer butter masala",
            current_meals=[],
            user_id=self.user_a
        )

        # AI should prompt user to select a category
        self.assertTrue(msg_1.get("meal_prompt"), "AI should return meal_prompt: True")
        self.assertIn("options", msg_1)
        for expected_cat in ["Breakfast", "Lunch", "Snacks", "Cheat Meal", "Dinner"]:
            self.assertIn(expected_cat, msg_1["options"])

        # Verify pending food log is stored for User A, but not User B (isolation)
        self.assertIn(self.user_a, self.ai.pending_food_logs)
        self.assertNotIn(self.user_b, self.ai.pending_food_logs)

        # 2. User confirms with "Cheat Meal"
        msg_2 = self.ai.process_message(
            "Cheat Meal",
            current_meals=[],
            user_id=self.user_a
        )

        # AI should have logged the meal under "Cheat Meal"
        self.assertIn("meal", msg_2)
        meal = msg_2["meal"]
        self.assertEqual(meal.meal_type, "Cheat Meal")
        self.assertGreater(meal.total_calories, 0)

        # Pending food log should be cleared
        self.assertNotIn(self.user_a, self.ai.pending_food_logs)

    def test_ai_category_prompt_cancellation(self):
        """User should be able to cancel pending food log by saying cancel or nevermind."""
        self.ai.process_message("I had a slice of chocolate cake", current_meals=[], user_id=self.user_a)
        self.assertIn(self.user_a, self.ai.pending_food_logs)

        # User cancels
        cancel_res = self.ai.process_message("never mind, cancel that", current_meals=[], user_id=self.user_a)
        self.assertNotIn(self.user_a, self.ai.pending_food_logs)
        self.assertIn("cancelled", cancel_res["reply_text"].lower())

    # =========================================================================
    # 4. Day Transition (IST Midnight Rollover) & Daily History
    # =========================================================================
    def test_day_transition_and_history_archival(self):
        """Verify rollover detection following IST and clean daily reset with history archival."""
        today_ist = get_ist_today_str()

        # Simulate user last active yesterday
        yesterday_str = "2026-10-22"
        conn = self.store.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET last_active_date = ? WHERE id = ?", (yesterday_str, self.user_a))
        conn.commit()
        conn.close()

        # Log some meals for yesterday
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

        # Re-set user last_active_date back to yesterday because add_meal updates it to today if not cautious
        conn = self.store.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET last_active_date = ? WHERE id = ?", (yesterday_str, self.user_a))
        conn.commit()
        conn.close()

        # 1. Check Day Transition status
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

        # 2. User clicks 'Start New Day'
        fresh_dash = self.store.start_new_day(self.user_a)
        self.assertEqual(fresh_dash.calories_consumed, 0)

        # 3. Transition check should now return False
        status_after = self.store.check_day_transition(self.user_a)
        self.assertFalse(status_after["show_transition"])

        # 4. Today's dashboard should be empty (0 calories consumed)
        dash_today = self.store.get_dashboard(self.user_a)
        self.assertEqual(dash_today.calories_consumed, 0)
        self.assertEqual(len(dash_today.meals), 0)

        # 5. History should contain yesterday's archived intake
        history = self.store.get_user_history(self.user_a)
        self.assertGreaterEqual(len(history), 1)
        archived_item = next((item for item in history if item["date_str"] == yesterday_str), None)
        self.assertIsNotNone(archived_item)
        self.assertEqual(archived_item["calories"], 850)
        self.assertEqual(archived_item["protein"], 55.0)
        self.assertEqual(archived_item["meals_count"], 2)


if __name__ == "__main__":
    unittest.main()
