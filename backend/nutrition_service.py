import os
import re
import time
import logging
from typing import Dict, Any, Optional
import requests
from dotenv import load_dotenv
from backend.smart_cache import smart_cache

# Ensure environment variables are loaded
load_dotenv()
logger = logging.getLogger("macroly.nutrition")

# Estimator heuristics for unknown foods based on food categories
FOOD_CATEGORY_HEURISTICS = {
    "salad": {"cal": 150, "p": 4.0, "c": 12.0, "f": 8.0, "unit": "bowl"},
    "soup": {"cal": 160, "p": 6.0, "c": 18.0, "f": 6.0, "unit": "bowl"},
    "curry": {"cal": 280, "p": 20.0, "c": 12.0, "f": 14.0, "unit": "bowl"},
    "roti": {"cal": 110, "p": 3.0, "c": 22.0, "f": 1.0, "unit": "piece"},
    "bread": {"cal": 90, "p": 3.0, "c": 16.0, "f": 1.0, "unit": "slice"},
    "rice": {"cal": 205, "p": 4.0, "c": 45.0, "f": 0.5, "unit": "bowl"},
    "shake": {"cal": 200, "p": 25.0, "c": 15.0, "f": 3.0, "unit": "glass"},
    "smoothie": {"cal": 210, "p": 6.0, "c": 40.0, "f": 2.0, "unit": "glass"},
    "pasta": {"cal": 360, "p": 12.0, "c": 60.0, "f": 6.0, "unit": "plate"},
    "pizza": {"cal": 285, "p": 12.0, "c": 36.0, "f": 10.0, "unit": "slice"},
    "burger": {"cal": 450, "p": 22.0, "c": 40.0, "f": 20.0, "unit": "burger"},
    "sandwich": {"cal": 320, "p": 14.0, "c": 32.0, "f": 12.0, "unit": "sandwich"},
    "coffee": {"cal": 30, "p": 1.0, "c": 3.0, "f": 1.0, "unit": "cup"},
    "tea": {"cal": 25, "p": 0.5, "c": 4.0, "f": 0.5, "unit": "cup"},
    "egg": {"cal": 75, "p": 6.3, "c": 0.5, "f": 5.0, "unit": "egg"},
    "fruit": {"cal": 80, "p": 1.0, "c": 20.0, "f": 0.2, "unit": "item"},
    "milk": {"cal": 150, "p": 8.0, "c": 12.0, "f": 8.0, "unit": "glass"},
    "corn pizza": {"cal": 260, "p": 10.0, "c": 32.0, "f": 9.0, "unit": "slice"},
}

