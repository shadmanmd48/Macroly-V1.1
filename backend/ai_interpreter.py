import os
import re
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv
from backend.models import FoodItem, MealLog, ChatMessage, WorkoutLog
from backend.nutrition_service import nutrition_service

# Ensure environment variables are loaded
load_dotenv(override=False)

logger = logging.getLogger("macroly.ai_interpreter")

NUMBER_WORDS = {
    "a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "half": 0.5, "quarter": 0.25, "couple": 2, "few": 3
}

UNIT_WORDS = [
    "bowl", "bowls", "cup", "cups", "slice", "slices", "glass", "glasses",
    "plate", "plates", "piece", "pieces", "roti", "rotis", "egg", "eggs",
    "scoop", "scoops", "tbsp", "tablespoon", "tsp", "handful", "parfait", "serving", "servings",
    "gram", "grams", "g", "ml", "oz"
]

CONVERSATIONAL_NOISE = [
    "along with", "finished with", "savory", "delicious", "indulged in", "indulged",
    "craving", "craved", "devoured", "grabbed", "side of", "followed by", "bunch of",
    "couple of", "plateful of", "taste of", "order of", "serving of", "snacked on",
    "approx", "approximately", "roughly", "around"
]

INTENT_FOOD_LOG = "food_log"
INTENT_CORRECTION = "correction"
INTENT_WORKOUT_LOG = "workout_log"
INTENT_WATER_LOG = "water_log"
INTENT_DELETION = "deletion"
INTENT_NOT_FOOD_RELATED = "not_food_related"

EDIBLE_FOOD_KEYWORDS = {
    "roti", "rotis", "chapati", "chapatis", "rice", "dal", "curry", "chicken", "paneer",
    "egg", "eggs", "toast", "bread", "avocado", "salad", "bowl", "soup", "pasta",
    "pizza", "burger", "sandwich", "coffee", "latte", "tea", "milk", "shake", "smoothie",
    "apple", "apples", "banana", "bananas", "orange", "oranges", "berries", "berry", "fruit", "fruits",
    "oat", "oats", "oatmeal", "yogurt", "parfait", "granola", "almond", "almonds",
    "peanut", "peanuts", "butter", "cheese", "tofu", "fish", "salmon", "tuna", "steak",
    "meat", "beef", "mutton", "lamb", "cookie", "cookies", "biscuit", "biscuits", "chocolate",
    "cake", "biryani", "dosa", "idli", "samosa", "muffin", "chips", "nuts", "water", "juice",
    "whey", "veggie", "vegetable", "vegetables", "pancake", "pancakes", "waffle", "waffles"
}

FOOD_ACTION_VERBS = {
    "ate", "eat", "eating", "had", "have", "having", "drank", "drink", "drinking",
    "consumed", "consuming", "logged", "logging", "snacked", "devoured", "ordered"
}

VALID_MEAL_TYPES = ["Breakfast", "Lunch", "Snacks", "Cheat Meal", "Dinner"]

def extract_explicit_meal_type(text: str) -> Optional[str]:
    """Checks if text already contains an explicit category reference."""
    text_lower = text.lower()
    if re.search(r'\bcheat\s*meal\b', text_lower):
        return "Cheat Meal"
    elif re.search(r'\bbreakfast\b', text_lower):
        return "Breakfast"
    elif re.search(r'\blunch\b', text_lower):
        return "Lunch"
    elif re.search(r'\b(?:snacks?)\b', text_lower):
        return "Snacks"
    elif re.search(r'\bdinner\b', text_lower):
        return "Dinner"
    return None

def is_category_selection(text: str) -> Optional[str]:
    """Matches standalone category selections like 'Breakfast', '🌅 Breakfast', 'For Lunch', 'Cheat meal'."""
    clean = re.sub(r'^[^\w\s]+', '', text.strip()).strip()
    clean_lower = clean.lower()
    clean_lower = re.sub(r'^(?:log\s+for|for|its|it\s+is|mark\s+as|set\s+to|into)\s+', '', clean_lower).strip()
    clean_lower = re.sub(r'[\!\.\?]', '', clean_lower).strip()
    if clean_lower in ["cheat meal", "cheat", "cheatmeal"]:
        return "Cheat Meal"
    elif clean_lower in ["breakfast", "brkfast"]:
        return "Breakfast"
    elif clean_lower in ["lunch"]:
        return "Lunch"
    elif clean_lower in ["snack", "snacks", "evening snack", "morning snack"]:
        return "Snacks"
    elif clean_lower in ["dinner", "supper"]:
        return "Dinner"
    return None

