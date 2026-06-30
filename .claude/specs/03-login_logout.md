# Step 3 — Login and Logout

## Overview

This step converts the `/login` stub into a functional `GET`/`POST` handler that:
- Verifies submitted credentials against the `users` table
- Stores the authenticated user's `id` in `session["user_id"]` on success
- Redirects to the landing page (`/`) until a dedicated dashboard route exists

It also implements `/logout`, which clears the session entirely and redirects to `/`. After this step the app can distinguish logged-in users from guests. This is a prerequisite for all expense features (Steps 4–9).

## Depends on

- Step 01 — Database Setup (`users` table must exist)
- Step 02 — Registration (`create_user()` and password hashing must be in place; a user must exist to log in against)

## Routes

- `GET /login` — render the login form — public
- `POST /login` — validate credentials, set session, redirect — public
- `GET /logout` — clear the session, redirect to `/` — public (no login required)

## Database changes

- No new tables or columns
- The `users` table from Step 01 already stores `email` and `password_hash`
- Add one new helper to `database/db.py`:
  - `get_user_by_email(email)`
    - Queries the `users` table for a row matching the given `email`
    - Returns the matching row (`sqlite3.Row`) or `None` if not found
    - Must live in `database/db.py` — not inlined in the route handler

## Templates

- Modify `templates/login.html`:
  - Add a `<form>` with `action="{{ url_for('login') }}"` and `method="post"`
  - Add `email` and `password` input fields with matching `name` attributes
  - Add a block to display flashed error messages
  - Add a link to `/register` for users who do not yet have an account

## Files to change

- `app.py` — implement `login()` as a `GET`+`POST` handler; implement `logout()`
- `database/db.py` — add `get_user_by_email()` helper
- `templates/login.html` — add POST form and flash message display

## Files to create

None.

## New dependencies

None. `werkzeug.security.check_password_hash` is already available via the existing `werkzeug` installation.

## Rules for implementation

- No SQLAlchemy or ORMs — use raw `sqlite3` via `get_db()`
- Parameterized queries only — never use f-strings or string formatting in SQL
- Verify passwords with `werkzeug.security.check_password_hash`
- The session key for the logged-in user must be `session["user_id"]` (an integer)
- Use `flask.session` — do not roll a custom session mechanism
- On failed login (wrong password or unregistered email) show a single generic flash error: `"Invalid email or password."` — do not reveal which field was wrong
- After successful login redirect to `url_for("landing")` until a dashboard route exists
- `logout()` must call `session.clear()` then redirect to `url_for("landing")`
- All templates must extend `base.html`
- Use CSS variables — never hardcode hex values in templates or new styles
- Use `url_for()` for every internal link — never hardcode paths

## Definition of done

- [ ] `GET /login` renders the login form with `email` and `password` fields
- [ ] Submitting with valid credentials (`demo@spendly.com` / `demo123`) sets `session["user_id"]` and redirects to `/`
- [ ] Submitting with a wrong password shows `"Invalid email or password."` flash and stays on the login page
- [ ] Submitting with an unregistered email shows the same generic error flash
- [ ] `GET /logout` clears the session and redirects to `/`
- [ ] After logout, `session["user_id"]` is no longer present in the session
- [ ] The `/logout` route no longer returns the raw stub string
