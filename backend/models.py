from typing import List, Optional, Dict, Any, Union
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
    meal_type: str  # Breakfast, Lunch, Snacks, Cheat Meal, Dinner
    timestamp: str
    date_str: Optional[str] = None
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
    height_cm: float = 172.0
    target_weight_kg: float = 62.0

class UpdateVitalsRequest(BaseModel):
    weight_kg: Optional[float] = Field(default=None, ge=10.0, le=500.0)
    height_cm: Optional[float] = Field(default=None, ge=40.0, le=300.0)
    target_weight_kg: Optional[float] = Field(default=None, ge=10.0, le=500.0)

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
    deleted_meal_id: Optional[str] = None
    meal_prompt: Optional[Union[Dict[str, Any], bool]] = None
    options: List[str] = []

class DashboardSummary(BaseModel):
    user_name: str = "User"
    greeting: str = "Good day, User 👋"
    date_str: str = ""
    calorie_target: int = 2000
    calories_consumed: int = 0
    calories_burned: int = 0
    calories_left: int = 2000
    protein_consumed: float = 0.0
    protein_target: float = 130.0
    carbs_consumed: float = 0.0
    carbs_target: float = 220.0
    fats_consumed: float = 0.0
    fats_target: float = 65.0
    vitals: Vitals
    meals: List[MealLog] = []

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: Optional[str] = Field(default="default", max_length=128)
    selected_meal_type: Optional[str] = Field(default=None, max_length=64)

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
    avatar_url: Optional[str] = None
    is_onboarded: bool = False

class UpdateGoalsRequest(BaseModel):
    calorie_goal: int = Field(default=2000, ge=500, le=20000)
    protein_goal: float = Field(default=130.0, ge=0.0, le=1000.0)
    carb_goal: float = Field(default=220.0, ge=0.0, le=1000.0)
    fat_goal: float = Field(default=65.0, ge=0.0, le=1000.0)
    display_name: Optional[str] = Field(default=None, max_length=100)
    avatar_url: Optional[str] = Field(default=None, max_length=1024)

class UpdateAvatarRequest(BaseModel):
    avatar_url: str = Field(..., min_length=1, max_length=1024)

class DailyHistoryItem(BaseModel):
    id: str
    user_id: str
    date_str: str
    date_label: str
    calories: int = 0
    protein: float = 0.0
    carbs: float = 0.0
    fats: float = 0.0
    calorie_target: int = 2000
    protein_target: float = 130.0
    carb_target: float = 220.0
    fat_target: float = 65.0
    meals_count: int = 0
    meals: List[Dict[str, Any]] = []
    created_at: Optional[str] = None

class DayTransitionStatus(BaseModel):
    show_transition: bool = False
    today_date_str: str = ""
    previous_day: Optional[Dict[str, Any]] = None
    yesterday_summary: Optional[Dict[str, Any]] = None