class AIInterpreter:
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
        self.last_meal: Optional[MealLog] = None
        self.conversation_context: Dict[str, Any] = {}
        # Multi-user isolated pending food logs waiting for category selection
        self.pending_food_logs: Dict[str, Dict[str, Any]] = {}

    def classify_intent(self, user_text: str, current_meals: Optional[List[MealLog]] = None) -> str:
        """
        Fast, cheap heuristic classification step before food extraction runs.
        Classifies into one of:
          - 'deletion'
          - 'correction'
          - 'workout_log'
          - 'not_food_related'
          - 'food_log'
        """
        text_clean = user_text.strip()
        text_lower = text_clean.lower()

        # 1. Obvious Deletion Heuristic (e.g. "remove this meal", "delete my lunch", "remove dal", "delete chicken", "drop the salad")
        if re.search(r'\b(?:remove|delete|drop|cancel|clear)\b', text_lower):
            if not any(fw in text_lower for fw in ["workout", "goal", "calorie target"]):
                return INTENT_DELETION

        # 2. Obvious Correction Heuristic (e.g. "make that 3 rotis", "actually 2 eggs", "change to 4 rotis")
        clean_punc = re.sub(r'[\!\.\?]', '', text_lower)
        if re.search(r'\b(?:make\s+that|make\s+it|change\s+to|actually|have)\s+(\d+|[a-z]+)\s+(.+)', clean_punc):
            return INTENT_CORRECTION

        # 3. Obvious Workout Log Heuristic (e.g. "ran for 30 mins", "gym for 45 mins", "walked 1 hour")
        workout_keywords = [
            "ran", "run", "running", "jog", "jogging", "walk", "walking", "walked",
            "workout", "gym", "cycling", "cycle", "swimming", "swim", "treadmill",
            "elliptical", "pilates", "yoga", "weightlifting", "pushups", "cardio"
        ]
        if any(re.search(rf'\b{re.escape(k)}\b', text_lower) for k in workout_keywords):
            # Ensure it's not a food item that happens to contain workout keywords
            if not any(fw in text_lower for fw in ["egg", "bakery", "bread", "milk", "coffee", "roti", "curry"]):
                return INTENT_WORKOUT_LOG

        # 3b. Obvious Hydration / Water Log Heuristic (e.g. "drank 500ml of water", "had 2 glasses of water")
        if re.search(r'\b(?:water|hydration)\b', text_lower):
            if not any(fw in text_lower for fw in ["watermelon", "water chestnut", "water spinach", "watercress"]):
                if any(verb in text_lower for verb in ["drank", "drink", "drinking", "had", "have", "logged", "log", "glass", "glasses", "bottle", "bottles", "ml", "liters", "litres", "liter", "litre", "sip", "sipped"]):
                    other_food = any(fw in text_lower for fw in EDIBLE_FOOD_KEYWORDS if fw not in ["water"])
                    if not other_food:
                        return INTENT_WATER_LOG

        # 4. Obvious Not-Food-Related Heuristics (greetings, small talk, gratitude, goal questions, general chatter)
        if self._is_not_food_related(text_clean):
            return INTENT_NOT_FOOD_RELATED

        # 5. Default candidate: food_log (falls through to Rule-Based and Groq parser)
        return INTENT_FOOD_LOG

    def _is_not_food_related(self, text: str) -> bool:
        """
        Fast heuristic checks for greetings, small talk, gratitude, goal/nutrition queries,
        and general non-food questions/statements.
        """
        clean_text = text.strip()
        text_lower = clean_text.lower()
        clean_punc = re.sub(r'[\!\.\?\,\;]', ' ', text_lower)
        words = clean_punc.split()

        # 1. Greetings (e.g. "hi", "hello", "hey", "good morning")
        greeting_words = {"hi", "hello", "hey", "hiya", "howdy", "yo", "greetings"}
        if words and words[0] in greeting_words and len(words) <= 3:
            return True
        if re.search(r'^(?:good\s+(?:morning|afternoon|evening|night|day))\b', text_lower):
            return True

        # 2. Small talk & pleasantries (e.g. "how are you", "what's up", "who are you")
        if re.search(r'\b(?:how\s+(?:are\s+you|are\s+u|is\s+it\s+going|r\s+u|do\s+you\s+do)|what(?:\'s|\s+is)\s+up|sup)\b', text_lower):
            return True
        if re.search(r'\b(?:who\s+(?:are\s+you|made\s+you)|what\s+are\s+you|what\s+can\s+you\s+do|tell\s+me\s+about\s+yourself|what\s+is\s+your\s+name|help\s+me)\b', text_lower):
            return True

        # 3. Gratitude & acknowledgments (e.g. "thanks!", "thank you", "appreciate it")
        if re.search(r'^(?:thanks|thank\s+you|thx|ty|thanks\s+a\s+lot|thank\s+you\s+so\s+much|much\s+appreciated|appreciate\s+it|ok|okay|cool|great|awesome|bye|goodbye)\b', text_lower):
            return True

        # 4. Nutrition / Calorie / Macro goal questions with no food nouns
        if re.search(r'\b(?:what(?:\'s|\s+is)?\s+(?:my|the)\s+(?:daily\s+)?(?:calorie|cal|macro|protein|carb|fat)?\s*(?:goal|target|budget|limit|allowance))\b', text_lower):
            return True
        if re.search(r'\b(?:how\s+many\s+calories\s+(?:can\s+i|do\s+i|should\s+i|am\s+i\s+allowed|left|remaining))\b', text_lower):
            return True
        if re.search(r'\b(?:calorie\s+goal|macro\s+targets?|daily\s+calories?)\b', text_lower):
            return True

        # 5. Question check: Starts with question word or ends with '?' and contains NO food keywords or units
        is_question = clean_text.endswith('?') or (words and words[0] in {"what", "why", "how", "when", "where", "who", "is", "are", "can", "could", "would", "should", "tell"})
        has_food_keyword = any(fw in text_lower for fw in EDIBLE_FOOD_KEYWORDS)
        has_unit = any(uw in words for uw in UNIT_WORDS)
        has_number = any(re.search(r'\d', w) or w in NUMBER_WORDS for w in words)
        has_action = any(av in words for av in FOOD_ACTION_VERBS)

        if is_question and not has_food_keyword and not has_unit:
            return True

        # 6. Sentence with zero food words, zero numbers, zero food units, and zero food consumption verbs
        if not has_food_keyword and not has_unit and not has_number and not has_action:
            return True

        return False

    def process_message(
        self,
        user_text: str,
        current_meals: List[MealLog],
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main decision maker:
        1. Checks if user is canceling a pending category prompt.
        2. Checks if user is selecting a meal category for pending food.
        3. Runs fast intent classification:
           - 'deletion'
           - 'correction'
           - 'workout_log'
           - 'not_food_related'
           - 'food_log'
        """
        if user_id:
            context = context or {}
            context["user_id"] = user_id
        user_id = (context or {}).get("user_id") or "default"
        clean_text = user_text.strip()
        text_lower = clean_text.lower()

        # 1. Cancel pending food log
        if re.search(r'\b(?:cancel|never\s*mind|clear|abort|stop|don\'?t\s+log)\b', text_lower) and user_id in self.pending_food_logs:
            self.pending_food_logs.pop(user_id, None)
            return {
                "intent": INTENT_NOT_FOOD_RELATED,
                "type": "not_food_related",
                "reply_text": "Cancelled! What else would you like to log or ask?"
            }

        # 2. Category selection for pending food log
        selected_type = (context or {}).get("selected_meal_type") or is_category_selection(clean_text)
        if selected_type and user_id in self.pending_food_logs:
            pending = self.pending_food_logs.pop(user_id)
            items = pending["items"]
            return self._create_meal_from_items(items, selected_type, pending.get("text", user_text), context)

        intent = self.classify_intent(user_text, current_meals)
        logger.info("🎯 [INTENT] Classified message as: '%s' -> %s (user: %s)", user_text, intent, user_id)

        if intent == INTENT_NOT_FOOD_RELATED:
            return self._handle_not_food_related(user_text, context)
        elif intent == INTENT_DELETION:
            return self._handle_deletion(user_text, current_meals)
        elif intent == INTENT_CORRECTION:
            return self._handle_correction(user_text, current_meals)
        elif intent == INTENT_WORKOUT_LOG:
            return self._handle_workout(user_text)
        elif intent == INTENT_WATER_LOG:
            return self._handle_water(user_text)
        else:  # INTENT_FOOD_LOG
            return self._handle_food_log(user_text, context)

    def _handle_not_food_related(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generates a natural, conversational reply when no food is being logged.
        Never logs or saves meals to the database.
        """
        text_lower = text.lower().strip()
        clean_punc = re.sub(r'[\!\.\?]', '', text_lower).strip()

        # 1. Goal / Target question (e.g. "what's my calorie goal today?")
        if any(w in text_lower for w in ["goal", "target", "allowance", "budget", "calories left", "how many calories"]):
            cal_goal = (context or {}).get("calorie_target", 2200)
            protein_goal = (context or {}).get("protein_target", 140)
            return {
                "intent": INTENT_NOT_FOOD_RELATED,
                "type": "not_food_related",
                "reply_text": f"Your daily calorie goal is {cal_goal:,} kcal (with {int(protein_goal)}g protein)! What did you eat today that you'd like to log?"
            }

        # 2. Greeting (e.g. "hi", "hello", "hey", "good morning")
        greeting_tokens = ["hi", "hello", "hey", "hiya", "howdy", "good morning", "good afternoon", "good evening", "yo"]
        if any(clean_punc == g or clean_punc.startswith(g + " ") for g in greeting_tokens):
            return {
                "intent": INTENT_NOT_FOOD_RELATED,
                "type": "not_food_related",
                "reply_text": "Hello! I'm Macroly, your AI nutrition assistant. What did you have to eat or drink today?"
            }

        # 3. Small talk (e.g. "how are you", "how's it going")
        if any(st in text_lower for st in ["how are you", "how're you", "how are u", "how r u", "how's it going", "how is it going", "what's up", "whats up"]):
            return {
                "intent": INTENT_NOT_FOOD_RELATED,
                "type": "not_food_related",
                "reply_text": "I'm doing great, thank you! Ready to track your macros. What did you eat today?"
            }

        # 4. Gratitude (e.g. "thanks", "thanks!", "thank you")
        if any(clean_punc == gr or clean_punc.startswith(gr + " ") for gr in ["thanks", "thank you", "thx", "ty", "appreciate it", "thanks a lot"]):
            return {
                "intent": INTENT_NOT_FOOD_RELATED,
                "type": "not_food_related",
                "reply_text": "You're very welcome! Let me know whenever you're ready to log your next meal."
            }

        # 5. App / Capabilities question
        if any(w in text_lower for w in ["what can you do", "who are you", "what are you", "help me", "how does this work"]):
            return {
                "intent": INTENT_NOT_FOOD_RELATED,
                "type": "not_food_related",
                "reply_text": "I'm Macroly AI! You can tell me what you ate in natural language (e.g., 'Had 2 rotis with dal'), choose a meal category (Breakfast, Lunch, Snacks, Cheat Meal, Dinner), delete meals ('remove this meal'), or log workouts ('ran for 30 mins'). What did you have today?"
            }

        # 6. General conversational fallback
        return {
            "intent": INTENT_NOT_FOOD_RELATED,
            "type": "not_food_related",
            "reply_text": "I'm just here to help you track your meals! What did you eat?"
        }

    def _handle_deletion(self, text: str, current_meals: List[MealLog]) -> Dict[str, Any]:
        """
        Handles deletion of entire meals or specific items from meals.
        Supports:
          - 'remove this meal', 'delete this meal', 'delete meal', 'remove last meal', 'delete that meal'
          - 'delete my breakfast', 'remove lunch', 'delete dinner', 'remove snacks', 'delete cheat meal'
          - 'remove [food_name]'
        """
        text_lower = text.lower().strip()
        if not current_meals:
            return {
                "intent": INTENT_DELETION,
                "type": "deletion",
                "reply_text": "I couldn't find any logged meals to remove today. What did you eat?",
                "meal": None
            }

        # 1. Whole meal deletion heuristics:
        # e.g., "remove this meal", "delete this meal", "delete meal", "remove meal", "remove last meal", "delete last meal", "delete that meal", "remove it"
        is_whole_meal = bool(
            re.search(r'\b(?:remove|delete|drop|cancel|clear)\s+(?:this|that|the|my|last)?\s*(?:entire\s+)?meal\b', text_lower) or
            re.search(r'^(?:remove|delete|cancel|clear|drop)\s+(?:this|that|last|it)\b', text_lower)
        )

        # Category-specific deletion: e.g. "delete my breakfast", "remove lunch", "delete dinner", "remove snacks", "delete cheat meal"
        cat_match = re.search(r'\b(?:remove|delete|clear|drop|cancel)\s+(?:the\s+|my\s+)?(breakfast|lunch|dinner|snacks?|cheat\s*meal)\b', text_lower)

        def _get_m(obj, prop, default=""):
            if hasattr(obj, prop):
                return getattr(obj, prop)
            if isinstance(obj, dict):
                return obj.get(prop, default)
            return default

        if is_whole_meal or cat_match:
            target_meal = None
            if cat_match:
                cat_term = cat_match.group(1).lower().replace(" ", "").rstrip("s")
                for m in reversed(current_meals):
                    m_type = _get_m(m, "meal_type", "").lower().replace(" ", "").rstrip("s")
                    if cat_term in m_type:
                        target_meal = m
                        break
            if not target_meal:
                target_meal = current_meals[-1]

            t_id = _get_m(target_meal, "id", "")
            t_title = _get_m(target_meal, "title", "Custom Meal")
            t_type = _get_m(target_meal, "meal_type", "Meal")
            t_cals = _get_m(target_meal, "total_calories", 0)

            logger.info("🗑️ [DELETION: Whole Meal] Deleting meal: %s (%s)", t_title, t_id)
            return {
                "intent": INTENT_DELETION,
                "type": "meal_deleted",
                "deleted_meal_id": t_id,
                "deleted_meal_title": t_title,
                "reply_text": f"Removed '{t_title}' ({t_type}, {t_cals} kcal) from your log."
            }

        # 2. Food name deletion
        remove_match = re.search(r'(?:remove|delete|drop|cancel|clear)\s+(?:the\s+)?([a-zA-Z\s]+)', text_lower)
        if remove_match:
            target_term = remove_match.group(1).strip()
            # If target_term refers to a meal itself (e.g. "remove avocado toast")
            for m in reversed(current_meals):
                m_title = _get_m(m, "title", "")
                m_id = _get_m(m, "id", "")
                m_type = _get_m(m, "meal_type", "Meal")
                m_cals = _get_m(m, "total_calories", 0)
                if target_term in m_title.lower() or m_title.lower() in target_term:
                    logger.info("🗑️ [DELETION: Meal by Title] Deleting meal: %s (%s)", m_title, m_id)
                    return {
                        "intent": INTENT_DELETION,
                        "type": "meal_deleted",
                        "deleted_meal_id": m_id,
                        "deleted_meal_title": m_title,
                        "reply_text": f"Removed '{m_title}' ({m_type}, {m_cals} kcal) from your log."
                    }

            # Search in last meal's items
            last_meal = current_meals[-1]
            target_words = [w.rstrip('s') for w in target_term.split() if len(w.rstrip('s')) >= 3]
            for idx, item in enumerate(last_meal.items):
                item_name_lower = item.name.lower()
                match_found = (
                    target_term in item_name_lower or
                    item_name_lower in target_term or
                    any(tw in item_name_lower for tw in target_words)
                )
                if match_found:
                    removed_item = last_meal.items.pop(idx)
                    # If no items left in meal, delete the entire meal
                    if len(last_meal.items) == 0:
                        logger.info("🗑️ [DELETION: Empty Meal] Last item removed from %s; deleting meal %s", last_meal.title, last_meal.id)
                        return {
                            "intent": INTENT_DELETION,
                            "type": "meal_deleted",
                            "deleted_meal_id": last_meal.id,
                            "deleted_meal_title": last_meal.title,
                            "reply_text": f"Removed {removed_item.name} and deleted {last_meal.meal_type} from your log."
                        }

                    old_cal = last_meal.total_calories
                    last_meal.total_calories = sum(i.calories for i in last_meal.items)
                    last_meal.protein = round(sum(i.protein for i in last_meal.items), 1)
                    last_meal.carbs = round(sum(i.carbs for i in last_meal.items), 1)
                    last_meal.fats = round(sum(i.fats for i in last_meal.items), 1)
                    delta = last_meal.total_calories - old_cal
                    last_meal.recalculated = True
                    last_meal.recalc_delta_kcal = delta

                    logger.info("🔄 [DELETION: Item] Removed %s from %s (%d kcal)", removed_item.name, last_meal.title, delta)
                    return {
                        "intent": INTENT_DELETION,
                        "type": "deletion",
                        "meal": last_meal,
                        "reply_text": f"Updated {last_meal.meal_type}! Removed {removed_item.name} ({delta} kcal).",
                        "note": f"Removed {removed_item.name} ({delta} kcal)",
                        "delta_kcal": delta
                    }

        return {
            "intent": INTENT_DELETION,
            "type": "deletion",
            "reply_text": "I couldn't find that item or meal to remove. You can say 'remove this meal' to delete the latest meal.",
            "meal": None
        }

    def _handle_correction(self, text: str, current_meals: List[MealLog]) -> Dict[str, Any]:
        text_lower = text.lower()
        last_meal = current_meals[-1] if current_meals else None
        if not last_meal:
            return {
                "intent": INTENT_CORRECTION,
                "type": "correction",
                "reply_text": "I couldn't find any recent meals to correct. What did you eat today?",
                "meal": None
            }

        clean_text = re.sub(r'[\!\.\?]', '', text_lower)

        # 1. Check replacement: e.g. "2 rotis instead of rice", "replace rice with 2 rotis"
        replace_match = re.search(r'(?:replace\s+([a-zA-Z\s]+)\s+with\s+(.+)|(.+)\s+instead\s+of\s+([a-zA-Z\s]+))', clean_text)
        if replace_match:
            if replace_match.group(1) and replace_match.group(2):
                old_term = replace_match.group(1).strip()
                new_term = replace_match.group(2).strip()
            else:
                new_term = replace_match.group(3).strip()
                new_term = re.sub(r'^(?:actually|make\s+it|change\s+to|i\s+had|had|i\s+ate|ate)\s+', '', new_term).strip()
                old_term = replace_match.group(4).strip()

            target_idx = -1
            for idx, it in enumerate(last_meal.items):
                if old_term in it.name.lower() or it.name.lower() in old_term:
                    target_idx = idx
                    break

            if target_idx >= 0:
                old_item = last_meal.items[target_idx]
                parsed_new = self._parse_single_item(new_term)
                if parsed_new:
                    last_meal.items[target_idx] = parsed_new
                    old_tot = last_meal.total_calories
                    last_meal.total_calories = sum(i.calories for i in last_meal.items)
                    last_meal.protein = round(sum(i.protein for i in last_meal.items), 1)
                    last_meal.carbs = round(sum(i.carbs for i in last_meal.items), 1)
                    last_meal.fats = round(sum(i.fats for i in last_meal.items), 1)
                    delta = last_meal.total_calories - old_tot
                    last_meal.recalculated = True
                    last_meal.recalc_delta_kcal = delta

                    qty_label = int(parsed_new.quantity) if parsed_new.quantity.is_integer() else parsed_new.quantity
                    note = f"Updated {last_meal.meal_type.lower()}! Replaced {old_item.name} with {qty_label}x {parsed_new.name}."
                    logger.info("🔄 [CORRECTION: Replacement] Replaced %s with %s in %s", old_item.name, parsed_new.name, last_meal.id)
                    return {
                        "intent": INTENT_CORRECTION,
                        "type": "correction",
                        "meal": last_meal,
                        "reply_text": note,
                        "note": note,
                        "delta_kcal": delta
                    }

        # 2. Standard quantity modification (e.g. "make it 3 rotis", "actually 2 rotis")
        clean_text_qty = re.sub(r'\bactually\s+(?:i\s+)?(?:had|ate|have|eating)\b', 'actually', clean_text)
        qty_change_match = re.search(r'(?:make\s+that|make\s+it|change\s+to|actually|have)\s+(\d+(?:\.\d+)?|[a-z]+)\s+(.+)', clean_text_qty)
        if qty_change_match:
            qty_raw = qty_change_match.group(1).strip()
            item_raw = qty_change_match.group(2).strip()
            item_raw = re.sub(r'\b(actually|instead|please|thanks)\b', '', item_raw).strip()
            if qty_raw in ["i", "we", "just"] and item_raw:
                parts = item_raw.split(None, 1)
                if parts and (parts[0].isdigit() or parts[0] in NUMBER_WORDS):
                    qty_raw = parts[0]
                    item_raw = parts[1] if len(parts) > 1 else ""
            new_qty = self._parse_qty_token(qty_raw)
            if new_qty is not None and item_raw:
                for item in last_meal.items:
                    clean_item_name = item.name.lower()
                    match_found = False
                    for w in item_raw.split():
                        w_stem = w.rstrip('s')
                        if len(w_stem) >= 3 and w_stem in clean_item_name:
                            match_found = True
                            break
                    if match_found or item_raw in clean_item_name or clean_item_name in item_raw:
                        old_qty = item.quantity
                        diff_qty = new_qty - old_qty
                        unit_nut = nutrition_service.get_nutrition(item.name, 1.0, item.unit)
                        item.quantity = new_qty
                        item.calories = int(round(unit_nut["calories"] * new_qty))
                        item.protein = round(unit_nut["protein"] * new_qty, 1)
                        item.carbs = round(unit_nut["carbs"] * new_qty, 1)
                        item.fats = round(unit_nut["fats"] * new_qty, 1)

                        old_total = last_meal.total_calories
                        last_meal.total_calories = sum(i.calories for i in last_meal.items)
                        last_meal.protein = round(sum(i.protein for i in last_meal.items), 1)
                        last_meal.carbs = round(sum(i.carbs for i in last_meal.items), 1)
                        last_meal.fats = round(sum(i.fats for i in last_meal.items), 1)
                        delta = last_meal.total_calories - old_total
                        last_meal.recalculated = True
                        last_meal.recalc_delta_kcal = delta

                        sign = "+" if delta >= 0 else ""
                        unit_label = "roti" if "roti" in item.name.lower() else item.unit
                        unit_label = unit_label if abs(diff_qty) == 1 else f"{unit_label}s"
                        qty_desc = f"Added {int(abs(diff_qty))} extra {unit_label}" if diff_qty > 0 else f"Reduced by {int(abs(diff_qty))} {unit_label}"
                        note = f"Updated {last_meal.meal_type.lower()}! {qty_desc} ({sign}{delta} kcal)."
                        
                        logger.info("🔄 [CORRECTION: Rule-Based] Updated %s quantity: %s -> %s (%s%d kcal)", item.name, old_qty, new_qty, sign, delta)
                        return {
                            "intent": INTENT_CORRECTION,
                            "type": "correction",
                            "meal": last_meal,
                            "reply_text": note,
                            "note": note,
                            "delta_kcal": delta
                        }

        return {
            "intent": INTENT_CORRECTION,
            "type": "correction",
            "reply_text": "I couldn't find that item in your recent meal to adjust. What would you like to update?",
            "meal": None
        }

    def _handle_workout(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        mins_match = re.search(r'(\d+)\s*(?:mins|min|minutes|minute|hour|hours|hr|hrs)', text_lower)
        duration = 30
        if mins_match:
            duration = int(mins_match.group(1))
            if "hour" in mins_match.group(0) or "hr" in mins_match.group(0):
                duration = duration * 60

        rate_per_min = 9.0
        activity = "Workout"
        if "ran" in text_lower or "run" in text_lower or "jog" in text_lower:
            activity = "Running"
            rate_per_min = 10.5
        elif "walk" in text_lower:
            activity = "Brisk Walking"
            rate_per_min = 4.5
        elif "cycle" in text_lower or "cycling" in text_lower:
            activity = "Cycling"
            rate_per_min = 8.0
        elif "swim" in text_lower:
            activity = "Swimming"
            rate_per_min = 10.0
        elif "gym" in text_lower or "weight" in text_lower:
            activity = "Strength Training"
            rate_per_min = 7.5

        # Check if user explicitly specified calories burned
        burned_match = re.search(r'(?:burned|burn|burnt|-)\s*(\d+)\s*(?:kcal|calories|cals|cal)?\b', text_lower)
        if not burned_match:
            burned_match = re.search(r'(\d+)\s*(?:kcal|calories|cals)\b', text_lower)

        if burned_match:
            burned = int(burned_match.group(1))
        else:
            burned = int(round(rate_per_min * duration))

        logger.info("🏃 [WORKOUT: Rule-Based] Logged %s for %d mins (-%d kcal)", activity, duration, burned)
        return {
            "intent": INTENT_WORKOUT_LOG,
            "type": "workout_log",
            "activity": activity,
            "duration_mins": duration,
            "calories_burned": burned,
            "reply_text": f"Awesome job! Logged {duration} mins of {activity} (-{burned} kcal). Your daily burn target has been updated!"
        }

    def _handle_water(self, text: str) -> Dict[str, Any]:
        """Handles drinking water / hydration logging."""
        text_lower = text.lower().strip()
        liters = 0.25

        # Check for explicit ml (e.g. 500ml, 750 ml)
        ml_match = re.search(r'(\d+(?:\.\d+)?)\s*ml\b', text_lower)
        if ml_match:
            ml_val = float(ml_match.group(1))
            liters = round(ml_val / 1000.0, 2)
        else:
            # Check for explicit liters (e.g. 1.5 liters, 1L, 2 l)
            l_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:l|liters?|litres?)\b', text_lower)
            if l_match:
                liters = round(float(l_match.group(1)), 2)
            else:
                glass_match = re.search(r'(\d+|one|two|three|four|five|a|an)\s*glasses?\b', text_lower)
                if glass_match:
                    count_str = glass_match.group(1).lower()
                    count = NUMBER_WORDS.get(count_str, 1)
                    if count_str.isdigit():
                        count = float(count_str)
                    liters = round(count * 0.25, 2)
                else:
                    bottle_match = re.search(r'(\d+|one|two|a|an)\s*bottles?\b', text_lower)
                    if bottle_match:
                        count_str = bottle_match.group(1).lower()
                        count = NUMBER_WORDS.get(count_str, 1)
                        if count_str.isdigit():
                            count = float(count_str)
                        liters = round(count * 0.75, 2)

        liters = max(0.05, min(10.0, liters))
        logger.info("💧 [WATER: Hydration Log] Logged %.2fL of water", liters)
        return {
            "intent": INTENT_WATER_LOG,
            "type": "water_log",
            "liters": liters,
            "reply_text": f"Logged {liters}L of water! 💧 Great job staying hydrated today."
        }

    def _infer_meal_type(self, text: str) -> str:
        text_lower = text.lower()
        if "breakfast" in text_lower:
            return "Breakfast"
        elif "lunch" in text_lower:
            return "Lunch"
        elif "dinner" in text_lower:
            return "Dinner"
        elif "snack" in text_lower or "coffee" in text_lower or "latte" in text_lower:
            return "Snack"
        else:
            hour = datetime.now().hour
            if hour < 11:
                return "Breakfast"
            elif hour < 16:
                return "Lunch"
            elif hour < 19:
                return "Snack"
            else:
                return "Dinner"

    def _parse_with_rules(self, text: str) -> Tuple[List[FoodItem], bool]:
        """
        Attempts to parse food items using regex and dictionary lookups.
        Returns (items, is_confident).
        """
        text_lower = text.lower().strip()

        # Check if the text contains conversational noise that confuses rule-based splitting
        for noise in CONVERSATIONAL_NOISE:
            if noise in text_lower:
                return [], False

        cleaned = re.sub(r'^(?:i\s+had|i\s+ate|had|ate|logged|log|having|eating)\s+', '', text_lower)
        cleaned = re.sub(r'\s+for\s+(?:breakfast|lunch|dinner|snack).*$', '', cleaned)
        
        segments = re.split(r'\s+(?:with|and|&|\+)\s+|,\s*|\s*;\s*', cleaned)
        
        items: List[FoodItem] = []
        for seg in segments:
            seg = seg.strip()
            if not seg:
                continue
            item = self._parse_single_item(seg)
            if item:
                items.append(item)

        if not items:
            return [], False

        # Evaluate confidence of rule-based output:
        # 1. Check if any extracted item name contains unusual long conversational phrases
        for item in items:
            words = item.name.lower().split()
            # If item name contains conjunctions or noise that leaked in
            if any(w in ["with", "and", "also", "some", "grabbed", "finished"] for w in words):
                return items, False

        # 2. If only one item extracted but the input was long and complex with many words
        if len(items) == 1 and len(text.split()) >= 7:
            # Check if this item is in the smart cache
            nut = nutrition_service.get_nutrition(items[0].name, items[0].quantity, items[0].unit)
            if not nut.get("cached"):
                # Single item from a long complex sentence that isn't cached -> not confident
                return items, False

        return items, True

    def _parse_with_groq(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Groq LLM Fallback:
        Calls Groq API using llama-3.3-70b-versatile with a strict system prompt
        returning structured JSON: {"items": [{"name": str, "quantity": float, "unit": str}], "meal_type": str}
        """
        api_key = self.groq_api_key or os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            logger.warning("⚠️ [PARSER: Groq LLM] GROQ_API_KEY is not set. Cannot call Groq LLM.")
            return None

        try:
            from groq import Groq, RateLimitError, APIConnectionError, APIStatusError
            client = Groq(api_key=api_key)

            system_prompt = (
                "You are an expert nutritional food parser. "
                "Analyze the user's food log message and extract all individual food items, their numerical quantities, "
                "and standard serving units. "
                "If an item is described with an ingredient portion (e.g., 'chicken curry with approx 20g chicken'), capture it as the dish (e.g. name: 'chicken curry', quantity: 1, unit: 'portion with 20g chicken'). Do NOT double count the meat as a separate item. Never drop items. "
                "Each food item must strictly get its own independent quantity from its own phrase. Do NOT assign, inherit, or share quantities across items connected by 'and', '&', '+', or commas. "
                "When a metric volume or weight is specified like '250ml milk' or '100g chicken', represent it strictly as quantity: 1, unit: '250ml' (or '100g'). Do NOT set quantity to 250 with unit 'ml'. "
                "Also identify the overall meal_type (Breakfast, Lunch, Dinner, or Snack). "
                "You must return ONLY a valid JSON object matching this exact schema with no extra text or markdown formatting:\n"
                '{"items": [{"name": "string", "quantity": number, "unit": "string"}], "meal_type": "string"}'
            )

            # Primary model available on Groq with fallbacks
            candidate_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
            completion = None
            for model_name in candidate_models:
                try:
                    completion = client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": text}
                        ],
                        temperature=0.1,
                        max_tokens=350,
                        response_format={"type": "json_object"}
                    )
                    if completion:
                        break
                except Exception as model_err:
                    logger.warning("Model %s unavailable, trying next: %s", model_name, model_err)
                    continue

            if not completion:
                logger.error("❌ [PARSER: Groq LLM] None of the candidate Groq models were reachable.")
                return None

            raw_content = completion.choices[0].message.content.strip()
            clean_json_str = re.sub(r'^```(?:json)?\s*', '', raw_content)
            clean_json_str = re.sub(r'\s*```$', '', clean_json_str).strip()

            parsed_data = json.loads(clean_json_str)
            raw_items = parsed_data.get("items", [])
            meal_type = parsed_data.get("meal_type") or self._infer_meal_type(text)

            if not raw_items:
                logger.warning("⚠️ [PARSER: Groq LLM] Groq returned empty items list for: '%s'", text)
                return None

            food_items: List[FoodItem] = []
            for it in raw_items:
                raw_name = str(it.get("name", "")).strip()
                if not raw_name:
                    continue
                try:
                    qty = float(it.get("quantity") or 1.0)
                except (ValueError, TypeError):
                    qty = 1.0
                unit = str(it.get("unit") or "serving").strip()

                # Defensive normalization: if model returns quantity=250 and unit="ml", normalize to 1 unit of 250ml
                if unit.lower() in ["ml", "g", "gram", "grams", "oz"] and qty > 5:
                    unit = f"{int(qty) if qty.is_integer() else qty}{unit.lower()}"
                    qty = 1.0

                nut = nutrition_service.get_nutrition(raw_name, qty, unit)
                food_items.append(FoodItem(
                    name=nut.get("name", raw_name.title()),
                    quantity=qty,
                    unit=nut.get("unit", unit),
                    calories=nut["calories"],
                    protein=nut["protein"],
                    carbs=nut["carbs"],
                    fats=nut["fats"]
                ))

            if food_items:
                return {
                    "items": food_items,
                    "meal_type": meal_type
                }
            return None

        except RateLimitError as e:
            logger.error("❌ [PARSER: Groq LLM] Groq rate limit hit: %s", e)
            return None
        except json.JSONDecodeError as e:
            logger.error("❌ [PARSER: Groq LLM] Groq returned malformed JSON: %s", e)
            return None
        except Exception as e:
            logger.error("❌ [PARSER: Groq LLM] Groq API error: %s", e)
            return None

    def _create_meal_from_items(
        self,
        items: List[FoodItem],
        meal_type: str,
        original_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Creates a persistable MealLog with appropriate naming, breakdown and category."""
        total_cal = sum(i.calories for i in items)
        total_p = round(sum(i.protein for i in items), 1)
        total_c = round(sum(i.carbs for i in items), 1)
        total_f = round(sum(i.fats for i in items), 1)

        if len(items) >= 2:
            main_items = sorted(items, key=lambda x: x.calories, reverse=True)
            title = f"{main_items[0].name} & {int(main_items[1].quantity) if main_items[1].quantity.is_integer() else main_items[1].quantity} {main_items[1].name.split()[-1].title()}s" if "roti" in main_items[1].name.lower() else f"{main_items[0].name} & {main_items[1].name}"
            if "roti" in original_text.lower():
                curry_item = next((i for i in items if "curry" in i.name.lower() or "chicken" in i.name.lower()), None)
                roti_item = next((i for i in items if "roti" in i.name.lower() or "chapati" in i.name.lower()), None)
                if curry_item and roti_item:
                    title = f"{curry_item.name} & {int(roti_item.quantity)} Rotis"
            sub_items = [i.name for i in items[2:]]
            subtitle = f"{sub_items[0]}" if sub_items else ""
        else:
            title = items[0].name
            subtitle = ""

        timestamp_str = datetime.now().strftime("%I:%M %p").lstrip("0")
        meal_id = f"meal_{int(datetime.now().timestamp()*1000)}"

        # Select representative image thumbnail
        image_url = None
        f_lower = title.lower()
        if "avocado" in f_lower or "toast" in f_lower:
            image_url = "/static/assets/avocado_toast.jpg"
        elif "quinoa" in f_lower or "bowl" in f_lower or "curry" in f_lower or "chicken" in f_lower:
            image_url = "/static/assets/quinoa_bowl.jpg"
        elif "yogurt" in f_lower or "parfait" in f_lower or "berry" in f_lower or "oat" in f_lower:
            image_url = "/static/assets/greek_yogurt.jpg"

        meal_log = MealLog(
            id=meal_id,
            title=title,
            meal_type=meal_type,
            timestamp=timestamp_str,
            items=items,
            total_calories=total_cal,
            protein=total_p,
            carbs=total_c,
            fats=total_f,
            subtitle=subtitle,
            image_url=image_url,
            entry_number=1084
        )

        return {
            "intent": INTENT_FOOD_LOG,
            "type": "new_meal",
            "meal": meal_log,
            "reply_text": f"Logged for **{meal_type}**! Here is the nutritional breakdown:"
        }

    def _handle_food_log(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Parses food items.
        If user explicitly specified a category (e.g. 'breakfast', 'lunch', 'snacks', 'cheat meal', 'dinner'),
        creates and logs it directly.
        Otherwise, stores pending food for this user and prompts: 'Which meal to log in for?'
        """
        user_id = (context or {}).get("user_id") or "default"

        # 1. Attempt rule-based parsing first
        rule_items, is_confident = self._parse_with_rules(text)
        items: List[FoodItem] = []

        if is_confident and rule_items:
            items = rule_items
            logger.info("🔍 [PARSER: Rule-Based] Parsed '%s' -> %s", text, [f"{i.quantity}x {i.name}" for i in items])
        else:
            logger.info("⚠️ [PARSER: Rule-Based] Low confidence for '%s'. Calling Groq LLM fallback...", text)
            groq_res = self._parse_with_groq(text)
            if groq_res and groq_res.get("items"):
                items = groq_res["items"]
                logger.info("🤖 [PARSER: Groq LLM] Parsed '%s' -> %s", text, [f"{i.quantity}x {i.name}" for i in items])
            elif rule_items:
                items = rule_items
                logger.warning("⚠️ [PARSER: Best Effort] Fallback to rule-based for '%s'", text)
            else:
                logger.info("ℹ️ [INTENT] No food items identified for '%s' -> not_food_related", text)
                return self._handle_not_food_related(text, context)

        if not items:
            return self._handle_not_food_related(text, context)

        # 2. If user already included the category in their text, log immediately
        explicit_cat = extract_explicit_meal_type(text)
        if explicit_cat:
            return self._create_meal_from_items(items, explicit_cat, text, context)

        # 3. Ask user which meal to log in for (Breakfast, Lunch, Snacks, Cheat Meal, Dinner)
        self.pending_food_logs[user_id] = {
            "items": items,
            "text": text,
            "timestamp": datetime.now()
        }

        food_summary = ", ".join(f"{int(i.quantity) if i.quantity.is_integer() else i.quantity}x {i.name}" for i in items)
        return {
            "intent": INTENT_FOOD_LOG,
            "type": "ask_meal_type",
            "reply_text": f"Got that ({food_summary})! Which meal would you like to log this for?",
            "meal": None,
            "meal_prompt": True,
            "options": VALID_MEAL_TYPES,
            "pending_food": text,
            "suggestions": ["🌅 Breakfast", "☀️ Lunch", "🥪 Snacks", "🍕 Cheat Meal", "🌙 Dinner"]
        }

    def _parse_single_item(self, text: str) -> Optional[FoodItem]:
        text = text.strip()
        if not text:
            return None

        # Clean conversational noise prefix within segment
        seg = re.sub(r'^(?:a\s+couple\s+of|a\s+few|a\s+plate\s+of|a\s+serving\s+of|a\s+glass\s+of|a\s+cup\s+of|a\s+bowl\s+of|some|also|just)\s+', '', text, flags=re.I).strip()
        seg = re.sub(r'\b(?:approx|approximately|around|roughly|about|nearly)\b', '', seg, flags=re.I).strip()
        if not seg:
            seg = text

        qty = 1.0
        unit = "serving"
        food_name = seg

        # 1. Check for explicit unit pattern: e.g. "1 unit of 250ml milk", "2 units of 250ml milk"
        m_explicit_unit = re.match(r'^(\d+(?:\.\d+)?)\s*(?:unit|units|serving|servings|portion|portions)\s+of\s+(\d+(?:\.\d+)?\s*(?:ml|g|grams?|oz|kg|litres?|liters?|l))\s+(?:of\s+)?(.+)$', seg, re.I)
        if m_explicit_unit:
            qty = float(m_explicit_unit.group(1))
            unit = m_explicit_unit.group(2).replace(" ", "").lower()
            food_name = m_explicit_unit.group(3).strip()
        else:
            # 2. Check for direct metric volume/weight: e.g. "250ml milk", "250 ml milk", "250ml of milk", "100g chicken"
            m_metric = re.match(r'^(\d+(?:\.\d+)?)\s*(ml|g|grams?|oz|kg|litres?|liters?|l)\b(?:\s+of)?\s+(.+)$', seg, re.I)
            if m_metric:
                val = float(m_metric.group(1))
                u = m_metric.group(2).lower()
                qty = 1.0
                unit = f"{int(val) if val.is_integer() else val}{u}"
                food_name = m_metric.group(3).strip()
            else:
                # 3. Check for count + metric: e.g. "2 x 250ml milk", "2 250ml milk"
                m_count_metric = re.match(r'^(\d+(?:\.\d+)?)(?:\s*x)?\s+(\d+(?:\.\d+)?\s*(?:ml|g|grams?|oz|kg|litres?|liters?|l))\s+(?:of\s+)?(.+)$', seg, re.I)
                if m_count_metric:
                    qty = float(m_count_metric.group(1))
                    unit = m_count_metric.group(2).replace(" ", "").lower()
                    food_name = m_count_metric.group(3).strip()
                else:
                    # 4. Standard tokens: [count] [unit] [of] [food]
                    tokens = seg.split()
                    lead_qty = None
                    food_tokens = tokens[:]

                    # Check leading count (e.g. "2", "2x", "1/2", "3/4", "a", "one")
                    m_frac = re.match(r'^(\d+)\s*/\s*(\d+)$', tokens[0])
                    m_qty = re.match(r'^(\d+(?:\.\d+)?)(?:x)?$', tokens[0])
                    if m_frac:
                        num = float(m_frac.group(1))
                        denom = float(m_frac.group(2))
                        lead_qty = round(num / denom, 2) if denom > 0 else 1.0
                        food_tokens = tokens[1:]
                    elif m_qty:
                        lead_qty = float(m_qty.group(1))
                        food_tokens = tokens[1:]
                    elif tokens[0].lower() in NUMBER_WORDS:
                        lead_qty = float(NUMBER_WORDS[tokens[0].lower()])
                        food_tokens = tokens[1:]

                    if lead_qty is not None:
                        qty = lead_qty
                    else:
                        qty = 1.0

                    # Strip filler articles after quantity (e.g. "half an avocado", "1/2 of avocado")
                    if food_tokens and food_tokens[0].lower() in ["a", "an", "of"]:
                        food_tokens = food_tokens[1:]

                    # Check unit (e.g. "bowl", "slice", "glass", "cup", "rotis", "pieces")
                    if food_tokens and food_tokens[0].lower() in UNIT_WORDS:
                        unit = food_tokens[0].lower()
                        food_tokens = food_tokens[1:]
                        if food_tokens and food_tokens[0].lower() in ["of", "a", "an"]:
                            food_tokens = food_tokens[1:]

                    food_name = " ".join(food_tokens).strip()
                    if not food_name:
                        food_name = seg

        food_name_clean = food_name.strip()
        nut = nutrition_service.get_nutrition(food_name_clean, qty, unit)

        resolved_unit = unit if unit not in ["serving", "item"] else nut.get("unit", unit)
        display_name = nut.get("name", food_name_clean.title())
        if "roti" in food_name_clean.lower() and "whole wheat" in text.lower():
            display_name = "Whole Wheat Roti"
        elif "chicken curry" in food_name_clean.lower():
            display_name = "Chicken Curry Bowl"
        elif "cucumber" in food_name_clean.lower():
            display_name = "Cucumber Salad"

        return FoodItem(
            name=display_name,
            quantity=qty,
            unit=resolved_unit,
            calories=nut["calories"],
            protein=nut["protein"],
            carbs=nut["carbs"],
            fats=nut["fats"]
        )

    def _parse_qty_token(self, token: str) -> Optional[float]:
        token = token.lower().strip()
        if token in NUMBER_WORDS:
            return float(NUMBER_WORDS[token])
        try:
            return float(token)
        except ValueError:
            return None

ai_interpreter = AIInterpreter()
