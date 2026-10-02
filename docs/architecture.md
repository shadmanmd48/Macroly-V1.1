# Architecture & System Design

Macroly is designed as a modular, resilient nutrition and workout logging platform that merges fast client-side interactions with an intelligent, multi-tiered AI and nutritional lookup backend.

For a comprehensive log of AI models, approximations, and parsing features, see [ai_architecture_and_feature_log.md](file:///c:/Users/user/OneDrive/Desktop/Macroly/docs/ai_architecture_and_feature_log.md).

---

## 1. System Overview

```
                      +-----------------------------------+
                      |      Client (Vanilla JS/CSS)      |
                      |   - Auth Modal (Supabase JS)      |
                      |   - Live Macro Ring & Trends      |
                      |   - Natural Language Quick Log    |
                      +-----------------+-----------------+
                                        |  REST + Bearer Token
                                        v
                      +-----------------+-----------------+
                      |       FastAPI Backend             |
                      |   - auth.py (JWT Verification)    |
                      |   - User Scoped Session Routing   |
                      +-----------------+-----------------+
                                        |
         +------------------------------+------------------------------+
         |                                                             |
         v                                                             v
+--------+------------------------+                  +-----------------+------------------+
|    Multi-Tier Nutrition Engine  |                  |         Data Layer               |
|                                 |                  |                                  |
| Layer 0: Intent Classifier      |                  | PostgreSQL (Supabase) via psycopg|
|   - Chit-chat & Workout guard   |                  | (with automatic SQLite fallback  |
|                                 |                  |  for zero-dependency offline dev)|
| Layer 1: Rule & Metric Parser   |                  |                                  |
|   - Multi-item isolation        |                  | Tables:                          |
|   - Unit normalization (ml, g)  |                  | - users                          |
|                                 |                  | - daily_goals                    |
| Layer 2: Groq LLM Fallback      |                  | - food_logs                      |
|   - Approximation qualifiers    |                  | - workout_logs                   |
|   - Ingredient modifiers        |                  | - cached_foods                   |
|                                 |                  | - chat_messages                  |
| Layer 3: CalorieNinjas Live API |                  |                                  |
|   - Real-time nutrient lookup   |                  |                                  |
|   - Header-based auth (no IP lock)                 |                                  |
|                                 |                  |                                  |
| Layer 4: Smart Cache & Fallback |                  |                                  |
|   - Pre-seeded staple catalog   |                  |                                  |
|   - Deterministic heuristics    |                  |                                  |
+---------------------------------+                  +----------------------------------+
```

---

## 2. Multi-Tier Nutrition Pipeline

When a user submits natural language input (e.g., *"3 butter naan and chicken curry with approx 20g chicken and 250ml milk"*), Macroly executes the following resolution strategy:

### Layer 0: Intent Classification (Pre-Parser Guard)
- **Conversational Filter:** Greetings, compliments, and general small talk (*"hello"*, *"thanks"*) are answered conversationally without triggering food lookups or database writes.
- **Target Inquiries:** Requests such as *"what's my calorie goal today?"* fetch the user's active goals from their profile without invoking parsers.
- **Workout Detection:** Detects workouts and exercises (*"ran 30 mins"*, *"weight lifting 45 min"*) and routes directly to the exercise caloric expenditure calculator.
- **Conversational Corrections & Deletions:** Handles natural updates (*"make that 2 eggs, not 3"*, *"remove the rice"*) with delta calorie calculations against the previous meal.

### Layer 1: Rule-Based Parser & Metric Extraction
- **Sub-millisecond Pre-Parser:** Evaluates clean, common food logs without invoking network LLMs.
- **Multi-Item Isolation:** Conjunctions (`"and"`, `","`, `"&"`, `"+"`) partition queries into isolated items so quantities do not leak across dishes.
- **Metric Volume & Weight Recognition:** Directly recognizes metric units like `250ml`, `500ml`, `100g`, `200g`, and explicit formats like `1 unit of 250ml milk`.
- **Staple Singular/Plural Normalization:** Automatically standardizes counts and units for staple items (`"3 rotis"` &rarr; `3 roti`, `"2 eggs"` &rarr; `2 egg`).

### Layer 2: Approximation Handling & Groq LLM Routing
- **Approximation Filtering:** When queries include conversational qualifiers (`"approx"`, `"roughly"`, `"about"`, `"around"`), the rule engine yields to Groq LLM (`llama-3.3-70b-versatile` / `qwen/qwen3.8-27b`).
- **Ingredient Portion Modifiers:** Solves double-counting when meat or additions are specified within dishes (e.g., *"chicken curry with approx 20gram chicken"*). Rather than logging chicken curry AND a separate chicken portion, it identifies the portion modifier and calculates:
  $$\text{Gravy Base} (\approx 100\text{ kcal}, 2.5\text{g P}) + 20\text{g Chicken} (\approx 33\text{ kcal}, 6.2\text{g P}) = 133\text{ kcal}, 8.7\text{g Protein}$$
- **Name Sanitization:** Strips qualifiers and conversational noise from the logged title for a clean dashboard view.

### Layer 3: CalorieNinjas Live Nutrition API
- **Dynamic IP Resilience:** Utilizes CalorieNinjas REST API authenticated via `X-Api-Key`, eliminating IP-whitelist restrictions (such as FatSecret's OAuth Error 21) on dynamic cloud platforms like Railway.
- **Compound Ingredient Resolution:** Queries un-cached ingredients and sums multi-component responses.
- **Proportional Scaling:** Scales results linearly by volume (`ml` vs standard 250ml glass) or weight (`g` vs 100g base).

### Layer 4: Smart Cache & Fallback Heuristics
- **Fast In-Memory / Persistent Cache:** Caches verified nutrient profiles in `cached_foods` with exact-match precedence and shortest-match ordering.
- **Deterministic Offline Heuristics:** If external APIs are unreachable or offline, category-based fallback heuristics guarantee that the user's log is never dropped or blocked.

---

## 3. Authentication & Multi-Tenancy

- **Client Authentication**: Handled via Supabase JavaScript Client (`@supabase/supabase-js`), supporting both email/password credentials and Google OAuth.
- **Token Verification**: The backend (`backend/auth.py`) extracts the `Authorization: Bearer <access_token>` header, verifies the JWT signature and expiration against the Supabase Project's public JWKS / user endpoint, and injects the authenticated `user_id` into all route handlers.
- **Data Scoping**: Every database write and read explicitly scopes records by `user_id`, preventing cross-tenant leakage.

---

## 4. Database Resilience

- **Primary**: Supabase hosted PostgreSQL database connected via `psycopg2-binary` connection pooling.
- **Failover / Local Mode**: If the remote PostgreSQL connection fails (e.g. DNS failure, missing internet connection, or zero-config development), the backend automatically initializes and switches to a local SQLite database (`backend/macroly.db`), creating all required schemas dynamically without crashing the server.
