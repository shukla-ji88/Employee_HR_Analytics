
# HR Analytics Dashboard

## Project Overview
A practice HR Analytics project built using Python, Pandas, SQL and Streamlit.
It analyzes employee salary, department distribution, hiring trends and
performance data using an interactive dashboard and Excel reports.


## Live Demo

**Try the HR Analytics Dashboard:**  
[Open Dashboard](https://employee-hr-analytics-demo.streamlit.app/)

> Note: Replace the URL above with your actual Streamlit URL
> after saving your app settings.

## Project Highlights

- Interactive employee analytics dashboard
- Department-wise salary and employee analysis
- SQL queries, aggregations and JOIN operations
- Monthly hiring trends
- Simulated employee lifecycle analysis
- Excel reports with multiple worksheets and charts

## Technology Stack

Python | Pandas | SQLite | SQL | Streamlit | Plotly | Excel

## Data Disclaimer

This is a learning project using sample employee records.
Employee exit data is simulated for demonstration purposes
and does not represent real company attrition.


## Technology Stack
- Python
- Pandas
- SQLite
- SQL
- Streamlit
- Plotly
- Matplotlib
- Excel / OpenPyXL
- Jupyter Notebook

## Features
- Employee data inspection and cleaning
- Department-wise employee and salary analysis
- Interactive filters and employee search
- Salary band distribution
- SQL queries and JOIN operations
- Monthly and yearly hiring trends
- Demo employee lifecycle analysis
- CSV and Excel report downloads
- Automated Excel report with multiple worksheets and charts

## Project Files
- employee_hr_analysis.ipynb: Data analysis notebook
- employee_data.csv: Sample employee dataset
- hr_dashboard.py: Interactive dashboard
- sql_analysis.py: SQL analysis
- sql_join_analysis.py: SQL JOIN demonstration
- create_lifecycle_demo.py: Simulated lifecycle data setup
- generate_final_report.py: Excel report generator
- hr_analytics.db: SQLite database

## How to Run
Install the required packages:

    python -m pip install pandas matplotlib seaborn openpyxl streamlit plotly

Generate or refresh the database:

    python sql_analysis.py

Create the department information table:

    python sql_join_analysis.py

Create demo lifecycle records:

    python create_lifecycle_demo.py

Launch the dashboard:

    python -m streamlit run hr_dashboard.py

Generate the final Excel report:

    python generate_final_report.py

## Outputs
- Interactive Streamlit dashboard
- SQL analysis CSV files
- Excel report with multiple worksheets and charts

## Data Disclaimer
This is a learning project based on sample employee records.
Lifecycle exits are simulated for demonstration and do not represent
actual company attrition or real employee information.
