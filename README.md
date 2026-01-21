# URL Shortener with Login

Simple Flask URL shortener secured with username/password login. Each user can shorten URLs and view only their own history; short links remain publicly redirectable.

## Stack
- Python 3.12+
- Flask, Flask-Login, Flask-SQLAlchemy, Flask-Migrate
- SQLite (default)

## Quickstart
```bash
git clone <this-repo>
cd URL-shortener

# create & activate virtualenv
python3 -m venv .venv
source .venv/bin/activate

# install deps
pip install -r requirements.txt

# set flask env (per shell)
export FLASK_APP=app.py
export FLASK_ENV=development  # optional, enables debugger/reload

# initialize DB (first time)
python -m flask db init        # skip if migrations/ already exists
python -m flask db migrate -m "create user and urls tables"
python -m flask db upgrade

# run the app
python -m flask run
```

Open http://127.0.0.1:5000/

## Usage
1) Sign up with a 5–9 char unique username and password.  
2) Log in, paste a URL (must start with https://) and click Shorten.  
3) Copy/use the generated short link; it remains public for redirects.  
4) View your history via “All URLs” or the table on the home page.

## Notes
- DB file: `urls.db` in the project root (SQLite). Delete it to reset locally, then rerun migrate/upgrade.
- Environment variables:
  - `SECRET_KEY` (optional; falls back to a dev default)
  - `DATABASE_URL` (optional; defaults to sqlite:///urls.db; set to Postgres URI if desired)
- If you switch databases, re-run migrations against the new target.

## Troubleshooting
- `ModuleNotFoundError: flask_sqlalchemy` → ensure venv is active and `pip install -r requirements.txt` was run.
- `No such table: user` → run `python -m flask db upgrade` (and `db migrate` if models changed); delete `urls.db` if you want a clean slate.
- Flask CLI not finding the app → confirm `export FLASK_APP=app.py` in the current shell.
