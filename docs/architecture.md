# Architecture & System Design

Macroly is designed as a modular, resilient nutrition and workout logging platform that merges fast client-side interactions with an intelligent, multi-tiered AI and nutritional lookup backend.

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
| 1. In-Memory Smart Cache        |                  | PostgreSQL (Supabase) via psycopg|
|    - Verified foods & portions  |                  | (with automatic SQLite fallback  |
|                                 |                  |  for zero-dependency offline dev)|
| 2. FatSecret Platform API       |                  |                                  |
|    - OAuth2 client credentials  |                  | Tables:                          |
|    - USDA / branded food database|                  | - users                          |
|                                 |                  | - daily_goals                    |
| 3. Groq LLM (Llama 3 70B/8B)    |                  | - food_logs                      |
|    - High-speed NL extraction   |                  | - workout_logs                   |
|    - Fallback: Gemini & Rules   |                  | - cached_foods                   |
+---------------------------------+                  +----------------------------------+
```

---

## 2. Multi-Tier Nutrition Pipeline

When a user submits natural language input (e.g., *"grilled chicken breast 200g, 1 cup brown rice, and a tablespoon olive oil"*), Macroly executes the following resolution strategy:

1. **Parser & Unit Extraction**:
   - Groq LLM (or Gemini / regex rules fallback) decomposes the raw text into distinct items, quantities, and units.
2. **Tier 1 — Smart Local Cache**:
   - Queries `cached_foods` table / in-memory cache for exact or normalized food names.
   - If found with verified nutrient profiles (calories, protein, carbs, fat, micronutrients), macros are scaled linearly and returned in `< 5ms`.
3. **Tier 2 — FatSecret Platform API**:
   - If un-cached, queries FatSecret's official food database using OAuth2 client credentials.
   - Extracts accurate macro breakdowns across serving sizes and stores the result in `cached_foods` for future queries.
4. **Tier 3 — Groq AI Model & Rule-Based Estimator**:
   - For complex, home-cooked dishes, composite meals, or when FatSecret is unreachable, Groq calculates macronutrient estimates using contextual recipe analysis.
   - A deterministic rule-based safety net guarantees that user input is never dropped or blocked even during complete network degradation.

---

## 3. Authentication & Multi-Tenancy

- **Client Authentication**: Handled via Supabase JavaScript Client (`@supabase/supabase-js`), supporting both email/password credentials and Google OAuth.
- **Token Verification**: The backend (`backend/auth.py`) extracts the `Authorization: Bearer <access_token>` header, verifies the JWT signature and expiration against the Supabase Project's public JWKS / user endpoint, and injects the authenticated `user_id` into all route handlers.
- **Data Scoping**: Every database write and read explicitly scopes records by `user_id`, preventing cross-tenant leakage.

---

## 4. Database Resilience

- **Primary**: Supabase hosted PostgreSQL database connected via `psycopg2-binary` connection pooling.
- **Failover / Local Mode**: If the remote PostgreSQL connection fails (e.g. DNS failure, missing internet connection, or zero-config development), the backend automatically initializes and switches to a local SQLite database (`backend/macroly.db`), creating all required schemas dynamically without crashing the server.
