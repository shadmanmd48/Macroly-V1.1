# Macroly 🥗⚡

> **Intelligent, real-time macronutrient and fitness tracking powered by natural language processing and verified nutrition databases.**

Macroly transforms daily nutrition tracking from a tedious chore into an effortless, conversational experience. Rather than searching through clunky databases and manually weighing individual components, users simply describe what they ate in plain English. Macroly extracts the items, references verified nutritional databases and high-speed LLMs, and maintains an interactive, real-time macro dashboard with multi-user authentication.

---

## 🌟 Key Features

- **Natural Language Food Logging**: Log meals naturally (e.g., *"2 scrambled eggs, avocado toast, and an iced oat latte"*). The backend parses items, portions, and units instantly.
- **Multi-Tiered Nutrition Engine**:
  - **Smart Cache**: Instant sub-5ms lookup for recurring and common food items.
  - **FatSecret Platform API**: Live access to verified commercial and USDA nutritional databases.
  - **Groq LLM (Llama 3 70B)**: Contextual recipe decomposition and macro estimation for complex meals, backed by a deterministic safety fallback.
- **Real-Time Macro Dashboard**: Visual progress rings tracking daily Calories, Protein, Carbohydrates, and Fats against personalized targets.
- **Conversational Corrections & Undo**: Quickly adjust previous entries (e.g., *"Actually it was 1 slice, not 2"*) or revert the latest log with one click.
- **Workout & Activity Tracking**: Log strength and cardiovascular sessions with automatic caloric expenditure calculation.
- **Secure Multi-User Authentication**: Production-ready authentication supporting both Email/Password credentials and Google OAuth via Supabase, with automatic database multi-tenancy.
- **Offline & Local Development Resilience**: Seamless automated failover from hosted PostgreSQL to local SQLite if network connectivity is interrupted.

---

## 🛠️ Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python 3.10+, [FastAPI](https://fastapi.tiangolo.com/), Uvicorn, Pydantic v2 |
| **Database** | [PostgreSQL](https://www.postgresql.org/) (hosted on [Supabase](https://supabase.com/)), `psycopg2-binary`, SQLite (zero-config fallback) |
| **Authentication** | Supabase Auth (JWT Bearer Token verification, Email/Password, Google OAuth) |
| **AI / NLP** | [Groq Cloud](https://groq.com/) (Llama-3.3-70b-versatile / Llama-3.1-8b-instant), Google Gemini API |
| **Nutrition Data** | [FatSecret REST API](https://platform.fatsecret.com/api/) (OAuth 2.0 Client Credentials) |
| **Frontend** | Modern Vanilla JavaScript (ES6+), Vanilla CSS (Custom Design System, Glassmorphism, Micro-animations), Supabase JS Client |

---

## 📁 Repository Structure

```text
Macroly/
├── backend/
│   ├── ai_interpreter.py     # Natural language meal parser (Groq / Gemini / Rule engine)
│   ├── auth.py               # Supabase JWT verification and user identity dependency
│   ├── database.py           # PostgreSQL/SQLite dual-mode connection pool and queries
│   ├── main.py               # FastAPI application routes, middleware, and lifecycle
│   ├── models.py             # Pydantic schemas for requests, responses, and user profiles
│   ├── nutrition_service.py  # FatSecret API integration and token management
│   └── smart_cache.py        # High-performance food caching and macro scaling
├── frontend/
│   ├── assets/               # Demo avatars and culinary imagery
│   ├── css/
│   │   └── styles.css        # Responsive dark-mode styling, tokens, and micro-animations
│   ├── js/
│   │   ├── api.js            # Client-side API client handling auth headers and requests
│   │   └── app.js            # Application controller, modal managers, and UI bindings
│   └── index.html            # Main single-page application dashboard
├── docs/
│   ├── api.md                # Comprehensive REST API endpoint reference
│   └── architecture.md       # Multi-tier pipeline and database system design
├── .env.example              # Environment variables template with setup documentation
├── .gitignore                # Production git ignore configuration
├── LICENSE                   # MIT License
├── README.md                 # Project documentation
└── requirements.txt          # Python dependencies
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+** installed on your system.
- *(Optional)* Free accounts for:
  - [Supabase](https://supabase.com) (for PostgreSQL database & User Auth)
  - [Groq Console](https://console.groq.com) (for high-speed AI parsing)
  - [FatSecret Platform](https://platform.fatsecret.com/api/) (for live food database search)

> **Note**: Macroly is designed to run out of the box even without external API keys — it will automatically fall back to rule-based parsing and local SQLite database storage for local testing!

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/macroly.git
cd macroly
```

### 2. Set Up a Virtual Environment

```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to create your local `.env`:

```bash
cp .env.example .env
```

Open `.env` in your editor and configure your credentials:

```ini
# Database (PostgreSQL / Supabase)
DATABASE_URL=postgresql://postgres:your_password@db.yourproject.supabase.co:5432/postgres

# Supabase Auth
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key_here

# AI Engine
GROQ_API_KEY=gsk_your_groq_api_key_here

# FatSecret API (Optional)
FATSECRET_CLIENT_ID=your_fatsecret_client_id_here
FATSECRET_CLIENT_SECRET=your_fatsecret_client_secret_here
```

### 5. Run the Application

Start the FastAPI backend with hot-reload enabled:

```bash
uvicorn backend.main:app --reload --port 8000
```

The application will be live at:
- **Web Dashboard**: [http://localhost:8000](http://localhost:8000)
- **Interactive OpenAPI Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative Redoc Docs**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Documentation

For detailed technical deep-dives, consult the `docs/` directory:
- [Architecture & Multi-Tier Resolution](docs/architecture.md): In-depth look at caching, API fallbacks, and JWT validation.
- [REST API Reference](docs/api.md): Schema specifications and example payloads for all HTTP endpoints.

---

## 🤖 Engineering & AI Methodology

This codebase was designed and built utilizing modern AI-assisted software engineering workflows (including Google DeepMind's Antigravity agentic coding framework). Architectural structure, domain modeling, API contracts, security audits, and code standards were guided by rigorous human design principles, ensuring a clean, maintainable, and production-ready standard.

---

## 📄 License

This project is licensed under the terms of the [MIT License](LICENSE).
