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
}

class NutritionService:
    def __init__(self):
        self.fatsecret_client_id = os.getenv("FATSECRET_CLIENT_ID", "").strip()
        self.fatsecret_client_secret = os.getenv("FATSECRET_CLIENT_SECRET", "").strip()
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0.0

    def _get_access_token(self) -> Optional[str]:
        """Obtains or reuses an OAuth2 client credentials token from FatSecret."""
        if not self.fatsecret_client_id or not self.fatsecret_client_secret:
            return None

        # Return valid cached token if available
        if self._access_token and time.time() < (self._token_expires_at - 60):
            return self._access_token

        try:
            token_url = "https://oauth.fatsecret.com/connect/token"
            resp = requests.post(
                token_url,
                auth=(self.fatsecret_client_id, self.fatsecret_client_secret),
                data={"grant_type": "client_credentials", "scope": "basic"},
                timeout=8
            )
            if resp.status_code == 200:
                data = resp.json()
                self._access_token = data.get("access_token")
                expires_in = data.get("expires_in", 86400)
                self._token_expires_at = time.time() + expires_in
                return self._access_token
            else:
                logger.warning("FatSecret OAuth token request failed (HTTP %s): %s", resp.status_code, resp.text)
                return None
        except Exception as e:
            logger.warning("FatSecret OAuth token network error: %s", e)
            return None

    def _fetch_fatsecret(self, food_name: str, quantity: float = 1.0, unit: str = "serving") -> Optional[Dict[str, Any]]:
        """Queries FatSecret foods.search endpoint and parses nutritional macros."""
        token = self._get_access_token()
        if not token:
            return None

        try:
            api_url = "https://platform.fatsecret.com/rest/server.api"
            headers = {"Authorization": f"Bearer {token}"}
            params = {
                "method": "foods.search",
                "search_expression": food_name,
                "format": "json"
            }
            resp = requests.post(api_url, headers=headers, data=params, timeout=8)
            if resp.status_code != 200:
                logger.warning("FatSecret API query returned HTTP %s for '%s'", resp.status_code, food_name)
                return None

            data = resp.json()
            if "error" in data:
                err = data["error"]
                logger.warning("FatSecret API error for '%s': %s (code %s)", food_name, err.get("message"), err.get("code"))
                return None

            foods = data.get("foods", {}).get("food", [])
            if isinstance(foods, dict):
                foods = [foods]
            if not foods:
                logger.info("FatSecret returned 0 results for '%s'", food_name)
                return None

            # Find best match: prioritize exact name match, otherwise take the first sensible result
            chosen = foods[0]
            clean_input = food_name.lower().strip()
            for f in foods:
                if f.get("food_name", "").lower().strip() == clean_input:
                    # Prefer standard portions if available
                    desc = f.get("food_description", "")
                    cal_m = re.search(r"Calories:\s*([0-9.]+)", desc, re.I)
                    if cal_m and float(cal_m.group(1)) < 1500:
                        chosen = f
                        break

            desc = chosen.get("food_description", "")
            cal_m = re.search(r"Calories:\s*([0-9.]+)", desc, re.I)
            fat_m = re.search(r"Fat:\s*([0-9.]+)g?", desc, re.I)
            carb_m = re.search(r"Carbs:\s*([0-9.]+)g?", desc, re.I)
            prot_m = re.search(r"Protein:\s*([0-9.]+)g?", desc, re.I)
            serv_m = re.search(r"Per\s+([^-|]+)", desc, re.I)

            if not cal_m:
                logger.warning("Unable to parse calories from FatSecret description: %s", desc)
                return None

            base_cal = float(cal_m.group(1))
            base_fat = float(fat_m.group(1)) if fat_m else 0.0
            base_carbs = float(carb_m.group(1)) if carb_m else 0.0
            base_protein = float(prot_m.group(1)) if prot_m else 0.0
            parsed_serving = serv_m.group(1).strip() if serv_m else "serving"

            return {
                "name": chosen.get("food_name", food_name).title(),
                "quantity": quantity,
                "unit": unit or parsed_serving,
                "calories": int(round(base_cal * quantity)),
                "protein": round(base_protein * quantity, 1),
                "carbs": round(base_carbs * quantity, 1),
                "fats": round(base_fat * quantity, 1),
                "cached": False,
                "source": "FatSecret API",
                "raw_description": desc,
                "brand": chosen.get("brand_name")
            }
        except Exception as e:
            logger.warning("Exception during FatSecret API call for '%s': %s", food_name, e)
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
        2. If missed, query live FatSecret API.
        3. If FatSecret fails/misses, fallback to heuristic catalog.
        4. Save resolved nutrition to Smart Cache for instant future lookups.
        """
        # Step 1: Check smart_cache
        cached = smart_cache.lookup(food_name, quantity, unit)
        if cached:
            logger.info("🟢 [CACHE HIT] '%s' (qty: %s %s) -> %d kcal, %sg P, %sg C, %sg F",
                        food_name, quantity, unit, cached["calories"], cached["protein"], cached["carbs"], cached["fats"])
            cached["source"] = "Smart Cache"
            return cached

        # Step 2: Attempt live FatSecret API
        nutrition = self._fetch_fatsecret(food_name, quantity, unit)
        if nutrition:
            logger.info("🔵 [FATSECRET API] '%s' (qty: %s %s) -> %d kcal, %sg P, %sg C, %sg F (serving: %s, raw: %s)",
                        food_name, quantity, unit, nutrition["calories"], nutrition["protein"], nutrition["carbs"], nutrition["fats"],
                        nutrition["unit"], nutrition.get("raw_description"))
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
