import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "ai_company.db"


def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def _columns(db, table):
    return {row[1] for row in db.execute(f"PRAGMA table_info({table})").fetchall()}


def _add_column(db, table, column, definition):
    if column not in _columns(db, table):
        db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def init_db():
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        plan TEXT DEFAULT '',
        status TEXT NOT NULL DEFAULT 'DRAFT',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS agents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        role TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'IDLE'
    );

    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        parent_task_id INTEGER,
        title TEXT NOT NULL,
        description TEXT DEFAULT '',
        assigned_agent TEXT DEFAULT '',
        priority TEXT NOT NULL DEFAULT 'MEDIUM',
        status TEXT NOT NULL DEFAULT 'PENDING',
        dependency TEXT DEFAULT '',
        deadline DATETIME,
        result TEXT DEFAULT '',
        retry_count INTEGER NOT NULL DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(project_id) REFERENCES projects(id),
        FOREIGN KEY(parent_task_id) REFERENCES tasks(id)
    );

    CREATE TABLE IF NOT EXISTS approvals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'PENDING',
        comment TEXT DEFAULT '',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(project_id) REFERENCES projects(id)
    );

    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT NOT NULL,
        details TEXT DEFAULT '',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # V1 -> V2 migration for an existing SQLite database.
    _add_column(db, "tasks", "parent_task_id", "INTEGER")
    _add_column(db, "tasks", "priority", "TEXT NOT NULL DEFAULT 'MEDIUM'")
    _add_column(db, "tasks", "dependency", "TEXT DEFAULT ''")
    _add_column(db, "tasks", "deadline", "DATETIME")
    _add_column(db, "tasks", "retry_count", "INTEGER NOT NULL DEFAULT 0")

    agents = [
        (1, "Manager", "Project Manager"),
        (2, "Researcher", "Research"),
        (3, "Developer", "Development"),
        (4, "Tester", "Testing"),
        (5, "Reviewer", "Quality Review"),
    ]
    for agent_id, name, role in agents:
        db.execute(
            "INSERT OR IGNORE INTO agents (id, name, role) VALUES (?, ?, ?)",
            (agent_id, name, role)
        )

    db.execute("CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_tasks_parent ON tasks(parent_task_id)")
    db.commit()
    db.close()
