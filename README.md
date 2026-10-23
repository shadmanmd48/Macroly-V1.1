# Macroly 🥗⚡

> **Intelligent, real-time macronutrient and fitness tracking powered by natural language processing and verified nutrition databases.**

Macroly transforms daily nutrition tracking from a tedious chore into an effortless, conversational experience. Rather than searching through clunky databases and manually weighing individual components, users simply describe what they ate in plain English. Macroly extracts the items, references verified nutritional databases and high-speed LLMs, and maintains an interactive, real-time macro dashboard with multi-user authentication.

---

## 🌟 Key Features

- **Conversational Food Logging**: Log meals naturally (e.g., *"2 boiled eggs, 200g rice, and chicken curry"*) with instant portion parsing and nutritional calculation.
- **Smart Meal Categorization**: Guided classification into Breakfast, Lunch, Snacks, Cheat Meal, or Dinner with dynamic prompts.
- **Real-Time Macro Dashboard**: Visual progress rings tracking daily calories, protein, carbs, and fats against personalized targets.
- **Conversational Corrections & Deletions**: Adjust quantities (e.g., *"Make that 3 rotis actually"*) or remove meals directly from chat with instant macro recalculation.
- **Daily History & Auto-Rollover**: Automatic midnight (IST) archival and historical daily macro logs to monitor long-term trends.
- **Vitals & Goal Customization**: Manage personal profile vitals (height, weight, target weight) alongside daily macro goals.
- **Multi-Tier Nutrition Engine**: High-speed hybrid architecture pairing local smart caching, verified nutrition databases, and LLM recipe decomposition.
- **Secure Multi-User Authentication**: Multi-tenant isolation supporting Email/Password and Google OAuth via Supabase.
- **Offline & Local Resilience**: Seamless automatic fallback from cloud PostgreSQL to local SQLite for uninterrupted development.

---

## 🛠️ Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python 3.10+, [FastAPI](https://fastapi.tiangolo.com/), Uvicorn, Pydantic v2 |
| **Database** | [PostgreSQL](https://www.postgresql.org/) (hosted on [Supabase](https://supabase.com/)), `psycopg2-binary`, SQLite (zero-config fallback) |
| **Authentication** | Supabase Auth (JWT Bearer Token verification, Email/Password, Google OAuth) |
| **AI / NLP** | [Groq Cloud](https://groq.com/) (`llama-3.3-70b-versatile`, `qwen/qwen3.8-27b`), Intent Classifier |
| **Nutrition Data** | [CalorieNinjas REST API](https://calorieninjas.com/api) (Header-based `X-Api-Key`, dynamic IP resilient) |
| **Frontend** | Modern Vanilla JavaScript (ES6+), Vanilla CSS (Custom Design System, Glassmorphism, Micro-animations), Supabase JS Client |

---

## 📁 Repository Structure

```text
Macroly/
├── backend/
│   ├── ai_interpreter.py     # Natural language meal parser (Groq LLM / Intent classifier / Rule engine)
│   ├── auth.py               # Supabase JWT verification and user identity dependency
│   ├── database.py           # PostgreSQL/SQLite dual-mode connection pool and queries
│   ├── main.py               # FastAPI application routes, middleware, and lifecycle
│   ├── models.py             # Pydantic schemas for requests, responses, and user profiles
│   ├── nutrition_service.py  # CalorieNinjas API integration and nutrient scaling
│   ├── smart_cache.py        # High-performance food caching and macro scaling
│   └── tests/                # Automated feature and multi-user isolation test suite
├── frontend/
│   ├── assets/               # Demo avatars and culinary imagery
│   ├── css/
│   │   └── styles.css        # Responsive dark-mode styling, tokens, and micro-animations
│   ├── js/
│   │   ├── api.js            # Client-side API client handling auth headers and requests
│   │   └── app.js            # Application controller, modal managers, and UI bindings
│   └── index.html            # Main single-page application dashboard
├── docs/
│   ├── ai_architecture_and_feature_log.md  # Comprehensive AI pipeline & intelligence record
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
  - [CalorieNinjas](https://calorieninjas.com) (for live food database search)

> **Note**: Macroly is designed to run out of the box even without external API keys — it will automatically fall back to rule-based parsing and local SQLite database storage for local testing!

### 1. Clone the Repository

```bash
git clone https://github.com/shadmanmd48/Macroly-V1.1.git
cd Macroly
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

# CalorieNinjas API (Optional, for live nutrition lookup)
CALORIENINJAS_API_KEY=your_calorieninjas_api_key_here
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
- [AI Architecture & Intelligence Feature Log](docs/ai_architecture_and_feature_log.md): Record of multi-tier AI layers, metric parsing, approximation qualifiers, and scaling logic.
- [Architecture & Multi-Tier Resolution](docs/architecture.md): In-depth look at system topology, pipeline layers, and JWT validation.
- [REST API Reference](docs/api.md): Schema specifications and example payloads for all HTTP endpoints.

---

## 📄 License

This project is licensed under the terms of the [MIT License](LICENSE).
