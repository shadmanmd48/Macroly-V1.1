# REST API Reference

All protected API endpoints require an `Authorization: Bearer <SUPABASE_JWT_TOKEN>` header.

Base URL: `http://localhost:8000` (or your production deployment domain, e.g. `https://macroly-v11-production.up.railway.app`)

---

## 1. System & Configuration

### `GET /api/config`
Retrieves public configuration required for client-side Supabase Auth initialization.

- **Authentication**: None
- **Response `200 OK`**:
  ```json
  {
    "supabase_url": "https://your-project.supabase.co",
    "supabase_anon_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
  ```

### `GET /api/health`
Health check and database diagnostics endpoint.

- **Authentication**: None
- **Response `200 OK`**:
  ```json
  {
    "status": "healthy",
    "database": {
      "is_postgres": true,
      "target": "db.yourproject.supabase.co"
    },
    "timestamp": "2026-10-03T00:20:00.000000"
  }
  ```

---

## 2. Authentication & User Profile

### `GET /api/user/profile`
Retrieves the authenticated user's profile and current macro/calorie targets.

- **Headers**: `Authorization: Bearer <token>`
- **Response `200 OK`**:
  ```json
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "email": "user@example.com",
    "display_name": "Alex Mercer",
    "calorie_goal": 2200,
    "protein_goal": 160.0,
    "carb_goal": 220.0,
    "fat_goal": 65.0,
    "onboarding_completed": true,
    "created_at": "2026-09-24T18:00:00Z"
  }
  ```

### `POST /api/user/goals`
Updates daily macro/calorie targets and marks onboarding as completed.

- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "calorie_goal": 2400,
    "protein_goal": 175.0,
    "carb_goal": 250.0,
    "fat_goal": 70.0,
    "display_name": "Alex Mercer"
  }
  ```
- **Response `200 OK`**:
  ```json
  {
    "status": "success",
    "user": { ... },
    "dashboard": { ... }
  }
  ```

---

## 3. Conversational AI Chat & Meal Logging

### `POST /api/chat`
Primary entry point for natural language meal logging, workouts, target inquiries, corrections, and deletions.

- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "message": "3 butter naan and chicken curry with approx 20g chicken and 250ml milk"
  }
  ```
- **Response `200 OK`**:
  ```json
  {
    "id": "msg_1790967000000_ai",
    "sender": "ai",
    "text": "Logged 3 items totaling 1041 kcal with 43.8g protein.",
    "timestamp": "12:20 AM",
    "meal_data": {
      "id": "meal_1790967000000",
      "name": "3 Butter Naan, Chicken Curry (portion with 20g chicken), 250ml Milk",
      "meal_type": "dinner",
      "calories": 1041,
      "protein": 43.8,
      "carbs": 140.2,
      "fat": 33.1,
      "items": [
        {
          "name": "Butter Naan",
          "quantity": 3.0,
          "unit": "piece",
          "calories": 780,
          "protein": 26.4,
          "carbs": 114.0,
          "fat": 24.0,
          "source": "smart_cache"
        },
        {
          "name": "Chicken Curry (portion with 20g chicken)",
          "quantity": 1.0,
          "unit": "serving",
          "calories": 133,
          "protein": 8.7,
          "carbs": 14.2,
          "fat": 4.3,
          "source": "calorieninjas"
        },
        {
          "name": "Milk",
          "quantity": 1.0,
          "unit": "250ml",
          "calories": 128,
          "protein": 8.7,
          "carbs": 12.0,
          "fat": 4.8,
          "source": "calorieninjas"
        }
      ]
    },
    "is_update": false,
    "update_note": null,
    "delta_kcal": null,
    "suggestions": [
      "☕ Morning Coffee",
      "🍎 Snack",
      "🔲 Scan barcode"
    ]
  }
  ```

#### Conversational Correction Example
- **Request Body**:
  ```json
  {
    "message": "Actually make that 2 butter naan instead of 3"
  }
  ```
- **Response `200 OK`**:
  ```json
  {
    "id": "msg_1790967050000_ai",
    "sender": "ai",
    "text": "Updated Butter Naan to 2 piece (-260 kcal).",
    "is_update": true,
    "update_note": "Adjusted Butter Naan from 3.0 to 2.0 piece",
    "delta_kcal": -260
  }
  ```

### `GET /api/chat/history`
Fetches conversation history strictly scoped to the authenticated user.

- **Headers**: `Authorization: Bearer <token>`
- **Response `200 OK`**: Array of `ChatMessage` objects.

---

## 4. Dashboard & Direct Meal Management

### `GET /api/dashboard`
Retrieves daily aggregated calories, remaining targets, macro progress rings, recent meal logs, and workout burns.

- **Headers**: `Authorization: Bearer <token>`
- **Response `200 OK`**:
  ```json
  {
    "total_calories": 1640,
    "remaining_calories": 560,
    "calorie_goal": 2200,
    "total_protein": 125.4,
    "protein_goal": 160.0,
    "total_carbs": 180.2,
    "carb_goal": 220.0,
    "total_fat": 48.6,
    "fat_goal": 65.0,
    "recent_meals": [ ... ],
    "total_workout_calories": 250,
    "active_workout_mins": 35
  }
  ```

### `POST /api/meal/override`
Manually edits portions or macros of an existing meal after verifying user ownership.

- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "meal_id": "meal_1790967000000",
    "calories": 950,
    "protein": 40.0
  }
  ```
- **Response `200 OK`**:
  ```json
  {
    "status": "success",
    "meal": { ... },
    "dashboard": { ... }
  }
  ```

### `DELETE /api/meal/{meal_id}`
Deletes a specific meal entry belonging to the authenticated user.

- **Headers**: `Authorization: Bearer <token>`
- **Response `200 OK`**:
  ```json
  {
    "status": "success",
    "dashboard": { ... }
  }
  ```

### `POST /api/reset`
Resets the authenticated user's logged meals and chat history back to the default demo state.

- **Headers**: `Authorization: Bearer <token>`
- **Response `200 OK`**:
  ```json
  {
    "status": "success",
    "dashboard": { ... }
  }
  ```
