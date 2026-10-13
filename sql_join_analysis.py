
from pathlib import Path
import sqlite3
import pandas as pd

# 1. Existing database ka path
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "hr_analytics.db"

if not DB_PATH.exists():
    raise FileNotFoundError(
        "Database nahi mili. Pehle python sql_analysis.py run karo."
    )

# 2. Department ki sample information
# Ye practice ke liye demo data hai, real company data nahi.
department_data = pd.DataFrame({
    "Department": [
        "IT", "HR", "Finance", "Sales",
        "Marketing", "Legal"
    ],
    "CostCenter": [
        "IT-101", "HR-102", "FIN-103",
        "SAL-104", "MKT-105", "LEG-106"
    ],
    "DepartmentType": [
        "Technology", "People Operations", "Finance",
        "Revenue", "Marketing", "Legal and Compliance"
    ]
})

with sqlite3.connect(DB_PATH) as conn:

    # 3. Database mein doosri table create/update karo
    department_data.to_sql(
        "department_info",
        conn,
        if_exists="replace",
        index=False
    )

    print("Department table created successfully!")

    # 4. INNER JOIN: Dono tables ke matching records
    inner_join_query = """
        SELECT
            e.EmployeeID,
            e.Name,
            e.Department,
            d.CostCenter,
            d.DepartmentType,
            e.Position,
            e.Salary
        FROM employee_data AS e
        INNER JOIN department_info AS d
            ON e.Department = d.Department
        ORDER BY e.Department, e.Salary DESC;
    """

    joined_employees = pd.read_sql_query(
        inner_join_query, conn
    )

    print("\n1. INNER JOIN - Employee Details")
    print("Matching employee records:", len(joined_employees))
    print(joined_employees.head(10).to_string(index=False))

    # 5. LEFT JOIN: Sabhi departments, chahe employees hon ya na hon
    left_join_query = """
        SELECT
            d.Department,
            d.CostCenter,
            d.DepartmentType,
            COUNT(e.EmployeeID) AS Total_Employees,
            COALESCE(ROUND(AVG(e.Salary), 2), 0)
                AS Average_Salary
        FROM department_info AS d
        LEFT JOIN employee_data AS e
            ON d.Department = e.Department
        GROUP BY
            d.Department,
            d.CostCenter,
            d.DepartmentType
        ORDER BY Total_Employees DESC, d.Department;
    """

    department_summary = pd.read_sql_query(
        left_join_query, conn
    )

    print("\n2. LEFT JOIN - Department Summary")
    print(department_summary.to_string(index=False))

    # 6. Check: Kya kisi employee ka department missing hai?
    unmatched_query = """
        SELECT COUNT(*) AS Unmatched_Employees
        FROM employee_data AS e
        LEFT JOIN department_info AS d
            ON e.Department = d.Department
        WHERE d.Department IS NULL;
    """

    unmatched = pd.read_sql_query(
        unmatched_query, conn
    )

    print(
        "\n3. Employees without department match:",
        int(unmatched.iloc[0]["Unmatched_Employees"])
    )

    # 7. Reports CSV mein export karo
    joined_employees.to_csv(
        BASE_DIR / "joined_employee_report.csv",
        index=False
    )

    department_summary.to_csv(
        BASE_DIR / "department_join_summary.csv",
        index=False
    )

print("\nSQL JOIN ANALYSIS COMPLETED!")
print("Reports exported successfully.")
