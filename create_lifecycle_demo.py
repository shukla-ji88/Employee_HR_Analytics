
from pathlib import Path
import sqlite3
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "hr_analytics.db"

# Simulated exits for practice only.
# Ye real employee exit records nahi hain.
EXIT_DATES = {
    104: "2024-01-15",
    108: "2024-03-20",
    112: "2024-06-30",
    116: "2024-08-15",
    120: "2024-11-10",
}

if not DB_PATH.exists():
    raise FileNotFoundError(
        "Database nahi mili. Pehle python sql_analysis.py run karo."
    )

with sqlite3.connect(DB_PATH) as conn:

    employees = pd.read_sql_query(
        """
        SELECT
            EmployeeID,
            Name,
            Department,
            Position,
            Salary,
            JoiningDate
        FROM employee_data
        """,
        conn
    )

    employees["EmploymentStatus"] = employees["EmployeeID"].apply(
        lambda employee_id:
            "Exited" if int(employee_id) in EXIT_DATES else "Active"
    )

    employees["ExitDate"] = employees["EmployeeID"].map(EXIT_DATES)

    employees.to_sql(
        "employee_lifecycle",
        conn,
        if_exists="replace",
        index=False
    )

print("Employee lifecycle demo table created!")
print("Total demo records:", len(employees))
print(
    "Active demo records:",
    (employees["EmploymentStatus"] == "Active").sum()
)
print(
    "Exited demo records:",
    (employees["EmploymentStatus"] == "Exited").sum()
)
print("Existing employee_data table unchanged.")
