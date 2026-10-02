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

    # V4 migration for Quality Control fields.\n    _ensure_column(db, "tasks", "attempts", "INTEGER NOT NULL DEFAULT 0")
    _ensure_column(db, "tasks", "result_status", "TEXT")
    _ensure_column(db, "tasks", "feedback", "TEXT")

    # V5 Software Company fields.
    _ensure_column(db, "projects", "project_type", "TEXT NOT NULL DEFAULT 'SOFTWARE'")
    _ensure_column(db, "projects", "release_status", "TEXT NOT NULL DEFAULT 'NOT_RELEASED'")

    db.executescript("""
    CREATE TABLE IF NOT EXISTS releases(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      project_id INTEGER NOT NULL,
      version TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'READY',
      release_notes TEXT,
      requirements TEXT,
      architecture TEXT,
      implementation TEXT,
      test_report TEXT,
      review_report TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(project_id) REFERENCES projects(id)
    );
    """)

    # V7 Workflow Automation.
    db.executescript("""
    CREATE TABLE IF NOT EXISTS workflows(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      project_id INTEGER NOT NULL UNIQUE,
      name TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'PENDING',
      current_step INTEGER NOT NULL DEFAULT 0,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(project_id) REFERENCES projects(id)
    );

    CREATE TABLE IF NOT EXISTS workflow_steps(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      workflow_id INTEGER NOT NULL,
      task_id INTEGER NOT NULL,
      step_order INTEGER NOT NULL,
      depends_on INTEGER,
      status TEXT NOT NULL DEFAULT 'PENDING',
      started_at TIMESTAMP,
      completed_at TIMESTAMP,
      FOREIGN KEY(workflow_id) REFERENCES workflows(id),
      FOREIGN KEY(task_id) REFERENCES tasks(id)
    );

    CREATE INDEX IF NOT EXISTS idx_workflow_steps_workflow ON workflow_steps(workflow_id);
    CREATE INDEX IF NOT EXISTS idx_workflow_steps_task ON workflow_steps(task_id);
    """)


    # V8 AI Meeting.
    db.executescript("""
    CREATE TABLE IF NOT EXISTS meetings(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      project_id INTEGER NOT NULL,
      title TEXT NOT NULL,
      objective TEXT NOT NULL,
      agenda TEXT,
      status TEXT NOT NULL DEFAULT 'DRAFT',
      decision TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(project_id) REFERENCES projects(id)
    );

    CREATE TABLE IF NOT EXISTS meeting_messages(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      meeting_id INTEGER NOT NULL,
      agent_name TEXT NOT NULL,
      role TEXT,
      message TEXT NOT NULL,
      recommendation TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(meeting_id) REFERENCES meetings(id)
    );

    CREATE TABLE IF NOT EXISTS meeting_decisions(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      meeting_id INTEGER NOT NULL,
      status TEXT NOT NULL DEFAULT 'PENDING_CEO',
      summary TEXT NOT NULL,
      action_items TEXT,
      approved_at TIMESTAMP,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(meeting_id) REFERENCES meetings(id)
    );

    CREATE INDEX IF NOT EXISTS idx_meetings_project ON meetings(project_id);
    CREATE INDEX IF NOT EXISTS idx_meeting_messages_meeting ON meeting_messages(meeting_id);
    CREATE INDEX IF NOT EXISTS idx_meeting_decisions_meeting ON meeting_decisions(meeting_id);
    """)

    # V6 AI Memory.
    db.executescript("""
    CREATE TABLE IF NOT EXISTS memories(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      project_id INTEGER,
      agent_name TEXT,
      memory_type TEXT NOT NULL DEFAULT 'TASK_RESULT',
      memory_key TEXT,
      content TEXT NOT NULL,
      importance INTEGER NOT NULL DEFAULT 5,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(project_id) REFERENCES projects(id)
    );
    CREATE INDEX IF NOT EXISTS idx_memories_project ON memories(project_id);
    CREATE INDEX IF NOT EXISTS idx_memories_agent ON memories(agent_name);
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
