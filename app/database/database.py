from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "ai_company.db"


def get_connection():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    return db


def _ensure_column(db, table: str, column: str, definition: str):
    columns = {
        row["name"]
        for row in db.execute(f"PRAGMA table_info({table})").fetchall()
    }
    if column not in columns:
        db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def init_db():
    db = get_connection()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS projects(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      description TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'DRAFT',
      plan_json TEXT,
      plan_provider TEXT,
      manager_analysis TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS agents(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT UNIQUE NOT NULL,
      role TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'IDLE'
    );

    CREATE TABLE IF NOT EXISTS tasks(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      project_id INTEGER NOT NULL,
      title TEXT NOT NULL,
      description TEXT,
      assigned_agent TEXT,
      status TEXT NOT NULL DEFAULT 'PENDING',
      result TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(project_id) REFERENCES projects(id)
    );

    CREATE TABLE IF NOT EXISTS approvals(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      project_id INTEGER NOT NULL,
      action TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'PENDING',
      notes TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(project_id) REFERENCES projects(id)
    );

    CREATE TABLE IF NOT EXISTS audit_logs(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      project_id INTEGER,
      action TEXT NOT NULL,
      details TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(project_id) REFERENCES projects(id)
    );
    """)

    # V2 migration for databases created by V1.x.
    _ensure_column(db, "projects", "plan_json", "TEXT")
    _ensure_column(db, "projects", "plan_provider", "TEXT")
    _ensure_column(db, "projects", "manager_analysis", "TEXT")

    for name, role in [
        ("Manager", "Project Manager"),
        ("Researcher", "Research"),
        ("Developer", "Development"),
        ("Tester", "Testing"),
        ("Reviewer", "Quality Review"),
    ]:
        db.execute(
            "INSERT OR IGNORE INTO agents(name,role) VALUES(?,?)",
            (name, role),
        )

    db.commit()
    db.close()
