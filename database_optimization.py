
from pathlib import Path
import sqlite3
import pandas as pd

from db_utils import ensure_indexes

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "hr_analytics.db"

if not DB_PATH.exists():
    raise FileNotFoundError(
        "Database nahi mili. Pehle python sql_analysis.py run karo."
    )

with sqlite3.connect(DB_PATH) as conn:

    # Create indexes safely
    index_count = ensure_indexes(conn)

    print("Index setup completed.")
    print("Tables checked for indexes:", index_count)

    # Display user-created indexes
    indexes = pd.read_sql_query(
        """
        SELECT name, tbl_name AS table_name
        FROM sqlite_master
        WHERE type = 'index'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY tbl_name, name
        """,
        conn
    )

    print("\nDATABASE INDEXES")
    if indexes.empty:
        print("No indexes found.")
    else:
        print(indexes.to_string(index=False))

    # Inspect how SQLite plans a common analytics query
    query_plan = pd.read_sql_query(
        """
        EXPLAIN QUERY PLAN
        SELECT EmployeeID, Name, Department, Salary
        FROM employee_data
        WHERE Department = ?
          AND Salary >= ?
        ORDER BY Salary DESC
        """,
        conn,
        params=("IT", 50000)
    )

    print("\nQUERY EXECUTION PLAN")
    print(query_plan.to_string(index=False))

print("\nDATABASE OPTIMIZATION CHECK COMPLETED!")
