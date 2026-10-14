
from pathlib import Path
import sqlite3

# Check the database in this project's folder
DB_PATH = Path(__file__).resolve().parent / "hr_analytics.db"

print("=" * 45)
print("EMPLOYEE DATABASE DIAGNOSTIC")
print("=" * 45)

print("Database path:", DB_PATH)
print("Database exists:", DB_PATH.exists())

if not DB_PATH.exists():
    print("\nERROR: Database file nahi mili.")
else:
    try:
        with sqlite3.connect(DB_PATH) as conn:

            tables = {
                row[0]
                for row in conn.execute("""
                    SELECT name
                    FROM sqlite_master
                    WHERE type = 'table'
                """).fetchall()
            }

            print("\nTables found:", sorted(tables))

            if "employee_data" not in tables:
                print("ERROR: employee_data table nahi mili.")

            else:
                total = conn.execute(
                    "SELECT COUNT(*) FROM employee_data"
                ).fetchone()[0]

                print("\nTotal employee records:", total)

                print("\nLatest employee records:")

                rows = conn.execute("""
                    SELECT
                        EmployeeID,
                        Name,
                        Department,
                        Position,
                        Salary
                    FROM employee_data
                    ORDER BY EmployeeID DESC
                    LIMIT 10
                """).fetchall()

                for row in rows:
                    print(row)

                print("\nDatabase check completed.")

    except sqlite3.Error as error:
        print("DATABASE ERROR:", error)
