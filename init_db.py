import sqlite3
from pathlib import Path


project_folder = Path(__file__).resolve().parent
database_path = project_folder / "event_hub.db"
schema_path = project_folder / "schema.sql"

conn = sqlite3.connect(database_path)

try:
    schema = schema_path.read_text(encoding="utf-8")
    conn.executescript(schema)
    conn.commit()
    print("Events Hub database created successfully.")
finally:
    conn.close()