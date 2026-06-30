# Step 2 — User Registration

## Overview

This step upgrades the existing stub `GET /register` route into a fully functional registration endpoint that handles both `GET` and `POST`. The form accepts four fields: `name`, `email`, `password`, and `confirm_password`. On successful registration the server flashes a success message and redirects to `/login`. Registration is the entry point for all authenticated features — no user can log in, view their profile, or manage expenses until they have registered.

## Depends on

- Step 01 — Database setup (`users` table, `get_db()`)

## Routes

- `GET /register` — render the registration form — public
  - Already exists as a stub in `app.py`; upgrade it to handle POST as well
- `POST /register` — validate form input, insert the new user, redirect to `/login` — public

## Database changes

- No new tables or columns
- The existing `users` table covers all requirements
- Add one new helper to `database/db.py`:
  - `create_user(name, email, password)`
    - Hashes `password` using `werkzeug.security.generate_password_hash`
    - Inserts a new row into `users` with the given `name`, `email`, and the hashed password
    - Returns the new user's `id` (from `cursor.lastrowid`)
    - Raises `sqlite3.IntegrityError` if the email is already registered (UNIQUE constraint violation)

## Templates

- Modify `templates/register.html`:
  - Set `action="{{ url_for('register') }}"` and `method="post"` on the `<form>` element
  - Add `name` attributes to all inputs: `name`, `email`, `password`, `confirm_password`
  - Add a block to display flashed error messages (e.g. "Email already registered", "Passwords do not match")
  - Keep all existing visual design unchanged

## Files to change

- `app.py` — upgrade `register()` to handle `GET` and `POST`; add `flash`, `redirect`, and validation logic; set `app.secret_key`
- `database/db.py` — add `create_user()` helper
- `templates/register.html` — wire up form `action`/`method` and flash message display

## Files to create

None.

## New dependencies

None. Uses `werkzeug.security` (already installed) and Flask's built-in `flash`, `redirect`, `url_for`.

## Rules for implementation

- No SQLAlchemy or ORMs — raw `sqlite3` only
- Parameterized queries only — never use f-strings or string formatting in SQL
- Hash passwords with `werkzeug.security.generate_password_hash` — never store plaintext
- `app.secret_key` must be set in `app.py` for `flash()` to work; use a hardcoded dev string for now
- Server-side validation must check in this order:
  1. All fields are non-empty
  2. `password == confirm_password`
  3. Email is not already registered (catch `sqlite3.IntegrityError` from `create_user()`)
- On any validation failure: re-render the form with a flashed error message — do not redirect
- On success: flash a success message and redirect to `url_for('login')`
- Use `abort(405)` if an unsupported HTTP method reaches the route
- All templates must extend `base.html`
- Use CSS variables — never hardcode hex values in templates or new styles
- Use `url_for()` for every internal link — never hardcode URLs

## Definition of done

- [ ] `GET /register` renders the registration form without errors
- [ ] Submitting with all valid fields creates a new user in `users` and redirects to `/login`
- [ ] Submitting with mismatched passwords re-renders the form with an error; no DB insert occurs
- [ ] Submitting with an already-registered email re-renders the form with "Email already registered"
- [ ] Submitting with any empty field re-renders the form with a validation error
- [ ] Password is stored as a hash — never plaintext — verifiable by inspecting `spendly.db`
- [ ] No duplicate user is created on repeated valid submissions with the same email
