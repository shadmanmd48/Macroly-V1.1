import os
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime
from backend.models import (
    ChatRequest, ChatMessage, DashboardSummary, ManualOverrideRequest,
    MealLog, FoodItem, UserProfile, UpdateGoalsRequest
)
from backend.database import data_store
from backend.auth import get_current_user, SUPABASE_URL, SUPABASE_ANON_KEY
from backend.ai_interpreter import ai_interpreter
from backend.smart_cache import smart_cache, get_database_info, is_postgres

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("macroly.server")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup diagnostics & database status check
    db_info = get_database_info()
    if db_info["is_postgres"]:
        logger.info("=" * 65)
        logger.info("🚀 MACROLY BACKEND STARTUP")
        logger.info("🔗 DATABASE_URL: PostgreSQL detected")
        logger.info("📍 Target Host:  %s", db_info['target'])
        logger.info("✅ Database connection: Connected to Postgres (Supabase)")
        logger.info("=" * 65)
    else:
        logger.warning("=" * 65)
        logger.warning("🚀 MACROLY BACKEND STARTUP")
        logger.warning("⚠️  DATABASE_URL is not configured for PostgreSQL.")
        logger.warning("📁 Local SQLite Fallback: %s", db_info['target'])
        logger.warning("=" * 65)
    yield

app = FastAPI(title="Macroly AI Nutrition Tracker API", version="3.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

@app.get("/api/config")
def get_public_config():
    """Provides public configuration needed for client-side Supabase Auth."""
    return {
        "supabase_url": SUPABASE_URL,
        "supabase_anon_key": SUPABASE_ANON_KEY
    }

@app.get("/api/health")
def health_check():
    db_info = get_database_info()
    return {
        "status": "healthy",
        "database": db_info,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/user/profile", response_model=UserProfile)
def get_profile(user: UserProfile = Depends(get_current_user)):
    """Fetch current user's profile and goal settings."""
    return user

@app.post("/api/user/goals")
def update_goals(req: UpdateGoalsRequest, user: UserProfile = Depends(get_current_user)):
    """Update user daily macro/calorie goals and mark onboarding as complete."""
    updated = data_store.update_user_goals(
        user_id=user.id,
        calorie_goal=req.calorie_goal,
        protein_goal=req.protein_goal,
        carb_goal=req.carb_goal,
        fat_goal=req.fat_goal,
        display_name=req.display_name
    )
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update goals")
    return {
        "status": "success",
        "user": updated,
        "dashboard": data_store.get_dashboard(user.id)
    }

@app.get("/api/dashboard", response_model=DashboardSummary)
def get_dashboard(user: UserProfile = Depends(get_current_user)):
    """Fetch user-scoped dashboard summary and rings."""
    return data_store.get_dashboard(user.id)

@app.post("/api/chat", response_model=ChatMessage)
def chat_endpoint(req: ChatRequest, user: UserProfile = Depends(get_current_user)):
    """Process nutrition chat message strictly scoped to the authenticated user."""
    user_text = req.message.strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    timestamp = datetime.now().strftime("%I:%M %p").lstrip("0")
    user_msg_id = f"msg_{int(datetime.now().timestamp()*1000)}_user"
    ai_msg_id = f"msg_{int(datetime.now().timestamp()*1000)}_ai"

    # Store user message in user-isolated history
    user_msg = ChatMessage(
        id=user_msg_id,
        sender="user",
        text=user_text,
        timestamp=timestamp
    )
    data_store.add_chat_message(user.id, user_msg)

    # Process through AI Interpreter with user's specific targets and profile
    user_meals = data_store.get_all_meals(user.id)
    context = {
        "calorie_target": user.calorie_goal,
        "protein_target": user.protein_goal,
        "carbs_target": user.carb_goal,
        "fats_target": user.fat_goal,
        "user_name": user.display_name
    }
    result = ai_interpreter.process_message(user_text, user_meals, context=context)
    res_type = result.get("type") or result.get("intent")

    ai_reply_text = result.get("reply_text", "Logged!")
    meal_data = None
    is_update = False
    update_note = None
    delta_kcal = None

    if res_type in ["new_meal", "food_log"]:
        if result.get("meal"):
            meal_data = result["meal"]
            meal_data.user_id = user.id
            data_store.add_meal(meal_data, user_id=user.id)
    elif res_type in ["update", "correction", "deletion"]:
        if result.get("meal"):
            is_update = True
            meal_data = result["meal"]
            meal_data.user_id = user.id
            update_note = result.get("note")
            delta_kcal = result.get("delta_kcal")
            data_store.update_meal(meal_data.id, meal_data.dict(), user_id=user.id)
    elif res_type in ["workout", "workout_log"]:
        data_store.log_workout(user.id, result["duration_mins"], result["calories_burned"])
    elif res_type == "not_food_related":
        meal_data = None

    ai_msg = ChatMessage(
        id=ai_msg_id,
        sender="ai",
        text=ai_reply_text,
        timestamp=timestamp,
        meal_data=meal_data,
        is_update=is_update,
        update_note=update_note,
        delta_kcal=delta_kcal,
        suggestions=["☕ Morning Coffee", "🍎 Snack", "🔲 Scan barcode"]
    )
    data_store.add_chat_message(user.id, ai_msg)

    return ai_msg

@app.get("/api/chat/history")
def get_chat_history(user: UserProfile = Depends(get_current_user)):
    """Fetch chat history for the authenticated user."""
    return data_store.get_chat_history(user.id)

@app.post("/api/meal/override")
def override_meal(req: ManualOverrideRequest, user: UserProfile = Depends(get_current_user)):
    """Manually update meal portions verifying ownership."""
    updated = data_store.update_meal(req.meal_id, req.dict(exclude_unset=True), user_id=user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Meal not found or unauthorized")
    return {"status": "success", "meal": updated, "dashboard": data_store.get_dashboard(user.id)}

@app.delete("/api/meal/{meal_id}")
def delete_meal(meal_id: str, user: UserProfile = Depends(get_current_user)):
    """Delete meal verifying user ownership."""
    success = data_store.delete_meal(meal_id, user_id=user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Meal not found or unauthorized")
    return {"status": "success", "dashboard": data_store.get_dashboard(user.id)}

@app.post("/api/reset")
def reset_store(user: UserProfile = Depends(get_current_user)):
    """Reset data for the authenticated user only."""
    data_store.reset_to_default(user.id)
    return {"status": "success", "dashboard": data_store.get_dashboard(user.id)}

# Mount frontend files
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
