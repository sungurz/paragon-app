"""
app/db/create_audit_table.py
==============================
Creates the audit_logs table in the existing database.
Run ONCE after the main tables have been created.

    python -m app.db.create_audit_table
"""

from app.db.database import engine, SessionLocal
from sqlalchemy import text


def create_audit_table():
    sql = """
    CREATE TABLE IF NOT EXISTS audit_logs (
        id          INT AUTO_INCREMENT PRIMARY KEY,
        user_id     INT,
        username    VARCHAR(100),
        action      VARCHAR(100)  NOT NULL,
        entity      VARCHAR(100),
        entity_id   INT,
        detail      TEXT,
        ip_address  VARCHAR(45),
        created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_user_id  (user_id),
        INDEX idx_action   (action),
        INDEX idx_created  (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
    print("✓ audit_logs table ready")


if __name__ == "__main__":
    create_audit_table()