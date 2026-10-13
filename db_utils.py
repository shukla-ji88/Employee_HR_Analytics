
import sqlite3


def table_exists(conn, table_name):
    """Check whether a table exists in the SQLite database."""
    result = conn.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE type = 'table' AND name = ?
        LIMIT 1
        """,
        (table_name,)
    ).fetchone()

    return result is not None


def ensure_indexes(conn):
    """
    Create useful indexes for employee analysis.
    Safe to call repeatedly: existing indexes are not duplicated.
    """
    index_definitions = [
        (
            "employee_data",
            """
            CREATE INDEX IF NOT EXISTS idx_employee_id
            ON employee_data(EmployeeID)
            """
        ),
        (
            "employee_data",
            """
            CREATE INDEX IF NOT EXISTS idx_employee_department_salary
            ON employee_data(Department, Salary DESC)
            """
        ),
        (
            "employee_data",
            """
            CREATE INDEX IF NOT EXISTS idx_employee_joining_date
            ON employee_data(JoiningDate)
            """
        ),
        (
            "employee_data",
            """
            CREATE INDEX IF NOT EXISTS idx_employee_rating
            ON employee_data(PerformanceRating)
            """
        ),
        (
            "department_info",
            """
            CREATE INDEX IF NOT EXISTS idx_department_info_department
            ON department_info(Department)
            """
        ),
        (
            "employee_lifecycle",
            """
            CREATE INDEX IF NOT EXISTS idx_lifecycle_employee_id
            ON employee_lifecycle(EmployeeID)
            """
        ),
        (
            "employee_lifecycle",
            """
            CREATE INDEX IF NOT EXISTS idx_lifecycle_status_exit_date
            ON employee_lifecycle(EmploymentStatus, ExitDate)
            """
        )
    ]

    created_or_verified = 0

    for table_name, sql in index_definitions:
        if table_exists(conn, table_name):
            conn.execute(sql)
            created_or_verified += 1

    return created_or_verified
