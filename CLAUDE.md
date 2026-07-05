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

**Spendly** is a step-by-step educational Flask project, built incrementally against the `Spec_NN_*.md` files in the project root (each spec = one implementation step, in build order). Routes for steps not yet implemented return placeholder strings in `app.py` — check a route's body before assuming it's real.

### Stack
- **Flask 3.1.3** + **Jinja2** — server-rendered HTML, no frontend framework
- **SQLite** (`spendly.db` in project root, git-ignored) — raw `sqlite3`, no ORM
- **Werkzeug** — password hashing only (`generate_password_hash` / `check_password_hash`)
- **Vanilla JS** — no bundler, no npm
- **pytest + pytest-flask** — `tests/conftest.py` provides `app`/`client` fixtures plus `seed_user_id` (the demo user seeded by `seed_db()`) and `empty_user_id` (a freshly created user with no expenses, torn down after the test)

### Request flow
```
Browser → app.py (Flask routes) → database/db.py (get_db, create_user, get_user_by_email)
                                → database/queries.py (read-only queries for profile page)
                                → spendly.db
                                ↓
                         templates/*.html (Jinja2, extend base.html)
                                ↓
                         static/css/style.css  (global)
                         static/css/landing.css (landing page only, loaded via {% block head %})
```

`database/db.py` owns writes and auth lookups (`get_db`, `init_db`, `seed_db`, `create_user`, `get_user_by_email`). `database/queries.py` owns the read-only aggregation queries used to render the profile page (`get_user_by_id`, `get_summary_stats`, `get_recent_transactions`, `get_category_breakdown`) — keep that split when adding new queries.

`init_db()` and `seed_db()` run at import time in `app.py` (inside `app.app_context()`), so the schema and demo user (`demo@spendly.com` / `demo123`) always exist before the first request.

### Key conventions
- `base.html` defines `{% block title %}`, `{% block head %}`, `{% block content %}`, and `{% block scripts %}`. All templates extend it.
- `landing.css` is injected via `{% block head %}` and loads *after* `style.css`, so it overrides hero styles without touching the shared stylesheet.
- `{% block scripts %}` before `</body>` is the injection point for page-specific JS (e.g., the video modal on the landing page).
- All SQL must use **parameterized queries** — never string formatting.
- `PRAGMA foreign_keys = ON` must be set on every `get_db()` call.
- Expense amounts are stored as `REAL`, dates as `TEXT` in `YYYY-MM-DD` format.
- Valid expense categories (fixed list): `Food`, `Transport`, `Bills`, `Health`, `Entertainment`, `Shopping`, `Other`.
- CSS variables only — never hardcode hex values in templates/stylesheets.
- Login required routes (e.g. `/profile`) check `session.get("user_id")` and redirect to `login` if absent — follow this pattern for any new authenticated route.

### Database schema
| Table | Key columns |
|-------|-------------|
| `users` | `id` PK, `name`, `email` UNIQUE, `password_hash`, `created_at` |
| `expenses` | `id` PK, `user_id` FK→users, `amount` REAL, `category`, `date`, `description`, `created_at` |

### Implementation steps (Spec files)
The `Spec_NN_*.md` files document the build order. Implemented so far (per `app.py` and `database/`):
1. ✅ Database setup (`database/db.py`)
2. ✅ Registration (`/register`)
3. ✅ Login / logout (`/login`, `/logout`)
4. ✅ Profile page (`/profile` — expense list, summary stats, category breakdown)
5. ✅ Backend routes for profile (`database/queries.py`)

Not yet implemented — still placeholder strings in `app.py`:
6. Date filter on profile
7. Add expense (`/expenses/add`)
8. Edit expense (`/expenses/<id>/edit`)
9. Delete expense (`/expenses/<id>/delete`)

### Spec-driven workflow (custom slash commands)
This repo uses a fixed workflow for building each step, driven by commands in `.claude/commands/`:
- **`/create-spec <step> <name>`** — creates a feature branch (`feature/<slug>`) off `main` and writes a spec to `.claude/specs/<step>-<slug>.md` (routes, DB changes, templates, rules, definition of done). Refuses to run if the working tree isn't clean.
- **`/code-review-feature <spec-name>`** — runs security + quality subagent reviews in parallel against the diff for that spec, then presents a combined report and asks for approval before applying fixes.
- **`/test-feature <spec-name>`** — writes and runs tests for a spec.
- **`/ship-feature`** — commits (Conventional Commits), pushes, opens a PR via GitHub MCP, squash-merges, and deletes both branches. Never commits directly to `main`.
- **`/seed-user`** / **`/seed-expense`** — create dummy users/expenses for manual testing.

When implementing a new spec step, follow the spec file in `.claude/specs/` for that step rather than improvising routes/schema.
