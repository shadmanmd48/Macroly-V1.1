from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class FoodItem(BaseModel):
    name: str
    quantity: float = 1.0
    unit: str = "serving"
    calories: int = 0
    protein: float = 0.0
    carbs: float = 0.0
    fats: float = 0.0

class MealLog(BaseModel):
    id: str
    user_id: Optional[str] = None
    title: str
    meal_type: str  # breakfast, lunch, dinner, snack
    timestamp: str
    items: List[FoodItem] = []
    total_calories: int = 0
    protein: float = 0.0
    carbs: float = 0.0
    fats: float = 0.0
    subtitle: Optional[str] = ""
    image_url: Optional[str] = None
    recalculated: bool = False
    recalc_delta_kcal: Optional[int] = None
    entry_number: Optional[int] = None

class WorkoutLog(BaseModel):
    id: str
    activity: str
    duration_mins: int
    calories_burned: int
    timestamp: str

class Vitals(BaseModel):
    workout_kcal: int = 320
    workout_mins: int = 45
    hydration_liters: float = 2.1
    hydration_target: float = 3.0
    weight_kg: float = 64.2

class ChatMessage(BaseModel):
    id: str
    sender: str  # "user" or "ai"
    text: str
    timestamp: str
    meal_data: Optional[MealLog] = None
    is_update: bool = False
    update_note: Optional[str] = None
    delta_kcal: Optional[int] = None
    suggestions: List[str] = []

class DashboardSummary(BaseModel):
    user_name: str = "Elena"
    greeting: str = "Good morning, Elena 👋"
    date_str: str = "Thursday, Oct 24"
    calorie_target: int = 2200
    calories_consumed: int = 1450
    calories_burned: int = 320
    calories_left: int = 750
    protein_consumed: float = 110.0
    protein_target: float = 140.0
    carbs_consumed: float = 165.0
    carbs_target: float = 220.0
    fats_consumed: float = 42.0
    fats_target: float = 65.0
    vitals: Vitals
    meals: List[MealLog] = []

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

class ManualOverrideRequest(BaseModel):
    meal_id: str
    title: Optional[str] = None
    meal_type: Optional[str] = None
    items: Optional[List[FoodItem]] = None
    total_calories: Optional[int] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fats: Optional[float] = None

class UserProfile(BaseModel):
    id: str
    email: str
    display_name: str = "User"
    calorie_goal: int = 2000
    protein_goal: float = 130.0
    carb_goal: float = 220.0
    fat_goal: float = 65.0
    is_onboarded: bool = False

class UpdateGoalsRequest(BaseModel):
    calorie_goal: int = 2000
    protein_goal: float = 130.0
    carb_goal: float = 220.0
    fat_goal: float = 65.0
    display_name: Optional[str] = None

