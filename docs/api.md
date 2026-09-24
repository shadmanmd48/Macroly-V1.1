# REST API Reference

All protected API endpoints require an `Authorization: Bearer <SUPABASE_JWT_TOKEN>` header.

Base URL: `http://localhost:8000` (or your production deployment domain)

---

## 1. Authentication & User Profile

### `GET /api/auth/me`
Retrieves the authenticated user's profile and settings.

- **Headers**: `Authorization: Bearer <token>`
- **Response `200 OK`**:
  ```json
  {
    "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "email": "user@example.com",
    "name": "Alex Mercer",
    "goal": "cut",
    "target_calories": 2150,
    "target_protein": 165.0,
    "target_carbs": 210.0,
    "target_fat": 65.0,
    "created_at": "2026-09-24T18:00:00Z"
  }
  ```

### `POST /api/profile`
Updates user profile settings and macro targets.

- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "name": "Alex Mercer",
    "goal": "lean_bulk",
    "target_calories": 2600,
    "target_protein": 180,
    "target_carbs": 300,
    "target_fat": 75
  }
  ```
- **Response `200 OK`**:
  ```json
  {
    "status": "success",
    "message": "Profile updated successfully."
  }
  ```

---

## 2. Food & Macro Logging

### `POST /api/log`
Logs food items from natural language text, calculating macros via the multi-tier engine.

- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "text": "3 scrambled eggs, 2 slices whole wheat toast, and 1 glass orange juice",
    "meal_type": "breakfast"
  }
  ```
- **Response `200 OK`**:
  ```json
  {
    "status": "success",
    "logged_items": [
      {
        "id": 104,
        "name": "Scrambled Eggs",
        "quantity": 3.0,
        "unit": "large",
        "calories": 213,
        "protein": 18.2,
        "carbs": 2.1,
        "fat": 14.7,
        "source": "smart_cache"
      },
      {
        "id": 105,
        "name": "Whole Wheat Bread",
        "quantity": 2.0,
        "unit": "slice",
        "calories": 160,
        "protein": 8.0,
        "carbs": 28.0,
        "fat": 2.0,
        "source": "fatsecret"
      }
    ],
    "daily_totals": {
      "calories": 373,
      "protein": 26.2,
      "carbs": 30.1,
      "fat": 16.7
    }
  }
  ```

### `GET /api/today`
Retrieves daily aggregated macros, goal percentages, and itemized logs for today.

- **Headers**: `Authorization: Bearer <token>`
- **Response `200 OK`**:
  ```json
  {
    "date": "2026-09-24",
    "totals": {
      "calories": 1780,
      "protein": 142.5,
      "carbs": 165.0,
      "fat": 58.2
    },
    "goals": {
      "calories": 2200,
      "protein": 160.0,
      "carbs": 220.0,
      "fat": 65.0
    },
    "items": [ ... ],
    "workouts": [ ... ]
  }
  ```

### `POST /api/correct`
Allows conversational or manual corrections to the most recently logged items.

- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "instruction": "Actually it was only 1 slice of toast, not 2"
  }
  ```

### `POST /api/undo`
Deletes the most recently logged food entry.

- **Headers**: `Authorization: Bearer <token>`
- **Response `200 OK`**:
  ```json
  {
    "status": "success",
    "message": "Removed last entry: Whole Wheat Bread (2.0 slice)"
  }
  ```

---

## 3. Workouts & Exercise

### `POST /api/workout`
Logs workout activity and calculates estimated caloric expenditure.

- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "activity": "Bench press 4 sets 8 reps, followed by 20 min incline treadmill run",
    "duration_minutes": 55,
    "intensity": "moderate_high"
  }
  ```
- **Response `200 OK`**:
  ```json
  {
    "status": "success",
    "workout": {
      "id": 42,
      "title": "Strength & Cardio Session",
      "calories_burned": 385,
      "duration_minutes": 55
    }
  }
  ```

---

## 4. History & Trends

### `GET /api/history?days=7`
Fetches historical macro data and caloric trends over a specified day range.

- **Headers**: `Authorization: Bearer <token>`
- **Query Parameters**:
  - `days` *(optional, integer, default: 7)*: Number of past days to query.
