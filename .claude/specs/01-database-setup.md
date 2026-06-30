# Step 1 — Database Setup

## 1. Overview

This step replaces the stub in `database/db.py` with a working SQLite implementation. It is the foundational step for the entire application: authentication (Step 2–3), the profile/expense list page (Step 4–6), and all expense CRUD operations (Step 7–9) all depend on the database being correctly initialized before any route is served.

## 2. Depends on

None. This is the first step and has no prerequisites.

## 3. Routes

No new routes are added in this step. All existing placeholder routes in `app.py` remain unchanged and continue returning their placeholder strings.

## 4. Database Schema

### Table A: `users`

| Column | SQLite Type | Constraints |
|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `name` | TEXT | NOT NULL |
| `email` | TEXT | NOT NULL UNIQUE |
| `password_hash` | TEXT | NOT NULL |
| `created_at` | TEXT | NOT NULL DEFAULT (datetime('now')) |

### Table B: `expenses`

| Column | SQLite Type | Constraints |
|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `user_id` | INTEGER | NOT NULL, FOREIGN KEY → users(id) |
| `amount` | REAL | NOT NULL |
| `category` | TEXT | NOT NULL |
| `date` | TEXT | NOT NULL — must be `YYYY-MM-DD` format |
| `description` | TEXT | |
| `created_at` | TEXT | NOT NULL DEFAULT (datetime('now')) |

## 5. Functions to Implement (`database/db.py`)

**`get_db()`**
- Opens `spendly.db` in the project root
- Sets `connection.row_factory = sqlite3.Row`
- Executes `PRAGMA foreign_keys = ON`
- Returns the connection

**`init_db()`**
- Creates both `users` and `expenses` tables using `CREATE TABLE IF NOT EXISTS`
- Safe to call multiple times without side effects

**`seed_db()`**
- Checks whether the `users` table already contains any rows; if yes, returns immediately
- Otherwise inserts one demo user:
  - name: `Demo User`
  - email: `demo@spendly.com`
  - password: `demo123` hashed with `generate_password_hash` from `werkzeug.security`
- Inserts 8 sample expenses linked to the demo user, covering all 7 categories, with dates spread across the current month

## 6. Changes to `app.py`

- Import `get_db`, `init_db`, `seed_db` from `database.db`
- After creating the Flask `app` instance, call `init_db()` and `seed_db()` inside a `with app.app_context():` block so the database is fully ready before any route is served

## 7. Files to Change

- `database/db.py`
- `app.py`

## 8. Files to Create

None.

## 9. Dependencies

No new pip packages. Use:
- `sqlite3` (Python standard library)
- `werkzeug.security` (already listed in `requirements.txt`)

## 10. Categories (Fixed List)

Valid values for `expenses.category`:

- Food
- Transport
- Bills
- Health
- Entertainment
- Shopping
- Other

## 11. Rules for Implementation

- No ORM, no SQLAlchemy — raw `sqlite3` only
- All SQL statements must use parameterized queries (`?` placeholders) — never string formatting or f-strings in SQL
- `PRAGMA foreign_keys = ON` must be executed on every connection returned by `get_db()`
- Store `amount` as `REAL`, not `INTEGER`
- Hash passwords with `generate_password_hash` from `werkzeug.security`
- `seed_db()` must be idempotent — safe to call on every app startup without inserting duplicates
- All dates must be stored as `TEXT` in `YYYY-MM-DD` format

## 12. Expected Behavior

**`get_db()`** — returns an open `sqlite3.Connection` with `row_factory = sqlite3.Row` set and foreign key enforcement active. Callers are responsible for closing the connection.

**`init_db()`** — after calling, both `users` and `expenses` tables exist in `spendly.db` with the schema defined in Section 4. Calling it again when tables already exist has no effect.

**`seed_db()`** — after calling on a fresh database, one user row and eight expense rows exist. Calling it again when data already exists returns immediately without inserting duplicates.

**Database-level constraints must enforce:**
- `users.email` uniqueness
- `expenses.user_id` referential integrity against `users.id`
- `NOT NULL` on all required columns

## 13. Error Handling Expectations

- Inserting a duplicate email → SQLite raises `UNIQUE constraint failed: users.email`
- Inserting an expense with a non-existent `user_id` → SQLite raises `FOREIGN KEY constraint failed`
- Any malformed or invalid query → exception propagates unhandled so errors are immediately visible during development

## 14. Definition of Done

- [ ] `spendly.db` is created in the project root on app startup
- [ ] Both `users` and `expenses` tables exist with the correct schema and constraints
- [ ] Demo user (`demo@spendly.com`) exists with a hashed password
- [ ] 8 sample expenses exist, covering all 7 categories
- [ ] Running the app a second time produces no duplicate seed data
- [ ] App starts without errors
- [ ] Foreign key enforcement is active (inserting an expense with an invalid `user_id` raises an error)
- [ ] All SQL queries use parameterized statements — no string formatting in SQL
