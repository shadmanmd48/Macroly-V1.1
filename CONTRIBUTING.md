# Contributing to Macroly 🥗

Thank you for your interest in contributing to Macroly! We welcome contributions from developers of all skill levels. To keep the project maintainable, predictable, and clean, please follow the guidelines below.

---

## 🌿 Branching Strategy

We follow a simplified Git Flow / Trunk-Based hybrid branching model designed for continuous integration:

```text
       feat/new-food-scanner
                \
  develop -----> * ----> * -----------> (Merge via PR)
                           \
  main    ------------------* ---------> (Production releases)
                           v1.1
```

- **`main`**: The stable, production-ready branch. Code in `main` is deployable at all times. Direct pushes to `main` should be reserved for versioned releases.
- **`develop`**: The primary integration branch for ongoing development. All new features, bug fixes, and improvements should target `develop`.
- **Feature Branches (`feat/<feature-name>`)**: Branch off `develop` to build isolated features or enhancements.
- **Fix Branches (`fix/<bug-name>`)**: Branch off `develop` to address specific bug fixes.
- **Hotfix Branches (`hotfix/<issue-name>`)**: Branch directly off `main` for critical production fixes, and merge back into both `main` and `develop`.

---

## 🛠️ Contribution Workflow

1. **Fork or Clone**:
   ```bash
   git clone https://github.com/shadmanmd48/Macroly-V1.1.git
   cd Macroly-V1.1
   ```

2. **Create a Feature Branch**:
   Always branch off `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feat/your-feature-name
   ```

3. **Set Up Local Environment**:
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\Activate.ps1
   # macOS / Linux
   source venv/bin/activate

   pip install -r requirements.txt
   cp .env.example .env
   ```

4. **Make Your Changes**:
   - Write clean, readable code with type hints where appropriate.
   - Do NOT commit sensitive keys, passwords, or local `.env` files.
   - Ensure the server starts with zero errors:
     ```bash
     uvicorn backend.main:app --reload --port 8000
     ```

5. **Commit Conventions**:
   Follow conventional commits:
   - `feat: add voice input logging for meals`
   - `fix: resolve token refresh race condition`
   - `docs: update FatSecret onboarding instructions`
   - `refactor: optimize smart cache query latency`

6. **Submit a Pull Request**:
   - Push your branch to GitHub:
     ```bash
     git push -u origin feat/your-feature-name
     ```
   - Open a Pull Request targeting the **`develop`** branch on GitHub.
   - Provide a concise description of what was changed and how to test it.

---

## 🧪 Code Quality & Architecture Rules

- **Database Safety**: Never run raw destructive SQL queries without transaction scoping. Maintain support for both PostgreSQL and SQLite fallback.
- **Security**: All protected backend routes must utilize the `get_current_user` dependency from `backend/auth.py`.
- **Styling**: Maintain vanilla CSS conventions in `frontend/css/styles.css` utilizing design tokens defined in `:root`.
