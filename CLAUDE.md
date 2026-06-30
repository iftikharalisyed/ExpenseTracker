# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the development server (port 5001, debug mode)
python app.py

# Run tests
pytest

# Run a single test file
pytest tests/test_auth.py

# Run a single test by name
pytest -k "test_login"
```

## Architecture

**Spendly** is a step-by-step educational Flask project. The codebase is intentionally incomplete — most routes return placeholder strings, and `database/db.py` is a stub. Each `Spec_NN_*.md` file in the project root is a spec for one implementation step.

### Stack
- **Flask 3.1.3** + **Jinja2** — server-rendered HTML, no frontend framework
- **SQLite** (`spendly.db` in project root, git-ignored) — raw `sqlite3`, no ORM
- **Werkzeug** — password hashing only (`generate_password_hash` / `check_password_hash`)
- **Vanilla JS** — no bundler, no npm

### Request flow
```
Browser → app.py (Flask routes) → database/db.py (get_db) → spendly.db
                                ↓
                         templates/*.html (Jinja2, extend base.html)
                                ↓
                         static/css/style.css  (global)
                         static/css/landing.css (landing page only, loaded via {% block head %})
```

### Key conventions
- `base.html` defines `{% block title %}`, `{% block head %}`, `{% block content %}`, and `{% block scripts %}`. All templates extend it.
- `landing.css` is injected via `{% block head %}` and loads *after* `style.css`, so it overrides hero styles without touching the shared stylesheet.
- `{% block scripts %}` before `</body>` is the injection point for page-specific JS (e.g., the video modal on the landing page).
- All SQL must use **parameterized queries** — never string formatting.
- `PRAGMA foreign_keys = ON` must be set on every `get_db()` call.
- Expense amounts are stored as `REAL`, dates as `TEXT` in `YYYY-MM-DD` format.
- Valid expense categories (fixed list): `Food`, `Transport`, `Bills`, `Health`, `Entertainment`, `Shopping`, `Other`.

### Database schema (target — not yet implemented)
| Table | Key columns |
|-------|-------------|
| `users` | `id` PK, `name`, `email` UNIQUE, `password_hash`, `created_at` |
| `expenses` | `id` PK, `user_id` FK→users, `amount` REAL, `category`, `date`, `description`, `created_at` |

### Implementation steps (Spec files)
The `Spec_NN_*.md` files document the intended build order:
1. Database setup (`database/db.py` — `get_db`, `init_db`, `seed_db`)
2. Registration
3. Login / logout
4. Profile page (expense list)
5. Backend routes for profile
6. Date filter on profile
7. Add expense
8. Edit expense
9. Delete expense

Most routes in `app.py` currently return placeholder strings — they are replaced as each spec is implemented.
