
import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path
from io import BytesIO
import sqlite3
from pathlib import Path
# -------------------------------
# 1. Page configuration
# -------------------------------
st.set_page_config(
    page_title="HR Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)



# 2. Load employee data and initialize database for deployment

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "employee_data.csv"
DB_PATH = BASE_DIR / "hr_analytics.db"

required_columns = [
    "EmployeeID",
    "Name",
    "Department",
    "Position",
    "Salary",
    "ExperienceYears",
    "PerformanceRating",
    "JoiningDate"
]

if not CSV_PATH.exists():
    st.error("employee_data.csv repository mein nahi mili.")
    st.stop()

try:
    source_df = pd.read_csv(CSV_PATH)

    missing_columns = [
        column for column in required_columns
        if column not in source_df.columns
    ]

    if missing_columns:
        st.error(f"CSV mein columns missing hain: {missing_columns}")
        st.stop()

    with sqlite3.connect(DB_PATH) as conn:

        # Check existing database tables
        table_names = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }

        # Table 1: Employee data
        if "employee_data" not in table_names:
            source_df.to_sql(
                "employee_data",
                conn,
                if_exists="replace",
                index=False
            )

        # Table 2: Department information
        if "department_info" not in table_names:
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
                    "Technology", "People Operations",
                    "Finance", "Revenue", "Marketing",
                    "Legal and Compliance"
                ]
            })

            department_data.to_sql(
                "department_info",
                conn,
                if_exists="replace",
                index=False
            )

        # Table 3: Simulated employee lifecycle demo data
        if "employee_lifecycle" not in table_names:

            lifecycle_df = pd.read_sql_query(
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

            # Demo exits only; these are not real employee records.
            EXIT_DATES = {
                104: "2024-01-15",
                108: "2024-03-20",
                112: "2024-06-30",
                116: "2024-08-15",
                120: "2024-11-10"
            }

            lifecycle_df["EmploymentStatus"] = (
                lifecycle_df["EmployeeID"].apply(
                    lambda employee_id:
                        "Exited"
                        if int(employee_id) in EXIT_DATES
                        else "Active"
                )
            )

            lifecycle_df["ExitDate"] = (
                lifecycle_df["EmployeeID"].map(EXIT_DATES)
            )

            lifecycle_df.to_sql(
                "employee_lifecycle",
                conn,
                if_exists="replace",
                index=False
            )

        # Load data after all required tables exist
        df = pd.read_sql_query(
            "SELECT * FROM employee_data",
            conn
        )

    if not all(column in df.columns for column in required_columns):
        st.error("Database mein required employee columns missing hain.")
        st.stop()

    st.success("Employee data aur database tables successfully loaded!")

except (sqlite3.Error, pd.errors.DatabaseError, OSError, ValueError) as e:
    st.error(f"Database initialization/load error: {e}")
    st.stop()

# -------------------------------
# 3. Dashboard heading
# -------------------------------
st.title("📊 HR Analytics Dashboard")
st.caption("Employee Overview | Salary Analysis | Performance Insights")
st.divider()

# -------------------------------
# 4. Sidebar filters
# -------------------------------
st.sidebar.header("Filter Employees")

departments = sorted(df["Department"].dropna().unique().tolist())
positions = sorted(df["Position"].dropna().unique().tolist())

selected_departments = st.sidebar.multiselect(
    "Select Department",
    departments,
    default=departments
)

selected_positions = st.sidebar.multiselect(
    "Select Position",
    positions,
    default=positions
)

min_salary = int(df["Salary"].min())
max_salary = int(df["Salary"].max())

salary_range = st.sidebar.slider(
    "Salary Range (₹)",
    min_value=min_salary,
    max_value=max_salary,
    value=(min_salary, max_salary),
    step=1000
)

search_name = st.sidebar.text_input("Search Employee Name")

# -------------------------------
# 5. Apply filters
# -------------------------------
filtered_df = df[
    df["Department"].isin(selected_departments)
    & df["Position"].isin(selected_positions)
    & df["Salary"].between(salary_range[0], salary_range[1])
].copy()

filtered_df = filtered_df[
    filtered_df["Name"].str.contains(
        search_name, case=False, na=False
    )
]


# 5A. SQL-based KPI and department analysis

employee_ids = (
    filtered_df["EmployeeID"].dropna().unique().tolist()
)

if employee_ids:
    placeholders = ", ".join(["?"] * len(employee_ids))

    with sqlite3.connect(DB_PATH) as conn:

        # SQL Query 1: Dashboard KPIs
        kpi_query = f"""
            SELECT
                COUNT(DISTINCT EmployeeID) AS total_employees,
                ROUND(COALESCE(AVG(Salary), 0), 2) AS average_salary,
                COALESCE(SUM(Salary), 0) AS total_salary_amount,
                ROUND(
                    COALESCE(AVG(PerformanceRating), 0), 2
                ) AS average_performance
            FROM employee_data
            WHERE EmployeeID IN ({placeholders})
        """

        kpi = pd.read_sql_query(
            kpi_query,
            conn,
            params=employee_ids
        ).iloc[0]

        # SQL Query 2: Department summary
        dept_query = f"""
            SELECT
                Department,
                COUNT(DISTINCT EmployeeID) AS Total_Employees,
                ROUND(AVG(Salary), 2) AS Average_Salary,
                SUM(Salary) AS Total_Payroll
            FROM employee_data
            WHERE EmployeeID IN ({placeholders})
            GROUP BY Department
            ORDER BY Average_Salary DESC
        """

        dept_summary = pd.read_sql_query(
            dept_query,
            conn,
            params=employee_ids
        )

else:
    kpi = {
        "total_employees": 0,
        "average_salary": 0,
        "total_salary_amount": 0,
        "average_performance": 0
    }

    dept_summary = pd.DataFrame(columns=[
        "Department",
        "Total_Employees",
        "Average_Salary",
        "Total_Payroll"
    ])


# -------------------------------
# 6. KPI cards
# -------------------------------
total_employees = filtered_df["EmployeeID"].nunique()

# KPI values calculated using SQL
total_employees = int(kpi["total_employees"])
avg_salary = float(kpi["average_salary"])
total_salary = float(kpi["total_salary_amount"])
avg_rating = float(kpi["average_performance"])

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Employees", total_employees)
col2.metric("Average Salary", f"₹{avg_salary:,.0f}")
col3.metric("Total Salary Amount", f"₹{total_salary:,.0f}")
col4.metric("Average Performance", f"{avg_rating:.2f}/5")

st.caption(
    "KPIs selected filters ke according update hote hain. "
    "Total Salary Amount sabhi filtered salary records ka sum hai."
)

st.divider()


# 7. Charts and business analysis

if filtered_df.empty:
    st.warning("Koi employee nahi mila. Filters change karke dekho.")

else:
    # Automated Business Insights
    st.subheader("Automated Business Insights")

    largest_dept = dept_summary.loc[
        dept_summary["Total_Employees"].idxmax()
    ]

    highest_avg_dept = dept_summary.loc[
        dept_summary["Average_Salary"].idxmax()
    ]

    top_employee = filtered_df.loc[
        filtered_df["Salary"].idxmax()
    ]

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Largest Department",
        largest_dept["Department"],
        f'{int(largest_dept["Total_Employees"])} employees'
    )

    c2.metric(
        "Highest Average Salary",
        highest_avg_dept["Department"],
        f'₹{highest_avg_dept["Average_Salary"]:,.0f}'
    )

    c3.metric(
        "Highest-Paid Employee",
        top_employee["Name"],
        f'₹{top_employee["Salary"]:,.0f}'
    )

    st.divider()

    
    # Step 15: Salary Band Analysis and Department Ranking
    st.subheader("SQL Analysis: Salary Bands & Department Ranking")

    with sqlite3.connect(DB_PATH) as conn:

        # Query 1: Salary bands using CASE WHEN
        salary_band_query = f"""
            SELECT
                CASE
                    WHEN Salary < 35000 THEN 'Below 35k'
                    WHEN Salary < 50000 THEN '35k-49,999'
                    WHEN Salary < 65000 THEN '50k-64,999'
                    ELSE '65k+'
                END AS Salary_Band,
                COUNT(DISTINCT EmployeeID) AS Employee_Count,
                SUM(Salary) AS Total_Salary_Amount
            FROM employee_data
            WHERE EmployeeID IN ({placeholders})
            GROUP BY Salary_Band
            ORDER BY MIN(Salary)
        """

        salary_band_summary = pd.read_sql_query(
            salary_band_query,
            conn,
            params=employee_ids
        )

        # Query 2: Department ranking using RANK()
        ranking_query = f"""
            SELECT
                Department,
                COUNT(DISTINCT EmployeeID) AS Total_Employees,
                ROUND(AVG(Salary), 2) AS Average_Salary,
                RANK() OVER (
                    ORDER BY AVG(Salary) DESC
                ) AS Salary_Rank
            FROM employee_data
            WHERE EmployeeID IN ({placeholders})
            GROUP BY Department
            ORDER BY Salary_Rank, Department
        """

        department_ranking = pd.read_sql_query(
            ranking_query,
            conn,
            params=employee_ids
        )

    # Display the reports
    left, right = st.columns(2)

    with left:
        st.markdown("**Employees by Salary Range**")

        salary_chart = px.bar(
            salary_band_summary,
            x="Salary_Band",
            y="Employee_Count",
            title="Salary Band Distribution",
            text="Employee_Count",
            labels={
                "Salary_Band": "Salary Range",
                "Employee_Count": "Number of Employees"
            }
        )

        st.plotly_chart(
            salary_chart,
            use_container_width=True
        )

        st.dataframe(
            salary_band_summary,
            use_container_width=True,
            hide_index=True
        )

    with right:
        st.markdown("**Department Salary Ranking**")

        st.dataframe(
            department_ranking,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    
    # STEP 16: Hiring Trends and Department Growth Analysis

    st.subheader("Hiring Trends & Department Growth")

    with sqlite3.connect(DB_PATH) as conn:

        # Query 1: Monthly hiring trend
        monthly_query = f"""
            SELECT
                strftime('%Y-%m', JoiningDate) AS Hire_Month,
                COUNT(DISTINCT EmployeeID) AS New_Hires
            FROM employee_data
            WHERE EmployeeID IN ({placeholders})
              AND JoiningDate IS NOT NULL
              AND TRIM(JoiningDate) != ''
              AND strftime('%Y-%m', JoiningDate) IS NOT NULL
            GROUP BY strftime('%Y-%m', JoiningDate)
            ORDER BY Hire_Month
        """

        monthly_hiring = pd.read_sql_query(
            monthly_query,
            conn,
            params=employee_ids
        )

        # Query 2: Department-wise hiring by year
        department_growth_query = f"""
            SELECT
                strftime('%Y', JoiningDate) AS Hire_Year,
                Department,
                COUNT(DISTINCT EmployeeID) AS New_Hires
            FROM employee_data
            WHERE EmployeeID IN ({placeholders})
              AND JoiningDate IS NOT NULL
              AND TRIM(JoiningDate) != ''
              AND strftime('%Y', JoiningDate) IS NOT NULL
            GROUP BY strftime('%Y', JoiningDate), Department
            ORDER BY Hire_Year, Department
        """

        department_growth = pd.read_sql_query(
            department_growth_query,
            conn,
            params=employee_ids
        )

    if not monthly_hiring.empty:

        # Fill months with zero hires for a continuous trend
        monthly_hiring["Hire_Month"] = pd.to_datetime(
            monthly_hiring["Hire_Month"],
            format="%Y-%m",
            errors="coerce"
        )

        monthly_hiring = monthly_hiring.dropna(
            subset=["Hire_Month"]
        ).sort_values("Hire_Month")

        if not monthly_hiring.empty:

            all_months = pd.date_range(
                start=monthly_hiring["Hire_Month"].min(),
                end=monthly_hiring["Hire_Month"].max(),
                freq="MS"
            )

            monthly_hiring = (
                monthly_hiring
                .set_index("Hire_Month")
                .reindex(all_months, fill_value=0)
                .rename_axis("Hire_Month")
                .reset_index()
            )

            # Two hiring charts
            left, right = st.columns(2)

            with left:
                fig5 = px.line(
                    monthly_hiring,
                    x="Hire_Month",
                    y="New_Hires",
                    markers=True,
                    title="Monthly Hiring Trend",
                    labels={
                        "Hire_Month": "Joining Month",
                        "New_Hires": "New Employees"
                    }
                )

                st.plotly_chart(
                    fig5,
                    use_container_width=True
                )

            with right:
                if not department_growth.empty:
                    fig6 = px.bar(
                        department_growth,
                        x="Hire_Year",
                        y="New_Hires",
                        color="Department",
                        barmode="stack",
                        title="Yearly Hires by Department",
                        labels={
                            "Hire_Year": "Year",
                            "New_Hires": "Employees Hired"
                        }
                    )

                    st.plotly_chart(
                        fig6,
                        use_container_width=True
                    )
                else:
                    st.info("Department-wise hiring data available nahi hai.")

            st.markdown("**Yearly Department Hiring Report**")
            st.dataframe(
                department_growth,
                use_container_width=True,
                hide_index=True
            )

            st.caption(
                "Yearly hires naye joiners ki count hai. "
                "Employee exits ka data nahi hai, isliye ise net "
                "department growth nahi maana ja sakta."
            )

        else:
            st.warning("Joining dates ka format check karo.")

    else:
        st.info("Selected employees ke liye valid joining dates nahi mili.")

    st.divider()

    
    # STEP 17: Retention and Attrition Analysis
    st.subheader("Employee Retention & Attrition Analysis")

    try:
        with sqlite3.connect(DB_PATH) as conn:

            # 1. Overall lifecycle summary
            lifecycle_kpi_query = f"""
                SELECT
                    COUNT(DISTINCT EmployeeID) AS Total_Records,

                    COUNT(DISTINCT CASE
                        WHEN EmploymentStatus = 'Active'
                        THEN EmployeeID END
                    ) AS Active_Count,

                    COUNT(DISTINCT CASE
                        WHEN EmploymentStatus = 'Exited'
                        THEN EmployeeID END
                    ) AS Exited_Count,

                    ROUND(
                        100.0 * COUNT(DISTINCT CASE
                            WHEN EmploymentStatus = 'Exited'
                            THEN EmployeeID END
                        ) / NULLIF(COUNT(DISTINCT EmployeeID), 0),
                        2
                    ) AS Demo_Exit_Share
                FROM employee_lifecycle
                WHERE EmployeeID IN ({placeholders})
            """

            lifecycle_kpi = pd.read_sql_query(
                lifecycle_kpi_query,
                conn,
                params=employee_ids
            ).iloc[0]

            # 2. Employee status distribution
            status_query = f"""
                SELECT
                    EmploymentStatus,
                    COUNT(DISTINCT EmployeeID) AS Employee_Count
                FROM employee_lifecycle
                WHERE EmployeeID IN ({placeholders})
                GROUP BY EmploymentStatus
            """

            status_summary = pd.read_sql_query(
                status_query,
                conn,
                params=employee_ids
            )

            # 3. Department-wise active and exited employees
            department_exit_query = f"""
                SELECT
                    Department,

                    COUNT(DISTINCT EmployeeID) AS Total_Records,

                    COUNT(DISTINCT CASE
                        WHEN EmploymentStatus = 'Active'
                        THEN EmployeeID END
                    ) AS Active_Count,

                    COUNT(DISTINCT CASE
                        WHEN EmploymentStatus = 'Exited'
                        THEN EmployeeID END
                    ) AS Exited_Count,

                    ROUND(
                        100.0 * COUNT(DISTINCT CASE
                            WHEN EmploymentStatus = 'Exited'
                            THEN EmployeeID END
                        ) / NULLIF(COUNT(DISTINCT EmployeeID), 0),
                        2
                    ) AS Demo_Exit_Share_Percent

                FROM employee_lifecycle
                WHERE EmployeeID IN ({placeholders})
                GROUP BY Department
                ORDER BY Demo_Exit_Share_Percent DESC
            """

            department_exit_summary = pd.read_sql_query(
                department_exit_query,
                conn,
                params=employee_ids
            )

            # 4. Monthly exit trend
            monthly_exit_query = f"""
                SELECT
                    substr(ExitDate, 1, 7) AS Exit_Month,
                    COUNT(DISTINCT EmployeeID) AS Exit_Count
                FROM employee_lifecycle
                WHERE EmployeeID IN ({placeholders})
                  AND EmploymentStatus = 'Exited'
                  AND ExitDate IS NOT NULL
                GROUP BY substr(ExitDate, 1, 7)
                ORDER BY Exit_Month
            """

            monthly_exits = pd.read_sql_query(
                monthly_exit_query,
                conn,
                params=employee_ids
            )

        # Show lifecycle KPIs
        st.caption(
            "Demo-only simulated records. "
            "Ye genuine company attrition rate nahi hai."
        )

        lc1, lc2, lc3 = st.columns(3)

        lc1.metric(
            "Active (Demo)",
            int(lifecycle_kpi["Active_Count"])
        )

        lc2.metric(
            "Exited (Demo)",
            int(lifecycle_kpi["Exited_Count"])
        )

        lc3.metric(
            "Demo Exit Share",
            f'{lifecycle_kpi["Demo_Exit_Share"]:.2f}%'
        )

        # Status chart and monthly exits chart
        left, right = st.columns(2)

        with left:
            if not status_summary.empty:
                status_chart = px.pie(
                    status_summary,
                    names="EmploymentStatus",
                    values="Employee_Count",
                    title="Demo Employee Status Distribution",
                    hole=0.45
                )

                st.plotly_chart(
                    status_chart,
                    use_container_width=True
                )

        with right:
            if not monthly_exits.empty:

                monthly_exits["Exit_Month"] = pd.to_datetime(
                    monthly_exits["Exit_Month"],
                    format="%Y-%m",
                    errors="coerce"
                )

                monthly_exits = monthly_exits.dropna(
                    subset=["Exit_Month"]
                )

                if not monthly_exits.empty:
                    monthly_exits = monthly_exits.set_index(
                        "Exit_Month"
                    )

                    all_exit_months = pd.date_range(
                        start=monthly_exits.index.min(),
                        end=monthly_exits.index.max(),
                        freq="MS"
                    )

                    monthly_exits = (
                        monthly_exits
                        .reindex(all_exit_months, fill_value=0)
                        .rename_axis("Exit_Month")
                        .reset_index()
                    )

                    exit_chart = px.bar(
                        monthly_exits,
                        x="Exit_Month",
                        y="Exit_Count",
                        title="Monthly Demo Exits",
                        labels={
                            "Exit_Month": "Month",
                            "Exit_Count": "Employees Exited"
                        },
                        text="Exit_Count"
                    )

                    st.plotly_chart(
                        exit_chart,
                        use_container_width=True
                    )

            else:
                st.info(
                    "Selected employees ke liye demo exit records nahi hain."
                )

        # Department-wise exit report
        st.markdown("**Department-wise Lifecycle Summary**")

        st.dataframe(
            department_exit_summary,
            use_container_width=True,
            hide_index=True
        )

    except (sqlite3.Error, pd.errors.DatabaseError) as e:
        st.error(f"Lifecycle analysis error: {e}")
        st.info(
            "Pehle terminal mein python create_lifecycle_demo.py run karo."
        )

    st.divider()


    # Chart 1 and Chart 2
    left, right = st.columns(2)

    with left:
        fig1 = px.bar(
            dept_summary,
            x="Department",
            y="Total_Employees",
            title="Employees by Department",
            text="Total_Employees"
        )

        st.plotly_chart(fig1, use_container_width=True)

    with right:
        fig2 = px.bar(
            dept_summary,
            x="Department",
            y="Average_Salary",
            title="Average Salary by Department",
            text_auto=".0f"
        )

        st.plotly_chart(fig2, use_container_width=True)

    # Chart 3 and Chart 4
    left, right = st.columns(2)

    with left:
        fig3 = px.scatter(
            filtered_df,
            x="ExperienceYears",
            y="Salary",
            color="Department",
            hover_name="Name",
            title="Experience vs Salary"
        )

        st.plotly_chart(fig3, use_container_width=True)

    with right:
        performance_summary = (
            filtered_df.groupby("PerformanceRating", as_index=False)
            .agg(
                Employee_Count=("EmployeeID", "nunique"),
                Average_Salary=("Salary", "mean")
            )
        )

        fig4 = px.bar(
            performance_summary,
            x="PerformanceRating",
            y="Employee_Count",
            title="Employees by Performance Rating",
            text="Employee_Count"
        )

        st.plotly_chart(fig4, use_container_width=True)

    # Department Summary
    st.subheader("Department Summary")

    st.dataframe(
        dept_summary,
        use_container_width=True,
        hide_index=True
    )

    # Employee Details
    st.subheader("Employee Details")

    st.dataframe(
        filtered_df.sort_values("Salary", ascending=False),
        use_container_width=True,
        hide_index=True
    )

    
    # SQL JOIN: Employee and department information
    st.subheader("Employee Details with Department Information")

    join_ids = (
        filtered_df["EmployeeID"].dropna().unique().tolist()
    )

    if join_ids:
        join_placeholders = ", ".join(["?"] * len(join_ids))

        try:
            with sqlite3.connect(DB_PATH) as conn:
                join_query = f"""
                    SELECT
                        e.EmployeeID,
                        e.Name,
                        e.Department,
                        d.CostCenter,
                        d.DepartmentType,
                        e.Position,
                        e.Salary
                    FROM employee_data AS e
                    LEFT JOIN department_info AS d
                        ON e.Department = d.Department
                    WHERE e.EmployeeID IN ({join_placeholders})
                    ORDER BY e.Department, e.Salary DESC
                """

                joined_df = pd.read_sql_query(
                    join_query,
                    conn,
                    params=join_ids
                )

            st.dataframe(
                joined_df,
                use_container_width=True,
                hide_index=True
            )

            st.download_button(
                label="Download SQL JOIN Report",
                data=joined_df.to_csv(index=False).encode("utf-8"),
                file_name="employee_department_join.csv",
                mime="text/csv"
            )

        except (sqlite3.Error, pd.errors.DatabaseError) as e:
            st.error(f"SQL JOIN report load nahi hui: {e}")

    else:
        st.info("JOIN report ke liye koi employee available nahi hai.")


    # CSV Download
    st.download_button(
        label="Download Filtered Employee Data (CSV)",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="filtered_employee_data.csv",
        mime="text/csv"
    )


st.divider()
st.caption("HR Analytics Project | Built with Python, Pandas and Streamlit")
