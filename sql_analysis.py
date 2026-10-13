
from pathlib import Path
import sqlite3
import pandas as pd

# 1. File paths
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "employee_data.csv"
DB_PATH = BASE_DIR / "hr_analytics.db"

# 2. Check whether the CSV exists
if not CSV_PATH.exists():
    raise FileNotFoundError(
        f"Dataset nahi mili: {CSV_PATH}"
    )

# 3. Load CSV data
df = pd.read_csv(CSV_PATH)

# 4. Create SQLite database and table
with sqlite3.connect(DB_PATH) as conn:

    df.to_sql(
        "employee_data",
        conn,
        if_exists="replace",
        index=False
    )

    print("Database created successfully!")

    # QUERY 1: Department-wise analysis
    query1 = """
    SELECT
        Department,
        COUNT(*) AS Total_Employees,
        ROUND(AVG(Salary), 2) AS Average_Salary,
        SUM(Salary) AS Total_Salary_Amount
    FROM employee_data
    GROUP BY Department
    ORDER BY Average_Salary DESC;
    """

    department_report = pd.read_sql_query(query1, conn)

    print("\n1. DEPARTMENT-WISE ANALYSIS")
    print(department_report.to_string(index=False))

    # QUERY 2: Top 5 highest-paid employees
    query2 = """
    SELECT Name, Department, Salary, ExperienceYears
    FROM employee_data
    ORDER BY Salary DESC
    LIMIT 5;
    """

    top_employees = pd.read_sql_query(query2, conn)

    print("\n2. TOP 5 HIGHEST-PAID EMPLOYEES")
    print(top_employees.to_string(index=False))

    # QUERY 3: Employees earning above ₹50,000
    query3 = """
    SELECT Name, Department, Position, Salary
    FROM employee_data
    WHERE Salary > 50000
    ORDER BY Salary DESC;
    """

    high_salary = pd.read_sql_query(query3, conn)

    print("\n3. EMPLOYEES WITH SALARY ABOVE 50000")
    print(high_salary.to_string(index=False))

    # QUERY 4: Salary analysis by performance rating
    query4 = """
    SELECT
        PerformanceRating,
        COUNT(*) AS Employee_Count,
        ROUND(AVG(Salary), 2) AS Average_Salary
    FROM employee_data
    GROUP BY PerformanceRating
    ORDER BY PerformanceRating DESC;
    """

    performance_report = pd.read_sql_query(query4, conn)

    print("\n4. PERFORMANCE ANALYSIS")
    print(performance_report.to_string(index=False))

    # 5. Export SQL analysis to CSV
    department_report.to_csv(
        BASE_DIR / "department_summary_sql.csv",
        index=False
    )

print("\nSQL ANALYSIS COMPLETED!")
print("Database:", DB_PATH.name)
print("Department report exported successfully.")