class NutritionService:
    def __init__(self):
        self.calorieninjas_api_key = os.getenv("CALORIENINJAS_API_KEY", "").strip()

    def _fetch_calorieninjas(self, food_name: str, quantity: float = 1.0, unit: str = "serving") -> Optional[Dict[str, Any]]:
        """Queries CalorieNinjas API and parses nutritional macros."""
        api_key = self.calorieninjas_api_key or os.getenv("CALORIENINJAS_API_KEY", "").strip()
        if not api_key:
            return None

        try:
            clean_unit = (unit or "serving").lower().strip()
            # If unit is metric ml (e.g. 250ml), convert to grams for CalorieNinjas (e.g. 250g)
            if "ml" in clean_unit:
                m_ml = re.search(r'(\d+(?:\.\d+)?)', clean_unit)
                if m_ml:
                    total_g = float(m_ml.group(1)) * quantity
                    query = f"{int(total_g) if total_g.is_integer() else total_g}g {food_name}"
                else:
                    query = f"{quantity} glass {food_name}"
            elif clean_unit in ["serving", "item", ""]:
                qty_str = f"{int(quantity) if quantity.is_integer() else quantity}"
                query = f"{qty_str} {food_name}"
            else:
                qty_str = f"{int(quantity) if quantity.is_integer() else quantity}"
                query = f"{qty_str} {clean_unit} {food_name}"

            api_url = "https://api.calorieninjas.com/v1/nutrition"
            headers = {"X-Api-Key": api_key}
            resp = requests.get(api_url, headers=headers, params={"query": query}, timeout=8)
            if resp.status_code != 200:
                logger.warning("CalorieNinjas API query returned HTTP %s for '%s'", resp.status_code, query)
                return None

            data = resp.json()
            items = data.get("items", [])
            # Fallback to plain food_name query if compound query returned 0 items
            if not items and query != food_name:
                resp_plain = requests.get(api_url, headers=headers, params={"query": food_name}, timeout=8)
                if resp_plain.status_code == 200:
                    data = resp_plain.json()
                    items = data.get("items", [])

            if not items:
                logger.info("CalorieNinjas returned 0 results for '%s'", query)
                return None

            tot_cal = sum(float(i.get("calories", 0.0)) for i in items)
            tot_p = sum(float(i.get("protein_g", 0.0)) for i in items)
            tot_c = sum(float(i.get("carbohydrates_total_g", 0.0)) for i in items)
            tot_f = sum(float(i.get("fat_total_g", 0.0)) for i in items)

            return {
                "name": food_name.title(),
                "quantity": quantity,
                "unit": unit or "serving",
                "calories": int(round(tot_cal)),
                "protein": round(tot_p, 1),
                "carbs": round(tot_c, 1),
                "fats": round(tot_f, 1),
                "cached": False,
                "source": "CalorieNinjas API"
            }
        except Exception as e:
            logger.warning("Exception during CalorieNinjas API call for '%s': %s", food_name, e)
            return None

    def _resolve_heuristic_or_estimate(self, food_name: str, quantity: float, unit: str) -> Dict[str, Any]:
        """Heuristic and sensible baseline fallback catalog."""
        cleaned = food_name.lower().strip()
        matched_cat = None
        for cat in FOOD_CATEGORY_HEURISTICS:
            if cat in cleaned:
                matched_cat = cat
                break

        if matched_cat:
            profile = FOOD_CATEGORY_HEURISTICS[matched_cat]
            return {
                "name": food_name.title(),
                "quantity": quantity,
                "unit": unit or profile["unit"],
                "calories": int(round(profile["cal"] * quantity)),
                "protein": round(profile["p"] * quantity, 1),
                "carbs": round(profile["c"] * quantity, 1),
                "fats": round(profile["f"] * quantity, 1),
                "cached": False,
                "source": "Smart Heuristic Catalog"
            }

        # Generic sensible baseline for unlisted food
        cal = int(round(180 * quantity))
        p = round(8.0 * quantity, 1)
        c = round(22.0 * quantity, 1)
        f = round(6.0 * quantity, 1)
        return {
            "name": food_name.title(),
            "quantity": quantity,
            "unit": unit or "serving",
            "calories": cal,
            "protein": p,
            "carbs": c,
            "fats": f,
            "cached": False,
            "source": "General Estimator"
        }

    def get_nutrition(self, food_name: str, quantity: float = 1.0, unit: str = "serving") -> Dict[str, Any]:
        """
        1. Check local Smart Cache first.
        2. If missed, query live CalorieNinjas API.
        3. If CalorieNinjas fails/misses, fallback to heuristic catalog.
        4. Save resolved nutrition to Smart Cache for instant future lookups.
        """
        # Step 1: Check smart_cache
        cached = smart_cache.lookup(food_name, quantity, unit)
        if cached:
            logger.info("🟢 [CACHE HIT] '%s' (qty: %s %s) -> %d kcal, %sg P, %sg C, %sg F",
                        food_name, quantity, unit, cached["calories"], cached["protein"], cached["carbs"], cached["fats"])
            cached["source"] = "Smart Cache"
            return cached

        # Step 2: Attempt live CalorieNinjas API
        nutrition = self._fetch_calorieninjas(food_name, quantity, unit)
        if nutrition:
            logger.info("🔵 [CALORIENINJAS API] '%s' (qty: %s %s) -> %d kcal, %sg P, %sg C, %sg F",
                        food_name, quantity, unit, nutrition["calories"], nutrition["protein"], nutrition["carbs"], nutrition["fats"])
        else:
            # Step 3: Heuristic / Estimator Fallback
            nutrition = self._resolve_heuristic_or_estimate(food_name, quantity, unit)
            logger.info("🟡 [HEURISTIC FALLBACK] '%s' (qty: %s %s) -> %d kcal, %sg P, %sg C, %sg F via %s",
                        food_name, quantity, unit, nutrition["calories"], nutrition["protein"], nutrition["carbs"], nutrition["fats"],
                        nutrition.get("source"))

        # Step 4: Persist to Smart Cache for instant future lookups
        try:
            smart_cache.save(
                name=food_name,
                quantity=quantity,
                unit=unit or nutrition.get("unit", "serving"),
                calories=nutrition["calories"],
                protein=nutrition["protein"],
                carbs=nutrition["carbs"],
                fats=nutrition["fats"],
                tags=nutrition.get("source", "auto-resolved")
            )
        except Exception as e:
            logger.warning("Could not persist '%s' to smart_cache: %s", food_name, e)

        return nutrition

nutrition_service = NutritionService()
